import asyncio
import time
from math import ceil
from hashlib import blake2b

from pyrogram.errors import MessageNotModified, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.basic.search import get_anime_info
from bot.logger import LOGGER
from database import get_variable  # + set_variable if available

log = LOGGER(__name__)

# Pagination/UI
PER_PAGE = 30
ROWS = 5
COLS = 6

# Callback encoding
DELIM = ":"
# Local in-process cache for long "text" payloads to respect 64-byte callback_data
_CB_TEXT_CACHE = {}  # token -> (text, ts)
_CB_TEXT_TTL = 60 * 60  # 1 hour
_LOCKS_BY_MSG = {}  # message_id -> asyncio.Lock


def _now():
    return int(time.time())


def cache_text(text: str) -> str:
    """Return a short deterministic token for text and cache it with TTL."""
    token = blake2b(text.encode("utf-8"), digest_size=6).hexdigest()  # 12 hex chars
    _CB_TEXT_CACHE[token] = (text, _now())
    # Optional GC to limit memory
    if len(_CB_TEXT_CACHE) > 5000:
        cutoff = _now() - _CB_TEXT_TTL
        for k, (_, ts) in list(_CB_TEXT_CACHE.items()):
            if ts < cutoff:
                _CB_TEXT_CACHE.pop(k, None)
    return token


def get_cached_text(token: str) -> str | None:
    item = _CB_TEXT_CACHE.get(token)
    if not item:
        return None
    text, ts = item
    if _now() - ts > _CB_TEXT_TTL:
        _CB_TEXT_CACHE.pop(token, None)
        return None
    return text


def pack_cb(prefix: str, *parts) -> str:
    """Pack callback_data as 'prefix:<...>' and ensure <= 64 bytes in UTF-8."""
    # Convert all parts to strings to handle integers, floats, etc.
    str_parts = [str(part) for part in parts]
    s = DELIM.join([prefix] + str_parts)
    
    # Ensure within Bot API 64-byte limit
    if len(s.encode("utf-8")) > 64:
        s = s.encode("utf-8")[:64].decode("utf-8", errors="ignore")
    return s



def parse_cb(data: str, expected_prefix: str, min_parts: int = 1) -> list[str]:
    """Parse callback_data and return parts after prefix."""
    parts = data.split(DELIM)
    if not parts or parts[0] != expected_prefix or len(parts) - 1 < min_parts:  # Change parts != to parts[0] !=
        raise ValueError("Invalid callback data")
    return parts[1:]


async def _get_lock_for_message(message_id: int) -> asyncio.Lock:
    lock = _LOCKS_BY_MSG.get(message_id)
    if not lock:
        lock = asyncio.Lock()
        _LOCKS_BY_MSG[message_id] = lock
    return lock


async def generate_episode_markup(anime_id: str, text: str, page: int = 1) -> InlineKeyboardMarkup:
    """
    Generate an InlineKeyboardMarkup for episodes of a given anime_id with pagination.
    - Uses cached token for 'text' to keep callback_data small and safe.
    - Handles empty episode lists gracefully.
    """
    anime_data = await get_variable("anime")  # expected: {anime_id: {ep_num_str: ...}}
    eps_map = (anime_data or {}).get(anime_id, {})
    eps = sorted(eps_map.keys(), key=lambda x: int(x))  # assumes ep keys are numeric strings
    total_eps = len(eps)

    if total_eps == 0:
        # Only "Back" button
        tok = cache_text(text or "")
        back = [[InlineKeyboardButton("🔙 Back", callback_data=pack_cb("info", anime_id, tok))]]
        return InlineKeyboardMarkup(back)

    total_pages = ceil(total_eps / PER_PAGE)
    page = max(1, min(page, total_pages))

    start = (page - 1) * PER_PAGE
    end = min(start + PER_PAGE, total_eps)
    page_eps = eps[start:end]

    tok = cache_text(text or "")
    buttons: list[list[InlineKeyboardButton]] = []

    # Build episodes grid
    for row in range(ROWS):
        row_buttons = []
        for col in range(COLS):
            idx = row * COLS + col
            if idx >= len(page_eps):
                break
            ep = page_eps[idx]
            # showep:<anime_id>:<ep>:<tok>
            cb_data = pack_cb("showep", anime_id, str(ep), tok)
            row_buttons.append(InlineKeyboardButton(text=str(ep), callback_data=cb_data))
        if row_buttons:
            buttons.append(row_buttons)

    # Navigation
    if total_pages > 1:
        prev_page = page - 1 if page > 1 else total_pages
        next_page = page + 1 if page < total_pages else 1
        nav_row = [
            InlineKeyboardButton("⏮️", callback_data=pack_cb("epi.page", anime_id, str(prev_page), tok)),
            InlineKeyboardButton(f"{page}/{total_pages}", callback_data=pack_cb("noop", "x")),
            InlineKeyboardButton("⏭️", callback_data=pack_cb("epi.page", anime_id, str(next_page), tok)),
        ]
        buttons.append(nav_row)

    # Back
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data=pack_cb("info", anime_id, tok))])

    return InlineKeyboardMarkup(buttons)


# Handlers

async def episode_page_handler(client, callback_query):
    """
    Handles pagination: callback_data = 'epi.page:<anime_id>:<page>:<tok>'
    - Answers callback immediately to avoid timeout/progress bar.
    - Serializes edits per message to avoid races & 'not modified'.
    - Obeys FloodWait on heavy interaction.
    """
    log.info(f"Episode page handler called: {callback_query.data}")  # Add this line
    try:
        await callback_query.answer(cache_time=0)
    except Exception as e:
        # Non-fatal; proceed. Some runtimes cache or ignore late answers.
        log.warning(f"answer() failed: {e}")

    try:
        anime_id, page_s, tok = parse_cb(callback_query.data, expected_prefix="epi.page", min_parts=3)[:3]
        page = int(page_s)
    except Exception:
        # Fallback: ignore
        return

    text = get_cached_text(tok) or ""

    markup = await generate_episode_markup(anime_id, text, page)

    lock = await _get_lock_for_message(callback_query.message.id)
    async with lock:
        try:
            await callback_query.edit_message_reply_markup(reply_markup=markup)
        except MessageNotModified:
            # Nothing changed; ignore gracefully
            pass
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await callback_query.edit_message_reply_markup(reply_markup=markup)
            except MessageNotModified:
                pass


# bot/basic/episode.py

async def episode_list_handler(client, q):
    # Always acknowledge quickly to clear spinner and reduce duplicate taps
    try:
        await q.answer(cache_time=0)
    except Exception:
        pass

    data = (q.data or "").strip()
    anime_id = None
    text_tok = None

    # New compact format: 'epi.list:<anime_id>:<tok>'
    if data.startswith("epi.list"):
        parts = data.split(":", 2)  # ['epi.list', '<id>', '<tok or rest>']
        if len(parts) == 3 and parts[1]:
            anime_id, text_tok = parts[1], parts[2]  # Use parts[1] and parts[2], NOT parts[14] and parts[10]
    
    # Legacy format: 'epi_<anime_id>_<text>'
    if anime_id is None and data.startswith("epi_"):
        parts = data.split("_", 2)  # ['epi', '<id>', '<text or rest>']
        if len(parts) == 3 and parts[1]:
            anime_id, text_tok = parts[1], parts[2]  # Use parts[1] and parts[2], NOT parts[14] and parts[10]

    if not anime_id:
        try:
            await q.answer("Invalid or expired button.", show_alert=False, cache_time=2)
        except Exception:
            pass
        return

    # Continue with existing logic...
    anime_data = await get_variable("anime")
    if anime_data is None or anime_id not in anime_data or not anime_data[anime_id]:
        requests = await get_variable("requests") or {}
        requests_count = len(requests.get(anime_id, []))
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"ʀᴇQᴜᴇꜱᴛ ᴀɴɪᴍᴇ {requests_count}", callback_data=pack_cb("request", anime_id))],
            [InlineKeyboardButton("🔙 Back", callback_data=pack_cb("info", anime_id, text_tok or "x"))],
        ])
        await q.message.edit(
            "<blockquote>ꜱᴏʀʀʏ ʏᴏᴜʀ ʀᴇQᴜᴇꜱᴛᴇᴅ ᴀɴɪᴍᴇ ɪꜱ ɴᴏᴛ ᴀᴡᴀɪʟᴀʙʟᴇ ʏᴇᴛ \n\n"
            f"Total requests: {requests_count}\n\n"
            "👇 ᴘʟᴇᴀꜱᴇ ʀᴇQᴜᴇꜱᴛ ꜰᴏʀᴍ ʙᴇʟᴏᴡ 👇</blockquote>",
            reply_markup=keyboard,
        )
        return

    try:
        text = get_cached_text(text_tok) or ""
        markup = await generate_episode_markup(anime_id, text, page=1)
    except Exception as e:
        await q.message.edit(f"Error generating episode markup: {e}")
        return

    try:
        anime_info = await get_anime_info(anime_id)
    except Exception as e:
        await q.message.edit(f"Error retrieving anime information: {e}")
        return

    if not anime_info:
        await q.message.edit("Error retrieving anime information.")
        return

    title, episodes = anime_info

    lock = await _get_lock_for_message(q.message.id)
    async with lock:
        try:
            await q.message.edit(
                text=(
                    f"🎬 <b>{title} </b><i>(ID:{anime_id})</i>"
                    f"<b> - Total Episode {episodes}</b>\n\nSelect an Episode to download:"
                ),
                reply_markup=markup,
            )
        except MessageNotModified:
            pass
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await q.message.edit(
                    text=(
                        f"🎬 <b>{title} </b><i>(ID:{anime_id})</i>"
                        f"<b> - Total Episode {episodes}</b>\n\nSelect an Episode to download:"
                    ),
                    reply_markup=markup,
                )
            except MessageNotModified:
                pass


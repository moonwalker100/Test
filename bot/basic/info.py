import asyncio
from pyrogram.errors import MessageNotModified, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from bot.basic.search import getinfo
from bot.decorator import task
from bot.logger import LOGGER
from database import get_variable

log = LOGGER(__name__)

# Use compact, safe callback packing (kept minimal here)
DELIM = ":"
def pack_cb(prefix: str, *parts: str) -> str:
    s = DELIM.join((prefix, *map(str, parts)))
    # Telegram Bot API requires 1–64 bytes; trim if ever exceeded
    if len(s.encode("utf-8")) > 64:
        s = s.encode("utf-8")[:64].decode("utf-8", errors="ignore")
    return s

def parse_info_data(data: str):
    """
    Accepts both:
      - legacy: 'info_<anime_id>[_<prev_id>]'
      - new:    'info:<anime_id>[:<prev_id>]'
    Returns (anime_id, prev_id or None) or (None, None) if invalid.
    """
    if not data:
        return None, None
    if data.startswith("info:"):
        parts = data.split(":", 3)
        # info:<anime_id>[:<prev_id>]
        anime_id = parts[1] if len(parts) > 1 else None
        prev_id = parts[2] if len(parts) > 2 and parts[2] else None
        return anime_id, prev_id
    if data.startswith("info_"):
        parts = data.split("_", 2)
        # info_<anime_id>[_<prev_id>]
        anime_id = parts[1] if len(parts) > 1 else None
        prev_id = parts[2] if len(parts) > 2 and parts[2] else None
        return anime_id, prev_id
    return None, None


@task
async def info(c, q):
    # Acknowledge quickly to clear the client's loading spinner
    try:
        await q.answer(cache_time=0)
    except Exception as e:
        log.debug(f"answer() failed: {e}")

    data = q.data or ""
    anime_id, prev_id = parse_info_data(data)
    if not anime_id:
        # Fallback: try very old format 'inf_<anime_id>'
        parts = data.split("_", 1)
        anime_id = parts[1] if len(parts) == 2 else None
        if not anime_id:
            return

    # Ensure anime data is warm in cache (if needed by downstream)
    await get_variable("anime", {})

    try:
        link, caption, prequel, sequel, current_episode, status = await getinfo(anime_id)
    except Exception as e:
        log.error(f"getinfo failed for {anime_id}: {e}")
        return

    log.info(f"status={status}, current_episode={current_episode}")

    buttons = []

    # Navigation: Prequel / Sequel (compact callbacks, include current as prev_id)
    nav_row = []
    if prequel:
        nav_row.append(
            InlineKeyboardButton(
                "⬅️ Prequel",
                callback_data=pack_cb("info", prequel, anime_id),
            )
        )
    if sequel:
        nav_row.append(
            InlineKeyboardButton(
                "Sequel ➡️",
                callback_data=pack_cb("info", sequel, anime_id),
            )
        )
    if nav_row:
        buttons.append(nav_row)

    # Episodes entry: use new compact epi.list; token not required here, pass a small placeholder
    buttons.append(
        [InlineKeyboardButton("📺 Watch Episodes", callback_data=pack_cb("epi.list", anime_id, "x"))]
    )

    # Back to search/index (keep legacy if existing flows rely on it)
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data=f"bto_{anime_id}")])

    keyboard = InlineKeyboardMarkup(buttons)

    # Edit media safely: handle FloodWait, and skip no-op changes
    media = InputMediaPhoto(media=link, caption=caption)
    try:
        await q.message.edit_media(media=media, reply_markup=keyboard)
    except MessageNotModified:
        # Media/caption unchanged; try updating just the buttons
        try:
            await q.message.edit_reply_markup(reply_markup=keyboard)
        except MessageNotModified:
            pass
    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            await q.message.edit_media(media=media, reply_markup=keyboard)
        except MessageNotModified:
            try:
                await q.message.edit_reply_markup(reply_markup=keyboard)
            except MessageNotModified:
                pass

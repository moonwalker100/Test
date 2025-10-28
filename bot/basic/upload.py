import asyncio
import re

import pyrogram.utils
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from bot.basic.search import get_anime_name, getinfo
from bot.basic.search import search as xi
from bot.config import DB_CHANNEL
from bot.decorator import task
from bot.logger import LOGGER
from database import get_variable, set_variable

from .request import onupload
from .sequence import sequence

log = LOGGER(__name__)
pyrogram.utils.MIN_CHANNEL_ID = -100914748364741
pyrogram.utils.MAX_CHANNEL_ID = -1000000000000


# Listener store: user_id -> asyncio.Task
active_listeners = {}


def add_or_update_quality(
    anime_data: dict, anime_id: str, episode: int, quality: str, link: str
):
    anime_id = str(anime_id)
    episode = str(episode)

    # Ensure anime_id exists
    if anime_id not in anime_data:
        anime_data[anime_id] = {}

    # Ensure episode exists under anime_id
    if episode not in anime_data[anime_id]:
        anime_data[anime_id][episode] = {}

    # Update or add quality under episode
    anime_data[anime_id][episode][quality] = link


def count(anime_dict: dict, anime_id: str):
    if anime_id not in anime_dict:
        return 0, 0, 0, 0

    episodes = anime_dict[anime_id]
    c_480, c_720, c_1080, c_hdrip = 0, 0, 0, 0

    for ep_data in episodes.values():
        if "480p" in ep_data:
            c_480 += 1
        if "720p" in ep_data:
            c_720 += 1
        if "1080p" in ep_data:
            c_1080 += 1
        if "hdrip" in ep_data:
            c_hdrip += 1

    return c_480, c_720, c_1080, c_hdrip


@task
async def upload(client, message, query=False, ongoing=0):
    admin = await get_variable("admin", [])
    if query:
        text = message
        if query.from_user.id not in admin:
            return
    else:
        if message.from_user.id not in admin:
            return
        if ongoing:
            text = message.text.removeprefix("/ongoing ")
        else:
            text = message.text.removeprefix("/upload ")
        text = text
    reply = await xi(text)  # Assuming xi is your anime search function

    if not reply:
        await message.reply_text(text="No results found.")
        return
    keyboard = []
    for anime_title, anime_id in reply:
        if anime_id is None or anime_title is None:
            log.warning(f"Skipping anime due to missing id or title: {anime_title}")
            continue  # Skip this anime if id or title is missing
        if not ongoing:
            button = InlineKeyboardButton(
                anime_title, callback_data=f"upload_{anime_id}_{text}"
            )
        else:
            button = InlineKeyboardButton(
                anime_title, callback_data=f"ongoing_{anime_id}_{text}"
            )
        keyboard.append([button])  # Each button on a new row

    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        try:
            await query.message.edit_media(
                media=InputMediaPhoto(
                    media="https://i.ibb.co/93zWxT5z/c33639521bf3.png",
                    caption="Choose an anime from Below:",
                ),
                reply_markup=reply_markup,
            )
        except Exception as e:
            log.error(f"Error sending message: {e}")
        return
    try:
        await message.reply_photo(
            photo="https://i.ibb.co/93zWxT5z/c33639521bf3.png",
            caption="Choose an anime for more information:",
            reply_markup=reply_markup,
        )
    except Exception as e:
        log.error(f"Error sending message: {e}")


@task
async def uploadinfo(c, q, m=0):
    get = q.data.split("_")

    # Ensure get has at least 3 elements
    while len(get) < 3:
        get.append("")

    # Set default value for get[2] if missing
    if not get[2]:
        get[2] = "naruto"

    # Set ani_id
    if m:
        try:
            ani_id = int(q.data.removeprefix("freepi"))
        except ValueError:
            return  # Invalid format, do nothing
        get[1] = str(ani_id)  # Replace get[1] with ani_id as string
    else:
        ani_id = get[1]

    get2 = get[2]
    anime_id = ani_id
    anime = await get_variable("anime", {})
    freepi = await get_variable(f"freepi{ani_id}", 3)
    if ani_id in anime:
        status = "ᴜᴘʟᴏᴀᴅᴇᴅ ✅"
    else:
        status = "ɴᴏᴛ ᴜᴘʟᴏᴀᴅᴇᴅ ❌"
    title, prequel, sequel, episodes, statuso = await getinfo(ani_id, upload=1)
    c480p, c720p, c1080p, chdrip = count(anime, ani_id)
    text = f'<blockquote expandable>Upload status :- {status}</blockquote>\n<blockquote expandable>Anime Title :- {title} (ID:{ani_id})</blockquote>\n<blockquote expandable>Anime Status :- {statuso}</blockquote>\n<blockquote expandable>Total episodes :- {episodes}</blockquote>\n<blockquote expandable>Free episodes :- {freepi}</blockquote>\n<blockquote expandable>Developed by <a href="tg://user?id=7024179022">Argon</a></blockquote>'
    buttons = []
    nav_buttons = []

    buttons.append(
        [
            InlineKeyboardButton(
                f"480p ({c480p})", callback_data=f"up_480p_{episodes}_{anime_id}"
            ),
            InlineKeyboardButton(
                f"720p ({c720p})", callback_data=f"up_720p_{episodes}_{anime_id}"
            ),
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                f"1080p ({c1080p})", callback_data=f"up_1080p_{episodes}_{anime_id}"
            ),
            InlineKeyboardButton(
                f"HDRip ({chdrip})", callback_data=f"up_hdrip_{episodes}_{anime_id}"
            ),
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                f"🎗 Free Episodes ({freepi})", callback_data=f"freepi{anime_id}"
            )
        ]
    )
    if prequel and get2:
        nav_buttons.append(
            InlineKeyboardButton("⬅️ Prequel", callback_data=f"upload_{prequel}_{get2}")
        )
    if sequel and get2:
        nav_buttons.append(
            InlineKeyboardButton(
                "Sequel ➡️",
                callback_data=f"upload_{sequel}_{
                    get2}",
            )
        )
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data=f"upto_{get2}")])

    markup = InlineKeyboardMarkup(buttons)
    if m:
        await m.edit_media(
            media=InputMediaPhoto(
                media=f"https://img.anili.st/media/{ani_id}", caption=text
            ),
            reply_markup=markup,
        )
        return

    await q.message.edit_media(
        media=InputMediaPhoto(
            media=f"https://img.anili.st/media/{ani_id}", caption=text
        ),
        reply_markup=markup,
    )


active_listeners = {}


async def collector(client: Client, msg: Message):
    """
    Global handler to collect documents from users who are in listening mode.
    """
    user_id = msg.from_user.id

    # If user isn't in active list, ignore
    if user_id not in active_listeners:
        msg.continue_propagation()
        return

    session = active_listeners[user_id]
    messages = session["messages"]
    stop_event = session["event"]
    total = session["total"]
    # Assuming you store the target channel ID here
    session.get("channel_id")

    # Handle /stop command
    if msg.text and msg.text.strip() == "/stop":
        await msg.reply_text("Listener stopped.")
        stop_event.set()
        msg.stop_propagation()
        return

    if msg.document:

        messages.append(msg)
        log.info(
            "Collected and copied document from %s (%d/%d)",
            user_id,
            len(messages),
            total,
        )
        # Stop collecting if limit reached
        if len(messages) >= total:
            stop_event.set()

    msg.stop_propagation()


async def fed(client: Client, callback_query: CallbackQuery):
    """
    Entry point for feeding episodes. Callback data format: fed_<quality>_<total>_<anime_id>
    """
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    _, quality, episodes_str, anime_id = callback_query.data.split("_")
    total_episodes = int(episodes_str)

    # Prevent duplicate listeners
    if user_id in active_listeners:
        await callback_query.answer(
            "Already awaiting your episodes. Send /stop to cancel.", show_alert=True
        )
        return

    # Prompt user to send documents
    await callback_query.message.reply_text(
        f"Please send or forward **{total_episodes}** episodes as documents.\n"
        "Send `/stop` to finish early.",
        quote=True,
    )

    # Initialize listening session
    stop_event = asyncio.Event()
    active_listeners[user_id] = {
        "messages": [],
        "event": stop_event,
        "total": total_episodes,
    }

    # Wait until enough docs or user stops
    try:
        await stop_event.wait()
        messages = active_listeners[user_id]["messages"]
    finally:
        # Clean up session
        active_listeners.pop(user_id, None)
    mob = []
    for msg in messages:
        try:
            # Copy to target channel
            copied = await client.copy_message(
                chat_id=DB_CHANNEL, from_chat_id=msg.chat.id, message_id=msg.id
            )
        except FloodWait as e:
            # If a FloodWait is caught, wait for the specified amount of time
            log.warning(
                f"FloodWait encountered. Sleeping for {
                    e.value} seconds."
            )
            await asyncio.sleep(e.value)
            # Then, retry copying the message
            copied = await client.copy_message(
                chat_id=DB_CHANNEL, from_chat_id=msg.chat.id, message_id=msg.id
            )
        mob.append(copied)
    messages = sequence(mob)
    # Notify and process
    await client.send_message(
        chat_id, f"✅ Collected {len(messages)} document(s). Processing now..."
    )
    anime = await get_variable("anime", {})
    log.info(f"Before edit {anime}")
    if not anime:
        anime = {}
    for msg, i in messages:
        add_or_update_quality(anime, anime_id, i, quality, msg.id)
    await set_variable("anime", anime)
    title = await get_anime_name(anime_id)
    data = f"{title}-{anime_id}"
    name = await get_variable("namelist", [])
    if data not in name:
        name.append(data)
        await set_variable("namelist", name)
        log.info(f"Added {data} to namelist\n namelist={name}")
    await onupload(client, anime_id)


EPISODES_PER_PAGE = 50


@task
async def ongoing_choose_anime(c: Client, q):
    _, anime_id, _ = q.data.split("_", 2)
    title, prequel, sequel, total_eps, status = await getinfo(anime_id, upload=1)

    total_eps = int(total_eps)
    total_pages = (total_eps + EPISODES_PER_PAGE - 1) // EPISODES_PER_PAGE
    current_page = total_pages  # Start from the last page

    start_ep = (current_page - 1) * EPISODES_PER_PAGE + 1
    end_ep = min(current_page * EPISODES_PER_PAGE, total_eps)

    # Create buttons for this page
    buttons = [
        InlineKeyboardButton(
            str(ep), callback_data=f"ongoing_ep_{anime_id}_{ep}_{title}"
        )
        for ep in range(start_ep, end_ep + 1)
    ]

    # Arrange in rows of 5
    button_rows = [buttons[i : i + 5] for i in range(0, len(buttons), 5)]

    # Add navigation buttons if needed
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                "⬅️ Prev",
                callback_data=f"page_{anime_id}_{
                    current_page -
                    1}_{title}",
            )
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                "Next ➡️",
                callback_data=f"page_{anime_id}_{
                    current_page +
                    1}_{title}",
            )
        )
    if nav_buttons:
        button_rows.append(nav_buttons)

    markup = InlineKeyboardMarkup(button_rows)

    await q.message.edit_caption(
        caption=f"📺 {title} has {total_eps} episodes.\nChoose one to upload (Page {current_page}/{total_pages}):",
        reply_markup=markup,
    )


@task
async def ongoing_choose_episode(c: Client, q):
    _, _, anime_id, episode_str, title = q.data.split("_")
    ep_num = int(episode_str)
    user = q.from_user.id

    # Notify user
    await q.message.reply_text(
        f"📥 Send or forward **files for Episode {ep_num}**.\n"
        "Qualities will be auto-detected from filename or file size.\n"
        "Send `/stop` when finished."
    )

    # Setup one-time listener
    stop = asyncio.Event()
    active_listeners[user] = {
        "ep": ep_num,
        "anime": anime_id,
        "event": stop,
        "total": 4,
        "messages": [],
    }

    await stop.wait()

    # Collect and cleanup
    session = active_listeners.pop(user)
    msgs = session["messages"]
    anime = await get_variable("anime", {}) or {}
    if not len(msgs):
        return
    log.info(len(msgs))
    for msg in msgs:
        fname = msg.document.file_name.lower()
        fname = re.sub(r"[\[\(\{<].*?[\]\)\}>]", "", fname)
        fname = re.sub(r"[^a-z0-9.\s_-]", "", fname)
        fname = re.sub(r"[\s_]+", " ", fname)
        fname = fname.strip()
        size = msg.document.file_size
        if msg.document.caption:
            cname = msg.document.caption.lower()
            cname = re.sub(r"[\[\(\{<].*?[\]\)\}>]", "", cname)
            cname = re.sub(r"[^a-z0-9.\s_-]", "", cname)
            cname = re.sub(r"[\s_]+", " ", cname)
            cname = cname.strip()

        # Prefer quality from filename
        fname = f"{fname} {cname}".lower()
        if "1080" in fname:
            quality = "1080p"
        elif "720" in fname:
            quality = "720p"
        elif "480" in fname:
            quality = "480p"
        elif "hdrip" in fname:
            quality = "hdrip"
        else:
            # Fallback: use file size
            if size > 1.4 * 1024 * 1024 * 1024:  # >1.4GB
                quality = "1080p"
            elif size > 700 * 1024 * 1024:  # >700MB
                quality = "720p"
            elif size > 300 * 1024 * 1024:  # >300MB
                quality = "480p"
            else:
                quality = "hdrip"

        # Copy to DB channel
        copied = await c.copy_message(DB_CHANNEL, msg.chat.id, msg.id)
        add_or_update_quality(anime, anime_id, ep_num, quality, copied.id)

    await set_variable("anime", anime)
    name = await get_variable("namelist", [])
    if title not in name:
        name.append(title)
        await set_variable("namelist", name)
    await q.message.reply_text(f"✅ Episode {ep_num} saved with {len(msgs)} file(s).")
    await onupload(c, anime_id)


async def switch_page(c: Client, q: CallbackQuery):
    try:
        # Parse the callback data
        parts = q.data.split("_", 3)
        anime_id = parts[1]
        page = int(parts[2])
        title = parts[3]
    except Exception:
        await q.answer("Invalid callback data", show_alert=True)
        return

    # Fetch total episodes
    _, _, _, total_eps, _ = await getinfo(anime_id, upload=1)
    total_eps = int(total_eps)
    total_pages = (total_eps + EPISODES_PER_PAGE - 1) // EPISODES_PER_PAGE

    start_ep = (page - 1) * EPISODES_PER_PAGE + 1
    end_ep = min(page * EPISODES_PER_PAGE, total_eps)

    # Generate episode buttons
    buttons = [
        InlineKeyboardButton(
            str(ep), callback_data=f"ongoing_ep_{anime_id}_{ep}_{title}"
        )
        for ep in range(start_ep, end_ep + 1)
    ]
    button_rows = [buttons[i : i + 5] for i in range(0, len(buttons), 5)]

    # Navigation buttons
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                "⬅️ Prev", callback_data=f"page_{anime_id}_{page - 1}_{title}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                "Next ➡️", callback_data=f"page_{anime_id}_{page + 1}_{title}"
            )
        )
    if nav_buttons:
        button_rows.append(nav_buttons)

    markup = InlineKeyboardMarkup(button_rows)

    await q.message.edit_caption(
        caption=f"📺 {title} has {total_eps} episodes.\nChoose one to upload (Page {page}/{total_pages}):",
        reply_markup=markup,
    )

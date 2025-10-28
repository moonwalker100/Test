import pyrogram.utils
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from bot.basic.search import search as xi
from bot.config import poster
from bot.decorator import task
from bot.logger import LOGGER
from database import get_variable, set_variable

log = LOGGER(__name__)
pyrogram.utils.MIN_CHANNEL_ID = -100914748364741
pyrogram.utils.MAX_CHANNEL_ID = -1000000000000


@task
async def search(client, message, admin=False, query=False, group=0):
    """
    Searches for anime and sends a message with inline keyboard buttons for each result,
    but only if they are in the namelist variable.
    """
    if query:
        text = message
    else:
        text = message.text

    if group:
        if " " in text:
            text = text.split(" ", 1)[1]
        else:
            await message.reply_text(
                "<blockquote>❌ 𝐰𝐫𝐨𝐧𝐠 𝐟𝐨𝐫𝐦𝐚𝐭𝐞  \n\n𝐩𝐥𝐞𝐚𝐬𝐞 𝐮𝐬𝐞 𝐟𝐨𝐫𝐦𝐚𝐭𝐞 /search Animename</blockquote>"
            )
            return

    log.info(f"text={text}")

    # Step 1: Fetch allowed namelist
    namelist = await get_variable("namelist", [])  # Format: ['anime-name1-id1', 'anime-name2-id2', ...]

    # Step 2: Extract allowed anime IDs from namelist
    allowed_ids = {entry.split("-")[-1] for entry in namelist if "-" in entry}

    # Step 3: Perform search
    reply = await xi(text)  # Expected format: [(anime_title, anime_id), ...]

    if not reply:
        if query:
            await query.message.reply_text(text="No results found.")
        else:    
            await message.reply_text(text="No results found.")
        return

    # Step 4: Filter results
    keyboard = []
    for anime_title, anime_id in reply:
        if not anime_title or not anime_id:
            log.warning(f"Skipping anime due to missing id or title: {anime_id}, {anime_title}")
            continue

        if str(anime_id) not in allowed_ids:
            log.info(f"Skipping '{anime_title}' (ID: {anime_id}) not in namelist.")
            continue

        button = InlineKeyboardButton(
            anime_title, callback_data=f"info_{anime_id}_{text}"
        )
        keyboard.append([button])  # Each button on a new row

    if not keyboard:
        if query:
            await query.message.reply_text("No matching results found in the list.")
        else:
            await message.reply_text("No matching results found in the list.")
        
        return

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if query:
            await query.message.edit_media(
                media=InputMediaPhoto(
                    media=poster,
                    caption="Choose an anime from below:",
                ),
                reply_markup=reply_markup,
            )
        else:
            await message.reply_photo(
                photo=poster,
                caption="Choose an anime for more information:",
                reply_markup=reply_markup,
            )
    except Exception as e:
        log.error(f"Error sending message: {e}")


import asyncio
import json
import os
import re
from math import ceil

from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.config import poster, text_go
from bot.logger import LOGGER
from database import get_variable, set_variable

from .search import get_anime_name as get_name

log = LOGGER(__name__)

# Constants
ITEMS_PER_PAGE = 9

# --- Command: /awailable ---


async def awailable_command(client, message, query=0, edit=0):
    keyboard = []
    row = []

    namelist = await get_variable("namelist", [])
    if edit:
        ugd = "iedcawl_"  # Shortened from "idecawail_"
    else:
        ugd = "awl_"      # Shortened from "awail_"
    
    for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1):
        row.append(
            InlineKeyboardButton(text=letter, callback_data=f"{ugd}{letter}")
        )
        if i % 6 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    if edit:
        keyboard.append(
            [InlineKeyboardButton(text_go("️Back 🔙"), callback_data="home")]
        )

    if query:
        await query.message.edit(
            text="🔤 *Select a letter to view available anime:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return
    if edit:
        await edit.message.edit(
            text=text_go(
                f"🔤 anime index \n <blockquote>total uploads = ✨{
                    len(namelist)}✨ </blockquote>"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return
    await message.reply_photo(
        photo=poster,
        caption=text_go("🔤 *Select a letter to view available anime:*"),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
async def awailable_command(client, message, query=0, edit=0):
    keyboard = []
    row = []

    namelist = await get_variable("namelist", [])
    if edit:
        ugd = "iedcawl_"  # Shortened from "idecawail_"
    else:
        ugd = "awl_"      # Shortened from "awail_"
    
    for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1):
        row.append(
            InlineKeyboardButton(text=letter, callback_data=f"{ugd}{letter}")
        )
        if i % 6 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    if edit:
        keyboard.append(
            [InlineKeyboardButton(text_go("️Back 🔙"), callback_data="home")]
        )

    if query:
        await query.message.edit(
            text="🔤 *Select a letter to view available anime:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return
    if edit:
        await edit.message.edit(
            text=text_go(
                f"🔤 anime index \n <blockquote>total uploads = ✨{
                    len(namelist)}✨ </blockquote>"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return
    await message.reply_photo(
        photo=poster,
        caption=text_go("🔤 *Select a letter to view available anime:*"),
        reply_markup=InlineKeyboardMarkup(keyboard),
            )
    

async def paginate_anime_list(client, cq: CallbackQuery):
    # Update regex to handle both old and new shortened formats
    match = re.match(
        r"^(?:awail_|idecawail_|awl_|iedcawl_)([A-Z])(?:_(?:page_|p_)(\d+))?$",
        cq.data,
    )
    if not match:
        log.info(f"Invalid callback data received: {cq.data}")
        return await cq.answer("Invalid callback data.", show_alert=True)

    letter = match.group(1)
    page = int(match.group(2)) if match.group(2) else 1
    log.info(f"Paginating anime list for letter '{letter}' at page {page}")

    namelist = await get_variable("namelist") or []
    log.info(f"Fetched namelist with {len(namelist)} items")

    matching = []
    for item in namelist:
        try:
            name, anime_id = item.rsplit("-", 1)
        except ValueError:
            log.info(f"Skipping malformed entry: {item}")
            continue
        if name.upper().startswith(letter.upper()):
            matching.append((anime_id, name))

    log.info(f"Found {len(matching)} anime starting with letter '{letter}'")

    matching.sort(key=lambda x: x[1])
    total = len(matching)
    pages = ceil(total / ITEMS_PER_PAGE) if total else 1
    page = max(1, min(page, pages))

    if total == 0:
        log.info(f"No matching anime for letter '{letter}'")
        return await cq.answer(f"No anime starting with '{letter}'", show_alert=True)

    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = matching[start:end]

    log.info(f"Displaying items {start} to {end} on page {page}")

    # Create anime buttons (without name in callback to stay under 64 bytes)
    keyboard = [
        [InlineKeyboardButton(text=name, callback_data=f"inf_{aid}")]
        for aid, name in page_items
    ]

    # Navigation buttons with page information preserved
    nav = []
    if page > 1:
        nav.append(
            InlineKeyboardButton(
                text_go("⬅️ Prev"),
                callback_data=f"awl_{letter}_p_{page - 1}",  # Keep page info
            )
        )
    if page < pages:
        nav.append(
            InlineKeyboardButton(
                text_go("Next ➡️"),
                callback_data=f"awl_{letter}_p_{page + 1}",  # Keep page info
            )
        )
    if nav:
        keyboard.append(nav)
    
    # Back buttons
    if cq.data.startswith(("idecawail_", "iedcawl_")):
        keyboard.append(
            [InlineKeyboardButton(text_go("Back 🔙"), callback_data="bti")]
        )
    else:
        keyboard.append(
            [InlineKeyboardButton(text_go("Back 🔙"), callback_data="bta")]
        )
    
    await cq.message.edit(
        text=f"📚 Anime starting with <b>{letter}</b> (Page {page}/{pages}):",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    

# --- Callback: select_{id} ---


async def handle_anime_selection(client, cq):
    anime_id = cq.matches[0].group(1)
    name = await get_name(anime_id)
    await cq.answer(f"Selected: {name}", show_alert=True)
    # Optionally, you can also edit the message or send more info:
    # await cq.message.edit_text(f"You selected: {name} (ID: {anime_id})")


async def parse(client, message: Message):
    # Ensure it's a document
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply_text("❌ Please reply to a JSON document.")

    file_path = await message.reply_to_message.download()

    try:
        # Load JSON file
        with open(file_path, "r") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return await message.reply_text("❌ Invalid JSON structure (not a dict).")

        ids = list(data.keys())
        names = []

        # Define backoff parameters
        max_retries = 5
        base_delay = 5  # in seconds

        for aid in ids:
            for attempt in range(1, max_retries + 1):
                name = await get_name(aid)
                if name and ("Too Many Requests" not in name):
                    names.append(f"{name}-{aid}")
                    await asyncio.sleep(0.5)  # avoid rate limiting
                    break
                elif name and ("Too Many Requests" in name):
                    delay = base_delay * (2 ** (attempt - 1))
                    log.warning(
                        f"429-like response for {aid}, retrying in {
                            delay:.2f}s (attempt {attempt}/{max_retries})"
                    )
                    await asyncio.sleep(delay)
                else:
                    log.error(f"No valid name for {aid} or unexpected response: {name}")
                    break

        if not names:
            return await message.reply_text("❌ No valid names found.")

        preview = "\n".join(names[:10]) + ("\n..." if len(names) > 10 else "")
        await message.reply_text(f"✅ Parsed {len(names)} names:\n\n`{preview}`")

        await set_variable("namelist", names)
        log.info(f"Stored {len(names)} names in variable 'namelist'.")

    except Exception as e:
        log.exception("Unexpected error parsing JSON document.")
        await message.reply_text(f"❌ Failed to parse JSON: `{e}`")


async def load_command(Client, message):
    if not message.reply_to_message.document.file_name.endswith(".json"):
        return await message.reply("Please send a valid `.json` file.")

    file_path = await message.reply_to_message.download()

    # Read and parse JSON
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        return await message.reply(f"Failed to load JSON: {e}")

    # Save to database
    await set_variable("anime", data)

    # Optional: Clean up the file
    os.remove(file_path)

    await message.reply("✅ Anime data has been successfully loaded and saved.")
    log.info("Loaded anime data from JSON file.")

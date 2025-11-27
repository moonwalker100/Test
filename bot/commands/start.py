import random
from datetime import datetime, timedelta

import pyrogram.utils
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto

from bot.config import START_MESSAGE, images, text_go, SUPPORT_TEXT
from bot.decorator import task
from bot.logger import LOGGER
from database import add_user, get_variable, present_user, set_variable
from bot.basic.epi import file, decode, parse_get_data

log = LOGGER(__name__)
pyrogram.utils.MIN_CHANNEL_ID = -10091474836474
pyrogram.utils.MAX_CHANNEL_ID = -1000000000000


@task
async def start(client, message, query=False):
    if not await present_user(message.from_user.id):
        # Add the user to the database
        await add_user(message.from_user.id)
    now = datetime.now()
    text = message.text
    user_id = message.from_user.id
    if " " in text:
        text = text.split(" ", 1)[1]
    if text.startswith("get_"):
        fileid, anime_id, episode = parse_get_data(text)
        await file(client, q=0, filei=fileid, uuid=user_id, anime_id=anime_id, episode=episode, verify=0, message=message)
    if text.startswith("verify_"):
        string = text.removeprefix("verify_")
        string = decode(string)
        _, fileid, anime_id, episode = string.split("_")
        await file(
            client,
            message=message,
            filei=fileid,
            uuid=message.from_user.id,
            anime_id=anime_id,
            episode=episode,
        )
        return
    if text.startswith("time_"):
        token = await get_variable(f"token{user_id}", "")
        if text == token:
            very = await get_variable("token_time", 0)
            time = now + timedelta(seconds=int(very))
            await set_variable(f"t{user_id}", time)
            await set_variable(f"token{user_id}", None)
            await message.reply_text("✅ 𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋")
            return
        else:
            log.info(f"I gey :-{text}, i want {token}")
            await message.reply_text("Invalid input")
            return
    else:
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=text_go("ɪɴᴅᴇx"), callback_data="index"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=text_go("ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ"), callback_data="prem"
                    ),
                    InlineKeyboardButton(
                        text=text_go("ꜱᴜᴘᴘᴏʀᴛ"), callback_data="contact"
                    ),
                ],
            ]
        )
        await message.reply_photo(
            photo=random.choice(images),
            caption=START_MESSAGE.format(message.from_user.mention()),
            reply_markup=reply_markup,
        )


async def home(client, message, query=False):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text_go("ɪɴᴅᴇx"), callback_data="index"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=text_go("ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ"), callback_data="prem"
                ),
                InlineKeyboardButton(
                    text=text_go("ꜱᴜᴘᴘᴏʀᴛ"), callback_data="contact"
                ),
            ],
        ]
    )
    mess = await message.message.edit_media(
        media=InputMediaPhoto(random.choice(images)), reply_markup=reply_markup
    )
    await mess.edit(
        START_MESSAGE.format(message.from_user.mention()), reply_markup=reply_markup
    )

async def contact(client, query=False):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text_go("ʜᴏᴍᴇ"), callback_data="home"
                ),
                InlineKeyboardButton(
                    text=text_go("ᴄᴀɴᴄᴇʟ"), callback_data="concel"
                ),
            ],
        ]
    )
    await query.message.edit(SUPPORT_TEXT, disable_web_page_preview=True, reply_markup=reply_markup)

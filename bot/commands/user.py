import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.decorator import task
from bot.logger import LOGGER
from database import del_user, full_userbase, get_variable

log = LOGGER(__name__)


@task
async def get_users(client, message):
    admin = await get_variable("admin", [])
    userid = message.from_user.id
    if userid not in admin:
        return
    msg = await client.send_message(chat_id=message.chat.id, text="Please wait.....")
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")


@task
async def send_text(client, message):
    admin = await get_variable("admin", [])
    userid = message.from_user.id
    if userid not in admin:
        return

    if not message.reply_to_message:
        return

    query = await full_userbase()
    broadcast_msg = message.reply_to_message

    total = successful = blocked = deleted = unsuccessful = edit = 0

    pls_wait = await message.reply(
        "<i>Select broadcast type</i>",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📢 Normal", callback_data="broadcast_normal"),
                    InlineKeyboardButton("📌 Pin", callback_data="broadcast_pin"),
                ]
            ]
        ),
    )

    try:
        callback = await client.wait_for_callback_query(
            chat_id=message.chat.id,
            filters=filters.user(message.from_user.id),
            timeout=30,
        )
    except asyncio.TimeoutError:
        return await pls_wait.edit("<i>⏰ Timed out. Please try again.</i>")

    await callback.answer()  # acknowledge the callback click

    pin = 1 if callback.data == "broadcast_pin" else 0
    await pls_wait.edit("<i>📤 Broadcast started...</i>")

    for chat_id in query:
        try:
            sent = await broadcast_msg.copy(chat_id)
            successful += 1
            if pin:
                try:
                    await sent.pin(both_sides=True)
                except Exception:
                    pass
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                sent = await broadcast_msg.copy(chat_id)
                successful += 1
            except BaseException:
                unsuccessful += 1
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except Exception:
            unsuccessful += 1
        total += 1
        edit += 1

        if edit >= 20:
            edit = 0
            status = """<b><u>Broadcast in progress</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
            await pls_wait.edit_text(status)

    status = """<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
    return await pls_wait.edit_text(status)

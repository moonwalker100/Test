from pyrogram.errors.pyromod.listener_timeout import ListenerTimeout
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from database import get_variable, set_variable


async def admin(client, message):
    a = await get_variable("admin", [])
    txt = f"<blockquote expandable>💠 𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋  ♻️\n</blockquote>\n<blockquote expandable>🚩 𝐀𝐃𝐌𝐈𝐍 :- {a}\n</blockquote>\n<blockquote expandable>⚠️ 𝐍𝐎𝐓𝐄 - ADMINS CAN USE ALL BOT COMMMANDS EXCEPT FSUB, ADMIN ‼️</blockquote>"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("𝐀𝐃𝐃 𝐀𝐃𝐌𝐈𝐍", callback_data="admin_add"),
                InlineKeyboardButton("𝐑𝐄𝐌𝐎𝐕𝐄 𝐀𝐃𝐌𝐈𝐍", callback_data="admin_rem"),
            ],
            [
                InlineKeyboardButton("ϲℓοѕє", callback_data="close"),
            ],
        ]
    )
    await message.reply_photo(
        photo="https://i.ibb.co/kVwykh4J/ce566244dba9.jpg",
        caption=txt,
        reply_markup=keyboard,
        message_effect_id=5104841245755180586,
    )


async def admin2(client, query):
    uid = query.from_user.id
    user_id = uid
    admin1 = await get_variable("owner", "5426061889")
    admin1 = [int(x.strip()) for x in admin1.split()]
    # Extract "on" or "off" from the callback data
    action = query.data.split("_")[1]

    if uid not in admin1:
        await query.answer(
            "❌ ϐακκα!, γου αяє иοτ αℓℓοωє∂ το υѕє τнє ϐυττοи", show_alert=True
        )
        return
    txt = (
        "<blockquote expandable>⚠️ <b>𝖣𝗈 𝖮𝗇𝖾 𝖡𝖾𝗅𝗈𝗐</b> ⚠️</blockquote>\n"
        "<blockquote expandable><i>🔱 𝖥𝗈𝗋𝗐𝖺𝗋𝖽 𝖠 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖥𝗋𝗈𝗆 𝖠𝖽𝗆𝗂𝗇</i></blockquote>\n"
        "<blockquote expandable><i>💠 𝖲𝖾𝗇𝖽 𝖬𝖾 𝖠𝖽𝗆𝗂𝗇 𝖨𝖣</i></blockquote>"
        "<blockquote>♨️ 𝗠𝗔𝗞𝗘 𝗦𝗨𝗥𝗘 𝗔𝗗𝗠𝗜𝗡 𝗜𝗗 𝗜𝗦 𝗩𝗔𝗟𝗜𝗗 ♨️</blockquote>"
    )

    if action == "add":
        while True:
            b = await client.send_message(
                uid,
                text=txt,
                reply_markup=ReplyKeyboardMarkup(
                    [["❌ Cancel"]], one_time_keyboard=True, resize_keyboard=True
                ),
            )
            try:
                a = await client.listen(user_id=uid, timeout=30, chat_id=uid)
            except ListenerTimeout:
                await client.send_message(
                    chat_id=uid,
                    text="⏳ Timeout! Fsub Setup cancelled.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                await b.delete()
                break
            if a.forward_from_chat:
                chat_id = a.forward_from_chat.id
            else:
                if a.text.lower() == "❌ cancel":
                    await client.send_message(
                        chat_id=uid,
                        text="❌ Fsub setup cancelled.",
                        reply_markup=ReplyKeyboardRemove(),
                    )
                    await b.delete()
                    break
                try:
                    chat_id = int(a.text.strip())
                except ValueError:
                    await client.send_message(
                        user_id, "Invalid input! Please send a valid channel/group ID."
                    )
                    await b.delete()
                    continue
            admin1 = await get_variable("admin", [])

            if chat_id in admin1:
                await client.send_message(
                    user_id, "User is already admin resend correct id...."
                )
                await b.delete()
                continue
            admin1.append(chat_id)

            # Convert back to string format

            await set_variable("admin", admin1)
            await b.delete()
            await admin(client, query.message)
            await query.message.delete()
            break

    elif action == "rem":
        while True:
            b = await client.send_message(
                uid,
                text=txt,
                reply_markup=ReplyKeyboardMarkup(
                    [["❌ Cancel"]], one_time_keyboard=True, resize_keyboard=True
                ),
            )
            try:
                a = await client.listen(user_id=uid, timeout=30, chat_id=uid)
            except ListenerTimeout:
                await client.send_message(
                    chat_id=uid,
                    text="⏳ Timeout! Fsub Setup cancelled.",
                    reply_markup=ReplyKeyboardRemove(),
                )
                await b.delete()
                break
            if a.forward_from_chat:
                chat_id = a.forward_from_chat.id
            else:
                if a.text.lower() == "❌ cancel":
                    await client.send_message(
                        chat_id=uid,
                        text="❌ Fsub setup cancelled.",
                        reply_markup=ReplyKeyboardRemove(),
                    )
                    await b.delete()
                    break
                try:
                    chat_id = int(a.text.strip())
                except ValueError:
                    await client.send_message(
                        user_id, "Invalid input! Please send a valid channel/group ID."
                    )
                    await b.delete()
                    continue
            admin1 = await get_variable("admin", [])

            if chat_id not in admin1:
                await client.send_message(
                    user_id, "User is not admin resend correct id...."
                )
                await b.delete()
                continue
            admin1.remove(chat_id)

            # Convert back to string format
            await set_variable("admin", admin1)
            await b.delete()
            await admin(client, query.message)
            await query.message.delete()
            break

    else:
        # Handle unexpected action (optional)
        await query.answer("Invalid action.", show_alert=True)

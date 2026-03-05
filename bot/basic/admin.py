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
    txt = f"<blockquote expandable><b>𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟 ♻️\n</blockquote>\n<blockquote expandable> 𝗔𝗗𝗠𝗜𝗡 :- {a}\n</blockquote>\n<blockquote expandable> 𝗡𝗢𝗧𝗘 - ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴀʟʟ ʙᴏᴛ ᴄᴏᴍᴍᴍᴀɴᴅꜱ ᴇxᴄᴇᴘᴛ ꜰꜱᴜʙ, ᴀᴅᴍɪɴ ‼️</b></blockquote>"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("𝗔𝗗𝗗 𝗔𝗗𝗠𝗜𝗡", callback_data="admin_add"),
                InlineKeyboardButton("𝗥𝗘𝗠𝗢𝗩𝗘 𝗔𝗗𝗠𝗜𝗡", callback_data="admin_rem"),
            ],
            [
                InlineKeyboardButton("Cʟᴏꜱᴇ", callback_data="close"),
            ],
        ]
    )
    await message.reply_photo(
        photo="https://graph.org/file/133955e7359e368757241-3b22219c9508b4429c.jpg",
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
        "<blockquote expandable>‼️ <b>Dᴏ ᴏɴᴇ ʙᴇʟᴏᴡ</b>‼️ </blockquote>\n"
        "<blockquote expandable><i>ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴀᴅᴍɪɴ</i></blockquote>\n"
        "<blockquote expandable><i>ꜱᴇɴᴅ ᴍᴇ ᴀᴅᴍɪɴ ɪᴅ</i></blockquote>"
        "<blockquote>ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴀᴅᴍɪɴ ɪᴅ ɪꜱ ᴠᴀʟɪᴅ </blockquote>"
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

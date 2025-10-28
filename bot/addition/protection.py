from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import get_variable, set_variable

async def file_protection_panel(client: Client, message: Message = None, callback_query: CallbackQuery = None):
    """
    Modern admin panel for managing file protection status
    Works with both messages and callback queries
    """
    
    # Determine the user and context
    if callback_query:
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.id
    else:
        user_id = message.from_user.id
        chat_id = message.chat.id
        message_id = None
    
    # Check admin privileges
    admin_list = await get_variable("admin", [])
    if user_id not in admin_list:
        error_text = (
            "🚨 𝗔𝗖𝗖𝗘𝗦𝗦 𝗥𝗘𝗦𝗧𝗥𝗜𝗖𝗧𝗘𝗗 🚨\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⛔ 𝙔𝙤𝙪 𝙙𝙤𝙣'𝙩 𝙝𝙖𝙫𝙚 𝙖𝙙𝙢𝙞𝙣 𝙥𝙧𝙞𝙫𝙞𝙡𝙚𝙜𝙚𝙨\n"
            "🔐 𝙊𝙣𝙡𝙮 𝙖𝙪𝙩𝙝𝙤𝙧𝙞𝙯𝙚𝙙 𝙪𝙨𝙚𝙧𝙨 𝙘𝙖𝙣 𝙖𝙘𝙘𝙚𝙨𝙨"
        )
        
        if callback_query:
            await callback_query.answer(error_text.replace('\n', ' '), show_alert=True)
        else:
            await message.reply_text(error_text, quote=True)
        return
    
    # Get current protection status
    protection_status = await get_variable("file_protection", False)
    
    # Modern status indicators
    if protection_status:
        status_indicator = "🟢"
        status_text = "𝗔𝗖𝗧𝗜𝗩𝗘"
        status_desc = "𝙁𝙞𝙡𝙚𝙨 𝙖𝙧𝙚 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙥𝙧𝙤𝙩𝙚𝙘𝙩𝙚𝙙"
        toggle_btn_text = "🔴 𝗧𝗨𝗥𝗡 𝗢𝗙𝗙"
        toggle_action = "protection_off"
    else:
        status_indicator = "🔴"
        status_text = "𝗜𝗡𝗔𝗖𝗧𝗜𝗩𝗘"
        status_desc = "𝙁𝙞𝙡𝙚𝙨 𝙖𝙧𝙚 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙪𝙣𝙥𝙧𝙤𝙩𝙚𝙘𝙩𝙚𝙙"
        toggle_btn_text = "🟢 𝗧𝗨𝗥𝗡 𝗢𝗡"
        toggle_action = "protection_on"
    
    # Create modern decorated message
    panel_text = (
        "🛡️ 𝗙𝗜𝗟𝗘 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡 𝗖𝗘𝗡𝗧𝗘𝗥 🛡️\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 𝗦𝗧𝗔𝗧𝗨𝗦: {status_indicator} {status_text}\n"
        f"📝 {status_desc}\n\n"
        "⚙️ 𝗤𝗨𝗜𝗖𝗞 𝗖𝗢𝗡𝗧𝗥𝗢𝗟𝗦\n"
        "┌─────────────────────────\n"
        "│ ⚡ 𝙄𝙣𝙨𝙩𝙖𝙣𝙩 𝙤𝙣/𝙤𝙛𝙛 𝙘𝙤𝙣𝙩𝙧𝙤𝙡\n"
        "│ 🔄 𝘼𝙪𝙩𝙤-𝙧𝙚𝙛𝙧𝙚𝙨𝙝 𝙨𝙩𝙖𝙩𝙪𝙨\n"
        "│ 🎛️ 𝙍𝙚𝙖𝙡-𝙩𝙞𝙢𝙚 𝙪𝙥𝙙𝙖𝙩𝙚𝙨\n"
        "└─────────────────────────\n\n"
        "🎯 𝗨𝘀𝗲 𝗯𝘂𝘁𝘁𝗼𝗻𝘀 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝗰𝗼𝗻𝘁𝗿𝗼𝗹 ⬇️"
    )
    
    # Create simple 2-button keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                toggle_btn_text, 
                callback_data=toggle_action
            ),
            InlineKeyboardButton(
                "❌ 𝗖𝗟𝗢𝗦𝗘", 
                callback_data="protection_close"
            )
        ]
    ])
    
    # Send or edit message based on context
    if callback_query:
        try:
            await callback_query.message.edit_text(
                panel_text,
                reply_markup=keyboard
            )
            await callback_query.answer("✅ 𝙋𝙖𝙣𝙚𝙡 𝙪𝙥𝙙𝙖𝙩𝙚𝙙!", show_alert=False)
        except Exception as e:
            await callback_query.answer(f"❌ Update failed: {str(e)}", show_alert=True)
    else:
        await message.reply_text(
            panel_text,
            reply_markup=keyboard,
            quote=True
        )

# Simplified callback handler
@Client.on_callback_query(filters.regex(r"^protection_"))
async def handle_protection_callbacks(client: Client, callback_query: CallbackQuery):
    """Handle protection panel interactions - simplified version"""
    
    # Check admin privileges first
    admin_list = await get_variable("admin", [])
    if callback_query.from_user.id not in admin_list:
        await callback_query.answer(
            "🚨 𝘼𝙘𝙘𝙚𝙨𝙨 𝙙𝙚𝙣𝙞𝙚𝙙! 𝘼𝙙𝙢𝙞𝙣 𝙤𝙣𝙡𝙮.", 
            show_alert=True
        )
        return
    
    action = callback_query.data.split("_")[1]
    
    if action == "on":
        await set_variable("file_protection", True)
        await callback_query.answer("🟢 𝙋𝙧𝙤𝙩𝙚𝙘𝙩𝙞𝙤𝙣 𝙖𝙘𝙩𝙞𝙫𝙖𝙩𝙚𝙙!", show_alert=True)
        await file_protection_panel(client, callback_query=callback_query)
        
    elif action == "off":
        await set_variable("file_protection", False)
        await callback_query.answer("🔴 𝙋𝙧𝙤𝙩𝙚𝙘𝙩𝙞𝙤𝙣 𝙙𝙞𝙨𝙖𝙗𝙡𝙚𝙙!", show_alert=True)
        await file_protection_panel(client, callback_query=callback_query)
        
    elif action == "close":
        close_text = (
            "✅ 𝗣𝗔𝗡𝗘𝗟 𝗖𝗟𝗢𝗦𝗘𝗗\n\n"
            "🛡️ 𝙁𝙞𝙡𝙚 𝙥𝙧𝙤𝙩𝙚𝙘𝙩𝙞𝙤𝙣 𝙧𝙚𝙢𝙖𝙞𝙣𝙨 𝙖𝙘𝙩𝙞𝙫𝙚\n"
            "⚡ 𝙐𝙨𝙚 /protection 𝙩𝙤 𝙧𝙚𝙤𝙥𝙚𝙣"
        )
        
        try:
            await callback_query.message.edit_text(close_text)
            await callback_query.answer("❌ 𝙋𝙖𝙣𝙚𝙡 𝙘𝙡𝙤𝙨𝙚𝙙", show_alert=False)
        except:
            await callback_query.message.delete()
            await callback_query.answer("❌ 𝙋𝙖𝙣𝙚𝙡 𝙘𝙡𝙤𝙨𝙚𝙙", show_alert=False)

# Command handler
@Client.on_message(filters.command("protection") & filters.private)
async def protection_command(client: Client, message: Message):
    await file_protection_panel(client, message=message)

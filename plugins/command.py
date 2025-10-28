from pyrogram import Client, filters

from bot.basic.admin import admin
from bot.basic.awailable import awailable_command, load_command, parse
from bot.basic.fsub import fsub1, onreq
from bot.basic.prem import add_premium, list_premium_users, remove_premium
from bot.basic.upload import collector, upload
from bot.basic.work import force_subs, not_subscribed
from bot.commands.start import start
from bot.commands.user import get_users, send_text
from bot.config import *
from bot.logger import LOGGER, send_logs
from bot.utils.anime import search
from bot.utils.restart import restart_bot
from database import get_variable
from bot.addition.short import short, short2, short3, short4
from bot.addition.protection import file_protection_panel

log = LOGGER(__name__)


@Client.on_message(filters.command("restart") & (filters.private | filters.group))
async def handle_restart(client, message):
    admin = await get_variable("admin")
    if message.from_user.id not in admin:
        return
    try:
        await message.reply_text("Restartingggg")
        await restart_bot(client, message)
    except Exception as e:
        log.error(e)
        await message.reply_text(f"error:-{e}")


@Client.on_message(filters.command("upload"))
async def handle_upload(client, message):
    await upload(client, message)


@Client.on_message(filters.command("ongoing"))
async def handle_onhoing(client, message):
    await upload(client, message, ongoing=1)


@Client.on_message(filters.command("log") & (filters.private | filters.group))
async def handle_logs(client, message):
    admin = await get_variable("admin")
    if message.from_user.id not in admin:
        return
    await send_logs(client, message)


@Client.on_message(filters.command("shell"))
async def handle_shell(client, message):
    admin = await get_variable("admin")
    if message.from_user.id not in admin:
        return
    await shell_command(client, message)


@Client.on_message(filters.command("available") & (filters.private | filters.group))
async def handle_awail(client, message):
    await awailable_command(client, message)


@Client.on_message(filters.command("parse") & filters.reply & filters.private)
async def handlepraisw(client, message):
    admin = await get_variable("admin")
    if message.from_user.id not in admin:
        return
    await parse(client, message)


@Client.on_message(filters.command("load") & filters.private & filters.reply)
async def handlesave(client, message):
    admin = await get_variable("admin")
    if message.from_user.id not in admin:
        return
    await load_command(client, message)


@Client.on_message(filters.private & filters.command("fsub"))
async def fsub(client, message):
    await fsub1(client, message)


@Client.on_message(filters.private & filters.command("admin"))
async def hadmin(client, message):
    await admin(client, message)


@Client.on_message(filters.group & filters.command("search"))
async def anime_command(client, message):
    await search(client, message, group=1)


@Client.on_message(filters.command("users"))
async def handle_user(c, m):
    await get_users(c, m)


@Client.on_message(filters.command("broadcast"))
async def handle_broadvasy(c, m):
    await send_text(c, m)

@Client.on_message(filters.private & filters.command("shortner"))
async def hshort(client, message):
    await short(client, message)



@Client.on_chat_join_request()
async def request(client, join):
    await onreq(client, join)


# ---------------processing here ---------------------


@Client.on_message(filters.private, group=-10)
async def handlefed(client, message):
    await collector(client, message)


@Client.on_message(filters.private & filters.create(not_subscribed))
async def handle_messages(client, message):
    await force_subs(client, message)


@Client.on_message(filters.command("start"))
async def handle_start(client, message):
    await start(client, message)


@Client.on_message(filters.private & filters.command("add_prem"))
async def prem1(client, message):
    uid = message.from_user.id
    admin = await get_variable("admin", [])
    if uid not in admin:
        return
    await add_premium(client, message)


@Client.on_message(filters.private & filters.command("rem_prem"))
async def prem2(client, message):
    uid = message.from_user.id
    admin = await get_variable("admin", [])
    if uid not in admin:
        return
    await remove_premium(client, message)


@Client.on_message(filters.private & filters.command("list_prem"))
async def prem3(client, message):
    uid = message.from_user.id
    admin = await get_variable("admin", [])
    if uid not in admin:
        return
    await list_premium_users(client, message)
    

@Client.on_message(filters.private & filters.command("protection"))
async def pro4(client, message):
    await file_protection_panel(client, message)

@Client.on_message(filters.private & filters.text)
async def handle_private_text(client, message):
    await search(client, message)

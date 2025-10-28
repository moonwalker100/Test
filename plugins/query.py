from pyrogram import Client
from bot.basic.admin import admin2
from bot.basic.awailable import awailable_command, paginate_anime_list
from bot.basic.epi import epo, file, upepi
from bot.basic.episode import episode_list_handler, episode_page_handler
from bot.basic.fsub import fsub2, fsub3, fsub4, fsub5
from bot.basic.info import info
from bot.basic.prem import free_ep, premcall
from bot.basic.request import request_handler
from bot.basic.upload import (
    fed,
    ongoing_choose_anime,
    ongoing_choose_episode,
    switch_page,
    upload,
    uploadinfo,
)
from bot.basic.work import check_subscription
from bot.commands.start import home, contact
from bot.logger import LOGGER
from bot.utils.anime import search
from bot.addition.short import short2, short3, short4
from bot.addition.protection import handle_protection_callbacks, protection_command

log = LOGGER(__name__)



@Client.on_callback_query()
async def global_callback_handler(client, callback_query):
    data = callback_query.data or ""
    log.info(data)

    # Always acknowledge quickly to clear spinner
    try:
        await callback_query.answer(cache_time=0)
    except Exception as e:
        log.debug(f"answer() failed: {e}")

    # Ignore no-op page indicator taps
    if data.startswith(("noop", "ignore")):
        return

    # Info (legacy/new)
    if data.startswith(("info", "inf")):
        await info(client, callback_query)
        return

    # Search button (legacy)
    if data.startswith("bto_"):
        parts = data.split("_", 1)
        if len(parts) == 2:
            await search(client, parts[1], query=callback_query)
        return

    # Upload flows
    if data.startswith("upload"):
        await uploadinfo(client, callback_query)
        return
    if data.startswith("upto_"):
        parts = data.split("_", 1)
        if len(parts) == 2:
            try:
                await upload(client, parts[1], query=callback_query)
            except Exception as e:
                log.error(e)
        return
    if data.startswith("update"):
        await upepi(client, callback_query)
        return
    if data.startswith("up"):
        await fed(client, callback_query)
        return

    # Episodes: SPECIFIC patterns FIRST (pagination)
    if data.startswith(("epi.page", "epi_page_")):
        await episode_page_handler(client, callback_query)
        return
        
    # Episode selected
    if data.startswith("showep"):
        await epo(client, callback_query)
        return
        
    # Episodes: GENERAL patterns AFTER specific ones (lists)
    if data.startswith(("epi.list", "epi_")) or data.startswith("epi"):
        await episode_list_handler(client, callback_query)
        return

    # File retrieval
    if data.startswith("get"):
        await file(client, callback_query)
        return

    # ... rest of your handlers remain the same


    # Available list pagination (legacy + new)
    if data.startswith(("awail", "awl_", "idecawail_", "iedcawl_")):
        await paginate_anime_list(client, callback_query)
        return

    # FSub toggles
    if data == "fsub_add":
        await fsub2(client, callback_query)
        return
    if data == "fsub_rem":
        await fsub3(client, callback_query)
        return
    if data == "rsub_add":
        await fsub4(client, callback_query)
        return
    if data == "rsub_rem":
        await fsub5(client, callback_query)
        return

    # Admin / subscription
    if data.startswith("admin_"):
        await admin2(client, callback_query)
        return
    if data.startswith("check_subscription"):
        extra = data.replace("check_subscription", "", 1)
        await check_subscription(client, callback_query, extra)
        return

    # Back navigations (legacy + new)
    if data in ("backtoavail", "bta"):
        await awailable_command(client, 1, callback_query)
        return
    if data in ("backtoindex", "bti"):
        await awailable_command(client, 1, edit=callback_query)
        return

    # Ongoing + pages
    if data.startswith("ongoing_ep"):
        await ongoing_choose_episode(client, callback_query)
        return
    if data.startswith("ongoing"):
        await ongoing_choose_anime(client, callback_query)
        return
    if data.startswith("page"):
        await switch_page(client, callback_query)
        return

    # Requests
    if data.startswith("request_"):
        await request_handler(client, callback_query)
        return

    # Index/Home
    if data == "index":
        await awailable_command(client, callback_query, edit=callback_query)
        return
    if data == "home":
        await home(client, callback_query)
        return

    # Premium / Shorteners
    if data.startswith("freepi"):
        await free_ep(client, callback_query)
        return
    if data.startswith("short_") and data != "short_rem":
        await short2(client, callback_query)
        return
    if data == "short_rem":
        await short3(client, callback_query)
        return
    if data.startswith("mode_"):
        await short4(client, callback_query)
        return
    if data == "prem":
        await premcall(client, callback_query)
        return

    # Misc controls
    if data == "cancel":
        await callback_query.message.delete()
        return
    if data == "contact":
        await contact(client, callback_query)
        return

    # Protection
    if data.startswith("protection_"):
        await handle_protection_callbacks(client, callback_query)
        return
    if data == "protection":
        await protection_command(client, callback_query)
        return

    # If unhandled, allow other handlers to try
    callback_query.continue_propagation()

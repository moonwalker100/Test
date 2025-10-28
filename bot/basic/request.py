import asyncio

from pyrogram.errors import FloodWait
from pyrogram.errors import MessageNotModified as MESSAGE_NOT_MODIFIED

from bot.basic.search import get_anime_name as get_name
from bot.config import SUPPORT_CHAT
from bot.decorator import task
from bot.logger import LOGGER
from database import get_variable, set_variable

log = LOGGER(__name__)


@task
async def request_handler(client, query):
    """Entry point for handling anime request button clicks.

    If the user's ID is not already in the list of requests for the anime, add it.
    If we have a support chat, send a message to the support chat with a list
    of all anime sorted by request count.

    """
    _, anime_id = query.data.split("_")
    # {anime_id: list of user_ids}
    requests = await get_variable("requests", {})

    if SUPPORT_CHAT:
        try:
            user_id = query.from_user.id
            if user_id not in requests.setdefault(anime_id, []):
                requests[anime_id].append(user_id)
                await query.answer(
                    "Request sent successfully. Total updated requests:",
                    show_alert=True,
                )

                request_message = await get_variable("request_message", 0)
                text = (
                    "<blockquote><b> Top 10 Requested Anime</b></blockquote>\n"
                    "<blockquote><i>Ranked by request count:</i></blockquote>\n\n"
                )
                sorted_requests = sorted(
                    requests.items(), key=lambda x: len(x[1]), reverse=True
                )[:10]
                for i, (anime_id, user_ids) in enumerate(sorted_requests, start=1):
                    text += f"\n<blockquote>{i}. {await get_name(anime_id)} - {len(user_ids)} requests</blockquote>"

                if request_message:
                    try:
                        await client.edit_message_text(
                            chat_id=SUPPORT_CHAT,
                            message_id=request_message,
                            text=text,
                        )
                    except MESSAGE_NOT_MODIFIED:
                        log.warning("Request message not modified, likely no changes.")
                    except Exception as e:
                        log.warning(f"Error editing request message: {e}")
                        send_message = await client.send_message(
                            chat_id=SUPPORT_CHAT, text=text
                        )
                        send_message.pin()
                        await set_variable("request_message", send_message.id)
                else:
                    sent_message = await client.send_message(
                        chat_id=SUPPORT_CHAT, text=text
                    )
                    await sent_message.pin()
                    await set_variable("request_message", sent_message.id)
            else:
                await query.answer(
                    "You have already requested this anime.", show_alert=True
                )
            await set_variable("requests", requests)
        except FloodWait as e:
            log.warning(f"Flood wait error: {e}")
            await asyncio.sleep(e.x)
        except Exception as e:
            log.error("Error sending request to support chat: %s", e, exc_info=True)


@task
async def onupload(client, aniid):
    """Task to handle actions after an anime upload."""
    requests = await get_variable("requests", {})
    if aniid not in requests:
        log.warning(f"No requests found for anime ID {aniid}.")
        return
    anime_id = aniid
    if aniid in requests:
        user_ids = requests[aniid]
        if user_ids:
            for user_id in user_ids:
                try:
                    await client.send_message(
                        chat_id=user_id,
                        text=f"Your request for {await get_name(aniid)} has been fulfilled! Enjoy!",
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await client.send_message(
                        chat_id=user_id,
                        text=f"Your request for {await get_name(aniid)} has been fulfilled! Enjoy!",
                    )
                except Exception as e:
                    log.error(
                        f"Error notifying user {user_id} about fulfilled request: {e}"
                    )

        request_message = await get_variable("request_message", 0)
        text = (
            "<blockquote><b> Top 10 Requested Anime</b></blockquote>\n"
            "<blockquote><i>Ranked by request count:</i></blockquote>\n\n"
        )
        sorted_requests = sorted(
            requests.items(), key=lambda x: len(x[1]), reverse=True
        )[:10]
        for i, (anime_id, user_ids) in enumerate(sorted_requests, start=1):
            text += f"\n<blockquote>{i}. {await get_name(anime_id)} - {len(user_ids)} requests</blockquote>"

        if request_message:
            try:
                await client.edit_message_text(
                    chat_id=SUPPORT_CHAT,
                    message_id=request_message,
                    text=text,
                )
            except MESSAGE_NOT_MODIFIED:
                log.warning("Request message not modified, likely no changes.")
            except Exception as e:
                log.warning(f"Error editing request message: {e}")
                send_message = await client.send_message(
                    chat_id=SUPPORT_CHAT, text=text
                )
                send_message.pin()
                await set_variable("request_message", send_message.id)
        else:
            sent_message = await client.send_message(chat_id=SUPPORT_CHAT, text=text)
            await sent_message.pin()
            await set_variable("request_message", sent_message.id)
        del requests[aniid]
        await set_variable("requests", requests)

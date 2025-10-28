import asyncio
import base64
import random
import re
import string
from datetime import datetime

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.errors.pyromod.listener_timeout import ListenerTimeout
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.addition.short import get_shortlink, isprem
from bot.config import DB_CHANNEL, images, text_go, AUTO_DELETE_TIME
from bot.decorator import task
from bot.logger import LOGGER
from database import get_variable, set_variable

from .episode import PER_PAGE, cache_text, pack_cb, parse_cb, get_cached_text
from .search import get_anime_name
from .upload import add_or_update_quality

log = LOGGER(__name__)


def encode(input_string: str) -> str:
    """Encodes a string into Base64."""
    bytes_data = input_string.encode("utf-8")
    base64_bytes = base64.b64encode(bytes_data)
    return base64_bytes.decode("utf-8")


def decode(base64_string: str) -> str:
    """Decodes a Base64 string back to regular string."""
    base64_bytes = base64_string.encode("utf-8")
    decoded_bytes = base64.b64decode(base64_bytes)
    return decoded_bytes.decode("utf-8")


def generate_hash(length=18):
    characters = string.hexdigits.lower()
    return "".join(random.choices(characters, k=length))


def parse_showep_data(data: str):
    """Parse both new (showep:<anime_id>:<ep>:<tok>) and legacy (showep_<ep>_<anime_id>_<text>) formats."""
    if data.startswith("showep:"):
        parts = data.split(":", 3)
        if len(parts) == 4:
            return parts[2], parts[1], parts[3]  # episode, anime_id, token
    elif data.startswith("showep_"):
        parts = data.split("_", 3)
        if len(parts) == 4:
            return parts[1], parts[2], parts[3]  # episode, anime_id, text
    return None, None, None


def parse_get_data(data: str):
    """Parse both new (get:<fileid>:<anime_id>:<episode>) and legacy (get_<fileid>_<anime_id>_<episode>) formats."""
    if data.startswith("get:"):
        parts = data.split(":", 3)
        if len(parts) == 4:
            return parts[1], parts[2], parts[3]  # fileid, anime_id, episode
    elif data.startswith("get_"):
        parts = data.split("_", 3)
        if len(parts) == 4:
            return parts[1], parts[2], parts[3]  # fileid, anime_id, episode
    return None, None, None


def parse_update_data(data: str):
    """Parse both new and legacy update callback formats."""
    if data.startswith("update:"):
        parts = data.split(":", 3)
        if len(parts) == 4:
            return parts[1], parts[2], parts[3]  # animeid, episode, token
    elif data.startswith("update_"):
        parts = data.split("_", 3)
        if len(parts) == 4:
            return parts[1], parts[2], parts[3]  # animeid, episode, text
    return None, None, None


@task
async def epo(c, q):
    # Always acknowledge callback quickly
    try:
        await q.answer(cache_time=0)
    except Exception as e:
        log.debug(f"answer() failed: {e}")

    try:
        episode, anime_id, text_tok = parse_showep_data(q.data)
        if not all([episode, anime_id]):
            await q.answer("Invalid episode data.", show_alert=True)
            return

        anime = await get_variable("anime")
        anime_id = str(anime_id)
        episode = str(episode)

        name = await get_anime_name(int(anime_id))

        # Get episode data
        episode_data = anime.get(anime_id, {}).get(episode)
        if not episode_data:
            await q.answer("No data found for this episode.", show_alert=True)
            return

        buttons = []
        # Define the preferred order of qualities
        preferred_quality_order = ["480p", "720p", "1080p", "hdrip"]
        sorted_episode_data = dict(
            sorted(
                episode_data.items(),
                key=lambda x: (
                    preferred_quality_order.index(x[0].lower())
                    if x[0].lower() in preferred_quality_order
                    else len(preferred_quality_order)
                ),
            )
        )
        
        if len(sorted_episode_data.items()) <= 0:
            await q.answer("This episode is not available")
            return

        for quality, msg_id in sorted_episode_data.items():
            # Get file details from DB_CHANNEL
            try:
                msg = await c.get_messages(int(DB_CHANNEL), int(msg_id))
                file_name = (
                    msg.document.file_name
                    if msg.document
                    else msg.video.file_name if msg.video else "Unknown"
                )
                file_size = round(
                    (msg.document.file_size if msg.document else msg.video.file_size)
                    / (1024 * 1024),
                    2,
                )
            except Exception:
                file_name = "Unknown"
                file_size = 0
            
            if quality == "hdrip":
                quality = "HDrip"
            file_lower = file_name.lower()
            audio_type = ""

            if "dual" in file_lower:
                audio_type = "Dual"
            elif "multi" in file_lower:
                audio_type = "Multi"
            elif "sub" in file_lower:
                audio_type = "Subbed"
            else:
                match = re.search(r"[\{]([^\d\}]+)[\}]", file_name)
                if match:
                    audio_type = match.group(1)
            
            button_text = f"({file_size}MB)   {quality}     [{audio_type}]".strip()
            
            if q.message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                me = await c.get_users("me")
                buttons.append(
                    [
                        InlineKeyboardButton(
                            button_text,
                            url=f"t.me/{me.username}?start=get_{msg_id}_{anime_id}_{episode}",
                        )
                    ]
                )
            else:
                # Use compact format for callback_data
                buttons.append(
                    [
                        InlineKeyboardButton(
                            button_text,
                            callback_data=pack_cb("get", msg_id, anime_id, episode),
                        )
                    ]
                )

        # Add navigation buttons
        nav_buttons = []
        if int(episode) > 1:
            if text_tok and not text_tok.isdigit():  # New format with token
                tok = text_tok
            else:  # Legacy or create new token
                text = get_cached_text(text_tok) if text_tok else ""
                tok = cache_text(text or "")
            
            nav_buttons.append(
                InlineKeyboardButton(
                    "⬅️ Previous",
                    callback_data=pack_cb("showep", anime_id, str(int(episode) - 1), tok),
                )
            )
        
        if text_tok and not text_tok.isdigit():  # New format with token
            tok = text_tok
        else:  # Legacy or create new token
            text = get_cached_text(text_tok) if text_tok else ""
            tok = cache_text(text or "")
            
        nav_buttons.append(
            InlineKeyboardButton(
                "➡️ Next",
                callback_data=pack_cb("showep", anime_id, str(int(episode) + 1), tok),
            )
        )
        buttons.append(nav_buttons)
        
        episode_int = int(episode)
        
        # Add admin button
        admin = await get_variable("admin")
        if q.from_user.id in admin:
            buttons.append(
                [
                    InlineKeyboardButton(
                        "Wrong files ❗",
                        callback_data=pack_cb("update", anime_id, episode, tok),
                    )
                ]
            )
        
        # Calculate page for back button
        page = max(1, (episode_int - 1) // PER_PAGE + 1)
        buttons.append(
            [
                InlineKeyboardButton(
                    "🔙 Back",
                    callback_data=pack_cb("epi.page", anime_id, str(page), tok),
                )
            ]
        )

        message_text = f"🎬 <b>{name} - Episode {episode_int}</b>\n\nSelect a quality to download:"
        
        try:
            await q.message.edit_text(message_text, reply_markup=InlineKeyboardMarkup(buttons))
        except MessageNotModified:
            pass
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await q.message.edit_text(message_text, reply_markup=InlineKeyboardMarkup(buttons))
            except MessageNotModified:
                pass

    except Exception as e:
        try:
            await q.answer(f"⚠️ Error: {str(e)[:100]}", show_alert=True)
        except Exception:
            pass
        log.error(f"Error in epo: {e}", exc_info=True)


@task
async def file(client, q=0, filei=0, uuid=0, anime_id=0, episode=0, verify=0, message=0):
    if q:
        # Always acknowledge callback quickly
        try:
            await q.answer("AnimeToon INDEX", cache_time=0)
        except Exception as e:
            log.debug(f"answer() failed: {e}")
            
        fileid, anime_id, episode = parse_get_data(q.data)
        if not all([fileid, anime_id, episode]):
            try:
                await q.answer("Invalid file data.", show_alert=True)
            except Exception:
                pass
            return
            
        fileid = int(fileid)
        anime_id = int(anime_id)
        episode = int(episode)
        uid = q.from_user.id
    else:
        fileid = int(filei)
        anime_id = int(anime_id)
        episode = int(episode)
        uid = uuid
    
    FILE_AUTO_DELETE = AUTO_DELETE_TIME
    file_id = fileid
    user_id = uid
    aba = await get_variable("short", "")
    mode = await get_variable("mode", "I")
    now = datetime.now()
    freep = await get_variable(f"freepi{anime_id}")
    
    if int(episode) > int(freep):
        if aba:
            if not await isprem(uid):
                if mode == "24":
                    time = await get_variable(f"t{user_id}", datetime.min)
                    if not time:
                        time = datetime.min
                    prm = await isprem(user_id)
                    if time < now and not prm:
                        # Get the time (string)
                        b = await get_variable("token_time")
                        total_seconds = int(b)  # Convert to integer

                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60

                        time_parts = []
                        if hours:
                            time_parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
                        if minutes:
                            time_parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
                        if seconds and not hours:  # Only show seconds if there are no hours
                            time_parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")

                        b = " ".join(time_parts) if time_parts else "0 seconds"
                        tim = f"<blockquote expandable>⚠️ 𝙎𝙚𝙨𝙨𝙞𝙤𝙣 𝙀𝙭𝙥𝙞𝙧𝙚𝙙 ⚠️</blockquote>\n<blockquote expandable>⏳ 𝘼𝙘𝙘𝙚𝙨𝙨 𝙏𝙞𝙢𝙚: {b}</blockquote>\n<blockquote expandable>🌟𝙒𝙝𝙖𝙩'𝙨 𝙩𝙝𝙞𝙨 𝙩𝙤𝙠𝙚𝙣?\n🔑 𝙄𝙩'𝙨 𝙖𝙣 𝙖𝙘𝙘𝙚𝙨𝙨 𝙥𝙖𝙨𝙨! 𝙒𝙖𝙩𝙘𝙝 𝙟𝙪𝙨𝙩 1 𝙖𝙙 𝙩𝙤 𝙪𝙣𝙡𝙤𝙘𝙠 𝙩𝙝𝙚 𝙗𝙤𝙩 𝙛𝙤𝙧 𝙩𝙝𝙚 𝙣𝙚𝙭𝙩 {b}</blockquote>"
                        token = generate_hash()
                        token = f"time_{token}"
                        await set_variable(f"token{user_id}", token)
                        me = await client.get_users("me")
                        link = f"https://t.me/{me.username}?start={token}"

                        try:
                            link = await get_shortlink(link)
                        except Exception as e:
                            if q:
                                await q.message.reply_text(f"Error in shortlink {e}")
                            
                        keyboard = InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton("🚀 𝐆𝐄𝐓 𝐋𝐈𝐍𝐊 🚀", url=link)],
                                [InlineKeyboardButton("𝙿𝚁𝙴𝙼𝙸𝚄𝙼 ", callback_data="prem")],
                            ]
                        )
                        if message:
                            await message.reply_photo(
                                photo=random.choice(images), caption=tim, reply_markup=keyboard
                            )
                            return
                        if q:
                            await q.message.reply_photo(
                                photo=random.choice(images), caption=tim, reply_markup=keyboard
                            )
                            return
                            
                if mode == "link":
                    if verify:
                        pass
                    else:
                        string = f"get_{file_id}_{anime_id}_{episode}"
                        string = encode(string)
                        me = await client.get_users("me")
                        link = f"https://t.me/{me.username}?start=verify_{string}"
                        
                        try:
                            link = await get_shortlink(link)
                        except Exception as e:
                            if q:
                                await q.message.reply_text(f"Error in shortlink {e}")
                            
                        keyboard = InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton("🚀 𝐆𝐄𝐓 𝐋𝐈𝐍𝐊 🚀", url=link)],
                                [InlineKeyboardButton("𝙿𝚁𝙴𝙼𝙸𝚄𝙼 ", callback_data="prem")],
                            ]
                        )
                        text = text_go(
                            "<blockquote expandable>Token Required ⚠️</blockquote>\n"
                            "<blockquote expandable>Please Verify Yourself by solving the short link below</blockquote>\n"
                            "<blockquote expandable>❌ Bypass is strictly prohibited</blockquote>"
                        )
                        log.info(f"generated text is {text}")
                        if message:
                            await message.reply_photo(
                                photo=random.choice(images),
                                caption=text,
                                reply_markup=keyboard
                            )
                            return
                        if q:
                            await q.message.reply_photo(
                                photo=random.choice(images),
                                caption=text,
                                reply_markup=keyboard
                            )
                            return

    try:
        sent_msg = await client.copy_message(
            chat_id=uid, 
            from_chat_id=DB_CHANNEL, 
            message_id=fileid, 
            protect_content=await get_variable("file_protection", False)
        )
        await asyncio.sleep(0.5)

    except FloodWait as e:
        await asyncio.sleep(e.value)
        try:
            sent_msg = await client.copy_message(
                chat_id=uid, 
                from_chat_id=DB_CHANNEL, 
                message_id=fileid, 
                protect_content=await get_variable("file_protection", False)
            )
        except Exception as e:
            log.error(f"Error copying message after FloodWait: {e}")
            return

    except Exception as e:
        log.error(f"Error copying message: {e}")
        return

    if FILE_AUTO_DELETE > 0:
        try:
            notification_msg = await sent_msg.reply_text(
                f"<blockquote>This file will be deleted in {FILE_AUTO_DELETE / 60} Minutes. Because of Copyright issue.</blockquote>"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            filename = (
                sent_msg.document.file_name
                if sent_msg.document
                else sent_msg.video.file_name if sent_msg.video else "Unknown"
            )
            
            if sent_msg:
                try:
                    await sent_msg.delete()
                except Exception as e:
                    log.info(f"Error deleting message {sent_msg.id}: {e}")

            try:
                me = await client.get_users("me")
                await notification_msg.edit_text(
                    f"<blockquote><b>><i>Your file has been deleted.\n\n>Filename : {filename}</i></b></blockquote>",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "ɢᴇᴛ ꜰɪʟᴇ ᴀɢᴀɪɴ",
                                    url=f"t.me/{me.username}?start=get_{fileid}_{anime_id}_{episode}",
                                )
                            ]
                        ]
                    ),
                )

            except Exception as e:
                log.error(f"Error editing notification: {e}")

        except Exception as e:
            log.error(f"Error in auto-delete logic: {e}")


@task
async def upepi(c, q):
    # Always acknowledge callback quickly
    try:
        await q.answer(cache_time=0)
    except Exception as e:
        log.debug(f"answer() failed: {e}")

    try:
        animeid, episode, text_tok = parse_update_data(q.data)
        if not all([animeid, episode]):
            await q.answer("Invalid update data.", show_alert=True)
            return
            
        anime = await get_variable("anime")
        anime_id = str(animeid)
        episode = str(episode)
        uid = q.from_user.id
        admin = await get_variable("admin")
        
        if uid not in admin:
            await q.answer("Unauthorized access.", show_alert=True)
            return

        name = await get_anime_name(int(anime_id))

        # Get episode data
        episode_data = anime.get(anime_id, {}).get(episode)
        if not episode_data:
            await q.answer("No data found for this episode.", show_alert=True)
            return

        buttons = []
        for quality, msg_id in episode_data.items():
            # Get file details from DB_CHANNEL
            try:
                msg = await c.get_messages(int(DB_CHANNEL), int(msg_id))
                file_name = (
                    msg.document.file_name
                    if msg.document
                    else msg.video.file_name if msg.video else "Unknown"
                )
                file_size = round(
                    (msg.document.file_size if msg.document else msg.video.file_size)
                    / (1024 * 1024),
                    2,
                )
            except Exception:
                file_name = "Unknown"
                file_size = 0

            dual_text = "Dual" if "dual" in file_name.lower() else ""
            button_text = f"({file_size}MB)   {quality}     [{dual_text}]".strip()
            buttons.append(
                [
                    InlineKeyboardButton(
                        button_text, callback_data=f"bsdk_{msg_id}_{quality}"
                    )
                ]
            )

        a = await q.message.reply_text(
            "Please select the quality to replace the file from below",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        
        try:
            call = await c.wait_for_callback_query(
                q.message.chat.id, timeout=60, filters=filters.user(uid)
            )
        except asyncio.TimeoutError:
            await c.send_message(
                chat_id=uid,
                text="<blockquote><b>Timeout reselct the wrong episode from starting</b></blockquote>"
            )
            return
            
        fileid, quality = call.data.split("_")[1:]
        await a.edit(
            f"<blockquote expandable><b>Please send the Correct File for </b>\n\n<b>Anime : {name} </b><i>(ID:{anime_id})</i>\n<b>Episode : {episode}\nQuality : {quality}</b>\n\n<b><i>Please send the Correct file under 60 seconds</i></b></blockquote>"
        )

        try:
            aa = await c.listen(user_id=uid, timeout=60, chat_id=uid)
        except ListenerTimeout:
            await a.delete()
            await c.send_message(
                chat_id=uid,
                text="⏳ Timeout setup cancelled.",
            )
            return
        except Exception as e:
            log.error(e, exc_info=True)
            return

        if not (aa.document or aa.video):
            await c.send_message(
                chat_id=uid,
                text="<blockquote>Invalid input only files are allowed retry!</blockquote>",
            )
            await aa.delete()
            await a.delete()
            return
            
        try:
            copied = await c.copy_message(
                chat_id=DB_CHANNEL, from_chat_id=aa.chat.id, message_id=aa.id
            )
        except FloodWait as e:
            log.warning(f"FloodWait encountered. Sleeping for {e.value} seconds.")
            await asyncio.sleep(e.value)
            try:
                copied = await c.copy_message(
                    chat_id=DB_CHANNEL, from_chat_id=aa.chat.id, message_id=aa.id
                )
            except Exception as e:
                log.error(f"Error copying after FloodWait: {e}")
                return

        if not anime:
            anime = {}
        add_or_update_quality(anime, anime_id, episode, quality, copied.id)
        await set_variable("anime", anime)
        await c.send_message(chat_id=uid, text="File Saved successfully")
        await aa.delete()
        await a.delete()

    except Exception as e:
        try:
            await q.answer(f"⚠️ Error: {str(e)[:100]}", show_alert=True)
        except Exception:
            pass
        log.error(f"Error in upepi: {e}", exc_info=True)

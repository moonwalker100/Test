import os
import sys

from bot.decorator import task
from bot.logger import LOGGER
from database import get_variable

log = LOGGER(__name__)


@task
async def restart_bot(client, message):
    admin = await get_variable("admin")
    if message.from_user.id not in admin:
        return
    await message.reply_text("Updating and restarting bot...")

    try:
        exit_code = os.system("python3 update.py")

        if exit_code == 0:
            await message.reply_text("✅ Update successful! Restarting bot...")
        else:
            await message.reply_text("⚠️ Update failed! Restarting bot anyway...")

        # Restart the bot process
        os.execv(sys.executable, ["python3", "-m", "bot"])
    except Exception as e:
        await log("ERROR", f"{str(e)}")

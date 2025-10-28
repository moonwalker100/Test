import asyncio
import json
import logging
import os
from logging.handlers import RotatingFileHandler

from database import get_variable

from .config import LOG_CHANNEL

LOG_FILE_NAME = "bot.txt"
MAX_LOG_SIZE = 50 * 1024 * 1024  # 50 MB
BACKUP_COUNT = 10

# Formatter used across all handlers
LOG_FORMAT = (
    "%(asctime)s - %(name)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

# Configure root logger with rotating file + console
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT
        ),
        logging.StreamHandler(),
    ],
)

# Apply formatter to all existing handlers
for handler in logging.getLogger().handlers:
    handler.setFormatter(formatter)

# Silence noisy logs (Pyrogram, urllib3, etc.)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def LOGGER(name: str = "App"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Ensure each logger gets our formatter
    for handler in logger.handlers:
        handler.setFormatter(formatter)

    return logger


# Optional: send log file to user
async def send_logs(client, message):
    admin = await get_variable("admin")
    if message.from_user.id not in admin:
        return
    log_file = LOG_FILE_NAME
    if os.path.exists(log_file):
        await message.reply_document(log_file, caption="📄 Here are the latest logs.")
    else:
        await message.reply_text("⚠️ No logs found.")


async def datalog(client):
    while True:
        episode_data = await get_variable("anime")
        with open("episode_data.json", "w") as f:
            json.dump(episode_data, f, indent=2)
        await client.send_document(
            int(LOG_CHANNEL), "episode_data.json", caption="#Db_backup"
        )
        os.remove("episode_data.json")
        await asyncio.sleep(60 * 60 * 2)

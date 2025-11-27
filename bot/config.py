import os
import re

from dotenv import load_dotenv

load_dotenv()


# Bot token @Botfather
TG_BOT_TOKEN = os.environ.get(
    "TG_BOT_TOKEN", "8518910641:AAG70JtguCseqV0K1kQzAZUaWqW0T6JgkI0"
)
# Your API ID from my.telegram.orgh
APP_ID = int(os.environ.get("APP_ID", "27693340"))
# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "1056193e68c138ee16edc02578c559e1")
# Your db channel Id
LOG_CHANNEL = int(os.environ.get("CHANNEL_ID", "-1002849677750"))
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1002413997036"))
SUPPORT_CHAT = int(os.environ.get("SUPPORT_CHAT", "-1002399693434"))
# NAMA OWNER
# OWNER ID
ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "7425487437").split()))
# OWNER_IDS is a list of owner IDs, separated by spaces

# Retrieve the OWNER_IDS from the environment variable and create a list
OWNER_IDS = list(map(int, os.environ.get("OWNER_IDS", "1718481517").split()))

# image link that will be used with seahrch and awailable commands
poster = os.environ.get("POSTER", "https://i.postimg.cc/RVD4RpG1/1329839.jpg")
# Bot username
# Port
PORT = os.environ.get("PORT", "8030")
# Database
DB_URI = os.environ.get(
    "DATABASE_URL",
    "mongodb+srv://moonwalker1092:moonwalker1234@cluster0.svrznzr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
)
START_MESSAGE = "ʜᴇʟʟᴏ, {} \n\n<blockquote> ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b> ɪɴᴅᴇx ʙᴏᴛ</b>   ᴘᴏᴡᴇʀᴇᴅ ʙʏ Ꮢᴇᴍᴏ 🜲 </blockquote>\n<blockquote>🎭 ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ғɪɴᴅ ᴀʟʟ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ  🌐 ᴛᴀᴍɪʟ ᴅᴜʙ ᴀɴɪᴍᴇ ꜱᴇʀɪᴇꜱ – ᴀʟʟ ɪɴ ᴏɴᴇ ᴘʟᴀᴄᴇ!</blockquote>\n──────────────────\n⚡ ᴇɴᴊᴏʏ ᴛʜᴇ ᴡᴏʀʟᴅ ᴏғ ᴀɴɪᴍᴇ ʟɪᴋᴇ ɴᴇᴠᴇʀ ʙᴇғᴏʀᴇ ⚡"
DB_NAME = os.environ.get("DATABASE_NAME", "argon")

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "500"))

AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", 7200))

SUPPORT_TEXT = """<b> 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 & 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 </b>

<blockquote>Hey there, <b>Senpai 👋</b>
Need help with the bot or facing any issue?
Don’t worry, I’ve got you covered! </blockquote>

━━━━━━━━━━━━━━━

<blockquote><b>⚔️ How to Use?</b>

• Report any bug to the developer.

<b>📞 Contact Support</b>
• ᴏᴡɴᴇʀ: <a href="https://t.me/Here_remo"> Ꮢᴇᴍᴏ 🜲</a>
• ᴄʜᴀɴɴᴇʟ: <a href="https://t.me/play_tamil_dubbed_series"> 𝗨𝗽𝗱𝗮𝘁𝗲𝘀</a>
• ɢʀᴏᴜᴩ: <a href="https://t.me/play_community_group"> 𝗗𝗶𝘀𝗰𝘂𝘀𝘀𝗶𝗼𝗻</a></blockquote>

━━━━━━━━━━━━━━━

<b>💡 Tip:</b> Always make sure you’re using the <i>latest bot version</i> for best performance! 🚀"""

images = [
    "https://i.postimg.cc/RVD4RpG1/1329839.jpg",
    "https://i.postimg.cc/G3MCLS00/1329845.jpg",
    "https://i.postimg.cc/NFPqdL8G/1329915.jpg",
    "https://i.postimg.cc/yYBvG7ps/1332278.jpg",
    "https://i.postimg.cc/NfHBd7nW/1343620.png",
    "https://i.postimg.cc/TYqH2K5K/1343746.png",
    "https://i.postimg.cc/h4m5wySb/1343747.png",
    "https://i.postimg.cc/fThrhcy4/1362335.jpg",
    "https://i.postimg.cc/j52rPzN3/1363139.png",
    "https://i.postimg.cc/wM5FBrvC/545909.jpg",
    "https://i.postimg.cc/BQgM9RRD/599379.jpg",
    "https://i.postimg.cc/Kj1svfLF/740666.png",
    "https://i.postimg.cc/7YmMQ0Tn/749966.png",
    "https://i.postimg.cc/t70DRjpt/928887.jpg",
    "https://i.postimg.cc/qRD45m4d/goku-ultra-instinct-5120x2880-21414.png",
    "https://i.postimg.cc/yYgYwzDp/luffy-straw-hat-3840x2160-20824.png",
]


# --------------------text elements---------------------


def text_go(text: str) -> str:
    if not text:
        return text

    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    fancy = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘQʀꜱᴛᴜᴠᴡxʏᴢ" \
            "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘQʀꜱᴛᴜᴠᴡxʏᴢ" \
            "0123456789"

    mapping = str.maketrans(normal, fancy)

    def convert_word(word: str) -> str:
        if not word or word.startswith("@"):
            return word
        return word.translate(mapping)

    parts = re.split(r"(<[^>]+>)", text)
    result = []

    for part in parts:
        if not part:
            continue
        if part.startswith("<") and part.endswith(">"):
            result.append(part)
        else:
            # Split text but keep whitespace (including newlines, tabs, spaces)
            tokens = re.split(r'(\s+)', part)
            converted = [convert_word(token) if not token.isspace() else token for token in tokens]
            result.append("".join(converted))

    return "".join(result)

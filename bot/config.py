import os
import re

from dotenv import load_dotenv

load_dotenv()

# Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

# Your API ID from my.telegram.orgh
APP_ID = int(os.environ.get("APP_ID", "27340"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "10568c19e1")

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
poster = os.environ.get("POSTER", "https://graph.org/file/b2f3dafcceffd24c4c7aa-e88337d53cfe8bb5f8.jpg")

# Bot username

# Port
PORT = os.environ.get("PORT", "8030")

# Database
DB_URI = os.environ.get("DATABASE_URL","mongodb+srv://moonwalker1092:moonwalker1234@cluster0.svrznzr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",)

START_MESSAGE = """<b>⚡ Hᴇʏ {}\n\n<blockquote>I ᴀᴍ ᴛʜᴇ ᴍᴏꜱᴛ ᴘᴏᴡᴇʀꜰᴜʟ ɪɴᴅᴇx ʙᴏᴛ ᴡɪᴛʜ ᴘʀᴇᴍɪᴜᴍ ꜰᴇᴀᴛᴜʀᴇꜱ,Tʜɪꜱ ɪꜱ ᴀ ᴄᴇɴᴛʀᴇ ᴛᴏ ᴡᴀᴛᴄʜ ʏᴏᴜʀ ꜰᴀᴠᴏᴜʀɪᴛᴇ ᴀɴɪᴍᴇ ʟᴇᴛ'ꜱ ʀᴏʟʟ!</blockquote></b> <b>\n‣ Mᴀɪɴᴛᴀɪɴᴇᴅ Bʏ :<a href="https://t.me/Here_remo">Ꮢᴇᴍᴏ</a></b>"""

DB_NAME = os.environ.get("DATABASE_NAME", "remodb")

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "500"))

AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", 7200))

SUPPORT_TEXT = """<b>𝗦𝗨𝗣𝗣𝗢𝗥𝗧 & 𝗖𝗢𝗡𝗧𝗔𝗖𝗧</b>

<blockquote><b>ʜᴇʏ ᴛʜᴇʀᴇ, ꜱᴇɴᴘᴀɪ
ɴᴇᴇᴅ ʜᴇʟᴘ ᴡɪᴛʜ ᴛʜᴇ ʙᴏᴛ ᴏʀ ꜰᴀᴄɪɴɢ ᴀɴʏ ɪꜱꜱᴜᴇ? ᴅᴏɴ’ᴛ ᴡᴏʀʀʏ, ɪ’ᴠᴇ ɢᴏᴛ ʏᴏᴜ ᴄᴏᴠᴇʀᴇᴅ! </b></blockquote>

━━━━━━━━━━━━━━━

<blockquote expandable><b> ʜᴏᴡ ᴛᴏ ᴜꜱᴇ?

• ʀᴇᴘᴏʀᴛ ᴀɴʏ ʙᴜɢ ᴛᴏ ᴛʜᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ </b>

<b>📞 ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ
• ᴏᴡɴᴇʀ: <a href="https://t.me/Here_remo"> Ꮢᴇᴍᴏ 🜲</a>
• ᴄʜᴀɴɴᴇʟ: <a href="https://t.me/play_tamil_dubbed_series"> 𝗨𝗽𝗱𝗮𝘁𝗲𝘀</a>
• ɢʀᴏᴜᴩ: <a href="https://t.me/play_community_group"> 𝗗𝗶𝘀𝗰𝘂𝘀𝘀𝗶𝗼𝗻</a></b></blockquote>

━━━━━━━━━━━━━━━

<b>💡 TIP: ᴀʟᴡᴀʏꜱ ᴍᴀᴋᴇ ꜱᴜʀᴇ ʏᴏᴜ’ʀᴇ ᴜꜱɪɴɢ ᴛʜᴇ <i>ʟᴀᴛᴇꜱᴛ ʙᴏᴛ ᴠᴇʀꜱɪᴏɴ</i> ꜰᴏʀ ʙᴇꜱᴛ ᴘᴇʀꜰᴏʀᴍᴀɴᴄᴇ!</b>"""

images = [
    "https://graph.org/file/c22ccad28832aed94dbf1-49c96f1f7912938b86.jpg", 
    "https://graph.org/file/19e15ec483ec1b7656b09-fef4ad2d01c0bc4552.jpg", 
    "https://graph.org/file/babf5708d7b0ea534a17c-0eb69cf7275020b3fe.jpg",
    "https://graph.org/file/c31acfb82bcb6b84cf0db-be7324cab11728ef6d.jpg", 
    "https://graph.org/file/751ee02f7a14fe4ce2654-bdd2466f2072f43072.jpg", 
    "https://graph.org/file/8f6cc424fd39cc1795a9a-b391b8231829437915.jpg", 
    "https://graph.org/file/6b3b30c050fcf3da727b4-60401beca28ed88771.jpg", 
    "https://graph.org/file/e359b78b725dc87ef9743-24d5f30754037d7926.jpg", 
    "https://graph.org/file/514e7cfb6c3feb200f7bc-ed0a96dd3d74c134c3.jpg", 
    "https://graph.org/file/7ab8a716cb00a542acdac-677062efb59b3f5c44.jpg", 
    "https://graph.org/file/a617481d19aa04ace0c7c-ab1b60b42572ba17ae.jpg", 
    "https://graph.org/file/a0aecb9fe2fe82e47ee29-407fa0435de3264296.jpg",
    "https://graph.org/file/580287fb4b172bd0a7919-8085660baa0f8326c9.jpg",
    "https://graph.org/file/c57ea68eab59cee31758b-e4ccde7a74cdf7c049.jpg",
    
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

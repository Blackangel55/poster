import os


# ─── TELEGRAM ────────────────────────────────────────────────────────────────
# Get API_ID and API_HASH from https://my.telegram.org
API_ID   = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")

# Get BOT_TOKEN from @BotFather on Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

# ─── OWNER / ADMIN ───────────────────────────────────────────────────────────
# Owner has full control — cannot be banned or removed from admin
# Add your Telegram user ID (integer) — get it from @userinfobot
OWNER_ID = int(os.getenv("OWNER_ID", "1350212613"))

# Static admin list — comma-separated user IDs e.g. "123456,789012"
# These are loaded at startup in addition to DB admins
# Dynamic admins can be added/removed via /addadmin and /deladmin commands
_ADMIN_IDS = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = (
    [int(x.strip()) for x in _ADMIN_IDS.split(",") if x.strip().isdigit()]
    if _ADMIN_IDS else []
)

# ─── MONGODB ─────────────────────────────────────────────────────────────────
# Get a free cluster at https://cloud.mongodb.com
DB_URI  = os.getenv("DB_URI", "mongodb+srv://AMFILMS:AMFILMS@cluster0.ddafmva.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.getenv("DB_NAME", "ott_poster")

# ─── SPIDY POSTER API ────────────────────────────────────────────────────────
SPIDY_KEY  = os.getenv("SPIDY_KEY", "YOUR_SPIDY_API_KEY")
SPIDY_BASE = os.getenv("SPIDY_BASE", "https://poster-api.ispidy.com/v1/fetch")

# ─── BOT SETTINGS ────────────────────────────────────────────────────────────
# Session file path — Kurigram writes a .session file here
SESSION_NAME = os.getenv("SESSION_NAME", "/app/sessions/ott_poster_bot")

# Max characters for plot/overview in captions
PLOT_MAX_CHARS = int(os.getenv("PLOT_MAX_CHARS", "280"))

# Spidy API request timeout in seconds
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))

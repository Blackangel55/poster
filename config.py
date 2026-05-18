import os
API_ID   = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "1350212613"))

# Static admin list — comma-separated user IDs e.g. "123456,789012"
_ADMIN_IDS = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = (
    [int(x.strip()) for x in _ADMIN_IDS.split(",") if x.strip().isdigit()]
    if _ADMIN_IDS else []
)

DB_URI  = os.getenv("DB_URI", "")
DB_NAME = os.getenv("DB_NAME", "ott_poster")

SPIDY_KEY  = os.getenv("SPIDY_KEY", "YOUR_SPIDY_API_KEY")
SPIDY_BASE = os.getenv("SPIDY_BASE", "https://poster-api.ispidy.com/v1/fetch")

SESSION_NAME = os.getenv("SESSION_NAME", "/app/sessions/ott_poster_bot")

PLOT_MAX_CHARS = int(os.getenv("PLOT_MAX_CHARS", "280"))

API_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))

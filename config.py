import os

# ─── TELEGRAM ────────────────────────────────────────────────────────────────
# Get API_ID and API_HASH from https://my.telegram.org
API_ID    = int(os.getenv("API_ID", "0"))
API_HASH  = os.getenv("API_HASH", "YOUR_API_HASH")

# Get BOT_TOKEN from @BotFather on Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

# ─── SPIDY POSTER API ────────────────────────────────────────────────────────
SPIDY_KEY  = os.getenv("SPIDY_KEY", "YOUR_SPIDY_API_KEY")
SPIDY_BASE = os.getenv("SPIDY_BASE", "https://api.spidyposter.com/v1/fetch")

# ─── BOT SETTINGS ────────────────────────────────────────────────────────────
# Session file path — Kurigram writes a .session file here
# In Docker this goes to /app/sessions/ott_poster_bot.session (created in Dockerfile)
SESSION_NAME = os.getenv("SESSION_NAME", "/app/sessions/ott_poster_bot")

# Max characters for plot/overview in captions
PLOT_MAX_CHARS = int(os.getenv("PLOT_MAX_CHARS", "280"))

# Spidy API request timeout in seconds
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))

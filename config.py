"""
config.py — Central config for OTT Poster Bot
Edit values here OR set environment variables (env vars take priority).
"""

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
# Session file name (Kurigram saves a .session file with this name)
SESSION_NAME = os.getenv("SESSION_NAME", "ott_poster_bot")

# Max characters for plot/overview in captions
PLOT_MAX_CHARS = int(os.getenv("PLOT_MAX_CHARS", "280"))

# Spidy API request timeout in seconds
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "15"))

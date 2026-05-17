"""
generate_session.py
Run this ONCE locally to generate a Pyrogram string session.
Copy the output string and set it as SESSION_STRING env var in Koyeb.
This avoids the ephemeral filesystem problem on free-tier cloud hosts.

Usage:
    python generate_session.py
"""

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import os
from pyrogram import Client

API_ID    = int(os.getenv("API_ID", "0"))
API_HASH  = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    print("❌ Set API_ID, API_HASH, and BOT_TOKEN in your .env or shell first.")
    exit(1)

with Client(":memory:", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN) as app:
    session_string = app.export_session_string()

print("\n✅ Your session string (set this as SESSION_STRING in Koyeb):\n")
print(session_string)
print("\n⚠️  Keep this secret — it gives full access to your bot account.")

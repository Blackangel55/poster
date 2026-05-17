"""
OTT Poster Bot — powered by Kurigram (Pyrogram fork)
Fetches movie & TV show posters using the Spidy Poster API.

Spidy API Endpoints:
  Movie  → /v1/fetch?api_key=KEY&title=RRR&year=2022
  TV     → /v1/fetch?api_key=KEY&title=Asur&season=2
  Query  → /v1/fetch?api_key=KEY&query=Asur.S02.1080p.mkv

Commands:
  /start          – Welcome message with buttons
  /help           – Full help & tips
  /about          – About this bot
  /movie RRR 2022 – Movie poster (optional year)
  /tv Asur 2      – TV season poster (optional season number)
  /query filename – Filename parser search
  /search Asur    – Auto plain-title search
  plain text      – Quick search by typing a title

All messages/texts live in script.py — edit there, not here.
"""

import os
import asyncio
import threading
import logging
import aiohttp

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message

# ─── LOAD .env ────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─── CONFIG ──────────────────────────────────────────────────────────────────
from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    SPIDY_KEY,
    SPIDY_BASE,
    SESSION_NAME,
    PLOT_MAX_CHARS,
    API_TIMEOUT,
)

# ─── SCRIPT ──────────────────────────────────────────────────────────────────
from script import (
    START_TEXT,
    START_BUTTONS,
    HELP_TEXT,
    HELP_BUTTONS,
    ABOUT_TEXT,
    ABOUT_BUTTONS,
    SEARCHING_TEXT,
    NOT_FOUND_TEXT,
    API_ERROR_TEXT,
    USAGE_MOVIE_TEXT,
    USAGE_TV_TEXT,
    USAGE_QUERY_TEXT,
    USAGE_SEARCH_TEXT,
    build_caption,
    build_keyboard,
)

# ─── LOGGING ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger(__name__)

# ─── KURIGRAM CLIENT ─────────────────────────────────────────────────────────
app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


# ─── SPIDY API ───────────────────────────────────────────────────────────────
async def fetch_poster(
    title: str = None,
    year: str = None,
    season: str = None,
    query: str = None,
) -> dict | None:
    """
    Call Spidy Poster API.

    Modes:
      - title + year  → movie search
      - title + season → TV season search
      - title only    → general search
      - query         → filename parser (e.g. Asur.S02.1080p.mkv)
    """
    params = {"api_key": SPIDY_KEY}

    if query:
        # Filename parser mode — takes priority
        params["query"] = query
    else:
        params["title"] = title
        if year:
            params["year"] = year
        if season:
            params["season"] = season

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                SPIDY_BASE,
                params=params,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                log.info(
                    "Spidy API → title=%s year=%s season=%s query=%s | type=%s",
                    title, year, season, query,
                    data.get("type", "?"),
                )
                return data
    except aiohttp.ClientResponseError as e:
        log.error("Spidy API HTTP %s: %s", e.status, e.message)
    except aiohttp.ClientError as e:
        log.error("Spidy API error: %s", e)
    except asyncio.TimeoutError:
        log.error("Spidy API timed out after %ss", API_TIMEOUT)
    return None


# ─── CORE POSTER SENDER ──────────────────────────────────────────────────────
async def send_poster(
    client: Client,
    message: Message,
    title: str = None,
    year: str = None,
    season: str = None,
    query: str = None,
):
    label = query or title
    thinking = await message.reply(SEARCHING_TEXT.format(title=label))

    data = await fetch_poster(title=title, year=year, season=season, query=query)

    await thinking.delete()

    # ── Error handling ──
    if not data:
        await message.reply(API_ERROR_TEXT)
        return

    if not data.get("poster"):
        await message.reply(NOT_FOUND_TEXT.format(title=label))
        return

    poster_url   = data["poster"]
    landscape_url = data.get("landscape")   # bonus wide image from API
    caption      = build_caption(data, plot_max=PLOT_MAX_CHARS)
    keyboard     = build_keyboard(data, landscape_url=landscape_url)

    # ── Send poster photo ──
    try:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=poster_url,
            caption=caption,
            reply_markup=keyboard,
        )
    except Exception as e:
        log.warning("send_photo failed (%s) — sending as link", e)
        fallback = f"{caption}\n\n🖼 [View Poster]({poster_url})"
        await message.reply(
            fallback,
            reply_markup=keyboard,
            disable_web_page_preview=False,
        )


# ─── COMMAND HANDLERS ────────────────────────────────────────────────────────

@app.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, message: Message):
    first_name = message.from_user.first_name or "there"
    await message.reply(
        START_TEXT.format(first_name=first_name),
        reply_markup=START_BUTTONS,
    )


@app.on_message(filters.command("help") & filters.private)
async def cmd_help(client: Client, message: Message):
    await message.reply(HELP_TEXT, reply_markup=HELP_BUTTONS)


@app.on_message(filters.command("about") & filters.private)
async def cmd_about(client: Client, message: Message):
    await message.reply(ABOUT_TEXT, reply_markup=ABOUT_BUTTONS)


@app.on_message(filters.command("movie") & filters.private)
async def cmd_movie(client: Client, message: Message):
    """
    /movie <title> [year]
    Uses: title + optional year → Spidy movie search
    """
    args = message.command[1:]
    if not args:
        await message.reply(USAGE_MOVIE_TEXT)
        return

    # Trailing 4-digit number = year
    if len(args) > 1 and args[-1].isdigit() and len(args[-1]) == 4:
        title = " ".join(args[:-1])
        year  = args[-1]
    else:
        title = " ".join(args)
        year  = None

    await send_poster(client, message, title=title, year=year)


@app.on_message(filters.command("tv") & filters.private)
async def cmd_tv(client: Client, message: Message):
    """
    /tv <title> [season]
    Uses: title + optional season number → Spidy TV search
    """
    args = message.command[1:]
    if not args:
        await message.reply(USAGE_TV_TEXT)
        return

    # Trailing number = season
    if len(args) > 1 and args[-1].isdigit():
        title  = " ".join(args[:-1])
        season = args[-1]
    else:
        title  = " ".join(args)
        season = None

    await send_poster(client, message, title=title, season=season)


@app.on_message(filters.command("query") & filters.private)
async def cmd_query(client: Client, message: Message):
    """
    /query <filename>
    Uses: Spidy filename parser — e.g. Asur.S02.1080p.mkv
    """
    args = message.command[1:]
    if not args:
        await message.reply(USAGE_QUERY_TEXT)
        return

    query = " ".join(args)
    await send_poster(client, message, query=query)


@app.on_message(filters.command("search") & filters.private)
async def cmd_search(client: Client, message: Message):
    """
    /search <title>
    Uses: title only → Spidy general search (auto-detects movie/TV)
    """
    args = message.command[1:]
    if not args:
        await message.reply(USAGE_SEARCH_TEXT)
        return

    title = " ".join(args)
    await send_poster(client, message, title=title)


@app.on_message(
    filters.private
    & filters.text
    & ~filters.command(["start", "help", "about", "movie", "tv", "query", "search"])
)
async def plain_search(client: Client, message: Message):
    """Any plain text → quick title search."""
    title = message.text.strip()
    if title:
        await send_poster(client, message, title=title)


# ─── CALLBACK QUERY HANDLERS ─────────────────────────────────────────────────

@app.on_callback_query(filters.regex("^start$"))
async def cb_start(client: Client, query: CallbackQuery):
    first_name = query.from_user.first_name or "there"
    await query.edit_message_text(
        START_TEXT.format(first_name=first_name),
        reply_markup=START_BUTTONS,
    )
    await query.answer()


@app.on_callback_query(filters.regex("^help$"))
async def cb_help(client: Client, query: CallbackQuery):
    await query.edit_message_text(HELP_TEXT, reply_markup=HELP_BUTTONS)
    await query.answer()


@app.on_callback_query(filters.regex("^about$"))
async def cb_about(client: Client, query: CallbackQuery):
    await query.edit_message_text(ABOUT_TEXT, reply_markup=ABOUT_BUTTONS)
    await query.answer()


# ─── KOYEB HEALTH SERVER ─────────────────────────────────────────────────────
from flask import Flask as _Flask

_health_app = _Flask(__name__)

@_health_app.route("/")
def _home():
    return "OTT Poster Bot is running! 🎬", 200

@_health_app.route("/health")
def _health():
    return {"status": "ok"}, 200

def _run_health_server():
    port = int(os.getenv("PORT", "8000"))
    log.info("Health server on port %s", port)
    _health_app.run(host="0.0.0.0", port=port, use_reloader=False)


# ─── RUN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    keep_alive = os.getenv("KEEP_ALIVE", "true").lower() == "true"
    if keep_alive:
        threading.Thread(target=_run_health_server, daemon=True).start()

    log.info("Starting OTT Poster Bot…")
    app.run()

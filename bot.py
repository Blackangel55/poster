import io
import os
import hashlib
import asyncio
import threading
import logging
import aiohttp

from pyrogram import Client, filters, enums
from pyrogram.types import (
    CallbackQuery,
    LinkPreviewOptions,
    Message,
)

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
    OWNER_ID,
    ADMIN_IDS,
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
    build_fsub_message,
    FSUB_STILL_NOT_JOINED,
    FSUB_JOINED,
    USAGE_ADDFSUB,
    USAGE_DELFSUB,
)

# ─── DATABASE ────────────────────────────────────────────────────────────────
from database import db

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


# ─── HELPERS ─────────────────────────────────────────────────────────────────
async def is_admin(user_id: int) -> bool:
    """Check if user is owner, static admin, or DB admin."""
    if user_id == OWNER_ID:
        return True
    if user_id in ADMIN_IDS:
        return True
    return await db.is_admin(user_id)


async def is_banned(user_id: int) -> bool:
    """Owner and admins can never be banned."""
    if user_id == OWNER_ID or await is_admin(user_id):
        return False
    return await db.is_banned(user_id)


# ─── FORCE SUBSCRIBE CHECK ───────────────────────────────────────────────────
async def check_fsub(client: Client, user_id: int) -> tuple[bool, list[dict]]:
    """
    Returns (all_joined, not_joined_channels).
    not_joined_channels is a list of dicts: {id, title, invite_link}
    """
    channel_ids = await db.get_fsub_channels()
    if not channel_ids:
        return True, []

    not_joined = []
    for ch_id in channel_ids:
        try:
            member = await client.get_chat_member(ch_id, user_id)
            if member.status.value in ("left", "banned", "restricted"):
                raise Exception("not member")
        except Exception:
            try:
                chat = await client.get_chat(ch_id)
                invite = await client.export_chat_invite_link(ch_id)
                not_joined.append({
                    "id": ch_id,
                    "title": chat.title,
                    "invite_link": invite,
                })
            except Exception as e:
                log.warning("Could not get fsub channel info for %s: %s", ch_id, e)

    return len(not_joined) == 0, not_joined


# ─── MIDDLEWARE — register user, check ban & fsub ────────────────────────────
@app.on_message(filters.private & filters.incoming, group=-1)
async def middleware(client: Client, message: Message):
    user_id = message.from_user.id

    # Auto-register user
    await db.add_user(user_id)

    # Block banned users
    if await is_banned(user_id):
        await message.reply("🚫 You are banned from using this bot.")
        message.stop_propagation()
        return

    # Skip fsub check for admins and /start command
    cmd = message.command[0].lower() if message.command else ""
    if await is_admin(user_id) or cmd == "start":
        return

    # Force subscribe check
    joined, missing = await check_fsub(client, user_id)
    if not joined:
        text, keyboard = build_fsub_message(missing)
        await message.reply(text, reply_markup=keyboard)
        message.stop_propagation()


# ─── SPIDY API ───────────────────────────────────────────────────────────────
async def fetch_poster(
    title: str = None,
    year: str = None,
    season: str = None,
    query: str = None,
) -> dict | None:
    params = {"api_key": SPIDY_KEY}
    if query:
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
                log.info("Spidy API raw response: %s", data)

                results = data.get("results", [])
                if not results:
                    log.warning("Spidy API returned empty results")
                    return None

                result = results[0]
                log.info("Spidy API → picked result: %s", result)
                return result
    except aiohttp.ClientResponseError as e:
        log.error("Spidy API HTTP %s: %s", e.status, e.message)
    except aiohttp.ClientError as e:
        log.error("Spidy API error: %s", e)
    except asyncio.TimeoutError:
        log.error("Spidy API timed out after %ss", API_TIMEOUT)
    return None


# ─── IMAGE DOWNLOADER ────────────────────────────────────────────────────────
async def download_image(url: str) -> bytes | None:
    """Download image with browser UA to bypass CDN restrictions (Zee5, Hotstar etc.)"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.zee5.com/",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                resp.raise_for_status()
                return await resp.read()
    except Exception as e:
        log.error("Image download failed: %s", e)
    return None


def url_hash(url: str) -> str:
    """Short MD5 hash of a URL — used as the MongoDB cache key."""
    return hashlib.md5(url.encode()).hexdigest()


def convert_to_jpeg(image_bytes: bytes) -> bytes:
    """
    Convert any valid image to JPEG using Pillow.
    Telegram reliably accepts JPEG — this fixes PHOTO_SAVE_FILE_INVALID
    for WebP, PNG with alpha, and other edge-case formats.
    Returns original bytes if conversion fails.
    """
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        # Convert RGBA/P mode images (PNG with transparency) to RGB for JPEG
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        converted = buf.getvalue()
        log.info(
            "Converted image to JPEG: %d bytes → %d bytes",
            len(image_bytes), len(converted)
        )
        return converted
    except Exception as e:
        log.warning("JPEG conversion failed (%s) — using original bytes", e)
        return image_bytes


def is_valid_image(data: bytes) -> bool:
    """
    Check magic bytes to confirm the download is actually an image.
    Telegram rejects non-image bytes with PHOTO_SAVE_FILE_INVALID.
    Supported: JPEG, PNG, WEBP, GIF
    """
    if not data or len(data) < 4:
        return False
    # JPEG: FF D8 FF
    if data[:3] == b'\xff\xd8\xff':
        return True
    # PNG: 89 50 4E 47
    if data[:4] == b'\x89PNG':
        return True
    # WEBP: RIFF....WEBP
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return True
    # GIF: GIF87a or GIF89a
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return True
    return False


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

    if not data:
        await message.reply(API_ERROR_TEXT)
        return

    image_url = data.get("landscape")
    if not image_url:
        await message.reply(NOT_FOUND_TEXT.format(title=label))
        return

    caption  = build_caption(data, plot_max=PLOT_MAX_CHARS)
    keyboard = build_keyboard(data)
    cache_key = url_hash(image_url)

    # ── 1. Check MongoDB cache ──────────────────────────────────────────────
    cached = await db.get_cached_image(cache_key)

    if cached and cached.get("file_id"):
        # Best case: reuse Telegram file_id — instant, no download
        log.info("Cache HIT (file_id): %s", cache_key)
        try:
            await client.send_photo(
                chat_id=message.chat.id,
                photo=cached["file_id"],
                caption=caption,
                reply_markup=keyboard,
            )
            return
        except Exception as e:
            # file_id expired or invalid — clear it and fall through
            log.warning("Cached file_id failed (%s), clearing and retrying", e)
            await db.update_file_id(cache_key, None)

    if cached and cached.get("bytes"):
        # Bytes cached — validate before sending
        image_bytes = bytes(cached["bytes"])
        log.info("Cache HIT (bytes): %s", cache_key)
        if not is_valid_image(image_bytes):
            log.warning("Cached bytes are not a valid image — clearing cache entry")
            await db.clear_cache(cache_key)
            image_bytes = None
    else:
        image_bytes = None

    # Cache MISS or invalid cached bytes — download fresh
    if not image_bytes:
        log.info("Downloading image: %s", image_url)
        image_bytes = await download_image(image_url)

        if not image_bytes:
            log.error("Download returned empty response")
            await message.reply(NOT_FOUND_TEXT.format(title=label))
            return

        if not is_valid_image(image_bytes):
            # Downloaded file is not a real image (HTML error page, etc.)
            log.error(
                "Downloaded file is not a valid image (magic bytes: %s) — url: %s",
                image_bytes[:16].hex(), image_url
            )
            await message.reply(
                f"{caption}\n\n"
                "⚠️ _Poster image could not be loaded (invalid format)._\n"
                f"🖼 [View directly]({image_url})",
                reply_markup=keyboard,
                link_preview_options=LinkPreviewOptions(is_disabled=True),
            )
            return

        # Valid image — cache bytes now, file_id after send
        await db.cache_image(cache_key, image_url, image_bytes=image_bytes)

    # ── 2. Try converting to JPEG first (fixes most Telegram rejections) ─────
    image_bytes = convert_to_jpeg(image_bytes)
    await db.cache_image(cache_key, image_url, image_bytes=image_bytes)

    # ── 3. Send photo — Telegram file_id cached on success ──────────────────
    try:
        sent = await client.send_photo(
            chat_id=message.chat.id,
            photo=io.BytesIO(image_bytes),
            caption=caption,
            reply_markup=keyboard,
        )
        if sent and sent.photo:
            await db.update_file_id(cache_key, sent.photo.file_id)
            log.info("file_id cached: %s", sent.photo.file_id)
        return
    except Exception as e:
        log.warning("send_photo failed (%s) — trying send_document", e)

    # ── 4. Fallback: send as document (always accepted by Telegram) ──────────
    try:
        sent = await client.send_document(
            chat_id=message.chat.id,
            document=io.BytesIO(image_bytes),
            file_name="poster.jpg",
            caption=caption,
            reply_markup=keyboard,
        )
        if sent and sent.document:
            await db.update_file_id(cache_key, sent.document.file_id)
            log.info("Sent as document, file_id cached: %s", sent.document.file_id)
        return
    except Exception as e:
        log.error("send_document also failed (%s) — sending link", e)

    # ── 5. Last resort: send as plain link ───────────────────────────────────
    await message.reply(
        f"{caption}\n\n🖼 [View Poster]({image_url})",
        reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# ════════════════════════════════════════════════════════════════════════════
# USER COMMANDS
# ════════════════════════════════════════════════════════════════════════════

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
    me = await client.get_me()
    await message.reply(
        ABOUT_TEXT.format(me.first_name),
        reply_markup=ABOUT_BUTTONS,
        parse_mode=enums.ParseMode.HTML,
    )


@app.on_message(filters.command("movie") & filters.private)
async def cmd_movie(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        await message.reply(USAGE_MOVIE_TEXT)
        return
    if len(args) > 1 and args[-1].isdigit() and len(args[-1]) == 4:
        title, year = " ".join(args[:-1]), args[-1]
    else:
        title, year = " ".join(args), None
    await send_poster(client, message, title=title, year=year)


@app.on_message(filters.command("tv") & filters.private)
async def cmd_tv(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        await message.reply(USAGE_TV_TEXT)
        return
    if len(args) > 1 and args[-1].isdigit():
        title, season = " ".join(args[:-1]), args[-1]
    else:
        title, season = " ".join(args), None
    await send_poster(client, message, title=title, season=season)


@app.on_message(filters.command("query") & filters.private)
async def cmd_query(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        await message.reply(USAGE_QUERY_TEXT)
        return
    await send_poster(client, message, query=" ".join(args))


@app.on_message(filters.command("search") & filters.private)
async def cmd_search(client: Client, message: Message):
    args = message.command[1:]
    if not args:
        await message.reply(USAGE_SEARCH_TEXT)
        return
    await send_poster(client, message, title=" ".join(args))


@app.on_message(
    filters.private & filters.text
    & ~filters.command(["start","help","about","movie","tv","query","search",
                        "addadmin","deladmin","admins","ban","unban","banned",
                        "stats","broadcast","addfsub","delfsub","listfsub"])
)
async def plain_search(client: Client, message: Message):
    title = message.text.strip()
    if title:
        await send_poster(client, message, title=title)


# ════════════════════════════════════════════════════════════════════════════
# ADMIN COMMANDS
# ════════════════════════════════════════════════════════════════════════════

@app.on_message(filters.command("stats") & filters.private)
async def cmd_stats(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")

    total   = await db.total_users()
    banned  = len(await db.get_banned_users())
    admins  = await db.get_all_admins()

    await message.reply(
        f"📊 **Bot Statistics**\n\n"
        f"👥 Total Users: `{total}`\n"
        f"🚫 Banned Users: `{banned}`\n"
        f"👮 DB Admins: `{len(admins)}`\n"
        f"🔑 Static Admins: `{len(ADMIN_IDS)}`"
    )


@app.on_message(filters.command("admins") & filters.private)
async def cmd_admins(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")

    db_admins = await db.get_all_admins()
    all_admins = list(set([OWNER_ID] + ADMIN_IDS + db_admins))

    lines = ["👮 **Admin List**\n"]
    for uid in all_admins:
        tag = " 👑 Owner" if uid == OWNER_ID else ""
        lines.append(f"• `{uid}`{tag}")
    await message.reply("\n".join(lines))


@app.on_message(filters.command("addadmin") & filters.private)
async def cmd_addadmin(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("⛔ Owner only.")

    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply("Usage: `/addadmin <user_id>`")

    user_id = int(args[0])
    if user_id == OWNER_ID:
        return await message.reply("That's already the owner.")

    await db.add_admin(user_id)
    await message.reply(f"✅ `{user_id}` added as admin.")


@app.on_message(filters.command("deladmin") & filters.private)
async def cmd_deladmin(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply("⛔ Owner only.")

    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply("Usage: `/deladmin <user_id>`")

    user_id = int(args[0])
    if user_id == OWNER_ID:
        return await message.reply("Cannot remove the owner.")

    await db.del_admin(user_id)
    await message.reply(f"✅ `{user_id}` removed from admins.")


@app.on_message(filters.command("ban") & filters.private)
async def cmd_ban(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")

    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply("Usage: `/ban <user_id>`")

    user_id = int(args[0])
    if user_id == OWNER_ID:
        return await message.reply("Cannot ban the owner.")
    if await is_admin(user_id):
        return await message.reply("Cannot ban an admin.")

    await db.ban_user(user_id)
    await message.reply(f"🚫 `{user_id}` has been banned.")


@app.on_message(filters.command("unban") & filters.private)
async def cmd_unban(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")

    args = message.command[1:]
    if not args or not args[0].isdigit():
        return await message.reply("Usage: `/unban <user_id>`")

    user_id = int(args[0])
    await db.unban_user(user_id)
    await message.reply(f"✅ `{user_id}` has been unbanned.")


@app.on_message(filters.command("banned") & filters.private)
async def cmd_banned(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")

    banned = await db.get_banned_users()
    if not banned:
        return await message.reply("✅ No banned users.")

    lines = ["🚫 **Banned Users**\n"]
    for uid in banned:
        lines.append(f"• `{uid}`")
    await message.reply("\n".join(lines))


@app.on_message(filters.command("broadcast") & filters.private)
async def cmd_broadcast(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")

    if not message.reply_to_message:
        return await message.reply(
            "Reply to a message with `/broadcast` to send it to all users."
        )

    status = await message.reply("📢 Broadcasting…")
    users  = await db.get_all_users()

    done, failed = 0, 0
    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            done += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)   # avoid flood limits

    await status.edit(
        f"📢 **Broadcast Complete**\n\n"
        f"✅ Sent: `{done}`\n"
        f"❌ Failed: `{failed}`\n"
        f"👥 Total: `{len(users)}`"
    )


# ─── FORCE SUBSCRIBE COMMANDS ───────────────────────────────────────────────

@app.on_message(filters.command("addfsub") & filters.private)
async def cmd_addfsub(client: Client, message: Message):
    """
    /addfsub <channel_id>
    Bot must be admin in the channel with invite link permission.
    """
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")

    args = message.command[1:]
    if not args:
        return await message.reply(USAGE_ADDFSUB)

    raw = args[0].lstrip("-")
    if not raw.isdigit():
        return await message.reply("❌ Invalid channel ID. Must be a number like `-1001234567890`")

    channel_id = int(args[0])

    # Verify bot is admin in that channel
    try:
        chat = await client.get_chat(channel_id)
        bot_member = await client.get_chat_member(channel_id, "me")
        if bot_member.status.value not in ("administrator", "creator"):
            return await message.reply(
                "❌ Bot is not an admin in that channel.\n"
                "Make the bot an admin with **Invite Users** permission first."
            )
    except Exception as e:
        return await message.reply(f"❌ Could not access channel: `{e}`")

    await db.add_fsub_channel(channel_id)
    await message.reply(
        f"✅ **{chat.title}** added to force subscribe list.\n"
        f"Channel ID: `{channel_id}`"
    )


@app.on_message(filters.command("delfsub") & filters.private)
async def cmd_delfsub(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")

    args = message.command[1:]
    if not args:
        return await message.reply(USAGE_DELFSUB)

    raw = args[0].lstrip("-")
    if not raw.isdigit():
        return await message.reply("❌ Invalid channel ID.")

    channel_id = int(args[0])
    if not await db.fsub_channel_exists(channel_id):
        return await message.reply("❌ That channel is not in the fsub list.")

    await db.remove_fsub_channel(channel_id)
    await message.reply(f"✅ Channel `{channel_id}` removed from force subscribe list.")


@app.on_message(filters.command("listfsub") & filters.private)
async def cmd_listfsub(client: Client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("⛔ Admins only.")

    channels = await db.get_fsub_channels()
    if not channels:
        return await message.reply("📭 No force subscribe channels set.")

    lines = ["📋 **Force Subscribe Channels**\n"]
    for ch_id in channels:
        try:
            chat = await client.get_chat(ch_id)
            lines.append(f"• **{chat.title}** — `{ch_id}`")
        except Exception:
            lines.append(f"• `{ch_id}` _(could not fetch name)_")

    await message.reply("\n".join(lines))


# ─── CALLBACK QUERY HANDLERS ─────────────────────────────────────────────────

@app.on_callback_query(filters.regex("^check_fsub$"))
async def cb_check_fsub(client: Client, query: CallbackQuery):
    """User taps 'I've Joined' — re-verify all channels."""
    user_id = query.from_user.id
    joined, missing = await check_fsub(client, user_id)

    if joined:
        await query.edit_message_text(FSUB_JOINED)
        await query.answer("✅ Verified!", show_alert=False)
    else:
        text, keyboard = build_fsub_message(missing)
        await query.edit_message_text(text, reply_markup=keyboard)
        await query.answer(FSUB_STILL_NOT_JOINED, show_alert=True)


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
    me = await client.get_me()
    await query.edit_message_text(
        ABOUT_TEXT.format(me.first_name),
        reply_markup=ABOUT_BUTTONS,
        parse_mode=enums.ParseMode.HTML,
    )
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

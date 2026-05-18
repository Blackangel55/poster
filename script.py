from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ════════════════════════════════════════════════════════════════════════════
# START MESSAGE
# ════════════════════════════════════════════════════════════════════════════

START_TEXT = """🎬 **Welcome to OTT Poster Bot!**

Hey {first_name}! 👋
I fetch **movie & TV show posters** instantly.

_Example:_ `/movie RRR 2022`
_Example:_ `/tv Asur 2`

💡 `/help` — Full help & tips
ℹ️ `/about` — About this bot
"""

START_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🎬 Movie", switch_inline_query_current_chat="movie "),
        InlineKeyboardButton("📺 TV Series", switch_inline_query_current_chat="tv "),
    ],
    [
        InlineKeyboardButton("💡 Help", callback_data="help"),
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
    ],
])


# ════════════════════════════════════════════════════════════════════════════
# HELP MESSAGE
# ════════════════════════════════════════════════════════════════════════════

HELP_TEXT = """💡 **OTT Poster Bot — Help**

━━━━━━━━━━━━━━━━━━━━
🎬 **Movie Search**
━━━━━━━━━━━━━━━━━━━━
`/movie <Title>`
`/movie <Title> <Year>`

• `/movie Bahubali`
• `/movie RRR 2022`
• `/movie The Dark Knight 2008`

━━━━━━━━━━━━━━━━━━━━
📺 **TV / OTT Series**
━━━━━━━━━━━━━━━━━━━━
`/tv <Title>`
`/tv <Title> <Season>`

• `/tv Mirzapur`
• `/tv Asur 2`
• `/tv Sacred Games 1`

━━━━━━━━━━━━━━━━━━━━
🗂 **Filename Search**
━━━━━━━━━━━━━━━━━━━━
`/query <Filename>`
_Auto-parses season, year, quality from filename._

• `/query Asur.S02.1080p.mkv`
• `/query RRR.2022.BluRay.mkv`
• `/query Sacred.Games.S01E03.mkv`

━━━━━━━━━━━━━━━━━━━━
🔍 **General Search**
━━━━━━━━━━━━━━━━━━━━
`/search <Title>`
_Auto-detects movie or TV show._

• `/search Pushpa`
• `/search Family Man`

━━━━━━━━━━━━━━━━━━━━
⚡ **Quick Search**
━━━━━━━━━━━━━━━━━━━━
Just **type any title** — no command needed!

• `KGF Chapter 2`
• `Scam 1992`

━━━━━━━━━━━━━━━━━━━━
💬 **Tips**
• Add year for accuracy: `/movie KGF 2022`
• Add season for specific poster: `/tv Asur 2`
• Use `/query` if you have a filename — it's the most accurate!
"""

HELP_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Back to Start", callback_data="start")],
])


# ════════════════════════════════════════════════════════════════════════════
# ABOUT MESSAGE
# ════════════════════════════════════════════════════════════════════════════

ABOUT_TEXT = """<b>○ 𝖬𝗒 𝖭𝖺𝗆𝖾: {}
○ 𝖢𝗋𝖾𝖺𝗍𝗈𝗋 : <a href='https://t.me/GUARDIANff'>𝖳𝗁𝗂𝗌 𝖯𝖾𝗋𝗌𝗈𝗇</a>
○ 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾 : 𝖯𝗒𝗍𝗁𝗈𝗇 𝟥
○ 𝖫𝗂𝖻𝗋𝖺𝗋𝗒 : 𝖪𝗎𝗋𝗂𝗀𝗋𝖺𝗆 (𝖯𝗒𝗋𝗈𝗀𝗋𝖺𝗆 𝖿𝗈𝗋𝗄)
○ 𝖯𝗈𝗌𝗍𝖾𝗋 𝖠𝖯𝖨 : 𝖲𝗉𝗂𝖽𝗒 𝖯𝗈𝗌𝗍𝖾𝗋 𝖠𝖯𝖨
○ 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖦𝗋𝗈𝗎𝗉 : <a href='https://t.me/AM_FILMS'>𝖳𝖺𝗉 𝖧𝖾𝗋𝖾</a></b>"""

ABOUT_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Back to Start", callback_data="start")],
])


# ════════════════════════════════════════════════════════════════════════════
# STATUS MESSAGES
# ════════════════════════════════════════════════════════════════════════════

SEARCHING_TEXT = "🔍 Searching for **{title}**…"

NOT_FOUND_TEXT = """❌ **No results found for:** `{title}`

Try:
• Check the spelling
• Add year: `/movie {title} 2023`
• For a series: `/tv {title}`
• Use filename: `/query {title}.S01.mkv`
"""

API_ERROR_TEXT = """⚠️ **Could not reach the Spidy API.**

Please try again in a moment.
"""


# ════════════════════════════════════════════════════════════════════════════
# USAGE / EMPTY COMMAND MESSAGES
# ════════════════════════════════════════════════════════════════════════════

USAGE_MOVIE_TEXT = """ℹ️ **Usage:** `/movie Title [Year]`

• `/movie RRR 2022`
• `/movie Bahubali`
"""

USAGE_TV_TEXT = """ℹ️ **Usage:** `/tv Title [Season]`

• `/tv Asur 2`
• `/tv Mirzapur`
"""

USAGE_QUERY_TEXT = """ℹ️ **Usage:** `/query Filename`

Parses season, year, quality automatically from the filename.

• `/query Asur.S02.1080p.mkv`
• `/query RRR.2022.BluRay.mkv`
"""

USAGE_SEARCH_TEXT = """ℹ️ **Usage:** `/search Title`

• `/search Pushpa`
• `/search Family Man`
"""


# ════════════════════════════════════════════════════════════════════════════
# FORCE SUBSCRIBE
# ════════════════════════════════════════════════════════════════════════════

def build_fsub_message(channels: list[dict]) -> tuple[str, "InlineKeyboardMarkup"]:
    """
    Build the force-subscribe message and join buttons.
    channels: list of dicts with keys: id, title, invite_link
    """
    text = (
        "👋 **Hello!**\n\n"
        "To use this bot you must join our channel(s) first:\n\n"
    )
    for i, ch in enumerate(channels, 1):
        text += f"{i}. **{ch['title']}**\n"

    text += "\nAfter joining, tap **✅ I've Joined** below."

    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(f"➕ Join {ch['title']}", url=ch["invite_link"])])
    buttons.append([InlineKeyboardButton("✅ I've Joined", callback_data="check_fsub")])

    return text, InlineKeyboardMarkup(buttons)


FSUB_STILL_NOT_JOINED = (
    "❌ You haven't joined all required channels yet!\n\n"
    "Please join all channels and tap **✅ I've Joined** again."
)

FSUB_JOINED = "✅ **Verified!** Welcome, enjoy the bot 🎬"

USAGE_ADDFSUB = "Usage: `/addfsub <channel_id>`\nExample: `/addfsub -1001234567890`"
USAGE_DELFSUB = "Usage: `/delfsub <channel_id>`\nExample: `/delfsub -1001234567890`"


# ════════════════════════════════════════════════════════════════════════════
# CAPTION BUILDER
# ════════════════════════════════════════════════════════════════════════════

def build_caption(data: dict, plot_max: int = 280) -> str:
    """
    Build a caption from Spidy API response.
    Real fields: title (str), year (int), landscape (URL)
    """
    title = data.get("title", "Unknown")
    year  = data.get("year", "")

    lines = []
    if year:
        lines.append(f"🎬 **{title}** ({year})")
    else:
        lines.append(f"🎬 **{title}**")

    lines.append("━━━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════════
# KEYBOARD BUILDER
# ════════════════════════════════════════════════════════════════════════════

def build_keyboard(data: dict) -> InlineKeyboardMarkup | None:
    """Reserved for future use when API returns extra URLs."""
    return None

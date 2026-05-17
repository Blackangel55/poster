"""
script.py — All bot messages, captions, and keyboards for OTT Poster Bot.
Edit this file to customise every message without touching bot.py.

Spidy API response fields used:
  title     → Movie/show title
  year      → Release year
  type      → "movie" or "tv"
  season    → e.g. "Season 2"
  poster    → Portrait poster URL
  landscape → Wide/banner image URL
"""

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ════════════════════════════════════════════════════════════════════════════
# START MESSAGE
# ════════════════════════════════════════════════════════════════════════════

START_TEXT = """🎬 **Welcome to OTT Poster Bot!**

Hey {first_name}! 👋
I fetch **movie & TV show posters** instantly using the Spidy Poster API.

━━━━━━━━━━━━━━━━━━━━
📌 **Commands**
━━━━━━━━━━━━━━━━━━━━

🎬 `/movie Title [Year]`
   _Example:_ `/movie RRR 2022`

📺 `/tv Title [Season]`
   _Example:_ `/tv Asur 2`

🗂 `/query Filename`
   _Example:_ `/query Asur.S02.1080p.mkv`

🔍 `/search Title`
   _Example:_ `/search Mirzapur`

💡 `/help` — Full help & tips
ℹ️ `/about` — About this bot

━━━━━━━━━━━━━━━━━━━━
Or just **type any title** to quick-search! 🚀
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

ABOUT_TEXT = """ℹ️ **About OTT Poster Bot**

━━━━━━━━━━━━━━━━━━━━
🤖 **Bot:** OTT Poster Bot
🛠 **Framework:** Kurigram (Pyrogram fork)
🎨 **Poster API:** Spidy Poster API
🐍 **Language:** Python 3.12
━━━━━━━━━━━━━━━━━━━━

Fetches high-quality **movie & OTT series posters** \
with portrait and landscape images.

Supports searching by title, year, season, or even \
a raw filename like `Asur.S02.1080p.mkv`. 🎬📺
"""

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
# CAPTION BUILDER
# ════════════════════════════════════════════════════════════════════════════

def build_caption(data: dict, plot_max: int = 280) -> str:
    """
    Build a Markdown caption from Spidy API response.

    Real Spidy API fields (from live response):
      title     → str
      year      → int
      landscape → URL (wide banner image — main image returned)
    """
    title = data.get("title", "Unknown")
    year  = data.get("year", "")

    lines = []

    # ── Title + year ──
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
    """
    Build inline buttons from Spidy API response.
    No extra URLs in current API response — reserved for future use.
    """
    return None

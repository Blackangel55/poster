"""
script.py — All bot messages, captions, and command texts for OTT Poster Bot.
Edit this file to customise every message the bot sends without touching bot.py.
"""

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ════════════════════════════════════════════════════════════════════════════
# START MESSAGE
# ════════════════════════════════════════════════════════════════════════════

START_TEXT = """🎬 **Welcome to OTT Poster Bot!**

Hey {first_name}! 👋  
I fetch beautiful **movie & TV show posters** with full details — \
ratings, genres, plot and more — powered by the Spidy Poster API.

━━━━━━━━━━━━━━━━━━━━
📌 **Commands**
━━━━━━━━━━━━━━━━━━━━

🎬 `/movie Title [Year]`
   Fetch a movie poster
   _Example:_ `/movie RRR 2022`

📺 `/tv Title [Season]`
   Fetch a TV show / OTT series poster
   _Example:_ `/tv Asur 2`

🔍 `/search Title`
   Auto-detect movie or series
   _Example:_ `/search Mirzapur`

💡 `/help` — Full help & tips
ℹ️ `/about` — About this bot

━━━━━━━━━━━━━━━━━━━━
Or just **type any title** to quick-search! 🚀
"""

START_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔍 Search a Movie", switch_inline_query_current_chat=""),
        InlineKeyboardButton("📺 Search a Series", switch_inline_query_current_chat="tv "),
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
🎬 **Movie Poster**
━━━━━━━━━━━━━━━━━━━━
`/movie <Title>`
`/movie <Title> <Year>`

Examples:
• `/movie Bahubali`
• `/movie RRR 2022`
• `/movie The Dark Knight 2008`

━━━━━━━━━━━━━━━━━━━━
📺 **TV / OTT Series Poster**
━━━━━━━━━━━━━━━━━━━━
`/tv <Title>`
`/tv <Title> <Season>`

Examples:
• `/tv Mirzapur`
• `/tv Asur 2`
• `/tv Sacred Games 1`

━━━━━━━━━━━━━━━━━━━━
🔍 **Auto Search**
━━━━━━━━━━━━━━━━━━━━
`/search <Title>`
_Tries movie first, falls back to TV show._

Examples:
• `/search Pushpa`
• `/search Family Man`

━━━━━━━━━━━━━━━━━━━━
⚡ **Quick Search**
━━━━━━━━━━━━━━━━━━━━
Just **type any title** without a command!

• `KGF Chapter 2`
• `Scam 1992`

━━━━━━━━━━━━━━━━━━━━
💬 **Tips**
• Include the year for better accuracy on popular titles.
• For season-specific posters, always add the season number.
• Partial titles work too — try `KGF` instead of the full name.
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

This bot fetches high-quality movie and OTT series posters \
along with details like ratings ⭐, genres 🏷, runtime 🕐, \
and plot summaries 📝 — all in one tap.

Built for cinephiles and binge-watchers. 🎬📺
"""

ABOUT_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏠 Back to Start", callback_data="start")],
])


# ════════════════════════════════════════════════════════════════════════════
# SEARCHING / LOADING MESSAGE
# ════════════════════════════════════════════════════════════════════════════

SEARCHING_TEXT = "🔍 Searching for **{title}**…"


# ════════════════════════════════════════════════════════════════════════════
# ERROR MESSAGES
# ════════════════════════════════════════════════════════════════════════════

NOT_FOUND_TEXT = """❌ **No results found for:** `{title}`

Try:
• Check the spelling
• Add the release year: `/movie {title} 2023`
• For a series: `/tv {title}`
• Use `/search {title}` for auto-detect
"""

API_ERROR_TEXT = """⚠️ **Could not reach the poster API.**

Please try again in a moment.
If the issue persists, the API may be down temporarily.
"""

USAGE_MOVIE_TEXT = """ℹ️ **Usage:** `/movie Title [Year]`

Examples:
• `/movie Bahubali`
• `/movie RRR 2022`
"""

USAGE_TV_TEXT = """ℹ️ **Usage:** `/tv Title [Season]`

Examples:
• `/tv Mirzapur`
• `/tv Asur 2`
"""

USAGE_SEARCH_TEXT = """ℹ️ **Usage:** `/search Title`

Examples:
• `/search Pushpa`
• `/search Family Man`
"""


# ════════════════════════════════════════════════════════════════════════════
# POSTER CAPTION BUILDER
# ════════════════════════════════════════════════════════════════════════════

def build_caption(data: dict, is_season: bool = False, plot_max: int = 280) -> str:
    """
    Build a rich Markdown caption from the Spidy API response dict.
    All field names have fallbacks to cover API variations.
    """
    title   = data.get("title") or data.get("name", "Unknown")
    year    = data.get("year") or data.get("release_year", "")
    rating  = data.get("rating") or data.get("imdb_rating", "")
    genres  = data.get("genres") or data.get("genre", [])
    plot    = data.get("plot") or data.get("overview", "")
    season  = data.get("season", "")
    network = data.get("network") or data.get("platform", "")
    runtime = data.get("runtime") or data.get("episode_runtime", "")
    language = data.get("language") or data.get("original_language", "")
    country  = data.get("country") or data.get("production_country", "")

    lines = []

    # ── Title line ──
    if is_season and season:
        lines.append(f"📺 **{title}** — Season {season}")
    elif year:
        lines.append(f"🎬 **{title}** ({year})")
    else:
        lines.append(f"🎬 **{title}**")

    lines.append("━━━━━━━━━━━━━━━━━━━━")

    # ── Meta row ──
    meta = []
    if rating:
        meta.append(f"⭐ {rating}/10")
    if runtime:
        meta.append(f"🕐 {runtime} min")
    if network:
        meta.append(f"📡 {network}")
    if meta:
        lines.append("  |  ".join(meta))

    # ── Genres ──
    if genres:
        tag = genres if isinstance(genres, str) else " · ".join(genres)
        lines.append(f"🏷 {tag}")

    # ── Language / Country ──
    info = []
    if language:
        info.append(f"🌐 {language.title()}")
    if country:
        info.append(f"🗺 {country}")
    if info:
        lines.append("  |  ".join(info))

    # ── Plot ──
    if plot:
        short = (plot[:plot_max] + "…") if len(plot) > plot_max else plot
        lines.append(f"\n📝 _{short}_")

    return "\n".join(lines)


def build_keyboard(data: dict) -> InlineKeyboardMarkup | None:
    """Build inline buttons for IMDb and Trailer links if present."""
    buttons = []
    if data.get("imdb_id"):
        buttons.append(
            InlineKeyboardButton("🎞 IMDb", url=f"https://www.imdb.com/title/{data['imdb_id']}")
        )
    if data.get("trailer"):
        buttons.append(
            InlineKeyboardButton("▶️ Trailer", url=data["trailer"])
        )
    return InlineKeyboardMarkup([buttons]) if buttons else None

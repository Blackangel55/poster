# 🎬 OTT Poster Bot 

Telegram bot that fetches movie & TV show posters.

---

## Requirements

- Python 3.8+
- Telegram **API_ID** and **API_HASH** from https://my.telegram.org
- A **Bot Token** from [@BotFather](https://t.me/BotFather)
- Your **Spidy API Key**

---

## Install

```bash
pip install -r requirements.txt
```

---

## Configure

Set environment variables (recommended):

```bash
export API_ID=12345678
export API_HASH=your_api_hash_here
export BOT_TOKEN=your_bot_token_here
export SPIDY_KEY=your_spidy_key_here
```

Or edit the constants directly in `bot.py`.

---

## Run

```bash
python bot.py
```

---

## Commands

| Command | Example | Description |
|---|---|---|
| `/movie Title [Year]` | `/movie RRR 2022` | Movie poster |
| `/tv Title [Season]` | `/tv Asur 2` | TV season poster |
| `/search Title` | `/search Mirzapur` | Auto-detect |
| Just type | `KGF` | Quick search |

---

## Docker

```bash
docker build -t ott-poster-bot .
docker run -d \
  -e API_ID=12345678 \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e SPIDY_KEY=your_spidy_key \
  ott-poster-bot
```

---

## Notes

- Kurigram uses **MTProto** (not Bot API webhooks), so no webhook setup needed.
- The session file `ott_poster_bot.session` is created in the working directory on first run — keep it safe.
- Update `SPIDY_BASE` and field names in `build_caption()` if your Spidy API response keys differ.

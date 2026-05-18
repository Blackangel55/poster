# 🎬 OTT Poster Bot 

Telegram bot that fetches movie & TV show posters.

---

## Requirements

- Python 3.12+
- Telegram **API_ID** and **API_HASH** from https://my.telegram.org
- A **Bot Token** from [@BotFather](https://t.me/BotFather)
- Your **Spidy API Key** from https://poster-api.ispidy.com
- A **MongoDB** URI from https://cloud.mongodb.com (free tier works)

---

## Install

```bash
pip install -r requirements.txt
```

---

## Configure

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `API_ID` | From https://my.telegram.org |
| `API_HASH` | From https://my.telegram.org |
| `BOT_TOKEN` | From @BotFather |
| `OWNER_ID` | Your Telegram user ID (from @userinfobot) |
| `ADMIN_IDS` | Optional comma-separated admin user IDs |
| `DB_URI` | MongoDB connection string |
| `DB_NAME` | MongoDB database name |
| `SPIDY_KEY` | Your Spidy Poster API key |
| `SPIDY_BASE` | Spidy API base URL |
| `SESSION_NAME` | Path for Kurigram session file |
| `KEEP_ALIVE` | `true` to run Flask health server (required for Koyeb) |
| `PORT` | Health server port (default `8000`) |

---

## Run

```bash
python bot.py
```

---

## 👤 User Commands

| Command | Example | Description |
|---|---|---|
| `/start` | `/start` | Welcome message |
| `/help` | `/help` | Full help & tips |
| `/about` | `/about` | About this bot |
| `/movie Title [Year]` | `/movie RRR 2022` | Fetch a movie poster |
| `/tv Title [Season]` | `/tv Asur 2` | Fetch a TV season poster |
| `/query Filename` | `/query Asur.S02.1080p.mkv` | Filename parser search |
| `/search Title` | `/search Mirzapur` | Auto-detect movie or series |
| Just type a title | `KGF Chapter 2` | Quick search |

---

## 👮 Admin Commands

> Admins can be added dynamically via `/addadmin` or set statically via `ADMIN_IDS` in config.

| Command | Example | Description |
|---|---|---|
| `/stats` | `/stats` | Total users, banned count, admin count |
| `/admins` | `/admins` | List all admins |
| `/ban <user_id>` | `/ban 123456789` | Ban a user |
| `/unban <user_id>` | `/unban 123456789` | Unban a user |
| `/banned` | `/banned` | List all banned users |
| `/broadcast` | _(reply to a message)_ `/broadcast` | Send message to all users |
| `/addfsub <channel_id>` | `/addfsub -1001234567890` | Add a force subscribe channel |
| `/delfsub <channel_id>` | `/delfsub -1001234567890` | Remove a force subscribe channel |
| `/listfsub` | `/listfsub` | List all force subscribe channels |

---

## 👑 Owner-Only Commands

> Owner is set via `OWNER_ID` in config. Cannot be banned or demoted.

| Command | Example | Description |
|---|---|---|
| `/addadmin <user_id>` | `/addadmin 123456789` | Promote a user to admin |
| `/deladmin <user_id>` | `/deladmin 123456789` | Remove a user from admins |

---

## 📡 Force Subscribe Setup

1. Add the bot as **admin** in your channel with **Invite Users via Link** permission
2. Get the channel ID (forward a message to @userinfobot)
3. Run `/addfsub -1001234567890` in the bot
4. Done — users must join before using the bot

> Admins and the owner always bypass the force subscribe check.

---

## 🐳 Docker

```bash
docker build -t ott-poster-bot .
docker run -d \
  -e API_ID=12345678 \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e OWNER_ID=your_user_id \
  -e DB_URI=mongodb+srv://... \
  -e SPIDY_KEY=your_spidy_key \
  ott-poster-bot
```

Or with Docker Compose:

```bash
cp .env.example .env   # fill in values
docker compose up -d
```

---

## ☁️ Deploy on Koyeb

Key points:
- Set all env vars in Koyeb dashboard (mark secrets as **Secret**)
- Port `8000` must be exposed — health check path `/health`
- Set `KEEP_ALIVE=true`

---

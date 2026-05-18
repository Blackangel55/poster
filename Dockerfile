# ─── Build Stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# TgCrypto is a C extension — needs gcc + python headers to compile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─── Runtime Stage ───────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy bot source files
COPY bot.py config.py script.py database.py ./

# Create session directory and set permissions BEFORE switching to non-root
RUN mkdir -p /app/sessions && chmod 777 /app/sessions

# Non-root user for security
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

# ─── Environment Variables ───────────────────────────────────────────────────
ENV API_ID=""
ENV API_HASH=""
ENV BOT_TOKEN=""
ENV SPIDY_KEY=""
ENV SPIDY_BASE="https://poster-api.ispidy.com/v1/fetch"
ENV SESSION_NAME="/app/sessions/ott_poster_bot"
ENV PLOT_MAX_CHARS="280"
ENV API_TIMEOUT="15"
ENV KEEP_ALIVE="true"
ENV PORT="8000"

# Expose Flask health-check port (required by Koyeb & Render)
EXPOSE 8000

# ─── Healthcheck ─────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "bot.py"]

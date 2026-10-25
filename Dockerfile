# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000 \
    DATABASE_PATH=/data/hotel_reviews.db

WORKDIR /app

# Dependencies first so code changes don't invalidate the pip layer.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py i18n.py ./
COPY templates ./templates
COPY static ./static

# Run as an unprivileged user; /data holds the SQLite database (mount a volume here).
RUN useradd --system --uid 10001 --home /app staysignal \
    && mkdir -p /data && chown staysignal /data
USER staysignal
VOLUME ["/data"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/health', timeout=2)"

# Single worker: SQLite does not like concurrent writers. Trust X-Forwarded-* from the reverse proxy for https URLs.
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]

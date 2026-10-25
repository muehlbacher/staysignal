# StaySignal — Hotel Review & Feedback MVP

A deployable MVP for a hotel QR feedback flow. Guests submit a private 1–5 rating and optional comments; **all guests see the same optional Google review link after submitting**, regardless of their rating. This avoids review gating.

## Features
- Mobile-first, two-step guest flow at `/r/<slug>` (optional `?table=12`): one tap on 1–5 stars, then a follow-up that depends on the rating: "What went wrong?" at 1–2★, "What would have made it a 5?" at 3★, "What stood out?" at 4–5★
- Tap-to-pick tags, optional comment, "contact me" request at 1–2★ (details deleted when marked resolved), "thank the team" at 4–5★
- English and German (`?lang=de`, or auto from the browser); same Google review offer at every rating
- Per-table QR codes; set `TIMEZONE` (default `Europe/Vienna`) for the "Tonight, 20:14" header
- Admin login and dashboard with total feedback, average rating and rating distribution
- Hotel name, public URL slug, welcome message and Google review link settings
- Downloadable QR code PNG and CSV export
- SQLite storage and health endpoint

## Run locally
Requires Python 3.9+. Built on FastAPI + Uvicorn.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="use-a-long-unique-password"
uvicorn app:app --reload --port 5000
```

Open `http://127.0.0.1:5000`. Admin: `/login`; public guest page: `/r/alpine-haven`.

On first run, the initial settings are created. The initial password is hashed. To change the hotel and add its actual Google review URL, log in and open **Settings**.

## Deploy with Docker
```bash
cp .env.example .env        # fill in SECRET_KEY and ADMIN_PASSWORD
docker compose up -d --build
```
The app listens on port 8000 (`HOST_PORT` in `.env` to change). The SQLite database lives in the `staysignal-data` volume at `/data`, so it survives rebuilds and restarts. Compose refuses to start without `SECRET_KEY` and `ADMIN_PASSWORD`; `ADMIN_PASSWORD` only seeds the very first start; change it later in **Settings**.

Put it behind a reverse proxy that terminates HTTPS (Caddy, Traefik, nginx); the container trusts `X-Forwarded-Proto`, so QR codes and links use `https://`. It runs a single worker on purpose, because SQLite handles one writer at a time.

Backup: `docker compose cp web:/data/hotel_reviews.db ./backup.db`

Without compose:
```bash
docker build -t staysignal .
docker run -d -p 8000:8000 -v staysignal-data:/data \
  -e SECRET_KEY=... -e ADMIN_PASSWORD=... staysignal
```

## Deploy without Docker
For a quick pilot, deploy to a Python host that supports persistent disks/volumes:
- Build/install: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT --proxy-headers` (see `Procfile`)
- Set environment variables: `SECRET_KEY` (long random secret), `ADMIN_USERNAME`, `ADMIN_PASSWORD`
- Mount persistent storage and set `DATABASE_PATH` to a path on that volume.

Important: SQLite data is lost on ephemeral filesystems when a host restarts or redeploys. Use a persistent disk for pilots, or migrate to managed PostgreSQL before production/multi-hotel use.

## Before production
This is a pilot MVP, not a finished multi-tenant SaaS. Add per-hotel accounts and role-based access, CSRF protection, rate limiting/bot controls, audit logging, database migrations, automated backups, monitoring, data retention/deletion controls, privacy notice and GDPR processing agreements. Use HTTPS in production. Never ask guests to include sensitive personal data in comments.

## Google review policy
Google prohibits discouraging negative reviews or selectively soliciting positive reviews. This MVP deliberately displays the same Google review link after every submitted rating. See:
https://support.google.com/contributionpolicy/answer/7400114

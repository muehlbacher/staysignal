import os, io, csv, sqlite3, secrets, hashlib, hmac, logging
from datetime import datetime, timezone
from typing import List
from zoneinfo import ZoneInfo
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import qrcode
from i18n import I18N, TAGS, band, pick_lang

APP_SECRET = os.environ.get("SECRET_KEY", "dev-only-change-me")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
DATABASE = os.environ.get("DATABASE_PATH", "hotel_reviews.db")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_TZ = ZoneInfo(os.environ.get("TIMEZONE", "Europe/Vienna"))
# Cache-busts static assets whenever any of them changes.
ASSET_VERSION = str(int(max(os.path.getmtime(os.path.join(BASE_DIR, "static", f)) for f in os.listdir(os.path.join(BASE_DIR, "static")))))

log = logging.getLogger("staysignal")
if APP_SECRET == "dev-only-change-me" or ADMIN_PASSWORD == "admin":
    log.warning("SECRET_KEY or ADMIN_PASSWORD is using the insecure dev default. Set them before deploying.")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET, same_site="lax")
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Passwords use werkzeug's "pbkdf2:sha256:<iterations>$<salt>$<hex>" format so existing hashes keep working.
def generate_password_hash(password, iterations=1_000_000):
    salt = secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()
    return f"pbkdf2:sha256:{iterations}${salt}${digest}"

def check_password_hash(pwhash, password):
    try:
        method, salt, expected = pwhash.split("$", 2)
        kind, hash_name, iterations = method.split(":")
        if kind != "pbkdf2":
            return False
        digest = hashlib.pbkdf2_hmac(hash_name, password.encode(), salt.encode(), int(iterations)).hex()
    except ValueError:
        return False
    return hmac.compare_digest(digest, expected)

def flash(request, message, category="message"):
    request.session.setdefault("_flashes", []).append([category, message])

def inject_globals(request):
    def get_flashed_messages(with_categories=False):
        messages = request.session.pop("_flashes", [])
        return messages if with_categories else [m for _, m in messages]
    return {"current_year": datetime.now().year, "session": request.session, "asset_v": ASSET_VERSION,
            "get_flashed_messages": get_flashed_messages}

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"), context_processors=[inject_globals])

def render(request, name, **context):
    return templates.TemplateResponse(request, name, context)

def redirect(url):
    return RedirectResponse(str(url), status_code=303)

def db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            hotel_name TEXT NOT NULL,
            slug TEXT NOT NULL,
            google_review_url TEXT NOT NULL,
            welcome_text TEXT NOT NULL,
            admin_password_hash TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            category TEXT NOT NULL DEFAULT '',
            message TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'qr'
        )""")
        # Lightweight migration for the rating-dependent guest flow.
        existing = {r["name"] for r in con.execute("PRAGMA table_info(feedback)")}
        for column, ddl in [("tags", "TEXT NOT NULL DEFAULT ''"), ("contact_requested", "INTEGER NOT NULL DEFAULT 0"),
                            ("contact", "TEXT NOT NULL DEFAULT ''"), ("thank_team", "INTEGER NOT NULL DEFAULT 0"),
                            ("table_no", "TEXT NOT NULL DEFAULT ''"), ("lang", "TEXT NOT NULL DEFAULT 'en'")]:
            if column not in existing:
                con.execute(f"ALTER TABLE feedback ADD COLUMN {column} {ddl}")
        row = con.execute("SELECT id FROM settings WHERE id=1").fetchone()
        if not row:
            con.execute("""INSERT INTO settings
                (id, hotel_name, slug, google_review_url, welcome_text, admin_password_hash)
                VALUES (1, ?, ?, ?, ?, ?)""",
                ("Alpine Haven Wellness Hotel", "alpine-haven",
                 "https://www.google.com/search?q=Google+review+link+replace+this",
                 "Thank you for staying with us. Your feedback helps us improve.",
                 generate_password_hash(ADMIN_PASSWORD)))

def get_settings():
    with db() as con:
        return con.execute("SELECT * FROM settings WHERE id=1").fetchone()

class LoginRequired(Exception):
    pass

@app.exception_handler(LoginRequired)
def login_redirect(request: Request, exc: LoginRequired):
    return RedirectResponse(str(request.url_for("login").include_query_params(next=request.url.path)), status_code=303)

def require_login(request: Request):
    if not request.session.get("logged_in"):
        raise LoginRequired()

@app.get("/")
def home(request: Request):
    return render(request, "home.html", hotel=get_settings())

def clean_table(value):
    return "".join(c for c in value if c.isalnum() or c == "-")[:10]

def guest_settings(slug):
    settings = get_settings()
    if slug != settings["slug"]:
        raise HTTPException(404)
    return settings

def review_url(request, slug, table=""):
    url = request.url_for("review", slug=slug)
    return url.include_query_params(table=table) if table else url

@app.get("/r/{slug}")
def review(request: Request, slug: str, table: str = ""):
    settings = guest_settings(slug)
    lang = pick_lang(request)
    t = I18N[lang]
    now = datetime.now(LOCAL_TZ)
    evening = now.hour >= 17
    return render(request, "review.html", hotel=settings, t=t, lang=lang, tags=TAGS, table=clean_table(table),
                  when=t["tonight"] if evening else t["today"], question=t["q_tonight"] if evening else t["q_today"],
                  time=now.strftime("%H:%M"))

@app.post("/r/{slug}")
def review_submit(request: Request, slug: str, rating: str = Form("0"), tags: List[str] = Form([]),
                  message: str = Form(""), contact_requested: str = Form(""), contact_name: str = Form(""),
                  contact_info: str = Form(""), thank_team: str = Form(""), table: str = Form("")):
    guest_settings(slug)
    lang = pick_lang(request)
    table = clean_table(table)
    try:
        rating = int(rating)
    except ValueError:
        rating = 0
    if rating not in range(1, 6):
        flash(request, I18N[lang]["rate_first"], "error")
        return redirect(review_url(request, slug, table))
    # Only keep what belongs to this rating's step: tags from its band, contact at 1–2★, team thanks at 4–5★.
    allowed = TAGS[band(rating)]
    picked = ",".join(tag for tag in allowed if tag in tags)
    contact_info = contact_info.strip()[:120]
    wants_contact = rating <= 2 and bool(contact_requested) and bool(contact_info)
    contact = " · ".join(p for p in (contact_name.strip()[:80], contact_info) if p) if wants_contact else ""
    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with db() as con:
        cur = con.execute("""INSERT INTO feedback (rating, tags, message, contact_requested, contact, thank_team,
                             table_no, lang, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          (rating, picked, message.strip()[:2000], int(wants_contact), contact,
                           int(rating >= 4 and bool(thank_team)), table, lang, created))
    request.session["last_feedback"] = cur.lastrowid
    return redirect(request.url_for("thanks", slug=slug))

@app.get("/r/{slug}/thanks")
def thanks(request: Request, slug: str):
    settings = guest_settings(slug)
    with db() as con:
        row = con.execute("SELECT * FROM feedback WHERE id=?", (request.session.get("last_feedback", 0),)).fetchone()
    if not row:
        return redirect(request.url_for("review", slug=slug))
    lang = pick_lang(request)
    # Policy-safe: every guest receives the same optional Google review link, regardless of rating.
    return render(request, "thanks.html", hotel=settings, t=I18N[lang], lang=lang, row=row,
                  band=band(row["rating"]), back_url=review_url(request, slug, row["table_no"]))

@app.get("/login")
def login(request: Request):
    return render(request, "login.html")

@app.post("/login")
def login_submit(request: Request, username: str = Form(""), password: str = Form(""), next: str = ""):
    settings = get_settings()
    if hmac.compare_digest(username, ADMIN_USERNAME) and check_password_hash(settings["admin_password_hash"], password):
        request.session.clear()
        request.session["logged_in"] = True
        # Only follow local paths to avoid open redirects.
        if next.startswith("/") and not next.startswith("//"):
            return redirect(next)
        return redirect(request.url_for("dashboard"))
    flash(request, "Incorrect username or password.", "error")
    return render(request, "login.html")

@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return redirect(request.url_for("login"))

@app.get("/admin", dependencies=[Depends(require_login)])
def dashboard(request: Request):
    settings = get_settings()
    today = datetime.now(timezone.utc).date().isoformat()
    with db() as con:
        rows = con.execute("SELECT * FROM feedback ORDER BY created_at DESC LIMIT 100").fetchall()
        stats = con.execute("SELECT COUNT(*) AS total, AVG(rating) AS avg, SUM(created_at >= ?) AS today FROM feedback", (today,)).fetchone()
        counts = dict(con.execute("SELECT rating, COUNT(*) FROM feedback GROUP BY rating").fetchall())
    distribution = {i: counts.get(i, 0) for i in range(1, 6)}
    avg = stats["avg"]
    return render(request, "dashboard.html", hotel=settings, rows=rows, total=stats["total"],
                  avg=round(avg, 1) if avg else 0, distribution=distribution, today=stats["today"] or 0,
                  tag_labels=I18N["en"]["tags"])

@app.post("/admin/feedback/{feedback_id}/resolve", dependencies=[Depends(require_login)])
def resolve_contact(request: Request, feedback_id: int):
    # Contact details are only kept until the manager has followed up.
    with db() as con:
        con.execute("UPDATE feedback SET contact='', contact_requested=0 WHERE id=?", (feedback_id,))
    flash(request, "Contact request resolved and details deleted.", "success")
    return redirect(request.url_for("dashboard"))

@app.get("/admin/settings", dependencies=[Depends(require_login)])
def settings_page(request: Request):
    return render(request, "settings.html", hotel=get_settings())

@app.post("/admin/settings", dependencies=[Depends(require_login)])
def settings_save(request: Request, hotel_name: str = Form(""), slug: str = Form(""), google_review_url: str = Form(""),
                  welcome_text: str = Form(""), new_password: str = Form("")):
    name = hotel_name.strip()[:120]
    slug = slug.strip().lower()
    google_url = google_review_url.strip()
    welcome = welcome_text.strip()[:500]
    back = request.url_for("settings_page")
    if not name or not slug or not all(c.isalnum() or c == "-" for c in slug):
        flash(request, "Enter a hotel name and a URL slug using letters, numbers or hyphens.", "error")
        return redirect(back)
    if not google_url.startswith("https://"):
        flash(request, "Google review URL must start with https://.", "error")
        return redirect(back)
    if new_password and len(new_password) < 12:
        flash(request, "New admin password must be at least 12 characters.", "error")
        return redirect(back)
    with db() as con:
        if new_password:
            con.execute("UPDATE settings SET hotel_name=?, slug=?, google_review_url=?, welcome_text=?, admin_password_hash=? WHERE id=1",
                        (name, slug, google_url, welcome, generate_password_hash(new_password)))
        else:
            con.execute("UPDATE settings SET hotel_name=?, slug=?, google_review_url=?, welcome_text=? WHERE id=1",
                        (name, slug, google_url, welcome))
    flash(request, "Settings saved.", "success")
    return redirect(back)

@app.get("/admin/qr.png", dependencies=[Depends(require_login)])
def qr_code(request: Request, table: str = "", download: str = ""):
    settings = get_settings()
    table = clean_table(table)
    target = str(review_url(request, settings["slug"], table))
    qr = qrcode.QRCode(box_size=10, border=3)
    qr.add_data(target)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#173b35", back_color="white")
    out = io.BytesIO()
    image.save(out, format="PNG")
    filename = f'{settings["slug"]}{"-table-" + table if table else ""}-qr.png'
    disposition = "attachment" if download else "inline"
    return Response(out.getvalue(), media_type="image/png",
                    headers={"Content-Disposition": f'{disposition}; filename="{filename}"'})

@app.get("/admin/export.csv", dependencies=[Depends(require_login)])
def export_csv():
    with db() as con:
        rows = con.execute("""SELECT rating, category, tags, message, table_no, contact_requested, contact, thank_team,
                              lang, created_at, source FROM feedback ORDER BY created_at DESC""").fetchall()
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["rating", "category", "tags", "message", "table", "contact_requested", "contact", "thank_team",
                     "lang", "created_at_utc", "source"])
    writer.writerows([tuple(row) for row in rows])
    return Response(out.getvalue().encode("utf-8-sig"), media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="hotel-feedback.csv"'})

@app.get("/health")
def health():
    return {"status": "ok"}

init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), reload=os.environ.get("DEBUG") == "1")

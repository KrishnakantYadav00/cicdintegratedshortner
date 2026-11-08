import os
import re
import string
import random
from datetime import datetime, timezone

from flask import Flask, request, redirect, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# Determine database URI:
# 1. Check DATABASE_URL environment variable
# 2. Check if /data directory exists (Docker volume mount) -> sqlite:////data/urls.db
# 3. Fallback to local SQLite file -> sqlite:///urls.db
raw_db_url = os.environ.get("DATABASE_URL")
if raw_db_url:
    # Heroku/Render/Supabase compatibility: convert postgres:// to postgresql://
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    db_url = raw_db_url
elif os.path.isdir("/data"):
    db_url = "sqlite:////data/urls.db"
else:
    db_url = "sqlite:///urls.db"

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
URL_REGEX = re.compile(
    r"^(https?://)"  # require explicit scheme
    r"([\w-]+\.)+[\w-]{2,}"  # domain
    r"(/.*)?$",
    re.IGNORECASE,
)


class ShortURL(db.Model):
    __tablename__ = "short_urls"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True, nullable=False, index=True)
    target_url = db.Column(db.String(2048), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    click_count = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "code": self.code,
            "target_url": self.target_url,
            "created_at": self.created_at.isoformat(),
            "click_count": self.click_count,
            "short_url": request.host_url + self.code,
        }


def generate_code(length: int = CODE_LENGTH) -> str:
    return "".join(random.choices(ALPHABET, k=length))


def is_valid_url(url: str) -> bool:
    if not url or len(url) > 2048:
        return False
    return bool(URL_REGEX.match(url))


@app.route("/health")
def health():
    """Used by CI/CD readiness & liveness probes.

    Verifies both web server liveness and database connectivity.
    """
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(
            status="ok",
            database="connected",
            db_engine=db.engine.name,
            timestamp=datetime.now(timezone.utc).isoformat()
        ), 200
    except Exception as exc:
        return jsonify(
            status="unhealthy",
            database="disconnected",
            error=str(exc)
        ), 503


@app.route("/api/shorten", methods=["POST"])
def shorten():
    payload = request.get_json(silent=True) or {}
    target_url = payload.get("url", "").strip()
    custom_code = (payload.get("custom_code") or "").strip()

    if not is_valid_url(target_url):
        return jsonify(error="Invalid or missing 'url'"), 400

    if custom_code:
        if not re.match(r"^[a-zA-Z0-9_-]{3,16}$", custom_code):
            return jsonify(error="custom_code must be 3-16 alphanumeric/_/- chars"), 400
        if ShortURL.query.filter_by(code=custom_code).first():
            return jsonify(error="custom_code already taken"), 409
        code = custom_code
    else:
        code = generate_code()
        attempts = 0
        while ShortURL.query.filter_by(code=code).first():
            code = generate_code()
            attempts += 1
            if attempts > 5:
                return jsonify(error="Could not generate a unique code, try again"), 500

    entry = ShortURL(code=code, target_url=target_url)
    db.session.add(entry)
    db.session.commit()

    return jsonify(entry.to_dict()), 201


@app.route("/<code>")
def resolve(code):
    entry = ShortURL.query.filter_by(code=code).first()
    if not entry:
        return jsonify(error="Short URL not found"), 404

    entry.click_count += 1
    db.session.commit()
    return redirect(entry.target_url, code=302)


@app.route("/api/stats/<code>")
def stats(code):
    entry = ShortURL.query.filter_by(code=code).first()
    if not entry:
        return jsonify(error="Short URL not found"), 404
    return jsonify(entry.to_dict()), 200


@app.route("/")
def index():
    return render_template("index.html")


def create_tables():
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    create_tables()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

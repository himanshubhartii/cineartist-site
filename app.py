import os
import sqlite3
from datetime import datetime
import io
import csv

from flask import (
    Flask,
    render_template,
    request,
    abort,
    session,
    redirect,
    url_for,
    Response,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)

# -------------------------
# SECRET KEY (for login)
# -------------------------
app.secret_key = "cineartist-secret-key"

# -------------------------
# ADMIN LOGIN CREDENTIALS
# -------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "cineartist123"

# -------------------------
# FILE UPLOAD SETTINGS
# -------------------------
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "stories")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


def allowed_file(filename: str) -> bool:
    """Check file extension"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------
# DATABASE (SQLite)
# -------------------------
DB_PATH = os.path.join(BASE_DIR, "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Story uploads (user submitted scripts)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS story_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uploaded_at TEXT NOT NULL,
            name TEXT,
            email TEXT,
            title TEXT,
            filename TEXT
        )
        """
    )

    # Contact messages
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            name TEXT,
            email TEXT,
            message TEXT
        )
        """
    )

    # Casting applications
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS casting_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            name TEXT,
            age TEXT,
            city TEXT,
            experience TEXT,
            profile_link TEXT
        )
        """
    )

    conn.commit()
    conn.close()


# Call once at startup
init_db()


# -------------------------
# STORIES DATABASE (STATIC)
# -------------------------
STORIES = [
    {
        "slug": "papa-beta-aur-ek-sapna",
        "title": "Papa, Beta aur Ek Sapna",
        "short": "A father silently sacrificing his dreams so his son can chase his own.",
        "full": [
            "A middle-class father works extra hours so his son can study in a better school.",
            "One day, the son discovers his father’s old sketchbook and realises how much he sacrificed.",
            "Their emotional conversation shows how fear and expectations shape our dreams."
        ],
        "tags": ["Family", "Emotional", "Drama"],
    },
    {
        "slug": "deadline",
        "title": "Deadline",
        "short": "A young professional stuck between office targets and mental peace.",
        "full": [
            "A new office employee keeps chasing deadlines and forgetting himself.",
            "One missed call changes everything and forces him to rethink life.",
            "A story about burnout, pressure and rediscovering balance."
        ],
        "tags": ["Corporate", "Mental Health"],
    },
    {
        "slug": "last-bench",
        "title": "Last Bench",
        "short": "School memories and friendships we lose touch with.",
        "full": [
            "A school reunion triggers memories of old friends and moments.",
            "Old photos make him question why people drift apart.",
            "He finally sends a message that he kept unsent for years."
        ],
        "tags": ["Friendship", "Nostalgia"],
    },
    {
        "slug": "parallel-festival",
        "title": "Parallel Festival",
        "short": "What if festivals were celebrated differently in another world?",
        "full": [
            "Two parallel versions of a family celebrate the same festival.",
            "One rich, one struggling — but love decides happiness, not money."
        ],
        "tags": ["Fantasy", "Emotion"],
    },
    {
        "slug": "unsent-messages",
        "title": "Unsent Messages",
        "short": "The things we type but never send.",
        "full": [
            "A character writes emotional messages but never sends them.",
            "One night all drafts get sent accidentally — chaos begins."
        ],
        "tags": ["Drama", "Relationships"],
    },
    {
        "slug": "invisible-hero",
        "title": "Invisible Hero",
        "short": "The unnoticed person in every family who keeps it together.",
        "full": [
            "Every family has someone who sacrifices without saying a word.",
            "A story told through the eyes of each family member."
        ],
        "tags": ["Family", "Slice of Life"],
    },
]


# ==========================================================
# BASIC ROUTES
# ==========================================================

@app.route("/")
def home():
    latest_film = {
        "title": "Lamhey",
        "url": "https://www.youtube.com/watch?v=H0Oi7bGxHS4",
        "thumb": "https://img.youtube.com/vi/H0Oi7bGxHS4/maxresdefault.jpg",
    }
    return render_template("index.html", latest_film=latest_film)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/films")
def films():
    return render_template("films.html")


# ==========================================================
# STORIES PAGE (LIST + UPLOAD)
# ==========================================================

@app.route("/stories", methods=["GET", "POST"])
def stories():
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        title = request.form.get("title", "")
        file = request.files.get("file")

        msg = None

        if not file:
            msg = "Please attach a PDF or DOCX file."
        elif not allowed_file(file.filename):
            msg = "Only PDF, DOC, or DOCX files are allowed."
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = secure_filename(file.filename)
            filename = f"{timestamp}_{safe_name}"
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            # Save in DB
            conn = get_db()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO story_uploads (uploaded_at, name, email, title, filename)
                VALUES (?, ?, ?, ?, ?)
                """,
                (datetime.now().isoformat(), name, email, title, filename),
            )
            conn.commit()
            conn.close()

            msg = "Thank you! Your story has been uploaded."

        return render_template(
            "stories.html",
            stories=STORIES,
            upload_message=msg
        )

    return render_template(
        "stories.html",
        stories=STORIES,
        upload_message=None
    )


# ==========================================================
# SINGLE STORY DETAIL PAGE
# ==========================================================

@app.route("/stories/<slug>")
def story_detail(slug):
    story = next((s for s in STORIES if s["slug"] == slug), None)
    if not story:
        abort(404)
    return render_template("story_detail.html", story=story)


# ==========================================================
# CASTING FORM
# ==========================================================

@app.route("/casting", methods=["GET", "POST"])
def casting():
    if request.method == "POST":
        name = request.form.get("name", "")
        age = request.form.get("age", "")
        city = request.form.get("city", "")
        experience = request.form.get("experience", "")
        profile_link = request.form.get("profile_link", "")

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO casting_submissions (
                created_at, name, age, city, experience, profile_link
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), name, age, city, experience, profile_link),
        )
        conn.commit()
        conn.close()

        return render_template(
            "success.html",
            title="Casting Application Received",
            message="Thank you! Your casting application has been received.",
        )

    return render_template("casting.html")


# ==========================================================
# CONTACT FORM
# ==========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        message_text = request.form.get("message", "")

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO contact_messages (created_at, name, email, message)
            VALUES (?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), name, email, message_text),
        )
        conn.commit()
        conn.close()

        return render_template(
            "success.html",
            title="Message Sent",
            message="Thank you! Your message has been received.",
        )

    return render_template("contact.html")


# ==========================================================
# ADMIN LOGIN
# ==========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/dashboard")
        else:
            return render_template("admin_login.html", error="Invalid credentials")

    return render_template("admin_login.html", error=None)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin/login")


# ==========================================================
# ADMIN DASHBOARD
# ==========================================================

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db()
    cur = conn.cursor()

    # Story uploads
    cur.execute(
        """
        SELECT uploaded_at, name, email, title, filename
        FROM story_uploads
        ORDER BY uploaded_at DESC
        """
    )
    story_rows = cur.fetchall()

    # Contact messages
    cur.execute(
        """
        SELECT created_at, name, email, message
        FROM contact_messages
        ORDER BY created_at DESC
        """
    )
    contact_rows = cur.fetchall()

    # Casting submissions
    cur.execute(
        """
        SELECT created_at, name, age, city, experience, profile_link
        FROM casting_submissions
        ORDER BY created_at DESC
        """
    )
    casting_rows = cur.fetchall()

    conn.close()

    # Convert to list-of-lists (first row header, rest data) for template
    story_data = []
    if story_rows:
        story_data.append(
            ["Uploaded At", "Name", "Email", "Title", "Filename"]
        )
        for r in story_rows:
            try:
                dt = datetime.fromisoformat(r["uploaded_at"])
                nice_dt = dt.strftime("%d %b %Y, %I:%M %p")
            except Exception:
                nice_dt = r["uploaded_at"]

            story_data.append(
                [nice_dt, r["name"], r["email"], r["title"], r["filename"]]
            )

    contact_data = []
    if contact_rows:
        contact_data.append(
            ["Sent At", "Name", "Email", "Message"]
        )
        for r in contact_rows:
            try:
                dt = datetime.fromisoformat(r["created_at"])
                nice_dt = dt.strftime("%d %b %Y, %I:%M %p")
            except Exception:
                nice_dt = r["created_at"]

            contact_data.append(
                [nice_dt, r["name"], r["email"], r["message"]]
            )

    casting_data = []
    if casting_rows:
        casting_data.append(
            ["Submitted At", "Name", "Age", "City", "Experience", "Profile Link"]
        )
        for r in casting_rows:
            try:
                dt = datetime.fromisoformat(r["created_at"])
                nice_dt = dt.strftime("%d %b %Y, %I:%M %p")
            except Exception:
                nice_dt = r["created_at"]

            casting_data.append(
                [nice_dt, r["name"], r["age"], r["city"], r["experience"], r["profile_link"]]
            )

    return render_template(
        "admin_dashboard.html",
        casting_data=casting_data,
        contact_data=contact_data,
        story_data=story_data,
    )


# ==========================================================
# ADMIN CSV DOWNLOAD (FROM DB)
# ==========================================================

@app.route("/admin/download/<kind>")
def admin_download(kind):
    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db()
    cur = conn.cursor()

    if kind == "stories":
        cur.execute(
            """
            SELECT uploaded_at, name, email, title, filename
            FROM story_uploads
            ORDER BY uploaded_at DESC
            """
        )
        rows = cur.fetchall()
        header = ["Uploaded At", "Name", "Email", "Title", "Filename"]
        filename = "story_uploads.csv"

    elif kind == "contact":
        cur.execute(
            """
            SELECT created_at, name, email, message
            FROM contact_messages
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
        header = ["Sent At", "Name", "Email", "Message"]
        filename = "contact_messages.csv"

    elif kind == "casting":
        cur.execute(
            """
            SELECT created_at, name, age, city, experience, profile_link
            FROM casting_submissions
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
        header = ["Submitted At", "Name", "Age", "City", "Experience", "Profile Link"]
        filename = "casting_submissions.csv"

    else:
        conn.close()
        return "Unknown data type", 400

    # Generate CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    for r in rows:
        writer.writerow(list(r))

    conn.close()

    csv_data = output.getvalue()
    output.close()

    resp = Response(csv_data, mimetype="text/csv")
    resp.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return resp


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)

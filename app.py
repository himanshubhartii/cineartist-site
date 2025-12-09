import os
import csv
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    abort,
    session,
    redirect,
    url_for,
    send_file,
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
ADMIN_PASSWORD = "Himanshu@cine123"

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
# SAVE ROW TO CSV
# -------------------------
def append_to_csv(filename, header_row, data_row):
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(header_row)

        writer.writerow(data_row)


# -------------------------
# STORIES DATABASE
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

            append_to_csv(
                "story_submissions.csv",
                ["Uploaded At", "Name", "Email", "Title", "Filename"],
                [datetime.now().isoformat(), name, email, title, filename],
            )

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

        append_to_csv(
            "casting_data.csv",
            ["Name", "Age", "City", "Experience", "Profile Link"],
            [name, age, city, experience, profile_link],
        )

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
        message = request.form.get("message", "")

        append_to_csv(
            "contact_data.csv",
            ["Name", "Email", "Message"],
            [name, email, message],
        )

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

    def safe_read(path):
        if os.path.exists(path):
            with open(path, newline="", encoding="utf-8") as f:
                return list(csv.reader(f))
        return []

    casting_data = safe_read("casting_data.csv")
    contact_data = safe_read("contact_data.csv")
    story_data = safe_read("story_submissions.csv")

    # human readable date for story_data
    if story_data:
        header = story_data[0]
        rows = []
        for r in story_data[1:]:
            try:
                dt = datetime.fromisoformat(r[0])
                r[0] = dt.strftime("%d %b %Y, %I:%M %p")
            except Exception:
                pass
            rows.append(r)
        story_data = [header] + rows

    return render_template(
        "admin_dashboard.html",
        casting_data=casting_data,
        contact_data=contact_data,
        story_data=story_data,
    )


# ==========================================================
# ADMIN CSV DOWNLOAD
# ==========================================================

@app.route("/admin/download/<kind>")
def admin_download(kind):
    if not session.get("admin"):
        return redirect("/admin/login")

    mapping = {
        "stories": "story_submissions.csv",
        "contact": "contact_data.csv",
        "casting": "casting_data.csv",
    }

    filename = mapping.get(kind)
    if not filename or not os.path.exists(filename):
        return "No data file found.", 404

    return send_file(filename, as_attachment=True)


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)


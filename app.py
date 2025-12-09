import os
import csv
from datetime import datetime

from flask import Flask, render_template, request, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------- FILE UPLOAD SETTINGS (for stories) ----------
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "stories")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- Helper: Save to CSV ----------
def append_to_csv(filename, header_row, data_row):
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(header_row)

        writer.writerow(data_row)


# ---------- STATIC STORY DATA ----------
STORIES = [
    {
        "slug": "papa-beta-aur-ek-sapna",
        "title": "Papa, Beta aur Ek Sapna",
        "short": "A father silently sacrificing his dreams so his son can chase his own.",
        "full": [
            "A middle-class father works extra hours so his son can study in a better school. "
            "He never talks about his own unfulfilled dreams of becoming an artist.",

            "One day, the son discovers his father’s old sketchbook and realises that the life "
            "he is living today is built on the dreams his father quietly gave up.",

            "The story follows their emotional conversation where, for the first time, both of them "
            "talk openly about fear, dreams and expectations."
        ],
    },
    {
        "slug": "deadline",
        "title": "Deadline",
        "short": "A young professional stuck between office targets and mental peace.",
        "full": [
            "A first-job employee keeps chasing deadlines, ignoring his friends, health and family.",
            "When one missed call changes everything, he starts questioning what ‘success’ really means.",
            "The story explores burnout, expectations and the cost of ignoring yourself."
        ],
    },
    {
        "slug": "last-bench",
        "title": "Last Bench",
        "short": "School memories, friendships and the people we lose touch with.",
        "full": [
            "A reunion party makes an introvert remember his school days — and the last-bench friends "
            "who gave him confidence.",
            "As he scrolls through old photos and chat archives, he realises how quietly people drift apart.",
            "The story is about one message he finally decides to send after years of silence."
        ],
    },
    {
        "slug": "parallel-festival",
        "title": "Parallel Festival",
        "short": "What if festivals were celebrated in a completely different world?",
        "full": [
            "Two parallel versions of the same family celebrate the same festival — one with money, one without.",
            "The story cuts between both worlds to show how love, not budget, decides the warmth of a festival."
        ],
    },
    {
        "slug": "unsent-messages",
        "title": "Unsent Messages",
        "short": "All the things we type on our phone… and never press send.",
        "full": [
            "A character writes long heartfelt messages to people but always saves them in drafts.",
            "One night, by mistake, all drafts get sent — and honest chaos begins.",
        ],
    },
    {
        "slug": "invisible-hero",
        "title": "Invisible Hero",
        "short": "The unnoticed person in every family who quietly keeps everyone together.",
        "full": [
            "Every family has someone who wakes up first and sleeps last.",
            "This story shows that ‘hero’ from the point of view of each family member.",
        ],
    },
]


# ---------- Routes ----------
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


# ---------- STORIES (LIST + UPLOAD) ----------
@app.route("/stories", methods=["GET", "POST"])
def stories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        title = request.form.get("title", "").strip()
        file = request.files.get("file")

        msg = None

        if not file or file.filename == "":
            msg = "Please attach a PDF or DOCX file."
        elif not allowed_file(file.filename):
            msg = "Only PDF, DOC and DOCX files are allowed."
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = secure_filename(file.filename)
            filename = f"{timestamp}_{safe_name}"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            append_to_csv(
                "story_submissions.csv",
                ["Uploaded At", "Name", "Email", "Title", "Filename"],
                [datetime.now().isoformat(), name, email, title, filename],
            )

            msg = "Thank you! Your story has been uploaded."

        return render_template("stories.html", stories=STORIES, upload_message=msg)

    # GET
    return render_template("stories.html", stories=STORIES, upload_message=None)


# ---------- SINGLE STORY DETAIL ----------
@app.route("/stories/<slug>")
def story_detail(slug):
    story = next((s for s in STORIES if s["slug"] == slug), None)
    if not story:
        abort(404)
    return render_template("story_detail.html", story=story)


# ---------- CASTING ----------
@app.route("/casting", methods=["GET", "POST"])
def casting():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        city = request.form.get("city", "").strip()
        experience = request.form.get("experience", "").strip()
        profile_link = request.form.get("profile_link", "").strip()

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


# ---------- CONTACT ----------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

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


# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True)

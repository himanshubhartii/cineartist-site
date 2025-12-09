import os
import csv
from datetime import datetime

from flask import Flask, render_template, request
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


# ---------- Routes ----------
@app.route("/")
def home():
    # yahan future me tum latest film change kar sakte ho
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


# ---------- STORIES (WITH FILE UPLOAD) ----------
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
            # safe filename + timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = secure_filename(file.filename)
            filename = f"{timestamp}_{safe_name}"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            # CSV me entry save karo
            append_to_csv(
                "story_submissions.csv",
                ["Uploaded At", "Name", "Email", "Title", "Filename"],
                [datetime.now().isoformat(), name, email, title, filename],
            )

            msg = "Thank you! Your story has been uploaded."

        return render_template("stories.html", upload_message=msg)

    # GET request
    return render_template("stories.html", upload_message=None)


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

import os, uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import qrcode
from PIL import Image

app = Flask(__name__)
app.secret_key = "bridge2026secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bridge.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["QR_FOLDER"] = "static/qrcodes"
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}

db = SQLAlchemy(app)

# ── Models ────────────────────────────────────────────────────────────────────

class Attendee(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(120), nullable=False)
    linkedin = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(30),  nullable=False)  # masterclass | vip | participant
    photo    = db.Column(db.String(200), nullable=True)
    qr_code  = db.Column(db.String(200), nullable=True)

class Masterclass(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    speaker     = db.Column(db.String(120), nullable=False)
    time_slot   = db.Column(db.String(60),  nullable=False)
    room        = db.Column(db.String(60),  nullable=False)
    description = db.Column(db.Text,        nullable=False)
    takeaway    = db.Column(db.String(300), nullable=True)
    video_url   = db.Column(db.String(300), nullable=True)  # YouTube embed

# ── Helpers ───────────────────────────────────────────────────────────────────

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

def generate_qr(linkedin_url, filename_stem):
    qr = qrcode.QRCode(version=1, box_size=8, border=2,
                        error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(linkedin_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0A2540", back_color="white")
    path = os.path.join(app.config["QR_FOLDER"], f"{filename_stem}.png")
    img.save(path)
    return f"qrcodes/{filename_stem}.png"

def seed_masterclasses():
    if Masterclass.query.count() == 0:
        sessions = [
            Masterclass(
                title="AI Diagnostics in Clinical Practice",
                speaker="Dr. Sana Rekik",
                time_slot="10:00 – 11:30",
                room="Salle Atlas",
                description=(
                    "Discover how machine learning models are reshaping radiology and pathology workflows. "
                    "This session covers real-world deployments in MENA hospitals, model interpretability, "
                    "and the practical steps to integrate AI tools into existing clinical pipelines without "
                    "disrupting patient care."
                ),
                takeaway="Deploy AI tools that assist — not replace — the clinician, with measurable outcomes.",
                video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
            ),
            Masterclass(
                title="Health Data Monetisation & Compliance",
                speaker="Me. Amine Hamdi",
                time_slot="13:00 – 14:30",
                room="Salle Médina",
                description=(
                    "Learn the legal frameworks and technical architecture that allow healthcare startups to "
                    "commercialise patient data while fully meeting GDPR and Tunisian law requirements. "
                    "Includes a step-by-step blueprint for building a compliant data product from scratch."
                ),
                takeaway="Structure a compliant, investor-ready health data product in 3 actionable steps.",
                video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
            ),
            Masterclass(
                title="Digital Therapeutics & Remote Patient Monitoring",
                speaker="Dr. Mohamed Ben Salah",
                time_slot="15:00 – 16:30",
                room="Salle Carthage",
                description=(
                    "Explore the rapidly growing market of prescription digital therapeutics (PDTs) and "
                    "connected devices for remote monitoring. Learn which chronic disease areas show the "
                    "strongest ROI, and how Tunisian startups can position themselves in the EU and Gulf markets."
                ),
                takeaway="Identify the top 3 digital therapeutic categories with a validated path to reimbursement.",
                video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
            ),
        ]
        db.session.add_all(sessions)
        db.session.commit()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    attendees   = Attendee.query.order_by(Attendee.id.desc()).all()
    masterclasses = Masterclass.query.all()
    counts = {
        "total":       Attendee.query.count(),
        "masterclass": Attendee.query.filter_by(category="masterclass").count(),
        "vip":         Attendee.query.filter_by(category="vip").count(),
        "participant": Attendee.query.filter_by(category="participant").count(),
    }
    return render_template("index.html", attendees=attendees,
                           masterclasses=masterclasses, counts=counts)

@app.route("/add", methods=["POST"])
def add_attendee():
    name     = request.form.get("name", "").strip()
    linkedin = request.form.get("linkedin", "").strip()
    category = request.form.get("category", "participant").strip()

    if not name or not linkedin:
        flash("Name and LinkedIn URL are required.", "error")
        return redirect(url_for("index"))

    # Normalise LinkedIn URL
    if not linkedin.startswith("http"):
        linkedin = "https://" + linkedin

    # Handle photo upload
    photo_path = None
    file = request.files.get("photo")
    if file and file.filename and allowed_file(file.filename):
        ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
        uid = uuid.uuid4().hex
        fname = f"{uid}.{ext}"
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
        photo_path = f"uploads/{fname}"

    # Generate QR code
    uid = uuid.uuid4().hex
    qr_path = generate_qr(linkedin, uid)

    attendee = Attendee(name=name, linkedin=linkedin,
                        category=category, photo=photo_path, qr_code=qr_path)
    db.session.add(attendee)
    db.session.commit()
    flash(f"{name} has been added to the directory!", "success")
    return redirect(url_for("index"))

@app.route("/masterclasses")
def masterclasses():
    sessions = Masterclass.query.all()
    return render_template("masterclasses.html", masterclasses=sessions)

@app.route("/delete/<int:id>", methods=["POST"])
def delete_attendee(id):
    a = Attendee.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    flash("Attendee removed.", "info")
    return redirect(url_for("index"))

# ── Init ──────────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()
    seed_masterclasses()

if __name__ == "__main__":
    app.run(debug=True, port=5000)

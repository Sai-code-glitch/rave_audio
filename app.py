import os
import re
import secrets
from datetime import date, datetime, timezone

from flask import Flask, Response, abort, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a")


class Speaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tagline = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    frequency_specs = db.Column(db.String(200), nullable=False)
    cabinet_finish = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)


class Booking(db.Model):
    """A private audition request submitted from /book."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    speaker_id = db.Column(db.Integer, db.ForeignKey("speaker.id"), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    speaker = db.relationship("Speaker")


def _database_url():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return "sqlite:///rave_laboratory.db"
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


def seed_speakers():
    if Speaker.query.count():
        return
    db.session.add_all([
        Speaker(
            name="RAVE Monolith-X",
            tagline="Floor-standing Acoustic Sculpture",
            price="$12,500 / pair",
            frequency_specs="18Hz - 28kHz | Ultra-low Transient Distortion",
            cabinet_finish="Hand-selected African Wenge Wood / Carbon Structural Composites",
            description="Engineered by Ravi Velnati Audio Labs. The Monolith-X sets an unprecedented benchmark in standard three-way loudspeaker architecture.",
        ),
        Speaker(
            name="RAVE Velocity Studio",
            tagline="Bespoke Near-field Precision",
            price="$6,200 / pair",
            frequency_specs="34Hz - 40kHz | Pure Ribbon High Frequency Driver",
            cabinet_finish="14-layer High-Gloss Italian Mirror-Matched Lacquer",
            description="Designed specifically for critical spatial engineering and luxury audiophile listening environments.",
        ),
    ])
    db.session.commit()


def validate_booking(form, today=None):
    """Return (clean_data, errors) for the booking form."""
    today = today or date.today()
    errors = {}
    name = (form.get("name") or "").strip()
    email = (form.get("email") or "").strip()
    notes = (form.get("notes") or "").strip()
    raw_date = (form.get("date") or "").strip()
    speaker_id = (form.get("speaker_id") or "").strip()

    if not name:
        errors["name"] = "Please enter your name."
    elif len(name) > 120:
        errors["name"] = "Name must be 120 characters or fewer."
    if not EMAIL_RE.match(email) or len(email) > 200:
        errors["email"] = "Please enter a valid email address."
    session_date = None
    try:
        session_date = date.fromisoformat(raw_date)
        if session_date < today:
            errors["date"] = "Please choose today or a future date."
    except ValueError:
        errors["date"] = "Please choose a session date."
    if len(notes) > 2000:
        errors["notes"] = "Notes must be 2000 characters or fewer."
    speaker = None
    if speaker_id:
        speaker = db.session.get(Speaker, int(speaker_id)) if speaker_id.isdigit() else None
        if speaker is None:
            errors["speaker_id"] = "Please choose a system from the list."

    clean = {"name": name, "email": email, "session_date": session_date, "notes": notes or None,
             "speaker_id": speaker.id if speaker else None}
    return clean, errors


def _audio_playlist(static_folder):
    audio_dir = os.path.join(static_folder, "audio")
    playlist = []
    if os.path.isdir(audio_dir):
        for file in sorted(os.listdir(audio_dir)):
            stem, ext = os.path.splitext(file)
            if ext.lower() in AUDIO_EXTENSIONS:
                playlist.append({"display_name": stem.replace("_", " "), "filename": file})
    return playlist


def _check_admin(password):
    auth = request.authorization
    return bool(auth and auth.password and secrets.compare_digest(auth.password, password))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        SQLALCHEMY_DATABASE_URI=_database_url(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    # Create tables and the two flagship speakers on every start, so the site
    # works under gunicorn as well as with `python app.py`.
    with app.app_context():
        db.create_all()
        seed_speakers()

    @app.route("/")
    def index():
        return render_template("index.html", products=Speaker.query.all(), playlist=_audio_playlist(app.static_folder))

    @app.route("/product/<int:speaker_id>")
    def product_detail(speaker_id):
        speaker = db.get_or_404(Speaker, speaker_id)
        return render_template("product.html", speaker=speaker)

    @app.route("/book", methods=["GET", "POST"])
    def book_session():
        speakers = Speaker.query.order_by(Speaker.id).all()
        if request.method == "POST":
            data, errors = validate_booking(request.form)
            if errors:
                return render_template("book.html", speakers=speakers, errors=errors, form=request.form,
                                       today=date.today().isoformat()), 400
            booking = Booking(**data)
            db.session.add(booking)
            db.session.commit()
            return redirect(url_for("booking_success", booking_id=booking.id))
        selected = request.args.get("speaker", "")
        return render_template("book.html", speakers=speakers, errors={}, form={"speaker_id": selected},
                               today=date.today().isoformat())

    @app.route("/book/confirmed/<int:booking_id>")
    def booking_success(booking_id):
        booking = db.get_or_404(Booking, booking_id)
        return render_template("success.html", name=booking.name, booking=booking)

    @app.route("/admin/bookings")
    def admin_bookings():
        password = os.environ.get("ADMIN_PASSWORD")
        if not password:
            abort(404)
        if not _check_admin(password):
            return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="RAVE admin"'})
        bookings = Booking.query.order_by(Booking.session_date.asc(), Booking.created_at.asc()).all()
        return render_template("admin_bookings.html", bookings=bookings)

    @app.errorhandler(404)
    def not_found(_err):
        return render_template("404.html"), 404

    return app


app = create_app()


def initialize_database_data():
    """Kept for compatibility with older scripts; tables are now created on start."""
    with app.app_context():
        db.create_all()
        seed_speakers()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=int(os.environ.get("PORT", 5000)))

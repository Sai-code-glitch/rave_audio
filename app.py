from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Configurations for security and database persistence
app.config['SECRET_KEY'] = 'rave_secret_acoustic_encryption_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rave_laboratory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Schema Model for RAVE Speakers Inventory
class Speaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tagline = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    frequency_specs = db.Column(db.String(200), nullable=False)
    cabinet_finish = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

# Database Schema Model for Client Listening Room Inquiries
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(100), nullable=False)
    preferred_date = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)

# Main Homepage Route
@app.route('/')
def index():
    # Pull items dynamically out of our local SQLite database layout
    all_speakers = Speaker.query.all()
    return render_template('index.html', products=all_speakers)

# ADVANCEMENT 2: Dynamic Routing Engine for Individual Product Detail Pages
@app.route('/product/<int:speaker_id>')
def product_detail(speaker_id):
    speaker = Speaker.query.get_or_404(speaker_id)
    return render_template('product.html', speaker=speaker)

# ADVANCEMENT 3: Listening Session Post Handler & Client Intake Engine
@app.route('/book', methods=['GET', 'POST'])
def book_session():
    if request.method == 'POST':
        try:
            new_booking = Booking(
                client_name=request.form['name'],
                client_email=request.form['email'],
                preferred_date=request.form['date'],
                notes=request.form['notes']
            )
            db.session.add(new_booking)
            db.session.commit()
            return render_template('success.html', name=request.form['name'])
        except Exception as e:
            return f"An operational error occurred handling database stream: {e}"
            
    return render_template('book.html')

# Core CLI initialization setup command loop to build DB schemas dynamically
def initialize_database_data():
    with app.app_context():
        db.create_all()
        # Seed the database only if empty
        if Speaker.query.count() == 0:
            monolith = Speaker(
                name="RAVE Monolith-X",
                tagline="Floor-standing Acoustic Sculpture",
                price="$12,500 / pair",
                frequency_specs="18Hz - 28kHz | Ultra-low Transient Distortion",
                cabinet_finish="Hand-selected African Wenge Wood / Carbon Structural Composites",
                description="Engineered by Ravi Velnati Audio Labs. The Monolith-X sets an unprecedented benchmark in standard three-way loudspeaker architecture, using complex mathematical phase-alignment models."
            )
            velocity = Speaker(
                name="RAVE Velocity Studio",
                tagline="Bespoke Near-field Precision",
                price="$6,200 / pair",
                frequency_specs="34Hz - 40kHz | Pure Ribbon High Frequency Driver",
                cabinet_finish="14-layer High-Gloss Italian Mirror-Matched Lacquer",
                description="Designed specifically for critical spatial engineering and luxury audiophile listening environments where soundstage width and phase coherency cannot be compromised."
            )
            db.session.add_all([monolith, velocity])
            db.session.commit()

if __name__ == '__main__':
    initialize_database_data()
    app.run(debug=True)

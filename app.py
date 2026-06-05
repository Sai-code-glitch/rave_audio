from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rave_secret_acoustic_encryption_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rave_laboratory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Speaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tagline = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    frequency_specs = db.Column(db.String(200), nullable=False)
    cabinet_finish = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

@app.route('/')
def index():
    all_speakers = Speaker.query.all()
    audio_dir = os.path.join(app.static_folder, 'audio')
    playlist = []
    
    if os.path.exists(audio_dir):
        for file in os.listdir(audio_dir):
            if file.endswith(('.mp3', '.wav', '.m4a')):
                playlist.append({
                    'display_name': file.replace('.mp3', '').replace('.wav', '').replace('_', ' '),
                    'filename': file
                })
                
    return render_template('index.html', products=all_speakers, playlist=playlist)

@app.route('/product/<int:speaker_id>')
def product_detail(speaker_id):
    speaker = Speaker.query.get_or_404(speaker_id)
    return render_template('product.html', speaker=speaker)

@app.route('/book', methods=['GET', 'POST'])
def book_session():
    if request.method == 'POST':
        return render_template('success.html', name=request.form['name'])
    return render_template('book.html')

def initialize_database_data():
    with app.app_context():
        db.create_all()
        if Speaker.query.count() == 0:
            monolith = Speaker(
                name="RAVE Monolith-X",
                tagline="Floor-standing Acoustic Sculpture",
                price="$12,500 / pair",
                frequency_specs="18Hz - 28kHz | Ultra-low Transient Distortion",
                cabinet_finish="Hand-selected African Wenge Wood / Carbon Structural Composites",
                description="Engineered by Ravi Velnati Audio Labs. The Monolith-X sets an unprecedented benchmark in standard three-way loudspeaker architecture."
            )
            velocity = Speaker(
                name="RAVE Velocity Studio",
                tagline="Bespoke Near-field Precision",
                price="$6,200 / pair",
                frequency_specs="34Hz - 40kHz | Pure Ribbon High Frequency Driver",
                cabinet_finish="14-layer High-Gloss Italian Mirror-Matched Lacquer",
                description="Designed specifically for critical spatial engineering and luxury audiophile listening environments."
            )
            db.session.add_all([monolith, velocity])
            db.session.commit()

if __name__ == '__main__':
    initialize_database_data()
    app.run(debug=True)

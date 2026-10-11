# RAVE Audio Laboratories

Showroom site for RAVE loudspeakers by Ravi Velnati Audio Labs: the flagship collection, an interactive listening console, product pages, and private audition booking.

## Features

- **Listening console**: play reference tracks from `static/audio/` and shape them live in the browser:
  - Calibration gain (±12 dB)
  - HF attenuator: high-shelf filter at 8 kHz (±3 dB)
  - Phase matrix: real polarity inversion
  - Room correction: low-shelf cut at 120 Hz (free-standing 0 dB, boundary −3 dB, corner −6 dB)
  - 3D spatial orbit (HRTF panner)
  - Wave-shaper overdrive saturation
  - Log-scale FFT spectrum analyzer
- **Collection and product pages** from the database
- **Audition booking**: requests are validated and saved; each product page links to the form with that speaker preselected
- **Bookings admin** at `/admin/bookings`, protected by a password
- Works on phones and respects reduced-motion settings

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python app.py              # http://localhost:5000
python -m pytest -q        # run the tests
```

Tables and the two flagship speakers are created automatically on start.

## Environment variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask secret key. Set a long random value in production. |
| `ADMIN_PASSWORD` | Enables `/admin/bookings` (browser login, any username). Without it the page is hidden. |
| `DATABASE_URL` | Optional Postgres URL. Defaults to SQLite (`instance/rave_laboratory.db`). |
| `FLASK_DEBUG` | Set to `1` for debug mode when running `python app.py`. |

## Deploy (Render or similar)

Build command `pip install -r requirements.txt`; the start command comes from the `Procfile`. Set `SECRET_KEY` and `ADMIN_PASSWORD`. For bookings to survive redeploys, use a Postgres `DATABASE_URL`; SQLite on most free hosts is wiped on each deploy.

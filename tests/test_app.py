import os
from datetime import date, timedelta

os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest  # noqa: E402

from app import Booking, Speaker, create_app, db, validate_booking  # noqa: E402


@pytest.fixture()
def app():
    application = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


def future(days=7):
    return (date.today() + timedelta(days=days)).isoformat()


def test_speakers_seeded_and_home_renders(client, app):
    with app.app_context():
        assert Speaker.query.count() == 2
    r = client.get("/")
    assert r.status_code == 200
    assert b"RAVE Monolith-X" in r.data
    assert b"fftSpectrumCanvas" in r.data
    assert b"overdriveSaturationSlider" in r.data


def test_product_page_and_404(client):
    r = client.get("/product/1")
    assert r.status_code == 200 and b"Monolith-X" in r.data
    assert b"/book?speaker=1" in r.data
    assert client.get("/product/999").status_code == 404
    assert b"Signal Lost" in client.get("/nope").data


def test_book_form_preselects_speaker(client):
    r = client.get("/book?speaker=2")
    assert r.status_code == 200
    assert b'value="2" selected' in r.data


def test_booking_is_saved_and_confirmed(client, app):
    r = client.post("/book", data={
        "name": "Ada Lovelace", "email": "ada@example.com", "date": future(),
        "speaker_id": "1", "notes": "Large room",
    })
    assert r.status_code == 302
    follow = client.get(r.headers["Location"])
    assert b"Ada Lovelace" in follow.data and b"RAVE Monolith-X" in follow.data
    with app.app_context():
        b = Booking.query.one()
        assert b.email == "ada@example.com" and b.speaker_id == 1 and b.notes == "Large room"


def test_invalid_booking_shows_errors_and_keeps_input(client, app):
    r = client.post("/book", data={"name": "", "email": "not-an-email", "date": "2000-01-01", "notes": "hi"})
    assert r.status_code == 400
    assert b"Please enter your name." in r.data
    assert b"valid email" in r.data
    assert b"future date" in r.data
    assert b"not-an-email" in r.data
    with app.app_context():
        assert Booking.query.count() == 0


def test_validate_booking_rules(app):
    with app.app_context():
        today = date(2026, 10, 11)
        ok, errors = validate_booking({"name": "A", "email": "a@b.co", "date": "2026-10-11"}, today=today)
        assert errors == {} and ok["speaker_id"] is None
        _, errors = validate_booking({"name": "A", "email": "a@b.co", "date": "2026-10-11", "speaker_id": "77"}, today=today)
        assert "speaker_id" in errors
        _, errors = validate_booking({"name": "A", "email": "a@b.co", "date": "bad"}, today=today)
        assert "date" in errors


def test_admin_bookings_hidden_without_password(client, monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    assert client.get("/admin/bookings").status_code == 404


def test_admin_bookings_requires_password(client, monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", "s3cret")
    client.post("/book", data={"name": "Grace", "email": "g@example.com", "date": future(3)})
    assert client.get("/admin/bookings").status_code == 401
    bad = client.get("/admin/bookings", headers={"Authorization": "Basic " + __import__("base64").b64encode(b"admin:wrong").decode()})
    assert bad.status_code == 401
    good = client.get("/admin/bookings", headers={"Authorization": "Basic " + __import__("base64").b64encode(b"admin:s3cret").decode()})
    assert good.status_code == 200 and b"Grace" in good.data and b"g@example.com" in good.data

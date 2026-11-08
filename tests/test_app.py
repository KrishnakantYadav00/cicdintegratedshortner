import pytest
from app import app as flask_app, db


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"URL Shortener" in res.data or b"html" in res.data.lower()


def test_shorten_valid_url(client):
    res = client.post("/api/shorten", json={"url": "https://example.com/page"})
    assert res.status_code == 201
    body = res.get_json()
    assert "code" in body
    assert body["target_url"] == "https://example.com/page"
    assert body["click_count"] == 0


def test_shorten_rejects_invalid_url(client):
    res = client.post("/api/shorten", json={"url": "not-a-url"})
    assert res.status_code == 400


def test_shorten_rejects_missing_url(client):
    res = client.post("/api/shorten", json={})
    assert res.status_code == 400


def test_custom_code(client):
    res = client.post(
        "/api/shorten", json={"url": "https://example.com", "custom_code": "my-link"}
    )
    assert res.status_code == 201
    assert res.get_json()["code"] == "my-link"


def test_custom_code_collision(client):
    client.post(
        "/api/shorten", json={"url": "https://example.com", "custom_code": "dup"}
    )
    res = client.post(
        "/api/shorten", json={"url": "https://example.org", "custom_code": "dup"}
    )
    assert res.status_code == 409


def test_redirect_increments_click_count(client):
    create_res = client.post(
        "/api/shorten", json={"url": "https://example.com/target"}
    )
    code = create_res.get_json()["code"]

    redirect_res = client.get(f"/{code}", follow_redirects=False)
    assert redirect_res.status_code == 302
    assert redirect_res.headers["Location"] == "https://example.com/target"

    stats_res = client.get(f"/api/stats/{code}")
    assert stats_res.get_json()["click_count"] == 1


def test_resolve_unknown_code_404(client):
    res = client.get("/does-not-exist")
    assert res.status_code == 404


def test_stats_unknown_code_404(client):
    res = client.get("/api/stats/does-not-exist")
    assert res.status_code == 404

from datetime import datetime, timedelta
from app.main import links_db, generate_short_code


def test_generate_short_code():
    code1 = generate_short_code()
    assert len(code1) == 6

    code2 = generate_short_code(length=8)
    assert len(code2) == 8

    code3 = generate_short_code()
    assert code1 != code3


def test_create_short_link(client):
    response = client.post(
        "/links/shorten", json={"original_url": "https://example.com/test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == "https://example.com/test"
    assert data["clicks"] == 0
    assert data["last_accessed"] is None


def test_create_short_link_with_custom_alias(client):
    response = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com/test", "custom_alias": "mytest"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == "mytest"

    response = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com/another", "custom_alias": "mytest"},
    )
    assert response.status_code == 400
    assert "Custom alias already in use" in response.json()["detail"]


def test_create_short_link_with_expiration(client):
    expires_at = (datetime.now() + timedelta(days=1)).isoformat()
    response = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com/test", "expires_at": expires_at},
    )
    assert response.status_code == 200
    data = response.json()
    assert "expires_at" in data
    assert data["expires_at"] is not None


def test_get_link_info(client):
    create_response = client.post(
        "/links/shorten", json={"original_url": "https://example.com/test"}
    )
    short_code = create_response.json()["short_code"]

    response = client.get(f"/links/{short_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == short_code
    assert data["original_url"] == "https://example.com/test"


def test_get_nonexistent_link(client):
    response = client.get("/links/nonexistent")
    assert response.status_code == 404
    assert "Link not found" in response.json()["detail"]


def test_update_link(client):
    create_response = client.post(
        "/links/shorten", json={"original_url": "https://example.com/test"}
    )
    short_code = create_response.json()["short_code"]

    response = client.put(
        f"/links/{short_code}", json={"original_url": "https://example.com/updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == "https://example.com/updated"

    response = client.get(f"/links/{short_code}")
    assert response.json()["original_url"] == "https://example.com/updated"


def test_delete_link(client):
    create_response = client.post(
        "/links/shorten", json={"original_url": "https://example.com/test"}
    )
    short_code = create_response.json()["short_code"]

    response = client.delete(f"/links/{short_code}")
    assert response.status_code == 200
    assert "Link deleted successfully" in response.json()["message"]

    response = client.get(f"/links/{short_code}")
    assert response.status_code == 404


def test_search_by_original_url(client):
    original_url = "https://example.com/searchtest"
    create_response = client.post("/links/shorten", json={"original_url": original_url})
    expected_short_code = create_response.json()["short_code"]

    response = client.get(f"/links/search?original_url={original_url}")
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == expected_short_code
    assert data["original_url"] == original_url


def test_search_nonexistent_url(client):
    response = client.get("/links/search?original_url=https://example.com/nonexistent")
    assert response.status_code == 404
    assert "Link not found" in response.json()["detail"]


def test_redirect_to_original(client):
    original_url = "https://example.com/redirect-test"
    create_response = client.post("/links/shorten", json={"original_url": original_url})
    short_code = create_response.json()["short_code"]

    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == original_url

    stats_response = client.get(f"/links/{short_code}")
    stats_data = stats_response.json()
    assert stats_data["clicks"] == 1
    assert stats_data["last_accessed"] is not None


def test_expired_link(client):
    expires_at = (datetime.now() - timedelta(days=1)).isoformat()
    create_response = client.post(
        "/links/shorten",
        json={"original_url": "https://example.com/expired", "expires_at": expires_at},
    )
    short_code = create_response.json()["short_code"]

    response = client.get(f"/{short_code}")
    assert response.status_code == 404
    assert "Link has expired" in response.json()["detail"]

    assert short_code not in links_db

from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app


def test_register_user(client: TestClient):
    response = client.post("/auth/register", json={"email": "driver@example.com", "password": "secret-password"})

    assert response.status_code == 201
    assert response.json()["email"] == "driver@example.com"


def test_login_user(client: TestClient):
    client.post("/auth/register", json={"email": "driver@example.com", "password": "secret-password"})
    response = client.post("/auth/login", json={"email": "driver@example.com", "password": "secret-password"})

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_normalizes_email(client: TestClient):
    client.post("/auth/register", json={"email": "driver@example.com", "password": "secret-password"})
    response = client.post("/auth/login", json={"email": " DRIVER@example.com ", "password": "secret-password"})

    assert response.status_code == 200


def test_reject_login_sql_injection_like_email(client: TestClient):
    response = client.post("/auth/login", json={"email": "' OR 1=1 --", "password": "secret-password"})

    assert response.status_code == 422


def test_reject_login_empty_password(client: TestClient):
    response = client.post("/auth/login", json={"email": "driver@example.com", "password": ""})

    assert response.status_code == 422


def test_reject_login_password_with_control_characters(client: TestClient):
    response = client.post("/auth/login", json={"email": "driver@example.com", "password": "secret\npassword"})

    assert response.status_code == 422


def test_reject_login_oversized_password(client: TestClient):
    response = client.post("/auth/login", json={"email": "driver@example.com", "password": "x" * 129})

    assert response.status_code == 422


def test_register_requires_email_verification_before_login(client: TestClient, monkeypatch):
    sent_tokens: list[str] = []

    def override_settings():
        return Settings(EMAIL_VERIFICATION_REQUIRED=True)

    def fake_send_verification_email(settings, recipient: str, token: str):
        sent_tokens.append(token)

    app.dependency_overrides[get_settings] = override_settings
    monkeypatch.setattr("app.api.routers.auth.send_verification_email", fake_send_verification_email)

    register_response = client.post(
        "/auth/register",
        json={"email": "driver@example.com", "password": "secret-password"},
    )
    blocked_login_response = client.post(
        "/auth/login",
        json={"email": "driver@example.com", "password": "secret-password"},
    )
    verify_response = client.get(f"/auth/verify-email?token={sent_tokens[0]}")
    login_response = client.post(
        "/auth/login",
        json={"email": "driver@example.com", "password": "secret-password"},
    )

    app.dependency_overrides.pop(get_settings, None)

    assert register_response.status_code == 201
    assert register_response.json()["email_verified"] is False
    assert blocked_login_response.status_code == 403
    assert verify_response.status_code == 200
    assert verify_response.json()["email_verified"] is True
    assert login_response.status_code == 200


def test_reject_invalid_login(client: TestClient):
    client.post("/auth/register", json={"email": "driver@example.com", "password": "secret-password"})
    response = client.post("/auth/login", json={"email": "driver@example.com", "password": "wrong-password"})

    assert response.status_code == 401


def test_rate_limits_auth_requests(client: TestClient):
    def override_settings():
        return Settings(RATE_LIMIT_AUTH_REQUESTS=2, RATE_LIMIT_GENERAL_REQUESTS=100)

    app.dependency_overrides[get_settings] = override_settings

    client.post("/auth/login", json={"email": "missing@example.com", "password": "wrong-password"})
    client.post("/auth/login", json={"email": "missing@example.com", "password": "wrong-password"})
    response = client.post("/auth/login", json={"email": "missing@example.com", "password": "wrong-password"})

    app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 429


def test_rate_limits_general_requests(client: TestClient):
    def override_settings():
        return Settings(RATE_LIMIT_GENERAL_REQUESTS=2, RATE_LIMIT_AUTH_REQUESTS=100)

    app.dependency_overrides[get_settings] = override_settings

    client.get("/health")
    client.get("/health")
    response = client.get("/health")

    app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 429


def test_reject_missing_token(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 401


def test_health(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/health", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_list_maps(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/api/maps", headers=auth_headers)

    assert response.status_code == 200
    map_ids = {item["map_id"] for item in response.json()["maps"]}
    assert map_ids >= {"small_loop", "crossroads", "parking"}


def test_create_map(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/api/maps",
        headers=auth_headers,
        json={
            "map_id": "lab_track",
            "name": "Lab track",
            "description": "User-owned test map.",
            "width": 250,
            "height": 150,
        },
    )

    assert response.status_code == 201
    assert response.json()["map_id"] == "lab_track"


def test_create_route(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/api/routes",
        headers=auth_headers,
        json={
            "map_id": "small_loop",
            "start": {"x": 10, "y": 20, "heading": 90},
            "end": {"x": 120, "y": 80},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["map_id"] == "small_loop"
    assert body["start"] == {"x": 10.0, "y": 20.0, "heading": 90.0}
    assert body["end"] == {"x": 120.0, "y": 80.0, "heading": None}
    assert body["is_current"] is True


def test_reject_unknown_map(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/api/routes",
        headers=auth_headers,
        json={
            "map_id": "missing",
            "start": {"x": 10, "y": 20},
            "end": {"x": 120, "y": 80},
        },
    )

    assert response.status_code == 400


def test_reject_start_point_outside_map(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/api/routes",
        headers=auth_headers,
        json={
            "map_id": "small_loop",
            "start": {"x": -1, "y": 20},
            "end": {"x": 120, "y": 80},
        },
    )

    assert response.status_code == 400


def test_reject_end_point_outside_map(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/api/routes",
        headers=auth_headers,
        json={
            "map_id": "small_loop",
            "start": {"x": 10, "y": 20},
            "end": {"x": 999, "y": 80},
        },
    )

    assert response.status_code == 400


def test_get_current_route(client: TestClient, auth_headers: dict[str, str]):
    client.post(
        "/api/routes",
        headers=auth_headers,
        json={
            "map_id": "small_loop",
            "start": {"x": 10, "y": 20},
            "end": {"x": 120, "y": 80},
        },
    )

    response = client.get("/api/routes/current", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["map_id"] == "small_loop"


def test_get_current_route_not_found(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/api/routes/current", headers=auth_headers)

    assert response.status_code == 404


def test_routes_are_isolated_between_users(client: TestClient, auth_headers: dict[str, str]):
    client.post(
        "/api/routes",
        headers=auth_headers,
        json={
            "map_id": "small_loop",
            "start": {"x": 10, "y": 20},
            "end": {"x": 120, "y": 80},
        },
    )
    client.post("/auth/register", json={"email": "other@example.com", "password": "secret-password"})
    login_response = client.post("/auth/login", json={"email": "other@example.com", "password": "secret-password"})
    other_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    response = client.get("/api/routes/current", headers=other_headers)

    assert response.status_code == 404

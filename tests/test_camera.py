import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app


def test_camera_stream_uses_configured_url(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    requested_urls: list[str] = []

    class FakeStream:
        def __init__(self, url: str):
            requested_urls.append(url)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        def raise_for_status(self):
            return None

        async def aiter_bytes(self):
            yield b"--frame\r\n"
            yield b"camera-bytes"

    class FakeAsyncClient:
        def __init__(self, timeout=None):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        def stream(self, method: str, url: str):
            assert method == "GET"
            return FakeStream(url)

    def override_settings():
        return Settings(CAMERA_STREAM_URL="http://camera.local/stream.mjpg")

    monkeypatch.setattr("app.api.routers.camera.httpx.AsyncClient", FakeAsyncClient)
    app.dependency_overrides[get_settings] = override_settings

    with client.stream("GET", "/api/camera/stream", headers=auth_headers) as response:
        body = response.read()

    app.dependency_overrides.pop(get_settings, None)

    assert response.status_code == 200
    assert b"camera-bytes" in body
    assert requested_urls == ["http://camera.local/stream.mjpg"]


def test_camera_stream_accepts_query_token(
    client: TestClient,
    auth_token: str,
    monkeypatch: pytest.MonkeyPatch,
):
    class FakeStream:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        def raise_for_status(self):
            return None

        async def aiter_bytes(self):
            yield b"query-token-camera-bytes"

    class FakeAsyncClient:
        def __init__(self, timeout=None):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        def stream(self, method: str, url: str):
            assert method == "GET"
            return FakeStream()

    monkeypatch.setattr("app.api.routers.camera.httpx.AsyncClient", FakeAsyncClient)

    with client.stream("GET", f"/api/camera/stream?access_token={auth_token}") as response:
        body = response.read()

    assert response.status_code == 200
    assert b"query-token-camera-bytes" in body

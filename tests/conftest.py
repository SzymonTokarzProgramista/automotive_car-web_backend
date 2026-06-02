import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings
from app.database import Base, get_db
from app.main import app
from app.rate_limit import clear_rate_limits


@pytest.fixture(autouse=True)
def reset_rate_limits():
    clear_rate_limits()
    yield
    clear_rate_limits()


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    def override_get_settings():
        return Settings(EMAIL_VERIFICATION_REQUIRED=False)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    client.post("/auth/register", json={"email": "driver@example.com", "password": "secret-password"})
    response = client.post("/auth/login", json={"email": "driver@example.com", "password": "secret-password"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_token(auth_headers: dict[str, str]) -> str:
    return auth_headers["Authorization"].replace("Bearer ", "")

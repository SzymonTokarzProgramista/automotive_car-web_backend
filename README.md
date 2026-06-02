# Automotive Car Web Backend

FastAPI backend for a web UI that previews an autonomous vehicle camera stream, lets the user choose a predefined map, and stores the current start/end route in PostgreSQL.

## Requirements

- Python 3.11+
- Docker Desktop or another Docker Compose runtime

## Run With Docker

For the full system, prefer the central Compose repository:

```powershell
cd ..\automotive_car-machine_docker
docker compose up --build
```

Standalone backend-only run:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The API will be available at `http://localhost:8000`. The backend container runs Alembic migrations before starting Uvicorn.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
docker compose up -d postgres
alembic upgrade head
```

## Local Run

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Configuration

Configuration is loaded from environment variables or `.env`:

- `DATABASE_URL` - PostgreSQL connection string.
- `CAMERA_STREAM_URL` - MJPEG/HTTP camera stream URL.
- `CORS_ORIGINS` - comma-separated frontend origins, defaulting to Vite and Create React App dev servers.
- `JWT_SECRET_KEY` - secret used to sign JWT access tokens.
- `JWT_EXPIRES_MINUTES` - token lifetime in minutes.
- `RATE_LIMIT_WINDOW_SECONDS` - request counting window.
- `RATE_LIMIT_GENERAL_REQUESTS` - max requests per client in that window.
- `RATE_LIMIT_AUTH_REQUESTS` - stricter auth request limit per client in that window.
- `EMAIL_VERIFICATION_REQUIRED` - requires users to confirm email before login.
- `EMAIL_VERIFICATION_EXPIRES_MINUTES` - email verification token lifetime.
- `PUBLIC_UI_URL` - base URL used to build email verification links.
- `SMTP_*` - optional SMTP settings; when `SMTP_HOST` is empty, verification links are logged.

## API

All endpoints except `POST /auth/register` and `POST /auth/login` require `Authorization: Bearer <token>`.

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/verify-email?token=<token>`
- `GET /auth/me`
- `GET /health`
- `GET /api/maps` - returns `{ "maps": [...] }`
- `GET /api/maps/{map_id}`
- `POST /api/maps`
- `POST /api/routes`
- `GET /api/routes/current`
- `GET /api/camera/stream` - accepts `Authorization: Bearer <token>` or `?access_token=<token>` for browser MJPEG previews.

Example registration request:

```json
{
  "email": "driver@example.com",
  "password": "secret-password"
}
```

Example login request:

```json
{
  "email": "driver@example.com",
  "password": "secret-password"
}
```

Example route payload:

```json
{
  "map_id": "small_loop",
  "start": { "x": 10, "y": 20, "heading": 90 },
  "end": { "x": 120, "y": 80 }
}
```

## Tests

```powershell
pytest
```

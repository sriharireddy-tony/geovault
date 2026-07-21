# AI Video Generation Backend

FastAPI backend with PostgreSQL, SQLAlchemy (async), and JWT authentication.

## Prerequisites

- Python 3.11+
- PostgreSQL with a database (default name in `.env.example` is `geovault`) and a user that can connect

## Setup

1. Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copy the environment file and adjust values:

```bash
copy .env.example .env
```

Edit `.env`:

- Set `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_NAME` (or set a single `DATABASE_URL` instead; the URL wins if both are present).
- The app converts `postgresql://` URLs to use the `asyncpg` driver automatically.
- Set `SECRET_KEY` to a long random string (for example from `openssl rand -hex 32`).

3. Ensure PostgreSQL is running and the database exists.

## Run

From the `backend` directory (with the virtual environment activated):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000/docs for interactive API documentation.

## API overview

| Method | Path | Auth |
|--------|------|------|
| POST | `/auth/register` | No |
| POST | `/auth/login` | No (form: `username` = email, `password`) |
| GET | `/auth/me` | Bearer token |
| POST | `/video/create` | Bearer token |
| GET | `/video/my-videos` | Bearer token |

After login, use the `access_token` value as `Authorization: Bearer <token>`.

## Frontend

A React (Vite) app in `../frontend` calls these APIs. Start the API on port **8000**, then in `frontend/` run `npm install` and `npm run dev` (see `frontend/README.md`). `CORS_ORIGINS` in `.env` must include the dev UI origin (defaults include `http://127.0.0.1:5173`).

# LuminaLib

Library app: auth, book upload/borrow/return, reviews, LLM summary and sentiment, and recommendations.

## Quick Start

From the project root:

```bash
docker-compose up --build
```

This starts:
- API Service (FastAPI) on port 8000
- React Frontend (Next.js) on port 3000
- PostgreSQL on port 5432
- Local LLM or mock (set `LLM_PROVIDER=ollama` or leave as `mock` default)

Open http://localhost:3000 in a browser.

### Using Ollama

1. Start the stack: `docker compose up --build`
2. Pull the model: `docker compose exec ollama ollama pull llama3.2`
3. Verify: `curl http://localhost:8000/health/ollama`

## Configuration

Backend: copy `backend/.env.example` to `backend/.env` and set:
- `DB_URL` – PostgreSQL URL
- `SECRET_KEY` – JWT signing key
- `STORAGE_BACKEND` – `local` (default) or `s3`
- `LLM_PROVIDER` – `mock`, `ollama`, or `openai`
- `RECOMMENDATION_ENGINE` – `hybrid` (default) or `llm`

Frontend: set `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`).

## Migrations

```bash
cd backend
alembic upgrade head
```

If you get `DuplicateTable` errors, stamp the initial migration:
```bash
alembic stamp 001
alembic upgrade head
```

## Run without Docker

1. PostgreSQL running; create database and user
2. Backend: `cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --reload`
3. Frontend: `cd frontend && npm install && npm run dev`
4. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` for the frontend

See `ARCHITECTURE.md` for detailed architecture documentation.

## Code Quality

- **Backend:** `ruff check .` and `ruff format .`
- **Frontend:** `npm run lint` and `npm test`

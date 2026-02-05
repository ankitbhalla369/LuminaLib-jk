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

Open http://localhost:3000 in a browser. Sign up, then add books (with optional file), borrow/return, and leave reviews. Summaries and review consensus run in the background (mock LLM by default).

### Using Ollama

When using the built-in `ollama` service from `docker-compose.yml`:

1. Start the stack: `docker compose up --build`
2. Pull the model: `docker compose exec ollama ollama pull llama3.2`
3. Verify: `curl http://localhost:8000/health/ollama`

The model is cached in the `ollama_data` volume, so you only need to run the pull command once unless you remove that volume.

## Configuration

Backend: copy `backend/.env.example` to `backend/.env` and set:

- `DB_URL` – PostgreSQL URL (default in compose: `postgresql+asyncpg://luminalib:luminalib@db:5432/luminalib`)
- `SECRET_KEY` – JWT signing key
- `STORAGE_BACKEND` – `local` (default) or `s3` (set `AWS_BUCKET`, `AWS_REGION`; uses boto3)
- `LLM_PROVIDER` – `mock`, `ollama`, or `openai` (for OpenAI set `OPENAI_API_KEY` and optionally `OPENAI_MODEL`, default `gpt-4o-mini`)
- `RECOMMENDATION_ENGINE` – `hybrid` (default: preference + collaborative + TF-IDF) or `llm` (LLM ranks recommendations and similar books)

Frontend: set `NEXT_PUBLIC_API_URL` (e.g. `http://localhost:8000`) when not using Docker default.

## Storage and LLM Swapping

You can swap **file storage** or **LLM provider** by changing one config line (and any required env vars).

**File storage:**
- **Local (default):** `STORAGE_BACKEND=local` (or omit). Files go to `LOCAL_STORAGE_PATH` (default `./uploads`).
- **S3:** Set `STORAGE_BACKEND=s3` and set `AWS_BUCKET` and `AWS_REGION` (e.g. `us-east-1`). No code changes needed.

**LLM:**
- **Mock (no API):** `LLM_PROVIDER=mock` (default). Hardcoded/simple responses.
- **Ollama (Llama 3, etc.):** `LLM_PROVIDER=ollama` and `OLLAMA_BASE_URL` (e.g. `http://ollama:11434` in Docker).
- **OpenAI:** Set `LLM_PROVIDER=openai`, `OPENAI_API_KEY=<your-key>`, and optionally `OPENAI_MODEL` (default `gpt-4o-mini`).

No application code changes; only config (env or `docker-compose` environment).

## Migrations

Schema is managed by Alembic. From the backend directory:

```bash
cd backend
alembic upgrade head
```

Use `DB_URL` from `.env` (or set it in the environment). To add a new migration after changing models: `alembic revision --autogenerate -m "description"` then `alembic upgrade head`.

**If the database already has tables** (e.g. created earlier without Alembic) and you get `DuplicateTable` when running `upgrade head`, tell Alembic the initial migration is already applied:

```bash
cd backend
alembic stamp 001
alembic upgrade head
```

## Run without Docker

1. PostgreSQL running; create database and user (e.g. `luminalib`).
2. Backend: `cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --reload`
3. Frontend: `cd frontend && npm install && npm run dev`
4. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` for the frontend.

See `ARCHITECTURE.md` for schema, async LLM, recommendation logic, and frontend design.

## Code Quality

- **Backend:** From `backend`, run `ruff check .` and `ruff format .` (or `--fix` / omit `--check` to fix/format). Import order and style are enforced via `pyproject.toml`.
- **Frontend:** From `frontend`, run `npm run lint` (ESLint) and `npm test` (Jest + React Testing Library).

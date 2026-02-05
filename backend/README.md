# LuminaLib Backend

FastAPI backend for LuminaLib library management system.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Configuration

Copy `.env.example` to `.env` and configure:
- `DB_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret
- `STORAGE_BACKEND` - `local` or `s3`
- `LLM_PROVIDER` - `mock`, `ollama`, or `openai`
- `RECOMMENDATION_ENGINE` - `hybrid` or `llm`

## Code Quality

```bash
ruff check .
ruff format .
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

See `ARCHITECTURE.md` in the project root for detailed architecture documentation.

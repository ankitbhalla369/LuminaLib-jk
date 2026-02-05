# LuminaLib Backend

FastAPI backend for LuminaLib library management system.

## Tech Stack

- FastAPI 0.109.2
- PostgreSQL with SQLAlchemy (async)
- Alembic for migrations
- JWT authentication
- scikit-learn for recommendations
- Pluggable LLM (Mock/Ollama/OpenAI) and Storage (Local/S3) backends

## Setup

### Using Docker

See the main project [README.md](../README.md) for docker-compose instructions.

### Local Development

1. **Install Dependencies:**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run Migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

API will be available at `http://localhost:8000`

## Configuration

Key environment variables (see `.env.example` for all options):

```bash
# Database
DB_URL=postgresql+asyncpg://user:pass@localhost:5432/luminalib

# Authentication
SECRET_KEY=your-secret-key-here

# Storage Backend
STORAGE_BACKEND=local  # or 's3'
LOCAL_STORAGE_PATH=./uploads

# For S3 storage:
# AWS_BUCKET=your-bucket-name
# AWS_REGION=us-east-1

# LLM Provider
LLM_PROVIDER=mock  # or 'ollama' or 'openai'

# For Ollama:
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2

# For OpenAI:
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini

# Recommendation Engine
RECOMMENDATION_ENGINE=hybrid  # or 'llm'
```

## Code Quality

```bash
ruff check .      # Check code
ruff format .     # Format code
ruff check --fix . # Auto-fix issues
```

Configuration is in `pyproject.toml`.

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

- `app/routers/` - API route handlers (auth, books, recommendations)
- `app/llm/` - LLM provider implementations (mock, ollama, openai)
- `app/storage/` - Storage backend implementations (local, s3)
- `app/models.py` - SQLAlchemy ORM models
- `app/schemas.py` - Pydantic request/response schemas
- `app/deps.py` - Dependency injection (auth, storage, LLM)

See `ARCHITECTURE.md` in the project root for detailed architecture documentation.

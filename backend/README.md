# LuminaLib Backend

FastAPI-based REST API backend for the LuminaLib library management system with ML-powered recommendations and LLM integrations.

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) 0.109.2
- **Server:** [Uvicorn](https://www.uvicorn.org/) with standard extras (WebSockets, HTTP/2)
- **Database:** PostgreSQL with async support
  - [SQLAlchemy](https://www.sqlalchemy.org/) 2.0.25 (async ORM)
  - [asyncpg](https://github.com/MagicStack/asyncpg) 0.29.0 (async PostgreSQL driver)
  - [psycopg2-binary](https://www.psycopg.org/) 2.9.9 (sync support)
- **Authentication:** JWT-based auth
  - [python-jose](https://github.com/mpdavis/python-jose) with cryptography
  - [passlib](https://passlib.readthedocs.io/) with bcrypt for password hashing
- **Data Validation:** [Pydantic](https://docs.pydantic.dev/) 2.6.1 with settings management
- **Database Migrations:** [Alembic](https://alembic.sqlalchemy.org/) 1.13.1
- **Machine Learning:** [scikit-learn](https://scikit-learn.org/) for recommendation engine
- **LLM Integrations:**
  - [OpenAI](https://github.com/openai/openai-python) Python SDK
  - Ollama (local LLM support via HTTP)
  - Mock provider for testing
- **Storage:**
  - Local file system storage
  - [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) for AWS S3 integration
- **PDF Processing:** [pypdf](https://pypdf.readthedocs.io/) for text extraction
- **HTTP Client:** [httpx](https://www.python-httpx.org/) for async HTTP requests
- **Code Quality:** [Ruff](https://docs.astral.sh/ruff/) for linting and formatting

## Features Implemented

### 1. Authentication & User Management
- User registration and login endpoints
- JWT token-based authentication
- Password hashing with bcrypt
- Protected routes with dependency injection
- User profile management with preferences

### 2. Book Management
- CRUD operations for books
- Book upload with optional PDF file attachment
- PDF text extraction for content analysis
- Book metadata (title, author, ISBN, genre, publication year)
- Book availability tracking (available/borrowed status)

### 3. Borrow/Return System
- Borrow books with timestamp tracking
- Return books functionality
- User borrowing history
- Book availability status management

### 4. Review System
- Users can leave reviews with ratings (1-5 stars)
- Text reviews with timestamps
- Review association with books and users
- Review retrieval per book

### 5. LLM Integration (Pluggable Architecture)
- **Three Provider Options:**
  - **Mock:** Hardcoded responses for testing
  - **Ollama:** Local Llama models (llama3.2 or custom)
  - **OpenAI:** Cloud-based GPT models (default: gpt-4o-mini)
- **Features:**
  - Book summary generation from content/metadata
  - Review sentiment analysis (positive/negative/neutral)
  - Review consensus generation (aggregated insights)
- **Async Background Processing:** LLM tasks run asynchronously to avoid blocking API responses
- **Health Check Endpoint:** `/health/ollama` to verify Ollama connectivity and model availability

### 6. Recommendation Engine
- **Hybrid Recommendation System (default):**
  - **User Preferences:** Genre-based matching
  - **Collaborative Filtering:** User-user similarity based on ratings
  - **TF-IDF:** Content-based filtering using book descriptions/summaries
- **LLM-based Recommendations (optional):**
  - LLM ranks and generates recommendations based on user history
  - Similar books suggestions using LLM analysis
- **Configurable:** Switch between `hybrid` and `llm` via `RECOMMENDATION_ENGINE` setting

### 7. File Storage (Pluggable Architecture)
- **Local Storage (default):** Files stored in `./uploads` directory
- **AWS S3 Storage:** Full S3 integration with boto3
- **Single-config Swap:** Change `STORAGE_BACKEND` to switch between providers
- Presigned URLs for secure file access
- File upload with multipart form data

### 8. Database Schema & Migrations
- **Alembic Migrations:** Version-controlled schema changes
- **Models:**
  - `User`: Authentication and preferences
  - `Book`: Book metadata and content
  - `Review`: User reviews with ratings
  - `BorrowRecord`: Borrow/return tracking
- **Relationships:** SQLAlchemy relationships for ORM queries
- **Indexes:** Optimized for common queries

### 9. API Documentation
- Auto-generated OpenAPI/Swagger documentation at `/docs`
- ReDoc documentation at `/redoc`
- Health check endpoint at `/health`

### 10. Configuration Management
- Environment-based configuration with `.env` file
- Pydantic settings for validation
- Configurable database URL, JWT secret, storage backend, LLM provider
- Docker-ready configuration

## Project Structure

```
backend/
├── alembic/                 # Database migrations
│   ├── versions/            # Migration scripts
│   └── env.py              # Alembic configuration
├── app/
│   ├── llm/                # LLM provider implementations
│   │   ├── base.py         # Abstract base class
│   │   ├── mock.py         # Mock provider
│   │   ├── ollama.py       # Ollama integration
│   │   ├── openai.py       # OpenAI integration
│   │   └── prompts.py      # LLM prompt templates
│   ├── routers/            # API route handlers
│   │   ├── auth.py         # Authentication endpoints
│   │   ├── books.py        # Book CRUD, borrow/return, reviews
│   │   └── recommendations.py  # Recommendation endpoints
│   ├── storage/            # File storage implementations
│   │   ├── base.py         # Abstract storage class
│   │   ├── local.py        # Local filesystem storage
│   │   └── s3.py           # AWS S3 storage
│   ├── config.py           # Application settings
│   ├── db.py               # Database connection and session
│   ├── deps.py             # Dependency injection (auth, storage, LLM)
│   ├── main.py             # FastAPI application entry point
│   ├── models.py           # SQLAlchemy ORM models
│   └── schemas.py          # Pydantic request/response schemas
├── uploads/                # Local file storage (when using local backend)
├── .env                    # Environment configuration
├── alembic.ini             # Alembic configuration
├── Dockerfile              # Docker container definition
├── pyproject.toml          # Ruff configuration
└── requirements.txt        # Python dependencies
```

## Setup & Running

### Using Docker (Recommended)
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
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

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

Run linting and formatting checks:

```bash
# Check code
ruff check .

# Format code
ruff format .

# Auto-fix issues
ruff check --fix .
```

Configuration is in `pyproject.toml`.

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update user preferences

### Books
- `GET /books` - List all books
- `GET /books/{id}` - Get book details
- `POST /books` - Create new book (with optional file upload)
- `PUT /books/{id}` - Update book
- `DELETE /books/{id}` - Delete book
- `POST /books/{id}/borrow` - Borrow a book
- `POST /books/{id}/return` - Return a book
- `POST /books/{id}/reviews` - Add review
- `GET /books/{id}/reviews` - Get book reviews

### Recommendations
- `GET /recommendations/for-me` - Get personalized recommendations
- `GET /recommendations/similar/{book_id}` - Get similar books

### Health
- `GET /health` - Basic health check
- `GET /health/ollama` - Ollama connectivity check

## Architecture Notes

- **Async/Await:** All database operations and external API calls use async/await for better concurrency
- **Dependency Injection:** FastAPI's dependency system for auth, database sessions, storage, and LLM providers
- **Repository Pattern:** Clean separation between API routes, business logic, and data access
- **Plugin Architecture:** Storage and LLM providers implement abstract base classes for easy swapping
- **Background Tasks:** LLM operations (summaries, sentiment analysis) run as background tasks
- **Security:** Password hashing, JWT tokens, CORS middleware, SQL injection protection via ORM

## Database Schema

See [ARCHITECTURE.md](../ARCHITECTURE.md) in the project root for detailed schema documentation.

Key tables:
- `users` - User accounts and preferences
- `books` - Book catalog
- `reviews` - User reviews and ratings
- `borrow_records` - Borrowing history

## Extensibility

The backend is designed for easy extension:

1. **Add new LLM provider:** Implement `LLMProvider` interface in `app/llm/`
2. **Add new storage backend:** Implement `StorageBackend` interface in `app/storage/`
3. **Add new recommendation algorithm:** Extend logic in `app/routers/recommendations.py`
4. **Add new API endpoints:** Create new router in `app/routers/` and include in `main.py`

See [ARCHITECTURE.md](../ARCHITECTURE.md) for more details.

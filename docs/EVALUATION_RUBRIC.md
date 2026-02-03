# Evaluation Rubric – LuminaLib

How the project addresses each criterion.

---

## 1. Modularity: Can we swap the Storage/LLM providers easily?

**Yes.** Swapping is done via a single config line (environment variable).

**Storage:**
- Interface: `app/storage/base.py` – `StorageBackend` (abstract `put`, `get`, `delete`).
- Implementations: `LocalStorage` (`app/storage/local.py`), `S3Storage` (`app/storage/s3.py`).
- Wiring: `app/deps.py` – `get_storage()` returns implementation based on `STORAGE_BACKEND` (e.g. `local` or `s3`).
- **Swap:** Set `STORAGE_BACKEND=s3` (and `AWS_BUCKET`, `AWS_REGION`) to use S3; no code change.

**LLM:**
- Interface: `app/llm/base.py` – `LLMBackend` (abstract `summarize`, `analyze_sentiment`, `recommend_for_user`, `recommend_similar`, `suggest_books_by_genre`).
- Implementations: `MockLLM` (`app/llm/mock.py`), `OllamaLLM` (`app/llm/ollama.py`).
- Wiring: `app/deps.py` – `get_llm()` returns implementation based on `LLM_PROVIDER` (e.g. `mock` or `ollama`).
- **Swap:** Set `LLM_PROVIDER=ollama` to use Ollama; add a new class (e.g. `OpenAILLM`) and one branch in `get_llm()` to support another provider.

Routers and services depend on `StorageBackend` and `LLMBackend` via FastAPI `Depends(get_storage)` / `Depends(get_llm)`; they never import concrete implementations.

---

## 2. Frontend Best Practices: SSR, abstracted network, unit tests

**SSR:**
- Next.js App Router is used. The root `layout.tsx` is a Server Component (default). Pages that need auth or client state use `'use client'` and fetch in `useEffect`. Static or SEO-relevant content can stay as Server Components; auth-gated content is client-rendered after hydration so the client can read the token and call the API. This matches a dashboard-style app where most content is behind login.

**Network layer abstracted:**
- All API calls go through a single typed service: `src/lib/api.ts`. Components never call `fetch` or axios directly; they use `api.auth.*`, `api.books.*`, `api.recommendations.*`, etc. Base URL and auth header are centralized; changing the API host or adding interceptors is done in one place.

**Unit tests:**
- Critical UI components are covered under `src/components/__tests__/`:
  - `Nav.test.tsx` – nav links when logged in / out.
  - `BookCard.test.tsx` – title, author, genre, link.
  - `ErrorMessage.test.tsx` – visibility and message.
  - `LoadingSpinner.test.tsx` – message and class.
- Jest is configured with `next/jest`, `jsdom`, and `@testing-library/jest-dom` (`jest.setup.js`). Run: `npm test` in the frontend directory.

---

## 3. Docker Proficiency: Does the compose file work seamlessly?

**Yes.** One-command start:

```bash
docker-compose up --build
```

**Services:**
1. **db** – PostgreSQL 15 (Alpine); env for user/password/db; volume for persistence; port 5432.
2. **api** – Backend built from `./backend` Dockerfile; runs `alembic upgrade head` then `uvicorn`; env for `DB_URL`, `SECRET_KEY`, `STORAGE_BACKEND`, `LLM_PROVIDER`; volume for local uploads; depends on `db`; port 8000.
3. **frontend** – Next.js built from `./frontend` Dockerfile; env `NEXT_PUBLIC_API_URL=http://localhost:8000`; depends on `api`; port 3000.

**Flow:** DB starts first; API waits for DB, runs migrations, then starts; frontend can call API. No separate LLM container by default (API uses `LLM_PROVIDER=mock`); for Ollama, run Ollama on the host and set `LLM_PROVIDER=ollama` (and point to host if needed).

The repo README documents this one-command start and the four deliverables (API, Frontend, DB, LLM or mock).

---

## 4. Code Hygiene: Imports sorted? Code linted?

**Backend:**
- **Linting:** Ruff is configured in `backend/pyproject.toml` with rules for style and import order (E, F, I, N, W; isort known-first-party: `app`). Run from backend: `ruff check .` and `ruff format --check .` (or `ruff check . --fix` and `ruff format .`).
- **Import order:** Imports follow a single convention: standard library, third-party, local (`app.*`). Ruff’s isort-compatible rules enforce this.

**Frontend:**
- **Linting:** ESLint with `eslint-config-next`. Run: `npm run lint` in the frontend directory.
- **Type safety:** TypeScript strict mode via `tsconfig.json`; API types in `src/lib/api.ts`.

Imports are ordered consistently; lint is runnable via the above commands.

---

## 5. GenAI Implementation: Structured, reusable prompt engineering?

**Yes.** Prompts are centralized and reused.

- **Module:** `app/llm/prompts.py` – defines prompt builders (e.g. `summary_prompt(text)`, `sentiment_prompt(reviews)`, `recommend_similar_prompt(book_info, candidates)`, `recommend_for_user_prompt(preferences, candidates)`, `suggest_books_prompt(genres, limit)`). Each returns a string (and optionally a system message) so prompts are consistent and easy to tune.
- **Usage:** `app/llm/ollama.py` (and any future LLM backend) imports these helpers and uses them in `summarize`, `analyze_sentiment`, `recommend_similar`, `recommend_for_user`, `suggest_books_by_genre`. No raw prompt strings in the Ollama class; all prompt text lives in `prompts.py`.
- **Benefits:** One place to edit prompts; same prompts reusable across backends (e.g. a future OpenAI backend); clear separation between “what we ask” (prompts) and “how we call the model” (ollama.py).

---

## Summary

| Criterion | Addressed |
|-----------|-----------|
| 1. Modularity (Storage/LLM swap) | Yes – single config line; interfaces in base modules; wiring in `deps.py`. |
| 2. Frontend (SSR, network, tests) | Yes – App Router; `api.ts` only; Jest + RTL for Nav, BookCard, ErrorMessage, LoadingSpinner. |
| 3. Docker | Yes – `docker-compose up --build` runs API, Frontend, DB; LLM via mock or external Ollama. |
| 4. Code hygiene | Yes – Ruff (backend) and ESLint (frontend); import order and lint documented. |
| 5. GenAI prompts | Yes – `app/llm/prompts.py`; structured, reusable; used by `ollama.py`. |

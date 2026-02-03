# Run LuminaLib with Docker only

From the **project root** (directory containing `docker-compose.yml`).

## Start everything

```bash
docker compose up --build
```

- **Frontend:** http://localhost:3000  
- **API:** http://localhost:8000  
- **PostgreSQL:** localhost:5433 (user `luminalib`, password `luminalib`, db `luminalib`)

Migrations run automatically on API startup (`alembic upgrade head`).

## Run in background

```bash
docker compose up --build -d
```

## View logs

```bash
docker compose logs -f
```

Single service:

```bash
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f db
```

## Stop

```bash
docker compose down
```

## Stop and remove volumes (fresh DB)

```bash
docker compose down -v
```

Then `docker compose up --build` for a clean start.

## Rebuild after code changes

```bash
docker compose up --build
```

Or rebuild a single service:

```bash
docker compose up --build api
docker compose up --build frontend
```

## Ollama (book summaries, review consensus, AI suggestions)

The stack runs **Ollama in Docker** so the API can reach it without host config. No need to install or run Ollama on your machine.

1. Start the stack (one command):
   ```bash
   docker compose up --build
   ```
   On first start, the `ollama` service automatically checks for the `llama3.2` model and pulls it into the `ollama_data` volume if missing. Subsequent starts skip the pull.
2. Verify: `curl http://localhost:8000/health/ollama` should return `{"ollama":"ok",...,"model_loaded":true}` once the model is ready.

Models are stored in the `ollama_data` volume, so you only need to pull once per environment; the automatic check in `docker-compose.yml` handles this for you.

To use **host Ollama** instead (e.g. you already run Ollama on the host): remove the `ollama` service from `docker-compose.yml`, set `OLLAMA_BASE_URL: http://host.docker.internal:11434` for the `api` service, add `extra_hosts: - "host.docker.internal:host-gateway"`, and ensure Ollama listens on `0.0.0.0` (snap installs often ignore `OLLAMA_HOST`; using Ollama in Docker avoids that).

To use the **Mock LLM** instead (no Ollama), set `LLM_PROVIDER: mock` for the `api` service and remove the `ollama` service (or leave it unused).

### Verify Ollama is working

1. **Health check** (no auth):
   ```bash
   curl http://localhost:8000/health/ollama
   ```
   - `{"ollama":"ok","url":"..."}` — Ollama is reachable.
   - `{"ollama":"unavailable","detail":"..."}` — Ollama not running or wrong URL (check `OLLAMA_BASE_URL`, and on Docker that the host is reachable).
   - `{"ollama":"not_used","llm_provider":"mock"}` — App is using Mock LLM, not Ollama.

2. **Ensure a model is pulled** on the host:
   ```bash
   ollama pull llama3.2
   ollama list
   ```

3. **Why no book recommendations?**
   - **Similar books** (on a book page): Needs Ollama reachable; if it fails, the API returns empty suggestions (no error).
   - **You might also like** (Recommendations page): Add at least one **genre preference** (e.g. Fiction, Sci-Fi) in the form on that page; then the AI suggestions use that. If Ollama is down, you get no suggestions.
   - **In your library (by genre)** (Recommendations page): Shows books from your catalog that match your genre preferences; add books and genre preferences if the list is empty.

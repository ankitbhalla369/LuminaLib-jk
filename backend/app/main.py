from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, books, recommendations

app = FastAPI(title="LuminaLib API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(recommendations.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/ollama")
async def health_ollama():
    """Verify Ollama is reachable and configured model is available."""
    from app.config import settings
    if settings.llm_provider != "ollama":
        return {"ollama": "not_used", "llm_provider": settings.llm_provider}
    import httpx
    base = settings.ollama_base_url.rstrip("/")
    model = getattr(settings, "ollama_model", "llama3.2") or "llama3.2"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{base}/api/tags")
            r.raise_for_status()
            data = r.json()
        models = data.get("models") or []
        names = [m.get("name", "") for m in models]
        # Model can be "llama3.2" or "llama3.2:latest"
        model_loaded = any(name == model or name.startswith(model + ":") for name in names)
        return {
            "ollama": "ok",
            "url": base,
            "model": model,
            "model_loaded": model_loaded,
            "hint": "Run: ollama pull " + model if not model_loaded else None,
        }
    except Exception as e:
        return {"ollama": "unavailable", "url": base, "model": model, "detail": str(e)}

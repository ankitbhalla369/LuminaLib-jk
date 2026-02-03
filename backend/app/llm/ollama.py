import json
import logging
import re

import httpx

from app.config import settings

logger = logging.getLogger(__name__)
from app.llm.base import LLMBackend
from app.llm.prompts import (
    recommend_for_user_prompt,
    recommend_similar_prompt,
    sentiment_prompt,
    suggest_books_prompt,
    suggest_books_similar_prompt,
    summary_prompt,
)


def _parse_id_list(text: str) -> list[int]:
    ids = []
    for part in re.split(r"[\s,]+", text.strip()):
        part = part.strip().rstrip(".")
        if part.isdigit():
            ids.append(int(part))
    return ids


def _normalize_suggestion_line(line: str) -> str:
    """Strip numbering and markdown so '1. Dune by Frank Herbert (Sci-Fi)' becomes 'Dune by Frank Herbert (Sci-Fi)'."""
    line = line.strip()
    # Remove leading markdown list: "1. ", "2) ", "- ", "* "
    line = re.sub(r"^\s*\d+[.)]\s*", "", line)
    line = re.sub(r"^[-*]\s+", "", line)
    return line.strip()


def _parse_suggestion_line(line: str, fallback_genre: str) -> dict[str, str] | None:
    """Parse a line like 'Title by Author (Genre)' or 'Title by Author'. Returns dict or None."""
    line = _normalize_suggestion_line(line)
    if not line or line.startswith("#"):
        return None
    by_idx = line.find(" by ")
    if by_idx <= 0:
        return None
    title = line[:by_idx].strip().strip('"')
    rest = line[by_idx + 4 :].strip()
    paren = rest.rfind(" (")
    if paren > 0 and rest.endswith(")"):
        author = rest[:paren].strip()
        genre = rest[paren + 2 : -1].strip()
    else:
        author = rest
        genre = fallback_genre
    if title and author:
        return {"title": title, "author": author, "genre": genre or fallback_genre}
    return None


class OllamaLLM(LLMBackend):
    def __init__(self):
        self.base = settings.ollama_base_url.rstrip("/")
        self.model = getattr(settings, "ollama_model", "llama3.2") or "llama3.2"

    async def _call(self, prompt: str, system: str = "") -> str:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(
                    f"{self.base}/api/generate",
                    json={"model": self.model, "prompt": prompt, "system": system or "You are helpful."},
                )
                r.raise_for_status()
                out = []
                async for line in r.aiter_lines():
                    if line:
                        d = json.loads(line)
                        if "response" in d:
                            out.append(d["response"])
                return "".join(out).strip() or "No response."
        except Exception as e:
            logger.warning("Ollama _call failed: %s", e, exc_info=True)
            return ""

    async def summarize(self, text: str) -> str:
        if not text or len(text.strip()) < 10:
            return "Summary not available."
        prompt, system = summary_prompt(text)
        return await self._call(prompt, system)

    async def analyze_sentiment(self, reviews: list[str]) -> str:
        if not reviews:
            return "No reviews yet."
        prompt, system = sentiment_prompt(reviews)
        return await self._call(prompt, system)

    async def recommend_similar(self, book_info: str, candidates: list[dict], limit: int = 10) -> list[int]:
        if not candidates:
            return []
        prompt, system = recommend_similar_prompt(book_info, candidates)
        out = await self._call(prompt, system)
        ids = _parse_id_list(out)
        seen = set()
        ordered = []
        for i in ids:
            if i not in seen and i in {c["id"] for c in candidates}:
                seen.add(i)
                ordered.append(i)
            if len(ordered) >= limit:
                break
        return ordered

    async def recommend_for_user(self, preferences: str, candidates: list[dict], limit: int = 10) -> list[int]:
        if not candidates:
            return []
        prompt, system = recommend_for_user_prompt(preferences, candidates)
        out = await self._call(prompt, system)
        ids = _parse_id_list(out)
        seen = set()
        ordered = []
        for i in ids:
            if i not in seen and i in {c["id"] for c in candidates}:
                seen.add(i)
                ordered.append(i)
            if len(ordered) >= limit:
                break
        return ordered

    async def suggest_books_by_genre(self, genres: list[str], limit: int = 10) -> list[dict[str, str]]:
        if not genres:
            return []
        prompt, system = suggest_books_prompt(genres, limit)
        out = await self._call(prompt, system)
        if not out or not out.strip() or out.strip().lower() == "no response.":
            logger.warning("Ollama suggest_books_by_genre returned empty response (check Ollama is running and model is loaded)")
            return []
        suggestions = []
        fallback = genres[0] if genres else ""
        for line in out.splitlines():
            parsed = _parse_suggestion_line(line, fallback)
            if parsed:
                suggestions.append(parsed)
            if len(suggestions) >= limit:
                break
        if not suggestions and out.strip():
            logger.warning("Ollama suggest_books_by_genre returned text but no parseable lines. First 300 chars: %s", out[:300])
        return suggestions[:limit]

    async def suggest_books_similar_to(
        self,
        book_title: str,
        book_author: str | None = None,
        book_genre: str | None = None,
        book_summary: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        if not book_title or not book_title.strip():
            return []
        prompt, system = suggest_books_similar_prompt(
            book_title.strip(),
            book_author,
            book_genre,
            book_summary,
            limit,
        )
        out = await self._call(prompt, system)
        if not out or not out.strip() or out.strip().lower() == "no response.":
            logger.warning("Ollama suggest_books_similar_to returned empty response (check Ollama is running and model is loaded)")
            return []
        suggestions = []
        fallback_genre = book_genre or "Fiction"
        for line in out.splitlines():
            parsed = _parse_suggestion_line(line, fallback_genre)
            if parsed:
                suggestions.append(parsed)
            if len(suggestions) >= limit:
                break
        if not suggestions and out.strip():
            logger.warning("Ollama suggest_books_similar_to returned text but no parseable lines. First 300 chars: %s", out[:300])
        return suggestions[:limit]

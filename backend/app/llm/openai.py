import re

from app.config import settings
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


class OpenAILLM(LLMBackend):
    def __init__(self):
        self.model = settings.openai_model or "gpt-4o-mini"

    async def _call(self, prompt: str, system: str = "") -> str:
        if not settings.openai_api_key:
            return ""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            resp = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system or "You are helpful."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
            )
            if resp.choices and resp.choices[0].message.content:
                return resp.choices[0].message.content.strip() or ""
            return ""
        except Exception:
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
        suggestions = []
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            by_idx = line.find(" by ")
            if by_idx <= 0:
                continue
            title = line[:by_idx].strip().strip('"')
            rest = line[by_idx + 4 :].strip()
            paren = rest.rfind(" (")
            if paren > 0 and rest.endswith(")"):
                author = rest[:paren].strip()
                genre = rest[paren + 2 : -1].strip()
            else:
                author = rest
                genre = genres[0] if genres else ""
            if title and author:
                suggestions.append({"title": title, "author": author, "genre": genre or (genres[0] if genres else "")})
            if len(suggestions) >= limit:
                break
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
        suggestions = []
        fallback_genre = book_genre or "Fiction"
        for line in out.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            by_idx = line.find(" by ")
            if by_idx <= 0:
                continue
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
                suggestions.append({"title": title, "author": author, "genre": genre or fallback_genre})
            if len(suggestions) >= limit:
                break
        return suggestions[:limit]

from abc import ABC, abstractmethod
from typing import Any


class LLMBackend(ABC):
    @abstractmethod
    async def summarize(self, text: str) -> str:
        pass

    @abstractmethod
    async def analyze_sentiment(self, reviews: list[str]) -> str:
        pass

    async def recommend_similar(self, book_info: str, candidates: list[dict[str, Any]], limit: int = 10) -> list[int]:
        return []

    async def recommend_for_user(self, preferences: str, candidates: list[dict[str, Any]], limit: int = 10) -> list[int]:
        return []

    async def suggest_books_by_genre(self, genres: list[str], limit: int = 10) -> list[dict[str, str]]:
        """Suggest well-known books in these genres that are not necessarily in the catalog. Returns list of { title, author, genre }."""
        return []

    async def suggest_books_similar_to(
        self,
        book_title: str,
        book_author: str | None = None,
        book_genre: str | None = None,
        book_summary: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        """Suggest well-known books similar to the given book (not necessarily in catalog). Returns list of { title, author, genre }."""
        return []

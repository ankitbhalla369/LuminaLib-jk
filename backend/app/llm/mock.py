from app.llm.base import LLMBackend


class MockLLM(LLMBackend):
    async def summarize(self, text: str) -> str:
        if not text or len(text.strip()) < 10:
            return "Summary not available."
        return text[:500] + "..." if len(text) > 500 else text

    async def analyze_sentiment(self, reviews: list[str]) -> str:
        if not reviews:
            return "No reviews yet."
        # Mock: synthesize a short consensus from review snippets (no real LLM call)
        snippets = [r.strip()[:100] for r in reviews[:5] if r and r.strip()]
        if not snippets:
            return "No reviews yet."
        if len(snippets) == 1:
            return f"One reader noted: {snippets[0]}{'...' if len(reviews[0]) > 100 else '.'}"
        themes = "; ".join(snippets) if len(snippets) <= 2 else "; ".join(snippets[:2]) + f" (and {len(snippets) - 2} more)"
        return f"Readers shared mixed perspectives. Recurring themes: {themes}"

    async def recommend_similar(self, book_info: str, candidates: list[dict], limit: int = 10) -> list[int]:
        return [c["id"] for c in candidates[:limit]]

    async def recommend_for_user(self, preferences: str, candidates: list[dict], limit: int = 10) -> list[int]:
        return [c["id"] for c in candidates[:limit]]

    async def suggest_books_by_genre(self, genres: list[str], limit: int = 10) -> list[dict[str, str]]:
        suggestions = []
        by_genre: dict[str, list[tuple[str, str]]] = {
            "fiction": [("To Kill a Mockingbird", "Harper Lee"), ("1984", "George Orwell"), ("Pride and Prejudice", "Jane Austen"), ("The Great Gatsby", "F. Scott Fitzgerald")],
            "sci-fi": [("Dune", "Frank Herbert"), ("Foundation", "Isaac Asimov"), ("The Martian", "Andy Weir"), ("Neuromancer", "William Gibson")],
            "science fiction": [("Dune", "Frank Herbert"), ("Foundation", "Isaac Asimov"), ("The Martian", "Andy Weir")],
            "mystery": [("The Girl with the Dragon Tattoo", "Stieg Larsson"), ("Gone Girl", "Gillian Flynn"), ("The Da Vinci Code", "Dan Brown")],
            "fantasy": [("The Lord of the Rings", "J.R.R. Tolkien"), ("A Game of Thrones", "George R.R. Martin"), ("Harry Potter and the Philosopher's Stone", "J.K. Rowling")],
            "non-fiction": [("Sapiens", "Yuval Noah Harari"), ("The Lean Startup", "Eric Ries"), ("Atomic Habits", "James Clear")],
            "nonfiction": [("Sapiens", "Yuval Noah Harari"), ("Atomic Habits", "James Clear")],
        }
        for g in genres[:5]:
            key = g.lower().strip()
            for genre_key, books in by_genre.items():
                if genre_key in key or key in genre_key:
                    for title, author in books[: max(2, limit // max(1, len(genres)))]:
                        suggestions.append({"title": title, "author": author, "genre": g})
                    break
            if len(suggestions) >= limit:
                break
        if not suggestions and genres:
            for title, author in by_genre.get("fiction", [])[:limit]:
                suggestions.append({"title": title, "author": author, "genre": genres[0] or "Fiction"})
        return suggestions[:limit]

    async def suggest_books_similar_to(
        self,
        book_title: str,
        book_author: str | None = None,
        book_genre: str | None = None,
        book_summary: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, str]]:
        genre = (book_genre or "fiction").lower()
        by_genre: dict[str, list[tuple[str, str]]] = {
            "fiction": [("To Kill a Mockingbird", "Harper Lee"), ("1984", "George Orwell"), ("Pride and Prejudice", "Jane Austen"), ("The Great Gatsby", "F. Scott Fitzgerald"), ("The Catcher in the Rye", "J.D. Salinger")],
            "sci-fi": [("Dune", "Frank Herbert"), ("Foundation", "Isaac Asimov"), ("The Martian", "Andy Weir"), ("Neuromancer", "William Gibson")],
            "science fiction": [("Dune", "Frank Herbert"), ("Foundation", "Isaac Asimov"), ("The Martian", "Andy Weir")],
            "mystery": [("The Girl with the Dragon Tattoo", "Stieg Larsson"), ("Gone Girl", "Gillian Flynn"), ("The Da Vinci Code", "Dan Brown")],
            "fantasy": [("The Lord of the Rings", "J.R.R. Tolkien"), ("A Game of Thrones", "George R.R. Martin"), ("Harry Potter and the Philosopher's Stone", "J.K. Rowling")],
        }
        suggestions = []
        for key, books in by_genre.items():
            if key in genre or genre in key:
                for title, author in books[:limit]:
                    suggestions.append({"title": title, "author": author, "genre": book_genre or key})
                break
        if not suggestions:
            for title, author in by_genre["fiction"][:limit]:
                suggestions.append({"title": title, "author": author, "genre": book_genre or "Fiction"})
        return suggestions[:limit]

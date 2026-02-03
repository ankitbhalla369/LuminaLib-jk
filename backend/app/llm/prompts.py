"""Structured, reusable prompts for LLM-backed features."""

SUMMARY_SYSTEM = "You write concise book summaries."
SENTIMENT_SYSTEM = "You synthesize reader opinions."
RECOMMEND_SYSTEM = "You recommend books. Reply only with numbers."
SUGGEST_BOOKS_SYSTEM = "You suggest real, well-known books. One per line: Title by Author (Genre)."


def summary_prompt(text: str, max_chars: int = 4000) -> tuple[str, str]:
    """Prompt and system message for book summarization."""
    prompt = f"Summarize this book content in 2-3 sentences:\n\n{text[:max_chars]}"
    return prompt, SUMMARY_SYSTEM


def sentiment_prompt(reviews: list[str], max_reviews: int = 20) -> tuple[str, str]:
    """Prompt and system message for review consensus / sentiment."""
    if not reviews:
        return "", SENTIMENT_SYSTEM
    combined = "\n".join(f"- {r}" for r in reviews[:max_reviews])
    prompt = (
        "Based on these reader reviews, write one short paragraph (2-3 sentences) "
        "describing the overall reader sentiment:\n\n" + combined
    )
    return prompt, SENTIMENT_SYSTEM


def _candidates_lines(candidates: list[dict], max_items: int = 80) -> str:
    return "\n".join(
        f"ID {c['id']}: {c.get('title', '')} by {c.get('author', '')} ({c.get('genre', '')})"
        for c in candidates[:max_items]
    )


def recommend_similar_prompt(book_info: str, candidates: list[dict]) -> tuple[str, str]:
    """Prompt and system for similar-books recommendation."""
    lines = _candidates_lines(candidates)
    prompt = f"""Book to match:
{book_info}

Candidates (pick the most similar, in order):
{lines}

Reply with ONLY a comma-separated list of book IDs, most similar first. Example: 5, 12, 3"""
    return prompt, RECOMMEND_SYSTEM


def recommend_for_user_prompt(preferences: str, candidates: list[dict]) -> tuple[str, str]:
    """Prompt and system for personalized recommendations."""
    lines = _candidates_lines(candidates)
    prompt = f"""User preferences / context:
{preferences}

Available books:
{lines}

Reply with ONLY a comma-separated list of book IDs to recommend, best first. Example: 2, 7, 1"""
    return prompt, RECOMMEND_SYSTEM


def suggest_books_prompt(genres: list[str], limit: int) -> tuple[str, str]:
    """Prompt and system for suggesting well-known books by genre."""
    genre_str = ", ".join(genres[:5])
    prompt = f"""Suggest {limit} well-known books in these genres: {genre_str}.
Reply with one book per line in this exact format: Title by Author (Genre)
Example:
Dune by Frank Herbert (Sci-Fi)
1984 by George Orwell (Fiction)
Do not number the lines. Only output the lines, nothing else."""
    return prompt, SUGGEST_BOOKS_SYSTEM


def suggest_books_similar_prompt(
    book_title: str,
    book_author: str | None,
    book_genre: str | None,
    book_summary: str | None,
    limit: int,
) -> tuple[str, str]:
    """Prompt and system for suggesting well-known books similar to a given book."""
    info = f"Title: {book_title}"
    if book_author:
        info += f", Author: {book_author}"
    if book_genre:
        info += f", Genre: {book_genre}"
    if book_summary and book_summary.strip():
        info += f"\nSummary/context: {book_summary[:400].strip()}"
    prompt = f"""This book: {info}

Suggest {limit} well-known books that readers who liked this book would also enjoy (similar style, theme, or genre). Books can be from any era.
Reply with one book per line in this exact format: Title by Author (Genre)
Example:
Dune by Frank Herbert (Sci-Fi)
Do not number the lines. Only output the lines, nothing else."""
    return prompt, SUGGEST_BOOKS_SYSTEM

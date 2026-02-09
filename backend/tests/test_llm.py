import pytest
from app.llm.mock import MockLLM
from app.llm.base import LLMBackend


@pytest.mark.asyncio
async def test_mock_llm_summarize():
    """Test mock LLM summarization."""
    llm = MockLLM()
    text = "This is a test book content. It has multiple sentences. The book is about testing."
    summary = await llm.summarize(text)
    assert isinstance(summary, str)
    assert len(summary) > 0


@pytest.mark.asyncio
async def test_mock_llm_analyze_sentiment():
    """Test mock LLM sentiment analysis."""
    llm = MockLLM()
    reviews = ["Great book!", "I loved it", "Amazing read"]
    consensus = await llm.analyze_sentiment(reviews)
    assert isinstance(consensus, str)
    assert len(consensus) > 0


@pytest.mark.asyncio
async def test_mock_llm_recommend_for_user():
    """Test mock LLM recommendations for user."""
    llm = MockLLM()
    preferences = "Genres: Fiction (weight 0.8), Science Fiction (weight 0.9)"
    candidates = [
        {"id": 1, "title": "Book 1", "author": "Author 1", "genre": "Fiction"},
        {"id": 2, "title": "Book 2", "author": "Author 2", "genre": "Science Fiction"},
    ]
    recommendations = await llm.recommend_for_user(preferences, candidates, limit=2)
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 2
    assert all(isinstance(r, int) for r in recommendations)


@pytest.mark.asyncio
async def test_mock_llm_recommend_similar():
    """Test mock LLM similar book recommendations."""
    llm = MockLLM()
    book_info = "Test Book by Test Author (Fiction). A great book about testing."
    candidates = [
        {"id": 1, "title": "Similar Book 1", "author": "Author 1", "genre": "Fiction"},
        {"id": 2, "title": "Similar Book 2", "author": "Author 2", "genre": "Fiction"},
    ]
    recommendations = await llm.recommend_similar(book_info, candidates, limit=2)
    assert isinstance(recommendations, list)
    assert len(recommendations) <= 2
    assert all(isinstance(r, int) for r in recommendations)


@pytest.mark.asyncio
async def test_mock_llm_suggest_books_by_genre():
    """Test mock LLM genre-based suggestions."""
    llm = MockLLM()
    genres = ["Fiction", "Science Fiction"]
    suggestions = await llm.suggest_books_by_genre(genres, limit=5)
    assert isinstance(suggestions, list)
    assert len(suggestions) <= 5
    assert all(isinstance(s, dict) for s in suggestions)
    assert all("title" in s and "author" in s for s in suggestions)


@pytest.mark.asyncio
async def test_mock_llm_suggest_books_similar_to():
    """Test mock LLM similar book suggestions."""
    llm = MockLLM()
    suggestions = await llm.suggest_books_similar_to(
        book_title="Test Book",
        book_author="Test Author",
        book_genre="Fiction",
        book_summary="A test book",
        limit=5
    )
    assert isinstance(suggestions, list)
    assert len(suggestions) <= 5
    assert all(isinstance(s, dict) for s in suggestions)
    assert all("title" in s and "author" in s for s in suggestions)

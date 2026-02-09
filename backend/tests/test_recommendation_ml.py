import pytest
from app.recommendation_ml import (
    similar_books,
    collaborative_scores,
    content_similarity_to_user_books,
    build_book_matrix,
)
from app.models import Book


@pytest.fixture
def sample_books():
    """Create sample books for testing."""
    return [
        Book(id=1, title="Fiction Book", author="Author A", genre="Fiction", summary="A fiction story"),
        Book(id=2, title="Science Fiction Book", author="Author B", genre="Science Fiction", summary="A sci-fi story"),
        Book(id=3, title="Another Fiction Book", author="Author A", genre="Fiction", summary="Another fiction story"),
        Book(id=4, title="Mystery Book", author="Author C", genre="Mystery", summary="A mystery story"),
    ]


def test_build_book_matrix(sample_books):
    """Test building TF-IDF matrix from books."""
    ids, matrix = build_book_matrix(sample_books)
    assert len(ids) == len(sample_books)
    assert matrix is not None
    assert matrix.shape[0] == len(sample_books)


def test_similar_books(sample_books):
    """Test finding similar books."""
    similar = similar_books(sample_books, book_id=1, limit=3)
    assert isinstance(similar, list)
    assert len(similar) <= 3
    # Should not include the book itself
    similar_ids = [b.id for b, _ in similar]
    assert 1 not in similar_ids


def test_collaborative_scores():
    """Test collaborative filtering scores."""
    borrowed_ids = {1, 2}
    all_borrows = [
        (1, 1),  # User 1 borrowed book 1
        (1, 2),  # User 1 borrowed book 2
        (2, 1),  # User 2 borrowed book 1
        (2, 3),  # User 2 borrowed book 3
        (3, 2),  # User 3 borrowed book 2
        (3, 3),  # User 3 borrowed book 3
    ]
    candidate_ids = {3, 4}

    scores = collaborative_scores(borrowed_ids, all_borrows, candidate_ids)
    assert isinstance(scores, dict)
    assert 3 in scores
    # Book 3 should have a score because user 2 borrowed both book 1 and book 3
    assert scores[3] > 0


def test_content_similarity_to_user_books(sample_books):
    """Test content similarity scoring."""
    borrowed_ids = {1, 3}
    ids, X = build_book_matrix(sample_books)
    scores = content_similarity_to_user_books(sample_books, borrowed_ids, X)
    assert isinstance(scores, dict)
    # Books similar to borrowed books should have higher scores
    assert len(scores) > 0


def test_collaborative_scores_no_overlap():
    """Test collaborative scores when there's no user overlap."""
    borrowed_ids = {1}
    all_borrows = [
        (1, 1),  # User 1 borrowed book 1
        (2, 2),  # User 2 borrowed book 2 (different user)
    ]
    candidate_ids = {2}

    scores = collaborative_scores(borrowed_ids, all_borrows, candidate_ids)
    assert scores.get(2, 0) == 0  # No overlap, should be 0

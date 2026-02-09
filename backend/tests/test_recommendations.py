import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Book, Borrow, UserPreference


@pytest.mark.asyncio
async def test_list_preferences(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user):
    """Test listing user preferences."""
    # Create a preference
    pref = UserPreference(user_id=test_user.id, genre="Fiction", weight=0.8)
    db_session.add(pref)
    await db_session.commit()

    response = await client.get("/preferences", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(p["genre"] == "Fiction" for p in data)


@pytest.mark.asyncio
async def test_set_preference(client: AsyncClient, auth_headers: dict, test_user):
    """Test setting a user preference."""
    response = await client.post(
        "/preferences",
        headers=auth_headers,
        json={
            "genre": "Science Fiction",
            "weight": 0.9
        }
    )
    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_set_preference_update_existing(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user):
    """Test updating an existing preference."""
    pref = UserPreference(user_id=test_user.id, genre="Fiction", weight=0.5)
    db_session.add(pref)
    await db_session.commit()

    response = await client.post(
        "/preferences",
        headers=auth_headers,
        json={
            "genre": "Fiction",
            "weight": 0.9
        }
    )
    assert response.status_code == 200

    # Verify update
    result = await db_session.execute(
        select(UserPreference).where(
            UserPreference.user_id == test_user.id,
            UserPreference.genre == "Fiction"
        )
    )
    updated_pref = result.scalar_one()
    assert updated_pref.weight == 0.9


@pytest.mark.asyncio
async def test_get_recommendations_empty(client: AsyncClient, auth_headers: dict):
    """Test getting recommendations with no preferences or borrows."""
    response = await client.get("/recommendations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_recommendations_with_preferences(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user):
    """Test getting recommendations with preferences."""
    # Create preference
    pref = UserPreference(user_id=test_user.id, genre="Fiction", weight=0.8)
    db_session.add(pref)

    # Create books
    book1 = Book(title="Fiction Book", author="Author", genre="Fiction", added_by_user_id=test_user.id)
    book2 = Book(title="Non-Fiction Book", author="Author", genre="Non-Fiction", added_by_user_id=test_user.id)
    db_session.add_all([book1, book2])
    await db_session.commit()

    response = await client.get("/recommendations?limit=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_recommendations_excludes_borrowed(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user, test_book: Book):
    """Test that recommendations exclude borrowed books."""
    # Borrow a book
    borrow = Borrow(user_id=test_user.id, book_id=test_book.id)
    db_session.add(borrow)
    await db_session.commit()

    response = await client.get("/recommendations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    borrowed_ids = {b["id"] for b in data}
    assert test_book.id not in borrowed_ids


@pytest.mark.asyncio
async def test_get_similar_books(client: AsyncClient, db_session: AsyncSession, test_user, test_book: Book):
    """Test getting similar books."""
    # Create another book
    book2 = Book(
        title="Similar Book",
        author="Author",
        genre=test_book.genre,
        added_by_user_id=test_user.id
    )
    db_session.add(book2)
    await db_session.commit()

    response = await client.get(f"/recommendations/similar/{test_book.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_similar_books_not_found(client: AsyncClient):
    """Test getting similar books for non-existent book."""
    response = await client.get("/recommendations/similar/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_ai_suggestions(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user):
    """Test getting AI suggestions."""
    # Create preferences
    pref = UserPreference(user_id=test_user.id, genre="Fiction", weight=0.8)
    db_session.add(pref)
    await db_session.commit()

    response = await client.get("/recommendations/suggestions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data


@pytest.mark.asyncio
async def test_get_ai_suggestions_no_preferences(client: AsyncClient, auth_headers: dict):
    """Test getting AI suggestions without preferences."""
    response = await client.get("/recommendations/suggestions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["suggestions"] == []


@pytest.mark.asyncio
async def test_get_ai_suggestions_similar_to_book(client: AsyncClient, auth_headers: dict, test_book: Book):
    """Test getting AI suggestions similar to a book."""
    response = await client.get(
        f"/recommendations/suggestions/similar/{test_book.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data


@pytest.mark.asyncio
async def test_get_ai_suggestions_similar_to_book_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting AI suggestions for non-existent book."""
    response = await client.get(
        "/recommendations/suggestions/similar/99999",
        headers=auth_headers
    )
    assert response.status_code == 404

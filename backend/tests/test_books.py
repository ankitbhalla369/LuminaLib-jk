import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Book, Borrow, Review


@pytest.mark.asyncio
async def test_create_book(client: AsyncClient, auth_headers: dict, test_user):
    """Test creating a book."""
    response = await client.post(
        "/books",
        headers=auth_headers,
        data={
            "title": "New Book",
            "author": "New Author",
            "genre": "Science Fiction"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Book"
    assert data["author"] == "New Author"
    assert data["genre"] == "Science Fiction"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_book_with_file(client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
    """Test creating a book with file upload."""
    file_content = b"This is a test file content for the book."
    files = {"file": ("test.txt", file_content, "text/plain")}
    data = {
        "title": "Book with File",
        "author": "Author",
        "genre": "Fiction"
    }
    response = await client.post("/books", headers=auth_headers, files=files, data=data)
    assert response.status_code == 200
    book_data = response.json()
    assert book_data["title"] == "Book with File"
    assert book_data["file_name"] == "test.txt"


@pytest.mark.asyncio
async def test_create_book_unauthorized(client: AsyncClient):
    """Test creating a book without auth."""
    response = await client.post("/books", data={"title": "Test"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_books(client: AsyncClient, test_book: Book):
    """Test listing books."""
    response = await client.get("/books")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert len(data["items"]) >= 1
    assert any(b["id"] == test_book.id for b in data["items"])


@pytest.mark.asyncio
async def test_list_books_pagination(client: AsyncClient, db_session: AsyncSession, test_user):
    """Test pagination in book listing."""
    # Create multiple books
    for i in range(5):
        book = Book(title=f"Book {i}", author="Author", added_by_user_id=test_user.id)
        db_session.add(book)
    await db_session.commit()

    response = await client.get("/books?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["skip"] == 0


@pytest.mark.asyncio
async def test_get_book_detail(client: AsyncClient, test_book: Book):
    """Test getting book details."""
    response = await client.get(f"/books/{test_book.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_book.id
    assert data["title"] == test_book.title
    assert data["author"] == test_book.author
    assert "currently_borrowed_by_me" in data
    assert "can_review" in data


@pytest.mark.asyncio
async def test_get_book_detail_with_user(client: AsyncClient, auth_headers: dict, test_book: Book, test_book_borrowed: Borrow):
    """Test getting book details when user has borrowed it."""
    response = await client.get(f"/books/{test_book.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["currently_borrowed_by_me"] is True
    assert data["can_review"] is True


@pytest.mark.asyncio
async def test_get_book_not_found(client: AsyncClient):
    """Test getting non-existent book."""
    response = await client.get("/books/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_book(client: AsyncClient, auth_headers: dict, test_book: Book):
    """Test updating a book."""
    response = await client.put(
        f"/books/{test_book.id}",
        headers=auth_headers,
        json={
            "title": "Updated Title",
            "author": "Updated Author"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Updated Author"


@pytest.mark.asyncio
async def test_update_book_not_found(client: AsyncClient, auth_headers: dict):
    """Test updating non-existent book."""
    response = await client.put("/books/99999", headers=auth_headers, json={"title": "Test"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_book(client: AsyncClient, auth_headers: dict, db_session: AsyncSession, test_user):
    """Test deleting a book."""
    book = Book(title="To Delete", author="Author", added_by_user_id=test_user.id)
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)

    response = await client.delete(f"/books/{book.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["ok"] is True

    # Verify deleted
    result = await db_session.execute(select(Book).where(Book.id == book.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_borrow_book(client: AsyncClient, auth_headers: dict, test_book: Book):
    """Test borrowing a book."""
    response = await client.post(f"/books/{test_book.id}/borrow", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_borrow_book_already_borrowed(client: AsyncClient, auth_headers: dict, test_book: Book, test_book_borrowed: Borrow):
    """Test borrowing a book that's already borrowed."""
    response = await client.post(f"/books/{test_book.id}/borrow", headers=auth_headers)
    assert response.status_code == 400
    assert "already borrowed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_borrow_book_not_found(client: AsyncClient, auth_headers: dict):
    """Test borrowing non-existent book."""
    response = await client.post("/books/99999/borrow", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_return_book(client: AsyncClient, auth_headers: dict, test_book: Book, test_book_borrowed: Borrow):
    """Test returning a book."""
    response = await client.post(f"/books/{test_book.id}/return", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_return_book_not_borrowed(client: AsyncClient, auth_headers: dict, test_book: Book):
    """Test returning a book that wasn't borrowed."""
    response = await client.post(f"/books/{test_book.id}/return", headers=auth_headers)
    assert response.status_code == 400
    assert "no active borrow" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_review(client: AsyncClient, auth_headers: dict, test_book: Book, test_book_borrowed: Borrow):
    """Test creating a review."""
    response = await client.post(
        f"/books/{test_book.id}/reviews",
        headers=auth_headers,
        json={
            "rating": 5,
            "text": "Great book!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["rating"] == 5
    assert data["text"] == "Great book!"
    assert data["book_id"] == test_book.id


@pytest.mark.asyncio
async def test_create_review_without_borrowing(client: AsyncClient, auth_headers: dict, test_book: Book):
    """Test creating a review without borrowing the book."""
    response = await client.post(
        f"/books/{test_book.id}/reviews",
        headers=auth_headers,
        json={
            "rating": 5,
            "text": "Great book!"
        }
    )
    assert response.status_code == 400
    assert "must borrow" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_review_invalid_rating(client: AsyncClient, auth_headers: dict, test_book: Book, test_book_borrowed: Borrow):
    """Test creating a review with invalid rating."""
    response = await client.post(
        f"/books/{test_book.id}/reviews",
        headers=auth_headers,
        json={
            "rating": 10,  # Invalid, should be 1-5
            "text": "Review"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_analysis(client: AsyncClient, test_book: Book):
    """Test getting book analysis."""
    response = await client.get(f"/books/{test_book.id}/analysis")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "consensus" in data

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.db import Base, get_db
from app.config import settings
from app.models import User, Book, Borrow, Review, UserPreference


# Test database URL - use in-memory SQLite for tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(TEST_DB_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Create all tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database override."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    from app.auth import hash_password
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpassword"),
        full_name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user2(db_session: AsyncSession) -> User:
    """Create a second test user."""
    from app.auth import hash_password
    user = User(
        email="test2@example.com",
        hashed_password=hash_password("testpassword"),
        full_name="Test User 2"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    response = await client.post("/auth/login", json={
        "email": test_user.email,
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_book(db_session: AsyncSession, test_user: User) -> Book:
    """Create a test book."""
    book = Book(
        title="Test Book",
        author="Test Author",
        genre="Fiction",
        added_by_user_id=test_user.id
    )
    db_session.add(book)
    await db_session.commit()
    await db_session.refresh(book)
    return book


@pytest.fixture
async def test_book_borrowed(db_session: AsyncSession, test_user: User, test_book: Book) -> Borrow:
    """Create a borrow record for test book."""
    borrow = Borrow(
        user_id=test_user.id,
        book_id=test_book.id
    )
    db_session.add(borrow)
    await db_session.commit()
    await db_session.refresh(borrow)
    return borrow

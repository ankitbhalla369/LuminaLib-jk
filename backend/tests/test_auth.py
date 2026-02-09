import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    """Test successful user signup."""
    response = await client.post("/auth/signup", json={
        "email": "newuser@example.com",
        "password": "securepassword",
        "full_name": "New User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "password" not in str(data)


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, test_user: User):
    """Test signup with duplicate email fails."""
    response = await client.post("/auth/signup", json={
        "email": test_user.email,
        "password": "password123",
        "full_name": "Another User"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login."""
    response = await client.post("/auth/login", json={
        "email": test_user.email,
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    """Test login with invalid email."""
    response = await client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "password123"
    })
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user: User):
    """Test login with invalid password."""
    response = await client.post("/auth/login", json={
        "email": test_user.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test getting current user info."""
    response = await client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without auth."""
    response = await client.get("/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test updating user profile."""
    response = await client.put("/auth/me", headers=auth_headers, json={
        "full_name": "Updated Name"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_update_profile_partial(client: AsyncClient, auth_headers: dict, test_user: User):
    """Test partial profile update."""
    response = await client.put("/auth/me", headers=auth_headers, json={})
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == test_user.full_name


@pytest.mark.asyncio
async def test_signout(client: AsyncClient, auth_headers: dict):
    """Test signout endpoint."""
    response = await client.post("/auth/signout", headers=auth_headers)
    assert response.status_code == 200
    assert "message" in response.json()

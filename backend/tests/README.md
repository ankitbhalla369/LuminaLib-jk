# Backend Tests

This directory contains comprehensive test suites for the LuminaLib backend API.

## Setup

Install test dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

Run all tests:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=app --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_auth.py
```

Run specific test:

```bash
pytest tests/test_auth.py::test_login_success
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_auth.py` - Authentication endpoint tests
- `test_books.py` - Books CRUD, borrow/return, and review tests
- `test_recommendations.py` - Recommendation engine tests
- `test_auth_utils.py` - Password hashing and JWT token utilities
- `test_storage.py` - Storage backend tests (local storage)
- `test_llm.py` - LLM backend tests (mock LLM)
- `test_recommendation_ml.py` - ML recommendation algorithm tests

## Test Database

Tests use an in-memory SQLite database that is created and destroyed for each test. No external database setup is required.

## Fixtures

Common fixtures available in `conftest.py`:

- `db_session` - Database session
- `client` - Async HTTP test client
- `test_user` - Pre-created test user
- `test_user2` - Second test user
- `auth_headers` - Authentication headers for test user
- `test_book` - Pre-created test book
- `test_book_borrowed` - Borrow record for test book

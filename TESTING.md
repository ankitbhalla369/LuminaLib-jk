# Testing Guide

This document provides an overview of the test coverage for LuminaLib.

## Backend Tests

### Coverage

✅ **Authentication** (`tests/test_auth.py`)
- User signup (success, duplicate email)
- User login (success, invalid credentials)
- Get current user (authenticated, unauthorized)
- Update profile
- Signout

✅ **Books** (`tests/test_books.py`)
- Create book (with/without file upload)
- List books (pagination)
- Get book details (with/without user context)
- Update book
- Delete book
- Borrow book (success, already borrowed, not found)
- Return book (success, not borrowed)
- Create review (success, without borrowing, invalid rating)
- Get book analysis

✅ **Recommendations** (`tests/test_recommendations.py`)
- List user preferences
- Set/update preferences
- Get personalized recommendations
- Get similar books
- Get AI suggestions (by genre, similar to book)
- Recommendations exclude borrowed books

✅ **Utilities**
- Auth utilities (`tests/test_auth_utils.py`) - Password hashing, JWT tokens
- Storage backend (`tests/test_storage.py`) - Local storage operations
- LLM backend (`tests/test_llm.py`) - Mock LLM operations
- Recommendation ML (`tests/test_recommendation_ml.py`) - ML algorithms

### Running Backend Tests

```bash
cd backend
pytest                    # Run all tests
pytest --cov=app          # With coverage
pytest -v                 # Verbose output
pytest tests/test_auth.py # Specific test file
```

## Frontend Tests

### Coverage

✅ **Components**
- `BookCard` - Book card rendering and links
- `ErrorMessage` - Error display
- `LoadingSpinner` - Loading state
- `Nav` - Navigation component
- `BookViewModal` - Book file viewer (PDF/text, pagination)
- `Toaster` - Toast notifications wrapper

✅ **Pages**
- `LoginPage` - Login form and authentication flow

✅ **Utilities**
- `api.ts` - API client (requests, error handling, auth tokens)
- `auth-context.tsx` - Authentication context (login, logout, user state)

### Running Frontend Tests

```bash
cd frontend
npm test                  # Run all tests
npm test -- --watch       # Watch mode
npm test -- --coverage    # With coverage
npm test LoginPage        # Specific test file
```

## Test Infrastructure

### Backend
- **Framework**: pytest with pytest-asyncio
- **Database**: In-memory SQLite (no external DB needed)
- **HTTP Client**: httpx AsyncClient
- **Fixtures**: Shared test fixtures in `conftest.py`

### Frontend
- **Framework**: Jest with React Testing Library
- **Environment**: jsdom
- **Mocking**: Jest mocks for API calls and Next.js router

## Test Coverage Summary

| Area | Backend | Frontend |
|------|---------|----------|
| Authentication | ✅ Complete | ✅ Complete |
| Books CRUD | ✅ Complete | ⚠️ Partial |
| Borrow/Return | ✅ Complete | ⚠️ Partial |
| Reviews | ✅ Complete | ⚠️ Partial |
| Recommendations | ✅ Complete | ⚠️ Partial |
| File Upload | ✅ Complete | ⚠️ Partial |
| Components | N/A | ✅ Complete |
| Pages | N/A | ⚠️ Partial |
| Utilities | ✅ Complete | ✅ Complete |

**Legend:**
- ✅ Complete - All critical paths tested
- ⚠️ Partial - Some tests exist, more coverage possible
- ❌ Missing - No tests

## Adding New Tests

### Backend Test Template

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_feature_name(client: AsyncClient, auth_headers: dict):
    response = await client.get("/endpoint", headers=auth_headers)
    assert response.status_code == 200
    # Add assertions
```

### Frontend Test Template

```typescript
import { render, screen } from '@testing-library/react'
import Component from './Component'

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
})
```

## Continuous Integration

Tests should be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run backend tests
  run: |
    cd backend
    pip install -r requirements.txt
    pytest

- name: Run frontend tests
  run: |
    cd frontend
    npm install
    npm test
```

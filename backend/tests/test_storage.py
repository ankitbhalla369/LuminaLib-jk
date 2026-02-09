import pytest
import tempfile
import os
from io import BytesIO
from app.storage.local import LocalStorage
from app.storage.base import StorageBackend


@pytest.mark.asyncio
async def test_local_storage_put_get():
    """Test local storage put and get operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(root=tmpdir)
        key = "test/file.txt"
        content = b"test content"

        # Put file
        await storage.put(key, BytesIO(content))

        # Get file
        retrieved = await storage.get(key)
        assert retrieved == content


@pytest.mark.asyncio
async def test_local_storage_delete():
    """Test local storage delete operation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(root=tmpdir)
        key = "test/file.txt"
        content = b"test content"

        await storage.put(key, BytesIO(content))
        retrieved = await storage.get(key)
        assert retrieved == content

        await storage.delete(key)
        retrieved = await storage.get(key)
        assert retrieved is None


@pytest.mark.asyncio
async def test_local_storage_nested_paths():
    """Test local storage with nested paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(root=tmpdir)
        key = "books/2024/test.txt"
        content = b"nested content"

        await storage.put(key, BytesIO(content))
        retrieved = await storage.get(key)
        assert retrieved == content


@pytest.mark.asyncio
async def test_local_storage_nonexistent_file():
    """Test getting non-existent file returns None."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(root=tmpdir)
        retrieved = await storage.get("nonexistent/file.txt")
        assert retrieved is None

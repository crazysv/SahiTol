"""Tests for local storage adapter: CRUD, path traversal defense, and size limits."""
import pytest
import tempfile
import shutil
from pathlib import Path
from app.storage.local import LocalStorageAdapter, MAX_MEDIA_BYTES


@pytest.fixture
def temp_storage():
    temp_dir = tempfile.mkdtemp(prefix="sahitol_storage_test_")
    adapter = LocalStorageAdapter(root_dir=temp_dir)
    yield adapter
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_storage_save_and_get(temp_storage):
    test_data = b"image-content-bytes"
    key = temp_storage.save("photo.jpg", test_data)
    assert key.endswith(".jpg")
    assert temp_storage.exists(key) is True

    retrieved = temp_storage.get(key)
    assert retrieved == test_data

    # Clean up delete
    assert temp_storage.delete(key) is True
    assert temp_storage.exists(key) is False


def test_storage_path_traversal_rejection(temp_storage):
    with pytest.raises(ValueError, match="Path traversal"):
        temp_storage._resolve_safe_path("../../../etc/passwd")


def test_storage_size_limit(temp_storage):
    oversized = b"x" * (MAX_MEDIA_BYTES + 100)
    with pytest.raises(ValueError, match="Media exceeds maximum"):
        temp_storage.save("large.jpg", oversized)

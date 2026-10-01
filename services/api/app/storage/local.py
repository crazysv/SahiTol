"""Local filesystem storage adapter with path-traversal protection."""
from pathlib import Path
import os
import uuid
import tempfile
from app.storage.base import StorageAdapter
from app.config import settings

MAX_MEDIA_BYTES = 2 * 1024 * 1024  # 2MB hard upload bound per Techspec


class LocalStorageAdapter(StorageAdapter):
    """Storage adapter using local persistent volume mount."""

    def __init__(self, root_dir: str = None):
        self.root = Path(root_dir or settings.LOCAL_MEDIA_ROOT).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def is_healthy(self) -> bool:
        """Return whether the configured local media root is usable."""
        return self.root.is_dir()

    def _resolve_safe_path(self, storage_key: str) -> Path:
        """Resolve storage key and verify it resides safely inside the root directory."""
        clean_key = storage_key.strip("/\\")
        candidate = (self.root / clean_key).resolve()
        if not candidate.is_relative_to(self.root):
            raise ValueError(f"Path traversal detected for storage key: {storage_key}")
        return candidate

    def save(self, filename: str, data: bytes, content_type: str = "image/jpeg") -> str:
        """Save file bytes safely to local root directory."""
        if len(data) > MAX_MEDIA_BYTES:
            raise ValueError(f"Media exceeds maximum allowed size of {MAX_MEDIA_BYTES} bytes")

        # Sanitize extension
        ext = Path(filename).suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".pdf"]:
            ext = ".jpg"

        # Unique key with random UUID
        storage_key = f"{uuid.uuid4().hex}{ext}"
        target_path = self._resolve_safe_path(storage_key)

        # Atomic write via tempfile in same filesystem
        temp_fd, temp_path = tempfile.mkstemp(dir=self.root, prefix="tmp_media_")
        try:
            with os.fdopen(temp_fd, "wb") as f:
                f.write(data)
            os.replace(temp_path, target_path)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

        return storage_key

    def get(self, storage_key: str) -> bytes:
        """Retrieve file bytes safely."""
        target_path = self._resolve_safe_path(storage_key)
        if not target_path.is_file():
            raise FileNotFoundError(f"Media file not found: {storage_key}")
        return target_path.read_bytes()

    def delete(self, storage_key: str) -> bool:
        """Delete file safely."""
        target_path = self._resolve_safe_path(storage_key)
        if target_path.is_file():
            target_path.unlink()
            return True
        return False

    def exists(self, storage_key: str) -> bool:
        """Check if file exists."""
        try:
            target_path = self._resolve_safe_path(storage_key)
            return target_path.is_file()
        except ValueError:
            return False

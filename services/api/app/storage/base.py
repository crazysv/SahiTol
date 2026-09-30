"""Abstract Storage Adapter interface for media files."""
from abc import ABC, abstractmethod


class StorageAdapter(ABC):
    """Abstract storage adapter for app media attachments."""

    @abstractmethod
    def save(self, filename: str, data: bytes, content_type: str = "image/jpeg") -> str:
        """Save file bytes and return storage key/path."""
        pass

    @abstractmethod
    def get(self, storage_key: str) -> bytes:
        """Retrieve file bytes for storage key."""
        pass

    @abstractmethod
    def delete(self, storage_key: str) -> bool:
        """Delete file by storage key."""
        pass

    @abstractmethod
    def exists(self, storage_key: str) -> bool:
        """Check if file exists."""
        pass

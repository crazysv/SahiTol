"""Storage factory for selecting configured media adapter."""
from app.config import settings
from app.storage.base import StorageAdapter
from app.storage.local import LocalStorageAdapter
from app.storage.supabase import SupabaseStorageAdapter


def get_storage_adapter() -> StorageAdapter:
    """Instantiate and return the configured storage adapter."""
    if settings.STORAGE_BACKEND.lower() == "supabase":
        return SupabaseStorageAdapter()
    return LocalStorageAdapter()

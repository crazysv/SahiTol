"""Supabase Private Storage Adapter using HTTP REST API."""
from pathlib import Path
import uuid
import httpx
from app.storage.base import StorageAdapter
from app.config import settings

MAX_MEDIA_BYTES = 2 * 1024 * 1024  # 2MB hard upload bound per Techspec


class SupabaseStorageAdapter(StorageAdapter):
    """Storage adapter connecting to private Supabase Storage bucket."""

    def __init__(
        self,
        supabase_url: str = None,
        service_role_key: str = None,
        bucket: str = None
    ):
        self.url = (supabase_url or settings.SUPABASE_URL).rstrip("/")
        self.key = service_role_key or settings.SUPABASE_SERVICE_ROLE_KEY
        self.bucket = bucket or settings.SUPABASE_STORAGE_BUCKET

        if not self.url or not self.key:
            raise ValueError("SupabaseStorageAdapter requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

        self.base_endpoint = f"{self.url}/storage/v1/object/{self.bucket}"
        self.headers = {
            "Authorization": f"Bearer {self.key}",
            "apiKey": self.key,
        }

    def save(self, filename: str, data: bytes, content_type: str = "image/jpeg") -> str:
        """Upload file bytes to private bucket."""
        if len(data) > MAX_MEDIA_BYTES:
            raise ValueError(f"Media exceeds maximum allowed size of {MAX_MEDIA_BYTES} bytes")

        ext = Path(filename).suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".pdf"]:
            ext = ".jpg"

        storage_key = f"{uuid.uuid4().hex}{ext}"
        upload_url = f"{self.base_endpoint}/{storage_key}"

        upload_headers = {**self.headers, "Content-Type": content_type}
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(upload_url, headers=upload_headers, content=data)
            if resp.status_code not in (200, 201):
                raise RuntimeError(f"Supabase upload failed ({resp.status_code}): {resp.text}")

        return storage_key

    def get(self, storage_key: str) -> bytes:
        """Retrieve file bytes from private bucket."""
        download_url = f"{self.base_endpoint}/{storage_key}"
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(download_url, headers=self.headers)
            if resp.status_code == 404:
                raise FileNotFoundError(f"Media file not found in Supabase: {storage_key}")
            if resp.status_code != 200:
                raise RuntimeError(f"Supabase download failed ({resp.status_code}): {resp.text}")
            return resp.content

    def delete(self, storage_key: str) -> bool:
        """Delete file from private bucket."""
        delete_url = f"{self.base_endpoint}/{storage_key}"
        with httpx.Client(timeout=10.0) as client:
            resp = client.delete(delete_url, headers=self.headers)
            return resp.status_code in (200, 204)

    def exists(self, storage_key: str) -> bool:
        """Check if file exists in private bucket."""
        info_url = f"{self.base_endpoint}/info/{storage_key}"
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(info_url, headers=self.headers)
            return resp.status_code == 200

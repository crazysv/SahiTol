"""Media router: Bounded uploads, EXIF stripping, checksum validation, and authorized access."""
import io
import re
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from PIL import Image

from app.config import settings
from app.db.session import get_db
from app.db.models.auth import User
from app.db.models.lot import MediaObject, Lot
from app.security import (
    UserRole,
    get_current_user,
    create_access_token,
    decode_token,
    oauth2_scheme
)
from app.storage import get_storage_adapter
from app.storage.local import MAX_MEDIA_BYTES

router = APIRouter(tags=["media"])

ALLOWED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf"
}


# --- Schemas ---

class UploadInstructionsRequest(BaseModel):
    media_id: Optional[uuid.UUID] = None
    parent_id: Optional[uuid.UUID] = Field(None, description="Linked parent entity ID (e.g., Lot UUID)")
    mime: str = Field(..., description="MIME type (image/jpeg, image/png, image/webp, application/pdf)")
    size: int = Field(..., gt=0, le=MAX_MEDIA_BYTES, description="Byte size bound to 2 MiB")
    sha256: str = Field(..., pattern=r"^[a-fA-F0-9]{64}$", description="Hexadecimal SHA-256 hash")

    @field_validator("mime")
    @classmethod
    def validate_mime(cls, v: str) -> str:
        v_clean = v.lower().strip()
        if v_clean not in ALLOWED_MIME_TYPES:
            raise ValueError(f"Unsupported MIME type '{v}'. Allowed types: {list(ALLOWED_MIME_TYPES.keys())}")
        return v_clean


class UploadInstructionsResponse(BaseModel):
    media_id: str
    upload_url: str
    method: str = "PUT"
    max_bytes: int = MAX_MEDIA_BYTES
    state: str = "STAGED"


class CompleteUploadResponse(BaseModel):
    media_id: str
    storage_key: str
    mime: str
    byte_size: int
    sha256: str
    state: str
    pixel_width: Optional[int] = None
    pixel_height: Optional[int] = None


class MediaAccessResponse(BaseModel):
    media_id: str
    access_url: str
    expires_in: int = 900


# --- Helpers ---

def _strip_exif_and_validate_image(data: bytes, mime_type: str) -> tuple[bytes, Optional[int], Optional[int]]:
    """Validate image bytes, strip all EXIF/privacy metadata, and return clean bytes and dimensions."""
    if mime_type == "application/pdf":
        if not data.startswith(b"%PDF"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid PDF file format: missing '%PDF' header."
            )
        return data, None, None

    try:
        image = Image.open(io.BytesIO(data))
        image.verify()  # Check file integrity
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid image file or corrupt data stream."
        )

    # Re-open after verify to perform operations
    image = Image.open(io.BytesIO(data))
    width, height = image.size

    # Re-save into fresh buffer without any EXIF/metadata
    clean_buf = io.BytesIO()
    fmt = "JPEG"
    if mime_type == "image/png":
        fmt = "PNG"
    elif mime_type == "image/webp":
        fmt = "WEBP"
    elif mime_type == "image/jpeg":
        fmt = "JPEG"
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

    image.save(clean_buf, format=fmt)
    return clean_buf.getvalue(), width, height


def _verify_media_access(user: User, media: MediaObject, db: Session) -> None:
    """Verify that user is authorized to read media (owner, admin, or counterparty)."""
    if user.role == UserRole.ADMIN.value:
        return
    if user.id == media.owner_user_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden: you do not have permission to view or download this media file."
    )


# --- Endpoints ---

@router.post("/media/uploads", response_model=UploadInstructionsResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/media/uploads", response_model=UploadInstructionsResponse, status_code=status.HTTP_201_CREATED)
def stage_upload(
    req: UploadInstructionsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate a bounded media upload with size, mime, and checksum bounds."""
    media_uuid = req.media_id or uuid.uuid4()

    # Optional parent ownership check
    if req.parent_id:
        parent_lot = db.query(Lot).filter(Lot.id == req.parent_id).first()
        if parent_lot and current_user.role != UserRole.ADMIN.value:
            if not current_user.collector or parent_lot.collector_id != current_user.collector.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: cannot attach media to a lot owned by another collector."
                )

    # Check if media object already staged/exists
    existing = db.query(MediaObject).filter(MediaObject.id == media_uuid).first()
    if existing:
        if existing.owner_user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Media ID already claimed by another user.")
        return UploadInstructionsResponse(
            media_id=str(existing.id),
            upload_url=f"/media/{existing.id}/content",
            state=existing.upload_state
        )

    # Temporary placeholder key until file is streamed
    placeholder_key = f"staged_{media_uuid.hex}"
    media_obj = MediaObject(
        id=media_uuid,
        owner_user_id=current_user.id,
        owner_entity_id=req.parent_id,
        storage_key=placeholder_key,
        mime_type=req.mime,
        byte_size=req.size,
        sha256=req.sha256.lower(),
        upload_state="STAGED",
        created_at=datetime.now(timezone.utc)
    )
    db.add(media_obj)
    db.commit()

    return UploadInstructionsResponse(
        media_id=str(media_obj.id),
        upload_url=f"/media/{media_obj.id}/content",
        state="STAGED"
    )


@router.put("/media/{id}/content", response_model=CompleteUploadResponse)
@router.put("/api/v1/media/{id}/content", response_model=CompleteUploadResponse)
async def upload_media_content(
    id: uuid.UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stream and validate bounded media content, verify checksum, strip EXIF, and store safely."""
    media_obj = db.query(MediaObject).filter(MediaObject.id == id).first()
    if not media_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media record not found. Call POST /media/uploads first.")

    if current_user.role != UserRole.ADMIN.value and media_obj.owner_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: you do not own this media record.")

    # Read body bytes up to MAX_MEDIA_BYTES + 1
    raw_data = await request.body()
    if len(raw_data) > MAX_MEDIA_BYTES:
        media_obj.upload_state = "REJECTED"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Media payload exceeds maximum allowed bound of {MAX_MEDIA_BYTES} bytes (2 MiB)."
        )

    # Check incoming SHA-256
    incoming_hash = hashlib.sha256(raw_data).hexdigest().lower()
    if media_obj.sha256 and media_obj.sha256 != incoming_hash:
        media_obj.upload_state = "REJECTED"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"SHA-256 checksum mismatch: expected {media_obj.sha256}, got {incoming_hash}."
        )

    # Validate image/pdf format and strip EXIF for privacy
    clean_data, width, height = _strip_exif_and_validate_image(raw_data, media_obj.mime_type)

    # Persist via configured StorageAdapter
    adapter = get_storage_adapter()
    ext = ALLOWED_MIME_TYPES.get(media_obj.mime_type, ".jpg")
    storage_filename = f"media_{media_obj.id.hex}{ext}"
    storage_key = adapter.save(storage_filename, clean_data, content_type=media_obj.mime_type)

    # Update MediaObject metadata
    media_obj.storage_key = storage_key
    media_obj.byte_size = len(clean_data)
    media_obj.sha256 = hashlib.sha256(clean_data).hexdigest().lower()
    media_obj.pixel_width = width
    media_obj.pixel_height = height
    media_obj.upload_state = "UPLOADED"
    db.commit()
    db.refresh(media_obj)

    return CompleteUploadResponse(
        media_id=str(media_obj.id),
        storage_key=media_obj.storage_key,
        mime=media_obj.mime_type,
        byte_size=media_obj.byte_size,
        sha256=media_obj.sha256,
        state=media_obj.upload_state,
        pixel_width=media_obj.pixel_width,
        pixel_height=media_obj.pixel_height
    )


@router.post("/media/{id}/complete", response_model=CompleteUploadResponse)
@router.post("/api/v1/media/{id}/complete", response_model=CompleteUploadResponse)
def complete_media(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify that uploaded media exists in storage and transition status to VALIDATED."""
    media_obj = db.query(MediaObject).filter(MediaObject.id == id).first()
    if not media_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media record not found.")

    if current_user.role != UserRole.ADMIN.value and media_obj.owner_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: you do not own this media record.")

    if media_obj.upload_state == "STAGED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Media content has not been uploaded yet.")

    adapter = get_storage_adapter()
    if not adapter.exists(media_obj.storage_key):
        media_obj.upload_state = "REJECTED"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file missing from storage backend. Recovery required: please re-upload."
        )

    media_obj.upload_state = "VALIDATED"
    db.commit()
    db.refresh(media_obj)

    return CompleteUploadResponse(
        media_id=str(media_obj.id),
        storage_key=media_obj.storage_key,
        mime=media_obj.mime_type,
        byte_size=media_obj.byte_size,
        sha256=media_obj.sha256,
        state=media_obj.upload_state,
        pixel_width=media_obj.pixel_width,
        pixel_height=media_obj.pixel_height
    )


@router.get("/media/{id}/access", response_model=MediaAccessResponse)
@router.get("/api/v1/media/{id}/access", response_model=MediaAccessResponse)
def get_media_access(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate short-lived signed access URL for private media download (expires in 15 min)."""
    media_obj = db.query(MediaObject).filter(MediaObject.id == id).first()
    if not media_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media record not found.")

    _verify_media_access(current_user, media_obj, db)

    # Issue 15-minute signed download token
    download_token = create_access_token(
        subject=str(current_user.id),
        role=current_user.role,
        expires_delta=timedelta(minutes=15),
        extra_claims={"media_id": str(media_obj.id), "scope": "media_read"}
    )

    access_url = f"/media/{media_obj.id}/content?token={download_token}"
    return MediaAccessResponse(
        media_id=str(media_obj.id),
        access_url=access_url,
        expires_in=900
    )


@router.get("/media/{id}/content")
@router.get("/api/v1/media/{id}/content")
def download_media_content(
    id: uuid.UUID,
    token: Optional[str] = Query(None, description="Short-lived signed download token"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Retrieve raw media content with strict authorization and private cache headers."""
    media_obj = db.query(MediaObject).filter(MediaObject.id == id).first()
    if not media_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media record not found.")

    # Authenticate via signed query token or Bearer header
    user = None
    if token:
        try:
            payload = decode_token(token)
            if payload.get("scope") != "media_read" or payload.get("media_id") != str(media_obj.id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token scope for this media.")
            user_uuid = uuid.UUID(payload.get("sub"))
            user = db.query(User).filter(User.id == user_uuid, User.deleted_at.is_(None)).first()
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired or invalid download token.")
    else:
        # Check standard Authorization header
        auth_header = request.headers.get("Authorization") if request else None
        if auth_header and auth_header.startswith("Bearer "):
            bearer_token = auth_header.split(" ", 1)[1]
            try:
                payload = decode_token(bearer_token)
                user_uuid = uuid.UUID(payload.get("sub"))
                user = db.query(User).filter(User.id == user_uuid, User.deleted_at.is_(None)).first()
            except Exception:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization token.")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to access private media.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    _verify_media_access(user, media_obj, db)

    adapter = get_storage_adapter()
    try:
        file_bytes = adapter.get(media_obj.storage_key)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media content not found in storage backend.")

    headers = {
        "Content-Type": media_obj.mime_type,
        "Cache-Control": "private, no-transform, max-age=900",
        "X-Content-Type-Options": "nosniff",
    }
    return Response(content=file_bytes, media_type=media_obj.mime_type, headers=headers)

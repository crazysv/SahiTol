"""Authentication router: Phone/PIN registration, login, session rotation, and isolated demo profiles."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.db.models.auth import User, AuthSession
from app.db.models.collector import Collector
from app.db.models.facility import FacilityUser, Region
from app.rate_limiter import phone_limiter, ip_limiter
from app.security import (
    UserRole,
    normalize_phone,
    mask_phone,
    hash_pin,
    verify_pin,
    hash_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    require_roles,
    check_demo_isolation
)

router = APIRouter(tags=["auth"])


# --- Request & Response Schemas ---

class RegisterRequest(BaseModel):
    phone: str = Field(..., description="Indian 10-digit mobile number")
    pin: str = Field(..., min_length=4, max_length=6, description="4-6 digit numeric PIN")
    alias: Optional[str] = Field(None, max_length=100)
    preferred_language: str = Field("hi", description="Preferred language (hi, mr, en)")
    region_id: Optional[str] = Field(None, max_length=50)
    general_area: Optional[str] = Field(None, max_length=200, description="Coarse neighborhood/locality only; no exact home address")
    device_id: Optional[str] = Field("collector-device", max_length=100)
    consent_version: str = Field("v1.0", max_length=50)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        try:
            return normalize_phone(v)
        except ValueError as e:
            raise ValueError(str(e))

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, v: str) -> str:
        if not v.isdigit() or not (4 <= len(v) <= 6):
            raise ValueError("PIN must be 4 to 6 numeric digits.")
        return v

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v not in {"hi", "mr", "en"}:
            raise ValueError("Language must be 'hi', 'mr', or 'en'.")
        return v


class LoginRequest(BaseModel):
    phone: str = Field(..., description="Indian 10-digit mobile number")
    pin: str = Field(..., min_length=4, max_length=6, description="4-6 digit numeric PIN")
    device_id: Optional[str] = Field("client-device", max_length=100)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        try:
            return normalize_phone(v)
        except ValueError as e:
            raise ValueError(str(e))


class DemoLoginRequest(BaseModel):
    role: UserRole = Field(UserRole.COLLECTOR, description="Demo role (COLLECTOR, RECYCLER, ADMIN)")
    persona_id: str = Field("demo_collector_01", max_length=100, description="Demo persona identifier")
    device_id: Optional[str] = Field("demo-device", max_length=100)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Rotating refresh token")
    device_id: Optional[str] = Field(None, max_length=100)


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: str
    is_demo: bool
    collector_id: Optional[str] = None


class CollectorProfileResponse(BaseModel):
    id: str
    display_alias: Optional[str]
    preferred_language: str
    region_id: Optional[str]
    general_area: Optional[str]
    consent_version: str
    version: int


class FacilityMembershipResponse(BaseModel):
    facility_id: str
    membership_role: str
    active: bool


class UserMeResponse(BaseModel):
    id: str
    phone_masked: str
    role: str
    account_state: str
    is_demo: bool
    collector: Optional[CollectorProfileResponse] = None
    facilities: List[FacilityMembershipResponse] = []


class CollectorUpdateRequest(BaseModel):
    alias: Optional[str] = Field(None, max_length=100)
    preferred_language: Optional[str] = Field(None, description="Preferred language (hi, mr, en)")
    region_id: Optional[str] = Field(None, max_length=50)
    general_area: Optional[str] = Field(None, max_length=200)
    expected_version: int = Field(..., description="Optimistic locking version")

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in {"hi", "mr", "en"}:
            raise ValueError("Language must be 'hi', 'mr', or 'en'.")
        return v


# --- Helper Methods ---

def _build_token_response(user: User, device_id: str, db: Session, collector_id: Optional[str] = None) -> TokenResponse:
    """Generate access/refresh tokens, record AuthSession in database, and return TokenResponse."""
    now = datetime.now(timezone.utc)
    access_token = create_access_token(
        subject=str(user.id),
        role=user.role,
        is_demo=user.is_demo
    )
    refresh_token = create_refresh_token(
        subject=str(user.id),
        role=user.role,
        device_id=device_id,
        is_demo=user.is_demo
    )

    # Persist session with SHA-256 token hash
    session_record = AuthSession(
        user_id=user.id,
        device_id=device_id,
        refresh_token_hash=hash_token(refresh_token),
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        last_seen_at=now,
        created_at=now
    )
    db.add(session_record)
    db.commit()

    cid = collector_id
    if cid is None and user.collector:
        cid = str(user.collector.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        role=user.role,
        is_demo=user.is_demo,
        collector_id=cid
    )


# --- Endpoint Implementations ---

@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Online first activation for collectors. Enforces COLLECTOR role and creates linked profile."""
    # Check if phone already registered
    existing_user = db.query(User).filter(User.phone_normalized == req.phone).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number is already registered. Please log in with your PIN."
        )

    now = datetime.now(timezone.utc)
    hashed_pin = hash_pin(req.pin)

    # Create User with explicit COLLECTOR role (self-registration cannot grant ADMIN/RECYCLER)
    new_user = User(
        phone_normalized=req.phone,
        pin_hash=hashed_pin,
        role=UserRole.COLLECTOR.value,
        account_state="ACTIVE",
        is_demo=False,
        version=1,
        created_at=now,
        updated_at=now
    )
    db.add(new_user)
    db.flush()

    # Create Collector profile
    new_collector = Collector(
        user_id=new_user.id,
        display_alias=req.alias,
        preferred_language=req.preferred_language,
        region_id=req.region_id,
        general_area=req.general_area,
        consent_version=req.consent_version,
        version=1,
        created_at=now,
        updated_at=now
    )
    db.add(new_collector)
    db.flush()

    device_id = req.device_id or "collector-device"
    return _build_token_response(new_user, device_id, db, collector_id=str(new_collector.id))


@router.post("/auth/login", response_model=TokenResponse)
@router.post("/api/v1/auth/login", response_model=TokenResponse)
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate any provisioned role using phone and PIN with rate-limiting protection."""
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Check brute-force lockouts
    is_phone_locked, phone_retry = phone_limiter.is_locked(req.phone)
    if is_phone_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts for this phone number. Please try again in {phone_retry} seconds.",
            headers={"Retry-After": str(phone_retry)}
        )

    is_ip_locked, ip_retry = ip_limiter.is_locked(client_ip)
    if is_ip_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts from this network. Please try again in {ip_retry} seconds.",
            headers={"Retry-After": str(ip_retry)}
        )

    user = db.query(User).filter(User.phone_normalized == req.phone, User.deleted_at.is_(None)).first()

    # Generic invalid credentials error to prevent phone enumeration
    if not user or user.account_state != "ACTIVE" or not verify_pin(req.pin, user.pin_hash):
        _, phone_retry = phone_limiter.record_failure(req.phone)
        _, ip_retry = ip_limiter.record_failure(client_ip)
        retry_time = max(phone_retry, ip_retry)
        headers = {"WWW-Authenticate": "Bearer"}
        if retry_time > 0:
            headers["Retry-After"] = str(retry_time)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or PIN.",
            headers=headers
        )

    # Success: reset rate limit counters
    phone_limiter.record_success(req.phone)
    ip_limiter.record_success(client_ip)

    device_id = req.device_id or "client-device"
    return _build_token_response(user, device_id, db)


@router.post("/auth/demo", response_model=TokenResponse)
@router.post("/api/v1/auth/demo", response_model=TokenResponse)
def demo_login(req: DemoLoginRequest, db: Session = Depends(get_db)):
    """Isolated demo authentication without SMS dependency."""
    if not settings.DEMO_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Isolated demo access is disabled in this environment."
        )

    persona = req.persona_id.strip().lower()
    demo_phone = f"demo_{req.role.value.lower()}_{persona}"

    user = db.query(User).filter(User.phone_normalized == demo_phone).first()
    if not user:
        now = datetime.now(timezone.utc)
        user = User(
            phone_normalized=demo_phone,
            pin_hash=hash_pin("1234"),
            role=req.role.value,
            account_state="ACTIVE",
            is_demo=True,
            version=1,
            created_at=now,
            updated_at=now
        )
        db.add(user)
        db.flush()

        if req.role == UserRole.COLLECTOR:
            # A fresh hosted demo database may not yet have run reference-data
            # seeding.  The isolated demo identity must bootstrap its own minimal
            # region instead of failing login on that deployment prerequisite.
            if not db.query(Region).filter(Region.id == "DELHI_NCR").first():
                db.add(Region(id="DELHI_NCR", name="Delhi-NCR", state_code="DL", kind="METRO"))
                db.flush()
            alias_name = persona.replace("_", " ").title()
            collector = Collector(
                user_id=user.id,
                display_alias=f"Demo {alias_name}",
                preferred_language="hi",
                region_id="DELHI_NCR",
                general_area="Mayapuri Scrap Yard (Demo)",
                consent_version="v1.0",
                version=1,
                created_at=now,
                updated_at=now
            )
            db.add(collector)
        db.commit()
        db.refresh(user)

    device_id = req.device_id or "demo-device"
    return _build_token_response(user, device_id, db)


@router.post("/auth/refresh", response_model=TokenResponse)
@router.post("/api/v1/auth/refresh", response_model=TokenResponse)
def refresh_session(req: RefreshRequest, db: Session = Depends(get_db)):
    """Rotating refresh token exchange with replay attack detection."""
    try:
        payload = decode_token(req.refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please re-authenticate."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    if payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: refresh token required."
        )

    incoming_hash = hash_token(req.refresh_token)
    session_record = db.query(AuthSession).filter(AuthSession.refresh_token_hash == incoming_hash).first()

    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or token unrecognized."
        )

    now = datetime.now(timezone.utc)

    # Replay attack detection: if a revoked refresh token is presented again
    if session_record.revoked_at is not None:
        # Revoke all active sessions for this user as a safeguard against stolen tokens
        db.query(AuthSession).filter(
            AuthSession.user_id == session_record.user_id,
            AuthSession.revoked_at.is_(None)
        ).update({"revoked_at": now})
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security violation: revoked refresh token reused (replay detected). All sessions terminated."
        )

    def _ensure_utc(dt: datetime) -> datetime:
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

    # Expiry verification
    if _ensure_utc(session_record.expires_at) < now:
        session_record.revoked_at = now
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired. Please re-authenticate."
        )

    user = db.query(User).filter(User.id == session_record.user_id, User.deleted_at.is_(None)).first()
    if not user or user.account_state != "ACTIVE":
        session_record.revoked_at = now
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive or disabled."
        )

    # Rotate session: revoke old session and issue new tokens
    session_record.revoked_at = now
    device_id = req.device_id or session_record.device_id

    return _build_token_response(user, device_id, db)


@router.post("/auth/logout")
@router.post("/api/v1/auth/logout")
def logout(
    req: LogoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke session. Client offline outbox data is preserved locally by client design."""
    now = datetime.now(timezone.utc)
    if req.refresh_token:
        r_hash = hash_token(req.refresh_token)
        db.query(AuthSession).filter(
            AuthSession.user_id == current_user.id,
            AuthSession.refresh_token_hash == r_hash
        ).update({"revoked_at": now})
    else:
        # Revoke all active sessions for this user if no specific token provided
        db.query(AuthSession).filter(
            AuthSession.user_id == current_user.id,
            AuthSession.revoked_at.is_(None)
        ).update({"revoked_at": now})

    db.commit()
    return {"status": "ok", "message": "Successfully logged out."}


@router.get("/auth/me", response_model=UserMeResponse)
@router.get("/api/v1/auth/me", response_model=UserMeResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve authenticated user identity, role, masked phone, and profile without leaking PII."""
    collector_data = None
    if current_user.collector:
        c = current_user.collector
        collector_data = CollectorProfileResponse(
            id=str(c.id),
            display_alias=c.display_alias,
            preferred_language=c.preferred_language,
            region_id=c.region_id,
            general_area=c.general_area,
            consent_version=c.consent_version,
            version=c.version
        )

    facilities_data = []
    facility_users = db.query(FacilityUser).filter(
        FacilityUser.user_id == current_user.id,
        FacilityUser.active == True
    ).all()
    for fu in facility_users:
        facilities_data.append(FacilityMembershipResponse(
            facility_id=str(fu.facility_id),
            membership_role=fu.membership_role,
            active=fu.active
        ))

    return UserMeResponse(
        id=str(current_user.id),
        phone_masked=mask_phone(current_user.phone_normalized),
        role=current_user.role,
        account_state=current_user.account_state,
        is_demo=current_user.is_demo,
        collector=collector_data,
        facilities=facilities_data
    )


# --- Collector Profile Endpoints ---

@router.get("/collectors/me", response_model=CollectorProfileResponse)
@router.get("/api/v1/collectors/me", response_model=CollectorProfileResponse)
def get_collector_me(
    current_user: User = Depends(require_roles(UserRole.COLLECTOR)),
    db: Session = Depends(get_db)
):
    """Retrieve current collector's own profile."""
    collector = current_user.collector
    if not collector:
        raise HTTPException(status_code=404, detail="Collector profile not found.")
    return CollectorProfileResponse(
        id=str(collector.id),
        display_alias=collector.display_alias,
        preferred_language=collector.preferred_language,
        region_id=collector.region_id,
        general_area=collector.general_area,
        consent_version=collector.consent_version,
        version=collector.version
    )


@router.patch("/collectors/me", response_model=CollectorProfileResponse)
@router.patch("/api/v1/collectors/me", response_model=CollectorProfileResponse)
def update_collector_me(
    req: CollectorUpdateRequest,
    current_user: User = Depends(require_roles(UserRole.COLLECTOR)),
    db: Session = Depends(get_db)
):
    """Update current collector's profile with optimistic locking (expected_version)."""
    collector = current_user.collector
    if not collector:
        raise HTTPException(status_code=404, detail="Collector profile not found.")

    if collector.version != req.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version conflict: profile version is {collector.version}, but expected {req.expected_version}."
        )

    if req.alias is not None:
        collector.display_alias = req.alias
    if req.preferred_language is not None:
        collector.preferred_language = req.preferred_language
    if req.region_id is not None:
        collector.region_id = req.region_id
    if req.general_area is not None:
        collector.general_area = req.general_area

    collector.version += 1
    collector.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(collector)

    return CollectorProfileResponse(
        id=str(collector.id),
        display_alias=collector.display_alias,
        preferred_language=collector.preferred_language,
        region_id=collector.region_id,
        general_area=collector.general_area,
        consent_version=collector.consent_version,
        version=collector.version
    )

"""Security utilities: Argon2id PIN hashing, JWT issuance, role and object authorization."""
import re
import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional, Sequence
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db

ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,  # 64 MiB
    parallelism=2,
    hash_len=32,
    salt_len=16
)

oauth2_scheme = HTTPBearer(auto_error=False)


class UserRole(str, Enum):
    COLLECTOR = "COLLECTOR"
    RECYCLER = "RECYCLER"
    ADMIN = "ADMIN"


def normalize_phone(phone: str) -> str:
    """Normalize Indian phone numbers to 10 digits starting with 6-9."""
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    if cleaned.startswith("91") and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith("0") and len(cleaned) == 11:
        cleaned = cleaned[1:]
    
    if not re.match(r"^[6-9]\d{9}$", cleaned):
        raise ValueError("Invalid phone number: must be a 10-digit Indian mobile number starting with 6, 7, 8, or 9.")
    return cleaned


def mask_phone(phone: str) -> str:
    """Mask phone number for safe display without revealing PII (e.g., ******1234)."""
    if len(phone) >= 4:
        return f"{'*' * (len(phone) - 4)}{phone[-4:]}"
    return "****"


def hash_pin(pin: str, pepper: Optional[str] = None) -> str:
    """Hash PIN using Argon2id with server-side pepper and unique random salt."""
    if not re.match(r"^\d{4,6}$", pin):
        raise ValueError("PIN must be 4 to 6 numeric digits.")
    effective_pepper = pepper if pepper is not None else settings.PIN_PEPPER
    salted = f"{pin}:{effective_pepper}"
    return ph.hash(salted)


def verify_pin(plain_pin: str, hashed_pin: str, pepper: Optional[str] = None) -> bool:
    """Verify PIN against Argon2id hash."""
    effective_pepper = pepper if pepper is not None else settings.PIN_PEPPER
    salted = f"{plain_pin}:{effective_pepper}"
    try:
        return ph.verify(hashed_pin, salted)
    except (VerifyMismatchError, VerificationError, Exception):
        return False


def hash_token(token: str) -> str:
    """Compute SHA-256 hash of a refresh token for safe storage in auth_sessions."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(
    subject: str,
    role: UserRole | str,
    is_demo: bool = False,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """Generate a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    role_str = role.value if isinstance(role, UserRole) else str(role)

    to_encode: Dict[str, Any] = {
        "sub": subject,
        "role": role_str,
        "is_demo": is_demo,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": settings.APP_NAME,
        "token_type": "access",
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded


def create_refresh_token(
    subject: str,
    role: UserRole | str,
    device_id: Optional[str] = "default-device",
    is_demo: bool = False,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a signed JWT refresh token with unique jti and device scoping."""
    now = datetime.now(timezone.utc)
    effective_device_id = device_id or "default-device"
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    role_str = role.value if isinstance(role, UserRole) else str(role)

    to_encode: Dict[str, Any] = {
        "sub": subject,
        "role": role_str,
        "device_id": effective_device_id,
        "is_demo": is_demo,
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": settings.APP_NAME,
        "token_type": "refresh",
    }

    encoded = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token claims."""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        issuer=settings.APP_NAME
    )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """FastAPI dependency to extract and authenticate current user from Bearer access token."""
    from app.db.models.auth import User  # Late import to prevent circular dependencies

    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired. Please refresh session.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: access token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(sub)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_uuid, User.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.account_state != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.account_state.lower()}."
        )

    return user


def require_roles(*allowed_roles: UserRole | str | list | set | tuple):
    """Dependency factory checking that current user has one of the allowed roles."""
    flat_roles = []
    for r in allowed_roles:
        if isinstance(r, (list, set, tuple)):
            flat_roles.extend(r)
        else:
            flat_roles.append(r)
    role_values = {r.value if isinstance(r, UserRole) else str(r) for r in flat_roles}

    def role_checker(user=Depends(get_current_user)):
        if user.role not in role_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: role '{user.role}' lacks permission for this resource."
            )
        return user

    return role_checker



def check_object_ownership(current_user, resource_user_id: uuid.UUID) -> None:
    """Verify that current user owns the resource or has ADMIN role."""
    if current_user.role == UserRole.ADMIN.value:
        return
    if current_user.id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: you do not have permission to access or modify this object."
        )


def check_demo_isolation(current_user, resource_is_demo: bool) -> None:
    """Enforce strict boundary between demo profiles and live production data."""
    if current_user.is_demo and not resource_is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo accounts are restricted from accessing or mutating production records."
        )
    if not current_user.is_demo and resource_is_demo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Production accounts cannot directly manipulate demo records."
        )

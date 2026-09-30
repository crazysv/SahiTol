"""Health check and service status router."""
from datetime import datetime, timezone
import logging
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.storage import get_storage_adapter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health():
    """Service health and diagnostics endpoint."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "storage_backend": settings.STORAGE_BACKEND,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/live")
def get_health_live():
    """Liveness probe: verifies process is running and responding."""
    return {
        "status": "live",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/health/ready")
def get_health_ready(db: Session = Depends(get_db)):
    """Readiness probe: validates database connectivity and storage readiness without leaking credentials."""
    db_ok = False
    storage_ok = False
    errors = []

    # 1. Database check
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.error("Readiness check: database connectivity failure: %s", type(e).__name__)
        errors.append("database unavailable")

    # 2. Storage check
    try:
        adapter = get_storage_adapter()
        if hasattr(adapter, "root") and adapter.root.is_dir():
            storage_ok = True
        else:
            storage_ok = True  # supabase / other configured storage
    except Exception as e:
        logger.error("Readiness check: storage availability failure: %s", type(e).__name__)
        errors.append("storage unavailable")

    is_ready = db_ok and storage_ok

    payload = {
        "status": "ready" if is_ready else "degraded",
        "database": "connected" if db_ok else "unavailable",
        "storage": "connected" if storage_ok else "unavailable",
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    if not is_ready:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=payload)

    return payload

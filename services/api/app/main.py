"""SahiTol FastAPI Application Factory."""
import logging
import re
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

logger = logging.getLogger("sahitol.access")
from app.routers import (
    health,
    auth,
    media,
    lots,
    prices,
    recyclers,
    facilities,
    handovers,
    payments,
    admin,
    sync,
    materials,
    reference,
    trade,
    economics,
    exports
)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="SahiTol backend API for offline scrap collectors, indicative prices, formal recyclers and handovers."
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def correlation_and_access_log_middleware(request: Request, call_next):
        # Extract or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or request.headers.get("X-Request-ID")
        if not correlation_id or not re.match(r"^[a-zA-Z0-9_\-\.]{8,64}$", correlation_id):
            correlation_id = uuid.uuid4().hex

        request.state.correlation_id = correlation_id
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "Unhandled error: correlation_id=%s method=%s path=%s duration_ms=%.2f error=%s",
                correlation_id, request.method, request.url.path, duration_ms, type(exc).__name__
            )
            raise exc

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Request-ID"] = correlation_id

        # Redact/mask client IP
        client_host = request.client.host if request.client else "unknown"
        if "." in client_host:
            parts = client_host.split(".")
            if len(parts) == 4:
                client_host = f"{parts[0]}.{parts[1]}.*.*"

        log_msg = (
            f"correlation_id={correlation_id} method={request.method} path={request.url.path} "
            f"status={response.status_code} duration_ms={duration_ms} client={client_host}"
        )
        if response.status_code >= 400:
            logger.warning("HTTP error response: %s", log_msg)
        else:
            logger.info("HTTP access: %s", log_msg)

        return response

    # Register routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(media.router)
    app.include_router(materials.router)
    app.include_router(materials.safety_router)
    app.include_router(reference.router)
    app.include_router(lots.router)
    app.include_router(prices.router)
    app.include_router(facilities.router)
    app.include_router(recyclers.router)
    app.include_router(handovers.router)
    app.include_router(payments.router)
    app.include_router(admin.router)
    app.include_router(sync.router)
    app.include_router(trade.router)
    app.include_router(economics.router)
    app.include_router(exports.router)

    @app.get("/")
    def root():
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
            "problem": "SIH26229"
        }

    return app


app = create_app()

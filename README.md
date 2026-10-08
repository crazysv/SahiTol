# SahiTol | सही तोल

**Fair weight. Transparent price. Confirmed handover.**

SahiTol is an offline-first prototype for informal e-waste collectors. It helps a collector record a material lot, compare indicative prices, find suitable recycling destinations, document a handover on two devices, and record payment status without confusing a locally saved record with a completed sale.

> Built for SIH26229 — *Kabadiwala Connect: Bringing the Informal Collector into the Formal Recycling Chain*.

## What it includes

- **Collector Android app:** Kotlin, Jetpack Compose, Room, WorkManager, CameraX, QR, offline-first outbox, and on-device LiteRT classification.
- **Recycler console:** React/Vite interface for requests, quotes, QR-assisted receipt confirmation, and history/export workflows.
- **Admin console:** source-aware price moderation, facility and taxonomy maintenance, traceability, and data-quality review.
- **FastAPI platform:** role-scoped API, PostgreSQL/PostGIS schema, append-only events, idempotent sync, private media adapter, and generated exports.
- **Language and safety support:** Hindi and Marathi offline audio, material aliases, clear safety guidance, and a separate battery route.

## Core workflow

```text
Capture lot → save locally → synchronize → request offer → accept terms
       → create QR handover → recycler confirms receipt → record payment
```

Each stage is deliberately distinct: **saved locally ≠ synchronized ≠ recycler confirmed ≠ payment acknowledged**.

## Architecture

| Surface | Implementation |
| --- | --- |
| Collector | Native Android — Kotlin, Compose, Room, WorkManager, LiteRT |
| API | FastAPI, SQLAlchemy, Alembic, PostgreSQL/PostGIS |
| Recycler/Admin web | React, Vite, TypeScript, Tailwind |
| Local runtime | Docker Compose with PostGIS and local media volume |
| Hosted media design | Private storage adapter; no public collector-photo URLs |

## Repository layout

```text
apps/android/      Collector Android application
apps/web/          Recycler and admin web console
services/api/      FastAPI application, migrations, and API tests
data/curated/      Versioned demo/reference data and model artifacts
infra/             Docker images, Compose stack, and PostGIS initialization
scripts/           Data, validation, backup, and maintenance tools
```

## Run locally

### Full stack with Docker

```bash
docker compose -f infra/docker-compose.yml up --build
```

This starts PostGIS, the API on `http://localhost:8000`, and the web console on `http://localhost:5173`.

### Individual services

```bash
# API
cd services/api
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload

# Web
cd apps/web
npm ci
npm run dev

# Android
# Open apps/android in Android Studio, then run on a device or emulator.
```

Copy `services/api/.env.example` before configuring non-demo services. Never commit credentials, signing keys, or runtime media.

## Verification

The CI workflow runs documentation integrity checks, the FastAPI test suite, web typecheck/tests/production build, and Android unit tests.

```bash
python scripts/check_docs.py
python scripts/test_doc_integrity.py

# From the repository root
PYTHONPATH="services/api:." pytest services/api/tests

cd apps/web && npm ci && npm run typecheck && npm run test && npm run build
cd ../android && ./gradlew test
```

## Important boundaries

- The classifier is advisory; a collector can always select a material manually.
- Prices are indicative observations, not guaranteed offers or income claims.
- A Digital Handover Record is not an EPR certificate and does not prove physical recycling.
- Payments are recorded assertions; SahiTol does not move money or verify bank settlement.
- Batteries follow a distinct route; the product does not provide dismantling or chemical-extraction instructions.
- This prototype uses secondary research and simulated demo data. Required collector fieldwork remains unmet.

## Contributing

Keep changes scoped, test the affected surface, and preserve the product’s safety, privacy, provenance, and offline-state boundaries. Avoid committing generated builds, `node_modules`, virtual environments, secrets, local media, or device-specific configuration.

---

SahiTol is a prototype, not a certified recycling, compliance, or payment-settlement platform.

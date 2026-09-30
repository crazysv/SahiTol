# SahiTol Backend API Service

FastAPI service powering the SahiTol platform: offline sync endpoints, indicative pricing (`PRICE_V1`), formal recycler matching (`MATCH_V1`), canonical handover hashing (`SAHITOL-JCS-1`), and data quality rules (`QUALITY_V1`).

## Tech Stack
- **Framework**: FastAPI (Pydantic v2, Python 3.10+)
- **Database**: PostgreSQL 16 + PostGIS 3.4 via SQLAlchemy 2.0 and GeoAlchemy2
- **Auth**: Phone + 4-6 digit PIN with Argon2id hashing and JWT access/refresh tokens
- **Storage**: Storage adapter supporting local Docker volume mounts and hosted private Supabase Storage
- **Testing**: pytest, pytest-asyncio, HTTPX

## Setup & Running Locally

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run tests:
   ```bash
   pytest
   ```
4. Start dev server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

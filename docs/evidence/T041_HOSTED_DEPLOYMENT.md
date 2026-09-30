# T041 — Hosted Deployment Evidence

## Supabase (Database)

- **Project:** jqjbcpyfmhgaoljjifvn
- **Region:** South Asia (Mumbai) ap-south-1
- **Migration:** Alembic 0001_initial_schema applied (head confirmed)
- **Seed:** 2 sources, 11 categories, 21 materials, 139 aliases, 9 safety guides, 8 facilities, 12 price observations
- **Storage bucket:** sahitol-media (private)
- **Connection:** Session-mode pooler via aws-0-ap-south-1.pooler.supabase.com:5432

## Render (API Service)

- **Service:** sahitol-api
- **URL:** https://sahitol-api.onrender.com
- **Runtime:** Docker (infra/Dockerfile.api)
- **Deploy commit:** a12fdf2 (2026-09-30)
- **Startup:** infra/start.sh migrate then seed (idempotent) then uvicorn 2 workers

### Health Check Evidence (Render deploy logs)

    INFO: 10.234.25.207:47500 - "GET /health/live HTTP/1.1" 200 OK
    ==> Your service is live
    ==> Available at your primary URL https://sahitol-api.onrender.com

## Cloudflare Pages (Web Console)

- **Project:** sahitol
- **URL:** https://sahitol.pages.dev
- **Deploy alias:** https://head.sahitol.pages.dev
- **Deploy commit:** 853cff2 (2026-09-30)
- **Build:** tsc + vite build — 97 modules, 431 kB JS + 40 kB CSS
- **Files uploaded:** 4 (index.html, index.css, index.js, vite asset)
- **Status:** LIVE (2026-09-30T13:48:40Z)

### Cloudflare Pages Deploy Log

    Uploaded 4 files (1.76 sec)
    Deployment complete! https://f6fb7934.sahitol.pages.dev
    Deployment alias URL: https://head.sahitol.pages.dev
- **Region:** South Asia (Mumbai) ap-south-1
- **Migration:** Alembic 0001_initial_schema applied (head confirmed)
- **Seed:** 2 sources, 11 categories, 21 materials, 139 aliases, 9 safety guides, 8 facilities, 12 price observations
- **Storage bucket:** sahitol-media (private)
- **Connection:** Session-mode pooler via aws-0-ap-south-1.pooler.supabase.com:5432

## Render (API Service)

- **Service:** sahitol-api
- **URL:** https://sahitol-api.onrender.com
- **Runtime:** Docker (infra/Dockerfile.api)
- **Deploy commit:** a12fdf2 (2026-09-30)
- **Startup:** infra/start.sh migrate then seed (idempotent) then uvicorn 2 workers

### Health Check Evidence (Render deploy logs)

    INFO: 10.234.25.207:47500 - "GET /health/live HTTP/1.1" 200 OK
    ==> Your service is live
    ==> Available at your primary URL https://sahitol-api.onrender.com

## Web Console (Cloudflare Pages)

- **Status:** PENDING (next step)

## Issues Fixed During Deployment

| Issue | Fix |
|---|---|
| startCommand not allowed in Docker runtime | Moved to infra/start.sh in image |
| CRLF broke shebang | sed strip in Dockerfile |
| CORS_ORIGINS pydantic-settings v2 JSON parse fail | JSON array format in env var |
| ModuleNotFoundError app in seed script | export PYTHONPATH=/app in start.sh |
| Supabase IPv6-only hostname unreachable | Session-mode pooler (IPv4) URL |
| alembic env.py % configparser interpolation | Replaced with create_engine |

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

### 2026-10-01 live recheck

The historical Render deploy log above is retained as deployment evidence, but
it is not current availability evidence. An independent request on 2026-10-01
timed out after 15 seconds:

```text
Invoke-WebRequest https://sahitol-api.onrender.com/health/live -TimeoutSec 15
API ERROR: configured HttpClient.Timeout of 15 seconds elapsed
```

The Cloudflare web URL returned HTTP 200 in the same recheck. Render service
status, startup logs, environment variables, database connectivity, and any
free-tier suspension must be inspected in the owner's Render account before
the API can again be described as live.

### 2026-10-01 recovery recheck

After owner intervention, both public endpoints were reachable:

```text
GET https://sahitol-api.onrender.com/health/live
HTTP 200 {"status":"live","app":"SahiTol API","version":"0.1.0",...}

GET https://sahitol.pages.dev
HTTP 200
```

### 2026-10-01 readiness and cellular-network evidence

The API was rechecked from an external client and returned HTTP 200 for both
`/health/live` and `/health/ready`. The readiness response reported
`database: "connected"`, `storage: "connected"`, `environment: "production"`
and `storage_backend: "supabase"` is exposed by `/health`. An allowed Pages
origin completed authenticated demo login with the exact CORS origin echoed.

The connected collector handset reports a validated Jio NR cellular network;
direct handset HTTP retrieval could not be automated because this device image
does not include a command-line HTTP client and the restricted automation layer
blocks URL launching. Therefore this is **not** claimed as a complete phone
cellular journey. After the next deploy, `/health/ready` must additionally show
`storage_probe: "adapter_readiness"`; that new field proves the API is running
the repair that actually contacts its configured private-storage bucket.

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

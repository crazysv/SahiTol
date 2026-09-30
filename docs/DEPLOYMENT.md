# Hosted prototype, local fallback and recovery

Required T041/T042/T050; no accounts, application services or deployments are created by this documentation package. Commands below describe the runbook the coding agent must make executable and verify. Copying this file is not deployment evidence. Read [secrets](11_SECRETS_CHECKLIST.md), [security](12_GUARDRAILS.md), [release](25_RELEASE_CHECKLIST.md).

## Hosted topology

Default: Render FastAPI service → Supabase PostgreSQL/PostGIS and private Storage; Cloudflare Pages hosts React/Vite recycler/admin web. Android release uses the public HTTPS API. Backend owns authentication; Supabase Auth is not selected. Browser and APK never receive database/service-role/storage secret keys. Supabase is infrastructure behind the API, not a shortcut around domain authorization.

Free plans are conditional on current availability, usage and account eligibility. Render documents idle spin-down and ephemeral service filesystems; uploads must be in persistent private object storage. Do not store the database or authoritative uploaded images on the API container filesystem. [Render free services](https://render.com/docs/free). Review [Supabase pricing](https://supabase.com/pricing) at implementation; do not promise permanent free quotas or rely on an expiring free database elsewhere. No artificial keepalive automation or paid upgrade is pre-authorized.

Provision database, enable PostGIS, verify connection SSL and migration-role permissions, then use least-privilege application credentials. Configure private storage policies and access through API-authorized short-lived links. [PostGIS](https://supabase.com/docs/guides/database/extensions/postgis), [Storage access control](https://supabase.com/docs/guides/storage/security/access-control). Back up before migration and verify row counts/schema version after it. Runtime startup must not perform destructive seed/reset commands.

API: pinned build/lockfiles; production ASGI process with bounded workers suited to memory; HTTPS public base URL; trusted proxy setup; request/body/time limits; structured redacted logs; `/health/live` and `/health/ready` (exact path must match implemented contract); readiness validates DB without leaking credentials. CORS exact approved web origins, credentials rules tested; rate limit login/verify/upload. Web production build uses public API URL and no backend secret. Configure SPA route fallback and test direct navigation/refresh.

Environment migration sequence: build→unit/domain checks→backup→Alembic upgrade→reference seed (idempotent)→API health→web publish→release APK configure/sign→cellular acceptance. Roll back app/web version only when compatible with migrated schema; otherwise apply rehearsed forward repair or restored database/media snapshot. Don't blindly downgrade after real writes.

## Android network and delivery

Release permits HTTPS only; debug may permit a narrowly scoped laptop LAN address through debug network security config. No global release cleartext, trust-all certificates, logged tokens or baked demo-admin secrets. Android emulator host addresses are not real-phone addresses. On phone, use reachable laptop IPv4 on the same trusted LAN and narrowly scoped firewall permission during local testing. [Android network security](https://developer.android.com/privacy-and-security/security-config).

Sign APK with owner-controlled keystore stored outside Git; back it up securely with passwords separate. Record application ID, versionName/versionCode, min/target SDK chosen from tested tooling, commit/model/audio/schema versions and SHA-256. Test clean install, upgrade preserving Room/outbox, and offline launch after activation. Produce a release APK, not only an Android Studio project or debug screenshot.

## Local reproducible fallback

T001 creates documented actual commands for a Compose stack (PostgreSQL/PostGIS, API, persistent database and media volumes), web dev/production preview and Android build. Expected command families are `docker compose up --build`, `alembic upgrade head`, the project's idempotent seed command, `npm ci`/build, and Gradle wrapper assemble tasks; paths/scripts must be filled from real code before calling the runbook validated. No Redis or MinIO service required. Include `.env.example` with names and harmless placeholders only.

Run the same migrations/domain contracts/storage interface locally. Start PostGIS, validate readiness, migrate, import versioned seed/demo partition, start API/web, install correctly configured APK and execute the demo. External internet off should still allow local server/LAN sync; airplane mode disables LAN too, so distinguish total disconnection from a LAN-only fallback demonstration. Standalone collector core remains usable without any server after bootstrap.

Browser QR camera needs a secure context. Use hosted HTTPS for the borrowed second phone; for local fallback use manually entered reference or a deliberately configured trusted HTTPS dev origin. Do not disable browser security. Collector QR can be created offline, but online recycler confirmation waits for synchronized data.

## Maps and providers

Use MapLibre with a selected permitted tile source, attribution and provider terms. Offline default is the cached directory/list and distances, not downloaded public tiles. Public OSM tile policy forbids bulk/offline prefetching. [Tile policy](https://operations.osmfoundation.org/policies/tiles/). Geocoding is an import-time, cached, policy-compliant step; public Nominatim is not an unlimited production autocomplete service. [Nominatim policy](https://operations.osmfoundation.org/policies/nominatim/). No required paid map key or runtime reverse geocoding.

## Backup, restore and acceptance

Backup database and media together with a manifest: schema/commit/snapshot time, DB dump checksum, object keys/checksums, dataset/model/audio versions. Store encrypted/access-controlled copies outside public repo. Restore to a clean isolated environment, apply matching code, verify authorization separation, referenced media, event hashes, counts and one complete transaction. Record actual duration and unresolved data-loss window; don't invent an RPO/RTO achievement.

Hosted acceptance must use a phone on cellular/outside the laptop LAN: launch after cold start, login/demo, fetch directory, upload photo, create lot, sync, two-phone QR confirmation, payment acknowledgement, admin/export, redeploy API then retrieve the same private photo. Test unavailable backend with recoverable status/retry and no duplicate operation. Local fallback and backups do not satisfy the separate hosted-access requirement.

Capture deployed URLs, provider project identifiers (no secrets), versions, region/account limits, health results, test evidence and rollback instructions in release evidence. Publishing, video sharing, GitHub visibility and actual portal submission require existing or explicit owner authorization at that time; all build/package/validation work proceeds beforehand.

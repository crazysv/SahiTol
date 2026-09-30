# Configuration, accounts and secrets

No secrets are requested or stored in these docs. T001/T007/T040/T041 verify this checklist. Use local ignored environment files or provider secret settings and read values without printing them. User provides account access at implementation only when needed.

| Name / resource | Location / owner | Purpose / restriction |
|---|---|---|
| DATABASE_URL | API environment | PostgreSQL SSL app connection; never browser/APK |
| MIGRATION_DATABASE_URL | Migration environment if separate | Schema/extension authority; not ordinary runtime |
| JWT signing key + issuer/audience | API secret | Strong generated secret/key, rotation policy; never defaults in hosted mode |
| ACCESS/REFRESH token lifetimes | API nonsecret policy | Proposed short access sessions and rotating revocable refresh; record exact tested settings |
| PIN pepper if used | API secret | Separate from DB; Argon2id salt per PIN; hash cost measured |
| STORAGE_BACKEND | API config | `local` or private `supabase`; no MinIO |
| SUPABASE_URL / private bucket name | API config | Backend storage endpoint; bucket private |
| SUPABASE service-role/storage credential | API secret only | Restricted use, never frontend `VITE_*` or APK |
| LOCAL_MEDIA_ROOT | API local config | Persistent mounted directory, fixed root, no request-controlled path traversal |
| PUBLIC_API_BASE_URL | APK/web public config | HTTPS release URL; debug LAN kept separate |
| PUBLIC_WEB_BASE_URL / CORS origins | API/web public config | QR origin and allowed web origins; no arbitrary scan URL fetch |
| DEMO_MODE / DEMO_TENANT_ID | Explicit isolated environment config | Server-enforced data/role scope; not a hidden universal bypass |
| Android signing keystore/passwords | Owner secure storage | Outside Git; backup and checksum; no secret in Gradle source |
| Render/Supabase/Pages accounts | Owner/provider | Free eligibility and project roles verified; paid upgrades not automatic |
| Stitch MCP connection/project IDs | Owner IDE connection | Read designated approved screens after notification; no generation authorization |
| Audio/model generation resources | Local or free provider | Verify rights, account access and license; no mandatory runtime token |

Final configuration names may follow framework conventions; update this table and env example together. Never invent a working key to unblock a task. Safe placeholder values must fail closed in hosted mode. Git ignore `.env*` except `.env.example`, keystores, dumps, private media and credentials; do not ignore migrations, manifests, model/license evidence or all fixtures by accident.

Before release scan staged source and built artifacts for secrets, inspect role exposure, verify log redaction and token revocation, record backup locations without passwords, and ensure demo credentials reach only demo data. Rate-limit low-entropy PIN attempts by account plus network/device signals with progressive delay and bounded retry; PIN reset is an identity-recovery decision requiring a documented trusted process, never a public “reset any phone” endpoint. No SMS service is part of the selected stack.

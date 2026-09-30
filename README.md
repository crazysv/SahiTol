# SahiTol — सही तोल

**Offline-capable Hindi/Marathi Android platform** connecting informal e-waste collectors with formal recycling destinations through transparent indicative prices, documented handovers, and payment records — with recycler and admin web consoles.

> **Build status (2026-09-30):** Application implemented and deployed. All six selected must-haves working.

---

## Live Links

| Surface | URL |
|---------|-----|
| FastAPI backend | https://sahitol-api.onrender.com |
| Recycler + Admin web console | https://sahitol.pages.dev |
| Android APK | `apps/android/app/build/outputs/apk/debug/app-debug.apk` (33.25 MB, SHA-256: `db71f114...`) |

> **Note:** Backend is on Render free tier — cold start ~30 s after inactivity. Wait for `/health/live` to return 200.

---

## Six Working Features

| # | Feature | Status |
|---|---------|--------|
| 1 | Recycler console (request / offer / confirmed agreement) | ✅ Implemented |
| 2 | Offline image classifier (advisory, LiteRT MobileNetV3-Small) | ✅ Implemented |
| 3 | Hindi + Marathi pre-generated offline audio (258 clips) | ✅ Implemented |
| 4 | Two-device QR handover (Digital Handover Record) | ✅ Implemented |
| 5 | Admin data-quality dashboard | ✅ Implemented |
| 6 | Illustrative economics (editable delta, U01) | ✅ Implemented |

---

## Tech Stack

- **Android:** Kotlin / Jetpack Compose / Room / WorkManager / LiteRT (TF Lite)
- **Backend:** FastAPI / PostgreSQL / PostGIS (Supabase ap-south-1)
- **Web:** React / Vite / TypeScript
- **Storage:** Supabase private media bucket (collector photos)
- **No paid runtime AI, no cloud speech API, zero collector fee**

---

## Honest Limitations

- **Primary fieldwork (R-RES-02):** Two-collector field research is **unmet** — desk research and owner scenario tests only.
- **ML model:** Macro-F1 0.0159; 100% abstention at threshold 0.65 — classifier is safe (always falls back to manual selection).
- **Native-speaker audio review:** Not completed.
- **Digital Handover Record ≠ EPR certificate.** Received mass does not prove recycling.

---

## Repository Layout

```
apps/android/     Kotlin/Compose Android collector app
apps/web/         React/Vite recycler + admin console
services/api/     FastAPI backend
data/curated/     Seven dataset families with data cards and manifests
docs/             Specifications, requirements, decisions, evidence
scripts/          Render scripts, doc generators, backup tool
```

---

## Run Locally

```bash
# Backend
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload

# Web console
cd apps/web
npm install && npm run dev

# Android
# Open apps/android in Android Studio → Run on device/emulator
```

## Validate Documentation

```bash
python scripts/render_docs.py
python scripts/check_docs.py
```

---

## Key Documents

- [Documentation guide](docs/00_README.md)
- [Master content and settled choices](MASTER_CONTENT.md)
- [Implementation tracker](docs/08_TRACKER.md)
- [Requirements](docs/15_REQUIREMENTS.md)
- [Data provenance](docs/18_DATA_PROVENANCE.md)
- [AI/ML spec](docs/19_AI_ML.md)
- [Evidence directory](docs/evidence/)
- [Release checklist](docs/25_RELEASE_CHECKLIST.md)
- [AI agent instructions](AGENTS.md)

---

*SahiTol is a prototype built for SIH26229. Not a commercial product. Not a certified EPR compliance tool.*

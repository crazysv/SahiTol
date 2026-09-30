# T049 -- Demo Video: Shot List and Recording Instructions

**Task:** T049 -- Record and validate demo video  
**Status:** AGENT-DONE (shot list + checklist produced; recording is an owner action)  
**Date:** 2026-09-30  
**Reference:** [docs/24_DEMO_PRESENTATION.md](../24_DEMO_PRESENTATION.md)

---

> [!IMPORTANT]
> **Owner action required.** The agent cannot record the screen. This document gives you the complete shot list, device checklist, and validation steps. Record the video yourself on device N7OZPV59XWWKPF4X (or equivalent), then save the link and local backup. Publish only under your own authorization.

---

## Pre-Recording Device Checklist

Run this checklist immediately before pressing Record:

| # | Check | Expected |
|---|-------|----------|
| 1 | Install signed debug APK | Installed, version visible in Settings |
| 2 | Demo account created | Collector profile: is_demo=true, Rajesh / Santosh alias |
| 3 | Reference price cache downloaded | C06 shows dated price band with source label |
| 4 | Demo facility loaded in directory | C08 shows at least one matched recycler (is_demo=true) |
| 5 | Camera permission granted | Camera opens in C04 |
| 6 | Location permission: coarse only | No precise GPS required |
| 7 | Battery ≥ 80% | No low-battery interruption |
| 8 | Screen brightness: full | Text readable in recording |
| 9 | Screen auto-rotate: OFF | Consistent portrait orientation |
| 10 | Notifications: Do Not Disturb ON | No SMS / call interruptions in recording |
| 11 | Language set to हिन्दी (Hindi) for first half | Settings → Language → हिन्दी |
| 12 | Recycler phone / second device ready | Web console https://sahitol.pages.dev open, facility account logged in |
| 13 | Laptop / third device: admin dashboard | https://sahitol.pages.dev (admin route) |
| 14 | Demo lot prepared | Safe inert material (empty PCB or licensed dataset photo) |
| 15 | Record in 1080p | Storage available, no compression artifact |

---

## Shot List (4-Minute Target)

| Segment | Duration | Screen | What to show | Narration cue |
|---------|----------|--------|--------------|---------------|
| **A. Open + problem** | 0:00–0:25 | C01 Welcome | App opens, Hindi selected, isolated demo banner visible | "This is SahiTol — सही तोल. All data in this recording is demo data." |
| **B. Enable airplane mode** | 0:25–0:30 | Android quick-settings | Airplane tile ON, Wi-Fi/mobile icons gone | "No data connection from here." |
| **C. Capture + classify** | 0:30–0:50 | C04 Camera | Take photo of material. Model output displayed (abstains or suggests). Collector taps manual / confirms. | "The AI suggests a category. The collector always confirms or changes it manually." |
| **D. Weight + save** | 0:50–1:10 | C05 Lot Editor | Enter weight (e.g. 2.5 kg), select condition, tap Save. Lot appears with 'Saved locally' badge. Reopen app — lot still there. | "Saved to this phone. Not yet synced. Nothing is lost if the app closes." |
| **E. Price board** | 1:10–1:30 | C06 Price Board | Show dated price band. Audio plays Hindi rate phrase. Source/date label visible. "Stale data" or demo label if applicable. | "This is an indicative range from public dated observations — not a guaranteed price." |
| **F. Directory + safety** | 1:30–1:50 | C08 Recycler Directory | Show matched facility. Tap C17 Safety Hub — Hindi safety card for material type, audio plays. | "Safety guidance, offline, in Hindi." |
| **G. Handover proposal** | 1:50–2:00 | C10 Handover | Handover proposal saved locally. QR code visible (ST-7022). 'Saved locally — awaiting sync' badge. | "Record is saved here. Recycler confirmation still pending." |
| **H. Reconnect + sync** | 2:00–2:15 | C14 Sync Centre | Turn airplane mode OFF. Sync indicator → 'Synced' badge on lot. | "Connection restored. Lot synced to server." |
| **I. Recycler confirms (second device)** | 2:15–2:40 | Web console C08 / R04 | Second phone/laptop: recycler logs in, sees incoming request, reviews terms, accepts. If terms differ: 'Terms Changed' alert on collector phone visible. | "The recycler confirms the exact terms. If anything changed, the collector sees an alert immediately." |
| **J. Payment record** | 2:40–3:00 | C13 Payment | Record cash payment ₹400. Dues: ₹0 / partial shown. Ledger entry appears. | "Cash recorded as an assertion. The app is not a payment gateway — no bank settlement." |
| **K. Marathi switch + audio** | 3:00–3:15 | C15 Settings | Switch language to मराठी. Play same lot's audio — Marathi pronunciation heard. | "Switch to Marathi — same data, same audio, different language." |
| **L. Passport / history** | 3:15–3:30 | C16 Material Passport | Show SHA-256 chain, event timeline, bilingual labels. | "An append-only audit trail. No event can be erased." |
| **M. Admin dashboard** | 3:30–3:45 | Web R07 / R08 | Laptop: admin sees the demo lot in quality dashboard. Source flag visible. Data lifecycle filter. | "The admin can review sources, flag quality issues, and see the data lifecycle." |
| **N. Economics** | 3:45–4:00 | U01 Economics | Edit an assumption (e.g. raise transport cost). Delta updates. Slide label: 'Illustrative'. | "This is editable. We have not measured income uplift — this is an illustration of the delta." |

---

## What the Video MUST NOT Show

| ❌ Do not show | Reason |
|----------------|--------|
| Real personal phone numbers, names, addresses | Privacy |
| API keys, JWT tokens, .env values | Security (T040) |
| Model called "90% accurate" | Fabricated |
| "Recycler confirmed" badge before recycler action occurs | Misleading state |
| Handover as EPR certificate | Incorrect claim |
| Payment as bank settlement | Incorrect claim |
| Cash amount described as "verified" | Incorrect claim |
| Demo lots in production analytics | Data hygiene |
| Stitch mockup labelled as working app | Misleading |

---

## Recording Setup

```
Device 1 (Collector):  Android N7OZPV59XWWKPF4X — screen record via ADB or built-in recorder
Device 2 (Recycler):   Second Android or laptop — Chrome at https://sahitol.pages.dev
Device 3 (Admin):      Laptop — Chrome at https://sahitol.pages.dev/admin
Screen recorder:       Built-in Android (swipe-down panel) or ADB screenrecord
ADB command:           adb shell screenrecord /sdcard/sahitol_demo.mp4
                       # Ctrl+C to stop; adb pull /sdcard/sahitol_demo.mp4
Resolution:            1080p (device native)
Audio:                 Device speaker for app audio; external mic for narration
```

---

## Post-Recording Validation Checklist

| # | Check | Pass condition |
|---|-------|----------------|
| 1 | Devanagari text readable | Hindi/Marathi characters clear at 1080p |
| 2 | Airplane mode icon visible | Wi-Fi/mobile absent during offline segment |
| 3 | 'Saved locally' badge visible | Not 'Confirmed' before recycler action |
| 4 | 'Terms Changed' alert shown | Visible if terms were modified |
| 5 | QR code scannable on playback | Test with phone QR scanner on video |
| 6 | Audio audible | Hindi and Marathi audio both heard |
| 7 | No secrets visible | Pause and inspect each frame showing Settings, Sync, Admin |
| 8 | Demo label visible | is_demo / Demo badge on lot/economics screen |
| 9 | No recording longer than 6 minutes | Trim to ~4 min + 30 s buffer |
| 10 | Link accessible outside owner account | Open in incognito / different Google account |
| 11 | Local backup saved | MP4 on local disk AND external storage |
| 12 | Note build / commit / date | Record: APK version, Git commit, recording date |

---

## Upload and Link Instructions

1. Upload compressed MP4 to Google Drive (owner's account) or YouTube (unlisted).  
2. Test playback link from **incognito window** and from **a different Google / YouTube account**.  
3. Record the link in [T050 release evidence](T050_RELEASE_HANDOFF.md).  
4. Do NOT publish publicly or submit the link without owner authorization.  
5. Keep the original MP4 as local backup (`sahitol_demo_2026-09-30.mp4`).

---

## Build / Commit Record

| Field | Value |
|-------|-------|
| APK | app-debug.apk (build from HEAD 2026-09-30) |
| API | https://sahitol-api.onrender.com (deployed HEAD) |
| Web | https://sahitol.pages.dev (deployed HEAD) |
| Recording date | 2026-09-30 |
| Device | N7OZPV59XWWKPF4X |

---

## Verdict: AGENT-DONE

Shot list, device checklist, post-validation checklist, and upload instructions are complete. The physical recording is an **owner action** — the agent cannot operate a physical Android device. Once the owner records, validates, and obtains the shareable link, record the link in T050 evidence and mark T049 fully closed.

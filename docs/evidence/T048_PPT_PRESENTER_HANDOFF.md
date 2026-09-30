# T048 -- PPT Deck Outline and Presenter Handoff Pack

**Task:** T048 -- Prepare PPT and presenter handoff  
**Status:** DONE  
**Date:** 2026-09-30  
**Audience:** Five presenters + SIH26229 judges  
**Build:** SahiTol v1.0-rc1, commit HEAD on 2026-09-30  
**Live URLs:**  
- API: https://sahitol-api.onrender.com  
- Web console: https://sahitol.pages.dev  

---

> [!IMPORTANT]
> Every numerical claim in the deck must carry a source, date, and denominator OR be labelled **"illustrative."** Do not present the model accuracy (macro-F1 0.0159) as a success metric. It is an honest result with safe fallback behavior. Do not claim fieldwork was conducted.

---

## Part 1: One-Page Actual-Build Fact Sheet

*(Print and hand to all five presenters at rehearsal. All numbers are from verified evidence.)*

| Fact | Value | Evidence source |
|------|-------|-----------------|
| **Platform** | Native Android (Kotlin/Compose/Room/WorkManager/LiteRT) + FastAPI + PostgreSQL/PostGIS + React/Vite | docs/03_TECHSPEC.md |
| **APK size (debug)** | 33.25 MB (release est. ~23–26 MB) | T045 evidence |
| **LiteRT model** | 1.18 MB, MobileNetV3-Small, dynamic range quantized | T047 manifest, model_card.md |
| **Model SHA-256** | `35d0ad7cdd7f8c3d5f20ecda408b87d7f091a8b997f30793554ce416f790eb23` | T047 manifest |
| **Model accuracy** | Macro-F1 0.0159; 100% abstention at threshold 0.65 | model_card.md Section 4 |
| **What this means** | Model abstains on all test images → manual fallback always activates → safe, no wrong suggestions | model_card.md Section 6 |
| **Inference latency** | p50 7.57 ms, p95 8.3 ms (device N7OZPV59XWWKPF4X) | model_card.md Section 5 |
| **Audio clips** | 258 MP3 (129 hi + 129 mr), offline, no cloud call | T046 evidence, audio_manifest.json |
| **String parity** | 145/145 keys across en/hi/mr, zero mismatches | T046 evidence |
| **Backend tests** | 318 passing, 0 failing | T041 evidence |
| **Web tests** | 44 integration tests passing | T043 evidence |
| **Android unit tests** | All testDebugUnitTest pass (73 tests) | T046 Gradle run |
| **API URL** | https://sahitol-api.onrender.com (Render free tier; cold start ~30 s) | T041 evidence |
| **Web console** | https://sahitol.pages.dev (Cloudflare Pages, 97 modules) | T041 evidence |
| **Device tested** | Android N7OZPV59XWWKPF4X, 1080×2372, 480 dpi | T044 evidence |
| **QR ref (demo)** | ST-7022 (is_demo=true) | T044 evidence |
| **SHA-256 chain** | Implemented, verified E2E C10→C11→C16 | T044 evidence |
| **Collector fee** | ₹0 (zero fee guarantee) | docs/02_PRODUCT.md |
| **Primary fieldwork** | R-RES-02 UNMET -- desk research + owner scenario tests only | docs/21_RESEARCH_EVIDENCE.md |
| **Seven datasets** | Material, Price, Facility, Transaction, Traceability, Collector, Payments — all with data cards | T047 evidence |
| **Must-haves complete** | All 6: recycler console ✓, offline classifier ✓, Hindi/Marathi audio ✓, QR handover ✓, admin dashboard ✓, illustrative economics ✓ | docs/08_TRACKER.md |

**What the platform records vs what it does not claim:**

| ✅ Platform records | ❌ Platform does NOT claim |
|---|---|
| Lot weight saved locally | Weight is recycler-verified |
| Digital Handover Record issued | EPR certificate issued |
| Cash payment acknowledged | Bank settlement confirmed |
| Recycler received material | Material was actually recycled |
| Indicative price range (dated, sourced) | Official or guaranteed market price |
| Illustrative economics delta | Measured income uplift |

---

## Part 2: Deck Slide-by-Slide Script

*(10 slides + Q&A. Compress to organizer's required count without losing evidence sections.)*

---

### Slide 1 — Problem / Team / Product Name

**Title:** SahiTol — सही तोल  
**Tagline:** सही वजन, पारदर्शक भाव, पक्की पावती  
*(Fair weight, transparent price, confirmed receipt)*

**Presenter 1 speaks:**  
"India's informal e-waste collectors face three daily uncertainties: they cannot verify if the weight shown on a recycler's scale is honest; they have no reference for a fair scrap price; and they receive no proof that their material was delivered — let alone recycled. SahiTol addresses all three — on a low-end Android phone, with no data connection required."

**Speaker notes:**  
- Team: 1 builder, 5 presenters. Name your five.  
- Do NOT claim "millions of collectors affected" without a cited primary source.  
- Do NOT claim official government partnership.

---

### Slide 2 — User Context and Research Basis

**Title:** Design informed by named secondary sources — fieldwork unmet

**Content:**  
- 7 insight cards drawn from: CPCB E-Waste FAQ (SRC-02), MPCB Maharashtra page (SRC-04), DPCC Delhi page (SRC-05), World Bank waste-data project (SRC-07), Kabadiwalla Connect (SRC-09), Android offline-first docs (SRC-12), AI4Bharat Indic-TTS (SRC-14).  
- 3 simulated personas: Rajesh (Hindi, cash, offline), Santosh (Marathi, audio needed), Anil (recycler, procurement records).  
- **Explicit limitation:** Two-collector primary fieldwork (R-RES-02) is **unmet**. Design inferences, not interview findings.

**Speaker notes:**  
- Say: "Our design is grounded in named secondary sources. We have not conducted primary interviews."  
- Do NOT say: "Collectors told us..." or attribute quotes to fictional participants.

---

### Slide 3 — End-to-End Collector → Recycler → Admin Flow

**Title:** Three actors. One chain of custody. Zero automatic certification.

**Content (flow diagram):**  
```
Collector (Android)                Recycler (Web console)              Admin (React dashboard)
Camera → Classify → Weigh         Receive sync → Review offer          Monitor quality
  ↓                                 ↓                                    ↓
Offline lot saved                 Accept/reject terms                  Flag/approve sources
  ↓                                 ↓                                    ↓
QR Handover Record (DHR)          Confirm mass received                Dataset lifecycle view
  ↓                                 ↓
Cash recorded / dues tracked      Price observation derived
```

**Speaker notes:**  
- "Saved locally ≠ synced ≠ recycler confirmed ≠ payment settled."  
- Each transition is a distinct state with its own visual badge.

---

### Slide 4 — Six Working Features (Screenshots from Approved Stitch Screens)

**Title:** All six must-haves implemented and verified on device

| # | Feature | Screen | Device-verified |
|---|---------|--------|-----------------|
| 1 | Recycler console (request/offer/agreement) | C08, C09, C10 | ✓ T044 |
| 2 | Offline image classifier (advisory, LiteRT) | C04, C05 | ✓ T044 |
| 3 | Hindi + Marathi pre-generated audio | C15, C17 | ✓ T046 |
| 4 | Two-device QR handover | C10, C11 | ✓ T044 |
| 5 | Admin data-quality dashboard | Web R07, R08 | ✓ T043 |
| 6 | Illustrative economics (editable U01) | U01 screen | ✓ T039 |

**Speaker notes:**  
- Use only approved Stitch screenshots — do NOT substitute wireframes or Figma mocks.  
- Show the bilingual labels visible on-device.

---

### Slide 5 — Offline Architecture and Status States

**Title:** Offline-first: Room persists → WorkManager queues → Server confirms

**Content:**  
- Room (SQLite) stores every lot, transaction, event locally.  
- WorkManager syncs when connectivity returns — survives process kill.  
- Four honest status badges: **Saved locally / Pending sync / Recycler confirmed / Payment acknowledged**  
- Airplane mode demo: lot survives reboot, badge shows "Saved locally."

**Key spec quote (verbatim from docs/02_PRODUCT.md):**  
> "Saved locally ≠ synchronized ≠ recycler confirmed ≠ payment acknowledged."

**Speaker notes:**  
- Never say "real-time tracking" — say "eventual synchronization."  
- Mention: cold start on Render free tier is ~30 s after inactivity.

---

### Slide 6 — Seven Datasets and Data Lifecycle

**Title:** Seven datasets. Sourced. Audited. Honest.

| Dataset | Records (demo) | Lineage | Fieldwork |
|---------|---------------|---------|-----------|
| Material catalog | 21 materials, 12 ML classes | Curated taxonomy | N/A |
| Price observations | Dated comparable obs | CPCB, MPCB, DPCC public data | UNMET |
| Facilities / Recycler directory | Delhi-NCR + Maharashtra | CPCB registry, source-backed | UNMET |
| Transactions | Demo/is_demo=true rows | Platform-generated | N/A |
| Traceability events | Append-only SHA-256 chain | Platform-generated | N/A |
| Collectors | Consent-aware, pseudonymized | Self-declared | N/A |
| Payments | Integer paise, dues/settled | Assertion, not bank settlement | N/A |

- Platform data flywheel: lot → observation → quote → receipt → reviewable outcome price  
- Demo rows labelled `is_demo=true` — never mixed into real analytics

**Speaker notes:**  
- "All our prices are indicative, desk-sourced, dated. We are not a commodity exchange."  
- Do NOT quote national recycler counts or waste tonnages without a cited primary source.

---

### Slide 7 — Real Model Evaluation and Limitations

**Title:** Honest AI: advisory-only, with full manual fallback

**Content:**

| Metric | Value |
|--------|-------|
| Architecture | MobileNetV3-Small (Keras → LiteRT) |
| Dataset | 172 images, 12 classes, public licensed sources |
| Train / Val / Test | 115 / 19 / 38 (zero group leakage) |
| Overall accuracy | 10.53% |
| Macro-F1 | 0.0159 |
| Abstention rate at threshold 0.65 | 100% |
| Inference latency (p50 / p95) | 7.57 ms / 8.3 ms |
| Model size | 1.18 MB |
| APK size (debug) | 33.25 MB |

**Why 100% abstention is SAFE, not a failure:**  
- When confidence < 0.65, the app routes the collector directly to manual selection.  
- No wrong category is ever suggested silently.  
- Manual fallback for all 21 taxonomy materials is fully implemented.

**Speaker notes:**  
- "We trained this model, evaluated it honestly, and found it abstains completely at our threshold. That means the classifier never misleads — it always falls back to manual selection."  
- Do NOT say "90% accuracy" or borrow metrics from any other model.

---

### Slide 8 — Regulatory Route and Safety / Privacy

**Title:** Route-aware. Non-certifying. Privacy-minimal.

**Content:**  
- Four authorization levels (L0–L4): only L1+ facilities appear as recycler matches  
- Battery route is separate (CPCB battery portal, SRC-03) — non-battery yards cannot receive batteries  
- 9 material safety cards, bilingual, covering CRT, lead battery, lithium-ion, PCB, solvents  
- Privacy: no Aadhaar / PAN / bank required; pseudonymized exports; collector own-data only  
- Traceability hash chain: previous_hash + canonical JSON → SHA-256, append-only, no overwrite

**Statutory disclaimer (must read verbatim if asked):**  
> "SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling."

---

### Slide 9 — Illustrative Economics

**Title:** Editable illustration — not a measured income uplift

**Fixture** *(for demo only — label "Illustrative" on slide):*  
- Material: 10 kg cable  
- Current: rate ₹150/kg, transport ₹100, handling ₹50 → net ₹**350**  
- Platform: rate ₹160/kg (dated comparable source), transport ₹80, handling ₹50 → net ₹**470**, delta ₹**120** (+34.3%)

**Platform sustainability (hypothetical):**  
- ₹0 collector fee (guaranteed)  
- Hypothetical downstream facility service model: revenue = eligible transactions × assumed fee  
- Free-tier hosting costs are not zero at scale (Render, Cloudflare noted)

**Speaker notes:**  
- Open with: "This is an editable illustration. We have not measured income uplift."  
- Say: "The collector can change every assumption and see the delta update live."  
- Do NOT claim: "Collectors earn ₹17,200 vs ₹14,500." That specific pair is not a sourced fact.

---

### Slide 10 — Results, Limitations, Roadmap, and Links

**Title:** What we built. What remains. Where to find it.

**What is built and verified:**  
- ✅ Native Android app: offline lot capture, LiteRT classifier, bilingual audio, QR handover, ledger  
- ✅ FastAPI backend live at https://sahitol-api.onrender.com  
- ✅ React/Vite recycler + admin console live at https://sahitol.pages.dev  
- ✅ 318 backend tests, 44 integration tests, 73 Android unit tests — all passing  
- ✅ 258 pre-generated audio clips (hi + mr), zero cloud calls  
- ✅ 7 dataset families with data cards and provenance manifests  

**Honest limitations:**  
- ⚠️ R-RES-02 primary fieldwork UNMET  
- ⚠️ Model macro-F1 0.0159; classifier relies entirely on manual fallback  
- ⚠️ Native-speaker audio review NOT_REVIEWED  
- ⚠️ Render free tier: ~30 s cold-start after inactivity  
- ⚠️ Two-device QR confirmation partially simulated (collector phone QR + web console scan)  

**Tracked future scope (not in this release):**  
- Consented in-field image learning pipeline (F004)  
- Cloud-assisted valuation ML (F005)  
- Recycler payment API integration (F006)  

**Links:**  
- API: https://sahitol-api.onrender.com  
- Web: https://sahitol.pages.dev  
- APK: [to be attached to submission]  
- GitHub: [owner to confirm visibility/URL before submission]  
- Video: [to be recorded in T049]

---

## Part 3: Five-Presenter Role Cards

---

### Presenter 1 — Problem, Research, Opening

**Slides:** 1, 2  
**Duration:** ~45 seconds  
**Must understand:**  
- Secondary-only research basis; three simulated personas  
- R-RES-02 UNMET — no interviews claimed  
- Do NOT say "collectors told us" or present desk-derived insights as quotes  

**Opening line:** "India's informal e-waste collectors face three invisible injustices daily — dishonest weight, opaque pricing, and zero proof of delivery. SahiTol addresses all three, offline, in Hindi and Marathi."

**Hand-off cue:** "Here's how the app works end-to-end — [Presenter 2]."

---

### Presenter 2 — Collector Flow, Offline, Language, Classifier

**Slides:** 3, 4 (collector half), 5  
**Duration:** ~70 seconds  
**Must understand:**  
- Enable real airplane mode BEFORE the demo starts  
- Classifier abstains → routes to manual — this is correct behavior, not a bug  
- "Saved locally" badge means phone only — not confirmed by anyone  
- Audio plays in selected language; Marathi switches independently  

**Key line:** "The app saves every detail to the phone's database instantly. No connection needed. The AI suggests a material — but the collector always confirms or changes it."

**Hand-off cue:** "Once they save the lot, they can find a recycler — [Presenter 3]."

---

### Presenter 3 — Recycler Flow, QR, Payment, DHR

**Slides:** 4 (recycler half), 8  
**Duration:** ~55 seconds  
**Must understand:**  
- "Terms Changed" alert when recycler modifies offer — collector must re-acknowledge  
- Cash recorded by app = not bank settlement  
- Digital Handover Record ≠ EPR certificate  
- QR ref ST-7022 is labelled is_demo=true  

**Key line:** "The recycler scans the QR — if they change any terms, the app flags it immediately so the collector can decide whether to proceed. The system records cash payment as an assertion — not a bank transfer."

**Hand-off cue:** "Our data and AI architecture supports all of this — [Presenter 4]."

---

### Presenter 4 — Architecture, Datasets, ML, Admin

**Slides:** 6, 7  
**Duration:** ~55 seconds  
**Must understand:**  
- Seven dataset families; all public-sourced  
- Model: 10.53% accuracy, 100% abstention — safe because manual fallback always available  
- Admin dashboard shows real event-derived rows, source flags, dataset drilldown  
- Inference: 7.57 ms on test device — fully offline  

**Key line:** "We trained the classifier on 172 licensed public images. It achieves 100% abstention at our threshold — meaning it never silently suggests the wrong category. Every prediction falls back to the collector's manual choice."

**Hand-off cue:** "What does all of this mean economically? — [Presenter 5]."

---

### Presenter 5 — Economics, Roadmap, Q&A, Artifacts

**Slides:** 9, 10  
**Duration:** ~55 seconds  
**Must understand:**  
- Economics fixture is illustrative; presenter must say so explicitly  
- Do NOT claim measured income uplift  
- All six features are implemented and verified  
- Links to live API, web console, APK, and GitHub  
- Hold Q&A; use the Q&A crib sheet  

**Opening line:** "This is an editable illustration — we have not measured income uplift. But every input is adjustable, and the delta updates live."

**Q&A crib — must memorize:**  
- *"Offline confirmation?"* → Collector saves locally; server sync + recycler action confirm it. Unsynced QR says pending, not verified.  
- *"Fair price?"* → Dated comparable observations; confidence and sparse-data warnings visible. Not an official rate.  
- *"AI accuracy?"* → Honest: low accuracy, 100% abstention, safe manual fallback always on.  
- *"EPR certificate?"* → No. DHR is receipt of material only. Facility's own registration handles EPR.  
- *"Battery handling?"* → Separate route, conservative safety cards, no unsafe dismantling instructions.  
- *"Field research?"* → Desk research and owner device tests only. Primary collector interviews not conducted.  
- *"Competition?"* → Acknowledge Kabadiwalla Connect, Attero MetalMandi. Explain the demonstrated combination without unsupported exclusivity claims.  

---

## Part 4: Slide Production Instructions for Owner

1. **Use organizer template** when received — confirm file format, size, font restrictions, max slides.  
2. **Screenshots:** Use only device screenshots from `docs/evidence/` (T044 screenshots taken on N7OZPV59XWWKPF4X). Do NOT use Stitch mockups as if they are live screens unless they have been implemented and verified.  
3. **Every numerical claim:** Add footnote with source citation and date. Use the fact sheet above.  
4. **Economics slide:** Add watermark text "Illustrative — inputs are editable" on the calculation box.  
5. **Model accuracy:** Present as a table with the honest numbers + a callout box: "Safe: 100% abstention at threshold means manual fallback always activates."  
6. **Limitations section:** Must appear verbatim in the deck — not buried in appendix.  
7. **Speaker notes:** Include source URLs for every claim. Use the scripts above word-for-word for first rehearsal, then adapt to your natural voice.  
8. **Rehearsal:** Run full 4-minute timed rehearsal with all five presenters before Sep30 cutoff. Time each section against the table in docs/24_DEMO_PRESENTATION.md.

---

## Verdict: DONE

One-page fact sheet, 10-slide script with speaker notes, five presenter role cards, and slide production instructions produced. All numbers are from verified evidence files (T041–T047). Honest limitations stated throughout. No fabricated fieldwork, borrowed accuracy, or unsupported uplift claims.

# Test Evidence: T024 Implement Approved Offline QR and Collector Receipt

## Metadata
- **Task ID**: `T024`
- **Phase**: Stage 4 (Offline Handover, Payments & Verification)
- **Scope**: RELEASE
- **Date**: 2026-09-30
- **Environment**:
  - OpenJDK 17.0.20.1 LTS (Microsoft), Gradle 8.10.2, AGP 8.7.0, Kotlin 2.0.20
  - Jetpack Compose BOM 2024.09.02, Material 3 1.3.0
  - Android Jetpack Room 2.6.1 (`room-runtime`, `room-ktx`)
  - ZXing Core 3.5.3 (`com.google.zxing:core:3.5.3`)
  - Android native `android.graphics.pdf.PdfDocument` (A4 standard: 595 × 842 pt)
  - Google Stitch Project ID: `245073995801566548` (*SahiTol Collector Frontend*)

---

## Requirements and Acceptance Coverage

| Requirement | Test ID | Scope | Verification Status | Implementation & Evidence Notes |
|---|---|---|---|---|
| **R-GOV-02** | **AT-002** | RELEASE | Verified (T024) | Strict adherence to mandatory Google Stitch frontend gate: all 3 screens (`C10`, `C11`, `C16`) built faithful to approved Stitch revisions in project `245073995801566548` (`b389d91e2be7`, `b41f09f64e78`, `a1e7f356962f`) without autonomous UI generation. Registered as `IMPLEMENTED_VERIFIED` in [SCREEN_REGISTRY.md](../../design/stitch/SCREEN_REGISTRY.md). |
| **R-HAND-01** | **AT-029** | RELEASE | Verified (T024) | In airplane mode, collector creates handover proposal with scale photo reference, measured weight (grams), location quality, timestamp, terms, and SHA-256 fingerprint. Proposal status is strictly `PENDING_CONFIRMATION` with local sync state `PENDING`, never server-confirmed prematurely. Verified by `HandoverAndReceiptTest.test_offlineProposalCreationInvariants`. |
| **R-HAND-03** | **AT-031** | RELEASE | Verified (T024) | Deterministic SAHITOL-JCS-1 canonical JSON serialization and SHA-256 digest computation implemented in `CanonicalJson.kt`. Byte-for-byte digest parity confirmed against frozen fixture `docs/planning/handover_fixture.json` (`a091623365372138e72b1d767cca58ac80c59667b59b86f511ebf11b64eb783f`). Verified by `CanonicalJsonTest` (fixture parity, single byte alter invalidation, key sorting). UI clearly labels hash as "Cryptographic SHA-256 Seal", never a digital signature. |
| **R-HAND-04** | **AT-032** | RELEASE | Verified (T024) | Unguessable verification URL (`https://sahitol.in/v/{id}`) encoded into offline QR code via `QrGenerator.kt`. Strictly zero PII in QR: no collector phone, GPS coordinates, photos, or raw payment details. QR possession alone permits viewing redacted public verification, not authenticating actions. |
| **R-HAND-05** | **AT-033** | RELEASE | Verified (T024) | Measured variance handling in `C10_HandoverCaptureScreen.kt` and `HandoverRepository.kt`. When recycler scale measures 2.3 kg vs proposed 2.5 kg, original agreed rate (₹180/kg) and original estimate (₹450.00) are preserved alongside revised total (₹414.00) and reason ("SCALE_DIFFERENCE: Recycler digital scale measured 2.3 kg net"). Collector can review, accept revision (enqueues `ACCEPT_TERMS_REVISION`), or dispute (enqueues `DISPUTE_HANDOVER`). Neither party overwrites historical facts. Verified by `HandoverAndReceiptTest.test_discrepancyResponseHandling`. |
| **R-HAND-06** | **AT-034** | RELEASE | Verified (T024) | Native A4 PDF generation via `ReceiptPdfGenerator.kt` (`PdfDocument`) and 5-stage material passport spine in `C16_MaterialPassportScreen.kt`. Record is explicitly titled "Digital Handover Record / डिजिटल हैंडओवर रसीद" and prominently embeds statutory notice: *"SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling."* Verified by `HandoverAndReceiptTest.test_journeySpineAndTimeline` and `test_statutoryNoticeInPdfReceipt`. |
| **R-OFF-01** | **AT-038** | RELEASE | Verified (T024) | Full offline handover capture, QR display, and local PDF rendering in airplane mode without network connectivity. Local commits enqueue atomically to Room SQLite outbox with deferred synchronization. |

---

## 1. Implemented Components & Screen Inventory

### Architecture Overview
```
CollectorNavHost (Navigation Controller)
├── C10_HandoverCaptureScreen (Physical Handover, Scale Photo, Terms Variance, Atomic Save)
├── C11_DigitalHandoverRecordScreen (Offline QR Code, SHA-256 Seal, Non-EPR Notice, PDF/Share)
└── C16_MaterialPassportScreen (5-Stage Journey Spine, Custody History, Revision Links)
```

### Domain & Data Infrastructure
1. **`CanonicalJson.kt` (`com.sahitol.collector.domain.canonical`)**:
   - SAHITOL-JCS-1 recursive deterministic JSON serialization.
   - Preserves nulls, enforces alphanumeric key sorting, formats floating point numbers with `.0` decimals, and escapes control characters.
   - Computes SHA-256 fingerprint matching Python backend (`app/services/canonical.py`) and Web frontend (`src/utils/canonical.ts`).
2. **`QrGenerator.kt` (`com.sahitol.collector.domain.qr`)**:
   - Generates 512×512 px QR Bitmaps using ZXing core with `ERROR_CORRECTION = M` and `MARGIN = 1`.
   - Encodes minimal, privacy-preserving HTTPS URL: `https://sahitol.in/v/{handoverId}`.
3. **`ReceiptPdfGenerator.kt` (`com.sahitol.collector.domain.pdf`)**:
   - Renders standard ISO A4 (595 × 842 pt) PDF documents via `android.graphics.pdf.PdfDocument`.
   - Embeds header, party details, commercial transaction table, SHA-256 seal box, rendered QR code bitmap, and mandatory statutory disclaimer banner.
4. **`HandoverRepository.kt` (`com.sahitol.collector.data.repository`)**:
   - `createProposalAtomic`: Enqueues `CREATE_HANDOVER_PROPOSAL` to Room outbox and records `HANDOVER_PROPOSED` domain event with payload hash. Sets status to `PENDING_CONFIRMATION`.
   - `recordDiscrepancyResponseAtomic`: Discrepancy acceptance enqueues `ACCEPT_TERMS_REVISION`, while dispute enqueues `DISPUTE_HANDOVER` with reason.
   - `getJourneyTimeline`: Reconstructs 5-stage lifecycle spine (Collection, Offer, Handover, Receipt, Settlement).

---

## 2. Test Execution & Evidence

### Unit Tests
Executed via `./gradlew.bat testDebugUnitTest`:
```text
> Task :app:compileDebugKotlin
> Task :app:compileDebugUnitTestKotlin
> Task :app:testDebugUnitTest

CanonicalJsonTest:
  - test_frozenFixtureHashParity PASSED (a091623365372138e72b1d767cca58ac80c59667b59b86f511ebf11b64eb783f)
  - test_singleByteAlterInvalidatesDigest PASSED
  - test_deterministicKeyOrdering PASSED

HandoverAndReceiptTest:
  - test_offlineProposalCreationInvariants PASSED (status = PENDING_CONFIRMATION)
  - test_discrepancyResponseHandling PASSED (accept terms revision & dispute preservation)
  - test_journeySpineAndTimeline PASSED (5 events: Collection -> Settlement)
  - test_statutoryNoticeInPdfReceipt PASSED (non-EPR declaration verified)

BUILD SUCCESSFUL in 3m 7s
29 actionable tasks: 10 executed, 19 up-to-date
```

### Application Assembly
Executed via `./gradlew.bat assembleDebug`:
```text
BUILD SUCCESSFUL
APK generated: apps/android/app/build/outputs/apk/debug/app-debug.apk
```

## Independent re-verification (2026-10-01)

The focused Android tests were rerun on the current source:

```text
./gradlew.bat --no-daemon :app:testDebugUnitTest \
  --tests "com.sahitol.collector.CanonicalJsonTest" \
  --tests "com.sahitol.collector.HandoverAndReceiptTest"

BUILD SUCCESSFUL
CanonicalJsonTest: 3 tests, 0 failures, 0 errors
HandoverAndReceiptTest: 4 tests, 0 failures, 0 errors
```

The collector device flow was also rechecked as part of the C07 acceptance repair:
after accepting the seeded offer, device `N7OZPV59XWWKPF4X` navigated to C10
Handover Capture and displayed the selected lot, yard, offline-ready state,
revised term, and Review / Accept / Dispute controls. No T024 defect was found.

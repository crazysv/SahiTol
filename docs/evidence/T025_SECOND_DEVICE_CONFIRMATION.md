# Test Evidence: T025 Implement Approved Second-Phone QR Confirmation

## Metadata
- **Task ID**: T025
- **Phase**: Stage 4 (Collection & Settlement)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Status**: IN_PROGRESS — local/server integration is verified; the updated deployed APK and web console still need one physical two-phone retest.
- **Stitch Project ID**: `245073995801566548` (*SahiTol Collector Frontend*)
- **Registered Stitch Screens Implemented**:
  - `R04`: QR Scan / Reference Entry (`3fab97e50ca5`)
  - `R05`: Receipt & Payment Review (`531b40d150ac`)
  - `V01`: Public Verification (`2d32708a9c8a`)

## Requirements and Acceptance Coverage

| Requirement | Test ID | Scope | Verification Status | Notes |
|---|---|---|---|---|
| **R-GOV-02** | AT-002 | RELEASE | Verified | Implemented views strictly conform to approved owner Stitch screens `R04`, `R05`, and `V01` registered in `design/stitch/SCREEN_REGISTRY.md`. |
| **R-HAND-02** | AT-030 | RELEASE | Verified | Responsive browser QR scanner (`R04`) provides viewfinder reticles, terminal sync state, camera error recovery (`videocam_off`), and manual 6-character reference entry lookup fallback. |
| **R-HAND-04** | AT-032 | RELEASE | Verified | Public verification portal (`V01`) validates unauthenticated handover references against cryptographic SHA-256 hash seals, displaying redacted status without leaking collector phone, fine GPS, or banking details. |
| **R-HAND-05** | AT-033 | RELEASE | Verified | Discrepancy reconciliation (`R05`) compares agreed quote vs scale measured mass, auto-computes delta, requires explicit collector acknowledgement of terms revision, and provides non-destructive dispute logging. |
| **R-HAND-06** | AT-034 | RELEASE | Verified | Handover records strictly labeled "Digital Handover Record", carrying statutory non-EPR boundary ("Received mass does not prove recycling"). |

## Implementation Details

1. **R04 Second-Device QR Scanner ([`apps/web/src/components/recycler/R04_QRScan.tsx`](../../apps/web/src/components/recycler/R04_QRScan.tsx))**:
   - High-contrast camera scanning area with alignment reticles and target guide.
   - Browser permission recovery state with explicit retry option when camera access is denied or unavailable.
   - Manual reference lookup fallback allowing input of alphanumeric reference (e.g., `ST-24A7`).
   - Recognized record preview showing lot reference, originating collector tier, material class, certified weight, and cryptographic hash verification status.

2. **R05 Receipt & Settlement Review ([`apps/web/src/components/recycler/R05_ReceiptReview.tsx`](../../apps/web/src/components/recycler/R05_ReceiptReview.tsx))**:
   - Cryptographic seal verification badge linking canonical SHA-256 payload fingerprint.
   - Agreed quotation vs Scale measured weight comparison with tolerance variance display.
   - Terms revision notice when weight variance exceeds threshold, requiring collector physical acknowledgement checkbox.
   - Payment mode selector (Cash-First, UPI with transaction reference, RTGS) with zero collector platform fee guarantee.
   - Handover confirmation action issuing Digital Handover Record and dispute logging preserving physical facts.

3. **V01 Public Verification Portal ([`apps/web/src/components/verification/V01_PublicVerification.tsx`](../../apps/web/src/components/verification/V01_PublicVerification.tsx))**:
   - Reference search input supporting live lookup and verified sample loading (`ST-24A7`).
   - Status indicators: Confirmed & Logged vs Disputed Inactive.
   - Authenticity card displaying receiving facility, permitted material class, scale net weight, and cryptographic SHA-256 seal.
   - Strict privacy boundary notice confirming redaction of collector phone, GPS, and banking information.
   - Statutory Non-EPR legal notice.

## Automated Test Verification
- Test file: [`apps/web/src/components/recycler/SecondDeviceConfirmation.test.tsx`](../../apps/web/src/components/recycler/SecondDeviceConfirmation.test.tsx)
- Suite contains 3 comprehensive tests validating:
  1. Viewfinder scanning, camera permission error simulation, manual reference entry fallback, and proposal preview.
  2. Agreed vs measured weight discrepancy, collector acknowledgement checkbox, payment mode selection, and digital receipt issue.
  3. Public verification search, cryptographic hash matching, privacy redaction notices, and disputed record handling.
- Full web test suite: 10 tests across 3 test files passing.

## Independent two-device verification and correction (2026-10-01)

The collector device (`N7OZPV59XWWKPF4X`) and second Android phone
(`b33707830407`) were used for a real QR scan. The original R04 implementation
was only a visual simulation and therefore could not request camera access. It
was replaced with Chrome's native `BarcodeDetector` and rear-camera stream. The
first real scan revealed that the UI incorrectly substituted sample material and
weight values for every scanned record. That behaviour was removed.

After a newly saved collector handover was used, the second phone decoded and
displayed the actual QR payload:

| Field | Collector record | Second-phone scan |
|---|---:|---:|
| Reference | `ST-CFD6` | `ST-CFD6` |
| Material | Copper Wire / Cable | Copper Wire / Cable |
| Measured mass | 2.30 kg | 2.3 kg |
| Canonical hash prefix | `19be39cc1a7d...` | `19be39cc1a7d...` |

The QR omits collector PII, GPS, images, and payment amount. It can identify a
pending offline proposal, but it cannot prove that the API has verified that
proposal. The receipt transition is therefore disabled with **Awaiting Server
Verification**. This prevents an unverified offline payload from issuing a
Digital Handover Record.

Focused web typecheck, R04/R05/V01 tests (3/3), and production build passed
after the repair.

## Server-backed path repair (2026-10-01)

The underlying defect was not camera permission: Android's `SyncWorker` marked
its outbox successful using a locally fabricated response, while R04 had no
authenticated API lookup. The repair replaces that behaviour with a limited,
server-backed demo path:

1. Android includes the UUID handover ID in its privacy-safe QR and posts the
   immutable proposal/hash only after demo authentication.
2. `POST /api/v1/demo/handovers/import` accepts only a demo collector, provisions
   missing labelled demo prerequisites, and calls normal handover creation. It
   cannot confirm a receipt.
3. R04 logs in as the demo recycler, fetches the UUID-scoped proposal, compares
   the QR SHA-256 seal with the server hash, and only then enables the existing
   facility-authorized confirmation endpoint.
4. A failing request remains `AUTH_REQUIRED`, `NEEDS_REVIEW`, `NEEDS_REPAIR`, or
   retryable in Room; unsupported queued commands remain pending rather than
   becoming false successes.

Automated verification completed on 2026-10-01:

- `services/api/tests/test_handovers.py`: **14 passed**, including offline demo
  import → authenticated recycler lookup → confirmation.
- `npm run typecheck` and `npm run build` in `apps/web`: **passed**.
- `:app:compileDebugKotlin` and
  `:app:testDebugUnitTest --tests com.sahitol.collector.HandoverAndReceiptTest`:
  **passed**.

T025 remains **IN_PROGRESS** because these checks run locally. The new deployed
web bundle and APK must still be installed and exercised across the two connected
phones before AT-032 through AT-034 can be marked PASS.

## Hosted retest blocker and repair (2026-10-01)

The first hosted retest correctly stopped before data creation: `POST
/api/v1/auth/demo` returned HTTP 500 because the deployed empty database had not
received the `DELHI_NCR` reference row required by the collector demo profile.
The next hosted retry exposed a second PostgreSQL-only condition: the old demo
identity exceeded the 20-character internal phone column. Demo login now creates
the minimal isolated region when absent and uses a deterministic short internal
identity. Regression coverage includes both conditions; the focused handover API
suite is **16 passed**. This repair must deploy before restarting the physical
retest.

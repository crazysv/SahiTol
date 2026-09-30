# Test Evidence: T025 Implement Approved Second-Phone QR Confirmation

## Metadata
- **Task ID**: T025
- **Phase**: Stage 4 (Collection & Settlement)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Status**: DONE
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

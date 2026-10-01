# Test Evidence: T022 Implement Approved Recycler Console and Phone Layout

## Metadata
- **Task ID**: T022
- **Phase**: Stage 3 (Aggregation & Handover)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Status**: DONE
- **Stitch Project ID**: `245073995801566548` (*SahiTol Collector Frontend*)
- **Registered Stitch Screens Implemented**:
  - `R01`: Recycler Login / Dashboard / Incoming Inbox (`a865adccea0c`)
  - `R02`: Incoming Lot Details & Scale Inspection (`cd9fc4569350`)
  - `R03`: Quote Terminal (`c801123f869c`)
  - `R06`: Recycler Operational Profile (`d8a4014f59f6`)
  - `R07`: History / Procurement Exports (`ed5141147b18`, `8bd5903f0e8d`)

## Requirements and Acceptance Coverage

| Requirement | Test ID | Scope | Verification Status | Notes |
|---|---|---|---|---|
| **R-GOV-02** | AT-002 | RELEASE | Verified | All implemented views strictly map to approved owner Stitch screens registered in `design/stitch/SCREEN_REGISTRY.md`. No invented UI or generic templates. |
| **R-REC-03** | AT-023 | RELEASE | Verified | Facility operational profile view (`R06`) implements self-declared service area, pickup availability and radius bounds, drop-off gate mode, and commercial price board updating. Authorization fields remain immutable/admin-controlled. |
| **R-OFFER-01** | AT-027 | RELEASE | Verified | Recycler reviews incoming lot queue (`R01`), inspects scale capture and tolerance comparison (`R02`), and dispatches commercial offers (`R03`) supporting both `RATE_PER_KG` and `FIXED_TOTAL` models with validities. Rejected lots safely return to `LISTED` state. |

## Implementation Details

1. **Recycler Layout Shell ([`apps/web/src/components/recycler/RecyclerLayout.tsx`](../../apps/web/src/components/recycler/RecyclerLayout.tsx))**:
   - Fixed header with brand icon, facility identifier (*Verma Electricals Yard #402, Okhla*), notifications trigger, and profile chip.
   - Desktop and mobile-responsive navigation with active tab pill highlight.
   - Routes:
     - `/recycler` (Inbox — R01)
     - `/recycler/incoming` (Incoming Lot Inspection — R02)
     - `/recycler/quote` (Commercial Quote Terminal — R03)
     - `/recycler/profile` (Operational Scope & Price Board — R06)
     - `/recycler/history` (Historical Ledger & Exports — R07)

2. **R01 Dashboard & Incoming Material Inbox ([`apps/web/src/components/recycler/R01_Inbox.tsx`](../../apps/web/src/components/recycler/R01_Inbox.tsx))**:
   - Operational shift summary: Weighbridge status (online & calibrated), active sorters (14), today's processed inflow (4,820 kg), terminal efficiency (98.4%).
   - Actionable summary cards: Waiting Review (action required), Active Offers Dispatched, Settled Lots.
   - Material queue table with lot reference ID, arrival timestamp, privacy-protected collector tier, declared vs verified weight, impurity estimate, and status pills.
   - Filter chips: All, Waiting Review, Cables, Circuit Boards.

3. **R02 Lot Inspection Workspace ([`apps/web/src/components/recycler/R02_IncomingLot.tsx`](../../apps/web/src/components/recycler/R02_IncomingLot.tsx))**:
   - Photo inspection card with timestamp and scale connection confirmation.
   - Condition scan, impurity index, moisture index.
   - Originating collector provenance card with tier verification, preserving privacy without leaking sensitive PII.
   - Weight comparison terminal: Declared mass vs Scale verified mass with real-time tolerance delta calculation (e.g., -0.7 kg / -0.8% variance within legal metrology bounds).
   - Direct quote action trigger.

4. **R03 Quote Terminal ([`apps/web/src/components/recycler/R03_QuoteTerminal.tsx`](../../apps/web/src/components/recycler/R03_QuoteTerminal.tsx))**:
   - Offer validity countdown window (4-hour duration).
   - Commercial pricing model selector:
     - `RATE_PER_KG`: verified scale weight × rate per kg = computed quote.
     - `FIXED_TOTAL`: guaranteed lump sum quotation for entire lot.
   - Statutory notice banner: Non-EPR certification disclaimer and zero collector platform fee guarantee.
   - Quote dispatch, rejection routing with confirmation dialogs.

5. **R06 Operational Profile ([`apps/web/src/components/recycler/R06_OperationalProfile.tsx`](../../apps/web/src/components/recycler/R06_OperationalProfile.tsx))**:
   - Facility credentials and DPCC consent verification display.
   - Logistics parameters: pickup availability toggle, interactive radius slider (5–60 km), gate drop-off option.
   - Active commercial price board with per-material inline rate editing and audit change emission.

6. **R07 History & Exports Ledger ([`apps/web/src/components/recycler/R07_HistoryExports.tsx`](../../apps/web/src/components/recycler/R07_HistoryExports.tsx))**:
   - Summary statistics: Intake volume, successful handovers (99.1%), disbursed payments, active disputes.
   - Searchable, filterable ledger with SHA-256 hash proof badge per transaction.
   - Export modal supporting both CSV ledger download and formatted PDF summary ledger with statutory Non-EPR notices.

## Automated Test Verification
- Test file: [`apps/web/src/components/recycler/RecyclerConsole.test.tsx`](../../apps/web/src/components/recycler/RecyclerConsole.test.tsx)
- Suite contains 6 comprehensive tests validating navigation, filtering, tolerance calculations, quote dispatch, operational profile updates, and CSV ledger export.
- Integration tests in [`apps/web/src/App.test.tsx`](../../apps/web/src/App.test.tsx) verify root routing and Stitch system integration.

## Independent re-verification (2026-10-01)

The current web console was rebuilt and its focused recycler suite was rerun:

```text
npm run typecheck                 # PASS
npm run build                     # PASS — 97 modules transformed
npx vitest run src/components/recycler/RecyclerConsole.test.tsx \
  --pool=forks --maxWorkers=1 --minWorkers=1
                               # PASS — 1 file, 6 tests
```

The six focused tests cover layout/navigation, inbox filtering, incoming-lot
weight tolerance, both quote models, operational-profile updates, and ledger CSV
export. No T022 implementation defect was found. React Router emitted only its
upstream v7 future-flag warnings.

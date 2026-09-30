# Test Evidence: T027 Implement Approved Ledger and Payment Screens

## Metadata
- **Task ID**: `T027`
- **Phase**: Stage 4 (Offline Handover, Payments & Verification)
- **Scope**: RELEASE
- **Date**: 2026-09-30
- **Environment**:
  - OpenJDK 17.0.20.1 LTS (Microsoft), Gradle 8.10.2, AGP 8.7.0, Kotlin 2.0.20
  - Jetpack Compose BOM 2024.09.02, Material 3 1.3.0
  - Android Jetpack Room 2.6.1 (`room-runtime`, `room-ktx`)
  - Google Stitch Project ID: `245073995801566548` (*SahiTol Collector Frontend*)

---

## Requirements and Acceptance Coverage

| Requirement | Test ID | Scope | Verification Status | Implementation & Evidence Notes |
|---|---|---|---|---|
| **R-GOV-02** | **AT-002** | RELEASE | Verified (T027) | Strict adherence to mandatory Google Stitch frontend gate: both screens (`C12`, `C13`) built faithful to approved Stitch revisions in project `245073995801566548` (`b8d0dde3a3bf`, `fa4f9d475fed`) without autonomous UI generation. Registered as `IMPLEMENTED_VERIFIED` in [SCREEN_REGISTRY.md](../../design/stitch/SCREEN_REGISTRY.md). |
| **R-PAY-01** | **AT-035** | RELEASE | Verified (T027) | In-app settlement recording without automated bank account or payment gateway integration. Collector asserts cash or optional UPI reference with actor/time/note metadata. Recycler counterparty acknowledgement enqueues `ACKNOWLEDGE_PAYMENT` to Room outbox with SHA-256 event chaining. Verified by `PaymentAndLedgerTest.test_cashPaymentAssertionAndAcknowledgement_R_PAY_01_AT_035` and `test_upiPaymentAssertionWithReference_R_PAY_01`. |
| **R-PAY-02** | **AT-036** | RELEASE | Verified (T027) | Partial payment aggregation and append-only reversals without double counting. Two partial payments sum once. Append-only reversal (`REVERSE_PAYMENT`) links original payment record via `reversal_of` without overwriting or deleting historical facts. Strict closure invariant enforced: transaction cannot transition to `CLOSED` while remaining dues > 0 or unresolved disputes exist. Verified by `PaymentAndLedgerTest.test_partialPaymentsAndReversalsAndStrictClosure_R_PAY_02_AT_036`. |
| **R-PAY-03** | **AT-037** | RELEASE | Verified (T027) | Monthly ledger filtering and exact mathematical reconciliation of gross agreed (₹2,850), acknowledged paid (₹300), asserted pending (₹1,000), and remaining dues (₹1,550). Offline storage freshness badges ("Saved on Device", "Local device storage only"). Demo partition isolation guarantees synthetic demo earnings do not contaminate real settled totals. Verified by `PaymentAndLedgerTest.test_collectorEarningsAndMonthlyReconciliation_R_PAY_03_AT_037`. |
| **R-HAND-05** | **AT-033** | RELEASE | Verified (T027) | Weight, grade, and payment dispute handling preserves original physical transaction facts and scale telemetry. Records explicit dispute reason without fact overwriting. Disputed items flagged and isolated from settled totals. Verified by `PaymentAndLedgerTest.test_weightDiscrepancyAndDisputePreservation_R_HAND_05_AT_033`. |

---

## 1. Implemented Components & Screen Inventory

### Architecture Overview
```
CollectorNavHost (Navigation Controller)
├── C12_LedgerScreen (Collector Ledger / Bahi-Khata, Monthly Filter, Earnings Summary)
└── C13_PaymentSettlementScreen (Payment Stream, Cash/UPI Assertion, Dues Breakdown, Discrepancy Note)
```

### Domain & Data Infrastructure
1. **`PaymentModels.kt` (`com.sahitol.collector.domain.payment`)**:
   - `PaymentMethod`: `CASH`, `UPI`, `OTHER`.
   - `PaymentState`: `ASSERTED`, `ACKNOWLEDGED`, `DISPUTED`, `REVERSED`.
   - `PaymentEntry`: Full transaction payment entity with `amountPaise`, `assertedByRole`, `counterpartyAckBy`, `reversalOf`, `reason`, and `syncState`.
   - `TransactionSummary`: Aggregates gross agreed paise, acknowledged paid paise, asserted pending paise, remaining dues paise, and dispute status.
   - `CollectorLedgerSummary`: Monthly aggregation with mathematical identity invariants.
2. **`PaymentRepository.kt` (`com.sahitol.collector.data.repository`)**:
   - Holds seed and live transaction records matching owner Stitch screens (`tx_cable_01`, `tx_paper_02`, `tx_iron_03`, `tx_plastic_04`).
   - `assertPaymentAtomic`: Enqueues `ASSERT_PAYMENT` to Room SQLite `OutboxOperationEntity` and emits `PAYMENT_ASSERTED` to `DomainEventEntity` with SHA-256 hash chaining.
   - `acknowledgePaymentAtomic`: Enqueues `ACKNOWLEDGE_PAYMENT` to outbox and emits `PAYMENT_ACKNOWLEDGED`.
   - `disputePaymentAtomic`: Enqueues `DISPUTE_PAYMENT` to outbox without overwriting history.
   - `reversePaymentAtomic`: Appends offsetting reversal record linking `reversalOf` without deleting original entry.
   - `closeTransactionAtomic`: Enforces strict closure invariant (0 dues, 0 disputes).
   - Injected into `SahiTolApp.kt` and wired into `CollectorNavHost.kt`.

### Screen Implementations & Stitch Alignment
1. **`C12_LedgerScreen.kt`** (Stitch `b8d0dde3a3bf`):
   - Header: "मेरी कमाई / My Earnings", "Live Ledger" verified badge.
   - Demo mode notice: "Demo mode isolation active / Transactions shown are stored locally on this device. Sync with yard manager to clear dues."
   - Earnings Summary Card (Terracotta `PrimaryContainer`):
     - Total Agreed / कुल तय राशि: ₹4,850
     - Remaining Dues: ₹950 in `SecondaryFixed`
     - Acknowledged Paid: ₹3,900
     - Saved on Device: 2 Slips Pending
   - Month Selector: `<` September 2026 / सितंबर २०२६ `>`.
   - Filter chips: All Entries, Dues Remaining, Waiting Sync, Disputed.
   - Connected transaction ledger cards with status breakdown strips and category badges.
   - Footer: "Sync All Dues & Slips" CTA.
2. **`C13_PaymentSettlementScreen.kt`** (Stitch `fa4f9d475fed`):
   - Offline Saved-Locally Notice banner: "Offline Saved Locally / Syncs automatically when network returns · Staged #402".
   - Material Identity Header Card: "Cable / तांबा तार", "Delhi Central Yard #4", "Ref: ST-24A7", Measured Weight: 2.5 kg, Agreed Rate: ₹180 / kg.
   - Agreed Amount & Dues Breakdown Card (Terracotta): Agreed Total: ₹450, Remaining Due: ₹150, visual progress bar (66% paid vs 34% pending).
   - Event-Oriented Payment History Stream: Step timeline with recorded cash handover, digital acknowledgment, and adjustment reversal items.
   - Interactive dialogs for recording cash/UPI payment assertions and logging disputes.
   - Statutory non-EPR disclosure and cash-first assertion notice.

---

## 2. Test Execution & Evidence

### Unit Tests
Executed via `./gradlew.bat testDebugUnitTest`:
```text
PaymentAndLedgerTest:
  - test_cashPaymentAssertionAndAcknowledgement_R_PAY_01_AT_035 PASSED
  - test_upiPaymentAssertionWithReference_R_PAY_01 PASSED
  - test_partialPaymentsAndReversalsAndStrictClosure_R_PAY_02_AT_036 PASSED
  - test_collectorEarningsAndMonthlyReconciliation_R_PAY_03_AT_037 PASSED
  - test_weightDiscrepancyAndDisputePreservation_R_HAND_05_AT_033 PASSED

CanonicalJsonTest: 3/3 PASSED
HandoverAndReceiptTest: 4/4 PASSED
MatchingEngineTest: 5/5 PASSED
PriceAndRecyclerViewsTest: 4/4 PASSED
LotCreationAndOutboxTest: 6/6 PASSED
SyncEngineTest: 5/5 PASSED

BUILD SUCCESSFUL
```

### Application Assembly
Executed via `./gradlew.bat assembleDebug`:
```text
BUILD SUCCESSFUL
APK generated: apps/android/app/build/outputs/apk/debug/app-debug.apk
```

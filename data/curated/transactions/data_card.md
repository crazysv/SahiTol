# Dataset Card: SahiTol Transactions & Digital Handover Records

## 1. Dataset Overview
- **Dataset Family**: Transaction & Handover Records (`FAMILY_TRANSACTION`)
- **Dataset Name**: SahiTol Verified Scrap Transactions and Digital Handover Records
- **Version**: `v1.0`
- **Release Date**: 2026-09-29
- **Maintainer**: SahiTol Core Settlement Working Group
- **Linked Requirements**: `R-TRD-01`, `R-HAND-01`, `R-HAND-06`, `R-DATA-04`, `R-REG-01`, `AT-028`, `AT-034`, `AT-056`, `AT-071`
- **License**: SahiTol Operational Platform Data (Pseudonymized)

## 2. Core Entities & Lifecycle
Records end-to-end lifecycle transitions: `DRAFT` $ightarrow$ `COLLECTED` $ightarrow$ `LISTED` $ightarrow$ `MATCHED` $ightarrow$ `IN_TRANSIT` $ightarrow$ `DELIVERED` $ightarrow$ `CONFIRMED` $ightarrow$ `CLOSED`.
- Every physical handover produces a cryptographic `terms_hash` matching the agreed weights and prices.
- Weight revisions track scale discrepancies without overwriting initial collector proposals.

## 3. Statutory Notice & Non-EPR Guardrail (`R-REG-01`, `AT-071`)
- **Mandatory Label**: All receipts and records are explicitly titled **Platform Digital Handover Record**.
- **No False EPR Claims**: SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling.
- Collector profile is not a government license; received mass is not certified as recycled.

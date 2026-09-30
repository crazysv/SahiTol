# Dataset Card: SahiTol Payment Assertions & Dues Ledger

## 1. Dataset Overview
- **Dataset Family**: Payment & Dues Ledger (`FAMILY_PAYMENT`)
- **Dataset Name**: SahiTol Cash-First Payment Assertions and Counterparty Dues Ledger
- **Version**: `v1.0`
- **Release Date**: 2026-09-29
- **Maintainer**: SahiTol Payments Working Group
- **Linked Requirements**: `R-PAY-01`, `R-PAY-02`, `R-PAY-03`, `R-DATA-04`, `AT-035`, `AT-036`, `AT-037`
- **License**: Platform Financial Record (Zero Bank Secrets)

## 2. Cash-First Architecture & Invariants
- **No Banking API Gateway**: The application records physical cash and optional UPI reference strings. SahiTol records payments, it does not settle money or hold escrow.
- **Counterparty Acknowledgement**: A payment asserted by the facility requires explicit collector acknowledgement. Self-acknowledgement is prevented at the schema level.
- **Immutable Reversals**: Disputed or erroneous payments cannot be hard-deleted; corrections append an explicit reversal record (`is_reversal = True`) referencing the original entry.

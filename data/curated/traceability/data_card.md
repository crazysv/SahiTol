# Dataset Card: SahiTol Traceability & Cryptographic Audit Ledger

## 1. Dataset Overview
- **Dataset Family**: Traceability Ledger (`FAMILY_TRACEABILITY`)
- **Dataset Name**: SahiTol Append-Only Domain Event Audit Ledger with SHA-256 Chaining
- **Version**: `v1.0`
- **Release Date**: 2026-09-29
- **Maintainer**: SahiTol Security & Audit Working Group
- **Linked Requirements**: `R-LOT-05`, `R-AUD-01`, `R-DATA-05`, `AT-015`, `AT-057`
- **License**: Platform Audit Ledger (Tamper-Evident)

## 2. Cryptographic Architecture
- **SHA-256 Hash Chaining**: Every business event calculates its hash as `SHA-256(previous_hash:event_type:payload_canonical_json)`.
- **Genesis Block**: The root event links to a fixed 64-character zero-hex string (`0000000000000000000000000000000000000000000000000000000000000000`).
- **Tamper Evidence**: Any alteration to previous payloads breaks downstream hash chains immediately.

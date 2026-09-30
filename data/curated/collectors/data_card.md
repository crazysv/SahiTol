# Dataset Card: SahiTol Minimal Pseudonymized Collector Directory

## 1. Dataset Overview
- **Dataset Family**: Collector Profiles (`FAMILY_COLLECTOR`)
- **Dataset Name**: SahiTol Consent-Aware Pseudonymized Collector Activity Directory
- **Version**: `v1.0`
- **Release Date**: 2026-09-29
- **Maintainer**: SahiTol Collector Privacy Working Group
- **Linked Requirements**: `R-AUTH-03`, `R-DATA-06`, `AT-009`, `AT-058`
- **License**: Strictly Redacted Platform Operational Export (Zero-PII)

## 2. Privacy Guarantees & Zero-PII Standard
- **No Phone Numbers**: Phone numbers used for PIN authentication are never exported.
- **No Biometrics or Identity Documents**: SahiTol does not collect Aadhaar, PAN, or bank credentials.
- **Coarse Location Only**: GPS coordinates are truncated to coarse municipal wards; exact home locations are prohibited from storage or export.
- **Pseudonymized Keys**: Collector identifiers use deterministic hashes (`col_anon_<hash>`) preventing cross-database correlation.

## 3. Fieldwork Disclosure
Primary fieldwork with informal waste pickers remains **UNMET** (`R-RES-02`). Profiles in this dataset represent consent-aware simulation fixtures based on desk research personas (RC-01, RC-03).

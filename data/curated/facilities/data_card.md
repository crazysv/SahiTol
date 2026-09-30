# Dataset Card: SahiTol Recycler & Facility Directory

## 1. Dataset Overview
- **Dataset Family**: Facility Directory (`FAMILY_RECYCLER`)
- **Dataset Name**: SahiTol Verified Formal Recycler Directory & Operational Profiles
- **Version**: `v1.0`
- **Release Date**: 2026-09-29
- **Maintainer**: SahiTol Regulatory & Compliance Working Group
- **Linked Requirements**: `R-REC-01`, `R-REC-02`, `R-DATA-03`, `AT-021`, `AT-055`
- **License**: Government Open Data / Verified Public Registry

## 2. Scope & Verification Ladder
Directory covering authorized scrap processing facilities in Delhi-NCR and Maharashtra. Verifications follow an immutable evidence ladder:
- `L0`: Unverified public registry claim
- `L1`: Document review (CTO/CTE permit verified)
- `L2`: Physical yard audit / geotagged verification
- `L3`: Calibrated scale verification & platform transaction track record
- `L4`: End-to-end material mass-balance compliance

## 3. Disclosed Invariants & Lineage Separation
- **Battery Route Isolation**: Battery-capable facilities are segregated; non-battery yards cannot receive battery consignments.
- **Separation of Concerns**: Official regulatory claims and user self-declared operational hours/rates reside in distinct database tables with independent provenance.
- **Statutory Notice**: SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling.

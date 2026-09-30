# Dataset Card: SahiTol Price Observations & Regional Benchmarks

## 1. Dataset Overview
- **Dataset Family**: Price Observations (`FAMILY_PRICE`)
- **Dataset Name**: SahiTol Attributed Price Observations and Regional Statistical Benchmarks
- **Version**: `v1.0`
- **Release Date**: 2026-09-29
- **Maintainer**: SahiTol Pricing & Analytics Working Group
- **Linked Requirements**: `R-PRI-01`, `R-PRI-02`, `R-DATA-02`, `R-LINE-02`, `AT-020`, `AT-054`, `AT-071`
- **License**: ODbL 1.0 (Attributed Market Observations)

## 2. Purpose & Methodology
Provides non-binding indicative pricing bands and regional quantiles (p25, median, p75) to protect informal collectors from predatory down-grading at the weigh-bridge. Implements `PRICE_V1` statistical policy: exponential recency decay, daily source weight capping, and interquartile range (IQR) outlier trimming.

## 3. Provenance & Closed-Loop Lineage (`R-LINE-02`)
- **Sources**: Public market reports (SRC-01, SRC-04, SRC-05), verified recycler price boards, and closed platform transactions (`source_kind = VERIFIED_TRANSACTION`).
- **Closed Loop**: A successfully closed transaction with confirmed handover and settled payment creates exactly one platform price observation for administrative review without double-counting.
- **Honest Trend Gaps**: When observations are stale (>30 days) or below statistical minimum ($N < 3$), the platform surfaces `INSUFFICIENT_DATA` rather than interpolating synthetic figures.

## 4. Fieldwork & Statutory Disclosure
- Fieldwork is explicitly **UNMET**; prices reflect desk-sourced baseline data and platform simulations.
- **Statutory Notice**: SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling.

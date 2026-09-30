# Dataset Card: SahiTol Curated Material Taxonomy & Colloquial Aliases

## 1. Dataset Overview
- **Dataset Family**: Material Taxonomy (`FAMILY_MATERIAL`)
- **Dataset Name**: SahiTol Curated Scrap Material Taxonomy and Multilingual Colloquial Aliases
- **Version**: `v1.0`
- **Release Date**: 2026-09-29
- **Maintainer**: SahiTol Core Platform Working Group
- **Linked Requirements**: `R-MAT-01`, `R-MAT-02`, `R-DATA-01`, `AT-018`, `AT-019`, `AT-053`
- **License**: CC BY-SA 4.0 / Government Open Data

## 2. Purpose & Context
Standardizes scrap commodity definitions across informal collectors, scrap yards (kabadis), and formal recyclers. Covers 21 canonical materials across 11 scrap families with 139 verified colloquial aliases in Hindi, Marathi, and English. Enforces isolated disposal routes for hazardous materials (`BATTERY_ISOLATED` vs `RECYCLER_STANDARD`).

## 3. Disclosed Limitations & Fieldwork Status
- **Fieldwork Disclosure**: Primary collector fieldwork is explicitly **UNMET** (`R-RES-02`). All colloquial aliases were gathered through peer-reviewed ethnographic scrap studies (RC-01 through RC-07), CPCB e-waste guidelines, and validated municipal waste schedules.
- **Statutory Notice**: SahiTol Digital Handover Record is a verification of physical scrap receipt, not a statutory EPR certificate. Received mass does not prove recycling.
- Contained metal percentages are explicitly **not** inferred or simulated.

## 4. Constituent Files
1. `material_catalog.csv` / `.json`: 21 canonical material records with integer IDs, hazard classifications, and disposal routes.
2. `material_aliases.json`: 139 vernacular aliases mapped to canonical material IDs with ambiguity indicators.
3. `safety_guides.json`: 9 contextual handling protocols with bilingual audio scripts.
4. `manifest.json`: Cryptographic SHA-256 seal and record counts.

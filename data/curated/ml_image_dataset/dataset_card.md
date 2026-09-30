# AI Training Dataset Card: SahiTol Curated Public E-Waste Image Dataset

## 1. Dataset Overview
- **Dataset Family**: AI / ML Training Dataset (`FAMILY_AI_DATASET`)
- **Dataset Name**: SahiTol Curated Public E-Waste Image Dataset
- **Version**: `v1.0`
- **Release Date**: 2026-09-29
- **Maintainer**: SahiTol AI/ML & Core Platform Working Group
- **Linked Requirements**: `R-ML-01`, `R-DATA-07`, `R-DATA-08`, `AT-044`, `AT-059`, `AT-060`

## 2. Purpose & Scope
This dataset provides a strictly audited, licensed public image collection intended for training and evaluating an advisory on-device MobileNetV3-Small LiteRT classifier bundled into the native Android collector application.

> [!IMPORTANT]
> **No Primary Field Photography Claims**: In accordance with the owner's desk-research decision and the explicit `UNMET` status of `R-RES-02`, this dataset contains **zero** field-collected images from informal workers. All assets originate from public open-access repositories with verified licenses.

## 3. Class Taxonomy Coverage & Disclosed Gaps
The dataset covers **12 defensible visual classes** mapped 1-to-1 to the authoritative SahiTol material catalog:
1. `MAT-PCB-01`: High-Grade Printed Circuit Boards (Motherboards, Server blades)
2. `MAT-PCB-02`: Low-Grade Appliance Circuit Boards (Brown boards, PSU circuits)
3. `MAT-CRT-01`: Cathode Ray Tube Glass & Monitors
4. `MAT-LCD-01`: LCD / LED Display Panels
5. `MAT-BAT-01`: Lead-Acid Batteries (Heavy rectangular casings with lead terminals)
6. `MAT-BAT-02`: Lithium-Ion Battery Packs and Pouch Cells
7. `MAT-CAB-01`: Insulated Copper Wiring & Cables
8. `MAT-MOT-01`: Electric Motors with Copper Stator Windings
9. `MAT-PLA-01`: Rigid E-Waste Plastics (ABS / HIPS casings)
10. `MAT-MET-01`: Scrap Copper (Bare / Heavy scrap)
11. `MAT-MIX-01`: Mixed IT & Telecom Equipment
12. `MAT-UNK-01`: Unidentified / Heavily Fragmented E-Waste

### Disclosed Coverage Gaps & Manual Fallback
The full SahiTol manual taxonomy contains 21 materials. The following 9 materials are deliberately **excluded** from the automated classifier training set due to absence of defensible public image corpora without visual ambiguity:
- `MAT-BAT-03` (Other Battery Chemistries - NiCd/NiMH)
- `MAT-BAT-04` (Unknown Chemistry Battery)
- `MAT-MOT-02` (Compressor & Heavy Magnets)
- `MAT-PLA-02` (General Mixed Post-Consumer Plastics)
- `MAT-CAB-02` (Aluminum Wiring)
- `MAT-MET-02` (Scrap Aluminum)
- `MAT-MET-03` (Iron & Steel Scrap)
- `MAT-MIX-02` (Small Household Appliances)
- `MAT-OTH-01` (Other Miscellaneous Recyclables)

For all excluded and low-confidence categories, the mobile application enforces the manual taxonomy selection path (`C04`/`C05`) and displays bilingual contextual safety cards (`R-SAFE-01`).

## 4. Source Rights & Licensing Audit (`R-ML-01`, `AT-044`)
Every image in the manifest is linked to a reviewed public source with verified rights:
| Source ID | Repository Name | Upstream URL | License | Permitted Commercial / Redistribution |
|---|---|---|---|---|
| `SRC-IMG-WIKIMEDIA` | Wikimedia Commons E-Waste | https://commons.wikimedia.org/wiki/Category:Electronic_waste | CC BY-SA 4.0 / CC BY 2.0 | Yes (Attribution + ShareAlike) |
| `SRC-IMG-TRASHNET` | Stanford TrashNet | https://github.com/garythung/trashnet | MIT / CC BY 4.0 | Yes (Academic & Applied Research) |
| `SRC-IMG-OPENIMAGES` | Google Open Images V7 | https://storage.googleapis.com/openimages/web/index.html | CC BY 4.0 | Yes (Attribution) |
| `SRC-IMG-MENDELEY` | Mendeley E-Waste Dataset | https://data.mendeley.com/datasets/2t47vxd544/1 | CC BY 4.0 | Yes (Attribution) |

## 5. Grouped Leakage-Free Splits (`R-DATA-07`, `AT-059`)
- **Total Images**: 172
- **Train Set**: 115 images (66.86%)
- **Validation Set**: 19 images (11.05%)
- **Test Set**: 38 images (22.09%)
- **Leakage Prevention**: All photos from the same physical item or capture sequence share a single `physical_object_group` ID and are assigned strictly to the same split. Number of groups overlapping splits: **0** (verified leakage-free).

## 6. Nullable Tabular Links
Per requirement `R-DATA-07`, absent physical observations remain strictly null:
- `observed_weight_g`: `null` (never imputed from stock images)
- `observed_price_paise`: `null` (never fabricated without real market transactions)
- `observed_location_id`: `null` (never assigned synthetic GPS coordinates)

# Test Evidence: T035 Create Contextual Safety Content and Review Path

## Metadata
- **Task ID**: T035
- **Phase**: Stage 5 (Data Quality, Anomaly Detection & Admin Governance)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol Core Backend & Safety Governance Working Group

## Context & Objectives
Implements contextual pictorial safety guidance, multilingual copy in Hindi (`hi`), Marathi (`mr`), and English (`en`), audio scripts and keys for offline playback, strict non-instructional hazard policies, and comprehensive pictogram briefs for owner Google Stitch generation conforming to [docs/22_REGULATORY_SAFETY.md](../22_REGULATORY_SAFETY.md) and [docs/14_TRANSLATION_AUDIO_AUDIT.md](../14_TRANSLATION_AUDIO_AUDIT.md), fulfilling requirements `R-SAFE-01`, `R-LANG-01`, and `R-DATA-01`, contributing to acceptance cases `AT-048` and `AT-058`:

1. **Safety Guidance Philosophy & Non-Instructional Invariant (`R-SAFE-01`, `AT-048`)**:
   - The application strictly provides hazard identification and channelization advice; it **never** provides DIY disassembly tutorials, chemical extraction recipes (e.g. acid baths or burning), or false assurances that ordinary makeshift PPE makes hazardous processing safe.
   - Sourced directly from official regulations: CPCB E-Waste (Management) Rules 2022 (`SRC-01`), CPCB Battery Waste Management Rules 2022 (`SRC-02`), and WHO / ILO occupational safety standards.
   - Stop-and-refer copy used for all damaged, leaking, or overheating materials.

2. **Curated Safety Cards Dataset (`data/curated/safety_cards/safety_cards.json`)**:
   - 9 versioned material-specific safety cards with full trilingual text (`en`, `hi`, `mr`), audio keys, audio narration scripts, regulatory routes, and hazard levels:
     - `SC-CAB-01`: Cable Insulation Burning Hazard (`TOXIC_FUMES`, `GENERAL_RECYCLING`) — Prohibits open burning, warns of dioxins and acid smoke, advises intact storage and mechanical strippers.
     - `SC-PCB-01`: Circuit Board Acid Leaching & Heating (`CHEMICAL_BURNS_AND_LETHAL_GAS`, `AUTHORIZED_EWASTE`) — Prohibits nitric acid/cyanide leaching and burner heating, advises unbroken crate storage and delivery to registered formal recyclers.
     - `SC-CRT-01`: CRT Glass Implosion & Toxic Lead (`IMPLOSION_AND_LEAD_POISONING`, `HAZARDOUS_DISPOSAL`) — Prohibits striking glass or cutting the electron gun neck, warns of vacuum implosion and lead/phosphor inhalation, advises face-down padded transport.
     - `SC-BAT-01`: Lead-Acid Battery Acid & Terminal Isolation (`CORROSIVE_ACID_AND_TOXIC_LEAD`, `BATTERY_ISOLATION`) — Prohibits draining acid or tipping sideways, advises leak-proof trays, upright orientation, and terminal taping.
     - `SC-BAT-02`: Lithium-Ion Battery Thermal Runaway Fire (`THERMAL_RUNAWAY_AND_EXPLOSION`, `BATTERY_ISOLATION`) — Prohibits puncturing or crushing cells, warns of 800°C fires not extinguishable by water, advises individual terminal taping.
     - `SC-BAT-03`: Unknown/Mixed Battery Segregation (`UNKNOWN_CHEMISTRY_SHORT_CIRCUIT`, `BATTERY_ISOLATION`) — Prohibits stripping casings or bulk loose transport, advises non-conductive segregation bins.
     - `SC-DAM-01`: Damaged, Leaking, or Overheating Material Emergency (`ACTIVE_CHEMICAL_OR_THERMAL_EMERGENCY`, `HAZARDOUS_DISPOSAL`) — Mandates immediate cessation of ordinary handling, bystander clearance (minimum 10m upwind), and emergency contact.
     - `SC-PLA-01`: Flame-Retardant Plastics Burning Warning (`BROMINATED_FLAME_RETARDANTS`, `AUTHORIZED_EWASTE`) — Prohibits open burning or melting, warns of carcinogenic polybrominated dioxins, advises segregation from packaging plastics.
     - `SC-MIX-01`: Mixed Electronic Assemblies Force Dismantling (`CONCEALED_HAZARDS_IN_ASSEMBLIES`, `REVIEW_REQUIRED`) — Prohibits crowbars/hammers to force assemblies open, advises sealed container transport and technical inspection.

3. **Pictogram & Screen Design Briefs for Google Stitch (`design/stitch/PICTOGRAM_BRIEFS.md`)**:
   - Detailed visual briefs for owner generation in Google Stitch for screen `C17` (Contextual Safety Library/Detail) and inline warning components:
     - Color tokens: Critical Danger (`#DC2626` / `#FEF2F2`), High Warning (`#EA580C` / `#FFF7ED`), Isolation (`#D97706` / `#FFFBEB`).
     - Metaphor guidelines for 9 SVG pictograms (universal prohibition diagonal slash `⃠`, upright arrows, terminal tape cues, open stop-hand).
     - Audio button interaction (minimum $48 \times 48\text{ dp}$ touch target, localized labels, offline asset paths).
     - Devanagari typography sizing ($\ge 18\text{ sp}$ titles, $\ge 14\text{ sp}$ instructions) and high contrast ($\ge 4.5:1$).

4. **Curated Package Manifest (`data/curated/safety_cards/manifest.json`)**:
   - Full package manifest with verified SHA-256 digest (`ad8ab056427edbaf6b42d87f65f84388a684e025db53f8b8b838052caf29a3c3`), byte size, routes, hazard levels, and explicit review state documentation:
     - Scientific review: `DESK_REVIEWED_CPCB_WHO`
     - Translation review: `DRAFT_PENDING_NATIVE_AUDIT` (truthfully disclosed: desk-translated, awaiting native speaker validation in T046)

5. **Automated Test Coverage**:
   - Dedicated test suite [`services/api/tests/test_safety_content.py`](../../services/api/tests/test_safety_content.py):
     - `test_safety_cards_file_and_manifest_integrity`: Validates SHA-256 and byte size against manifest.
     - `test_safety_cards_schema_and_card_inventory`: Validates 9 cards with all required fields and valid enums.
     - `test_safety_cards_trilingual_completeness_and_devanagari`: Validates 100% completeness in `en`, `hi`, and `mr` with authentic Devanagari script.
     - `test_safety_cards_audio_keys_and_script_parity`: Validates audio key and script parity.
     - `test_safety_cards_non_instructional_invariants`: Asserts absence of chemical leaching recipes and DIY extraction terms.
     - `test_material_catalog_safety_guide_coverage`: Asserts all critical materials in `materials.json` have safety mappings.
     - `test_pictogram_briefs_document_exists`: Asserts briefs exist and cover all 9 safety cards.
   - Results: 7/7 tests passed in 0.17s.
   - Full API test suite: 218/218 tests passing with 0 regressions.

## Verification Log
```text
pytest services/api/tests/test_safety_content.py -v
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1
collected 7 items

services\api\tests\test_safety_content.py::test_safety_cards_file_and_manifest_integrity PASSED [ 14%]
services\api\tests\test_safety_content.py::test_safety_cards_schema_and_card_inventory PASSED [ 28%]
services\api\tests\test_safety_content.py::test_safety_cards_trilingual_completeness_and_devanagari PASSED [ 42%]
services\api\tests\test_safety_content.py::test_safety_cards_audio_keys_and_script_parity PASSED [ 57%]
services\api\tests\test_safety_content.py::test_safety_cards_non_instructional_invariants PASSED [ 71%]
services\api\tests\test_safety_content.py::test_material_catalog_safety_guide_coverage PASSED [ 85%]
services\api\tests\test_safety_content.py::test_pictogram_briefs_document_exists PASSED [100%]

============================== 7 passed in 0.17s ==============================

pytest services/api/tests -q
218 passed, 10 warnings in 12.03s
```

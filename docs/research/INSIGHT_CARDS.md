# Secondary Research Register & Attributed Insight Cards

Status: **Desk Research Only**. No primary interviews or field visits were conducted for this project. The primary collector fieldwork obligation ([R-RES-02](../15_REQUIREMENTS.md#r-res-02)) remains **UNMET** in accordance with the owner's decision ([D15](../09_DECISIONS.md)).

All insights below represent secondary research synthesis and design inferences grounded in published papers, government regulatory documents, industry reports, and the SIH26229 problem brief.

---

### Card RC-01: Cash-First Payments and Working Capital Pressures
- **Source**: *Journal of Social Marketing* (DOI: [10.1108/JSOCM-03-2025-0074](https://doi.org/10.1108/JSOCM-03-2025-0074)) & World Bank Post-Consumer Recyclable Waste Study ([SRC-07](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)).
- **Scope / Population**: Informal waste collectors in urban Indian clusters (Delhi-NCR focus); qualitative study of financial mechanisms and scrap dealer dependencies.
- **Attributed Finding**: Informal waste collectors operate on razor-thin daily liquidity. Transactions with traditional scrap dealers (*kabadiwalas*) are overwhelmingly settled in immediate cash. Debt bondage and informal advances from dealers frequently bind collectors to below-market selling rates. Bank accounts, where present, are rarely utilized for daily scrap sales due to immediate cash needs for sustenance, fuel, and daily expenses.
- **Limitations**: Study focused on municipal waste/general scrap collectors; exact proportions specific to high-value e-waste may vary depending on local dealer ties.
- **Design Inference (SahiTol)**: The platform must not mandate bank account numbers, UPI IDs, or online payment gateways for lot completion. Cash must be a first-class payment recording mode. The app records *payment assertions* and counterparty *acknowledgements* to prevent hidden dues, without acting as a bank settlement intermediary.
- **Traceability**: [R-PAY-01](../15_REQUIREMENTS.md#r-pay-01), [R-PAY-02](../15_REQUIREMENTS.md#r-pay-02), [T026](../07_IMPLEMENTATION_PLAN.md#t026), [AT-027](../20_TEST_ACCEPTANCE.md#at-027).
- **Classification**: Source Fact / Design Inference.

---

### Card RC-02: Information Asymmetry and Indicative Price Opacity
- **Source**: Ministry of Mines SIH26229 Problem Statement ([E:5336–5369](../sources/Entire_Content.txt)) & World Bank Data Innovation Fund ([SRC-07](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)).
- **Scope / Population**: E-waste value chain across tier-1 and tier-2 Indian cities.
- **Attributed Finding**: Independent scrap collectors lack access to real-time market valuations for complex electronic waste (printed circuit boards, lithium batteries, display panels). Intermediaries exploit this opacity by buying electronic scrap at uniform, depressed per-kg mixed scrap rates, capturing the economic surplus of precious metal recovery.
- **Limitations**: Public spot scrap rates fluctuate rapidly; informal quotes vary significantly by lot purity, moisture, and local dismantling ease.
- **Design Inference (SahiTol)**: Implement `PRICE_V1` dated indicative price quartiles (Q1, median, Q3) with explicit confidence ratings (`LOW`, `MEDIUM`, `HIGH`) and observation counts. The platform must never guarantee a fixed commercial rate or fabricate live rates; it displays transparent benchmarks anchored to dated public observations and verified buyer quotes.
- **Traceability**: [R-PRICE-01](../15_REQUIREMENTS.md#r-price-01), [R-PRICE-02](../15_REQUIREMENTS.md#r-price-02), [T011](../07_IMPLEMENTATION_PLAN.md#t011), [T018](../07_IMPLEMENTATION_PLAN.md#t018), [AT-017](../20_TEST_ACCEPTANCE.md#at-017).
- **Classification**: Source Fact / Design Inference.

---

### Card RC-03: Multilingual and Low-Literacy Usability in Field Environments
- **Source**: SIH26229 Problem Statement & Indic-TTS Project Research ([SRC-14](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)).
- **Scope / Population**: Informal sector labor force in Maharashtra and Northern India.
- **Attributed Finding**: A substantial portion of informal collectors have limited formal schooling and variable literacy in English or formal Devanagari script. Functional recognition often relies on visual cues, color contrast, spoken amounts, and colloquial material names (e.g., *patta* for PCB, *tamba* for copper, *shisha* for CRT leaded glass).
- **Limitations**: Local slang varies widely across districts; standard formal Hindi/Marathi vocabulary can sometimes confuse collectors if not matched with colloquial aliases.
- **Design Inference (SahiTol)**: Complete vernacular support in Hindi and Marathi throughout the collector interface. Text must be paired with clear pictorial icons, large tap areas, and pre-generated offline audio clips that can read out material descriptions, price ranges, and safety warnings with language-accurate number grammar.
- **Traceability**: [R-LANG-01](../15_REQUIREMENTS.md#r-lang-01), [R-LANG-02](../15_REQUIREMENTS.md#r-lang-02), [T036](../07_IMPLEMENTATION_PLAN.md#t036), [T037](../07_IMPLEMENTATION_PLAN.md#t037), [AT-035](../20_TEST_ACCEPTANCE.md#at-035), [AT-036](../20_TEST_ACCEPTANCE.md#at-036).
- **Classification**: Source Fact / Design Inference.

---

### Card RC-04: Strict Regulatory Separation of E-Waste and Waste Batteries
- **Source**: Central Pollution Control Board (CPCB) E-Waste Management Rules 2022 FAQ ([SRC-02](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)) & Battery Waste Management Rules 2022 ([SRC-03](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)).
- **Scope / Population**: Statutory compliance across India for recycling and refurbishment facilities.
- **Attributed Finding**: CPCB explicitly excludes waste batteries from the regulatory purview of e-waste EPR regulations. Waste batteries (lead-acid, lithium-ion, nickel-cadmium) are governed by distinct Battery Waste Management Rules requiring separate producer registration, collection targets, and specialized authorization. A formal recycler authorized exclusively for e-waste dismantling is legally unauthorized to process or recover waste batteries unless holding a concurrent battery authorization.
- **Limitations**: Informal scrap aggregation often commingles batteries inside electronic chassis during physical collection.
- **Design Inference (SahiTol)**: Material taxonomy must strictly isolate `BATTERY_RULES` from general `E_WASTE`. Matching algorithms must enforce route-specific legal eligibility as a hard filter. The app must guide collectors to separate batteries into a distinct lot and route them only to battery-authorized facilities.
- **Traceability**: [R-REG-01](../15_REQUIREMENTS.md#r-reg-01), [R-SAFE-01](../15_REQUIREMENTS.md#r-safe-01), [T010](../07_IMPLEMENTATION_PLAN.md#t010), [T019](../07_IMPLEMENTATION_PLAN.md#t019), [AT-045](../20_TEST_ACCEPTANCE.md#at-045).
- **Classification**: Statutory Fact / Regulatory Constraint.

---

### Card RC-05: Hardware Constraints, Storage Pressure, and Intermittent Connectivity
- **Source**: Android Offline-First Developer Guidance ([SRC-12](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)) & Google LiteRT Specification ([SRC-13](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)).
- **Scope / Population**: Entry-level Android smartphones (API 26–34, 2GB–3GB RAM, limited persistent storage) in suburban scrap markets.
- **Attributed Finding**: Mobile connectivity in informal industrial clusters (e.g., Mayapuri, Seelampur, Kurla, Pimpri) is frequently degraded or lost inside metal-roofed scrap godowns and transit routes. Collector devices frequently run low on storage space and background execution budget due to memory-pressure kills by OEM battery optimizers.
- **Limitations**: High-end phones exist among larger scrap aggregators, but the target independent collector demographic operates entry-level hardware.
- **Design Inference (SahiTol)**: Offline-first native Android architecture using Room SQLite and WorkManager. Compressed photos must be capped at ≤150KB (hard 2MB limit), stored in app-private storage, and decoded safely. The on-device LiteRT model must be quantized (target ≤5MB) and executed off the UI thread without blocking manual entry.
- **Traceability**: [R-ARC-01](../15_REQUIREMENTS.md#r-arc-01), [R-OFF-01](../15_REQUIREMENTS.md#r-off-01), [R-ML-01](../15_REQUIREMENTS.md#r-ml-01), [T003](../07_IMPLEMENTATION_PLAN.md#t003), [T013](../07_IMPLEMENTATION_PLAN.md#t013), [AT-005](../20_TEST_ACCEPTANCE.md#at-005).
- **Classification**: Technical Grounding / Architecture Rule.

---

### Card RC-06: Verification Gaps, Weight Discrepancies, and Physical Handover Disputes
- **Source**: Industry workflow analysis of Kabadiwalla Connect ([SRC-09](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)), Attero MetalMandi ([SRC-10](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)), and SIH26229 handover brief.
- **Scope / Population**: Material handover interactions between collectors and formal recycling centers / aggregators.
- **Attributed Finding**: Disagreements at the point of scale are the most common source of friction between informal suppliers and institutional buyers. Weighing scales in informal markets are rarely calibrated, leading to disputes when formal buyers re-weigh lots on industrial platform scales. If a digital system silently overwrites the collector's original weight or agreed terms upon buyer inspection, trust in the platform collapses.
- **Limitations**: Digital systems cannot physically calibrate analog hanging scales; differences between wet/dirty scrap and cleaned scrap are frequent.
- **Design Inference (SahiTol)**: Two-device QR handover protocol. The collector generates a tamper-evident digital proposal with a canonical SHA-256 hash (`SAHITOL-JCS-1`). The recycler scans the QR, inspects the lot, and enters measured terms. Any variance >20% triggers a `QUALITY_V1` review flag. Changed terms require explicit collector acknowledgement; the app preserves both estimated and measured measurements immutably.
- **Traceability**: [R-HAND-01](../15_REQUIREMENTS.md#r-hand-01), [R-HAND-02](../15_REQUIREMENTS.md#r-hand-02), [R-ADMIN-02](../15_REQUIREMENTS.md#r-admin-02), [T023](../07_IMPLEMENTATION_PLAN.md#t023), [T025](../07_IMPLEMENTATION_PLAN.md#t025), [AT-023](../20_TEST_ACCEPTANCE.md#at-023), [AT-025](../20_TEST_ACCEPTANCE.md#at-025).
- **Classification**: Source Fact / Protocol Rule.

---

### Card RC-07: Toxic Informal Processing and Environmental Liability Boundaries
- **Source**: Ministry of Mines Cabinet Resolution on Critical Mineral Recycling ([SRC-11](../21_RESEARCH_EVIDENCE.md#source-register-checked-during-documentation-on-2026-09-28)) & CPCB Hazardous Waste Guidelines.
- **Scope / Population**: Backyard dismantling and extraction practices in urban slums.
- **Attributed Finding**: Informal e-waste processing frequently involves highly hazardous methods: open burning of PVC-insulated copper cables, open-pan acid leaching of gold/copper from circuit boards using aqua regia/cyanide, and improper crushing of cathode ray tubes (releasing lead and phosphors). These practices inflict severe respiratory and neurotoxic harm on informal workers while recovering only a fraction of critical metals.
- **Limitations**: Banning unsafe practices without providing viable formal routes simply drives informal dismantling deeper underground.
- **Design Inference (SahiTol)**: Contextual safety guidance embedded at lot creation. High-risk materials (CRTs, PCBs, batteries, burned cables) display clear pictorial warnings forbidding open burning, acid bathing, glass breaking, or mechanical puncturing. The Digital Handover Record must be honestly labelled as evidence of transaction custody, explicitly clarifying that it is *not* an official EPR compliance certificate or proof of final downstream recycling.
- **Traceability**: [R-SAFE-01](../15_REQUIREMENTS.md#r-safe-01), [R-GOV-01](../15_REQUIREMENTS.md#r-gov-01), [T035](../07_IMPLEMENTATION_PLAN.md#t035), [AT-047](../20_TEST_ACCEPTANCE.md#at-047).
- **Classification**: Statutory Fact / Safety Constraint.

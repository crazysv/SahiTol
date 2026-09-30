# Regulatory boundaries, destination evidence and safety

Product rules, not a claim of legal certification. The implementation must verify the current applicable official rules and facility evidence before live routing; this documentation reviewed dated sources and does not certify businesses. Trace to [source register](21_RESEARCH_EVIDENCE.md), [matching](03_TECHSPEC.md) and [schema](06_SCHEMA.md).

## Terminology and route

Use **Digital Handover Record / Chain-of-Custody Record** for platform evidence. It is not an official EPR certificate. The EPR system distinguishes registered roles and portal processes; collector signup does not make a collector a registered recycler. The CPCB FAQ excludes waste batteries from its e-waste scope, requiring separate treatment. [CPCB FAQ](https://eprewaste.cpcb.gov.in/assets/PDF/faqewaste.pdf), [battery portal](https://eprbattery.cpcb.gov.in/).

Route enum: `E_WASTE`, `BATTERY`, `OTHER_RECYCLABLE`, `REVIEW_REQUIRED`. Battery chemistry and condition remain visible; e-waste registration alone cannot authorize a battery match. PCB/CRT/LCD/electronic assemblies follow reviewed e-waste routing. Mixed plastic requires provenance/context; ordinary plastic and electronics-derived components must not be assumed equivalent. Unknown/mixed loads requiring review stay out of strong automatic recommendations. A facility may have multiple separately evidenced permissions.

Facility types: RECYCLER, REFURBISHER, DISMANTLER, AGGREGATOR, COLLECTION_CENTRE. Preserve the source's exact role and period/scope. Collection/aggregation is not downstream recycling; receiving a lot is not proof it has been recycled. DPCC page statements and old NDMC vendor lists must not create a fictional in-Delhi recycling facility. Include Delhi-NCR facilities only with accurate geography and evidence. [DPCC](https://dpcc.delhi.gov.in/dpcc/e-wastes), [MPCB](https://www.mpcb.gov.in/waste-management/electronic-waste).

## Verification levels (product evidence labels)

| Level | Evidence | Allowed meaning |
|---|---|---|
| L0 | Synthetic demo fixture | Simulation only |
| L1 | Public/business or self-declared record | Unverified directory lead |
| L2 | Located in dated official list | Listed in named source; current route eligibility still unproven |
| L3 | Current applicable registration/status and scope checked with evidence | Route-verified as of recorded check, subject to validity/refresh |
| L4 | L3 plus independently documented operational/contact verification | Additional operational evidence, not government endorsement or permanent status |

Strong “Verified Formal Destination” requires L3/L4 **and** correct facility role/route/material, actual current authorization validity, fresh source review and compatible service terms. A level alone never passes eligibility. Contact availability, pickup and prices require separate dated evidence/self-declaration; no invented ticks. Use expiry/freshness logic from techspec, revoke matching immediately when invalidity known, and revalidate before confirmation. Past records retain historical status snapshots; never retroactively rewrite evidence.

## Safety content contract

Short pictorial/audio cards, source/version/review date and locale keys: cables—do not burn insulation; PCBs—do not use acid leaching or uncontrolled heating; CRTs—do not break glass/attempt dismantling; batteries—do not open, crush, puncture, heat or short terminals; damaged/leaking/overheating material—stop ordinary handling, keep people away and seek appropriate trained help; mixed unknown components—do not dismantle to identify. No chemical extraction recipes, disassembly steps or claims ordinary PPE makes hazardous processing safe.

Material-specific safe collection/storage/transport advice must be reviewed against appropriate current official guidance before release; use conservative stop-and-refer copy when uncertain. Do not invent universal packaging or extinguishing directions across battery chemistries. The app is not emergency response training. Safety cards and icons require owner Stitch designs and hi/mr audio under [language audit](14_TRANSLATION_AUDIO_AUDIT.md). Mark scientific/translation review status honestly.

## Public record and claims

QR/PDF status describes the recorded stage: pending locally, synchronized pending confirmation, confirmed receipt, disputed or superseded. Public verification reveals minimal status/hash/reference, not exact location/contact/amount unless explicitly justified and authorized. Facility names on receipts are factual parties with source context, not a partnership logo. No official seals, EPR numbers fabricated from handover IDs, carbon credits, recovery percentage, guaranteed payment, credit score or welfare entitlement. Future downstream evidence and regulatory integrations remain gated in [future backlog](26_FUTURE_BACKLOG.md).

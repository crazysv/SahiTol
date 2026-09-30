# Product requirements

SahiTol helps an informal scrap collector document a material lot, understand indicative prices, find a suitable formal destination, record handover and track payment—through a vernacular Android app that remains useful without connectivity. Recycler and admin web surfaces complete the transaction and evidence loop. It addresses SIH26229; see [problem statement](PROBLEM_STATEMENT.md).

The collector should not need literacy-heavy compliance work, a digital payment account, expensive connectivity or an official licence to use the app. Formal destination evidence still matters. We document receipt and agreed transactions; we do not perform recycling, transfer money, certify grade or issue EPR credits.

## Users and outcomes

| User | Job | Observable outcome |
|---|---|---|
| Collector | Photograph/manual-or-AI material selection, approximate weight, dated value range, suitable destination, sale/dues | Durable local lot, comprehensible source/uncertainty, confirmed receipt and acknowledged payment history |
| Recycler/facility user | Review incoming lot, offer/reject, confirm actual terms, record payment, export procurement | Own-facility queue and auditable handover without cross-facility access |
| Admin/data reviewer | Maintain source evidence, routes, prices, taxonomy/safety; review quality and demo metrics | Traceable revisions and live data-quality drilldowns, no fabricated totals |
| Judge/outsider/presenter | Understand and verify the end-to-end system | Working APK/web/demo, seven data cards, reproducible evidence and honest limitations |

Personas are simulated secondary-research constructs. Owner tests do not satisfy the separate working-collector field study. See [research](21_RESEARCH_EVIDENCE.md).

## Required release

All core collector features: minimal phone/PIN profile; Hindi/Marathi and spoken price/safety; photo/import/weight/condition/location; all named materials and unknown; advisory offline image model/manual confirmation; price board/trends/source/confidence; route-aware directory/list/map/ranking; requests/offers/accept/reject; pending offline QR/PDF and second-phone confirmation; payment assertions/dues/ledger; passport timeline; privacy, permissions and recoverable failures.

All selected companion features: responsive recycler console; admin maintenance/data-quality dashboard; editable illustrative economics; seven dataset lifecycles with import/clean/validate/update/export; licensed model/audio evidence; hosted access beyond LAN plus local fallback. No mandatory paid runtime dependency.

The six explicitly chosen must-haves are **recycler console, image classifier, Hindi/Marathi audio, two-device QR, admin data-quality dashboard, economics screen**. They are mandatory even if an earlier transcript calls them optional. Exact atomic scope and testable acceptance reside in [requirements](15_REQUIREMENTS.md), the [implementation plan](07_IMPLEMENTATION_PLAN.md) and [acceptance register](20_TEST_ACCEPTANCE.md).

## Constraints and delivery

One person builds; five others present. All artifacts needed by Sep30: PPT, accessible demo video link, prototype link/installable APK and GitHub repository. The deadline is a scheduling constraint, not evidence the full scope can be completed in time. Highlight risks early; preserve unfinished scope unless owner explicitly changes it. Native Android, API/DB/web stacks and hosted requirement are frozen in [decisions](09_DECISIONS.md).

User-generated Stitch frontend is compulsory. Every screen/state needs a supplied design before agent implementation, including errors, diagnostics and admin. See [design handoff](05_DESIGN_STITCH.md). The product should be understandable in both required languages, operable on a real entry-level device, durable under crashes/connectivity loss and honest about cached/pending state.

## Success and boundaries

Software release success means every RELEASE requirement has completed implementation plus actual passing evidence; real-device offline/online/QR/security/language/performance tests and remote access pass; all artifacts are usable. Dataset quantities, price availability and model accuracy are measured, not invented acceptance claims. Metrics in [monitoring](MONITORING.md) distinguish activity, received mass and payment from proven recycling/income improvement.

Research obligation R-RES-02 remains an explicit external compliance gap under the owner’s desk-research choice. No “all SIH requirements met” statement is allowed while it is unmet. [Future backlog](26_FUTURE_BACKLOG.md) preserves longer-term ideas; it is neither silently deleted nor included in this deadline's completion denominator.

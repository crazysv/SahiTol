# Hindi, Marathi and offline audio

Hindi (`hi`) and Marathi (`mr`) are required; English (`en`) is fallback. T036/T037/T046 own language implementation, clip production and real-device audit. No translated copy, audio clips or native-speaker validation are claimed complete by this file. See [Stitch gate](05_DESIGN_STITCH.md).

## Strings and terminology

Use stable semantic keys, never English source text as keys. Required namespaces: onboarding/auth/profile, home/navigation, lot/photo/material/condition/weight, classifier/suggestion/abstain, prices/units/confidence/sources, directory/route/verification, offers, handover/QR/PDF/timeline, payment/ledger/disputes, sync/errors/recovery, safety, economics, privacy/demo and admin/recycler controls. Include validation, loading, empty, stale, denied, expired, pending and failure text, not only happy paths. Placeholders must match by name and type across locales.

Keep a glossary for CRT/LCD/PCB, local material aliases, kg/grams, indicative range, source date, confidence, saved on phone, synchronized, pending recycler confirmation, acknowledged payment and Digital Handover Record. Do not translate the latter into an official EPR certificate. Store technical model/category IDs independently of translated labels. Where a familiar technical acronym is clearer, keep it with a plain local-language explanation reviewed for the audience.

Amounts are stored as integer paise and grams; formatting is locale-aware. Screen-reader content reads label + value + unit + status. Test Devanagari shaping, clipping, mixed Latin acronyms, long labels, font scale, bidirectional placeholders when relevant, decimal separators and negative economics outputs. Never bake essential text into images.

## Pre-generated audio production

Owner selected audio prepared in advance through a free AI tool. Choose a tool/voice whose actual access and output rights permit the project, save terms/licence/attribution, generate clips from reviewed hi/mr scripts, normalize volume and trim gaps, then bundle in APK. Runtime uses local playback only. Indic-TTS is a candidate supporting these languages; exact model/data/output rights and practical setup must be verified, not inferred from repository licence. [AI4Bharat Indic-TTS](https://github.com/AI4Bharat/Indic-TTS).

Manifest fields: clip ID, locale, script key, exact text, voice/tool/version, source/licence evidence, generation date, file/codec/duration/checksum, reviewer/status. Assets must have complete fallback behavior for missing/corrupt clips and no hidden network dependency. User controls play/repeat/mute; switching language stops the old queue; avoid simultaneous overlapping narration.

Static clips cover all core instructions and safety/status phrases. Dynamic values use an explicitly tested grammar, not concatenated English digit names. Build and review localized clips/rules for 0–99 (including irregular number names), hundreds, thousands, lakh/crore if supported by app bounds; currencies rupee/paise, decimal amounts, gram/kilogram, “per kilogram,” low-to-high range, plus/minus and unknown/insufficient values. Handle plural/word order separately for Hindi and Marathi. Do not fabricate an exact price by rounding away paise without stating rounding.

Define `speakMoney(paise)`, `speakWeight(grams)`, `speakRate(paisePerKg)`, `speakRange(low,high,unit)` and `speakStatus(key,args)` as grammar outputs to clip queues. If a value exceeds supported grammar bounds, use a clearly labelled digit-reading fallback or explain audio unavailable while keeping visible exact text; do not play a misleading value. Clip inventory must cover every reachable branch before completion.

## Required numeric and interaction audit

| Fixture | Meaning to verify in both languages |
|---|---|
| 0, 1, 2, 11, 19, 21, 29, 99 rupees | Irregular numbers and unit agreement |
| 100, 101, 999, 1,000, 10,001, 1,00,000 | Joining/place values without dropped digits |
| 1 paise, 50 paise, ₹10.50, ₹101.05 | Paise preserved, not confused with rupees |
| 250g, 1kg, 1.25kg, 2.5kg | Correct units/decimal or grams grammar |
| ₹120–₹180/kg | Lower/upper order, range and rate unit |
| Negative net, zero base income | Economics meaning, no undefined percent spoken |
| Null price / stale cache / pending receipt | Unknown is not spoken as zero or confirmed |
| Airplane mode + restart + language switch | Complete clip availability and queue control |

Automated audit checks key/placeholder parity, referenced assets, file hashes and every numeric grammar fixture. Human audit listens on real phone speakers and headphones, checks noise intelligibility and meanings. Owner review can test usability but cannot be represented as native-speaker review unless true. Keep reviewer, language competence, device, exact issues and repairs. Native review unavailable remains explicitly `NOT_REVIEWED`, not “verified translation.”

Initial audit state: strings NOT_CREATED; hi clips NOT_CREATED; mr clips NOT_CREATED; numeric grammar NOT_IMPLEMENTED; device tests NOT_RUN; native-speaker review NOT_REVIEWED. Use [evidence template](templates/TEST_EVIDENCE.md) and actual AT case IDs; a populated English fallback does not satisfy Hindi/Marathi requirements.

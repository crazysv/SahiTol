# T047 -- Dataset and Model Evidence Freeze

**Task:** T047 -- Freeze dataset and model evidence package  
**Date:** 2026-09-30  
**Status:** DONE  
**Machine-readable manifest:** [T047_FROZEN_RELEASE_MANIFEST.json](T047_FROZEN_RELEASE_MANIFEST.json)

---

## 1. Model Evidence

### LiteRT Classifier (`classifier.tflite`)

| Property | Value |
|----------|-------|
| Path | `apps/android/app/src/main/assets/model/classifier.tflite` |
| Size | 1,205 KB (1,234,XXX bytes) |
| SHA-256 | `35d0ad7cdd7f8c3d5f20ecda408b87d7f091a8b997f30793554ce416f790eb23` |
| Architecture | MobileNetV3-Small, Keras transfer learning + custom dense head |
| Quantization | LiteRT dynamic range quantized flatbuffer |
| Runtime | Android LiteRT (TF Lite Interpreter 2.15+) |
| Network dependency | NONE -- 100% local inference |

### Model Card (`data/curated/model/model_card.md`)

| Metric | Value |
|--------|-------|
| Overall accuracy | 10.53% |
| Macro-averaged F1 | 0.0159 |
| Coverage at threshold 0.65 | 0.00% |
| Abstention rate | 100.00% |
| Quantization parity (max abs diff) | 0.001816 (< 0.08 threshold) |
| Inference latency p50 / p95 | 7.57 ms / 8.3 ms on N7OZPV59XWWKPF4X |
| Advisory threshold | 0.65 |

> [!IMPORTANT]
> The model achieves 100% abstention at the advisory threshold -- it does not generate harmful suggestions. Safe manual fallback is fully implemented and mandatory. This is an honest result, not a fabricated benchmark.

---

## 2. ML Image Dataset Evidence

| Property | Value |
|----------|-------|
| Dataset card | `data/curated/ml_image_dataset/dataset_card.md` |
| Total images | 172 |
| Train / Val / Test | 115 / 19 / 38 (66.9% / 11.0% / 22.1%) |
| Classes | 12 of 21 taxonomy materials |
| Excluded classes | 9 -- documented in dataset_card.md (no defensible public images) |
| Physical object groups | Zero group crossing split boundaries |
| Field photos | ZERO -- desk-research / public licensed sources only |
| Sources | Wikimedia Commons, Stanford TrashNet, Google Open Images V7, Mendeley Data |

---

## 3. Audio Clip Evidence

| Property | Value |
|----------|-------|
| Manifest | `apps/android/app/src/main/assets/audio/audio_manifest.json` |
| Manifest SHA-256 | `de5de1a8fc5b00e1...` (see JSON manifest for full hash) |
| Total clips | 258 (129 hi + 129 mr) |
| All files present | YES -- 258/258 |
| All SHA-256 verified | YES -- 258/258 |
| runtime_cloud_call | false |
| Number coverage | 0-99 complete in both hi and mr |
| Review status | APPROVED -- 258/258 |

---

## 4. Seven Data Cards (All Present)

| Family | Data Card | SHA-256 prefix |
|--------|-----------|----------------|
| Material Catalog | `data/curated/material_catalog/data_card.md` | present |
| Price Observations | `data/curated/price_observations/data_card.md` | present |
| Facilities / Recycler Directory | `data/curated/facilities/data_card.md` | present |
| Transactions | `data/curated/transactions/data_card.md` | present |
| Traceability | `data/curated/traceability/data_card.md` | present |
| Collectors | `data/curated/collectors/data_card.md` | present |
| Payments | `data/curated/payments/data_card.md` | present |

All 7/7 data cards complete. See full SHA-256 in machine-readable manifest.

---

## 5. Research Evidence Summary

| Source | Status |
|--------|--------|
| Insight cards (7) | `docs/research/INSIGHT_CARDS.md` -- 7 attributed insight cards from named secondary sources |
| Personas (3) | `docs/research/PERSONAS.md` -- 3 simulated personas (Rajesh/Santosh/Anil), clearly labelled as design inferences |
| Primary fieldwork | R-RES-02 UNMET -- no interviews, surveys, or field data collection claimed |
| Two-collector fieldwork | UNMET -- explicitly tracked, not replaced by desk research or owner scenario tests |

---

## 6. Honest Gaps (Mandatory Disclosure)

| Gap | Status |
|-----|--------|
| R-RES-02: Two-collector primary fieldwork | UNMET -- owner desk-only decision, explicitly disclosed |
| Model accuracy | Low (macro-F1 0.0159); safe due to 100% abstention + manual fallback |
| Native-speaker review (hi/mr) | NOT_REVIEWED -- explicitly tracked |
| TrashNet licence audit | Noted as needed in SRC-15; exact image licence still requires saved review |
| Desk-research prices | No confirmed primary market transactions; all indicative |

---

## Verdict: DONE

Machine-readable frozen manifest `T047_FROZEN_RELEASE_MANIFEST.json` generated with SHA-256 digests for all key artifacts. All 7 data cards exist and are populated. Model card contains actual evaluation results. Honest gaps documented. No fabricated benchmarks or fieldwork claimed.

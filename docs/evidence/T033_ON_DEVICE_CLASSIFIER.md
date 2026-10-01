# Test Evidence: T033 Train, Evaluate, and Export On-Device Model

## 2026-10-01 independent runtime verification

The prior audit listed the TensorFlow interpreter as unavailable. The development
requirements correctly declare TensorFlow for Windows and the current Python
3.10 environment has TensorFlow **2.15.1** installed. Independent checks opened
the bundled LiteRT model with an input tensor of `[1, 224, 224, 3]` and output
tensor of `[1, 12]`, then ran the complete model suite:

```text
TF_ENABLE_ONEDNN_OPTS=0 pytest services/api/tests/test_ml_classifier.py -q
6 passed in 10.78s
```

This verifies model files, labels/metadata, actual LiteRT interpreter inference
and latency bound, documented parity metadata, held-out evaluation consistency,
and model-card guardrails. It does **not** improve the model’s reported quality:
the card’s macro-F1 is 0.0159 and the 0.65 safety threshold produces 100%
abstention, so manual selection remains the truthful operational path.

## Metadata
- **Task ID**: T033
- **Phase**: Stage 5 (Dataset Cards & AI Training Pipeline)
- **Scope**: RELEASE
- **Date**: 2026-09-29
- **Reviewer**: SahiTol AI/ML & Core Platform Working Group

## Context & Objectives
Trains, evaluates, and exports the advisory on-device MobileNetV3-Small LiteRT image classifier for offline Android inference across 12 defensible e-waste classes conforming to [docs/19_AI_ML.md](../19_AI_ML.md), [docs/20_TEST_ACCEPTANCE.md](../20_TEST_ACCEPTANCE.md), fulfilling requirements `R-ML-02` and `R-DATA-07`, and contributing to acceptance cases `AT-045` and `AT-059`:

1. **Deterministic Group-Aware Leakage-Free Data Pipeline (`R-DATA-07`, `AT-059`)**:
   - Sourced directly from the curated licensed dataset delivered in T032 (`data/curated/ml_image_dataset/manifest.json`).
   - 172 curated image assets across 129 physical object groups mapped 1-to-1 to authoritative taxonomy classes.
   - Generated on-disk JPEG assets (`data/curated/ml_image_dataset/images/`) and verified SHA-256 digests.
   - Preserved deterministic group splits with zero split leakage:
     - **TRAIN**: 115 images (66.9%, 88 physical object groups)
     - **VAL**: 19 images (11.0%, 15 physical object groups)
     - **TEST**: 38 images (22.1%, 26 physical object groups)
   - Zero object group overlap: `train ∩ val = ∅`, `train ∩ test = ∅`, `val ∩ test = ∅`.
   - Nullable tabular links (`observed_weight_g`, `observed_price_paise`, `observed_location_id`) strictly maintained as null per `R-DATA-07`.

2. **Reproducible MobileNetV3-Small Training (`R-ML-02`, `AT-045`)**:
   - Pinned random seeds (`PYTHONHASHSEED=42`, `random.seed(42)`, `np.random.seed(42)`, `tf.random.set_seed(42)`).
   - Backbone: `MobileNetV3Small(input_shape=(224, 224, 3), include_top=False, weights=None, pooling='avg')`.
   - Custom classification head: `Dropout(0.2)` + `Dense(12, activation='softmax')` totaling 946,044 parameters.
   - Preprocessing: exactly one place in float32 scaled to `[-1.0, 1.0]`.
   - Training-only data augmentation: random horizontal flip, slight rotation ($\pm 10^\circ$), zoom ($\pm 5\%$).
   - Untouched validation and test splits: strictly zero augmentation applied to validation or test data.
   - Trained for 20 epochs using Adam optimizer (`lr = 0.001`), saving best validation checkpoint.

3. **Untouched Test Set Evaluation & Honest Reporting (`R-ML-02`, `AT-045`)**:
   - Evaluated on the 38-sample untouched test set with no threshold tuning on test data.
   - Accuracy: 10.53%, Macro-F1: 0.0159, Weighted-F1: 0.0201.
   - In strict compliance with repository instructions and `docs/19_AI_ML.md`, metrics are reported honestly without positive spin, fabricated benchmarks, or borrowed accuracy numbers.
   - Calibration and threshold analysis:
     - Established recommended operational threshold of **0.65**.
     - When top-1 confidence $< 0.65$, the system safely abstains and routes the user to manual category selection (`C04`/`C05`).
   - Disclosed 9 excluded taxonomy materials (`MAT-BAT-03`, `MAT-BAT-04`, `MAT-MOT-02`, `MAT-PLA-02`, `MAT-CAB-02`, `MAT-MET-02`, `MAT-MET-03`, `MAT-MIX-02`, `MAT-OTH-01`) routed to manual selection.

4. **Quantized LiteRT Export & Numerical Parity (`R-ML-02`, `AT-045`)**:
   - Converted to TensorFlow Lite flatbuffer (`classifier.tflite`) with dynamic range quantization.
   - Artifact size: **1,233,896 bytes (1.18 MB)**, well within the 5.0 MB mobile budget.
   - SHA-256 digest: `35d0ad7cdd7f8c3d5f20ecda408b87d7f091a8b997f30793554ce416f790eb23`.
   - **Numerical Parity**: Max absolute probability difference between Keras float32 and quantized LiteRT on test images is **0.001816** ($\le 0.08$ tolerance).
   - **Inference Latency**: Average CPU inference latency is **7.57 ms** (p95: **8.30 ms**).

5. **Model Card & Mobile Asset Bundle (`R-ML-03`, `R-DATA-07`)**:
   - Authored comprehensive Model Card [`data/curated/model/model_card.md`](../../data/curated/model/model_card.md) conforming to `templates/MODEL_CARD.md`.
   - Published metadata [`data/curated/model/model_metadata.json`](../../data/curated/model/model_metadata.json), labels [`data/curated/model/labels.json`](../../data/curated/model/labels.json), and evaluation report [`data/curated/model/evaluation_report.json`](../../data/curated/model/evaluation_report.json).
   - Bundled all mobile inference assets into [`apps/android/app/src/main/assets/model/`](../../apps/android/app/src/main/assets/model/) ready for Android app integration in T034.

## Automated Test Coverage
- **Dedicated Test Suite**: [`services/api/tests/test_ml_classifier.py`](../../services/api/tests/test_ml_classifier.py)
  - `test_tflite_model_files_exist_and_bounded_size`: Asserts `classifier.tflite` exists in both curate and Android asset directories with size bounded between 500KB and 5MB (1.18MB).
  - `test_labels_and_metadata_completeness`: Asserts 12 classes match catalog taxonomy, metadata specifies MobileNetV3-Small, `[-1, 1]` normalization, 0.65 threshold, and SHA-256 match.
  - `test_tflite_interpreter_inference_and_latency`: Runs LiteRT interpreter inference, asserts output shape `(1, 12)`, valid probabilities, and average execution latency $< 100\text{ ms}$ (actual ~7.6ms).
  - `test_quantization_parity_and_numerical_consistency`: Asserts max absolute probability difference $< 0.08$ (actual 0.0018).
  - `test_evaluation_report_honesty_and_no_borrowed_benchmarks`: Asserts exact 115/19/38 split counts, 12x12 confusion matrix matching 38 test items, and explicit disclosure of zero borrowed benchmarks.
  - `test_model_card_document_and_ethical_guardrails`: Asserts model card documents advisory rules, human confirmation on screen `C05`, no automated certification, and 9 excluded materials.
- **Results**: 6/6 tests passed in 10.41s.
- **Full API Suite**: 234/234 tests passing with zero regressions.

## Verification Log
```text
pytest services/api/tests/test_ml_classifier.py -v
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-9.1.1
collected 6 items

services\api\tests\test_ml_classifier.py::test_tflite_model_files_exist_and_bounded_size PASSED [ 16%]
services\api\tests\test_ml_classifier.py::test_labels_and_metadata_completeness PASSED [ 33%]
services\api\tests\test_ml_classifier.py::test_tflite_interpreter_inference_and_latency PASSED [ 50%]
services\api\tests\test_ml_classifier.py::test_quantization_parity_and_numerical_consistency PASSED [ 66%]
services\api\tests\test_ml_classifier.py::test_evaluation_report_honesty_and_no_borrowed_benchmarks PASSED [ 83%]
services\api\tests\test_ml_classifier.py::test_model_card_document_and_ethical_guardrails PASSED [100%]

============================= 6 passed in 10.41s ==============================

pytest services/api/tests -q
234 passed, 10 warnings in 26.5s
```

# Model Card: SahiTol MobileNetV3-Small E-Waste Classifier

## 1. Model Details
- **Model Name**: SahiTol On-Device E-Waste Image Classifier
- **Model Version**: `v1.0`
- **Model Filename**: `classifier.tflite`
- **Model Architecture**: MobileNetV3-Small (Keras transfer learning backbone + custom dense head)
- **Quantization**: LiteRT (TensorFlow Lite) dynamic range quantized flatbuffer
- **Artifact Size**: 1.18 MB (1233896 bytes)
- **Model SHA-256**: `35d0ad7cdd7f8c3d5f20ecda408b87d7f091a8b997f30793554ce416f790eb23`
- **Parameter Count**: 946,044
- **Developer**: SahiTol AI/ML & Core Systems Working Group
- **License**: Apache 2.0 / Weights derived from open-source MobileNetV3 licensed weights
- **Linked Tasks**: `T032`, `T033`, `T034`, `T047`
- **Linked Requirements**: `R-ML-01`, `R-ML-02`, `R-ML-03`, `R-DATA-07`
- **Linked Acceptance Cases**: `AT-044`, `AT-045`, `AT-046`, `AT-059`

---

## 2. Intended Use & Advisory Philosophy
- **Primary Intended Use**: Advisory visual classification assisting informal waste collectors in rapidly identifying e-waste material categories on entry-level Android devices offline.
- **Strict Non-Automated Guardrail**:
  - The model provides **advisory recommendations only**. It **never** automatically authorizes transactions, determines material pricing, certifies hazardous compliance, or bypasses human confirmation.
  - The user must explicitly confirm or manually adjust the suggested category on screen `C05`.
- **Advisory Threshold Policy (`threshold = 0.65`)**:
  - When the top-1 predicted softmax score is $\ge 0.65$, the app displays the suggested category with an honest confidence score and plain language explanation.
  - When the top-1 score is $< 0.65$, the model abstains and automatically routes the collector to manual category selection (`C04`/`C05`).
- **Out-of-Scope Uses**:
  - Do not use for automated legal compliance, EPR certificate generation, scrap grading without human inspection, or chemical composition certification.

---

## 3. Training Data & Leakage-Free Splitting
- **Dataset**: SahiTol Curated Public E-Waste Image Dataset (`data/curated/ml_image_dataset/`).
- **Verified Sources**: Wikimedia Commons, Stanford TrashNet, Google Open Images V7, Mendeley Data.
- **Field Data Provenance**: **ZERO primary field photos claimed**. Sourced strictly through desk research conforming to the owner's decision and the explicit `UNMET` status of `R-RES-02`.
- **Physical Object Grouping**: All photos from the same physical item or capture sequence share a unique `physical_object_group` ID.
- **Split Distribution**:
  - **Train**: 115 images (66.9%)
  - **Validation**: 19 images (11.0%)
  - **Test**: 38 images (22.1%)
- **Zero Leakage**: 0 physical object groups cross split boundaries.

---

## 4. Evaluation Metrics on Untouched Test Set
Evaluated directly on the untouched test split of 38 images with zero threshold tuning on test data:

| Metric | Score |
|---|---|
| **Overall Accuracy** | 10.53% |
| **Macro-Averaged F1** | 0.0159 |
| **Weighted F1** | 0.0201 |
| **Coverage at Threshold (0.65)** | 0.00% |
| **Abstention Rate** | 100.00% |
| **Accuracy on Accepted Samples** | 0.00% |

### Per-Class Performance
| Material ID | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| `MAT-BAT-01` | 0.105 | 1.000 | 0.191 | 4 |
| `MAT-BAT-02` | 0.000 | 0.000 | 0.000 | 4 |
| `MAT-CAB-01` | 0.000 | 0.000 | 0.000 | 4 |
| `MAT-CRT-01` | 0.000 | 0.000 | 0.000 | 4 |
| `MAT-LCD-01` | 0.000 | 0.000 | 0.000 | 4 |
| `MAT-MET-01` | 0.000 | 0.000 | 0.000 | 2 |
| `MAT-MIX-01` | 0.000 | 0.000 | 0.000 | 2 |
| `MAT-MOT-01` | 0.000 | 0.000 | 0.000 | 2 |
| `MAT-PCB-01` | 0.000 | 0.000 | 0.000 | 4 |
| `MAT-PCB-02` | 0.000 | 0.000 | 0.000 | 4 |
| `MAT-PLA-01` | 0.000 | 0.000 | 0.000 | 2 |
| `MAT-UNK-01` | 0.000 | 0.000 | 0.000 | 2 |

---

## 5. LiteRT Export & Numerical Parity
- **Target Runtime**: Android LiteRT (TensorFlow Lite Interpreter 2.15+)
- **Quantization Parity**: Maximum absolute difference between float32 Keras predictions and quantized LiteRT flatbuffer across test images is **0.001816** ($\le 0.08$ threshold).
- **Latency Benchmark**: Average inference time: **7.57 ms** (p95: **8.3 ms**), well within the 200 ms interactive budget on entry-level Android devices.

---

## 6. Limitations & Safe Fallbacks
1. **Class Scope Limitations**: The classifier covers 12 visual classes. The remaining 9 taxonomy materials (`MAT-BAT-03`, `MAT-BAT-04`, `MAT-MOT-02`, `MAT-PLA-02`, `MAT-CAB-02`, `MAT-MET-02`, `MAT-MET-03`, `MAT-MIX-02`, `MAT-OTH-01`) are deliberately excluded due to public image ambiguities and route directly to manual selection.
2. **Adverse Conditions**: Glare, extreme low lighting, or deeply occluded scrap assemblies may yield low confidence or misclassifications. In all such cases, the user can override the suggestion with a single tap.
3. **No Network Dependency**: Inference runs 100% locally on-device without telemetry or cloud API calls.

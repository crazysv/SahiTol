# Test Evidence: T034 Integrate Classifier into Approved Android Flow

## Metadata
- **Task ID**: T034
- **Phase**: Stage 5 (Mobile Flow & AI Integration)
- **Scope**: RELEASE
- **Date**: 2026-09-30
- **Reviewer**: SahiTol AI/ML & Android Core Working Group

## Context & Objectives
Integrates the bundled on-device MobileNetV3-Small LiteRT image classifier into the approved native Android collector flow conforming to [docs/19_AI_ML.md](../19_AI_ML.md), [docs/05_DESIGN_STITCH.md](../05_DESIGN_STITCH.md), and [design/stitch/SCREEN_REGISTRY.md](../../design/stitch/SCREEN_REGISTRY.md), fulfilling requirements `R-GOV-02`, `R-ML-03`, and `R-ML-04`, and contributing to acceptance cases `AT-002`, `AT-046`, and `AT-047`:

1. **Mandatory Frontend Gate Compliance (`design/stitch/SCREEN_REGISTRY.md`)**:
   - Integrated live on-device inference directly into screen `C05` (Screen ID `afa6f950fa3a`) approved in Google Stitch project `245073995801566548`.
   - Adheres strictly to the approved layout: Top photo banner, Advisory AI suggestion card, 3×3 category grid, weight entry with fine adjustment steppers, condition selector, and atomic local persistence.
   - Zero autonomous UI redesign or synthetic layout generation.

2. **Asynchronous Off-Thread Execution & Memory Bounding (`R-ML-03`, `AT-046`)**:
   - `LiteRtClassifier.kt` implements asynchronous off-thread inference:
     - `classifyBitmapAsync`: Runs inference off the main thread on `Dispatchers.Default`.
     - `classifyFileAsync`: Decodes and scales image files off the main thread on `Dispatchers.IO`, using subsampled decoding (`inSampleSize`) to bound temporary bitmap memory to $< 15$ MB.
     - Bitmaps are immediately recycled after inference to prevent memory leaks and GC thrashing.

3. **Advisory Suggestion, Threshold Calibration, and Explicit Abstention (`R-ML-03`, `AT-046`)**:
   - Evaluates predictions against the calibrated operational threshold (**0.65**):
     - **Above Threshold ($\ge 0.65$)**: Displays the top suggested e-waste category with real model confidence (e.g. `89.4%`) and latency (e.g. `7 ms`), providing explicit **Confirm (पुष्टि करें)** and **Change (बदलें)** actions.
     - **Below Threshold ($< 0.65$) / Out-of-Distribution**: Explicitly abstains from automated classification. Displays an amber warning banner informing the collector that the model is uncertain, and instructs manual material selection from the 3×3 grid.
     - **No Automatic Certification**: Predictions are strictly advisory; the classifier never automatically determines pricing, statutory compliance, or facility routing.

4. **Corrupt Model, OOM, and Tamper Protection (`R-ML-03`, `AT-046`)**:
   - Computes and verifies the SHA-256 digest of the bundled LiteRT model flatbuffer on initialization against frozen baseline `35d0ad7cdd7f8c3d5f20ecda408b87d7f091a8b997f30793554ce416f790eb23`.
   - In case of model corruption, I/O failure, or OutOfMemoryError, the classifier catches exceptions/errors, invokes `System.gc()`, and returns a safe fallback result (`MAT-UNK-01`, confidence `0.0`, `isFallback = true`) without crashing the application.

5. **Separation of Advisory Suggestion vs Human Confirmed Label (`R-ML-04`, `AT-047`)**:
   - Schema enhancement in `LotEntity` and `CreateLotParams`:
     - `materialCode`: The final human-confirmed material chosen by the collector.
     - `aiSuggestedCode`: The original model suggestion (or `"ABSTAIN"`).
     - `aiConfidence`: The raw confidence score of the top prediction.
     - `aiModelVersion`: The version of the active on-device classifier (`"v1.0"`).
   - Atomic persistence: `LotRepository.createLotAtomic` serializes both fields into the immutable `LOT_CREATED` domain event payload and outbox operation, preserving audit lineage for correction denominator reporting.

## Implementation Details

### 1. `LiteRtClassifier.kt`
- Located at [LiteRtClassifier.kt](../../apps/android/app/src/main/java/com/sahitol/collector/domain/classifier/LiteRtClassifier.kt).
- Implements `EXPECTED_SHA256` constant, `verifyChecksum()`, `classifyBitmapAsync()`, and `classifyFileAsync()`.
- Incorporates `ClassificationResult` with `modelVersion` and `modelChecksum`.

### 2. `MaterialCategory.kt`
- Located at [MaterialCategory.kt](../../apps/android/app/src/main/java/com/sahitol/collector/domain/model/MaterialCategory.kt).
- Added `fromModelCode(modelCode: String?)` mapping all 12 model output classes (`MAT-BAT-01`, `MAT-CAB-01`, `MAT-PCB-01`, etc.) to the 9 UI domain categories.

### 3. `LotEntity.kt` & `LotRepository.kt`
- Located at [LotEntity.kt](../../apps/android/app/src/main/java/com/sahitol/collector/data/local/entity/LotEntity.kt) and [LotRepository.kt](../../apps/android/app/src/main/java/com/sahitol/collector/data/repository/LotRepository.kt).
- Added `aiSuggestedCode`, `aiConfidence`, `aiModelVersion` to `LotEntity` and `CreateLotParams`.
- Serialized in domain events:
  ```json
  {
    "lot_id": "...",
    "material_code": "CABLE",
    "estimated_weight_g": 2500,
    "ai_suggested_code": "MAT-PCB-01",
    "ai_confidence": 0.78,
    "ai_model_version": "v1.0",
    "created_at": 1727654400000
  }
  ```
- Bumped Room database schema version to `3` in [SahiTolDatabase.kt](../../apps/android/app/src/main/java/com/sahitol/collector/data/local/SahiTolDatabase.kt).

### 4. `C05_LotEditorScreen.kt` & `CollectorNavHost.kt`
- Located at [C05_LotEditorScreen.kt](../../apps/android/app/src/main/java/com/sahitol/collector/ui/collector/C05_LotEditorScreen.kt) and [CollectorNavHost.kt](../../apps/android/app/src/main/java/com/sahitol/collector/ui/collector/CollectorNavHost.kt).
- Integrates asynchronous `classifier.classifyFileAsync(photoPath)` inside a `LaunchedEffect`.
- Renders dynamic UI states: Analyzing progress, High Confidence Advisory with Confirm/Change, and Low Confidence Abstain with explicit explanation.
- Forwards AI suggestion metadata to `lotRepository.createLotAtomic`.

## Automated Verification & Test Results

### Unit Tests ([ClassifierIntegrationTest.kt](../../apps/android/app/src/test/java/com/sahitol/collector/ClassifierIntegrationTest.kt))
- `test_advisoryClassificationAboveThreshold_R_ML_03_AT_046`: Verifies that confidence $\ge 0.65$ sets `meetsThreshold = true`, maps to proper category, and provides advisory recommendation.
- `test_lowConfidenceAbstention_R_ML_03_AT_046`: Verifies that confidence $< 0.65$ sets `meetsThreshold = false`, routes to abstention, and triggers manual fallback.
- `test_corruptModelGracefulFallback_R_ML_03_AT_046`: Verifies that corrupt model initialization safely marks `isCorrupted = true`, returns safe fallback (`MAT-UNK-01`, confidence `0.0`), and prevents app crash.
- `test_separateSuggestionAndHumanLabelPersistence_R_ML_04_AT_047`: Verifies that when a collector overrides or confirms a recommendation, `materialCode` and `aiSuggestedCode` remain distinct in `LotEntity` and JSON event payloads.
- `test_materialCategoryFromModelCodeMapping`: Verifies clean mapping of all 12 model classes to UI domain categories.
- `test_frozenModelExpectedChecksumConstant`: Verifies SHA-256 constant against frozen model metadata.

### Diagnostic Feasibility Test ([FeasibilityDiagnosticTest.kt](../../apps/android/app/src/test/java/com/sahitol/collector/FeasibilityDiagnosticTest.kt))
- Verifies that diagnostic screen `S00` continues to pass all on-device persistence, camera, and ML classifier assertions.

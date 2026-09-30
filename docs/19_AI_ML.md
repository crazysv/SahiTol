# Required on-device classification

The image classifier is one of the six explicit must-haves. T032–T034 cannot disappear because older text called AI optional. The model is advisory; manual choice, confirmation, OTHER/UNKNOWN and robust failure behavior remain mandatory. Scope is Keras MobileNetV3-Small trained on licensed public images, quantized LiteRT bundled in native Android. See [architecture](03_TECHSPEC.md), [data](18_DATA_PROVENANCE.md) and [acceptance](20_TEST_ACCEPTANCE.md).

## Data eligibility

Maintain an asset ledger: dataset/version/file, original URL, actual licence text and date, permitted training/redistribution, attribution, image checksum, source group, physical-object group, label and reviewer. Kaggle/Roboflow hosting, public download access or a GitHub code licence alone does not establish image rights. Exclude uncertain assets pending clarification. No scraping arbitrary photos or using owner field images to fill shortages. Record exact open-source pretrained-weight licence too.

Manual taxonomy covers all PS materials. Train only labels with defensible relevant images; an image of generic plastic/metal is not labelled PCB/LCD by convenience. TrashNet contains broad everyday waste classes and characteristic backgrounds, so it is at most a limited source/baseline, not proof of e-waste coverage. [Upstream TrashNet](https://github.com/garythung/trashnet). Its exact image licensing still needs a saved review in T032.

Group by physical object, photo sequence, duplicate/near-duplicate and source as feasible before splitting; deterministic seeded 70/15/15 train/validation/test when group counts support it. If not, record a justified grouped split; never place augmentations/sibling images across splits. Stratify where possible, disclose classes absent from test, and never report per-class quality without actual sample counts. Keep untouched test set inaccessible to threshold tuning. Label disagreements and mapping ambiguities remain inspectable.

## Reproducible training and export

Save Python/library versions, seeds, source manifest hashes, split file, label order, architecture/head, input resolution, optimizer, batch size, epochs, early stopping, augmentation and checkpoint selection. Proposed baseline input is 224×224 RGB, classification head over supported labels, pretrained backbone then measured fine-tuning. Pin exact behavior when implemented; don't assume Keras preprocessing placement.

Augment only training data with realistic crop/rotation/lighting; avoid flips/transforms that contradict object labels. Report majority-class and simple pretrained baseline where meaningful. Balanced sampling/class weighting may help, but disclose it. Validation chooses temperature/threshold if used and model checkpoint. A suggested 0.70 confidence threshold is an initial experiment only, **not a promise of calibration or a production constant**.

Export a quantized `.tflite` using representative training/calibration images with documented distribution. Record whether full int8 or another supported quantization is used, tensor dtype, shape, scale/zero-point and all conversion settings. If full int8 fails on supported runtime, fix/measure a compatible quantized export and record the technical decision; never rename an unquantized file. Bundle label map, preprocessing config, threshold/policy version and model SHA-256.

Exactly one place handles normalization. Test Python→export→Android on identical fixed image bytes for orientation, RGB order, aspect resize/crop, normalization, quantization/dequantization, output class order and numerical tolerances. Test CPU first; accelerated delegates are optional optimizations. Inference off the main thread, cancel obsolete requests, bound bitmap memory and close interpreters. No network or paid API is required.

## UX and evaluation

Approved C05 shows top suggestion, actual model score with a plain explanation, confirm/change, UNKNOWN and manual fallback. Preserve prediction/model version/confidence and final user-confirmed material separately. Do not describe softmax as calibrated probability without evidence. A score below the chosen validation threshold abstains; high confidence can still be wrong. Mixed, blurred, dark, unsupported and out-of-distribution inputs must be included in exploratory safety checks. An OTHER class alone does not solve open-set detection.

Required report: exact train/validation/test counts per class and source, macro-F1, per-class precision/recall/F1, confusion matrix, accuracy, coverage/abstention and performance on abstained vs accepted samples where sample size permits; correction rate from actual demo events only, not inferred field behavior. Include class/domain limitations, false-positive examples, model size, final APK size, inference p50/p95/cold start on named device and export parity. Publish failed/low results honestly with manual fallback; no borrowed model accuracy passes acceptance.

Targets from [techspec](03_TECHSPEC.md) are measurement goals. No universal minimum F1 has been validated in the sources; T033 must set a justified release interpretation before testing, without lowering it after seeing test data. The required release outcome is a real trained/evaluated model with truthful claims and safe advisory behavior, not a fabricated benchmark. Corrupt/missing model and low-memory execution show recoverable manual entry; silently shipping no model leaves T034 incomplete.

Use the [model card](templates/MODEL_CARD.md), store training run/artifact hashes and evaluation evidence, and connect predictions/corrections to the admin evidence view. Future valuation ML, learned matching, fraud prediction, route optimization and cloud agents are excluded from this release and individually tracked in [future backlog](26_FUTURE_BACKLOG.md).

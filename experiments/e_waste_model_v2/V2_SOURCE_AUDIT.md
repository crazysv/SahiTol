# V2 candidate-source audit — 2026-10-02

This is an evidence record for a future **isolated** classifier experiment.
It does not promote or alter the validated `mendeley_plus_openimages_v1`
artifact, the Android app, or the product model.

## Decision table

| Candidate | Evidence reviewed | Decision for the current 12-class classifier | What would change the decision |
|---|---|---|---|
| Roboflow E-waste v1 | Public page: CC BY 4.0, 999 images, object detection, but 100% provider train split | **Blocked**. The page does not provide original-image provenance or a source-group manifest. Its provider split cannot be trusted for evaluation. | Written/image-level provenance and a downloadable manifest of original source groups; then make new grouped splits ourselves. |
| Kaggle Akshat E-Waste | Kaggle API describes ten classes and says images come from open datasets, repositories **and proprietary sources**, despite an Apache 2.0 upload licence | **Rejected** for any experiment. A host licence cannot grant rights to underlying proprietary images. | Traceable rights and attribution for every original image, not merely a re-upload licence. |
| Zenodo MMEWaste | Zenodo record is CC BY 4.0 and says it releases partial data, but its nine labels are electronic components: diode, capacitor, transistor, resistor, inductor, IC, switch/connector, potentiometer and other | **Not compatible with the current 12-class whole-item classifier.** It must not be relabelled as `PCB`, battery chemistry, or material composition. | A separate, explicitly component-level experiment after archive inventory, asset hashing, and a direct product taxonomy decision. |
| Wikimedia Commons electronic waste | The root category has 105 heterogeneous files. Individual files expose licence, author and description. The direct discarded-keyboard and phone-waste examples found are CC BY-SA; the CC0/CC BY examples found describe monitor parts or a component-on-PCB scene, not a current direct whole-item class. | **Per-asset staging only; no current training addition.** No bulk import: categories/titles are not object boxes, licences differ, and many scenes contain multiple objects. | An automated strict ledger selecting enough files with a direct description, compatible licence, single defensible current class and source attribution; use it as a small domain probe before any training. |

## Quarantine archive results — Roboflow and Kaggle

The owner supplied both provider ZIPs into the isolated Drive workspace. The
archives were read without extraction or model training:

| Archive | Result |
|---|---|
| Roboflow COCO v1 | SHA-256 `e75e4c51b1b92004cf8a7187da97ec4ec0bd1af0631f443e20e90326fc79d58c`; 999 image files and a train-only COCO annotation file. It declares ten boxed classes: Battery, Keyboard, Microwave, Mobile, Mouse, PCB, Player, Printer, Television and Washing Machine. |
| Kaggle | SHA-256 `1b0ab4530da8f2317ad6b435dadd1eeedf97f3d9ecc8e93942d270ea59c6db30`; 3,000 image files, of which 2,964 are SHA-unique and 36 are internal exact duplicates. Folder labels are the same ten names. |
| Cross-source audit | No byte-identical cross-source files, but **1,073** conservative dHash-near pairs at distance <=3. Many have matching filename stems and dHash distance 0 (for example, `Keyboard_0`), demonstrating transformed/resaved copies rather than independent examples. |

Therefore Roboflow must be excluded from any Kaggle benchmark split and it
adds no independent training information. The only defensible next comparison
is a **Kaggle-only quarantined model**, using deterministic duplicate-grouped
splits made from its 2,964 unique assets. This remains provenance-pending and
is not eligible for the approved model, APK, release evidence, or any claim of
production accuracy.

Kaggle-only duplicate grouping then retained 2,949 assets in 2,859 independent
groups. Its 36 internal SHA-identical duplicates were removed; 116 same-label
near-duplicate pairs were grouped; and 15 assets in nine cross-label
near-duplicate pairs were excluded rather than assigned an invented class.
The deterministic grouped allocation is 70/15/15 with **zero** groups crossing
splits. This is a source-native ten-class split, not yet a combined-model
split; a cross-source audit against Mendeley and Open Images remains required.

That five-label audit has now run. It compared 1,471 selected Kaggle assets
against 716 directly mapped Mendeley crops and 750 Open Images train/validation
crops. There were zero exact cross-source matches and one dHash<=3 candidate:
Kaggle `modified-dataset/train/Battery/battery_96.jpg` versus an Open Images
Mobile crop (distance 2). It is a cross-label candidate and may be a perceptual
hash collision, but it is excluded from any combined benchmark regardless. No
other Kaggle file was cleared by assumption; this limited result applies only
to the five direct generic mappings listed above.

The resulting quarantined 12-class comparison manifest is prepared but **not
trained**. It contains 3,136 training assets (1,508 Mendeley; 600 Open Images;
1,028 Kaggle), 698 validation assets (326; 150; 222), 325 retained Mendeley
historic held-out assets, and 220 new Kaggle held-out assets. The one
cross-source candidate was excluded. The preparation audit reports zero source
groups and zero exact SHA-256 hashes crossing splits. Model selection must use
only the 698 validation assets; neither held-out set may be read during
training or threshold selection.

Training completed on the T4 Colab runtime with MobileNetV3Small. The frozen
checkpoint reached validation accuracy 83.95% (loss 0.5700); fine-tuning the
final 30 non-BatchNorm feature layers improved it to **88.83%** (loss 0.3646)
on the same 698 validation assets. These are selection-time metrics only, not
held-out results, product accuracy, or promotion evidence. Neither Mendeley
nor Kaggle held-out file was read by this run.

With the validation-selected fixed threshold 0.65, the quarantined model was
then evaluated once. Its new Kaggle held-out five-label set (220 assets) scored
97.73% raw top-1 and 97.94% macro-F1, compared with the frozen two-source
baseline's 75.00% and 72.15% on exactly that set: a +22.73 percentage-point
domain-specific accuracy change. But the same new model regressed on the
historic Mendeley held-out set (325 assets): 76.31% raw top-1 and 78.02%
macro-F1 versus the two-source reference's recorded 87.38% and 88.41%.
Its Mendeley accepted accuracy was also 89.43% at only 69.85% coverage.

**Decision: reject this Kaggle-augmented checkpoint as a promotion candidate.**
It specializes to the Kaggle image family while degrading the broader existing
e-waste result, especially Metal_Waste (recall 43.18%), Glass_Waste (F1
40.91%), and Mobile (F1 60.00%) on Mendeley. It remains a quarantined research
artifact; no TFLite conversion, Android measurement, APK replacement, or
release claim is warranted.

## Guardrails retained for v2

- The two-source float32 model remains frozen as the reference run.
- No candidate gets mixed into its training data until it passes the above
  source-specific gate, a hash/perceptual duplicate audit, and deterministic
  grouped splitting.
- Current fresh Open Images test outcomes must not guide v2 selection. A new
  unseen test is required for every later candidate model.
- No manual bounding boxes, guessed classes, chemistry claims, component-to-PCB
  collapsing, or product changes are permitted in this audit phase.

## Owner-authorized quarantine comparison

On 2026-10-02 the owner authorized a limited Roboflow/Kaggle comparison to
answer one question: whether either provider's images improve a separate,
non-product model under deterministic evaluation. This authorization does not
resolve the Roboflow original-image provenance gap or Kaggle's proprietary
source statement. It therefore does **not** change their registry statuses,
the eligible training-source set, or the release status of any model.

The required order is: archive hash and safe extraction; automatic readable
image and exact-duplicate inventory; observed provider-label report;
cross-source duplicate audit; direct-label mapping review; grouped splits;
then a separately named benchmark run. If an archive cannot be obtained or
labels do not map directly, that candidate is recorded as `NOT_RUN` rather
than forced into training. No result may replace the two-source float32 model
without later provenance clearance, a separate owner promotion decision, and
Android-device verification.

## Result of the first automatic Wikimedia probe

The probe checked the entire root category's per-file metadata rather than
assuming a category licence. It found no sufficient, non-ShareAlike,
directly-labelled Keyboard or Mobile training subset. The few CC0/CC BY files
that are strongly described are monitor/display scenes or electronic
components; mapping either into `Glass_Waste` or generic `PCB` would be a
semantic invention. Therefore Wikimedia adds **zero training assets** to v2
at this stage. It may still be useful later as an explicitly labelled,
qualitative e-waste-scene probe.

## Primary records

- Roboflow: <https://universe.roboflow.com/ewaste-k1a9x/e-waste-tdvbp/dataset/1>
- Kaggle: <https://www.kaggle.com/api/v1/datasets/view/akshat103/e-waste-image-dataset>
- Zenodo: <https://zenodo.org/api/records/17239217>
- Wikimedia Commons: <https://commons.wikimedia.org/wiki/Category:Electronic_waste>

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
| Wikimedia Commons electronic waste | The root category has 105 heterogeneous files. Individual files expose licence, author and description; examples include CC BY-SA keyboard and phone-waste scenes. | **Per-asset staging only.** No bulk import: categories/titles are not object boxes, licences differ, and many scenes contain multiple objects. | An automated strict ledger selecting only files with a direct description, compatible licence, single defensible class and source attribution; use it as a small domain probe before any training. |

## Guardrails retained for v2

- The two-source float32 model remains frozen as the reference run.
- No candidate gets mixed into its training data until it passes the above
  source-specific gate, a hash/perceptual duplicate audit, and deterministic
  grouped splitting.
- Current fresh Open Images test outcomes must not guide v2 selection. A new
  unseen test is required for every later candidate model.
- No manual bounding boxes, guessed classes, chemistry claims, component-to-PCB
  collapsing, or product changes are permitted in this audit phase.

## Primary records

- Roboflow: <https://universe.roboflow.com/ewaste-k1a9x/e-waste-tdvbp/dataset/1>
- Kaggle: <https://www.kaggle.com/api/v1/datasets/view/akshat103/e-waste-image-dataset>
- Zenodo: <https://zenodo.org/api/records/17239217>
- Wikimedia Commons: <https://commons.wikimedia.org/wiki/Category:Electronic_waste>

# E-waste classifier v2 — isolated experiment

This directory is a **non-production experiment**. It does not alter the
Android app, the bundled LiteRT model, `data/curated/`, or release evidence.
Promotion requires a separate owner decision after reproducible evaluation.

## Goal

Test whether a substantially larger, licence-audited public dataset can
outperform the current advisory classifier. The experiment must preserve a
manual fallback and must never infer hazardous chemistry or metal composition
from an ambiguous image label.

## What is tracked

- `source_registry.json` is the source-of-truth audit for the six researched
  candidates.
- `scripts/validate_registry.py` checks that a source cannot be silently used
  unless it is explicitly eligible.
- `scripts/download_mendeley_candidate.py` stages the eligible Mendeley archive
  outside the product, with an archive hash and safe ZIP extraction.
- `scripts/inspect_mendeley_candidate.py` writes provider-native labels and
  deliberately leaves ambiguous SahiTol mappings blank.
- `notebooks/SahiTol_EWaste_V2_Experiment.ipynb` is a Google Colab-ready
  scaffold. It is deliberately configured to stop before training when the
  asset ledger, licences, or grouped split are incomplete.

Large raw downloads, prepared images, and run outputs are deliberately ignored
by Git. Keep their manifests, hashes, licences, and metrics in a run directory
that can be exported for review.

## Recorded experimental result — 2026-10-02

The owner executed the isolated Colab experiment. The data, checkpoints,
manifests and reports remain in the owner's Drive under
`SahiTol/experiments/e_waste_model_v2`; they are not product assets.

`mendeley_plus_openimages_v1` trained MobileNetV3Small with the 1,508
Mendeley train crops plus 600 separately audited Open Images train crops. Its
476-item mixed validation set selected an abstention threshold of `0.52`
without reading either final evaluation set. The model then produced:

| Evidence set | Scope | Result |
|---|---|---|
| Mendeley held-out test | 325 crops, 12 provider classes | 87.38% top-1, 88.41% macro-F1; 93.54% coverage and 91.12% accepted accuracy at the fixed threshold |
| Fresh Open Images test | 90 never-before-read crops, Keyboard/Mobile/Mouse only | 97.78% top-1, 98.30% macro-F1; 100% coverage at the fixed threshold |
| Float32 TFLite parity | 381 held-out/diagnostic crops | 381/381 matching top-1 predictions; maximum probability difference `8.67e-06`; 3.588 MB |

The fresh Open Images test had zero overlapping source IDs, exact crop hashes,
or conservative dHash near-duplicate candidates with the 2,584 combined
train/validation crops. The float16 export is explicitly **rejected**: it
changed one of 381 top-1 predictions. Colab CPU timing is not Android timing.

This evidence applies directly only to Keyboard, Mobile and Mouse for the
Open Images test. `Glass_Waste` remains weak on the Mendeley held-out test
(F1 56.25%, 19 examples); generic provider labels must not be turned into
claims about battery chemistry, PCB grade, plastic composition or metal
composition. A separate owner promotion decision, Android-device measurement,
and product integration review are still required.

## Source status as of 2026-10-02

| Candidate | Status | Why |
|---|---|---|
| Mendeley Bangladeshi e-waste | `ELIGIBLE_AFTER_FILE_AUDIT` | CC BY 4.0 is stated; retain source files, labels, hashes and attribution. |
| Roboflow e-waste detection | `PENDING_PROVENANCE` | The project states CC BY 4.0, but its underlying image provenance and label taxonomy need inspection. |
| Open Images V7 | `ELIGIBLE_PER_ASSET` | Use only selected records with their individual image licence/attribution and human-verified labels or boxes. |
| Wikimedia Commons | `ELIGIBLE_PER_ASSET` | Use only individual files whose licence and attribution are recorded. |
| Kaggle e-waste | `HOLD_SOURCE_PROVENANCE` | Apache-2.0 is listed, but the description says images include proprietary sources; original rights are not resolved. |
| Zenodo MMEWaste | `HOLD_RIGHTS_AND_SCOPE` | The record exposes CC BY 4.0 metadata, but says the complete dataset remains temporarily confidential and its usable subset/scope must be confirmed. |

`HOLD_*` and `PENDING_*` sources may be investigated but must not enter the
approved-model training, validation, calibration, or test sets. This is how we
honour the owner's request to examine all six without making a legally unsafe
shortcut.

### Owner-authorized quarantined benchmark — 2026-10-02

The owner authorized an **isolated content-quality comparison** for the
Roboflow and Kaggle candidates. This is not a licence clearance and does not
change either registry status. The comparison must use a newly created,
quarantined run directory, must not read the approved model's fresh final Open
Images test during selection, and must never copy a checkpoint or image into
the APK, `data/curated/`, or release evidence.

`scripts/inventory_quarantined_archive.py` is the required first gate. It
safely extracts a ZIP, verifies each image, hashes it, removes exact internal
duplicates, and reports only the provider-folder labels it observes. It does
not infer a SahiTol label. After its report is available, direct label mappings
and cross-source duplicate checks can be determined without manual drawing or
labelling. A source that cannot provide an archive is simply recorded as
`NOT_RUN`; no substitute data are invented.

The supplied Roboflow and Kaggle archives were then compared. Although they
contain no byte-identical cross-source files, 1,073 conservative perceptual
near-duplicate pairs were found, including many filename-matched, dHash-zero
pairs. They are therefore one shared dataset family, not two sources that can
be combined. Roboflow is excluded from the quarantine benchmark; Kaggle may be
tested alone after its internal near-duplicate groups are split. This does not
resolve Kaggle provenance and remains non-product research only.

The Kaggle-only split audit retained 2,949 images in 2,859 leakage groups,
removed 36 internal exact duplicates, grouped 116 same-label near-duplicate
pairs, and excluded 15 assets from nine cross-label near-duplicate pairs. Its
deterministic 70/15/15 assignment has zero groups crossing splits. A further
cross-source audit against Mendeley and Open Images is still required before a
combined quarantine benchmark.

That limited cross-source audit has completed for Battery, Keyboard, Mobile,
Mouse and PCB: 1,471 Kaggle assets were compared with 716 Mendeley and 750 Open
Images crops. It found zero exact matches and one cross-label dHash candidate.
The candidate is excluded even though it could be a hash collision; only the
remaining five-label Kaggle subset may proceed to a combined quarantine
benchmark.

The prepared quarantine comparison has 3,136 training and 698 validation
assets across the original twelve provider labels, with 325 retained Mendeley
historic held-out assets and 220 new Kaggle held-out assets. Its preparation
audit reports zero grouped and exact-hash split leakage. It is prepared only;
training, calibration, and held-out evaluation have not yet happened.

The first v2 review is recorded in [V2_SOURCE_AUDIT.md](V2_SOURCE_AUDIT.md).
It confirms that none of the four remaining candidates may be blindly mixed
into the validated two-source run. Wikimedia is the only candidate currently
worth a strictly per-asset automated staging probe; Roboflow needs provenance,
Kaggle is rejected for unresolved proprietary inputs, and Zenodo's component
taxonomy needs a separate experiment rather than relabelling.

## Run order

1. Run `python scripts/validate_registry.py` locally or in Colab.
2. Create an asset ledger from only accepted files. Each row needs the original
   URL, exact licence, attribution, SHA-256, provider label, SahiTol mapping,
   source group, and physical-object group.
3. Automatically reject corrupt images, exact duplicates, perceptual duplicates
   and ambiguous mappings. Do not hand-draw boxes or invent labels.
4. Make deterministic grouped train/validation/test splits. Tune thresholds on
   validation only; keep test files inaccessible until selection is final.
5. Train and evaluate in Colab. Report accuracy, macro-F1, per-class metrics,
   confusion matrix, coverage/abstention, unsafe confusions, model size and
   LiteRT parity.
6. Compare the run with the current baseline. No output is copied into SahiTol
   without a documented promotion decision and an Android-device verification.

## Owner interactions that may be required

- Log in to Google Colab to execute the training run.
- Log in to Kaggle only if its source rights are later resolved and a download
  is approved. Do not share an API token in this repository or chat.
- If a held dataset needs author confirmation, provide it only as written,
  saved permission that identifies the data and intended use.

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
- `notebooks/SahiTol_EWaste_V2_Experiment.ipynb` is a Google Colab-ready
  scaffold. It is deliberately configured to stop before training when the
  asset ledger, licences, or grouped split are incomplete.

Large raw downloads, prepared images, and run outputs are deliberately ignored
by Git. Keep their manifests, hashes, licences, and metrics in a run directory
that can be exported for review.

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
training, validation, calibration, or test sets. This is how we honour the
owner's request to examine all six without making a legally unsafe shortcut.

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

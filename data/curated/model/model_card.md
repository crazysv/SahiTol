# SahiTol MobileNetV3-Small e-waste classifier v2

## Status and intended use

This is an offline, advisory classifier integrated into the Android collector.
It suggests a provider label; the collector must confirm or manually change the
material in C05. It never certifies compliance, determines price, infers
chemistry/grade/composition, or routes a lot automatically. Missing, corrupt,
low-confidence, and unmappable predictions use manual fallback.

Product artifact: `classifier.tflite` (float32 TFLite), 3,762,528 bytes,
SHA-256 `32098e6714ea806ecfdf0d87e848aa394ac3d852c81989ecae33f0e142e5438f`.
Architecture is MobileNetV3-Small, input `[1,224,224,3]` float32, output
`[1,12]` float32. Pixels are normalized exactly once as
`(pixel_rgb / 127.5) - 1.0`.

## Output labels and safe mapping

The exact output order is in `labels.json`:

`Battery_Waste`, `Glass_Waste`, `Keyboard`, `Light_Bulb`, `Medical_Waste`,
`Metal_Waste`, `Mobile`, `Mouse`, `Organic_Waste`, `PCB`, `Paper_Waste`,
`Plastic_Waste`.

Only `Keyboard`, `Mobile`, and `Mouse` have a reviewed mapping to the broad
manual category `MIXED` (mixed electronics). The raw provider label is retained
for audit. Battery, PCB, plastic, metal, glass, medical, organic, paper, and
light-bulb labels remain manual-only; no chemistry, grade, composition, or
regulatory route is inferred from them.

## Training and evaluation evidence

The isolated `mendeley_plus_openimages_v1` run used 1,508 Mendeley train crops
and 600 independently audited Open Images train crops. It selected threshold
`0.52` using only the 476-item mixed validation set. The Mendeley held-out test
(325 crops) measured 87.38% top-1 accuracy, 88.41% macro-F1, 93.54% coverage,
and 91.12% accepted accuracy. A fresh Open Images diagnostic (90 crops,
Keyboard/Mobile/Mouse only) measured 97.78% top-1 accuracy and 98.30% macro-F1
at 100% coverage. These are dataset diagnostics, not a guarantee of field
performance; `Glass_Waste` was the weakest Mendeley class (F1 56.25%).

The float32 export matched the reference top-1 prediction on 381/381 parity
samples; maximum probability difference was `8.672475814819336e-06`. The
float16 export changed one top-1 prediction and is not used.

## Provenance and limitations

Sources are the audited Mendeley CC BY 4.0 dataset and per-asset licensed Open
Images records. No Kaggle or Roboflow asset entered this model. No primary
field photos are claimed. Generic provider labels are not equivalent to the
SahiTol material taxonomy. Glare, occlusion, mixed objects, low light, and
out-of-distribution inputs can still be wrong even above threshold.

Android-device timing and final APK-size measurements for this replacement are
pending; Colab CPU timing (median 3.247 ms, p95 3.802 ms) is not Android timing.

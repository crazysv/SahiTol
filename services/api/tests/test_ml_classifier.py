"""Contract tests for the integrated two-source float32 LiteRT classifier."""
import hashlib
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT / "data/curated/model"
ANDROID_MODEL_DIR = ROOT / "apps/android/app/src/main/assets/model"
EXPECTED_LABELS = [
    "Battery_Waste", "Glass_Waste", "Keyboard", "Light_Bulb",
    "Medical_Waste", "Metal_Waste", "Mobile", "Mouse", "Organic_Waste",
    "PCB", "Paper_Waste", "Plastic_Waste",
]
EXPECTED_SHA = "32098e6714ea806ecfdf0d87e848aa394ac3d852c81989ecae33f0e142e5438f"


def test_tflite_model_files_exist_and_bounded_size():
    for model_dir in (MODEL_DIR, ANDROID_MODEL_DIR):
        model = model_dir / "classifier.tflite"
        assert model.is_file()
        assert 500_000 < model.stat().st_size < 5_000_000
        assert hashlib.sha256(model.read_bytes()).hexdigest() == EXPECTED_SHA


def test_labels_and_metadata_completeness():
    for model_dir in (MODEL_DIR, ANDROID_MODEL_DIR):
        labels = json.loads((model_dir / "labels.json").read_text(encoding="utf-8"))
        metadata = json.loads((model_dir / "model_metadata.json").read_text(encoding="utf-8"))
        assert labels == EXPECTED_LABELS
        assert metadata["model_version"] == "v2.0-mendeley-openimages"
        assert metadata["classes"] == labels
        assert metadata["input_tensor"]["shape"] == [1, 224, 224, 3]
        assert metadata["output_tensor"]["shape"] == [1, 12]
        assert metadata["input_tensor"]["normalization_range"] == [-1.0, 1.0]
        assert metadata["advisory_threshold"] == 0.52
        assert metadata["mapping_policy"]["reviewed_manual_category_mappings"] == {
            "Keyboard": "MIXED", "Mobile": "MIXED", "Mouse": "MIXED"
        }


def test_tflite_interpreter_inference_and_latency():
    import tensorflow as tf

    interpreter = tf.lite.Interpreter(model_path=str(MODEL_DIR / "classifier.tflite"))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    assert input_details[0]["shape"].tolist() == [1, 224, 224, 3]
    assert output_details[0]["shape"].tolist() == [1, 12]
    assert input_details[0]["dtype"] == np.float32
    assert output_details[0]["dtype"] == np.float32
    dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
    latencies = []
    for _ in range(5):
        start = time.perf_counter()
        interpreter.set_tensor(input_details[0]["index"], dummy)
        interpreter.invoke()
        latencies.append((time.perf_counter() - start) * 1000)
    assert float(np.mean(latencies[1:])) < 100.0
    output = interpreter.get_tensor(output_details[0]["index"])[0]
    assert output.shape == (12,)
    assert np.all(output >= 0.0)
    assert np.isclose(np.sum(output), 1.0, atol=0.05)


def test_export_parity_and_evaluation_report_honesty():
    metadata = json.loads((MODEL_DIR / "model_metadata.json").read_text(encoding="utf-8"))
    parity = metadata["export_parity"]
    assert parity["parity_verified"] is True
    assert parity["top1_match_rate"] == 1.0
    assert parity["max_abs_probability_difference"] < 0.08
    report = json.loads((MODEL_DIR / "evaluation_report.json").read_text(encoding="utf-8"))
    assert report["dataset_split_counts"]["mendeley_train"] == 1508
    assert report["dataset_split_counts"]["openimages_train"] == 600
    assert report["mendeley_held_out_test"]["support"] == 325
    assert report["openimages_fresh_external_test"]["support"] == 90
    assert report["safety_and_provenance"]["manual_confirmation_required"] is True
    assert report["safety_and_provenance"]["kaggle_or_roboflow_assets_used"] is False


def test_model_card_document_and_ethical_guardrails():
    content = (MODEL_DIR / "model_card.md").read_text(encoding="utf-8")
    assert "MobileNetV3-Small" in content
    assert "classifier.tflite" in content
    assert "advisory" in content.lower()
    assert "manual-only" in content
    assert "inferred" in content
    assert "Mendeley" in content

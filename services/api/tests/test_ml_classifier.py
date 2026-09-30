"""Automated tests for On-Device MobileNetV3-Small LiteRT Classifier (T033).
Conforms to docs/19_AI_ML.md, R-ML-02, R-DATA-07, AT-045, AT-059.
"""
import hashlib
import json
import time
from pathlib import Path
import pytest
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT / "data/curated/model"
ANDROID_MODEL_DIR = ROOT / "apps/android/app/src/main/assets/model"
CATALOG_PATH = ROOT / "data/curated/material_catalog/material_catalog.json"


def test_tflite_model_files_exist_and_bounded_size():
    """Validates existence and compact mobile size of classifier.tflite."""
    for m_dir in (MODEL_DIR, ANDROID_MODEL_DIR):
        tflite_file = m_dir / "classifier.tflite"
        assert tflite_file.is_file(), f"Missing classifier.tflite in {m_dir}"

        size_bytes = tflite_file.stat().st_size
        size_mb = size_bytes / (1024 * 1024)

        # Must be compact for entry-level Android devices (< 5.0 MB, target ~1.18 MB)
        assert 500_000 < size_bytes < 5_000_000, f"Unexpected model size: {size_bytes} bytes ({size_mb:.2f} MB)"


def test_labels_and_metadata_completeness():
    """Validates labels map, taxonomy linkage, and metadata integrity."""
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    valid_mat_ids = {m["material_id"] for m in catalog}

    for m_dir in (MODEL_DIR, ANDROID_MODEL_DIR):
        labels_file = m_dir / "labels.json"
        metadata_file = m_dir / "model_metadata.json"

        assert labels_file.is_file(), f"Missing labels.json in {m_dir}"
        assert metadata_file.is_file(), f"Missing model_metadata.json in {m_dir}"

        with open(labels_file, "r", encoding="utf-8") as f:
            labels = json.load(f)
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # 12 targeted defensible visual classes
        assert len(labels) == 12
        for mat_id in labels:
            assert mat_id in valid_mat_ids, f"Label {mat_id} not in authoritative catalog"

        # Metadata specifications
        assert metadata["architecture"] == "MobileNetV3-Small"
        assert metadata["classes"] == labels
        assert metadata["input_tensor"]["shape"] == [1, 224, 224, 3]
        assert metadata["output_tensor"]["shape"] == [1, 12]
        assert metadata["input_tensor"]["normalization_range"] == [-1.0, 1.0]
        assert metadata["advisory_threshold"] == 0.65

        # SHA-256 integrity
        tflite_file = m_dir / "classifier.tflite"
        with open(tflite_file, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        assert metadata["sha256"] == actual_sha, "Model SHA-256 hash mismatch!"


def test_tflite_interpreter_inference_and_latency():
    """Loads LiteRT interpreter, verifies input/output shapes, probability distribution, and execution speed."""
    import tensorflow as tf

    tflite_path = MODEL_DIR / "classifier.tflite"
    interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    assert input_details[0]["shape"].tolist() == [1, 224, 224, 3]
    assert output_details[0]["shape"].tolist() == [1, 12]
    assert input_details[0]["dtype"] == np.float32
    assert output_details[0]["dtype"] == np.float32

    # Run inference on normalized dummy input
    dummy_input = np.random.uniform(-1.0, 1.0, (1, 224, 224, 3)).astype(np.float32)

    latencies = []
    for _ in range(5):
        t0 = time.perf_counter()
        interpreter.set_tensor(input_details[0]["index"], dummy_input)
        interpreter.invoke()
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)

    avg_ms = float(np.mean(latencies[1:]))  # Skip cold-start first iteration
    assert avg_ms < 100.0, f"Inference took too long: {avg_ms:.2f} ms"

    output = interpreter.get_tensor(output_details[0]["index"])[0]
    assert output.shape == (12,)
    assert np.all(output >= 0.0), "Negative probability output!"
    assert np.isclose(np.sum(output), 1.0, atol=0.05), f"Probabilities do not sum to 1: {np.sum(output)}"


def test_quantization_parity_and_numerical_consistency():
    """Validates export parity metrics documented in model_metadata.json."""
    with open(MODEL_DIR / "model_metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    parity = metadata.get("export_parity", {})
    assert parity.get("parity_verified") is True
    max_diff = parity.get("max_abs_probability_difference", 1.0)
    assert max_diff < 0.08, f"Quantization error too high: {max_diff}"


def test_evaluation_report_honesty_and_no_borrowed_benchmarks():
    """Verifies evaluation report contains exact counts, honest metrics, and zero borrowed benchmarks."""
    eval_file = MODEL_DIR / "evaluation_report.json"
    assert eval_file.is_file(), "Missing evaluation_report.json"

    with open(eval_file, "r", encoding="utf-8") as f:
        report = json.load(f)

    # Verification of split counts (172 total: 115 train, 19 val, 38 test)
    assert report["dataset_split_counts"]["train"] == 115
    assert report["dataset_split_counts"]["validation"] == 19
    assert report["dataset_split_counts"]["test"] == 38

    # Confusion matrix integrity
    cm = np.array(report["confusion_matrix"])
    assert cm.shape == (12, 12)
    assert np.sum(cm) == 38, f"Confusion matrix total does not equal test set count (38), got {np.sum(cm)}"

    # Per-class metrics
    breakdown = report["per_class_breakdown"]
    assert len(breakdown) == 12
    total_support = sum(m["support"] for m in breakdown.values())
    assert total_support == 38

    # Honest disclosure
    disclosure = report["honest_reporting_disclosure"]
    assert "NONE" in disclosure["borrowed_benchmarks"]
    assert "NONE" in disclosure["primary_field_data"]
    assert disclosure["excluded_materials_count"] == 9
    assert len(disclosure["excluded_materials"]) == 9


def test_model_card_document_and_ethical_guardrails():
    """Verifies model card documents non-automated advisory rules and safe manual fallback."""
    card_file = MODEL_DIR / "model_card.md"
    assert card_file.is_file(), "Missing model_card.md"

    content = card_file.read_text(encoding="utf-8")

    # Guardrails and disclosures
    assert "MobileNetV3-Small" in content
    assert "classifier.tflite" in content
    assert "ZERO primary field photos claimed" in content
    assert "advisory recommendations only" in content.lower() or "advisory" in content.lower()
    assert "never" in content.lower() and "authorizes" in content.lower()
    assert "c05" in content.lower()
    assert "mat-bat-03" in content.lower()

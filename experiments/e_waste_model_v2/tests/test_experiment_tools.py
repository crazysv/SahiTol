from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREPARE = ROOT / "scripts" / "prepare_asset_ledger.py"
SPLIT = ROOT / "scripts" / "make_grouped_splits.py"


class ExperimentToolTests(unittest.TestCase):
    def test_eligible_asset_is_kept_held_asset_is_rejected_and_groups_do_not_leak(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            accepted_file = temp / "accepted.jpg"
            held_file = temp / "held.jpg"
            accepted_file.write_bytes(b"accepted-image")
            held_file.write_bytes(b"held-image")
            incoming = temp / "incoming.csv"
            with incoming.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=[
                    "file_path", "source_id", "original_url", "license", "attribution",
                    "provider_label", "material_id", "provider_object_group",
                ])
                writer.writeheader()
                writer.writerow({
                    "file_path": accepted_file, "source_id": "MENDELEY_BANGLADESHI_2025",
                    "original_url": "https://example.test/accepted.jpg", "license": "CC BY 4.0",
                    "attribution": "Example", "provider_label": "Mobile", "material_id": "MAT-MIX-01",
                    "provider_object_group": "object-1",
                })
                writer.writerow({
                    "file_path": held_file, "source_id": "KAGGLE_AKSHAT_EWASTE",
                    "original_url": "https://example.test/held.jpg", "license": "Apache-2.0",
                    "attribution": "Example", "provider_label": "PCB", "material_id": "MAT-PCB-01",
                    "provider_object_group": "object-2",
                })

            prepared = temp / "prepared"
            result = subprocess.run(
                [sys.executable, str(PREPARE), "--input", str(incoming), "--output-dir", str(prepared)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            with (prepared / "asset_ledger.csv").open(encoding="utf-8") as stream:
                ledger = list(csv.DictReader(stream))
            rejected = json.loads((prepared / "rejected_assets.json").read_text(encoding="utf-8"))
            self.assertEqual(len(ledger), 1)
            self.assertEqual(ledger[0]["source_id"], "MENDELEY_BANGLADESHI_2025")
            self.assertEqual(len(rejected), 1)
            self.assertIn("not eligible", rejected[0]["reason"])

            split_path = prepared / "splits.csv"
            split = subprocess.run(
                [sys.executable, str(SPLIT), "--ledger", str(prepared / "asset_ledger.csv"), "--output", str(split_path)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(split.returncode, 0, split.stderr + split.stdout)
            summary = json.loads(split_path.with_suffix(".summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["groups_crossing_splits"], 0)


if __name__ == "__main__":
    unittest.main()

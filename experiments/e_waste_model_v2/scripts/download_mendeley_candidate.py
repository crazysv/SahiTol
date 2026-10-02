"""Download and stage the Mendeley candidate archive for the isolated experiment.

The archive is stored under the ignored experiment data directory. This command
does not place anything in SahiTol's curated dataset or Android application.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "MENDELEY_BANGLADESHI_2025"
DOWNLOAD_URL = "https://data.mendeley.com/public-api/zip/77383kmdnw/download/1"


def safe_extract(archive: Path, destination: Path) -> int:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    count = 0
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            target = (destination / member.filename).resolve()
            if root not in target.parents and target != root:
                raise RuntimeError(f"unsafe ZIP member path: {member.filename}")
        bundle.extractall(destination)
        count = len(bundle.infolist())
    return count


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "raw" / SOURCE_ID)
    args = parser.parse_args()
    output = args.output_dir
    archive = output / "source.zip"
    extracted = output / "extracted"
    output.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {SOURCE_ID} from {DOWNLOAD_URL}")
    request = urllib.request.Request(DOWNLOAD_URL, headers={"User-Agent": "SahiTol-experiment/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, archive.open("wb") as stream:
            shutil.copyfileobj(response, stream)
    except Exception as error:  # provider errors must remain visible to the operator
        print(f"Download failed: {error}", file=sys.stderr)
        return 1

    if not zipfile.is_zipfile(archive):
        print("Download did not produce a ZIP archive; keeping it for inspection.", file=sys.stderr)
        return 1
    members = safe_extract(archive, extracted)
    receipt = {
        "source_id": SOURCE_ID,
        "download_url": DOWNLOAD_URL,
        "archive": str(archive),
        "archive_sha256": digest(archive),
        "archive_bytes": archive.stat().st_size,
        "zip_members": members,
        "status": "STAGED_UNAUDITED",
        "next_step": "Generate an asset ledger; do not train or promote this archive yet.",
    }
    (output / "download_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

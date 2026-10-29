import json
from pathlib import Path

import requests


endpoint = "http://localhost:8002/scans"

for metadata_path in sorted(Path("sample-data").glob("*/metadata.json")):
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    scan_path = metadata_path.parent / metadata["file"]
    measurement_id = metadata["measurement_id"]

    print(f"Sending {measurement_id}...")

    with scan_path.open("rb") as scan_file:
        response = requests.post(
            endpoint,
            data={"measurement_id": measurement_id},
            files={
                "file": (
                    scan_path.name,
                    scan_file,
                    "application/octet-stream",
                )
            },
            timeout=(5, 60),
        )

    print(f"HTTP {response.status_code}: {response.text}")
    response.raise_for_status()
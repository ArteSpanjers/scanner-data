import json
from pathlib import Path

import requests


endpoint = "http://localhost:8002/scans"

for metadata_path in sorted(Path("sample-data").glob("*/metadata.json")):
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    scan_path = metadata_path.parent / metadata["file"]
    measurement_id = metadata["measurement_id"]

    print(f"Sending {measurement_id}...")

    try:
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
    except requests.exceptions.Timeout:
        print(f"Timed out for {measurement_id}; outcome unknown. Continuing.")
        continue
    except requests.exceptions.ConnectionError:
        print(f"Connection failed for {measurement_id}; continuing.")
        continue

    print(f"HTTP {response.status_code}: {response.text}")

    if not response.ok:
        print(f"Upload failed for {measurement_id}; continuing.")
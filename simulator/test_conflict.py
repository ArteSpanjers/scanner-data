import io
import json
from pathlib import Path

import numpy as np
import requests


metadata_path = sorted(Path("sample-data").glob("*/metadata.json"))[0]
metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

scan = np.load(metadata_path.parent / metadata["file"], allow_pickle=False)
scan[0, 0, 0] += 1  # Change one value in memory only.

buffer = io.BytesIO()
np.save(buffer, scan)
buffer.seek(0)

response = requests.post(
    "http://localhost:8002/scans",
    data={"measurement_id": metadata["measurement_id"]},
    files={"file": ("scan.npy", buffer, "application/octet-stream")},
    timeout=(5, 60),
)

print(f"HTTP {response.status_code}: {response.text}")
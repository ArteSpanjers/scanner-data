import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import numpy as np


output_dir = Path("sample-data")
output_dir.mkdir(exist_ok=True)

rng = np.random.default_rng(42)

for _ in range(5):
    measurement_id = str(uuid4())
    measurement_dir = output_dir / measurement_id
    measurement_dir.mkdir()

    scan = rng.integers(
        low=0,
        high=100,
        size=(64, 64, 64),
        dtype=np.uint16,
    )

    # A brighter block inside the noisy volume: our pretend chip feature.
    scan[20:44, 20:44, 20:44] += 1000

    np.save(measurement_dir / "scan.npy", scan)

    metadata = {
        "scanner_id": "simulator-01",
        "measurement_id": measurement_id,
        "acquired_at": datetime.now(timezone.utc).isoformat(),
        "file": "scan.npy",
        "shape": list(scan.shape),
        "dtype": str(scan.dtype),
    }

    (measurement_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print(f"Generated {measurement_id}: {scan.shape}, {scan.nbytes:,} bytes")
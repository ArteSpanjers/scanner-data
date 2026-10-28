from fastapi import FastAPI
from pathlib import Path
import shutil
from uuid import uuid4
from fastapi import UploadFile

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/scans", status_code=201)
def upload_scan(file: UploadFile):
    scan_id = str(uuid4())
    print(scan_id)

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    destination = upload_dir / f"{scan_id}.bin"

    with destination.open("wb") as output:
        shutil.copyfileobj(file.file, output)

    return {
        "scan_id": scan_id,
        "filename": file.filename,
        "status": "stored",
    }
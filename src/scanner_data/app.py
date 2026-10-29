from fastapi import FastAPI, UploadFile, HTTPException, Form
from pathlib import Path
import shutil
from uuid import UUID
import os
import boto3
from botocore.config import Config
from botocore.exceptions import EndpointConnectionError
import hashlib
from scanner_data.database import claim_measurement, set_measurement_state, get_measurement, reclaim_failed_measurement
from fastapi.responses import JSONResponse

app = FastAPI()

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT_URL"],
    region_name=os.environ["AWS_DEFAULT_REGION"],
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required",
    ),
)

bucket = os.environ["S3_BUCKET"]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/scans", status_code=201)
def upload_scan(file: UploadFile, measurement_id: UUID = Form(...)):
    scan_id = str(measurement_id)
    object_key = f"{scan_id}.bin"

    hasher = hashlib.sha256()

    while chunk := file.file.read(1024 * 1024):
        hasher.update(chunk)

    checksum = hasher.hexdigest()
    file.file.seek(0)

    claimed = claim_measurement(measurement_id, checksum, object_key)

    if not claimed:
        existing = get_measurement(measurement_id)

        if existing is None:
            raise HTTPException(
                status_code=503,
                detail="Measurement record unavailable. Try again later.",
            )

        if existing["sha256"] != checksum:
            raise HTTPException(
                status_code=409,
                detail="This measurement ID has different file contents.",
            )

        if existing["state"] == "COMPLETE":
            return JSONResponse(
                status_code=200,
                content={
                    "scan_id": scan_id,
                    "object_key": existing["object_key"],
                    "sha256": existing["sha256"],
                    "status": "already_stored",
                },
            )

        if existing["state"] == "FAILED":
            claimed = reclaim_failed_measurement(measurement_id, checksum)

            if not claimed:
                raise HTTPException(
                    status_code=409,
                    detail="Measurement state changed. Try again later.",
                )
        else:
            raise HTTPException(
                status_code=409,
                detail=f"Measurement is currently {existing['state']}.",
            )


    try:
        s3.upload_fileobj(file.file, bucket, object_key)
    except EndpointConnectionError as exc:
        set_measurement_state(measurement_id, "FAILED")

        raise HTTPException(
            status_code=503,
            detail="Scan storage is temporarily unavailable. Upload was not confirmed.",
        ) from exc

    set_measurement_state(measurement_id, "COMPLETE")

    return {
        "scan_id": scan_id,
        "filename": file.filename,
        "object_key": object_key,
        "sha256": checksum,
        "status": "stored",
    }
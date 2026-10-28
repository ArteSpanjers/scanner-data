from fastapi import FastAPI, UploadFile, HTTPException
from pathlib import Path
import shutil
from uuid import uuid4
# from fastapi import UploadFile
import os
import boto3
from botocore.config import Config
from botocore.exceptions import EndpointConnectionError
# from fastapi import HTTPException

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
def upload_scan(file: UploadFile):
    scan_id = str(uuid4())
    object_key = f"{scan_id}.bin"

    try:
        s3.upload_fileobj(file.file, bucket, object_key)
    except EndpointConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail="Scan storage is temporarily unavailable. Upload was not confirmed.",
        ) from exc

    return {
        "scan_id": scan_id,
        "filename": file.filename,
        "object_key": object_key,
        "status": "stored",
    }
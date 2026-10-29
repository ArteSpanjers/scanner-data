# Changelog

Small milestones from the scanner playground. Break things, learn things, write them down.

## 2026-10-29 — Fake scanner and database foundations

- Added a local simulator generating batches of five small 3D NumPy arrays with saved measurement IDs and JSON metadata.
- Added an uploader that sends saved measurements to the API and prints HTTP responses.
- Updated `/scans` to accept and validate a scanner-provided measurement UUID instead of generating a fresh ID per request.
- Added chunked SHA-256 calculation and included the checksum in upload responses. Repeated IDs still overwrite objects; retry/conflict detection isn't implemented yet.
- Added HTTP 503 handling for storage connection failures; tested Garage being unavailable and recovering.
- Deployed PostgreSQL with its own PVC, Service and password Secret, and supplied database settings to the API Pod.
- Added Psycopg and tested a database connection from Python inside the API Pod.
- Added the initial `measurements` table schema with a unique measurement ID, checksum, object key, state and creation timestamp. The upload handler doesn't write database records yet.
- Expanded the README command reference with live logs, simulator commands, SQL through standard input and database inspection.

## 2026-10-28 — Uploads now live in Garage

- Deployed single-node Garage with a dedicated 1 GiB PVC, ConfigMap and ClusterIP Service.
- Added an RPC Secret for Garage and separate S3 credentials for the ingestion API, created outside Git.
- Created bucket `scans` and granted the API key read/write access.
- Supplied API settings and credentials through a ConfigMap and Secret using `envFrom`.
- Switched uploads from local file writes to Boto3's S3 client; verified Garage's object count increased.
- Removed the API's old uploads mount; kept its PVC and earlier practice files.
- Updated the README with the current architecture, Garage commands and completed subtasks.

## 2026-10-28 — First working pipeline

- Added a FastAPI health endpoint and file-upload endpoint with UUID filenames.
- Set up the `scanner_data` Python package and uv dependency management.
- Built a Docker image that starts Uvicorn directly from its virtual environment.
- Deployed to the local `scanner` kind cluster with a namespace, Deployment and ClusterIP Service.
- Added a 1 GiB PVC mounted at `/app/uploads`; verified uploads survive Pod replacement.
- Practised scaling replicas, replacing Pods and accessing the API through port-forward.
- Added Git/Docker ignore rules and project documentation.

Next up: record uploads in PostgreSQL, handle retries and conflicts, then build a pretend HPC consumer.

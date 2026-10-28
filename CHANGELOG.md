# Changelog

Small milestones from the scanner playground. Break things, learn things, write them down.

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

Next up: metadata, checksums, safe retries and dataset states, then a pretend HPC consumer.

# Changelog

Small milestones from the scanner playground. Break things, learn things, write them down.

## 2026-10-28 — First working pipeline

- Added a FastAPI health endpoint and file-upload endpoint with UUID filenames.
- Set up the `scanner_data` Python package and uv dependency management.
- Built a Docker image that starts Uvicorn directly from its virtual environment.
- Deployed to the local `scanner` kind cluster with a namespace, Deployment and ClusterIP Service.
- Added a 1 GiB PVC mounted at `/app/uploads`; verified uploads survive Pod replacement.
- Practised scaling replicas, replacing Pods and accessing the API through port-forward.
- Added Git/Docker ignore rules and project documentation.

Next up: S3-compatible object storage, then reliable ingestion and a pretend HPC consumer.

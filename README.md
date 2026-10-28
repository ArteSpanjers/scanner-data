# Scanner data playground

Learning the plumbing around soft X-ray scanner data, one experiment (and broken Pod) at a time.

## The plan

Fake scanner → ingestion API → durable storage → validated dataset → fake HPC processor.

- [x] Python API with FastAPI, managed with uv
- [x] Container image and local kind cluster
- [x] Deployment, Service and persistent uploads via a PVC
- [x] S3-compatible object storage
- [ ] Metadata, checksums, safe retries and dataset states
- [ ] Fake processing with a Kubernetes Job
- [ ] Later: practise deploying on my server

## What works now

`GET /health` checks the API. `POST /scans` accepts a file and saves its unchanged bytes as `<uuid>.bin`. Every upload gets a new ID, so retries currently create duplicates.

The API runs as the `scanner_data` Python package. Uvicorn serves it on port 8000; the Kubernetes Service exposes port 80 inside the cluster.

Uploads now go through Boto3 to bucket `scans` in Garage at `http://garage:3900`. Garage stores objects and metadata on PVC `garage-data`; the API no longer mounts its own upload storage. The old `scanner-uploads` PVC remains with our earlier practice files.

Garage runs as one instance with replication factor 1. Its data survives Pod replacement, but deleting the kind cluster loses its local storage. Deleting a PVC normally deletes its backing volume too. Persistence isn't a backup!

## Run it

Local Python development (requires the S3 settings and credentials in your shell, plus a Garage endpoint reachable from your laptop):

```powershell
uv run uvicorn scanner_data.app:app --reload
```

For Kubernetes, the setup below assumes the `garage-rpc` and `scanner-s3` Secrets already exist in namespace `scanner`, and Garage's `scans` bucket and API key permissions have been configured. Secret values stay out of Git. On a fresh cluster, those setup steps are also needed; applying YAML alone isn't enough.

Create the cluster once if needed, then build and deploy:

```powershell
kind create cluster --name scanner
kubectl config use-context kind-scanner
docker build -t scanner-api:local .
kind load docker-image scanner-api:local --name scanner
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/
kubectl port-forward -n scanner service/scanner-api 8002:80
```

Open [the upload docs](http://localhost:8002/docs). Keep port-forward running; it tunnels to one Pod, so restart it if that Pod is replaced. A rebuilt image also needs loading into kind and a Deployment restart to update running Pods.

## Handy Kubernetes commands

These assume the `kind-scanner` context, except where explicitly provided. Replace `<pod-name>` with an actual name.

```powershell
# Watch Pods, including their IPs and nodes
kubectl --context kind-scanner get pods -n scanner -w -o wide

# Inspect the app and its storage
kubectl get deployment,rs,svc,pvc -n scanner
kubectl get pv
kubectl logs -n scanner deployment/scanner-api
kubectl describe pod <pod-name> -n scanner

# Explore one API Pod; Garage's image has no shell
kubectl exec -it -n scanner deployment/scanner-api -- sh

# Check Garage and the bucket's object count/size
kubectl exec -n scanner deployment/garage -- /garage status
kubectl exec -n scanner deployment/garage -- /garage bucket info scans

# Delete a Pod and watch its replacement appear
kubectl delete pod <pod-name> -n scanner

# Roll out a newly loaded image
kubectl rollout restart deployment/scanner-api -n scanner
kubectl rollout status deployment/scanner-api -n scanner
```

`exec deployment/...` selects one Pod; it doesn't run in every replica. Ctrl+C stops a watch or port-forward, not the application.

## What we did per task

**Python API + uv**

- Created the project and installed FastAPI, Uvicorn and upload support with uv.
- Built `/health` and `/scans`; tested uploads through `/docs`.
- Organised the code as the `src/scanner_data` package.
- Uploaded the same file twice and observed duplicate scans with new UUIDs.

**Containers + kind**

- Wrote a Dockerfile with explicit copies, cached dependency installation and a direct Uvicorn startup command.
- Added `.dockerignore` and `.gitignore` for generated files and uploads.
- Compared container restart with replacement: local files survive the former, disappear with the latter.
- Created the separate `scanner` cluster and loaded our image into its node.

**Kubernetes + persistent uploads**

- Created the namespace, Deployment and ClusterIP Service; accessed the API with port-forward.
- Scaled replicas, deleted Pods and observed their replacement names/IPs.
- Used the default StorageClass to provision a PV through a 1 GiB PVC.
- Mounted `/app/uploads` and verified files survived Pod replacement.
- Returned to one API replica for the storage experiments.

**S3-compatible object storage**

- Deployed single-node Garage with its own PVC, ConfigMap and Service.
- Created an RPC Secret and injected it with `secretKeyRef`.
- Created bucket `scans`, an API key and bucket read/write permissions.
- Stored S3 credentials in a separate Secret; injected API settings and credentials with `envFrom`.
- Replaced local file writes with Boto3 uploads; rebuilt, loaded and rolled out the API image.
- Verified Garage's object count increased, then removed the API's old PVC mount.

**Still ahead**

- Metadata and reliability: dataset states, checksums, interrupted uploads and safe retries.
- Fake HPC: a Kubernetes Job that reads a scan and writes a result.
- Server deployment: run the platform online for practice, later on.

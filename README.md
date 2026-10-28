# Scanner data playground

Learning the plumbing around soft X-ray scanner data, one experiment (and broken Pod) at a time.

## The plan

Fake scanner → ingestion API → durable storage → validated dataset → fake HPC processor.

- [x] Python API with FastAPI, managed with uv
- [x] Container image and local kind cluster
- [x] Deployment, Service and persistent uploads via a PVC
- [ ] S3-compatible object storage
- [ ] Metadata, checksums, safe retries and dataset states
- [ ] Fake processing with a Kubernetes Job
- [ ] Later: practise deploying on my server

## What works now

`GET /health` checks the API. `POST /scans` accepts a file and saves its unchanged bytes as `<uuid>.bin`. Every upload gets a new ID, so retries currently create duplicates.

The API runs as the `scanner_data` Python package. Uvicorn serves it on port 8000; the Kubernetes Service exposes port 80 inside the cluster.

Uploads go to `/app/uploads`, mounted from PVC `scanner-uploads`. They survive Pod replacement. This is local kind storage, though: deleting the cluster loses it, and deleting the PVC normally deletes its backing volume. Persistence isn't a backup!

## Run it

Local Python development:

```powershell
uv run uvicorn scanner_data.app:app --reload
```

For Kubernetes, create the cluster once if needed, then build and deploy:

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

# Explore one Pod, or check its uploads
kubectl exec -it -n scanner deployment/scanner-api -- sh
kubectl exec -n scanner deployment/scanner-api -- ls -lh /app/uploads

# Delete a Pod and watch its replacement appear
kubectl delete pod <pod-name> -n scanner

# Roll out a newly loaded image
kubectl rollout restart deployment/scanner-api -n scanner
kubectl rollout status deployment/scanner-api -n scanner
```

`exec deployment/...` selects one Pod; it doesn't run in every replica. Ctrl+C stops a watch or port-forward, not the application.

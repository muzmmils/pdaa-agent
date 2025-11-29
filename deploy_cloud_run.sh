#!/usr/bin/env bash
set -euo pipefail

# Usage: ./deploy_cloud_run.sh <gcp-project-id> <region>
# Example: ./deploy_cloud_run.sh my-gcp-project us-central1

PROJECT_ID=${1:-}
REGION=${2:-us-central1}
SERVICE_NAME=pdaa-agent
IMAGE=gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

if [ -z "$PROJECT_ID" ]; then
  echo "ERROR: Project ID required. Usage: ./deploy_cloud_run.sh <project-id> [region]" >&2
  exit 1
fi

echo "== Building & Deploying PDAA Agent to Cloud Run =="

gcloud config set project "$PROJECT_ID"

echo "-> Submitting Cloud Build"
gcloud builds submit --tag "$IMAGE"

echo "-> Deploying to Cloud Run (service: $SERVICE_NAME, region: $REGION)"
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,USE_NLP=false,PATIENTS_FILE=data/patients.json

echo "-> Fetching service URL"
URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)')

echo "\nDeployment complete!"
echo "Service URL: $URL"
echo "Health Check: curl $URL/health"
echo "Run Simulation: curl -X POST $URL/simulate -H 'Content-Type: application/json' -d '{"days":3}'"

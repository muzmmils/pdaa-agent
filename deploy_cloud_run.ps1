param(
  [Parameter(Mandatory=$true)][string]$ProjectId,
  [string]$Region = "us-central1"
)

$ServiceName = "pdaa-agent"
$Image = "gcr.io/$ProjectId/$ServiceName:latest"

Write-Host "== Building & Deploying PDAA Agent to Cloud Run ==" -ForegroundColor Cyan

Write-Host "-> Setting project" -ForegroundColor Yellow
gcloud config set project $ProjectId | Out-Null

Write-Host "-> Submitting Cloud Build" -ForegroundColor Yellow
gcloud builds submit --tag $Image

Write-Host "-> Deploying to Cloud Run (service: $ServiceName, region: $Region)" -ForegroundColor Yellow
gcloud run deploy $ServiceName `
  --image $Image `
  --platform managed `
  --region $Region `
  --allow-unauthenticated `
  --set-env-vars GEMINI_API_KEY=$env:GEMINI_API_KEY,USE_NLP=false,PATIENTS_FILE=data/patients.json

Write-Host "-> Fetching service URL" -ForegroundColor Yellow
$Url = gcloud run services describe $ServiceName --region $Region --format "value(status.url)"

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Service URL: $Url" -ForegroundColor Green
Write-Host "Health Check: curl $Url/health" -ForegroundColor Green
Write-Host "Run Simulation (3 days): curl -X POST $Url/simulate -H 'Content-Type: application/json' -d '{"days":3}'" -ForegroundColor Green

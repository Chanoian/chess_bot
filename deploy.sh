SERVICE_NAME=chess-bot-cloud-run-service
REGION=us-central1

gcloud builds submit --tag gcr.io/chess-bot-cloud-run/chess-bot-image
gcloud run deploy $SERVICE_NAME --image gcr.io/chess-bot-cloud-run/chess-bot-image --platform managed --region $REGION --allow-unauthenticated  --set-cloudsql-instances chess-bot-cloud-run:us-central1:sql-instance
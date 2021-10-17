SERVICE_NAME=chess-bot-cloud-run-service
REGION=us-central1
IMAGE=gcr.io/chess-bot-cloud-run/chess-bot-image

gcloud builds submit --tag $IMAGE
gcloud beta run deploy $SERVICE_NAME \
    --image $IMAGE --platform managed --region $REGION --allow-unauthenticated  \
    --set-cloudsql-instances chess-bot-cloud-run:us-central1:sql-instance \
    --update-secrets CLOUD_SQL_CONN=CLOUD_SQL_CONN:latest \
    --update-secrets DB_USER=DB_USER:latest \
    --update-secrets DB_PASS=DB_PASS:latest \
    --update-secrets DB_NAME=DB_NAME:latest
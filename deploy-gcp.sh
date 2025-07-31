#!/bin/bash

# Google Cloud Run Deployment Script for Cisco Automation Certification Chatbot
# Usage: ./deploy-gcp.sh [PROJECT_ID]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="cisco-automation-chatbot"
REGION="us-central1"
IMAGE_NAME="cisco-automation-chatbot"

# Get project ID from argument or prompt
if [ -z "$1" ]; then
    echo -e "${YELLOW}Enter your Google Cloud Project ID:${NC}"
    read -r PROJECT_ID
else
    PROJECT_ID=$1
fi

echo -e "${GREEN}🚀 Starting deployment to Google Cloud Run...${NC}"
echo -e "${GREEN}Project ID: ${PROJECT_ID}${NC}"
echo -e "${GREEN}Service Name: ${SERVICE_NAME}${NC}"
echo -e "${GREEN}Region: ${REGION}${NC}"

# Set the project
echo -e "${YELLOW}Setting Google Cloud project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}Enabling required Google Cloud APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push the container image
echo -e "${YELLOW}Building container image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME

# Create secrets for API keys (if they don't exist)
echo -e "${YELLOW}Setting up secrets...${NC}"

# Check if secrets exist, create if not
if ! gcloud secrets describe cisco-chatbot-secrets >/dev/null 2>&1; then
    echo -e "${YELLOW}Creating secret for API keys...${NC}"
    echo -e "${YELLOW}Please enter your Google API Key:${NC}"
    read -s GOOGLE_API_KEY
    echo -e "${YELLOW}Please enter your SerpAPI Key (optional, press Enter to skip):${NC}"
    read -s SERPAPI_KEY
    
    # Create secret with both keys
    echo "{\"google-api-key\":\"$GOOGLE_API_KEY\",\"serpapi-key\":\"$SERPAPI_KEY\"}" | gcloud secrets create cisco-chatbot-secrets --data-file=-
else
    echo -e "${GREEN}Secrets already exist, skipping creation...${NC}"
fi

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --concurrency 10 \
    --set-env-vars EMBEDDING_MODEL=paraphrase-MiniLM-L3-v2,PYTHONUNBUFFERED=1,TOKENIZERS_PARALLELISM=false \
    --set-secrets GOOGLE_API_KEY=cisco-chatbot-secrets:latest:google-api-key,SERPAPI_KEY=cisco-chatbot-secrets:latest:serpapi-key

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your Cisco Automation Certification Chatbot is now live at:${NC}"
echo -e "${GREEN}${SERVICE_URL}${NC}"
echo -e "${GREEN}📊 Monitor your service at: https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}${NC}"

# Optional: Open the URL
echo -e "${YELLOW}Would you like to open the chatbot in your browser? (y/n)${NC}"
read -r OPEN_BROWSER
if [[ $OPEN_BROWSER =~ ^[Yy]$ ]]; then
    open $SERVICE_URL
fi

#!/bin/bash
#
# Non-interactive FastAPI Deployment Script for Cisco Automation Certification Station
# This script deploys the FastAPI version of the application to Google Cloud Run without prompting
#

# ANSI color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values - no prompting
PROJECT_ID="affable-relic-467620-c5"
SERVICE_NAME="cisco-automation-certification-station"
REGION="us-central1"
MEMORY="2Gi"
CPU="2"
TIMEOUT="300s"
MIN_INSTANCES="0"
MAX_INSTANCES="10"
DOCKERFILE="Dockerfile.fastapi"

# Print header
echo -e "${BLUE}================================================${NC}"
echo -e "${CYAN}Cisco Automation Certification Station${NC}"
echo -e "${CYAN}FastAPI Deployment to Google Cloud Run (Non-interactive)${NC}"
echo -e "${BLUE}================================================${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    echo -e "${YELLOW}Please install the Google Cloud SDK from:${NC}"
    echo -e "${CYAN}https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# Check if user is logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${YELLOW}You need to log in to Google Cloud first.${NC}"
    gcloud auth login
fi

# Set project
echo -e "${GREEN}Using project: ${CYAN}$PROJECT_ID${NC}"
gcloud config set project "$PROJECT_ID"

# Display deployment settings
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}Deployment Settings:${NC}"
echo -e "${CYAN}Project ID:${NC} $PROJECT_ID"
echo -e "${CYAN}Service Name:${NC} $SERVICE_NAME"
echo -e "${CYAN}Region:${NC} $REGION"
echo -e "${CYAN}Memory:${NC} $MEMORY"
echo -e "${CYAN}CPU:${NC} $CPU"
echo -e "${CYAN}Dockerfile:${NC} $DOCKERFILE"
echo -e "${BLUE}================================================${NC}"

# Check if .env file exists and read API keys
if [ -f .env ]; then
    echo -e "${GREEN}Found .env file. Using environment variables from file.${NC}"
    # Read API keys from .env file (macOS compatible)
    GOOGLE_API_KEY=$(grep 'GOOGLE_API_KEY=' .env | sed 's/GOOGLE_API_KEY=//' || echo "")
    SERPAPI_KEY=$(grep 'SERPAPI_KEY=' .env | sed 's/SERPAPI_KEY=//' || echo "")
else
    echo -e "${YELLOW}No .env file found. Proceeding without API keys.${NC}"
    GOOGLE_API_KEY=""
    SERPAPI_KEY=""
fi

# Start deployment
echo -e "${BLUE}Starting deployment...${NC}"

# Build and push Docker image
echo -e "${CYAN}Building and pushing Docker image...${NC}"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo -e "${YELLOW}Building with Cloud Build (this may take 10-15 minutes)...${NC}"
# Update substitutions in cloudbuild-fastapi.yaml
sed -i '' "s/_SERVICE_NAME: .*/_SERVICE_NAME: $SERVICE_NAME/" cloudbuild-fastapi.yaml
sed -i '' "s/_REGION: .*/_REGION: $REGION/" cloudbuild-fastapi.yaml
sed -i '' "s/_MEMORY: .*/_MEMORY: $MEMORY/" cloudbuild-fastapi.yaml
sed -i '' "s/_CPU: .*/_CPU: '$CPU'/" cloudbuild-fastapi.yaml
sed -i '' "s/_DOCKERFILE: .*/_DOCKERFILE: $DOCKERFILE/" cloudbuild-fastapi.yaml

# Submit build using config file
gcloud builds submit --config=cloudbuild-fastapi.yaml --timeout=30m .

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Docker build failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Docker image built and pushed successfully.${NC}"

# Create secrets for API keys if they don't exist
echo -e "${CYAN}Setting up secrets...${NC}"

# Check if secrets already exist
echo -e "${YELLOW}Checking for existing secrets...${NC}"
gcloud secrets list

echo -e "${YELLOW}Looking for google-api-key secret...${NC}"
GOOGLE_API_SECRET_EXISTS=$(gcloud secrets list --filter="name:google-api-key" --format="value(name)" 2>/dev/null || echo "")
echo -e "${YELLOW}Google API Key secret exists: ${GREEN}$([ -n "$GOOGLE_API_SECRET_EXISTS" ] && echo "YES" || echo "NO")${NC}"

echo -e "${YELLOW}Looking for serpapi-key secret...${NC}"
SERPAPI_SECRET_EXISTS=$(gcloud secrets list --filter="name:serpapi-key" --format="value(name)" 2>/dev/null || echo "")
echo -e "${YELLOW}SerpAPI Key secret exists: ${GREEN}$([ -n "$SERPAPI_SECRET_EXISTS" ] && echo "YES" || echo "NO")${NC}"

# Check if App Engine service account exists
echo -e "${YELLOW}Checking for App Engine service account...${NC}"
APP_ENGINE_SA=$(gcloud iam service-accounts list --filter="email:$PROJECT_ID@appspot.gserviceaccount.com" --format="value(email)" 2>/dev/null || echo "")
echo -e "${YELLOW}App Engine service account exists: ${GREEN}$([ -n "$APP_ENGINE_SA" ] && echo "YES" || echo "NO")${NC}"

# If App Engine service account doesn't exist, use Cloud Run service account instead
if [ -z "$APP_ENGINE_SA" ]; then
    echo -e "${YELLOW}App Engine service account not found. Using Cloud Run service account instead.${NC}"
    # Get the Cloud Run service account
    CLOUD_RUN_SA="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"
    echo -e "${YELLOW}Using Cloud Run service account: ${CYAN}$CLOUD_RUN_SA${NC}"
    SERVICE_ACCOUNT="$CLOUD_RUN_SA"
    
    # Create the service account if it doesn't exist
    echo -e "${YELLOW}Creating service account for Cloud Run...${NC}"
    gcloud iam service-accounts create "$SERVICE_NAME-sa" --display-name="$SERVICE_NAME Service Account" 2>/dev/null || true
    SERVICE_ACCOUNT="$SERVICE_NAME-sa@$PROJECT_ID.iam.gserviceaccount.com"
    echo -e "${GREEN}Using service account: ${CYAN}$SERVICE_ACCOUNT${NC}"
    
    # Grant necessary permissions
    echo -e "${YELLOW}Granting necessary permissions to service account...${NC}"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor" 2>/dev/null || true
else
    SERVICE_ACCOUNT="$PROJECT_ID@appspot.gserviceaccount.com"
    echo -e "${GREEN}Using App Engine service account: ${CYAN}$SERVICE_ACCOUNT${NC}"
fi

# Create Google API Key secret
if [ -z "$GOOGLE_API_SECRET_EXISTS" ] && [ -n "$GOOGLE_API_KEY" ]; then
    echo -e "${YELLOW}Creating Google API Key secret...${NC}"
    echo -n "$GOOGLE_API_KEY" | gcloud secrets create google-api-key --data-file=-
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully created Google API Key secret${NC}"
    else
        echo -e "${RED}Failed to create Google API Key secret${NC}"
    fi
    
    echo -e "${YELLOW}Setting IAM permissions for Google API Key secret...${NC}"
    gcloud secrets add-iam-policy-binding google-api-key \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully set IAM permissions for Google API Key secret${NC}"
    else
        echo -e "${RED}Failed to set IAM permissions for Google API Key secret${NC}"
    fi
else
    echo -e "${GREEN}Skipping Google API Key secret creation (already exists or no key provided)${NC}"
fi

# Create SerpAPI Key secret
if [ -z "$SERPAPI_SECRET_EXISTS" ] && [ -n "$SERPAPI_KEY" ]; then
    echo -e "${YELLOW}Creating SerpAPI Key secret...${NC}"
    echo -n "$SERPAPI_KEY" | gcloud secrets create serpapi-key --data-file=-
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully created SerpAPI Key secret${NC}"
    else
        echo -e "${RED}Failed to create SerpAPI Key secret${NC}"
    fi
    
    echo -e "${YELLOW}Setting IAM permissions for SerpAPI Key secret...${NC}"
    gcloud secrets add-iam-policy-binding serpapi-key \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully set IAM permissions for SerpAPI Key secret${NC}"
    else
        echo -e "${RED}Failed to set IAM permissions for SerpAPI Key secret${NC}"
    fi
else
    echo -e "${GREEN}Skipping SerpAPI Key secret creation (already exists or no key provided)${NC}"
fi

echo -e "${CYAN}Secrets setup complete${NC}"

# Deploy to Cloud Run
echo -e "${CYAN}Deploying to Cloud Run...${NC}"
DEPLOY_COMMAND="gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_NAME \
    --platform=managed \
    --region=$REGION \
    --memory=$MEMORY \
    --cpu=$CPU \
    --timeout=$TIMEOUT \
    --min-instances=$MIN_INSTANCES \
    --max-instances=$MAX_INSTANCES \
    --allow-unauthenticated"

# Add environment variables if API keys are provided
if [ -n "$GOOGLE_API_KEY" ]; then
    DEPLOY_COMMAND="$DEPLOY_COMMAND --set-env-vars=GOOGLE_API_KEY=$GOOGLE_API_KEY"
fi

if [ -n "$SERPAPI_KEY" ]; then
    DEPLOY_COMMAND="$DEPLOY_COMMAND --set-env-vars=SERPAPI_KEY=$SERPAPI_KEY"
fi

# Execute deployment command
echo -e "${YELLOW}Executing: $DEPLOY_COMMAND${NC}"
eval "$DEPLOY_COMMAND"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Deployment failed.${NC}"
    exit 1
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)")

echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "${CYAN}Service URL:${NC} $SERVICE_URL"
echo -e "${BLUE}================================================${NC}"

echo -e "${YELLOW}Opening service URL in browser...${NC}"
if command -v open &> /dev/null; then
    open "$SERVICE_URL"
elif command -v xdg-open &> /dev/null; then
    xdg-open "$SERVICE_URL"
elif command -v start &> /dev/null; then
    start "$SERVICE_URL"
else
    echo -e "${YELLOW}Could not open browser automatically. Please visit:${NC}"
    echo -e "${CYAN}$SERVICE_URL${NC}"
fi

echo -e "${GREEN}Thank you for using the FastAPI Deployment Script!${NC}"
echo -e "${BLUE}================================================${NC}"

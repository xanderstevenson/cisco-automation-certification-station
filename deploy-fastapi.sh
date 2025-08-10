#!/bin/bash
#
# FastAPI Deployment Script for Cisco Automation Certification Station
# This script deploys the FastAPI version of the application to Google Cloud Run
#
# This is a non-interactive version that uses sensible defaults and secure practices

# ANSI color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get current project ID and set default values
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
SERVICE_NAME="cisco-automation-certification-station"
REGION="us-central1"
MEMORY="2Gi"
CPU="2"
MIN_INSTANCES="0"
MAX_INSTANCES="10"
TIMEOUT="300s"

# Suppress sensitive info in output
export CLOUDSDK_CORE_DISABLE_PROMPTS=1
export CLOUDSDK_PYTHON_SITEPACKAGES=1

# Function to print usage information
function print_usage() {
    echo -e "${YELLOW}Usage:${NC} $0 [options]"
    echo -e "\nOptions:"
    echo -e "  -p, --project-id PROJECT_ID    Google Cloud project ID (required if not set in gcloud config)"
    echo -e "  -s, --service-name NAME       Service name (default: $SERVICE_NAME)"
    echo -e "  -r, --region REGION          Google Cloud region (default: $REGION)"
    echo -e "  -m, --memory MEMORY          Memory allocation (default: $MEMORY)"
    echo -e "  -c, --cpu CPU                CPU allocation (default: $CPU)"
    echo -e "  -h, --help                   Show this help message"
    echo -e "\nExample:"
    echo -e "  $0 --project-id my-project --service-name my-service --region us-central1"
    echo -e "  $0 -p my-project -s my-service -r us-central1 -m 2Gi -c 2"
    exit 1
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--project-id)
            PROJECT_ID=$2
            shift 2
            ;;
        -s|--service-name)
            SERVICE_NAME=$2
            shift 2
            ;;
        -r|--region)
            REGION=$2
            shift 2
            ;;
        -m|--memory)
            MEMORY=$2
            shift 2
            ;;
        -c|--cpu)
            CPU=$2
            shift 2
            ;;
        -h|--help)
            print_usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            print_usage
            ;;
    esac
done

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: Google Cloud SDK (gcloud) is not installed. Please install it first.${NC}"
    echo -e "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if project ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No project ID specified. Please set PROJECT_ID environment variable or use --project-id flag.${NC}"
    print_usage
    exit 1
fi

# Set the project
echo -e "\n${GREEN}Using project: ${YELLOW}$PROJECT_ID${NC}"
if ! gcloud config set project "$PROJECT_ID" >/dev/null 2>&1; then
    echo -e "${RED}Error: Failed to set project. Please check your project ID and permissions.${NC}"
    exit 1
fi

# Check if user is logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${RED}Error: Not authenticated. Please run 'gcloud auth login' first.${NC}"
    exit 1
fi

# Print deployment information
echo -e "\n${BLUE}================================================${NC}"
echo -e "${CYAN}Cisco Automation Certification Station${NC}"
echo -e "${CYAN}FastAPI Deployment to Google Cloud Run${NC}"
echo -e "${BLUE}================================================${NC}\n"

# Enable required services
echo -e "${CYAN}Enabling required Google Cloud services...${NC}"
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    --quiet

# Build and push the Docker image
echo -e "\n${CYAN}Building and pushing Docker image...${NC}"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo -e "${YELLOW}Building with Cloud Build using FastAPI Dockerfile...${NC}"
gcloud builds submit --config=cloudbuild-fastapi.yaml --timeout=1800s --quiet

# Deploy to Cloud Run
echo -e "\n${GREEN}Deploying to Cloud Run...${NC}"
echo -e "Service: ${YELLOW}$SERVICE_NAME${NC}"
echo -e "Region:  ${YELLOW}$REGION${NC}"
echo -e "Memory:  ${YELLOW}$MEMORY${NC}"
echo -e "CPU:     ${YELLOW}$CPU${NC}"

gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --memory "$MEMORY" \
    --cpu "$CPU" \
    --timeout "$TIMEOUT" \
    --min-instances "$MIN_INSTANCES" \
    --max-instances "$MAX_INSTANCES" \
    --allow-unauthenticated \
    --quiet

# Get the service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')
echo -e "\n${BLUE}================================================${NC}"
echo -e "${GREEN}Deployment Successful!${NC}"
echo -e "Service URL: ${CYAN}$SERVICE_URL${NC}"
echo -e "${BLUE}================================================${NC}\n"

echo -e "${GREEN}Deployment completed successfully!${NC}\n"

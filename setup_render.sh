#!/bin/bash

# Exit on error
set -e

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo "Installing curl..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install curl
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y curl
    else
        echo "Please install curl manually"
        exit 1
    fi
fi

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo "Installing Render CLI..."
    curl -o render https://render.com/download/render-linux-amd64
    chmod +x render
    sudo mv render /usr/local/bin/
fi

# Check if user is logged in to Render
if ! render auth whoami &> /dev/null; then
    echo "Please log in to Render:"
    render auth login
fi

# Function to create a new service on Render
create_render_service() {
    local api_key=$1
    local service_name=$2
    local repo_url=$3
    
    curl -X POST https://api.render.com/v1/services \
    -H "Authorization: Bearer $api_key" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"$service_name\",
        \"type\": \"web\",
        \"repo\": \"$repo_url\",
        \"branch\": \"main\",
        \"buildCommand\": \"pip install -r requirements.txt\",
        \"startCommand\": \"gunicorn app:app\",
        \"envVars\": [
            {
                \"key\": \"PYTHON_VERSION\",
                \"value\": \"3.9.0\"
            },
            {
                \"key\": \"FLASK_APP\",
                \"value\": \"app.py\"
            },
            {
                \"key\": \"FLASK_ENV\",
                \"value\": \"production\"
            }
        ]
    }"
}

# Get Render API key
read -p "Enter your Render API key: " RENDER_API_KEY

# Get GitHub repository URL
read -p "Enter your GitHub repository URL: " GITHUB_REPO_URL

# Create service on Render
echo "Creating service on Render..."
SERVICE_RESPONSE=$(create_render_service "$RENDER_API_KEY" "travel-calculator" "$GITHUB_REPO_URL")

# Extract service ID
SERVICE_ID=$(echo $SERVICE_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$SERVICE_ID" ]; then
    echo "Failed to create service on Render"
    exit 1
fi

echo "Service created successfully with ID: $SERVICE_ID"

# Save service ID to .env file
echo "RENDER_SERVICE_ID=$SERVICE_ID" >> .env
echo "RENDER_API_KEY=$RENDER_API_KEY" >> .env

# Create a new web service
echo "Creating new web service on Render..."
render service create \
    --name travel-app \
    --type web \
    --env python \
    --build-command "pip install -r requirements.txt" \
    --start-command "gunicorn app:app" \
    --env-vars \
        SECRET_KEY="$(openssl rand -hex 32)" \
        SMTP_USERNAME="$SMTP_USERNAME" \
        SMTP_PASSWORD="$SMTP_PASSWORD" \
        TWILIO_ACCOUNT_SID="$TWILIO_ACCOUNT_SID" \
        TWILIO_AUTH_TOKEN="$TWILIO_AUTH_TOKEN" \
        TWILIO_PHONE_NUMBER="$TWILIO_PHONE_NUMBER" \
        FIREBASE_CREDENTIALS="$FIREBASE_CREDENTIALS"

# Get the service ID
SERVICE_ID=$(render service ls --name travel-app --json | jq -r '.[0].id')

# Set up automatic deployments
echo "Setting up automatic deployments..."
render service update "$SERVICE_ID" \
    --auto-deploy true \
    --branch main

# Set up health check
echo "Setting up health check..."
render service update "$SERVICE_ID" \
    --health-check-path /health \
    --health-check-timeout 10

# Set up scaling
echo "Setting up scaling..."
render service update "$SERVICE_ID" \
    --min-instances 1 \
    --max-instances 3 \
    --target-cpu 70

# Set up custom domain (if provided)
if [ -n "$CUSTOM_DOMAIN" ]; then
    echo "Setting up custom domain..."
    render service update "$SERVICE_ID" \
        --custom-domain "$CUSTOM_DOMAIN"
fi

echo "Setup completed successfully!"
echo "Your application is now deployed on Render."

echo "Render setup completed successfully!"
echo "Please add the following environment variables in the Render dashboard:"
echo "- SECRET_KEY"
echo "- SMTP_USERNAME"
echo "- SMTP_PASSWORD"
echo "- TWILIO_ACCOUNT_SID"
echo "- TWILIO_AUTH_TOKEN"
echo "- TWILIO_PHONE_NUMBER" 
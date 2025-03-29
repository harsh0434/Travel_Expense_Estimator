#!/bin/bash

# Exit on error
set -e

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "Installing doctl..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install doctl
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        snap install doctl --classic
    else
        echo "Please install doctl manually from https://docs.digitalocean.com/reference/doctl/how-to/install/"
        exit 1
    fi
fi

# Check if user is authenticated
if ! doctl account get &> /dev/null; then
    echo "Please authenticate with DigitalOcean:"
    doctl auth init
fi

# Create app if it doesn't exist
if ! doctl apps list | grep -q "travel-calculator"; then
    echo "Creating new app..."
    doctl apps create --spec .do/app.yaml
else
    echo "Updating existing app..."
    APP_ID=$(doctl apps list --format ID,Name | grep "travel-calculator" | awk '{print $1}')
    doctl apps update $APP_ID --spec .do/app.yaml
fi

echo "Deployment completed successfully!" 
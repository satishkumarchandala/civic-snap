#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements-prod.txt

# Create necessary directories
mkdir -p uploads logs models

echo "Build completed successfully!"

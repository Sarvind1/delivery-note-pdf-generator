#!/bin/bash

# Lambda Layer Build Script for PDF Generator Dependencies
# This script creates a Lambda layer with all required Python dependencies

set -e

echo "Building Lambda Layer for PDF Generator..."

# Create layer directory structure
LAYER_DIR="lambda-layer"
PYTHON_DIR="$LAYER_DIR/python"

# Clean up previous builds
rm -rf $LAYER_DIR
rm -f lambda-layer.zip

# Create directory structure
mkdir -p $PYTHON_DIR

echo "Installing dependencies..."

# Install dependencies to the python directory
# Using --platform and --only-binary to ensure Linux-compatible wheels
pip3 install \
    --platform manylinux2014_x86_64 \
    --target=$PYTHON_DIR \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: \
    --upgrade \
    -r requirements.txt

# Remove unnecessary files to reduce layer size
echo "Cleaning up unnecessary files..."
cd $PYTHON_DIR
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

cd ../..

# Create zip file
echo "Creating layer zip file..."
cd $LAYER_DIR
zip -r9 ../lambda-layer.zip .
cd ..

# Get layer size
LAYER_SIZE=$(du -h lambda-layer.zip | cut -f1)
echo ""
echo "✅ Layer built successfully!"
echo "📦 Layer file: lambda-layer.zip"
echo "📊 Layer size: $LAYER_SIZE"
echo ""
echo "Next steps:"
echo "1. Upload lambda-layer.zip to AWS Lambda as a layer:"
echo "   aws lambda publish-layer-version \\"
echo "     --layer-name pdf-generator-dependencies \\"
echo "     --description 'Dependencies for PDF generator' \\"
echo "     --zip-file fileb://lambda-layer.zip \\"
echo "     --compatible-runtimes python3.11"
echo ""
echo "2. Or upload via AWS Console:"
echo "   - Go to Lambda > Layers > Create layer"
echo "   - Upload lambda-layer.zip"
echo "   - Select compatible runtimes: Python 3.11"
echo ""
echo "3. Attach the layer to your Lambda function"
echo ""
echo "⚠️  Note: Maximum layer size is 50MB (unzipped: 250MB)"

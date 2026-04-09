#!/bin/bash
# Build Lambda Layer for WeasyPrint PDF Generator
# NOTE: WeasyPrint requires system libraries. This script attempts a basic build.
# For production, consider building on Amazon Linux 2 or using Docker.

echo "Building Lambda Layer for WeasyPrint..."

# Create directory structure
mkdir -p python/lib/python3.11/site-packages

# Install dependencies
python3 -m pip install -r requirements.txt -t python/lib/python3.11/site-packages --platform manylinux2014_x86_64 --only-binary=:all:

# Check if WeasyPrint installed successfully
if [ ! -d "python/lib/python3.11/site-packages/weasyprint" ]; then
    echo "ERROR: WeasyPrint installation failed"
    echo "WeasyPrint requires system libraries (cairo, pango, gdk-pixbuf)"
    echo ""
    echo "Options:"
    echo "1. Build on Amazon Linux 2 EC2 instance"
    echo "2. Use Docker with amazonlinux:2 image"
    echo "3. Try installing system libraries locally and rebuild"
    exit 1
fi

# Create zip file
echo "Creating lambda-layer.zip..."
zip -r lambda-layer.zip python/

# Get file size
SIZE=$(ls -lh lambda-layer.zip | awk '{print $5}')
echo "Layer size: $SIZE"

# Check size limits
BYTES=$(stat -f%z lambda-layer.zip 2>/dev/null || stat -c%s lambda-layer.zip 2>/dev/null)
if [ $BYTES -gt 52428800 ]; then
    echo "WARNING: Layer size exceeds 50MB compressed limit ($SIZE)"
    echo "Consider removing unused dependencies"
fi

echo ""
echo "Lambda layer created successfully: lambda-layer.zip"
echo "Next steps:"
echo "1. Upload to AWS Lambda as a layer"
echo "2. Attach layer to your Lambda function"
echo "3. Upload lambda_function.py and pdf_generator_weasyprint_lambda.py"
echo ""
echo "Note: If WeasyPrint fails in Lambda, you may need to:"
echo "- Build on Amazon Linux 2"
echo "- Include system library binaries in the layer"
echo "- Use a pre-built WeasyPrint layer from the community"

# Cleanup
rm -rf python/

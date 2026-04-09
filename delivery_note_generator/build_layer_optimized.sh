#!/bin/bash
# Optimized Lambda Layer build - reduces size to under 50MB

echo "Building optimized Lambda Layer for WeasyPrint..."

# Clean up any existing build
rm -rf python lambda-layer.zip

# Create directory structure
mkdir -p python/lib/python3.11/site-packages

# Install dependencies with size optimizations
python3 -m pip install \
  -r requirements.txt \
  -t python/lib/python3.11/site-packages \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --no-cache-dir

# Remove unnecessary files to reduce size
cd python/lib/python3.11/site-packages

# Remove test files and documentation
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null
find . -type d -name "test" -exec rm -rf {} + 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.dist-info" -exec rm -rf {} + 2>/dev/null
find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null

# Remove unnecessary pyphen dictionaries (keep only English)
if [ -d "pyphen/dictionaries" ]; then
    cd pyphen/dictionaries
    ls | grep -v "hyph_en" | grep -v "README" | xargs rm -f 2>/dev/null
    cd ../..
fi

# Remove numpy tests and docs
rm -rf numpy/tests 2>/dev/null
rm -rf numpy/doc 2>/dev/null
rm -rf pandas/tests 2>/dev/null

cd ../../../../

# Create zip file
echo "Creating lambda-layer.zip..."
zip -r -q lambda-layer.zip python/

# Get file size
SIZE=$(ls -lh lambda-layer.zip | awk '{print $5}')
BYTES=$(stat -f%z lambda-layer.zip 2>/dev/null || stat -c%s lambda-layer.zip 2>/dev/null)
SIZE_MB=$((BYTES / 1048576))

echo "Layer size: $SIZE (${SIZE_MB}MB)"

if [ $BYTES -gt 52428800 ]; then
    echo "⚠️  WARNING: Layer size ${SIZE_MB}MB still exceeds 50MB limit"
    echo "You'll need to upload via AWS CLI or S3"
else
    echo "✅ Layer size is under 50MB limit"
fi

echo ""
echo "Lambda layer created: lambda-layer.zip"

# Cleanup
rm -rf python/

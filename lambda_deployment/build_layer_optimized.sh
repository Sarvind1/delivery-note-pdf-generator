#!/bin/bash
# Optimized Lambda Layer builder for WeasyPrint
# Target: <50MB layer size
# Includes system libraries for Amazon Linux 2

set -e

echo "=== Building Optimized Lambda Layer for WeasyPrint ==="
echo ""

# Clean previous builds
echo "1. Cleaning previous builds..."
rm -rf python lib lambda-layer-optimized.zip
mkdir -p python/lib/python3.11/site-packages
mkdir -p lib

# Install Python packages with optimizations
echo ""
echo "2. Installing Python packages (optimized)..."
pip install \
  --target python/lib/python3.11/site-packages \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.11 \
  --only-binary=:all: \
  --upgrade \
  -r requirements_weasyprint.txt

# Remove unnecessary files to reduce size
echo ""
echo "3. Removing unnecessary files to reduce size..."

cd python/lib/python3.11/site-packages

# Remove test files
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "test" -exec rm -rf {} + 2>/dev/null || true

# Remove documentation
find . -type d -name "docs" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.md" -delete 2>/dev/null || true
find . -type f -name "*.rst" -delete 2>/dev/null || true

# Remove examples
find . -type d -name "examples" -exec rm -rf {} + 2>/dev/null || true

# Remove cached files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Remove .dist-info (keep minimal metadata)
find . -type d -name "*.dist-info" -exec rm -rf {}/RECORD {} + 2>/dev/null || true

# Remove typing stubs
find . -type f -name "*.pyi" -delete 2>/dev/null || true

cd ../../../../

echo ""
echo "4. Size after Python package optimization:"
du -sh python/

# Note about system libraries
echo ""
echo "=== IMPORTANT: System Libraries Required ==="
echo ""
echo "WeasyPrint needs these system libraries (.so files):"
echo "  - libcairo, libpango, libfontconfig, libfreetype"
echo "  - Plus their dependencies (see SYSTEM_LIBRARIES_PLAN.md)"
echo ""
echo "You have TWO options:"
echo ""
echo "Option A - Docker (Recommended):"
echo "  Run the included build_with_docker.sh script"
echo ""
echo "Option B - Manual (if you have the .so files):"
echo "  1. Place all .so files in the 'lib/' folder"
echo "  2. Re-run this script"
echo ""

# Check if lib folder has any .so files
if [ -n "$(find lib -name '*.so*' 2>/dev/null)" ]; then
    echo "✓ Found system libraries in lib/"
    echo ""
    echo "5. System libraries size:"
    du -sh lib/
else
    echo "⚠ WARNING: No system libraries found in lib/"
    echo "   The layer will be created but Lambda will fail without them!"
    echo ""
fi

# Create the layer zip
echo ""
echo "6. Creating lambda-layer-optimized.zip..."
zip -r -q lambda-layer-optimized.zip python/ lib/

LAYER_SIZE=$(du -h lambda-layer-optimized.zip | cut -f1)
echo ""
echo "=== Layer Build Complete ==="
echo "File: lambda-layer-optimized.zip"
echo "Size: $LAYER_SIZE"
echo ""

# Check size
LAYER_SIZE_MB=$(du -m lambda-layer-optimized.zip | cut -f1)
if [ "$LAYER_SIZE_MB" -lt 50 ]; then
    echo "✓ Layer size is under 50MB - can upload via console"
else
    echo "⚠ Layer size is ${LAYER_SIZE_MB}MB (over 50MB)"
    echo "  You must upload via AWS CLI:"
    echo "  aws lambda publish-layer-version \\"
    echo "    --layer-name weasyprint-pdf-layer \\"
    echo "    --zip-file fileb://lambda-layer-optimized.zip \\"
    echo "    --compatible-runtimes python3.11"
fi

echo ""
echo "Next steps:"
echo "  1. Upload layer to AWS Lambda (see above)"
echo "  2. Create Lambda function with:"
echo "     - Runtime: Python 3.11"
echo "     - Handler: lambda_handler.lambda_handler"
echo "     - Env var: LD_LIBRARY_PATH=/opt/lib"
echo "  3. Attach the layer to your function"
echo "  4. Upload lambda_handler.py + pdf_generator_weasyprint.py as function code"

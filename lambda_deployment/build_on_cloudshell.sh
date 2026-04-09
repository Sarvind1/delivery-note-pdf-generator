#!/bin/bash
# Build Lambda Layer using AWS CloudShell
# Run this directly in AWS CloudShell (no Docker needed!)

set -e

echo "=== Building Lambda Layer in AWS CloudShell ==="
echo ""

# Clean previous builds
echo "1. Cleaning previous builds..."
rm -rf python lib lambda-layer-optimized.zip

# Install system packages
echo ""
echo "2. Installing system packages..."
sudo yum install -y cairo pango fontconfig freetype \
  libpng harfbuzz fribidi glib2 pixman

# Create directory structure
echo ""
echo "3. Creating directory structure..."
mkdir -p python/lib/python3.11/site-packages
mkdir -p lib

# Install Python packages
echo ""
echo "4. Installing Python packages..."
pip3 install \
  -r requirements_weasyprint.txt \
  -t python/lib/python3.11/site-packages \
  --no-cache-dir

# Optimize Python packages
echo ""
echo "5. Optimizing Python packages..."
cd python/lib/python3.11/site-packages

find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "test" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "docs" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "examples" -exec rm -rf {} + 2>/dev/null || true
find . -type f \( -name "*.md" -o -name "*.rst" \) -delete 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
find . -type f -name "*.pyi" -delete 2>/dev/null || true

cd /home/cloudshell-user

# Copy system libraries
echo ""
echo "6. Copying system libraries..."
cp -P /usr/lib64/libpango-1.0.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libpangocairo-1.0.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libpangoft2-1.0.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libcairo.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libfontconfig.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libfreetype.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libpng*.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libharfbuzz.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libfribidi.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libthai.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libglib-2.0.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libgobject-2.0.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libpixman-1.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libexpat.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libuuid.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libgraphite2.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libdatrie.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libffi.so.* lib/ 2>/dev/null || true
cp -P /usr/lib64/libpcre.so.* lib/ 2>/dev/null || true

# Show sizes
echo ""
echo "Size summary:"
du -sh python/
du -sh lib/

# Create zip
echo ""
echo "7. Creating zip file..."
zip -r -q lambda-layer-optimized.zip python/ lib/

echo ""
echo "=== ✓ Build Complete ==="
du -h lambda-layer-optimized.zip

echo ""
echo "Download the file:"
echo "1. Click 'Actions' → 'Download file'"
echo "2. Enter path: lambda-layer-optimized.zip"
echo "3. Save to your computer"

#!/bin/bash
# Build Lambda Layer using Docker (Amazon Linux 2 environment)
# This ensures compatibility with AWS Lambda runtime

set -e

echo "=== Building Lambda Layer with Docker (Amazon Linux 2) ==="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Clean previous builds
echo "1. Cleaning previous builds..."
rm -rf lambda-layer-optimized.zip python lib

echo ""
echo "2. Building layer in Amazon Linux 2 container..."
echo "   This may take a few minutes..."
echo ""

# Run Docker container to build the layer (force x86_64/amd64 architecture)
# Using public.ecr.aws/lambda/python:3.9 which has Python 3.9 pre-installed
docker run --platform linux/amd64 --rm --entrypoint /bin/bash -v "$PWD":/var/task public.ecr.aws/lambda/python:3.9 -c '
set -e

echo "Installing system packages..."
yum install -y zip \
  cairo cairo-gobject pango fontconfig freetype \
  libpng harfbuzz fribidi glib2 pixman \
  mesa-libEGL mesa-libGL libX11 libXrender libXext

echo ""
echo "Creating directory structure..."
mkdir -p /var/task/python/lib/python3.9/site-packages
mkdir -p /var/task/lib

echo ""
echo "Installing Python packages..."
pip install \
  -r /var/task/requirements_weasyprint.txt \
  -t /var/task/python/lib/python3.9/site-packages \
  --no-cache-dir

echo ""
echo "Optimizing Python packages (removing unnecessary files)..."
cd /var/task/python/lib/python3.9/site-packages

# Remove tests, docs, examples
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "test" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "docs" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "examples" -exec rm -rf {} + 2>/dev/null || true
find . -type f \( -name "*.md" -o -name "*.rst" -o -name "*.txt" \) -delete 2>/dev/null || true

# Remove cache and compiled files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true

# Remove typing stubs
find . -type f -name "*.pyi" -delete 2>/dev/null || true

cd /var/task

echo ""
echo "Copying system libraries..."
# Core libraries
cp -P /usr/lib64/libpango-1.0.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libpangocairo-1.0.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libpangoft2-1.0.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libcairo.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libfontconfig.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libfreetype.so.* /var/task/lib/ 2>/dev/null || true

# Dependencies
cp -P /usr/lib64/libpng*.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libharfbuzz.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libfribidi.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libthai.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libglib-2.0.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libgobject-2.0.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libpixman-1.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libexpat.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libuuid.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libgraphite2.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libdatrie.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libffi.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libpcre.so.* /var/task/lib/ 2>/dev/null || true

# EGL/GL dependencies (for Cairo)
cp -P /usr/lib64/libEGL.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libGL.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libGLdispatch.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libglvnd.so.* /var/task/lib/ 2>/dev/null || true

# X11 dependencies
cp -P /usr/lib64/libX11.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libXrender.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libXext.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libxcb.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libXau.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libxcb-render.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libxcb-shm.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libXfixes.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libXdamage.so.* /var/task/lib/ 2>/dev/null || true

# Additional dependencies
cp -P /usr/lib64/libgbm.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libdrm.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libglapi.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libwayland-client.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libwayland-server.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libxshmfence.so.* /var/task/lib/ 2>/dev/null || true
cp -P /usr/lib64/libXxf86vm.so.* /var/task/lib/ 2>/dev/null || true

echo ""
echo "Size summary:"
echo "Python packages:"
du -sh /var/task/python/
echo "System libraries:"
du -sh /var/task/lib/

echo ""
echo "Creating zip file..."
cd /var/task
zip -r -q lambda-layer-optimized.zip python/ lib/

echo ""
echo "Final layer size:"
du -h /var/task/lambda-layer-optimized.zip
'

# Check result
if [ -f "lambda-layer-optimized.zip" ]; then
    LAYER_SIZE_MB=$(du -m lambda-layer-optimized.zip | cut -f1)
    echo ""
    echo "=== ✓ Build Complete ==="
    echo "File: lambda-layer-optimized.zip"
    echo "Size: $(du -h lambda-layer-optimized.zip | cut -f1) (${LAYER_SIZE_MB}MB)"
    echo ""

    if [ "$LAYER_SIZE_MB" -lt 50 ]; then
        echo "✓ Layer is under 50MB - can upload via AWS Console"
    else
        echo "⚠ Layer is ${LAYER_SIZE_MB}MB (over 50MB limit)"
        echo ""
        echo "Upload via AWS CLI:"
        echo "aws lambda publish-layer-version \\"
        echo "  --layer-name weasyprint-pdf-layer \\"
        echo "  --zip-file fileb://lambda-layer-optimized.zip \\"
        echo "  --compatible-runtimes python3.11"
    fi

    echo ""
    echo "Next: See DEPLOYMENT_GUIDE.md for manual upload instructions"
else
    echo ""
    echo "❌ Build failed - lambda-layer-optimized.zip not created"
    exit 1
fi

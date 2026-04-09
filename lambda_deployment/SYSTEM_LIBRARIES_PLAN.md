# Adding System Libraries to WeasyPrint Lambda Layer

## Problem
The current Lambda Layer (40MB) contains Python packages but **lacks system libraries** that WeasyPrint requires:
- Cairo (graphics library)
- Pango (text layout)
- FontConfig (font management)
- FreeType (font rendering)

Without these, Lambda will fail with errors like "cairo not found" or "pango not found".

---

## Solution: Include Pre-built System Libraries

Based on:
- GitHub issue: https://github.com/Kozea/WeasyPrint/issues/499
- Working example: https://github.com/Prasengupta/weasyprint_for_awslambda

We need to **bundle compiled Linux system libraries** into the Lambda Layer.

---

## Required System Libraries

### Core Libraries:
```
libpango-1.0.so.0
libpangocairo-1.0.so.0
libpangoft2-1.0.so.0
libcairo.so.2
libfontconfig.so.1
libfreetype.so.6
```

### Dependencies (these libraries depend on):
```
libpng16.so.16
libharfbuzz.so.0
libfribidi.so.0
libthai.so.0
libglib-2.0.so.0
libgobject-2.0.so.0
libpixman-1.so.0
libexpat.so.1
libuuid.so.1
```

---

## Implementation Plan

### Step 1: Download Amazon Linux 2 Libraries

**Option A - From EC2 Instance:**
1. Launch Amazon Linux 2 EC2 instance (free tier)
2. SSH into instance
3. Install packages:
```bash
sudo yum install -y cairo pango fontconfig freetype
```
4. Copy libraries from `/usr/lib64/`:
```bash
mkdir libs
cp /usr/lib64/libpango*.so.* libs/
cp /usr/lib64/libcairo*.so.* libs/
cp /usr/lib64/libfontconfig*.so.* libs/
cp /usr/lib64/libfreetype*.so.* libs/
cp /usr/lib64/libpng*.so.* libs/
cp /usr/lib64/libharfbuzz*.so.* libs/
cp /usr/lib64/libfribidi*.so.* libs/
cp /usr/lib64/libthai*.so.* libs/
cp /usr/lib64/libglib*.so.* libs/
cp /usr/lib64/libgobject*.so.* libs/
cp /usr/lib64/libpixman*.so.* libs/
cp /usr/lib64/libexpat*.so.* libs/
cp /usr/lib64/libuuid*.so.* libs/
```
5. Download `libs/` folder to your local machine
6. Terminate EC2 instance

**Option B - Download RPM Packages Directly:**
```bash
# Download RPM packages for Amazon Linux 2
wget https://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/p/pango-1.42.4-4.el7_7.x86_64.rpm
wget https://dl.rockylinux.org/pub/rocky/8/BaseOS/x86_64/os/Packages/c/cairo-1.15.12-6.el8.x86_64.rpm
# ... etc for all required packages

# Extract libraries from RPM
rpm2cpio pango-*.rpm | cpio -idmv
rpm2cpio cairo-*.rpm | cpio -idmv
# Copy .so files from extracted directories
```

### Step 2: Modify Lambda Layer Structure

New layer structure:
```
python/
  lib/
    python3.11/
      site-packages/
        pandas/
        weasyprint/
        ... (all Python packages)
lib/
  libpango-1.0.so.0
  libpangocairo-1.0.so.0
  libpangoft2-1.0.so.0
  libcairo.so.2
  libfontconfig.so.1
  libfreetype.so.6
  ... (all other .so files)
```

### Step 3: Build Enhanced Layer

Modified `build_layer_with_libs.sh`:
```bash
#!/bin/bash
echo "Building Lambda Layer with system libraries..."

# Build Python packages (as before)
mkdir -p python/lib/python3.11/site-packages
pip install -r requirements.txt -t python/lib/python3.11/site-packages --platform manylinux2014_x86_64 --only-binary=:all:

# Add system libraries
mkdir -p lib
cp /path/to/downloaded/libs/*.so.* lib/

# Create zip
zip -r lambda-layer.zip python/ lib/
```

### Step 4: Environment Variables in Lambda

Set in Lambda function configuration:
```
LD_LIBRARY_PATH=/opt/lib:/var/task/lib
```

This tells Lambda where to find the system libraries.

---

## Alternative: Use Docker to Build Layer

**Easiest method** - Build on exact Lambda environment:

```bash
docker run -v "$PWD":/var/task amazonlinux:2 /bin/bash -c "
  yum install -y python3.11 python3.11-pip zip cairo pango fontconfig && \
  pip3.11 install -r requirements.txt -t python/lib/python3.11/site-packages && \
  mkdir -p lib && \
  cp /usr/lib64/libpango*.so.* lib/ && \
  cp /usr/lib64/libcairo*.so.* lib/ && \
  cp /usr/lib64/libfontconfig*.so.* lib/ && \
  cp /usr/lib64/libfreetype*.so.* lib/ && \
  cp /usr/lib64/libpng*.so.* lib/ && \
  cp /usr/lib64/libharfbuzz*.so.* lib/ && \
  cp /usr/lib64/libfribidi*.so.* lib/ && \
  cp /usr/lib64/libthai*.so.* lib/ && \
  cp /usr/lib64/libglib*.so.* lib/ && \
  cp /usr/lib64/libgobject*.so.* lib/ && \
  cp /usr/lib64/libpixman*.so.* lib/ && \
  cp /usr/lib64/libexpat*.so.* lib/ && \
  cp /usr/lib64/libuuid*.so.* lib/ && \
  zip -r lambda-layer.zip python/ lib/
"
```

---

## Expected Layer Size

- Python packages (optimized): ~40MB
- System libraries: ~10-15MB
- **Total: ~50-55MB**

May slightly exceed 50MB console limit → Upload via AWS CLI:
```bash
aws lambda publish-layer-version \
  --layer-name pdf-weasyprint-complete \
  --zip-file fileb://lambda-layer.zip \
  --compatible-runtimes python3.11
```

---

## Testing

After deploying:

1. **Test in Lambda Console:**
   - Use `example_request.json`
   - Check CloudWatch Logs for any missing library errors

2. **Common Errors & Fixes:**

**Error:** `OSError: cannot load library 'gobject-2.0'`
**Fix:** Add `libgobject-2.0.so.0` to lib/

**Error:** `OSError: cannot load library 'pango-1.0'`
**Fix:** Verify `libpango-1.0.so.0` exists in lib/ and set `LD_LIBRARY_PATH`

**Error:** Font rendering issues
**Fix:** Include font files or use web-safe fonts in HTML

---

## References

- **GitHub Issue:** https://github.com/Kozea/WeasyPrint/issues/499
- **Working Example:** https://github.com/Prasengupta/weasyprint_for_awslambda
- **AWS Lambda Layers:** https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html

---

## Current Status

✅ Python packages layer built (40MB)
❌ System libraries NOT yet included

**Next Steps:**
1. Choose method to get system libraries (EC2 / Docker / RPM download)
2. Rebuild layer with libraries
3. Test in Lambda
4. Update deployment guide

---

## Simpler Alternative

If this is too complex, consider:
- **ReportLab** - No system libraries needed, works out-of-box in Lambda
- Existing `pdf_generator_lambda.py` in parent folder uses ReportLab
- Can adapt WeasyPrint code to ReportLab format

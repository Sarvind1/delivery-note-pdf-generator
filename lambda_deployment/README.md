# Lambda Deployment - WeasyPrint PDF Generator

This folder contains everything you need to manually deploy the WeasyPrint PDF generator to AWS Lambda with an optimized layer under 50MB.

## 📁 Files

| File | Description |
|------|-------------|
| `DEPLOYMENT_GUIDE.md` | **START HERE** - Complete step-by-step deployment instructions |
| `build_with_docker.sh` | Automated layer builder using Docker (recommended) |
| `build_layer_optimized.sh` | Manual layer builder (requires system libraries) |
| `lambda_handler.py` | Lambda function handler code |
| `pdf_generator_weasyprint.py` | PDF generator class (WeasyPrint) |
| `requirements_weasyprint.txt` | Python dependencies |
| `call_lambda_api.py` | Example client for invoking Lambda |
| `example_request.json` | Sample test event |
| `SYSTEM_LIBRARIES_PLAN.md` | Technical details about system libraries |

## 🚀 Quick Start

### 1. Build the Lambda Layer

```bash
cd lambda_deployment
./build_with_docker.sh
```

This creates `lambda-layer-optimized.zip` (~45-55MB)

### 2. Follow Deployment Guide

Open `DEPLOYMENT_GUIDE.md` for complete instructions on:
- Uploading the layer to AWS
- Creating the Lambda function
- Configuring environment variables
- Testing and troubleshooting

## 📦 What's in the Layer?

**Python Packages:**
- pandas (for CSV processing)
- weasyprint (PDF generation)
- python-barcode (barcode generation)
- Pillow (image handling)
- numpy (pandas dependency)

**System Libraries (.so files):**
- Cairo, Pango, FontConfig, FreeType (rendering)
- Plus dependencies (libpng, harfbuzz, etc.)

## 🎯 Goal

Deploy `pdf_generator_weasyprint.py` to Lambda with:
- ✅ Layer size < 50MB (for console upload)
- ✅ All system dependencies included
- ✅ Ready for manual deployment

## ⚠️ Important Notes

1. **Docker Required:** The recommended build method uses Docker to ensure compatibility with Amazon Linux 2
2. **System Libraries:** WeasyPrint requires native libraries - pure Python won't work
3. **Manual Deployment:** You'll upload the layer and function through AWS Console or CLI
4. **Environment Variable:** Must set `LD_LIBRARY_PATH=/opt/lib` in Lambda

## 📊 Expected Sizes

- Python packages: ~30-35 MB
- System libraries: ~15-20 MB
- **Total layer:** ~45-55 MB

If over 50MB, you can still deploy via AWS CLI (see deployment guide).

## 🔧 Build Options

### Recommended: Docker Build
```bash
./build_with_docker.sh
```
- ✅ Ensures compatibility
- ✅ Includes all libraries
- ✅ Single command

### Alternative: Manual Build
```bash
./build_layer_optimized.sh
```
- ⚠️ Requires you to obtain .so files separately
- ⚠️ More complex
- See `SYSTEM_LIBRARIES_PLAN.md` for details

## 📖 Documentation

- **DEPLOYMENT_GUIDE.md** - Main deployment instructions
- **SYSTEM_LIBRARIES_PLAN.md** - Technical background on system libraries

## 🧪 Testing Locally

Before deploying, you can test locally:

```bash
python3 pdf_generator_weasyprint.py
```

This generates a sample PDF using the CSV files in the parent directory.

## ❓ Troubleshooting

See the "Common Issues & Fixes" section in `DEPLOYMENT_GUIDE.md`

Common problems:
- Layer too large → Use AWS CLI upload
- Missing libraries → Rebuild with Docker
- Memory errors → Increase Lambda memory
- Timeouts → Increase Lambda timeout

## 📞 Support

For issues specific to:
- **WeasyPrint:** https://github.com/Kozea/WeasyPrint
- **AWS Lambda:** https://docs.aws.amazon.com/lambda/

## ✅ Deployment Checklist

- [ ] Docker installed and running
- [ ] Build layer with `./build_with_docker.sh`
- [ ] Layer size checked (<50MB or prepared for CLI upload)
- [ ] AWS account ready
- [ ] Read `DEPLOYMENT_GUIDE.md`
- [ ] Follow steps 1-7 in deployment guide
- [ ] Test with sample data
- [ ] Verify PDF output

---

**Ready to deploy? Start with `DEPLOYMENT_GUIDE.md`** 🚀

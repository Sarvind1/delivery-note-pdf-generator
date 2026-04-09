# WeasyPrint PDF Generator - AWS Lambda Deployment Guide

This guide explains how to deploy the WeasyPrint-based PDF generator as an AWS Lambda function with API Gateway.

## 📁 Files Overview

- `lambda_function.py` - Lambda handler for API requests
- `pdf_generator_weasyprint_lambda.py` - WeasyPrint PDF generator (JSON input)
- `requirements.txt` - Python dependencies
- `build_layer.sh` - Build Lambda layer (Linux/Mac)
- `build_layer.bat` - Build Lambda layer (Windows)
- `deploy.sh` - Automated deployment script
- `example_request.json` - Sample API request
- `test_local.py` - Local testing script

## ⚠️ Important: WeasyPrint Requirements

WeasyPrint requires **system libraries** (cairo, pango, gdk-pixbuf) that are not included in standard Lambda runtime.

### Options:

1. **Try the basic build** (may work with newer WeasyPrint versions)
2. **Build on Amazon Linux 2** (recommended for production)
3. **Use pre-built community layers** (if available)
4. **Switch to Docker-based Lambda** (not covered in this guide)

## 🚀 Quick Start

### Option A: Automated Deployment (Recommended)

```bash
cd delivery_note_generator
chmod +x deploy.sh
./deploy.sh
```

This script will:
1. Build the Lambda Layer
2. Upload to AWS
3. Create/update Lambda function
4. Optionally create API Gateway

### Option B: Manual Deployment

Follow the detailed steps below.

## 📋 Detailed Deployment Steps

### 1. Build Lambda Layer

**On Linux/Mac:**
```bash
chmod +x build_layer.sh
./build_layer.sh
```

**On Windows:**
```cmd
build_layer.bat
```

This creates `lambda-layer.zip` with all dependencies.

**Note:** If the build fails due to missing system libraries, see "Building on Amazon Linux 2" section below.

### 2. Upload Lambda Layer to AWS

**Via AWS CLI:**
```bash
aws lambda publish-layer-version \
  --layer-name pdf-generator-weasyprint-dependencies \
  --description "WeasyPrint dependencies" \
  --zip-file fileb://lambda-layer.zip \
  --compatible-runtimes python3.11 \
  --region us-east-1
```

**Via AWS Console:**
1. Go to AWS Lambda → Layers → Create layer
2. Name: `pdf-generator-weasyprint-dependencies`
3. Upload `lambda-layer.zip`
4. Compatible runtimes: Python 3.11
5. Click Create

Save the Layer ARN for the next step.

### 3. Create Lambda Function

**Create function package:**
```bash
zip function.zip lambda_function.py pdf_generator_weasyprint_lambda.py
```

**Via AWS Console:**
1. Go to AWS Lambda → Create function
2. Function name: `pdf-generator-weasyprint`
3. Runtime: Python 3.11
4. Architecture: x86_64
5. Click Create function

**Upload code:**
- Upload `function.zip` via console or AWS CLI

**Configure function:**
1. **Add Layer:** Functions → Layers → Add layer → Custom layers → Select your layer
2. **Memory:** 1024 MB (recommended)
3. **Timeout:** 60 seconds
4. **Environment variables:** (optional)
   - `FONT_CONFIG_PATH` if using custom fonts

**Via AWS CLI:**
```bash
aws lambda create-function \
  --function-name pdf-generator-weasyprint \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --layers arn:aws:lambda:REGION:ACCOUNT:layer:pdf-generator-weasyprint-dependencies:VERSION \
  --memory-size 1024 \
  --timeout 60 \
  --region us-east-1
```

### 4. Add S3 Permissions (Optional)

If using S3 upload feature, add this policy to Lambda execution role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

### 5. Create API Gateway

**Via AWS Console:**
1. API Gateway → Create API → REST API
2. Create resource: `/generate-pdf`
3. Create POST method
4. Integration: Lambda Function → Select your function
5. Deploy to stage (e.g., `prod`)
6. Enable CORS if needed

**Via AWS CLI:** (see `deploy.sh` for automation)

### 6. Test the Deployment

**Test locally first:**
```bash
python test_local.py
```

**Test Lambda function:**
```bash
aws lambda invoke \
  --function-name pdf-generator-weasyprint \
  --payload file://example_request.json \
  --region us-east-1 \
  output.json

cat output.json
```

**Test API Gateway:**
```bash
curl -X POST https://YOUR-API-ID.execute-api.REGION.amazonaws.com/prod/generate-pdf \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

## 📝 API Request Format

```json
{
  "non_body_data": {
    "delivery_no": "3701-250909001",
    "po_no": "3302-250800198",
    "buyer": "Lisa Huang",
    "delivery_date": "2025-09-09",
    "inbship_no": "INBSHIP14376",
    "batch_no": "BATCH0008326",
    "supplier": "Company Name",
    "ship_from": "Address",
    "contact_person": "Name",
    "contact_phone": "Phone",
    "delivery_address": "Delivery Address",
    "page_current": 1,
    "page_total": 1
  },
  "body_data": [
    {
      "item_no": "0001",
      "sku": "SKU-123",
      "qty": 512,
      "qty_per_carton": 16,
      "cartons": 32,
      "qc_result": "Pass",
      "length": 50,
      "width": 40,
      "height": 30,
      "ctn_weight": 10,
      "total_cbm": 1.92,
      "total_weight": 320
    }
  ],
  "save_to_s3": false,
  "s3_bucket": "your-bucket-name",
  "s3_key": "path/to/file.pdf"
}
```

## 📤 API Response Format

```json
{
  "message": "PDF generated successfully",
  "pdf_base64": "JVBERi0xLjQKJeLjz9...",
  "s3_bucket": "your-bucket-name",
  "s3_key": "delivery-notes/3701-250909001_20251028_123456.pdf",
  "presigned_url": "https://..."
}
```

## 🔧 Building on Amazon Linux 2 (Production)

If WeasyPrint fails in Lambda, build the layer on Amazon Linux 2:

### Method 1: EC2 Instance

1. Launch Amazon Linux 2 EC2 instance
2. SSH into instance
3. Install dependencies:
```bash
sudo yum update -y
sudo yum install -y python3.11 python3.11-pip zip
sudo yum install -y cairo pango gdk-pixbuf2
```

4. Copy files and build:
```bash
# Upload requirements.txt and build_layer.sh
chmod +x build_layer.sh
./build_layer.sh
```

5. Download `lambda-layer.zip` to your local machine
6. Continue with deployment steps

### Method 2: Docker (Alternative)

```bash
docker run -v "$PWD":/var/task amazonlinux:2 /bin/bash -c "
  yum install -y python3.11 python3.11-pip zip cairo pango gdk-pixbuf2 && \
  pip3.11 install -r requirements.txt -t python/lib/python3.11/site-packages && \
  zip -r lambda-layer.zip python/
"
```

## 🐛 Troubleshooting

### Error: "No module named 'weasyprint'"
- **Cause:** Layer not attached or incorrect Python path
- **Fix:** Verify layer is attached to function, check Python version (3.11)

### Error: "cairo library not found"
- **Cause:** System libraries missing from Lambda environment
- **Fix:** Build layer on Amazon Linux 2 (see above)

### Error: "Layer size too large"
- **Cause:** Layer exceeds 250MB uncompressed limit
- **Fix:** Remove unused dependencies from `requirements.txt`

### Error: "Task timed out"
- **Cause:** PDF generation takes too long
- **Fix:** Increase Lambda timeout (max 15 minutes) or optimize HTML/CSS

### Font rendering issues
- **Cause:** Chinese fonts not available in Lambda
- **Fix:**
  - Include font files in layer
  - Use web-safe fonts as fallback
  - Set `FONT_CONFIG_PATH` environment variable

### PDF displays incorrect characters
- **Cause:** Font fallback to system font
- **Fix:** Embed fonts in HTML using `@font-face` or include in layer

## 💰 Cost Optimization

1. **Reduce layer size:** Remove unused packages
2. **Adjust memory:** Test with 512MB if possible
3. **Use S3 upload:** For large PDFs, return presigned URL instead of base64
4. **Enable CloudWatch Logs:** Monitor execution time and optimize

## 📊 Performance

- **Cold start:** ~2-5 seconds (with WeasyPrint layer)
- **Warm execution:** ~500ms - 2s (depends on PDF complexity)
- **Memory usage:** 200-500MB (typical)
- **Recommended:** 1024MB memory, 60s timeout

## 🔐 Security Best Practices

- [ ] Enable CloudWatch Logs
- [ ] Set up IAM roles with least privilege
- [ ] Use API Gateway with API keys or Cognito
- [ ] Enable WAF for API Gateway
- [ ] Validate input data
- [ ] Set up VPC if accessing private resources
- [ ] Implement rate limiting
- [ ] Use Secrets Manager for sensitive data

## 📚 Additional Resources

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [WeasyPrint Documentation](https://weasyprint.org/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)

## 🆘 Support

If you encounter issues:
1. Check CloudWatch Logs for error details
2. Test locally with `test_local.py`
3. Verify all dependencies are in the layer
4. Ensure system libraries are included (for WeasyPrint)

## 📄 License

This deployment package is provided as-is for educational and commercial use.

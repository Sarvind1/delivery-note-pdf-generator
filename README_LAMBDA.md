# PDF Generator Lambda Deployment Guide

This guide explains how to deploy the PDF generator as an AWS Lambda function accessible via API Gateway.

## Files Overview

- `lambda_function.py` - Main Lambda handler that processes API requests
- `pdf_generator_lambda.py` - Modified PDF generator that works with JSON input
- `requirements.txt` - Python dependencies
- `build_layer.sh` - Script to build Lambda layer (Linux/Mac)
- `build_layer.bat` - Script to build Lambda layer (Windows)
- `example_request.json` - Example API request payload

## Deployment Steps

### 1. Build Lambda Layer

The dependencies (pandas, reportlab, numpy, etc.) are too large to include directly in the Lambda function. You need to create a Lambda Layer.

**On Linux/Mac:**
```bash
chmod +x build_layer.sh
./build_layer.sh
```

**On Windows:**
```cmd
build_layer.bat
```

This creates `lambda-layer.zip` containing all dependencies.

### 2. Upload Lambda Layer to AWS

**Via AWS CLI:**
```bash
aws lambda publish-layer-version \
  --layer-name pdf-generator-dependencies \
  --description "Dependencies for PDF generator" \
  --zip-file fileb://lambda-layer.zip \
  --compatible-runtimes python3.11
```

**Via AWS Console:**
1. Go to AWS Lambda → Layers → Create layer
2. Name: `pdf-generator-dependencies`
3. Upload `lambda-layer.zip`
4. Compatible runtimes: Python 3.11
5. Click Create

Note the Layer ARN - you'll need it for the next step.

### 3. Create Lambda Function

**Via AWS Console:**
1. Go to AWS Lambda → Create function
2. Function name: `pdf-generator`
3. Runtime: Python 3.11
4. Architecture: x86_64
5. Click Create function

**Configure the function:**
1. Upload `lambda_function.py` and `pdf_generator_lambda.py` as a zip:
   ```bash
   zip function.zip lambda_function.py pdf_generator_lambda.py
   ```
2. Upload via Console or CLI:
   ```bash
   aws lambda update-function-code \
     --function-name pdf-generator \
     --zip-file fileb://function.zip
   ```

3. **Attach the Layer:**
   - In Lambda function → Layers → Add a layer
   - Choose custom layers
   - Select `pdf-generator-dependencies`

4. **Configure settings:**
   - Memory: 1024 MB (recommended)
   - Timeout: 60 seconds
   - IAM Role: Add S3 permissions if using S3 upload feature

### 4. Add S3 Permissions (if using S3 upload)

Add this policy to your Lambda execution role:

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
1. Go to API Gateway → Create API
2. Choose REST API (not private)
3. Create new API
4. Create resource (e.g., `/generate-pdf`)
5. Create POST method
6. Integration type: Lambda Function
7. Select your `pdf-generator` function
8. Deploy API to a stage (e.g., `prod`)

**Enable CORS:**
1. Select the resource
2. Actions → Enable CORS
3. Deploy API again

### 6. Test the API

**Using curl:**
```bash
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/generate-pdf \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

**Using Postman:**
1. Method: POST
2. URL: Your API Gateway endpoint
3. Headers: `Content-Type: application/json`
4. Body: Copy content from `example_request.json`

## API Request Format

```json
{
  "non_body_data": {
    "delivery_no": "3701-250909001",
    "po_no": "3302-250800198",
    "buyer": "Lisa Huang",
    "delivery_date": "2025-09-09",
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
      "qty": 100,
      "qty_per_carton": 10,
      "cartons": 10,
      "tail_carton_qty": null,
      "qc_result": "Pass",
      "length": 50,
      "width": 40,
      "height": 30,
      "ctn_weight": 10,
      "total_cbm": 1.5,
      "total_weight": 100
    }
  ],
  "save_to_s3": true,
  "s3_bucket": "your-bucket-name",
  "s3_key": "path/to/file.pdf"
}
```

## API Response Format

```json
{
  "message": "PDF generated successfully",
  "pdf_base64": "JVBERi0xLjQKJeLjz9...",
  "s3_bucket": "your-bucket-name",
  "s3_key": "delivery-notes/3701-250909001_20251015_123456.pdf",
  "presigned_url": "https://your-bucket.s3.amazonaws.com/..."
}
```

### Response Fields:
- `pdf_base64`: Base64-encoded PDF (can be decoded and downloaded)
- `s3_bucket`: S3 bucket name (if S3 upload enabled)
- `s3_key`: S3 object key (if S3 upload enabled)
- `presigned_url`: Temporary download URL valid for 1 hour (if S3 upload enabled)

## Decode PDF from Response

**Python:**
```python
import base64

response = api_response_json
pdf_bytes = base64.b64decode(response['pdf_base64'])
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

**JavaScript:**
```javascript
const pdfBase64 = response.pdf_base64;
const pdfBlob = new Blob([Uint8Array.from(atob(pdfBase64), c => c.charCodeAt(0))],
                         {type: 'application/pdf'});
const url = URL.createObjectURL(pdfBlob);
window.open(url);
```

## Cost Optimization

1. **Reduce Layer Size:** Remove unused dependencies
2. **Adjust Memory:** Test with lower memory (512 MB) if possible
3. **Use S3 Upload:** For large PDFs, return presigned URL instead of base64
4. **Enable CloudWatch Logs:** Monitor and optimize execution time

## Troubleshooting

**Layer too large (>50MB compressed, >250MB uncompressed):**
- Remove unnecessary packages from requirements.txt
- Use slim versions of libraries if available

**Timeout errors:**
- Increase Lambda timeout (max 15 minutes)
- Optimize PDF generation code

**Memory errors:**
- Increase Lambda memory allocation
- Process data in smaller batches

**Import errors:**
- Verify layer is attached to function
- Check Python version compatibility (3.11)

## Local Testing

Test the Lambda function locally:

```python
from lambda_function import lambda_handler
import json

with open('example_request.json') as f:
    event = json.load(f)

result = lambda_handler(event, None)
print(result)
```

## Production Checklist

- [ ] Enable CloudWatch Logs
- [ ] Set up CloudWatch Alarms for errors
- [ ] Configure Dead Letter Queue (DLQ)
- [ ] Enable X-Ray tracing
- [ ] Set up API Gateway usage plans and API keys
- [ ] Configure WAF for API Gateway (if needed)
- [ ] Set up VPC (if accessing private resources)
- [ ] Implement rate limiting
- [ ] Add authentication (API Key, Cognito, IAM)
- [ ] Set up monitoring and alerts

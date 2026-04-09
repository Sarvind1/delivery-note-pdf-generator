# Manual Lambda Deployment Guide
## WeasyPrint PDF Generator

This guide walks you through manually deploying the WeasyPrint PDF generator to AWS Lambda with a layer under 50MB.

---

## Prerequisites

- AWS Account with Lambda access
- AWS CLI installed (optional, for >50MB layers)
- Docker installed (for building the layer)

---

## Step 1: Build the Lambda Layer

### Option A: Using Docker (Recommended)

```bash
cd lambda_deployment
./build_with_docker.sh
```

This will create `lambda-layer-optimized.zip` with:
- Python packages (pandas, weasyprint, pillow, etc.)
- System libraries (.so files for Cairo, Pango, etc.)

**Expected size:** 45-55MB

### Option B: Manual Build (macOS/Windows)

If you don't have Docker, you can:
1. Use an EC2 Amazon Linux 2 instance
2. Install packages and copy libraries manually
3. See `SYSTEM_LIBRARIES_PLAN.md` for details

---

## Step 2: Upload Lambda Layer

### If layer is <50MB:

1. Go to AWS Lambda Console
2. Navigate to **Layers** → **Create layer**
3. Fill in:
   - **Name:** `weasyprint-pdf-layer`
   - **Upload:** Choose `lambda-layer-optimized.zip`
   - **Compatible runtimes:** Python 3.11
4. Click **Create**

### If layer is >50MB:

Use AWS CLI:

```bash
aws lambda publish-layer-version \
  --layer-name weasyprint-pdf-layer \
  --zip-file fileb://lambda-layer-optimized.zip \
  --compatible-runtimes python3.11 \
  --region us-east-1
```

**Note the Layer Version ARN** from the output - you'll need it.

---

## Step 3: Create Lambda Function

### 3.1 Create Function

1. Go to AWS Lambda Console
2. Click **Create function**
3. Choose **Author from scratch**
4. Fill in:
   - **Function name:** `delivery-note-pdf-generator`
   - **Runtime:** Python 3.11
   - **Architecture:** x86_64
5. Click **Create function**

### 3.2 Attach the Layer

1. In the function page, scroll to **Layers** section
2. Click **Add a layer**
3. Choose **Custom layers**
4. Select your layer: `weasyprint-pdf-layer`
5. Choose the latest version
6. Click **Add**

### 3.3 Configure Environment Variables

1. Go to **Configuration** → **Environment variables**
2. Click **Edit** → **Add environment variable**
3. Add:
   - **Key:** `LD_LIBRARY_PATH`
   - **Value:** `/opt/lib`
4. Click **Save**

This tells Lambda where to find the system libraries.

### 3.4 Increase Memory & Timeout

1. Go to **Configuration** → **General configuration**
2. Click **Edit**
3. Set:
   - **Memory:** 512 MB (or higher if PDFs are large)
   - **Timeout:** 30 seconds
4. Click **Save**

---

## Step 4: Upload Function Code

### 4.1 Prepare Function Package

Create a zip with your function code:

```bash
cd lambda_deployment
zip function.zip lambda_handler.py pdf_generator_weasyprint.py
```

### 4.2 Upload to Lambda

**Via Console:**
1. In Lambda function page, go to **Code** tab
2. Click **Upload from** → **.zip file**
3. Choose `function.zip`
4. Click **Save**

**Via AWS CLI:**
```bash
aws lambda update-function-code \
  --function-name delivery-note-pdf-generator \
  --zip-file fileb://function.zip
```

### 4.3 Set Handler

1. Go to **Runtime settings** (in Code tab)
2. Click **Edit**
3. Set **Handler:** `lambda_handler.lambda_handler`
4. Click **Save**

---

## Step 5: Test the Function

### 5.1 Create Test Event

1. In Lambda function page, click **Test** tab
2. Click **Create new event**
3. Event name: `test-pdf-generation`
4. Use this JSON (based on your CSV structure):

```json
{
  "non_body_data": [
    {
      "QI type": "DN-2024-001",
      "po_no": "PO123456",
      "buyer": "John Doe",
      "delivery_date": "2024-10-28",
      "inbship_no": "SHIP001",
      "batch_no": "BATCH001",
      "supplier": "Test Supplier Co.",
      "ship_from": "123 Factory Street, City",
      "contact_person": "Jane Smith",
      "contact_phone": "+1234567890",
      "delivery_address": "456 Warehouse Ave, City",
      "page_current": 1,
      "page_total": 1
    }
  ],
  "body_data": [
    {
      "item_no": 1,
      "sku": "SKU-001",
      "qty": 100,
      "qty_per_carton": 50,
      "cartons": 2,
      "qc_result": "PASS",
      "length": 40,
      "width": 30,
      "height": 20,
      "ctn_weight": 5.5,
      "total_cbm": 0.024,
      "total_weight": 11
    }
  ]
}
```

5. Click **Save**
6. Click **Test**

### 5.2 Check Results

**Success Response:**
```json
{
  "statusCode": 200,
  "body": {
    "message": "PDF generated successfully",
    "pdf_base64": "JVBERi0xLjQK...",
    "size_bytes": 45678
  }
}
```

**Error Response:**
Check CloudWatch Logs for details:
- Go to **Monitor** tab → **View CloudWatch logs**

---

## Step 6: Common Issues & Fixes

### Issue 1: Missing System Libraries

**Error:** `OSError: cannot load library 'cairo'`

**Fix:**
- Verify layer includes system libraries in `lib/` folder
- Check `LD_LIBRARY_PATH` environment variable is set
- Rebuild layer using Docker method

### Issue 2: Out of Memory

**Error:** `Lambda function exceeded memory limit`

**Fix:**
- Increase Lambda memory (Configuration → General → Memory)
- Try 1024 MB for larger PDFs

### Issue 3: Timeout

**Error:** `Task timed out after 3.00 seconds`

**Fix:**
- Increase timeout (Configuration → General → Timeout)
- Set to at least 30 seconds

### Issue 4: Layer Too Large

**Error:** `Unzipped size must be smaller than X`

**Fix:**
- Use AWS CLI to upload (see Step 2)
- Or optimize further by removing more unnecessary files

### Issue 5: Font Issues

**Error:** `Font rendering problems or missing characters`

**Fix:**
- Add web-safe fonts in HTML/CSS
- Or include font files in the layer

---

## Step 7: Invoke from Application

### Using Python (boto3):

```python
import boto3
import json
import base64

lambda_client = boto3.client('lambda', region_name='us-east-1')

# Prepare event
event = {
    "non_body_data": [...],
    "body_data": [...]
}

# Invoke Lambda
response = lambda_client.invoke(
    FunctionName='delivery-note-pdf-generator',
    InvocationType='RequestResponse',
    Payload=json.dumps(event)
)

# Get result
result = json.loads(response['Payload'].read())
body = json.loads(result['body'])

# Decode PDF
pdf_bytes = base64.b64decode(body['pdf_base64'])

# Save to file
with open('delivery_note.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### Using AWS CLI:

```bash
aws lambda invoke \
  --function-name delivery-note-pdf-generator \
  --payload file://example_request.json \
  --region us-east-1 \
  response.json

cat response.json
```

---

## Layer Size Optimization Tips

If your layer is still >50MB, try:

1. **Remove more packages:**
   - Check if you really need all pandas features
   - Consider using `openpyxl` instead of full pandas

2. **Strip binaries:**
   ```bash
   find python/ -name "*.so" -exec strip {} \;
   ```

3. **Remove locale files:**
   ```bash
   find python/ -type d -name "locale" -exec rm -rf {} +
   ```

4. **Use minimal numpy:**
   Instead of full numpy, install minimal binary wheels

---

## Costs

- **Lambda Layer storage:** Free (first 50GB)
- **Lambda invocations:** Free tier = 1M requests/month
- **Lambda compute:** Free tier = 400,000 GB-seconds/month

**Estimated cost per PDF:**
- Memory: 512 MB
- Duration: ~2 seconds
- Cost: $0.000001667 per invocation
- **~$1.67 per 1 million PDFs**

---

## Next Steps

1. ✅ Build layer
2. ✅ Upload layer to Lambda
3. ✅ Create Lambda function
4. ✅ Test with sample data
5. 🔄 Integrate with your application
6. 🔄 Set up API Gateway (optional, for HTTP access)
7. 🔄 Add authentication/authorization

---

## Support Files

- `build_with_docker.sh` - Automated layer builder
- `build_layer_optimized.sh` - Manual builder (requires .so files)
- `lambda_handler.py` - Lambda function code
- `pdf_generator_weasyprint.py` - PDF generator class
- `call_lambda_api.py` - Example client script
- `SYSTEM_LIBRARIES_PLAN.md` - Technical details

---

## Troubleshooting Checklist

- [ ] Layer uploaded successfully
- [ ] Layer attached to function
- [ ] Environment variable `LD_LIBRARY_PATH=/opt/lib` set
- [ ] Handler set to `lambda_handler.lambda_handler`
- [ ] Memory ≥ 512 MB
- [ ] Timeout ≥ 30 seconds
- [ ] Python runtime is 3.11
- [ ] Test event JSON is valid
- [ ] CloudWatch Logs show no errors

---

**Good luck with your deployment! 🚀**

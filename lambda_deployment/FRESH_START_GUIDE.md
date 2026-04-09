# Fresh Start Guide: Deploy WeasyPrint to AWS Lambda

**Starting Point:** You have only `pdf_generator_weasyprint.py`

**Goal:** Deploy it to AWS Lambda using a pre-built, tested layer

**Approach:** Use Kotify's maintained WeasyPrint layer (Python 3.12)

---

## Prerequisites

- AWS Account with Lambda access
- Your `pdf_generator_weasyprint.py` file
- Basic knowledge of AWS Console

---

## Step 1: Download Pre-built WeasyPrint Layer

### 1.1 Get the Layer

1. Go to: https://github.com/kotify/cloud-print-utils/releases
2. Find the latest release
3. Download: **`weasyprint-layer-python3.12-x86_64.zip`**
   - Size: ~60-80 MB
   - Python: 3.12
   - Architecture: x86_64 (Intel/AMD)

4. Save to your Downloads folder

### 1.2 What's Included

This layer contains:
- ✅ WeasyPrint Python package
- ✅ All system libraries (Cairo, Pango, fontconfig, etc.)
- ✅ Fonts
- ✅ All dependencies pre-compiled for Lambda

---

## Step 2: Create Lambda Handler

Create a new file called `lambda_handler.py`:

```python
#!/usr/bin/env python3
"""
Lambda handler for WeasyPrint PDF generation
"""

import json
import base64
import pandas as pd
from io import BytesIO
from pdf_generator_weasyprint import DeliveryNotePDFGeneratorWeasy


def lambda_handler(event, context):
    """
    Lambda function handler for PDF generation

    Expected event structure:
    {
        "non_body_data": [{...}],  # Single record with header info
        "body_data": [{...}]       # Array of line items
    }

    OR:
    {
        "non_body_csv": "base64_encoded_csv",
        "body_csv": "base64_encoded_csv"
    }
    """

    try:
        # Option 1: JSON data
        if 'non_body_data' in event and 'body_data' in event:
            non_body_path = '/tmp/non_body.csv'
            body_path = '/tmp/body.csv'

            # Convert JSON to CSV
            pd.DataFrame(event['non_body_data']).to_csv(non_body_path, index=False)
            pd.DataFrame(event['body_data']).to_csv(body_path, index=False)

        # Option 2: Base64 CSV data
        elif 'non_body_csv' in event and 'body_csv' in event:
            non_body_csv = base64.b64decode(event['non_body_csv']).decode('utf-8')
            body_csv = base64.b64decode(event['body_csv']).decode('utf-8')

            non_body_path = '/tmp/non_body.csv'
            body_path = '/tmp/body.csv'

            with open(non_body_path, 'w') as f:
                f.write(non_body_csv)
            with open(body_path, 'w') as f:
                f.write(body_csv)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid input. Provide non_body_data + body_data OR non_body_csv + body_csv'
                })
            }

        # Generate PDF
        output_path = '/tmp/delivery_note.pdf'
        generator = DeliveryNotePDFGeneratorWeasy(
            non_body_csv=non_body_path,
            body_csv=body_path,
            output_pdf=output_path
        )
        generator.generate_pdf()

        # Read PDF and encode to base64
        with open(output_path, 'rb') as f:
            pdf_content = f.read()

        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'PDF generated successfully',
                'pdf_base64': pdf_base64,
                'size_bytes': len(pdf_content)
            })
        }

    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'traceback': traceback.format_exc()
            })
        }
```

---

## Step 3: Package Your Function Code

### 3.1 Create Function Zip

Create a zip file with your code:

```bash
zip function.zip lambda_handler.py pdf_generator_weasyprint.py
```

**Contents:**
- `lambda_handler.py` - Lambda entry point
- `pdf_generator_weasyprint.py` - Your PDF generator

**Note:** Don't include pandas, weasyprint, etc. - they're in the layer!

---

## Step 4: Upload Layer to AWS Lambda

### 4.1 Create Layer

1. Go to **AWS Lambda Console**
2. Click **Layers** (left sidebar)
3. Click **Create layer**
4. Fill in:
   - **Name:** `weasyprint-layer-python312`
   - **Description:** Pre-built WeasyPrint layer from Kotify
   - **Upload:** Choose the downloaded `weasyprint-layer-python3.12-x86_64.zip`
   - **Compatible runtimes:** Select **Python 3.12**
   - **Compatible architectures:** Select **x86_64**
5. Click **Create**

### 4.2 Note the Layer ARN

After creation, copy the **Layer ARN** - you'll need it:
```
arn:aws:lambda:us-east-1:123456789:layer:weasyprint-layer-python312:1
```

---

## Step 5: Create Lambda Function

### 5.1 Create Function

1. Go to **AWS Lambda Console**
2. Click **Create function**
3. Choose **Author from scratch**
4. Fill in:
   - **Function name:** `delivery-note-pdf-generator`
   - **Runtime:** **Python 3.12**
   - **Architecture:** **x86_64**
5. Click **Create function**

### 5.2 Upload Function Code

1. In the function page, go to **Code** tab
2. Click **Upload from** → **.zip file**
3. Choose your `function.zip`
4. Click **Save**

### 5.3 Configure Handler

1. Scroll down to **Runtime settings**
2. Click **Edit**
3. Set **Handler:** `lambda_handler.lambda_handler`
4. Click **Save**

---

## Step 6: Attach the Layer

### 6.1 Add Layer to Function

1. Scroll down to **Layers** section
2. Click **Add a layer**
3. Choose **Custom layers**
4. Select: `weasyprint-layer-python312`
5. Version: `1` (or latest)
6. Click **Add**

You should now see the layer attached in the Layers section.

---

## Step 7: Configure Environment Variables

### 7.1 Set Required Variables

1. Go to **Configuration** tab
2. Click **Environment variables** (left menu)
3. Click **Edit**
4. Add two variables:

| Key | Value |
|-----|-------|
| `LD_LIBRARY_PATH` | `/opt/lib` |
| `FONTCONFIG_PATH` | `/opt/fonts` |

5. Click **Save**

**Why these are needed:**
- `LD_LIBRARY_PATH`: Tells Lambda where to find system libraries (.so files)
- `FONTCONFIG_PATH`: Tells fontconfig where to find fonts

---

## Step 8: Configure Memory and Timeout

### 8.1 Adjust Settings

1. Go to **Configuration** tab
2. Click **General configuration**
3. Click **Edit**
4. Set:
   - **Memory:** `512 MB` (or higher for large PDFs)
   - **Timeout:** `30 seconds`
5. Click **Save**

**Why:**
- PDF generation is memory-intensive
- Complex PDFs may take 5-10 seconds

---

## Step 9: Create Test Event

### 9.1 Create Test

1. Go to **Test** tab
2. Click **Create new event**
3. Event name: `test-pdf-generation`
4. Use this JSON:

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

---

## Step 10: Test Your Function

### 10.1 Run Test

1. Click **Test** button
2. Wait for execution (should take 3-10 seconds)

### 10.2 Success Response

You should see:

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

### 10.3 Decode PDF (Optional)

To view the PDF locally:

```python
import base64

# Copy the pdf_base64 string from response
pdf_base64 = "JVBERi0xLjQK..."  # Your base64 string

# Decode and save
pdf_bytes = base64.b64decode(pdf_base64)
with open('test_output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

---

## Troubleshooting

### Issue 1: "Module not found" errors

**Problem:** Lambda can't find weasyprint, pandas, etc.

**Solution:**
1. Check layer is attached (Step 6)
2. Verify layer version is correct
3. Check runtime is Python 3.12

### Issue 2: "Cannot load library" errors

**Problem:** System libraries not found

**Solution:**
1. Check environment variables are set (Step 7)
2. Verify `LD_LIBRARY_PATH=/opt/lib`
3. Verify `FONTCONFIG_PATH=/opt/fonts`

### Issue 3: Timeout

**Problem:** Function times out before completing

**Solution:**
1. Increase timeout to 60 seconds (Step 8)
2. Increase memory to 1024 MB
3. Simplify your PDF (fewer items)

### Issue 4: Out of memory

**Problem:** Lambda runs out of memory

**Solution:**
1. Increase memory to 1024 MB or 2048 MB
2. Process PDFs in batches
3. Reduce image sizes in HTML

### Issue 5: Function works but PDF is blank/corrupted

**Problem:** PDF generates but looks wrong

**Solution:**
1. Check your CSV data format
2. Verify all required fields are present
3. Check for special characters in data
4. Review CloudWatch Logs for warnings

---

## Invoking from Your Application

### Python (boto3)

```python
import boto3
import json
import base64

lambda_client = boto3.client('lambda', region_name='us-east-1')

# Prepare event
event = {
    "non_body_data": [{...}],
    "body_data": [{...}]
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
if result['statusCode'] == 200:
    pdf_bytes = base64.b64decode(body['pdf_base64'])
    with open('delivery_note.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print(f"PDF saved! Size: {body['size_bytes']} bytes")
else:
    print(f"Error: {body.get('error')}")
```

### AWS CLI

```bash
aws lambda invoke \
  --function-name delivery-note-pdf-generator \
  --payload file://test_event.json \
  --region us-east-1 \
  response.json

cat response.json
```

---

## Cost Estimate

**Lambda Pricing (US East 1):**
- Memory: 512 MB
- Avg Duration: 3 seconds
- Requests: 1,000 per month

**Monthly Cost:**
- Compute: $0.00 (within free tier)
- Requests: $0.00 (within free tier)

**Free Tier:**
- 1M requests per month
- 400,000 GB-seconds per month

**After Free Tier:**
- ~$0.30 per 100,000 PDFs

---

## Next Steps

1. ✅ Test with your actual data
2. ✅ Set up API Gateway (if needed for HTTP access)
3. ✅ Add authentication/authorization
4. ✅ Configure CloudWatch alarms
5. ✅ Set up S3 storage (optional, for large PDFs)

---

## Additional Resources

- **Kotify Cloud Print Utils:** https://github.com/kotify/cloud-print-utils
- **WeasyPrint Docs:** https://doc.courtbouillon.org/weasyprint/
- **AWS Lambda Docs:** https://docs.aws.amazon.com/lambda/

---

## Comparison: This Approach vs Building Your Own

| Aspect | Pre-built Layer (Kotify) | Build Your Own |
|--------|-------------------------|----------------|
| Setup Time | 30 minutes | 4-8 hours |
| Success Rate | ~95% | ~50% |
| Maintenance | Community maintained | You maintain |
| Python Version | 3.12 required | Any version |
| Layer Size | ~70MB | Varies |
| Dependencies | All included | Must compile all |

---

## Why This Works

✅ **Pre-compiled:** All system libraries compiled for Lambda's environment
✅ **Tested:** Used by many production applications
✅ **Maintained:** Regular updates for new WeasyPrint versions
✅ **Complete:** Includes fonts, configs, and all dependencies
✅ **Documented:** Clear instructions and examples

---

## Summary

You've now deployed WeasyPrint to AWS Lambda using a battle-tested, pre-built layer. This approach:

- ✅ Avoids dependency hell
- ✅ Uses proven infrastructure
- ✅ Saves hours of troubleshooting
- ✅ Gets you a production-ready function

**Total time:** ~30 minutes
**Success rate:** Very high

**Trade-off:** Must use Python 3.12 instead of 3.9

---

**Happy PDF Generating! 🎉**

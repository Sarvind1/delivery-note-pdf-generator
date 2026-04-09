# WeasyPrint PDF Generator for AWS Lambda

**Status:** ✅ Tested and working locally

This folder contains everything you need to deploy a Chinese delivery note PDF generator to AWS Lambda.

---

## 📦 What's Included

### Ready-to-Deploy Files:
- **`lambda-layer.zip`** (66MB) - Python dependencies package
- **`function.zip`** (4.6KB) - Lambda function code
- **`example_request.json`** - Sample test data

### Deployment Guide:
- **`DEPLOYMENT_STEPS.md`** ← **START HERE** - Simple step-by-step AWS Console instructions

### Additional Documentation:
- **`README_LAMBDA_WEASYPRINT.md`** - Detailed technical documentation with troubleshooting

---

## 🚀 Quick Start

### Option 1: Simple AWS Console Deployment (Recommended for beginners)
**Follow:** `DEPLOYMENT_STEPS.md`

This guide walks you through:
1. Uploading the layer via AWS Console
2. Creating the Lambda function
3. Attaching the layer
4. Configuring settings
5. Testing
6. (Optional) Creating API Gateway

**Time:** ~15 minutes

### Option 2: Detailed Technical Setup
**Follow:** `README_LAMBDA_WEASYPRINT.md`

For advanced users who want to understand the architecture, build from source, or troubleshoot issues.

---

## ⚡ Testing

### Local Test (Already Done ✅):
```bash
python3 test_local_simple.py
```
**Result:** Generated `test_output.pdf` successfully

### Lambda Test:
After deployment, use `example_request.json` as test event in Lambda console.

---

## 📋 PDF Features

The generated delivery note includes:
- ✅ Bilingual Chinese/English headers
- ✅ INBSHIP No. and Batch No. fields
- ✅ Barcode (format: P{INBSHIP_NO})
- ✅ Product table with quantities, dimensions, weights
- ✅ Supplier and delivery information
- ✅ Signature line

---

## ⚠️ Important Warning

### WeasyPrint System Dependencies

WeasyPrint requires **cairo** and **pango** system libraries that may not be in the Lambda layer.

**If deployment fails with "cairo not found" or "pango not found":**
- The current layer may not include system libraries
- You'll need to build the layer on Amazon Linux 2
- See `README_LAMBDA_WEASYPRINT.md` section "Building on Amazon Linux 2"

**Success depends on:** Lambda environment having compatible system libraries.

---

## 🗂️ File Structure

```
delivery_note_generator/
├── 📄 README.md (this file)
├── 📘 DEPLOYMENT_STEPS.md (simple guide)
├── 📘 README_LAMBDA_WEASYPRINT.md (detailed docs)
│
├── 📦 lambda-layer.zip (upload to Lambda Layer)
├── 📦 function.zip (upload to Lambda Function)
├── 📄 example_request.json (test data)
│
├── 🐍 lambda_function.py (source code)
├── 🐍 pdf_generator_weasyprint_lambda.py (source code)
├── 🐍 test_local_simple.py (local testing)
│
└── ⚙️ build_layer.sh/bat (rebuild scripts)
```

---

## 💰 AWS Costs

Estimated costs (US East region):
- **Lambda:** ~$0.20 per 1M requests
- **API Gateway:** ~$3.50 per 1M requests
- **Storage:** Negligible

**Free Tier:** 1M Lambda requests/month free

---

## 🆘 Need Help?

1. **Start with:** `DEPLOYMENT_STEPS.md` - Follow each step carefully
2. **Check logs:** CloudWatch Logs in AWS Lambda console
3. **Common issues:** See Troubleshooting in `DEPLOYMENT_STEPS.md`
4. **Detailed help:** See `README_LAMBDA_WEASYPRINT.md`

---

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
    ...
  },
  "body_data": [
    {
      "item_no": "0001",
      "sku": "SKU-123",
      "qty": 512,
      "qty_per_carton": 16,
      "cartons": 32,
      ...
    }
  ]
}
```

See `example_request.json` for complete example.

---

## 🎯 Next Steps

1. ✅ Read `DEPLOYMENT_STEPS.md`
2. ✅ Upload `lambda-layer.zip` to AWS Lambda Layers
3. ✅ Upload `function.zip` to AWS Lambda Function
4. ✅ Configure and test
5. ✅ (Optional) Create API Gateway endpoint

Good luck! 🚀

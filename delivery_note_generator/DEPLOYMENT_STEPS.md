# Simple Lambda Deployment Steps

✅ **Pre-built files ready in this folder:**
- `lambda-layer.zip` (66MB) - Dependencies
- `function.zip` (4.6KB) - Lambda code
- `example_request.json` - Test data

---

## Step 1: Upload Lambda Layer

1. Go to **AWS Lambda Console** → **Layers** → **Create layer**
2. Fill in:
   - **Name:** `pdf-weasyprint-layer` (or any name you want)
   - **Upload:** Click "Upload" and select `lambda-layer.zip`
   - **Compatible runtimes:** Select `Python 3.11` or `Python 3.13`
3. Click **Create**
4. **Copy the Layer ARN** (looks like: `arn:aws:lambda:region:account:layer:pdf-weasyprint-layer:1`)

---

## Step 2: Create Lambda Function

1. Go to **AWS Lambda Console** → **Functions** → **Create function**
2. Fill in:
   - **Function name:** `pdf-generator` (or any name)
   - **Runtime:** `Python 3.11` or `Python 3.13`
   - **Architecture:** `x86_64`
3. Click **Create function**

---

## Step 3: Upload Function Code

1. In your Lambda function page, scroll to **Code** section
2. Click **Upload from** → **.zip file**
3. Select `function.zip`
4. Click **Save**

---

## Step 4: Attach the Layer

1. Scroll down to **Layers** section
2. Click **Add a layer**
3. Select **Custom layers**
4. Choose your layer: `pdf-weasyprint-layer`
5. Select **Version 1**
6. Click **Add**

---

## Step 5: Configure Function Settings

1. Go to **Configuration** tab → **General configuration** → **Edit**
2. Change:
   - **Memory:** `1024 MB`
   - **Timeout:** `1 min 0 sec`
3. Click **Save**

---

## Step 6: Test the Function

1. Go to **Test** tab
2. Click **Create new event**
3. **Event name:** `test-pdf`
4. **Event JSON:** Copy and paste contents from `example_request.json`
5. Click **Save**
6. Click **Test** button
7. **Check response:**
   - Should see `"statusCode": 200`
   - Should see `"message": "PDF generated successfully"`
   - Should see `"pdf_base64"` with long encoded string

---

## Step 7: Create API Gateway (Optional)

### If you want a REST API endpoint:

1. Go to **API Gateway Console** → **Create API** → **REST API** (not private) → **Build**
2. **API name:** `pdf-generator-api`
3. Click **Create API**

4. **Create Resource:**
   - Click **Actions** → **Create Resource**
   - **Resource name:** `generate-pdf`
   - Click **Create Resource**

5. **Create POST Method:**
   - Select `/generate-pdf` resource
   - Click **Actions** → **Create Method** → Select **POST**
   - **Integration type:** Lambda Function
   - **Lambda Function:** Select your function (`pdf-generator`)
   - Click **Save** → Click **OK** on the popup

6. **Enable CORS (if needed):**
   - Select `/generate-pdf` resource
   - Click **Actions** → **Enable CORS**
   - Click **Enable CORS and replace existing CORS headers**

7. **Deploy API:**
   - Click **Actions** → **Deploy API**
   - **Deployment stage:** [New Stage] → Name it `prod`
   - Click **Deploy**

8. **Get API URL:**
   - Copy the **Invoke URL** (looks like: `https://abc123.execute-api.us-east-1.amazonaws.com/prod`)
   - Your endpoint will be: `https://abc123.execute-api.us-east-1.amazonaws.com/prod/generate-pdf`

---

## Testing Your API

Use curl or Postman:

```bash
curl -X POST https://YOUR-API-URL/generate-pdf \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

---

## ⚠️ Important Notes

### Layer Size Warning
- The layer is **66MB compressed**
- AWS limit is 50MB for direct console upload
- If upload fails:
  - Option 1: Use AWS CLI: `aws lambda publish-layer-version --layer-name pdf-weasyprint-layer --zip-file fileb://lambda-layer.zip --compatible-runtimes python3.11`
  - Option 2: Upload to S3 first, then reference S3 URL when creating layer

### WeasyPrint System Libraries
- WeasyPrint requires **cairo** and **pango** system libraries
- The current layer may NOT work in Lambda without these libraries
- **If you get import errors:**
  1. Build the layer on Amazon Linux 2 (EC2 instance or Docker)
  2. Include Pango libraries as mentioned in GitHub issue #499
  3. See detailed instructions in `README_LAMBDA_WEASYPRINT.md`

### Python Runtime
- Built for Python 3.11/3.13
- Make sure Lambda function uses same Python version

---

## Troubleshooting

### Error: "No module named 'weasyprint'"
- Layer not attached or wrong Python version
- **Fix:** Re-attach layer, check Python runtime matches

### Error: "cairo library not found" or "pango not found"
- System libraries missing (expected issue)
- **Fix:** Build layer on Amazon Linux 2 with system libraries included
- See full instructions in `README_LAMBDA_WEASYPRINT.md`

### Error: "Task timed out after 3.00 seconds"
- Timeout too short
- **Fix:** Increase timeout to 60 seconds in Configuration

### Layer upload fails
- File too large for console upload
- **Fix:** Use AWS CLI or S3 upload method

---

## Files in This Folder

- ✅ `lambda-layer.zip` - Ready to upload as Lambda Layer
- ✅ `function.zip` - Ready to upload as Lambda Function code
- ✅ `example_request.json` - Test event data
- 📄 `lambda_function.py` - Source code (already in function.zip)
- 📄 `pdf_generator_weasyprint_lambda.py` - PDF generator (already in function.zip)
- 📄 `requirements.txt` - Dependencies list (already in lambda-layer.zip)
- 📘 `README_LAMBDA_WEASYPRINT.md` - Detailed documentation

---

## Need Help?

1. Check CloudWatch Logs in Lambda console for error details
2. Test locally first with `test_local_simple.py`
3. Review `README_LAMBDA_WEASYPRINT.md` for detailed troubleshooting

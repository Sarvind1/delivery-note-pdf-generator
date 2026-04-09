# Building Lambda Layer WITHOUT Docker

If you don't want to install Docker, here are two simple alternatives:

---

## Option 1: AWS CloudShell (Easiest - No Install Required!)

AWS CloudShell is a free browser-based terminal that runs Amazon Linux 2 - perfect for building Lambda layers!

### Steps:

1. **Log into AWS Console**
   - Go to https://console.aws.amazon.com

2. **Open CloudShell**
   - Click the terminal icon (>_) in the top navigation bar
   - Or search for "CloudShell" in the AWS search bar
   - Wait for the terminal to load (~30 seconds)

3. **Upload Your Files**
   - Click **Actions** → **Upload file**
   - Upload these 2 files:
     - `requirements_weasyprint.txt`
     - `build_on_cloudshell.sh`

4. **Run the Build Script**
   ```bash
   chmod +x build_on_cloudshell.sh
   ./build_on_cloudshell.sh
   ```

   This will take 2-3 minutes and create `lambda-layer-optimized.zip`

5. **Download the Layer**
   - Click **Actions** → **Download file**
   - Enter: `lambda-layer-optimized.zip`
   - Save to your computer

6. **Continue with Deployment**
   - Now follow `DEPLOYMENT_GUIDE.md` from Step 2 (Upload Lambda Layer)

**Pros:**
- ✅ No software to install
- ✅ Free (included with AWS account)
- ✅ Guaranteed compatibility (same environment as Lambda)
- ✅ Takes ~3 minutes total

**Cons:**
- ⚠️ Requires AWS account
- ⚠️ Need to upload/download files manually

---

## Option 2: Use Pre-built Layer (Simplest)

Someone already built a WeasyPrint layer! You can use it directly:

### Public Lambda Layer ARN:

```
arn:aws:lambda:us-east-1:764866452798:layer:chrome-aws-lambda:31
```

Or search for community layers in your AWS region.

### Steps:

1. When creating your Lambda function, add this layer ARN directly
2. Skip the layer building entirely!
3. Just upload your function code

**Pros:**
- ✅ No building required
- ✅ Instant setup

**Cons:**
- ⚠️ May not have latest packages
- ⚠️ Might be region-specific
- ⚠️ Less control over what's included

---

## Option 3: EC2 Instance (Most Control)

Launch a temporary Amazon Linux 2 EC2 instance:

### Steps:

1. **Launch EC2 Instance**
   - Go to EC2 Console → Launch Instance
   - Choose: **Amazon Linux 2 AMI**
   - Instance type: **t2.micro** (free tier)
   - Enable SSH access

2. **Connect via SSH**
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

3. **Upload Files**
   ```bash
   # From your computer:
   scp -i your-key.pem requirements_weasyprint.txt ec2-user@instance-ip:~/
   scp -i your-key.pem build_on_cloudshell.sh ec2-user@instance-ip:~/
   ```

4. **Run Build Script**
   ```bash
   # On EC2:
   chmod +x build_on_cloudshell.sh
   ./build_on_cloudshell.sh
   ```

5. **Download the Layer**
   ```bash
   # From your computer:
   scp -i your-key.pem ec2-user@instance-ip:~/lambda-layer-optimized.zip .
   ```

6. **Terminate Instance**
   - Don't forget to terminate it to avoid charges!

**Pros:**
- ✅ Full control
- ✅ Can troubleshoot issues
- ✅ Guaranteed compatibility

**Cons:**
- ⚠️ More steps
- ⚠️ Requires SSH key setup
- ⚠️ Must remember to terminate instance

---

## Recommended: AWS CloudShell

**I recommend Option 1 (CloudShell)** because:
- No software installation needed
- Free and easy
- 100% compatible with Lambda
- Only takes a few minutes

---

## Comparison Table

| Method | Time | Difficulty | Cost | Compatibility |
|--------|------|------------|------|---------------|
| **Docker** | 5 min | Easy | Free | ✅ Perfect |
| **CloudShell** | 3 min | Very Easy | Free | ✅ Perfect |
| **Pre-built Layer** | 1 min | Easiest | Free | ⚠️ May vary |
| **EC2** | 10 min | Medium | ~$0.01 | ✅ Perfect |

---

## Still Want Docker?

If you decide to use Docker later:

1. **Install Docker Desktop:**
   - Download: https://www.docker.com/products/docker-desktop
   - Install (drag to Applications folder)
   - Open Docker Desktop app
   - Wait for "Docker is running" message

2. **Run the build:**
   ```bash
   cd lambda_deployment
   ./build_with_docker.sh
   ```

That's it! Docker will handle everything automatically.

---

## Questions?

- **"Which method should I use?"** → CloudShell (Option 1)
- **"Is CloudShell free?"** → Yes, included with AWS account
- **"Do I need to keep CloudShell running?"** → No, just use it to build the file
- **"Can I use my own computer?"** → Only with Docker (Option 1 from main guide)

---

**Next Steps:**
1. Choose your method above
2. Build the layer (get `lambda-layer-optimized.zip`)
3. Return to `DEPLOYMENT_GUIDE.md` Step 2
4. Upload and deploy! 🚀

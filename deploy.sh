#!/bin/bash

# Quick deployment script for Lambda function
# Prerequisites: AWS CLI configured with appropriate credentials

set -e

FUNCTION_NAME="pdf-generator"
LAYER_NAME="pdf-generator-dependencies"
RUNTIME="python3.11"
HANDLER="lambda_function.lambda_handler"
MEMORY=1024
TIMEOUT=60
REGION=${AWS_REGION:-us-east-1}

echo "🚀 Deploying PDF Generator Lambda Function..."
echo "Region: $REGION"
echo ""

# Step 1: Build and upload layer
echo "📦 Step 1: Building Lambda Layer..."
./build_layer.sh

echo ""
echo "⬆️  Step 2: Uploading Lambda Layer..."
LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --description "Dependencies for PDF generator (pandas, reportlab, etc.)" \
    --zip-file fileb://lambda-layer.zip \
    --compatible-runtimes $RUNTIME \
    --region $REGION \
    --query 'Version' \
    --output text)

LAYER_ARN=$(aws lambda list-layer-versions \
    --layer-name $LAYER_NAME \
    --region $REGION \
    --query "LayerVersions[0].LayerVersionArn" \
    --output text)

echo "✅ Layer uploaded: $LAYER_ARN"

# Step 2: Package Lambda function
echo ""
echo "📦 Step 3: Packaging Lambda Function..."
rm -f function.zip
zip -r function.zip lambda_function.py pdf_generator_lambda.py

# Step 3: Check if function exists
echo ""
echo "🔍 Step 4: Checking if function exists..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Function exists, updating code..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://function.zip \
        --region $REGION

    echo "Updating function configuration..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --handler $HANDLER \
        --memory-size $MEMORY \
        --timeout $TIMEOUT \
        --layers $LAYER_ARN \
        --region $REGION

    echo "✅ Function updated successfully"
else
    echo "Function doesn't exist, creating new function..."

    # Create IAM role if needed
    ROLE_NAME="lambda-pdf-generator-role"

    if ! aws iam get-role --role-name $ROLE_NAME 2>/dev/null; then
        echo "Creating IAM role..."

        cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

        aws iam create-role \
            --role-name $ROLE_NAME \
            --assume-role-policy-document file://trust-policy.json

        aws iam attach-role-policy \
            --role-name $ROLE_NAME \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

        # Add S3 permissions
        cat > s3-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::*/*"
    }
  ]
}
EOF

        aws iam put-role-policy \
            --role-name $ROLE_NAME \
            --policy-name S3Access \
            --policy-document file://s3-policy.json

        rm -f trust-policy.json s3-policy.json

        echo "Waiting for role to be available..."
        sleep 10
    fi

    ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://function.zip \
        --memory-size $MEMORY \
        --timeout $TIMEOUT \
        --layers $LAYER_ARN \
        --region $REGION

    echo "✅ Function created successfully"
fi

# Step 4: Get function details
echo ""
echo "📋 Function Details:"
FUNCTION_ARN=$(aws lambda get-function \
    --function-name $FUNCTION_NAME \
    --region $REGION \
    --query 'Configuration.FunctionArn' \
    --output text)

echo "Function ARN: $FUNCTION_ARN"
echo "Function Name: $FUNCTION_NAME"
echo "Runtime: $RUNTIME"
echo "Memory: ${MEMORY}MB"
echo "Timeout: ${TIMEOUT}s"
echo "Layer: $LAYER_ARN"

# Cleanup
echo ""
echo "🧹 Cleaning up temporary files..."
rm -f function.zip

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Create API Gateway:"
echo "   - Go to API Gateway Console"
echo "   - Create REST API"
echo "   - Create POST method pointing to: $FUNCTION_NAME"
echo "   - Enable CORS"
echo "   - Deploy to stage"
echo ""
echo "2. Test the function:"
echo "   aws lambda invoke \\"
echo "     --function-name $FUNCTION_NAME \\"
echo "     --payload file://example_request.json \\"
echo "     --region $REGION \\"
echo "     response.json"
echo ""
echo "   cat response.json | jq"
echo ""

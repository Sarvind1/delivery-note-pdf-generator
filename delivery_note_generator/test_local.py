#!/usr/bin/env python3
"""
Local testing script for Lambda function
Tests the PDF generator without deploying to AWS
"""

import json
import base64
from lambda_function import lambda_handler


def test_local():
    """Test the Lambda function locally"""

    print("Loading test data from example_request.json...")

    # Load example request
    with open('example_request.json', 'r', encoding='utf-8') as f:
        event = json.load(f)

    print("Calling Lambda handler...")

    # Call Lambda handler
    response = lambda_handler(event, None)

    print(f"\nStatus Code: {response['statusCode']}")

    if response['statusCode'] == 200:
        body = json.loads(response['body'])
        print(f"Message: {body['message']}")

        # Save PDF to file
        if 'pdf_base64' in body:
            pdf_bytes = base64.b64decode(body['pdf_base64'])
            output_file = 'test_output.pdf'

            with open(output_file, 'wb') as f:
                f.write(pdf_bytes)

            print(f"\nPDF saved to: {output_file}")
            print(f"PDF size: {len(pdf_bytes)} bytes")

        # Print S3 info if available
        if 's3_key' in body:
            print(f"\nS3 Bucket: {body.get('s3_bucket')}")
            print(f"S3 Key: {body.get('s3_key')}")
            print(f"Presigned URL: {body.get('presigned_url')}")
    else:
        body = json.loads(response['body'])
        print(f"Error: {body.get('error')}")
        print(f"Message: {body.get('message')}")


if __name__ == '__main__':
    try:
        test_local()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

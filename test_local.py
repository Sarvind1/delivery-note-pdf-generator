#!/usr/bin/env python3
"""
Local testing script for the Lambda function
Tests the PDF generation without needing to deploy to AWS
"""

import json
import base64
from lambda_function import lambda_handler

def test_pdf_generation():
    """Test PDF generation with example data"""

    print("🧪 Testing PDF Generator Lambda Function Locally...\n")

    # Load example request
    with open('example_request.json', 'r') as f:
        event = json.load(f)

    # Remove S3 upload for local testing
    event['save_to_s3'] = False

    print("📄 Input Data:")
    print(f"  Delivery No: {event['non_body_data']['delivery_no']}")
    print(f"  PO No: {event['non_body_data']['po_no']}")
    print(f"  Items: {len(event['body_data'])}")
    print()

    # Call Lambda handler
    print("⚙️  Generating PDF...")
    try:
        response = lambda_handler(event, None)

        if response['statusCode'] == 200:
            print("✅ PDF Generated Successfully!\n")

            body = json.loads(response['body'])

            # Decode and save PDF
            if 'pdf_base64' in body:
                pdf_bytes = base64.b64decode(body['pdf_base64'])
                output_file = 'test_output.pdf'

                with open(output_file, 'wb') as f:
                    f.write(pdf_bytes)

                print(f"📥 PDF saved to: {output_file}")
                print(f"📊 PDF size: {len(pdf_bytes):,} bytes")
                print()

            print("✅ Test Passed!")
            return True

        else:
            print(f"❌ Test Failed!")
            print(f"Status Code: {response['statusCode']}")
            print(f"Response: {response['body']}")
            return False

    except Exception as e:
        print(f"❌ Test Failed with Exception!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_with_s3():
    """Test with S3 upload (requires AWS credentials)"""

    print("\n🧪 Testing with S3 Upload...\n")

    with open('example_request.json', 'r') as f:
        event = json.load(f)

    # You need to set your S3 bucket
    event['save_to_s3'] = True
    event['s3_bucket'] = input("Enter S3 bucket name (or press Enter to skip): ").strip()

    if not event['s3_bucket']:
        print("⏭️  Skipping S3 test")
        return

    try:
        response = lambda_handler(event, None)

        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print("✅ PDF uploaded to S3!")
            print(f"📍 S3 Location: s3://{body['s3_bucket']}/{body['s3_key']}")
            if 'presigned_url' in body:
                print(f"🔗 Download URL: {body['presigned_url']}")
            return True
        else:
            print(f"❌ S3 Test Failed!")
            print(f"Response: {response['body']}")
            return False

    except Exception as e:
        print(f"❌ S3 Test Failed!")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Test basic PDF generation
    success = test_pdf_generation()

    # Optionally test S3 upload
    if success:
        print("\n" + "="*50)
        test_s3 = input("\nTest S3 upload? (y/N): ").strip().lower()
        if test_s3 == 'y':
            test_with_s3()

    print("\n" + "="*50)
    print("Testing complete!")

#!/usr/bin/env python3
"""
Script to call the PDF Generator Lambda API
Can be used to test the deployed API Gateway endpoint
"""

import requests
import json
import base64
import sys
from datetime import datetime

# Configuration
API_ENDPOINT = "https://your-api-id.execute-api.region.amazonaws.com/prod/generate-pdf"

def call_pdf_api(api_url, data, save_pdf=True, output_filename=None):
    """
    Call the PDF generator API

    Args:
        api_url: API Gateway endpoint URL
        data: Dictionary with non_body_data and body_data
        save_pdf: Whether to save the PDF locally
        output_filename: Name for the saved PDF file

    Returns:
        dict: API response
    """

    print(f"🚀 Calling PDF Generator API...")
    print(f"📍 Endpoint: {api_url}")
    print(f"📄 Delivery No: {data['non_body_data']['delivery_no']}")
    print(f"📦 Items: {len(data['body_data'])}\n")

    try:
        # Make API request
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(api_url, headers=headers, json=data)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ PDF Generated Successfully!\n")

            # Save PDF if requested
            if save_pdf and 'pdf_base64' in result:
                pdf_bytes = base64.b64decode(result['pdf_base64'])

                if not output_filename:
                    delivery_no = data['non_body_data'].get('delivery_no', 'output')
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_filename = f"{delivery_no}_{timestamp}.pdf"

                with open(output_filename, 'wb') as f:
                    f.write(pdf_bytes)

                print(f"💾 PDF saved to: {output_filename}")
                print(f"📊 PDF size: {len(pdf_bytes):,} bytes\n")

            # Show S3 info if available
            if 's3_bucket' in result:
                print(f"☁️  S3 Upload:")
                print(f"   Bucket: {result['s3_bucket']}")
                print(f"   Key: {result['s3_key']}")

                if 'presigned_url' in result:
                    print(f"   Download URL: {result['presigned_url']}\n")

            return result

        else:
            print(f"❌ API Error!")
            print(f"Response: {response.text}\n")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request Failed!")
        print(f"Error: {str(e)}\n")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error!")
        print(f"Error: {str(e)}\n")
        return None


def load_example_data():
    """Load example data from example_request.json"""
    try:
        with open('example_request.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ example_request.json not found")
        sys.exit(1)


def create_custom_request():
    """Create a custom request interactively"""
    print("📝 Creating custom request...\n")

    data = {
        "non_body_data": {
            "delivery_no": input("Delivery No: ").strip() or "TEST-001",
            "po_no": input("PO No: ").strip() or "PO-001",
            "buyer": input("Buyer: ").strip() or "Test Buyer",
            "delivery_date": input("Delivery Date (YYYY-MM-DD): ").strip() or datetime.now().strftime('%Y-%m-%d'),
            "supplier": input("Supplier: ").strip() or "Test Supplier Co.",
            "ship_from": input("Ship From: ").strip() or "Test Address",
            "contact_person": input("Contact Person: ").strip() or "Test Contact",
            "contact_phone": input("Contact Phone: ").strip() or "000-0000",
            "delivery_address": input("Delivery Address: ").strip() or "Test Delivery Address",
            "page_current": 1,
            "page_total": 1
        },
        "body_data": [
            {
                "item_no": "0001",
                "sku": "TEST-SKU-001",
                "qty": 100,
                "qty_per_carton": 10,
                "cartons": 10,
                "tail_carton_qty": None,
                "qc_result": "Pass",
                "length": 50,
                "width": 40,
                "height": 30,
                "ctn_weight": 10,
                "total_cbm": 1.5,
                "total_weight": 100
            }
        ],
        "save_to_s3": False
    }

    return data


def main():
    """Main function"""
    print("=" * 60)
    print("  PDF Generator Lambda API Client")
    print("=" * 60)
    print()

    # Get API endpoint
    api_url = input(f"API Endpoint URL (or press Enter for default):\n> ").strip()
    if not api_url:
        api_url = API_ENDPOINT
        print(f"Using: {api_url}\n")

    # Choose data source
    print("Data source:")
    print("1. Use example_request.json")
    print("2. Create custom request")
    choice = input("Choice (1/2): ").strip()

    if choice == "2":
        data = create_custom_request()
    else:
        data = load_example_data()

    # Ask about S3 upload
    s3_upload = input("\nSave to S3? (y/N): ").strip().lower()
    if s3_upload == 'y':
        data['save_to_s3'] = True
        data['s3_bucket'] = input("S3 Bucket: ").strip()
        s3_key = input("S3 Key (optional, press Enter to auto-generate): ").strip()
        if s3_key:
            data['s3_key'] = s3_key
    else:
        data['save_to_s3'] = False

    # Ask about output filename
    save_local = input("\nSave PDF locally? (Y/n): ").strip().lower()
    output_filename = None
    if save_local != 'n':
        output_filename = input("Output filename (press Enter for auto-generated): ").strip()
        if not output_filename:
            output_filename = None

    print("\n" + "=" * 60)

    # Call API
    result = call_pdf_api(
        api_url,
        data,
        save_pdf=(save_local != 'n'),
        output_filename=output_filename
    )

    if result:
        print("✅ Done!")
    else:
        print("❌ Failed!")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)

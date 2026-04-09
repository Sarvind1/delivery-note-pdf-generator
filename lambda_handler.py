#!/usr/bin/env python3
"""
Lambda handler for WeasyPrint PDF generation
Accepts JSON input directly - no CSV files needed
"""

import json
import base64
from pdf_generator_weasyprint import DeliveryNotePDFGeneratorWeasy


def lambda_handler(event, context):
    """
    Lambda function handler for PDF generation

    Expected event structure:
    {
        "non_body_data": {
            "QI type": "DN-2024-001",
            "po_no": "PO123456",
            "buyer": "John Doe",
            ...
        },
        "body_data": [
            {
                "item_no": 1,
                "sku": "SKU-001",
                "qty": 100,
                ...
            }
        ]
    }

    Returns:
    {
        "statusCode": 200,
        "body": {
            "message": "PDF generated successfully",
            "pdf_base64": "JVBERi0xLjQK...",
            "size_bytes": 45678
        }
    }
    """

    try:
        # Handle Lambda Function URL format (HTTP request)
        if 'body' in event and isinstance(event.get('body'), str):
            # Parse the JSON body from Function URL
            event = json.loads(event['body'])

        # Validate input
        if 'non_body_data' not in event or 'body_data' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid input. Must provide non_body_data and body_data'
                })
            }

        non_body_data = event['non_body_data']
        body_data = event['body_data']

        # Handle non_body_data as array or single object
        if isinstance(non_body_data, list):
            non_body_data = non_body_data[0] if non_body_data else {}

        # Validate body_data is a list
        if not isinstance(body_data, list):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'body_data must be an array of items'
                })
            }

        # Generate PDF in Lambda's /tmp directory
        output_path = '/tmp/delivery_note.pdf'
        generator = DeliveryNotePDFGeneratorWeasy(
            non_body_data=non_body_data,
            body_data=body_data,
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

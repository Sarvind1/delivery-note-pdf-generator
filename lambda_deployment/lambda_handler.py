#!/usr/bin/env python3
"""
Lambda handler for WeasyPrint PDF generation
Optimized for AWS Lambda with minimal dependencies
"""

import json
import base64
import pandas as pd
from io import BytesIO, StringIO
from pdf_generator_weasyprint import DeliveryNotePDFGeneratorWeasy


def lambda_handler(event, context):
    """
    Lambda function handler for PDF generation

    Expected event structure:
    {
        "non_body_csv": "base64_encoded_csv_content",
        "body_csv": "base64_encoded_csv_content"
    }

    Or:
    {
        "non_body_data": [...],  // JSON array
        "body_data": [...]       // JSON array
    }
    """

    try:
        # Parse input data
        if 'non_body_csv' in event and 'body_csv' in event:
            # Decode base64 CSV data
            non_body_csv = base64.b64decode(event['non_body_csv']).decode('utf-8')
            body_csv = base64.b64decode(event['body_csv']).decode('utf-8')

            # Save to temporary files
            non_body_path = '/tmp/non_body.csv'
            body_path = '/tmp/body.csv'

            with open(non_body_path, 'w') as f:
                f.write(non_body_csv)
            with open(body_path, 'w') as f:
                f.write(body_csv)

        elif 'non_body_data' in event and 'body_data' in event:
            # Use JSON data directly
            non_body_path = '/tmp/non_body.csv'
            body_path = '/tmp/body.csv'

            pd.DataFrame(event['non_body_data']).to_csv(non_body_path, index=False)
            pd.DataFrame(event['body_data']).to_csv(body_path, index=False)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid input format. Provide either CSV (base64) or JSON data.'
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

        # Read and encode PDF
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

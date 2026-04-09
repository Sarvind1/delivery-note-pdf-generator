import json
import boto3
import base64
from datetime import datetime
from pdf_generator_lambda import DeliveryNotePDFGenerator

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda handler for PDF generation API

    Expected event structure:
    {
        "non_body_data": {...},  # Single record as dict
        "body_data": [{...}, {...}],  # List of records
        "save_to_s3": true/false,  # Optional, default false
        "s3_bucket": "bucket-name",  # Required if save_to_s3 is true
        "s3_key": "path/to/file.pdf"  # Optional, auto-generated if not provided
    }
    """

    try:
        # Parse input
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event

        non_body_data = body.get('non_body_data')
        body_data = body.get('body_data')
        save_to_s3 = body.get('save_to_s3', False)
        s3_bucket = body.get('s3_bucket')
        s3_key = body.get('s3_key')

        # Validate input
        if not non_body_data or not body_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing non_body_data or body_data'})
            }

        # Generate PDF
        generator = DeliveryNotePDFGenerator(non_body_data, body_data)
        pdf_bytes = generator.generate_pdf()

        response_data = {}

        # Save to S3 if requested
        if save_to_s3:
            if not s3_bucket:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 's3_bucket is required when save_to_s3 is true'})
                }

            # Generate S3 key if not provided
            if not s3_key:
                delivery_no = non_body_data.get('delivery_no', 'unknown')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                s3_key = f"delivery-notes/{delivery_no}_{timestamp}.pdf"

            # Upload to S3
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=s3_key,
                Body=pdf_bytes,
                ContentType='application/pdf'
            )

            # Generate presigned URL (valid for 1 hour)
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': s3_bucket, 'Key': s3_key},
                ExpiresIn=3600
            )

            response_data['s3_bucket'] = s3_bucket
            response_data['s3_key'] = s3_key
            response_data['presigned_url'] = presigned_url

        # Return base64 encoded PDF
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        response_data['pdf_base64'] = pdf_base64
        response_data['message'] = 'PDF generated successfully'

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to generate PDF'
            })
        }

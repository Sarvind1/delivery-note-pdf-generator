#!/usr/bin/env python3
"""
Simple local test without boto3
"""

import json
from pdf_generator_weasyprint_lambda import DeliveryNotePDFGeneratorWeasy

# Load test data
with open('example_request.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Testing PDF generation...")
print(f"Delivery No: {data['non_body_data']['delivery_no']}")
print(f"Items: {len(data['body_data'])}")

# Generate PDF
generator = DeliveryNotePDFGeneratorWeasy(
    data['non_body_data'],
    data['body_data']
)

pdf_bytes = generator.generate_pdf()

# Save to file
with open('test_output.pdf', 'wb') as f:
    f.write(pdf_bytes)

print(f"\n✅ PDF generated successfully!")
print(f"Output: test_output.pdf ({len(pdf_bytes)} bytes)")

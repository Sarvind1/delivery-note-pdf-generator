# Delivery Note PDF Generator

A Python-based PDF generation service for creating delivery notes (shipping documents) from CSV or JSON data. Includes AWS Lambda deployment with support for S3 storage and two rendering engines (WeasyPrint and Pillow).

## Key Features

- **Multiple Input Formats**: Accept data as CSV files or JSON objects
- **Rendering Options**: WeasyPrint (high-quality HTML-to-PDF) or Pillow-based rendering
- **AWS Lambda Ready**: Pre-configured Lambda handlers and layer packaging scripts
- **S3 Integration**: Optional automatic upload of generated PDFs to AWS S3
- **Customizable Output**: Template-based delivery note generation with header/body structure
- **Optimized Layers**: Pre-built Lambda layer with all dependencies (NumPy, Pandas, WeasyPrint, etc.)

## Tech Stack

- **Core**: Python 3.11
- **PDF Libraries**: WeasyPrint, Pillow, ReportLab
- **Data Processing**: Pandas, NumPy
- **Cloud**: AWS Lambda, AWS S3, Boto3
- **Build Tools**: Shell scripts for layer compilation

## Setup

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/delivery-note-pdf-generator.git
cd delivery-note-pdf-generator

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r delivery_note_generator/requirements.txt
```

### AWS Lambda Deployment

```bash
# Build Lambda layer with all dependencies
cd delivery_note_generator
./build_layer.sh

# Deploy to AWS Lambda
./deploy.sh
```

See `DEPLOYMENT_STEPS.md` in the delivery_note_generator directory for detailed Lambda setup instructions.

## Usage

### Local Example

```python
from delivery_note_generator.pdf_generator_weasyprint import DeliveryNotePDFGeneratorWeasy

# Define delivery note data
non_body_data = {
    'delivery_no': 'DN-2026-001',
    'date': '2026-04-10',
    'customer': 'ACME Corp',
    'address': '123 Main St'
}

body_data = [
    {'item': 'Product A', 'qty': 10, 'price': 25.00},
    {'item': 'Product B', 'qty': 5, 'price': 50.00}
]

# Generate PDF
generator = DeliveryNotePDFGeneratorWeasy(non_body_data, body_data)
pdf_bytes = generator.generate_pdf()

# Save locally
with open('delivery_note.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

### AWS Lambda Example

```python
# Invoke via API Gateway or AWS SDK with event:
{
    "non_body_data": {
        "delivery_no": "DN-2026-001",
        "customer": "ACME Corp"
    },
    "body_data": [
        {"item": "Product A", "qty": 10}
    ],
    "save_to_s3": true,
    "s3_bucket": "my-bucket",
    "s3_key": "delivery-notes/DN-2026-001.pdf"
}
```

## Project Structure

```
delivery_note_generator/     # Main PDF generation module
  - lambda_function.py       # AWS Lambda handler
  - pdf_generator_weasyprint.py  # WeasyPrint implementation
  - requirements.txt         # Python dependencies
  - build_layer.sh          # Lambda layer build script
lambda_deployment/          # Alternative Lambda setup
lambda-layer/              # Pre-built dependency layer (git-ignored)
```

## License

[Specify your license here]
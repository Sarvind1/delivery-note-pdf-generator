#!/usr/bin/env python3
"""
PDF Generator using WeasyPrint with HTML/CSS for AWS Lambda
Accepts JSON input instead of CSV files
"""

import pandas as pd
from weasyprint import HTML
import base64
from io import BytesIO
from barcode import Code128
from barcode.writer import ImageWriter


class DeliveryNotePDFGeneratorWeasy:
    def __init__(self, non_body_data, body_data):
        """
        Initialize the PDF generator with JSON data

        Args:
            non_body_data: dict - Single record with header information
            body_data: list of dicts - List of line items
        """
        # Convert JSON to pandas DataFrames
        self.non_body_data = pd.DataFrame([non_body_data])
        self.body_data = pd.DataFrame(body_data)

    def generate_barcode_base64(self, code_text):
        """Generate barcode and return as base64 string"""
        try:
            rv = BytesIO()
            code = Code128(str(code_text), writer=ImageWriter())
            code.write(rv, options={
                'write_text': True,
                'module_height': 35,
                'module_width': 1,
                'quiet_zone': 0,
                'text_distance': 10,
                'font_size': 15
            })
            rv.seek(0)
            barcode_base64 = base64.b64encode(rv.read()).decode('utf-8')
            return f"data:image/png;base64,{barcode_base64}"
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None

    def generate_html(self):
        """Generate HTML content for the PDF"""
        header_info = self.non_body_data.iloc[0]

        # Extract header data
        delivery_no = str(header_info.get('delivery_no', ''))
        po_no = str(header_info.get('po_no', ''))
        buyer = str(header_info.get('buyer', ''))
        delivery_date = str(header_info.get('delivery_date', ''))
        inbship_no = str(header_info.get('inbship_no', ''))
        batch_no = str(header_info.get('batch_no', ''))
        supplier = str(header_info.get('supplier', ''))
        ship_from = str(header_info.get('ship_from', ''))
        contact_person = str(header_info.get('contact_person', ''))
        contact_phone = str(header_info.get('contact_phone', ''))
        delivery_address = str(header_info.get('delivery_address', ''))
        page_current = header_info.get('page_current', 1)
        page_total = header_info.get('page_total', 1)

        # Generate barcode using INBSHIP No. with P prefix
        barcode_text = f"P{inbship_no}" if inbship_no else ''
        barcode_img = self.generate_barcode_base64(barcode_text) if barcode_text else None

        # Build items table rows
        items_rows = ""
        for idx, row in self.body_data.iterrows():
            def format_val(val):
                if pd.isna(val):
                    return ''
                if isinstance(val, float) and val.is_integer():
                    return str(int(val))
                return str(val)

            length = str(int(row['length'])) if pd.notna(row.get('length')) else ''
            width = str(int(row['width'])) if pd.notna(row.get('width')) else ''
            height = str(int(row['height'])) if pd.notna(row.get('height')) else ''

            items_rows += f"""
            <tr>
                <td>{str(row.get('item_no', idx + 1)).zfill(4)}</td>
                <td class="text-left">{row.get('sku', '')}</td>
                <td>{format_val(row.get('qty'))}</td>
                <td>{format_val(row.get('qty_per_carton'))}</td>
                <td>{format_val(row.get('cartons'))}</td>
                <td>{row.get('qc_result', '')}</td>
                <td></td>
                <td>{length}</td>
                <td>{width}</td>
                <td>{height}</td>
                <td>{format_val(row.get('ctn_weight'))}</td>
                <td>{format_val(row.get('total_cbm'))}</td>
                <td>{format_val(row.get('total_weight'))}</td>
                <td></td>
            </tr>
            """

        # Calculate totals
        qty_total = int(self.body_data['qty'].sum()) if 'qty' in self.body_data else 0
        cartons_total = int(self.body_data['cartons'].sum()) if 'cartons' in self.body_data else 0
        cbm_total = self.body_data['total_cbm'].sum() if 'total_cbm' in self.body_data else 0
        weight_total = int(self.body_data['total_weight'].sum()) if 'total_weight' in self.body_data else 0

        # Barcode image tag
        barcode_html = f'<img src="{barcode_img}" class="barcode" />' if barcode_img else ''

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: 1100px 580px;
                    margin: 10px;
                }}

                body {{
                    font-family: 'SimSun', 'Arial', sans-serif;
                    font-size: 10pt;
                    margin: 0;
                    padding: 15px;
                    border: 2px solid black;
                    box-sizing: border-box;
                    height: 560px;
                }}

                .header {{
                    text-align: center;
                    margin-bottom: 8px;
                }}

                .header h1 {{
                    font-size: 24pt;
                    margin: 0;
                    display: inline-block;
                    width: 82%;
                }}

                .header .page-num {{
                    font-size: 9pt;
                    float: right;
                    margin-right: 30px;
                }}

                .header-section {{
                    position: relative;
                    margin-bottom: 10px;
                }}

                .barcode {{
                    position: absolute;
                    right: 0;
                    top: 0;
                    width: 280px;
                    height: 100px;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 10px;
                }}

                table.header-table {{
                    width: 71%;
                }}

                th, td {{
                    border: 0.5px solid black;
                    padding: 4px 6px;
                    text-align: center;
                    font-size: 10pt;
                }}

                .text-left {{
                    text-align: left !important;
                }}

                .header-label {{
                    background-color: #e6e6e6;
                    font-weight: normal;
                }}

                .items-table th {{
                    background-color: #e6e6e6;
                    font-size: 8pt;
                    padding: 3px;
                }}

                .items-table td {{
                    font-size: 10pt;
                }}

                .total-row {{
                    background-color: #f2f2f2;
                    font-weight: bold;
                }}

                .footer {{
                    margin-top: 30px;
                    font-size: 10pt;
                    line-height: 1.4;
                }}

                .footer-title {{
                    margin-top: 8px;
                    font-weight: bold;
                }}

                .signature {{
                    text-align: right;
                    margin-top: 60px;
                    font-size: 11pt;
                }}

                .fix-font {{
                    font-family: 'PingFang SC', 'Heiti SC', 'STSong', sans-serif;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>送货单</h1>
                <span class="page-num">页次 page {page_current} / {page_total}</span>
            </div>

            <div class="header-section">
                <table class="header-table">
                    <tr>
                        <td class="header-label">送货单号 Delivery No.</td>
                        <td>{delivery_no}</td>
                        <td class="header-label">订单号 PO No.</td>
                        <td>{po_no}</td>
                    </tr>
                    <tr>
                        <td class="header-label">采购 Purchasing Buyer</td>
                        <td>{buyer}</td>
                        <td class="header-label">送货日期 Delivery Date</td>
                        <td>{delivery_date}</td>
                    </tr>
                    <tr>
                        <td class="header-label">INBSHIP No.</td>
                        <td>{inbship_no}</td>
                        <td class="header-label">Batch No.</td>
                        <td>{batch_no}</td>
                    </tr>
                    <tr>
                        <td class="header-label">供应商 Supplier</td>
                        <td colspan="3">{supplier}</td>
                    </tr>
                    <tr>
                        <td class="header-label">地址 Ship From</td>
                        <td colspan="3">{ship_from}</td>
                    </tr>
                </table>
                {barcode_html}
            </div>

            <table class="items-table">
                <thead>
                    <tr>
                        <th rowspan="2">序号<br>Item</th>
                        <th rowspan="2">产品编码<br>SKU</th>
                        <th rowspan="2">进货数量<br>Qty</th>
                        <th rowspan="2">装箱数<br>Qty/Ctn</th>
                        <th rowspan="2">进货箱数<br>Cartons</th>
                        <th rowspan="2">验收结果<br>QC Result</th>
                        <th rowspan="2">测试结果<br>Test Result</th>
                        <th colspan="3">箱规<br>Ctn Dimension (CM)</th>
                        <th rowspan="2">重量<br>Ctn Weight (KG)</th>
                        <th rowspan="2">总体积<br>Total CBM</th>
                        <th rowspan="2">总重量<br>Total Weight</th>
                        <th rowspan="2">备注<br>Remark</th>
                    </tr>
                    <tr>
                        <th>L</th>
                        <th>W</th>
                        <th>H</th>
                    </tr>
                </thead>
                <tbody>
                    {items_rows}
                    <tr class="total-row">
                        <td colspan="2">Total</td>
                        <td>{qty_total}</td>
                        <td></td>
                        <td>{cartons_total}</td>
                        <td colspan="6"></td>
                        <td>{cbm_total:.2f}</td>
                        <td>{weight_total}</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>

            <div class="footer">
                <div>收货单位联系人(CONTACT PERSON)：{contact_person}</div>
                <div>收货单位联系人电话(CONTACT PHONE)：{contact_phone}</div>
                <div class="footer-title">供应商送货注意事项</div>
                <div>1.送货到<span class="fix-font">门</span>，负责卸货到地（托板）上，货物按品种分类好，不混装</div>
                <div>2.收货时间: 8:30 – 17:00（周一至周五）</div>
                <div>3.送货地址：{delivery_address}</div>
            </div>

            <div class="signature">
                收货签名 Receipt Signature: _______________________
            </div>
        </body>
        </html>
        """

        return html_content

    def generate_pdf(self):
        """Generate PDF from HTML and return as bytes"""
        html_content = self.generate_html()

        # Generate PDF to bytes
        pdf_bytes = HTML(string=html_content).write_pdf()

        return pdf_bytes

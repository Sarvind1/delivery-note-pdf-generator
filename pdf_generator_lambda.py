import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from barcode import Code128
from barcode.writer import ImageWriter
import io
import numpy as np

class DeliveryNotePDFGenerator:
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
        self.elements = []

        # Register Chinese font support
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

        # Setup styles
        self.styles = getSampleStyleSheet()
        self.normal_style = ParagraphStyle(
            'NormalStyle',
            fontName='STSong-Light',
            fontSize=10,
            leading=12,
            wordSpacing=1
        )

        self.title_style = ParagraphStyle(
            'TitleStyle',
            fontName='STSong-Light',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=8
        )

        self.small_style = ParagraphStyle(
            'SmallStyle',
            fontName='STSong-Light',
            fontSize=9,
            leading=11
        )

    def generate_barcode(self, code_text):
        """Generate barcode image from text"""
        try:
            rv = io.BytesIO()
            code = Code128(str(code_text), writer=ImageWriter())
            code.write(rv, options={
                'write_text': True,  # Show text below barcode
                'module_height': 35,
                'module_width': 1,  # Stretched width
                'quiet_zone': 0,
                'text_distance': 10,
                #distance between barcode and text below
                'font_size': 15
            })
            rv.seek(0)
            # Return a stretched barcode
            return Image(rv, width=200, height=55)
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None

    def create_complete_document(self):
        """Create the complete document enclosed in a table"""
        header_info = self.non_body_data.iloc[0]

        # Title with page info
        title_text = "送货单"
        page_text = f"页次 page {header_info.get('page_current', 1)} / {header_info.get('page_total', 1)}"

        title_row = Table([[title_text, page_text]], colWidths=[870, 100])
        title_row.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),
            ('FONTSIZE', (0, 0), (0, 0), 25),
            ('FONTSIZE', (1, 0), (1, 0), 9),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        # Extract header data
        delivery_no = str(header_info.get('delivery_no', ''))
        po_no = str(header_info.get('po_no', ''))
        buyer = str(header_info.get('buyer', ''))
        delivery_date = str(header_info.get('delivery_date', ''))
        supplier = str(header_info.get('supplier', ''))
        ship_from = str(header_info.get('ship_from', ''))

        # Generate barcode (keep it in top right)
        barcode_text = po_no.replace('P', '') if po_no.startswith('P') else po_no
        barcode_img = self.generate_barcode(barcode_text) if po_no else None

        # Create header table with barcode on the right
        header_data = [
            ['送货单号 Delivery No.', delivery_no, '订单号 PO No.', po_no],
            ['采购 Purchasing Buyer', buyer, '送货日期 Delivery Date', delivery_date],
            ['供应商 Supplier', supplier, '', ''],
            ['地址 Ship From', ship_from, '', '']
        ]

        # Header table
        header_table = Table(header_data, colWidths=[130, 230, 120, 200])
        header_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.9, 0.9, 0.9)),
            ('BACKGROUND', (2, 0), (2, 1), colors.Color(0.9, 0.9, 0.9)),
            ('SPAN', (1, 2), (3, 2)),  # Supplier spans
            ('SPAN', (1, 3), (3, 3)),  # Ship from spans
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        # Combine header table with barcode on right (vertically centered)
        if barcode_img:
            header_with_barcode = Table([[header_table, barcode_img]],
                                      colWidths=[700, 230])
            header_with_barcode.setStyle(TableStyle([
                # ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (0, 0), 'TOP'),
                ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),  # Vertically center barcode
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ]))
        else:
            header_with_barcode = header_table

        # Items table with proper formatting
        headers_cn = ['序号', '产品编码', '进货数量', '装箱数', '进货箱数', '尾箱箱率',
                      '验收结果', '测试需求', '测试结果', '箱规', '', '', '重量', '总体积', '总重量', '备注']
        headers_en = ['Item', 'SKU', 'Qty', 'Qty/Ctn', 'Cartons', 'Qty/Ctn',
                      'QC\nResult', 'Test\nNeeded', 'Test\nResult',
                      'Ctn Dimension (CM)', '', '', 'Ctn Weight\n(KG)',
                      'Total CBM', 'Total\nWeight', 'Remark']

        items_data = [headers_cn, headers_en]

        # Process items
        for idx, row in self.body_data.iterrows():
            def format_val(val):
                if pd.isna(val):
                    return ''
                if isinstance(val, (float, np.floating)) and val.is_integer():
                    return str(int(val))
                return str(val)

            # Split dimensions
            length = str(int(row['length'])) if pd.notna(row.get('length')) else ''
            width = str(int(row['width'])) if pd.notna(row.get('width')) else ''
            height = str(int(row['height'])) if pd.notna(row.get('height')) else ''

            item_row = [
                str(row.get('item_no', idx + 1)).zfill(4),
                str(row.get('sku', '')),
                format_val(row.get('qty')),
                format_val(row.get('qty_per_carton')),
                format_val(row.get('cartons')),
                format_val(row.get('tail_carton_qty')),  # Tail carton qty
                str(row.get('qc_result', '')),
                '',  # Test needed
                '',  # Test result
                length, width, height,  # Dimensions split
                format_val(row.get('ctn_weight')),
                format_val(row.get('total_cbm')),
                format_val(row.get('total_weight')),
                ''  # Remark
            ]
            items_data.append(item_row)

        # Calculate totals
        qty_total = self.body_data['qty'].sum() if 'qty' in self.body_data else 0
        cartons_total = self.body_data['cartons'].sum() if 'cartons' in self.body_data else 0

        # Add tail cartons to total
        if 'tail_carton_qty' in self.body_data:
            has_tail = self.body_data['tail_carton_qty'].notna().any()
            if has_tail:
                cartons_total += 1

        cbm_total = self.body_data['total_cbm'].sum() if 'total_cbm' in self.body_data else 0
        weight_total = self.body_data['total_weight'].sum() if 'total_weight' in self.body_data else 0

        total_row = ['Total', '', str(int(qty_total)), '', str(int(cartons_total)),
                    '', '', '', '', '', '', '', '',
                    f"{cbm_total:.2f}", str(int(weight_total)), '']
        items_data.append(total_row)

        # Column widths optimized
        col_widths = [40, 120, 50, 50, 50, 60, 65, 65, 65, 35, 35, 35, 60, 60, 60, 60]
        items_table = Table(items_data, colWidths=col_widths, repeatRows=2)

        items_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, 1), colors.Color(0.9, 0.9, 0.9)),

            # Merge headers for Ctn Dimension
            ('SPAN', (9, 0), (11, 0)),
            ('SPAN', (9, 1), (11, 1)),

            ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
            ('ALIGN', (0, 2), (0, -1), 'CENTER'),
            ('ALIGN', (1, 2), (1, -1), 'LEFT'),
            ('ALIGN', (2, 2), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 2), (-1, -1), 'MIDDLE'),

            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
            ('SPAN', (0, -1), (1, -1)),

            # Increased padding for better readability
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        # Footer section
        contact_person = str(header_info.get('contact_person', ''))
        contact_phone = str(header_info.get('contact_phone', ''))
        delivery_address = str(header_info.get('delivery_address', ''))

        footer_data = [
            [f'收货单位联系人(CONTACT PERSON)：{contact_person}'],
            [f'收货单位联系人电话(CONTACT PHONE)：{contact_phone}'],
            ['供应商送货注意事项'],
            ['1.送货到门，负责卸货到地（托板）上，货物按品种分类好，不混装'],
            ['2.收货时间: 8:30 – 17:00（周一至周五）'],
            [f'3.送货地址：{delivery_address}']
        ]

        footer_table = Table(footer_data, colWidths=[950])
        footer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 2), (0, 2), 10),
        ]))

        # Receipt signature section
        signature_data = [
            ['收货签名 Receipt Signature:', '', '', '']
        ]

        signature_table = Table(signature_data, colWidths=[200, 250, 250, 250])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'STSong-Light'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 25),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))

        # Create main container with all content
        main_content = []
        main_content.append([title_row])
        main_content.append([Spacer(1, 0.3*cm)])
        main_content.append([header_with_barcode])
        main_content.append([Spacer(1, 0.4*cm)])
        main_content.append([items_table])
        main_content.append([Spacer(1, 0.4*cm)])
        main_content.append([footer_table])
        main_content.append([Spacer(1, 0.3*cm)])
        main_content.append([signature_table])

        # Main container table with outer border
        main_table = Table(main_content, colWidths=[950])
        main_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),  # Outer border
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (0, 0), 15),
            ('BOTTOMPADDING', (0, -1), (0, -1), 15),
        ]))

        self.elements.append(main_table)

    def generate_pdf(self):
        """Generate PDF and return as bytes"""
        # Use BytesIO instead of file
        pdf_buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=(1000, 460),
            rightMargin=0.3*cm,
            leftMargin=0.3*cm,
            topMargin=0.5*cm,
            bottomMargin=0.5*cm
        )

        # Build document
        self.create_complete_document()
        doc.build(self.elements)

        # Get PDF bytes
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()

        print(f"PDF generated successfully ({len(pdf_bytes)} bytes)")
        return pdf_bytes

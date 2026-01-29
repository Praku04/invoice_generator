"""PDF generation service for invoices and receipts."""

import os
from typing import Optional
from decimal import Decimal
from datetime import datetime
import weasyprint
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.models.invoice import Invoice
from app.models.payment_receipt import PaymentReceipt
from app.models.company_profile import CompanyProfile
from app.models.file_asset import FileAsset
from app.config import settings


class PDFService:
    """Service class for PDF generation."""
    
    def __init__(self, db: Session = None):
        self.db = db
        self.template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "pdf")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def generate_invoice_pdf(self, invoice_id: int, user_id: int, template_id: int = None) -> Optional[str]:
        """Generate PDF for an invoice using specified or default template."""
        # Get invoice with items
        invoice = self.db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.user_id == user_id
        ).first()
        
        if not invoice:
            return None
        
        # Get template
        from app.services.template_service import TemplateService
        from app.models.template import TemplateCategory
        
        template_service = TemplateService(self.db)
        
        if template_id:
            template = template_service.get_template_by_id(template_id)
            if not template or template.category != TemplateCategory.INVOICE:
                template = template_service.get_user_default_template(user_id, TemplateCategory.INVOICE)
        else:
            template = template_service.get_user_default_template(user_id, TemplateCategory.INVOICE)
        
        if not template:
            template = template_service.get_default_template(TemplateCategory.INVOICE)
        
        if not template:
            return None
        
        # Update invoice template reference
        invoice.template_id = template.id
        self.db.commit()
        
        # Get company profile
        company_profile = self.db.query(CompanyProfile).filter(
            CompanyProfile.user_id == user_id
        ).first()
        
        # Get logo and stamp files
        logo_url = None
        stamp_url = None
        
        if company_profile:
            if company_profile.logo_file_id:
                logo_file = self.db.query(FileAsset).filter(
                    FileAsset.id == company_profile.logo_file_id
                ).first()
                if logo_file:
                    logo_url = logo_file.file_path
            
            if company_profile.stamp_file_id:
                stamp_file = self.db.query(FileAsset).filter(
                    FileAsset.id == company_profile.stamp_file_id
                ).first()
                if stamp_file:
                    stamp_url = stamp_file.file_path
        
        # Prepare template context
        context = {
            'invoice': invoice,
            'company': company_profile,
            'logo_url': logo_url,
            'stamp_url': stamp_url,
            'items': invoice.items,
            'generated_at': datetime.now(),
            'format_currency': self._format_currency,
            'format_date': self._format_date,
            'number_to_words': self._number_to_words
        }
        
        # Load template using Jinja2
        from jinja2 import Environment, FileSystemLoader
        import os
        
        template_dir = os.path.dirname(template.html_path)
        env = Environment(loader=FileSystemLoader(template_dir))
        jinja_template = env.get_template(template.html_file)
        
        # Render HTML content
        html_content = jinja_template.render(context)
        
        # Load CSS content
        css_content = ""
        if os.path.exists(template.css_path):
            with open(template.css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        
        # Generate PDF
        pdf_filename = f"invoice_{invoice.invoice_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(settings.upload_dir, "pdfs", pdf_filename)
        
        # Ensure PDF directory exists
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        try:
            # Generate PDF with WeasyPrint
            weasyprint.HTML(string=html_content, base_url=template_dir).write_pdf(
                pdf_path,
                stylesheets=[weasyprint.CSS(string=css_content)]
            )
            
            # Update invoice with PDF path
            invoice.pdf_generated = True
            invoice.pdf_file_path = pdf_path
            self.db.commit()
            
            return pdf_path
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            return None
    
    def _format_currency(self, amount: Decimal, symbol: str = "₹") -> str:
        """Format currency amount."""
        return f"{symbol} {amount:,.2f}"
    
    def _format_date(self, date_obj) -> str:
        """Format date for display."""
        if not date_obj:
            return ""
        return date_obj.strftime("%d/%m/%Y")
    
    def _number_to_words(self, amount: Decimal) -> str:
        """Convert number to words (simplified version)."""
        # This is a simplified implementation
        # In production, use a proper number-to-words library
        
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
        teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", 
                "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def convert_hundreds(num):
            result = ""
            if num >= 100:
                result += ones[num // 100] + " Hundred "
                num %= 100
            if num >= 20:
                result += tens[num // 10] + " "
                num %= 10
            elif num >= 10:
                result += teens[num - 10] + " "
                num = 0
            if num > 0:
                result += ones[num] + " "
            return result
        
        if amount == 0:
            return "Zero Rupees Only"
        
        # Split into rupees and paise
        rupees = int(amount)
        paise = int((amount - rupees) * 100)
        
        result = ""
        
        # Convert rupees
        if rupees >= 10000000:  # Crores
            crores = rupees // 10000000
            result += convert_hundreds(crores) + "Crore "
            rupees %= 10000000
        
        if rupees >= 100000:  # Lakhs
            lakhs = rupees // 100000
            result += convert_hundreds(lakhs) + "Lakh "
            rupees %= 100000
        
        if rupees >= 1000:  # Thousands
            thousands = rupees // 1000
            result += convert_hundreds(thousands) + "Thousand "
            rupees %= 1000
        
        if rupees > 0:
            result += convert_hundreds(rupees)
        
        result += "Rupees"
        
        if paise > 0:
            result += " and " + convert_hundreds(paise) + "Paise"
        
        result += " Only"
        
        return result.strip()
    
    def _get_pdf_css(self) -> str:
        """Get CSS styles for PDF generation."""
        return """
        @page {
            size: A4;
            margin: 1cm;
        }
        
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 12px;
            line-height: 1.4;
            color: #333;
        }
        
        .invoice-header {
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .company-info {
            float: left;
            width: 60%;
        }
        
        .invoice-info {
            float: right;
            width: 35%;
            text-align: right;
        }
        
        .logo {
            max-width: 150px;
            max-height: 80px;
            margin-bottom: 10px;
        }
        
        .invoice-title {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
        }
        
        .client-info {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        
        .items-table th,
        .items-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        .items-table th {
            background-color: #007bff;
            color: white;
            font-weight: bold;
        }
        
        .items-table .text-right {
            text-align: right;
        }
        
        .totals-section {
            float: right;
            width: 40%;
            margin-top: 20px;
        }
        
        .totals-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .totals-table td {
            padding: 5px 10px;
            border-bottom: 1px solid #eee;
        }
        
        .totals-table .total-row {
            font-weight: bold;
            border-top: 2px solid #007bff;
            background-color: #f8f9fa;
        }
        
        .tax-breakdown {
            margin-top: 20px;
            clear: both;
        }
        
        .tax-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }
        
        .tax-table th,
        .tax-table td {
            border: 1px solid #ddd;
            padding: 5px;
            text-align: center;
        }
        
        .tax-table th {
            background-color: #6c757d;
            color: white;
        }
        
        .footer-section {
            margin-top: 30px;
            clear: both;
        }
        
        .stamp {
            float: right;
            max-width: 100px;
            max-height: 60px;
            margin-top: 20px;
        }
        
        .amount-words {
            font-style: italic;
            margin-top: 15px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        
        .clearfix::after {
            content: "";
            display: table;
            clear: both;
        }
        """
    
    def generate_receipt_pdf(self, receipt: PaymentReceipt, template_id: int = None) -> bytes:
        """Generate PDF for a payment receipt using specified or default template."""
        
        # Get template
        from app.services.template_service import TemplateService
        from app.models.template import TemplateCategory
        
        template_service = TemplateService(self.db)
        
        if template_id:
            template = template_service.get_template_by_id(template_id)
            if not template or template.category != TemplateCategory.RECEIPT:
                template = template_service.get_user_default_template(receipt.user_id, TemplateCategory.RECEIPT)
        else:
            template = template_service.get_user_default_template(receipt.user_id, TemplateCategory.RECEIPT)
        
        if not template:
            template = template_service.get_default_template(TemplateCategory.RECEIPT)
        
        if not template:
            raise ValueError("No receipt template available")
        
        # Update receipt template reference
        receipt.template_id = template.id
        if self.db:
            self.db.commit()
        
        # Prepare template context
        context = {
            'receipt': receipt,
            'generated_at': datetime.now(),
            'format_currency': self._format_currency,
            'format_date': self._format_date,
            'number_to_words': self._number_to_words
        }
        
        # Load template using Jinja2
        from jinja2 import Environment, FileSystemLoader
        import os
        
        template_dir = os.path.dirname(template.html_path)
        env = Environment(loader=FileSystemLoader(template_dir))
        jinja_template = env.get_template(template.html_file)
        
        # Render HTML content
        html_content = jinja_template.render(context)
        
        # Load CSS content
        css_content = ""
        if os.path.exists(template.css_path):
            with open(template.css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        
        try:
            # Generate PDF with WeasyPrint and return as bytes
            pdf_bytes = weasyprint.HTML(string=html_content, base_url=template_dir).write_pdf(
                stylesheets=[weasyprint.CSS(string=css_content)]
            )
            
            return pdf_bytes
            
        except Exception as e:
            print(f"Receipt PDF generation error: {e}")
            raise e
    
    def _get_receipt_pdf_css(self) -> str:
        """Get CSS styles for receipt PDF generation."""
        return """
        @page {
            size: A4;
            margin: 1cm;
        }
        
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 12px;
            line-height: 1.4;
            color: #333;
        }
        
        .receipt-header {
            text-align: center;
            border-bottom: 2px solid #28a745;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .receipt-title {
            font-size: 28px;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 10px;
        }
        
        .receipt-number {
            font-size: 18px;
            font-weight: bold;
            color: #6c757d;
            margin-bottom: 5px;
        }
        
        .receipt-date {
            font-size: 14px;
            color: #6c757d;
        }
        
        .company-section {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .company-name {
            font-size: 18px;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 5px;
        }
        
        .customer-section {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 14px;
            font-weight: bold;
            color: #495057;
            margin-bottom: 10px;
            border-bottom: 1px solid #dee2e6;
            padding-bottom: 5px;
        }
        
        .payment-details {
            background-color: #fff;
            border: 2px solid #28a745;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .payment-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        
        .payment-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .payment-table .label {
            font-weight: bold;
            color: #495057;
            width: 40%;
        }
        
        .payment-table .value {
            color: #212529;
        }
        
        .amount-section {
            background-color: #d4edda;
            border: 2px solid #28a745;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .total-amount {
            font-size: 24px;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 10px;
        }
        
        .amount-breakdown {
            font-size: 14px;
            color: #495057;
        }
        
        .amount-words {
            font-style: italic;
            margin-top: 15px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #28a745;
        }
        
        .tax-section {
            margin-bottom: 20px;
        }
        
        .tax-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }
        
        .tax-table th,
        .tax-table td {
            border: 1px solid #dee2e6;
            padding: 8px;
            text-align: center;
        }
        
        .tax-table th {
            background-color: #28a745;
            color: white;
            font-weight: bold;
        }
        
        .footer-section {
            margin-top: 40px;
            text-align: center;
            border-top: 1px solid #dee2e6;
            padding-top: 20px;
        }
        
        .footer-text {
            font-size: 11px;
            color: #6c757d;
            line-height: 1.6;
        }
        
        .signature-section {
            margin-top: 40px;
            text-align: right;
        }
        
        .signature-line {
            border-top: 1px solid #333;
            width: 200px;
            margin: 40px 0 10px auto;
        }
        
        .signature-label {
            font-size: 12px;
            color: #495057;
        }
        
        .watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 72px;
            color: rgba(40, 167, 69, 0.1);
            z-index: -1;
            font-weight: bold;
        }
        
        .clearfix::after {
            content: "";
            display: table;
            clear: both;
        }
        """
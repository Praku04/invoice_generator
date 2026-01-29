"""Additional template generators for the multi-template system."""

class TemplateGenerators:
    """Class containing all template generation methods."""
    
    # ===== INVOICE TEMPLATE GENERATORS =====
    
    @staticmethod
    def generate_elegant_invoice_html() -> str:
        """Generate elegant invoice HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invoice {{ invoice.invoice_number }}</title>
</head>
<body>
    <div class="invoice-container">
        <div class="elegant-header">
            <div class="header-content">
                {% if logo_url %}
                <img src="{{ logo_url }}" alt="Logo" class="elegant-logo">
                {% endif %}
                <div class="company-info">
                    <h1 class="company-name">{{ company.company_name if company else invoice.user.full_name }}</h1>
                    {% if company and company.address %}
                    <div class="company-address">{{ company.address }}, {{ company.city }}</div>
                    {% endif %}
                </div>
            </div>
            <div class="invoice-badge">
                <div class="invoice-title">INVOICE</div>
                <div class="invoice-number">{{ invoice.invoice_number }}</div>
                <div class="invoice-date">{{ format_date(invoice.invoice_date) }}</div>
            </div>
        </div>
        
        <div class="client-section">
            <div class="section-title">Bill To</div>
            <div class="client-card">
                <div class="client-name">{{ invoice.client_name }}</div>
                {% if invoice.client_address_line1 %}
                <div class="client-address">{{ invoice.client_address_line1 }}, {{ invoice.client_city }}</div>
                {% endif %}
                {% if invoice.client_email %}
                <div class="client-email">{{ invoice.client_email }}</div>
                {% endif %}
            </div>
        </div>
        
        <div class="items-section">
            <table class="elegant-table">
                <thead>
                    <tr>
                        <th>Description</th>
                        <th>Qty</th>
                        <th>Rate</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td>
                            <div class="item-desc">{{ item.description }}</div>
                            {% if item.notes %}
                            <div class="item-notes">{{ item.notes }}</div>
                            {% endif %}
                        </td>
                        <td class="text-center">{{ item.quantity }}</td>
                        <td class="text-right">{{ format_currency(item.rate, invoice.currency_symbol) }}</td>
                        <td class="text-right">{{ format_currency(item.amount, invoice.currency_symbol) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="totals-section">
            <div class="totals-card">
                <div class="total-row">
                    <span>Subtotal</span>
                    <span>{{ format_currency(invoice.subtotal, invoice.currency_symbol) }}</span>
                </div>
                {% if invoice.tax_amount > 0 %}
                <div class="total-row">
                    <span>Tax</span>
                    <span>{{ format_currency(invoice.tax_amount, invoice.currency_symbol) }}</span>
                </div>
                {% endif %}
                <div class="total-row grand-total">
                    <span>Total</span>
                    <span>{{ format_currency(invoice.grand_total, invoice.currency_symbol) }}</span>
                </div>
            </div>
        </div>
        
        {% if invoice.notes %}
        <div class="notes-section">
            <div class="notes-title">Notes</div>
            <div class="notes-content">{{ invoice.notes }}</div>
        </div>
        {% endif %}
        
        <div class="elegant-footer">
            <div class="footer-line"></div>
            <div class="footer-text">Thank you for your business</div>
            <div class="generated-text">Generated on {{ generated_at.strftime('%B %d, %Y') }}</div>
        </div>
    </div>
</body>
</html>"""
    
    @staticmethod
    def generate_elegant_invoice_css() -> str:
        """Generate elegant invoice CSS template."""
        return """@page { size: A4; margin: 1.5cm; }
body { font-family: 'Georgia', serif; font-size: 13px; line-height: 1.5; color: #2c3e50; background: #fefefe; }
.invoice-container { max-width: 800px; margin: 0 auto; background: white; }
.elegant-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; padding: 30px 0; border-bottom: 3px solid #d4af37; }
.header-content { display: flex; align-items: center; }
.elegant-logo { max-width: 80px; max-height: 60px; margin-right: 20px; border-radius: 8px; }
.company-name { font-size: 26px; margin: 0; color: #d4af37; font-weight: 300; letter-spacing: 1px; }
.company-address { font-size: 12px; color: #7f8c8d; margin-top: 8px; font-style: italic; }
.invoice-badge { text-align: right; background: linear-gradient(135deg, #d4af37, #f1c40f); color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
.invoice-title { font-size: 24px; font-weight: bold; margin-bottom: 8px; }
.invoice-number { font-size: 16px; margin-bottom: 5px; }
.invoice-date { font-size: 14px; opacity: 0.9; }
.client-section { margin-bottom: 35px; }
.section-title { font-size: 18px; color: #d4af37; margin-bottom: 15px; font-weight: 500; border-bottom: 2px solid #d4af37; padding-bottom: 5px; display: inline-block; }
.client-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #d4af37; }
.client-name { font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 8px; }
.client-address, .client-email { color: #7f8c8d; margin: 4px 0; }
.items-section { margin-bottom: 35px; }
.elegant-table { width: 100%; border-collapse: collapse; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
.elegant-table th { background: linear-gradient(135deg, #d4af37, #f1c40f); color: white; padding: 15px 12px; text-align: left; font-weight: 500; }
.elegant-table td { padding: 12px; border-bottom: 1px solid #ecf0f1; }
.elegant-table tbody tr:hover { background: #f8f9fa; }
.elegant-table tbody tr:last-child td { border-bottom: none; }
.item-desc { font-weight: 500; color: #2c3e50; }
.item-notes { font-size: 11px; color: #7f8c8d; font-style: italic; margin-top: 4px; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.totals-section { display: flex; justify-content: flex-end; margin-bottom: 35px; }
.totals-card { min-width: 300px; background: #f8f9fa; border-radius: 8px; padding: 20px; border: 2px solid #d4af37; }
.total-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ecf0f1; }
.total-row:last-child { border-bottom: none; }
.total-row.grand-total { font-size: 18px; font-weight: bold; color: #d4af37; border-top: 2px solid #d4af37; padding-top: 15px; margin-top: 10px; }
.notes-section { margin-bottom: 35px; background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #d4af37; }
.notes-title { font-size: 16px; color: #d4af37; margin-bottom: 10px; font-weight: 500; }
.notes-content { color: #7f8c8d; line-height: 1.6; }
.elegant-footer { text-align: center; padding-top: 30px; }
.footer-line { height: 2px; background: linear-gradient(to right, transparent, #d4af37, transparent); margin-bottom: 15px; }
.footer-text { font-size: 16px; color: #d4af37; font-style: italic; margin-bottom: 8px; }
.generated-text { font-size: 11px; color: #95a5a6; }"""
    
    @staticmethod
    def generate_corporate_invoice_html() -> str:
        """Generate corporate invoice HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invoice {{ invoice.invoice_number }}</title>
</head>
<body>
    <div class="invoice-container">
        <div class="corporate-header">
            <div class="header-stripe"></div>
            <div class="header-content">
                <div class="logo-section">
                    {% if logo_url %}
                    <img src="{{ logo_url }}" alt="Company Logo" class="corporate-logo">
                    {% endif %}
                    <div class="company-details">
                        <h1 class="company-name">{{ company.company_name if company else invoice.user.full_name }}</h1>
                        {% if company and company.address %}
                        <div class="company-info">
                            {{ company.address }}, {{ company.city }}, {{ company.state }} {{ company.postal_code }}
                        </div>
                        {% endif %}
                        {% if company and company.phone %}
                        <div class="company-contact">{{ company.phone }} | {{ invoice.user.email }}</div>
                        {% endif %}
                    </div>
                </div>
                <div class="invoice-info">
                    <div class="invoice-title">INVOICE</div>
                    <div class="invoice-details">
                        <div class="detail-item">
                            <span class="label">Invoice #:</span>
                            <span class="value">{{ invoice.invoice_number }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Date:</span>
                            <span class="value">{{ format_date(invoice.invoice_date) }}</span>
                        </div>
                        {% if invoice.due_date %}
                        <div class="detail-item">
                            <span class="label">Due Date:</span>
                            <span class="value">{{ format_date(invoice.due_date) }}</span>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="billing-info">
            <div class="bill-to-section">
                <div class="section-header">BILL TO</div>
                <div class="client-info">
                    <div class="client-name">{{ invoice.client_name }}</div>
                    {% if invoice.client_address_line1 %}
                    <div class="client-address">
                        {{ invoice.client_address_line1 }}
                        {% if invoice.client_address_line2 %}<br>{{ invoice.client_address_line2 }}{% endif %}
                        <br>{{ invoice.client_city }}, {{ invoice.client_state }} {{ invoice.client_postal_code }}
                    </div>
                    {% endif %}
                    {% if invoice.client_email %}
                    <div class="client-contact">{{ invoice.client_email }}</div>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="items-container">
            <table class="corporate-table">
                <thead>
                    <tr>
                        <th class="desc-header">DESCRIPTION</th>
                        <th class="qty-header">QTY</th>
                        <th class="rate-header">UNIT PRICE</th>
                        <th class="amount-header">AMOUNT</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr class="item-row">
                        <td class="desc-cell">
                            <div class="item-title">{{ item.description }}</div>
                            {% if item.notes %}
                            <div class="item-subtitle">{{ item.notes }}</div>
                            {% endif %}
                        </td>
                        <td class="qty-cell">{{ item.quantity }}</td>
                        <td class="rate-cell">{{ format_currency(item.rate, invoice.currency_symbol) }}</td>
                        <td class="amount-cell">{{ format_currency(item.amount, invoice.currency_symbol) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="summary-container">
            <div class="summary-box">
                <div class="summary-row">
                    <span class="summary-label">SUBTOTAL</span>
                    <span class="summary-value">{{ format_currency(invoice.subtotal, invoice.currency_symbol) }}</span>
                </div>
                {% if invoice.tax_amount > 0 %}
                <div class="summary-row">
                    <span class="summary-label">TAX</span>
                    <span class="summary-value">{{ format_currency(invoice.tax_amount, invoice.currency_symbol) }}</span>
                </div>
                {% endif %}
                <div class="summary-row total-row">
                    <span class="summary-label">TOTAL</span>
                    <span class="summary-value">{{ format_currency(invoice.grand_total, invoice.currency_symbol) }}</span>
                </div>
            </div>
        </div>
        
        {% if invoice.notes %}
        <div class="notes-container">
            <div class="notes-header">NOTES</div>
            <div class="notes-body">{{ invoice.notes }}</div>
        </div>
        {% endif %}
        
        <div class="corporate-footer">
            <div class="footer-stripe"></div>
            <div class="footer-content">
                {% if stamp_url %}
                <div class="signature-section">
                    <img src="{{ stamp_url }}" alt="Authorized Signature" class="signature-stamp">
                    <div class="signature-text">Authorized Signature</div>
                </div>
                {% endif %}
                <div class="footer-info">
                    <div class="generated-info">Document generated on {{ generated_at.strftime('%B %d, %Y at %I:%M %p') }}</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    @staticmethod
    def generate_corporate_invoice_css() -> str:
        """Generate corporate invoice CSS template."""
        return """@page { size: A4; margin: 1cm; }
body { font-family: 'Arial', sans-serif; font-size: 12px; line-height: 1.4; color: #2c3e50; margin: 0; padding: 0; }
.invoice-container { max-width: 100%; margin: 0 auto; background: white; }
.corporate-header { margin-bottom: 30px; }
.header-stripe { height: 8px; background: linear-gradient(90deg, #1e3a8a, #3b82f6, #1e3a8a); }
.header-content { display: flex; justify-content: space-between; align-items: flex-start; padding: 25px 0; }
.logo-section { display: flex; align-items: center; }
.corporate-logo { max-width: 120px; max-height: 80px; margin-right: 20px; }
.company-name { font-size: 28px; font-weight: bold; color: #1e3a8a; margin: 0; letter-spacing: -0.5px; }
.company-info { font-size: 11px; color: #64748b; margin-top: 8px; line-height: 1.3; }
.company-contact { font-size: 11px; color: #64748b; margin-top: 4px; }
.invoice-info { text-align: right; }
.invoice-title { font-size: 36px; font-weight: bold; color: #1e3a8a; margin-bottom: 15px; letter-spacing: 2px; }
.invoice-details { }
.detail-item { display: flex; justify-content: space-between; margin: 6px 0; min-width: 200px; }
.label { font-weight: bold; color: #475569; }
.value { color: #1e293b; }
.billing-info { margin-bottom: 30px; }
.section-header { font-size: 12px; font-weight: bold; color: #1e3a8a; margin-bottom: 12px; letter-spacing: 1px; border-bottom: 2px solid #1e3a8a; padding-bottom: 4px; display: inline-block; }
.client-name { font-size: 16px; font-weight: bold; color: #1e293b; margin-bottom: 8px; }
.client-address { color: #64748b; line-height: 1.4; margin: 6px 0; }
.client-contact { color: #64748b; margin-top: 6px; }
.items-container { margin-bottom: 30px; }
.corporate-table { width: 100%; border-collapse: collapse; border: 2px solid #1e3a8a; }
.corporate-table th { background: #1e3a8a; color: white; padding: 12px 10px; text-align: left; font-weight: bold; font-size: 11px; letter-spacing: 0.5px; }
.desc-header { width: 50%; }
.qty-header { width: 15%; text-align: center; }
.rate-header { width: 17.5%; text-align: right; }
.amount-header { width: 17.5%; text-align: right; }
.corporate-table td { padding: 12px 10px; border-bottom: 1px solid #e2e8f0; }
.item-row:nth-child(even) { background: #f8fafc; }
.item-row:hover { background: #f1f5f9; }
.item-title { font-weight: 500; color: #1e293b; }
.item-subtitle { font-size: 10px; color: #64748b; margin-top: 3px; font-style: italic; }
.qty-cell { text-align: center; }
.rate-cell, .amount-cell { text-align: right; font-family: 'Courier New', monospace; }
.summary-container { display: flex; justify-content: flex-end; margin-bottom: 30px; }
.summary-box { min-width: 300px; border: 2px solid #1e3a8a; background: #f8fafc; }
.summary-row { display: flex; justify-content: space-between; padding: 10px 15px; border-bottom: 1px solid #e2e8f0; }
.summary-row:last-child { border-bottom: none; }
.summary-label { font-weight: bold; color: #475569; font-size: 11px; letter-spacing: 0.5px; }
.summary-value { font-family: 'Courier New', monospace; color: #1e293b; }
.total-row { background: #1e3a8a; color: white; font-size: 14px; font-weight: bold; }
.total-row .summary-label, .total-row .summary-value { color: white; }
.notes-container { margin-bottom: 30px; border: 1px solid #e2e8f0; background: #f8fafc; }
.notes-header { background: #1e3a8a; color: white; padding: 8px 15px; font-weight: bold; font-size: 11px; letter-spacing: 0.5px; }
.notes-body { padding: 15px; color: #475569; line-height: 1.5; }
.corporate-footer { margin-top: 40px; }
.footer-stripe { height: 4px; background: linear-gradient(90deg, #1e3a8a, #3b82f6, #1e3a8a); }
.footer-content { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; }
.signature-section { text-align: center; }
.signature-stamp { max-width: 100px; max-height: 60px; }
.signature-text { font-size: 10px; color: #64748b; margin-top: 5px; }
.footer-info { text-align: right; }
.generated-info { font-size: 10px; color: #94a3b8; }"""
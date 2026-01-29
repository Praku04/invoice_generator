"""Template initialization service for setting up default templates."""

import os
import shutil
from sqlalchemy.orm import Session
from app.services.template_service import TemplateService
from app.models.template import TemplateCategory


class TemplateInitializationService:
    """Service for initializing default templates."""
    
    def __init__(self, db: Session):
        self.db = db
        self.template_service = TemplateService(db)
    
    def initialize_all_templates(self):
        """Initialize all default templates."""
        print("🎨 Initializing template system...")
        
        # Create invoice templates
        self._create_invoice_templates()
        
        # Create receipt templates  
        self._create_receipt_templates()
        
        # Copy template assets to static directory
        self._copy_template_assets()
        
        print("✅ Template system initialized successfully!")
    
    def _create_invoice_templates(self):
        """Create default invoice templates."""
        print("📄 Creating 20 invoice templates...")
        
        # Define all 20 invoice templates
        invoice_templates = [
            # Free Templates (5)
            {
                'template_id': 'classic',
                'name': 'Classic Invoice',
                'description': 'Traditional professional invoice template with clean layout',
                'is_premium': False,
                'sort_order': 1,
                'features': ['Professional layout', 'Logo support', 'Signature support', 'Tax breakdown', 'Print optimized'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'simple',
                'name': 'Simple Invoice',
                'description': 'Clean and straightforward invoice design for basic needs',
                'is_premium': False,
                'sort_order': 2,
                'features': ['Simple layout', 'Easy to read', 'Basic styling', 'Logo support'],
                'supports_logo': True,
                'supports_signature': False,
                'supports_watermark': False
            },
            {
                'template_id': 'basic',
                'name': 'Basic Invoice',
                'description': 'Essential invoice template with all necessary elements',
                'is_premium': False,
                'sort_order': 3,
                'features': ['Essential elements', 'Clear structure', 'Professional appearance'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'standard',
                'name': 'Standard Invoice',
                'description': 'Standard business invoice template with professional styling',
                'is_premium': False,
                'sort_order': 4,
                'features': ['Standard layout', 'Business professional', 'Tax calculations', 'Logo placement'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'traditional',
                'name': 'Traditional Invoice',
                'description': 'Time-tested traditional invoice format',
                'is_premium': False,
                'sort_order': 5,
                'features': ['Traditional format', 'Formal appearance', 'Standard elements'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': False
            },
            
            # Premium Templates (15)
            {
                'template_id': 'modern',
                'name': 'Modern Invoice',
                'description': 'Contemporary invoice design with gradients and modern styling',
                'is_premium': True,
                'sort_order': 6,
                'features': ['Modern design', 'Gradient headers', 'Color accents', 'Card layouts', 'Premium styling'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'minimal',
                'name': 'Minimal Invoice',
                'description': 'Clean, minimalist invoice design focusing on simplicity',
                'is_premium': True,
                'sort_order': 7,
                'features': ['Minimal design', 'Clean typography', 'Spacious layout', 'Subtle styling'],
                'supports_logo': True,
                'supports_signature': False,
                'supports_watermark': False
            },
            {
                'template_id': 'elegant',
                'name': 'Elegant Invoice',
                'description': 'Sophisticated and elegant invoice design with refined styling',
                'is_premium': True,
                'sort_order': 8,
                'features': ['Elegant typography', 'Refined colors', 'Sophisticated layout', 'Premium feel'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'corporate',
                'name': 'Corporate Invoice',
                'description': 'Professional corporate invoice template for large businesses',
                'is_premium': True,
                'sort_order': 9,
                'features': ['Corporate branding', 'Professional structure', 'Formal appearance', 'Logo prominence'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'creative',
                'name': 'Creative Invoice',
                'description': 'Creative and artistic invoice design for creative professionals',
                'is_premium': True,
                'sort_order': 10,
                'features': ['Creative layout', 'Artistic elements', 'Color variety', 'Unique design'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'tech',
                'name': 'Tech Invoice',
                'description': 'Modern tech-focused invoice template with clean lines',
                'is_premium': True,
                'sort_order': 11,
                'features': ['Tech aesthetic', 'Clean lines', 'Modern fonts', 'Digital feel'],
                'supports_logo': True,
                'supports_signature': False,
                'supports_watermark': True
            },
            {
                'template_id': 'luxury',
                'name': 'Luxury Invoice',
                'description': 'Premium luxury invoice template with gold accents',
                'is_premium': True,
                'sort_order': 12,
                'features': ['Luxury styling', 'Gold accents', 'Premium materials', 'Exclusive design'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'bold',
                'name': 'Bold Invoice',
                'description': 'Bold and striking invoice design that stands out',
                'is_premium': True,
                'sort_order': 13,
                'features': ['Bold typography', 'Strong colors', 'Eye-catching design', 'Impact focus'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'professional',
                'name': 'Professional Invoice',
                'description': 'Ultra-professional invoice template for serious business',
                'is_premium': True,
                'sort_order': 14,
                'features': ['Ultra-professional', 'Serious business', 'Formal structure', 'Executive appeal'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'colorful',
                'name': 'Colorful Invoice',
                'description': 'Vibrant and colorful invoice template with modern appeal',
                'is_premium': True,
                'sort_order': 15,
                'features': ['Vibrant colors', 'Modern appeal', 'Energetic design', 'Brand flexibility'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'geometric',
                'name': 'Geometric Invoice',
                'description': 'Modern geometric patterns and shapes in invoice design',
                'is_premium': True,
                'sort_order': 16,
                'features': ['Geometric patterns', 'Modern shapes', 'Contemporary feel', 'Visual interest'],
                'supports_logo': True,
                'supports_signature': False,
                'supports_watermark': True
            },
            {
                'template_id': 'vintage',
                'name': 'Vintage Invoice',
                'description': 'Classic vintage-inspired invoice with retro styling',
                'is_premium': True,
                'sort_order': 17,
                'features': ['Vintage styling', 'Retro elements', 'Classic appeal', 'Timeless design'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'industrial',
                'name': 'Industrial Invoice',
                'description': 'Industrial-themed invoice with strong, bold elements',
                'is_premium': True,
                'sort_order': 18,
                'features': ['Industrial theme', 'Strong elements', 'Bold structure', 'Robust design'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'artistic',
                'name': 'Artistic Invoice',
                'description': 'Artistic and creative invoice template for artists and designers',
                'is_premium': True,
                'sort_order': 19,
                'features': ['Artistic flair', 'Creative elements', 'Designer appeal', 'Unique layout'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'executive',
                'name': 'Executive Invoice',
                'description': 'Executive-level invoice template with premium presentation',
                'is_premium': True,
                'sort_order': 20,
                'features': ['Executive level', 'Premium presentation', 'High-end appeal', 'Luxury feel'],
                'supports_logo': True,
                'supports_signature': True,
                'supports_watermark': True
            }
        ]
        
        # Create all invoice templates
        for template_data in invoice_templates:
            template_data['category'] = 'invoice'
            
            html_content = self._get_invoice_html_template(template_data['template_id'])
            css_content = self._get_invoice_css_template(template_data['template_id'])
            
            self.template_service.create_template(
                template_data=template_data,
                html_content=html_content,
                css_content=css_content
            )
            print(f"  ✅ {template_data['name']} created ({'Premium' if template_data['is_premium'] else 'Free'})")
    
    def _create_receipt_templates(self):
        """Create default receipt templates."""
        print("🧾 Creating 20 receipt templates...")
        
        # Define all 20 receipt templates
        receipt_templates = [
            # Free Templates (5)
            {
                'template_id': 'classic',
                'name': 'Classic Receipt',
                'description': 'Traditional receipt template with professional styling',
                'is_premium': False,
                'sort_order': 1,
                'features': ['Professional layout', 'Tax breakdown', 'Company branding', 'Watermark'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'simple',
                'name': 'Simple Receipt',
                'description': 'Clean and simple receipt design for basic transactions',
                'is_premium': False,
                'sort_order': 2,
                'features': ['Simple layout', 'Clear information', 'Easy to read', 'Basic styling'],
                'supports_logo': False,
                'supports_signature': False,
                'supports_watermark': False
            },
            {
                'template_id': 'basic',
                'name': 'Basic Receipt',
                'description': 'Essential receipt template with all necessary information',
                'is_premium': False,
                'sort_order': 3,
                'features': ['Essential elements', 'Clear structure', 'Standard format'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'standard',
                'name': 'Standard Receipt',
                'description': 'Standard business receipt template',
                'is_premium': False,
                'sort_order': 4,
                'features': ['Standard format', 'Business appropriate', 'Professional appearance'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'traditional',
                'name': 'Traditional Receipt',
                'description': 'Traditional receipt format with classic styling',
                'is_premium': False,
                'sort_order': 5,
                'features': ['Traditional format', 'Classic styling', 'Time-tested design'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': False
            },
            
            # Premium Templates (15)
            {
                'template_id': 'horizontal',
                'name': 'Horizontal Receipt',
                'description': 'Wide format receipt template with horizontal layout',
                'is_premium': True,
                'sort_order': 6,
                'features': ['Horizontal layout', 'Modern design', 'Color sections', 'Space efficient'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'compact',
                'name': 'Compact Receipt',
                'description': 'Space-efficient receipt template for minimal printing',
                'is_premium': True,
                'sort_order': 7,
                'features': ['Compact design', 'Space efficient', 'Clean layout', 'Minimal styling'],
                'supports_logo': False,
                'supports_signature': False,
                'supports_watermark': False
            },
            {
                'template_id': 'modern',
                'name': 'Modern Receipt',
                'description': 'Contemporary receipt design with modern styling',
                'is_premium': True,
                'sort_order': 8,
                'features': ['Modern design', 'Contemporary styling', 'Clean lines', 'Professional'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'elegant',
                'name': 'Elegant Receipt',
                'description': 'Sophisticated receipt template with elegant styling',
                'is_premium': True,
                'sort_order': 9,
                'features': ['Elegant design', 'Sophisticated styling', 'Refined appearance', 'Premium feel'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'corporate',
                'name': 'Corporate Receipt',
                'description': 'Professional corporate receipt template',
                'is_premium': True,
                'sort_order': 10,
                'features': ['Corporate styling', 'Professional appearance', 'Business appropriate', 'Formal'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'colorful',
                'name': 'Colorful Receipt',
                'description': 'Vibrant receipt template with color accents',
                'is_premium': True,
                'sort_order': 11,
                'features': ['Vibrant colors', 'Color accents', 'Eye-catching', 'Modern appeal'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'minimal',
                'name': 'Minimal Receipt',
                'description': 'Clean minimalist receipt design',
                'is_premium': True,
                'sort_order': 12,
                'features': ['Minimal design', 'Clean layout', 'Simple styling', 'Uncluttered'],
                'supports_logo': False,
                'supports_signature': False,
                'supports_watermark': False
            },
            {
                'template_id': 'detailed',
                'name': 'Detailed Receipt',
                'description': 'Comprehensive receipt template with detailed information',
                'is_premium': True,
                'sort_order': 13,
                'features': ['Detailed information', 'Comprehensive layout', 'Full breakdown', 'Complete data'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'professional',
                'name': 'Professional Receipt',
                'description': 'Ultra-professional receipt template for business use',
                'is_premium': True,
                'sort_order': 14,
                'features': ['Ultra-professional', 'Business focused', 'Formal appearance', 'Executive level'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'branded',
                'name': 'Branded Receipt',
                'description': 'Receipt template with strong branding elements',
                'is_premium': True,
                'sort_order': 15,
                'features': ['Strong branding', 'Brand focused', 'Company identity', 'Marketing appeal'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'thermal',
                'name': 'Thermal Receipt',
                'description': 'Thermal printer optimized receipt template',
                'is_premium': True,
                'sort_order': 16,
                'features': ['Thermal optimized', 'Printer friendly', 'Narrow format', 'High contrast'],
                'supports_logo': False,
                'supports_signature': False,
                'supports_watermark': False
            },
            {
                'template_id': 'luxury',
                'name': 'Luxury Receipt',
                'description': 'Premium luxury receipt template with gold accents',
                'is_premium': True,
                'sort_order': 17,
                'features': ['Luxury styling', 'Gold accents', 'Premium feel', 'Exclusive design'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            },
            {
                'template_id': 'digital',
                'name': 'Digital Receipt',
                'description': 'Modern digital-first receipt template',
                'is_premium': True,
                'sort_order': 18,
                'features': ['Digital optimized', 'Screen friendly', 'Modern layout', 'Tech focused'],
                'supports_logo': False,
                'supports_signature': False,
                'supports_watermark': True
            },
            {
                'template_id': 'eco',
                'name': 'Eco Receipt',
                'description': 'Environmentally conscious receipt template',
                'is_premium': True,
                'sort_order': 19,
                'features': ['Eco-friendly', 'Green theme', 'Sustainable design', 'Environmental focus'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': False
            },
            {
                'template_id': 'premium',
                'name': 'Premium Receipt',
                'description': 'High-end premium receipt template with luxury appeal',
                'is_premium': True,
                'sort_order': 20,
                'features': ['Premium design', 'Luxury appeal', 'High-end styling', 'Exclusive feel'],
                'supports_logo': False,
                'supports_signature': True,
                'supports_watermark': True
            }
        ]
        
        # Create all receipt templates
        for template_data in receipt_templates:
            template_data['category'] = 'receipt'
            
            html_content = self._get_receipt_html_template(template_data['template_id'])
            css_content = self._get_receipt_css_template(template_data['template_id'])
            
            self.template_service.create_template(
                template_data=template_data,
                html_content=html_content,
                css_content=css_content
            )
            print(f"  ✅ {template_data['name']} created ({'Premium' if template_data['is_premium'] else 'Free'})")
    
    def _copy_template_assets(self):
        """Copy template assets to static directory."""
        print("📁 Setting up template assets...")
        
        # Create static template directories
        static_templates_dir = "static/templates"
        os.makedirs(f"{static_templates_dir}/invoices", exist_ok=True)
        os.makedirs(f"{static_templates_dir}/receipts", exist_ok=True)
        
        # Copy template directories to static for preview images
        template_base = "app/templates/pdf"
        
        for category in ['invoices', 'receipts']:
            category_path = os.path.join(template_base, category)
            static_category_path = os.path.join(static_templates_dir, category)
            
            if os.path.exists(category_path):
                for template_dir in os.listdir(category_path):
                    template_path = os.path.join(category_path, template_dir)
                    static_template_path = os.path.join(static_category_path, template_dir)
                    
                    if os.path.isdir(template_path):
                        os.makedirs(static_template_path, exist_ok=True)
                        
                        # Copy preview images if they exist
                        preview_path = os.path.join(template_path, "preview.png")
                        if os.path.exists(preview_path):
                            shutil.copy2(preview_path, static_template_path)
        
        print("  ✅ Template assets copied to static directory")
    
    def _get_invoice_html_template(self, template_id: str) -> str:
        """Get HTML content for invoice templates."""
        
        # Check if template file exists
        template_path = f"app/templates/pdf/invoices/{template_id}/template.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Generate template based on template_id
        if template_id == 'classic':
            return self._get_classic_invoice_html()
        elif template_id == 'modern':
            return self._get_modern_invoice_html()
        elif template_id == 'minimal':
            return self._get_minimal_invoice_html()
        elif template_id == 'simple':
            return self._generate_simple_invoice_html()
        elif template_id == 'basic':
            return self._generate_basic_invoice_html()
        elif template_id == 'standard':
            return self._generate_standard_invoice_html()
        elif template_id == 'traditional':
            return self._generate_traditional_invoice_html()
        elif template_id == 'elegant':
            return self._generate_elegant_invoice_html()
        elif template_id == 'corporate':
            return self._generate_corporate_invoice_html()
        elif template_id == 'creative':
            return self._generate_creative_invoice_html()
        elif template_id == 'tech':
            return self._generate_tech_invoice_html()
        elif template_id == 'luxury':
            return self._generate_luxury_invoice_html()
        elif template_id == 'bold':
            return self._generate_bold_invoice_html()
        elif template_id == 'professional':
            return self._generate_professional_invoice_html()
        elif template_id == 'colorful':
            return self._generate_colorful_invoice_html()
        elif template_id == 'geometric':
            return self._generate_geometric_invoice_html()
        elif template_id == 'vintage':
            return self._generate_vintage_invoice_html()
        elif template_id == 'industrial':
            return self._generate_industrial_invoice_html()
        elif template_id == 'artistic':
            return self._generate_artistic_invoice_html()
        elif template_id == 'executive':
            return self._generate_executive_invoice_html()
        else:
            return self._get_default_invoice_html()
    
    def _get_invoice_css_template(self, template_id: str) -> str:
        """Get CSS content for invoice templates."""
        
        # Check if template file exists
        template_path = f"app/templates/pdf/invoices/{template_id}/style.css"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Generate CSS based on template_id
        if template_id == 'classic':
            return self._get_classic_invoice_css()
        elif template_id == 'modern':
            return self._get_modern_invoice_css()
        elif template_id == 'minimal':
            return self._get_minimal_invoice_css()
        elif template_id == 'simple':
            return self._generate_simple_invoice_css()
        elif template_id == 'basic':
            return self._generate_basic_invoice_css()
        elif template_id == 'standard':
            return self._generate_standard_invoice_css()
        elif template_id == 'traditional':
            return self._generate_traditional_invoice_css()
        elif template_id == 'elegant':
            return self._generate_elegant_invoice_css()
        elif template_id == 'corporate':
            return self._generate_corporate_invoice_css()
        elif template_id == 'creative':
            return self._generate_creative_invoice_css()
        elif template_id == 'tech':
            return self._generate_tech_invoice_css()
        elif template_id == 'luxury':
            return self._generate_luxury_invoice_css()
        elif template_id == 'bold':
            return self._generate_bold_invoice_css()
        elif template_id == 'professional':
            return self._generate_professional_invoice_css()
        elif template_id == 'colorful':
            return self._generate_colorful_invoice_css()
        elif template_id == 'geometric':
            return self._generate_geometric_invoice_css()
        elif template_id == 'vintage':
            return self._generate_vintage_invoice_css()
        elif template_id == 'industrial':
            return self._generate_industrial_invoice_css()
        elif template_id == 'artistic':
            return self._generate_artistic_invoice_css()
        elif template_id == 'executive':
            return self._generate_executive_invoice_css()
        else:
            return self._get_default_invoice_css()
    
    def _get_receipt_html_template(self, template_id: str) -> str:
        """Get HTML content for receipt templates."""
        
        # Check if template file exists
        template_path = f"app/templates/pdf/receipts/{template_id}/template.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Generate template based on template_id
        if template_id == 'classic':
            return self._get_classic_receipt_html()
        elif template_id == 'horizontal':
            return self._get_horizontal_receipt_html()
        elif template_id == 'compact':
            return self._get_compact_receipt_html()
        elif template_id == 'simple':
            return self._generate_simple_receipt_html()
        elif template_id == 'basic':
            return self._generate_basic_receipt_html()
        elif template_id == 'standard':
            return self._generate_standard_receipt_html()
        elif template_id == 'traditional':
            return self._generate_traditional_receipt_html()
        elif template_id == 'modern':
            return self._generate_modern_receipt_html()
        elif template_id == 'elegant':
            return self._generate_elegant_receipt_html()
        elif template_id == 'corporate':
            return self._generate_corporate_receipt_html()
        elif template_id == 'colorful':
            return self._generate_colorful_receipt_html()
        elif template_id == 'minimal':
            return self._generate_minimal_receipt_html()
        elif template_id == 'detailed':
            return self._generate_detailed_receipt_html()
        elif template_id == 'professional':
            return self._generate_professional_receipt_html()
        elif template_id == 'branded':
            return self._generate_branded_receipt_html()
        elif template_id == 'thermal':
            return self._generate_thermal_receipt_html()
        elif template_id == 'luxury':
            return self._generate_luxury_receipt_html()
        elif template_id == 'digital':
            return self._generate_digital_receipt_html()
        elif template_id == 'eco':
            return self._generate_eco_receipt_html()
        elif template_id == 'premium':
            return self._generate_premium_receipt_html()
        else:
            return self._get_default_receipt_html()
    
    def _get_receipt_css_template(self, template_id: str) -> str:
        """Get CSS content for receipt templates."""
        
        # Check if template file exists
        template_path = f"app/templates/pdf/receipts/{template_id}/style.css"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Generate CSS based on template_id
        if template_id == 'classic':
            return self._get_classic_receipt_css()
        elif template_id == 'horizontal':
            return self._get_horizontal_receipt_css()
        elif template_id == 'compact':
            return self._get_compact_receipt_css()
        elif template_id == 'simple':
            return self._generate_simple_receipt_css()
        elif template_id == 'basic':
            return self._generate_basic_receipt_css()
        elif template_id == 'standard':
            return self._generate_standard_receipt_css()
        elif template_id == 'traditional':
            return self._generate_traditional_receipt_css()
        elif template_id == 'modern':
            return self._generate_modern_receipt_css()
        elif template_id == 'elegant':
            return self._generate_elegant_receipt_css()
        elif template_id == 'corporate':
            return self._generate_corporate_receipt_css()
        elif template_id == 'colorful':
            return self._generate_colorful_receipt_css()
        elif template_id == 'minimal':
            return self._generate_minimal_receipt_css()
        elif template_id == 'detailed':
            return self._generate_detailed_receipt_css()
        elif template_id == 'professional':
            return self._generate_professional_receipt_css()
        elif template_id == 'branded':
            return self._generate_branded_receipt_css()
        elif template_id == 'thermal':
            return self._generate_thermal_receipt_css()
        elif template_id == 'luxury':
            return self._generate_luxury_receipt_css()
        elif template_id == 'digital':
            return self._generate_digital_receipt_css()
        elif template_id == 'eco':
            return self._generate_eco_receipt_css()
        elif template_id == 'premium':
            return self._generate_premium_receipt_css()
        else:
            return self._get_default_receipt_css()
    
    def _get_minimal_invoice_html(self) -> str:
        """Get minimal invoice HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invoice {{ invoice.invoice_number }}</title>
</head>
<body>
    <div class="invoice-container">
        <div class="header">
            <h1>INVOICE</h1>
            <div class="invoice-number">#{{ invoice.invoice_number }}</div>
        </div>
        
        <div class="parties">
            <div class="from">
                <h3>From</h3>
                <div class="company-name">{{ company.company_name if company else invoice.user.full_name }}</div>
                {% if company and company.address %}
                <div>{{ company.address }}, {{ company.city }}</div>
                {% endif %}
            </div>
            
            <div class="to">
                <h3>To</h3>
                <div class="client-name">{{ invoice.client_name }}</div>
                {% if invoice.client_address_line1 %}
                <div>{{ invoice.client_address_line1 }}, {{ invoice.client_city }}</div>
                {% endif %}
            </div>
        </div>
        
        <div class="details">
            <div>Date: {{ format_date(invoice.invoice_date) }}</div>
            {% if invoice.due_date %}
            <div>Due: {{ format_date(invoice.due_date) }}</div>
            {% endif %}
        </div>
        
        <table class="items">
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
                    <td>{{ item.description }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ format_currency(item.rate, invoice.currency_symbol) }}</td>
                    <td>{{ format_currency(item.amount, invoice.currency_symbol) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="totals">
            <div class="total-line">
                <span>Subtotal:</span>
                <span>{{ format_currency(invoice.subtotal, invoice.currency_symbol) }}</span>
            </div>
            {% if invoice.tax_amount > 0 %}
            <div class="total-line">
                <span>Tax:</span>
                <span>{{ format_currency(invoice.tax_amount, invoice.currency_symbol) }}</span>
            </div>
            {% endif %}
            <div class="total-line grand">
                <span>Total:</span>
                <span>{{ format_currency(invoice.grand_total, invoice.currency_symbol) }}</span>
            </div>
        </div>
        
        {% if invoice.notes %}
        <div class="notes">{{ invoice.notes }}</div>
        {% endif %}
    </div>
</body>
</html>"""
    
    def _get_minimal_invoice_css(self) -> str:
        """Get minimal invoice CSS template."""
        return """@page { size: A4; margin: 2cm; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 14px; line-height: 1.6; color: #333; }
.invoice-container { max-width: 800px; margin: 0 auto; }
.header { text-align: center; margin-bottom: 40px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
.header h1 { font-size: 36px; margin: 0; color: #333; font-weight: 300; }
.invoice-number { font-size: 18px; color: #666; margin-top: 10px; }
.parties { display: flex; justify-content: space-between; margin-bottom: 40px; }
.from, .to { flex: 1; }
.from h3, .to h3 { font-size: 16px; color: #666; margin-bottom: 10px; font-weight: 400; }
.company-name, .client-name { font-size: 18px; font-weight: 500; margin-bottom: 5px; }
.details { margin-bottom: 30px; font-size: 14px; color: #666; }
.items { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
.items th { background: #f8f9fa; padding: 15px 10px; text-align: left; font-weight: 500; border-bottom: 1px solid #eee; }
.items td { padding: 15px 10px; border-bottom: 1px solid #f0f0f0; }
.items tbody tr:hover { background: #fafafa; }
.totals { text-align: right; margin-bottom: 30px; }
.total-line { display: flex; justify-content: space-between; padding: 8px 0; max-width: 300px; margin-left: auto; }
.total-line.grand { font-size: 18px; font-weight: 600; border-top: 1px solid #333; padding-top: 15px; margin-top: 15px; }
.notes { margin-top: 40px; padding: 20px; background: #f8f9fa; border-left: 3px solid #333; font-style: italic; }"""
    
    def _get_classic_receipt_html(self) -> str:
        """Get classic receipt HTML template."""
        template_path = "app/templates/pdf/receipts/classic/template.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "<!-- Classic receipt template HTML -->"
    
    def _get_classic_receipt_css(self) -> str:
        """Get classic receipt CSS template."""
        template_path = "app/templates/pdf/receipts/classic/style.css"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "/* Classic receipt template CSS */"
    
    def _get_horizontal_receipt_html(self) -> str:
        """Get horizontal receipt HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Receipt {{ receipt.formatted_receipt_number }}</title>
</head>
<body>
    <div class="receipt-container">
        <div class="header-section">
            <div class="receipt-info">
                <h1>PAYMENT RECEIPT</h1>
                <div class="receipt-number">{{ receipt.formatted_receipt_number }}</div>
                <div class="receipt-date">{{ format_date(receipt.receipt_date) }}</div>
            </div>
            <div class="amount-display">
                <div class="amount-label">Amount Paid</div>
                <div class="amount-value">{{ format_currency(receipt.total_amount, receipt.currency_symbol) }}</div>
            </div>
        </div>
        
        <div class="details-section">
            <div class="company-details">
                <h3>From</h3>
                <div class="company-name">{{ receipt.company_name or "Invoice Generator SaaS" }}</div>
                {% if receipt.company_address %}
                <div class="company-address">{{ receipt.company_address }}</div>
                {% endif %}
            </div>
            
            <div class="customer-details">
                <h3>To</h3>
                <div class="customer-name">{{ receipt.customer_name }}</div>
                <div class="customer-email">{{ receipt.customer_email }}</div>
            </div>
            
            <div class="payment-details">
                <h3>Payment Info</h3>
                <div>Method: {{ receipt.payment_method or 'N/A' }}</div>
                {% if receipt.transaction_id %}
                <div>Transaction: {{ receipt.transaction_id }}</div>
                {% endif %}
            </div>
        </div>
        
        <div class="description-section">
            <h3>Description</h3>
            <div class="description-text">{{ receipt.title }}</div>
            {% if receipt.description %}
            <div class="description-details">{{ receipt.description }}</div>
            {% endif %}
        </div>
        
        <div class="footer-section">
            <div class="thank-you">Thank you for your payment!</div>
            <div class="generated-info">Generated on {{ format_date(generated_at) }}</div>
        </div>
        
        <div class="watermark">PAID</div>
    </div>
</body>
</html>"""
    
    def _get_horizontal_receipt_css(self) -> str:
        """Get horizontal receipt CSS template."""
        return """@page { size: A4 landscape; margin: 1cm; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 12px; color: #333; position: relative; }
.receipt-container { max-width: 100%; }
.watermark { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg); font-size: 80px; color: rgba(76, 175, 80, 0.1); z-index: -1; font-weight: bold; }
.header-section { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
.receipt-info h1 { font-size: 28px; margin: 0 0 10px 0; }
.receipt-number { font-size: 18px; font-weight: bold; }
.receipt-date { font-size: 14px; opacity: 0.9; }
.amount-display { text-align: right; }
.amount-label { font-size: 14px; opacity: 0.9; }
.amount-value { font-size: 32px; font-weight: bold; margin-top: 5px; }
.details-section { display: flex; justify-content: space-between; margin-bottom: 30px; gap: 30px; }
.company-details, .customer-details, .payment-details { flex: 1; background: #f8f9fa; padding: 20px; border-radius: 8px; }
.details-section h3 { color: #4CAF50; margin: 0 0 15px 0; font-size: 16px; border-bottom: 2px solid #4CAF50; padding-bottom: 5px; }
.company-name, .customer-name { font-weight: bold; font-size: 16px; margin-bottom: 8px; }
.description-section { background: #fff; border: 2px solid #4CAF50; border-radius: 8px; padding: 25px; margin-bottom: 30px; }
.description-section h3 { color: #4CAF50; margin: 0 0 15px 0; }
.description-text { font-size: 16px; font-weight: bold; margin-bottom: 10px; }
.description-details { color: #666; }
.footer-section { text-align: center; padding: 20px; border-top: 1px solid #eee; }
.thank-you { font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 10px; }
.generated-info { font-size: 11px; color: #999; }"""
    
    def _get_compact_receipt_html(self) -> str:
        """Get compact receipt HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Receipt {{ receipt.formatted_receipt_number }}</title>
</head>
<body>
    <div class="receipt-container">
        <div class="header">
            <div class="title">RECEIPT</div>
            <div class="number">{{ receipt.formatted_receipt_number }}</div>
        </div>
        
        <div class="info-grid">
            <div class="info-item">
                <span class="label">Date:</span>
                <span class="value">{{ format_date(receipt.receipt_date) }}</span>
            </div>
            <div class="info-item">
                <span class="label">Amount:</span>
                <span class="value amount">{{ format_currency(receipt.total_amount, receipt.currency_symbol) }}</span>
            </div>
            <div class="info-item">
                <span class="label">From:</span>
                <span class="value">{{ receipt.company_name or "Invoice Generator SaaS" }}</span>
            </div>
            <div class="info-item">
                <span class="label">To:</span>
                <span class="value">{{ receipt.customer_name }}</span>
            </div>
            <div class="info-item">
                <span class="label">Method:</span>
                <span class="value">{{ receipt.payment_method or 'N/A' }}</span>
            </div>
            {% if receipt.transaction_id %}
            <div class="info-item">
                <span class="label">Transaction:</span>
                <span class="value">{{ receipt.transaction_id }}</span>
            </div>
            {% endif %}
        </div>
        
        <div class="description">
            <div class="desc-label">Description:</div>
            <div class="desc-text">{{ receipt.title }}</div>
        </div>
        
        <div class="amount-words">
            {{ number_to_words(receipt.total_amount) }}
        </div>
        
        <div class="footer">
            <div class="status">PAID</div>
            <div class="generated">{{ format_date(generated_at) }}</div>
        </div>
    </div>
</body>
</html>"""
    
    def _get_compact_receipt_css(self) -> str:
        """Get compact receipt CSS template."""
        return """@page { size: A4; margin: 1.5cm; }
body { font-family: 'DejaVu Sans', sans-serif; font-size: 11px; color: #333; }
.receipt-container { max-width: 600px; margin: 0 auto; border: 2px solid #333; padding: 20px; }
.header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 20px; }
.title { font-size: 24px; font-weight: bold; }
.number { font-size: 16px; margin-top: 5px; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }
.info-item { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dotted #ccc; }
.label { font-weight: bold; }
.value.amount { font-size: 14px; font-weight: bold; color: #2e7d32; }
.description { margin-bottom: 20px; padding: 15px; background: #f5f5f5; border-left: 4px solid #333; }
.desc-label { font-weight: bold; margin-bottom: 5px; }
.desc-text { font-size: 12px; }
.amount-words { text-align: center; font-style: italic; margin-bottom: 20px; padding: 10px; background: #f9f9f9; }
.footer { display: flex; justify-content: space-between; align-items: center; border-top: 2px solid #333; padding-top: 15px; }
.status { font-size: 18px; font-weight: bold; color: #2e7d32; }
.generated { font-size: 10px; color: #666; }"""
    # ===== INVOICE TEMPLATE GENERATORS =====
    
    def _get_classic_invoice_html(self) -> str:
        """Get classic invoice HTML template."""
        template_path = "app/templates/pdf/invoices/classic/template.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._get_default_invoice_html()
    
    def _get_classic_invoice_css(self) -> str:
        """Get classic invoice CSS template."""
        template_path = "app/templates/pdf/invoices/classic/style.css"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._get_default_invoice_css()
    
    def _get_modern_invoice_html(self) -> str:
        """Get modern invoice HTML template."""
        template_path = "app/templates/pdf/invoices/modern/template.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._get_default_invoice_html()
    
    def _get_modern_invoice_css(self) -> str:
        """Get modern invoice CSS template."""
        template_path = "app/templates/pdf/invoices/modern/style.css"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._get_default_invoice_css()
    
    def _generate_simple_invoice_html(self) -> str:
        """Generate simple invoice HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invoice {{ invoice.invoice_number }}</title>
</head>
<body>
    <div class="invoice-container">
        <div class="header">
            <h1>INVOICE</h1>
            <div class="invoice-number">{{ invoice.invoice_number }}</div>
            <div class="invoice-date">{{ format_date(invoice.invoice_date) }}</div>
        </div>
        
        <div class="parties">
            <div class="from">
                <h3>From:</h3>
                <div>{{ company.company_name if company else invoice.user.full_name }}</div>
                {% if company and company.address %}
                <div>{{ company.address }}, {{ company.city }}</div>
                {% endif %}
            </div>
            
            <div class="to">
                <h3>To:</h3>
                <div>{{ invoice.client_name }}</div>
                {% if invoice.client_address_line1 %}
                <div>{{ invoice.client_address_line1 }}, {{ invoice.client_city }}</div>
                {% endif %}
            </div>
        </div>
        
        <table class="items">
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
                    <td>{{ item.description }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ format_currency(item.rate, invoice.currency_symbol) }}</td>
                    <td>{{ format_currency(item.amount, invoice.currency_symbol) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="totals">
            <div class="total-line">
                <span>Subtotal:</span>
                <span>{{ format_currency(invoice.subtotal, invoice.currency_symbol) }}</span>
            </div>
            {% if invoice.tax_amount > 0 %}
            <div class="total-line">
                <span>Tax:</span>
                <span>{{ format_currency(invoice.tax_amount, invoice.currency_symbol) }}</span>
            </div>
            {% endif %}
            <div class="total-line grand">
                <span>Total:</span>
                <span>{{ format_currency(invoice.grand_total, invoice.currency_symbol) }}</span>
            </div>
        </div>
        
        {% if invoice.notes %}
        <div class="notes">{{ invoice.notes }}</div>
        {% endif %}
    </div>
</body>
</html>"""
    
    def _generate_simple_invoice_css(self) -> str:
        """Generate simple invoice CSS template."""
        return """@page { size: A4; margin: 2cm; }
body { font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #333; }
.invoice-container { max-width: 800px; margin: 0 auto; }
.header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #ddd; }
.header h1 { font-size: 32px; margin: 0; color: #2c3e50; }
.invoice-number { font-size: 16px; margin: 10px 0; }
.invoice-date { font-size: 14px; color: #666; }
.parties { display: flex; justify-content: space-between; margin-bottom: 30px; }
.from, .to { flex: 1; }
.from h3, .to h3 { color: #2c3e50; margin-bottom: 10px; }
.items { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
.items th, .items td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
.items th { background: #f8f9fa; font-weight: bold; }
.totals { text-align: right; margin-bottom: 20px; }
.total-line { display: flex; justify-content: space-between; padding: 5px 0; max-width: 250px; margin-left: auto; }
.total-line.grand { font-size: 18px; font-weight: bold; border-top: 2px solid #2c3e50; padding-top: 10px; margin-top: 10px; }
.notes { margin-top: 30px; padding: 15px; background: #f8f9fa; border-left: 4px solid #2c3e50; }"""
    
    def _generate_basic_invoice_html(self) -> str:
        """Generate basic invoice HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invoice {{ invoice.invoice_number }}</title>
</head>
<body>
    <div class="invoice-container">
        <div class="header-section">
            <div class="company-info">
                {% if logo_url %}
                <img src="{{ logo_url }}" alt="Logo" class="logo">
                {% endif %}
                <h1>{{ company.company_name if company else invoice.user.full_name }}</h1>
                {% if company and company.address %}
                <div class="address">{{ company.address }}, {{ company.city }}</div>
                {% endif %}
            </div>
            <div class="invoice-info">
                <h2>INVOICE</h2>
                <div class="invoice-details">
                    <div>Invoice #: {{ invoice.invoice_number }}</div>
                    <div>Date: {{ format_date(invoice.invoice_date) }}</div>
                    {% if invoice.due_date %}
                    <div>Due: {{ format_date(invoice.due_date) }}</div>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="client-section">
            <h3>Bill To:</h3>
            <div class="client-info">
                <div class="client-name">{{ invoice.client_name }}</div>
                {% if invoice.client_address_line1 %}
                <div>{{ invoice.client_address_line1 }}</div>
                {% if invoice.client_address_line2 %}
                <div>{{ invoice.client_address_line2 }}</div>
                {% endif %}
                <div>{{ invoice.client_city }}, {{ invoice.client_state }} {{ invoice.client_postal_code }}</div>
                {% endif %}
                {% if invoice.client_email %}
                <div>{{ invoice.client_email }}</div>
                {% endif %}
            </div>
        </div>
        
        <table class="items-table">
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total</th>
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
                    <td>{{ item.quantity }}</td>
                    <td>{{ format_currency(item.rate, invoice.currency_symbol) }}</td>
                    <td>{{ format_currency(item.amount, invoice.currency_symbol) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="totals-section">
            <div class="totals">
                <div class="total-row">
                    <span>Subtotal:</span>
                    <span>{{ format_currency(invoice.subtotal, invoice.currency_symbol) }}</span>
                </div>
                {% if invoice.tax_amount > 0 %}
                <div class="total-row">
                    <span>Tax:</span>
                    <span>{{ format_currency(invoice.tax_amount, invoice.currency_symbol) }}</span>
                </div>
                {% endif %}
                <div class="total-row grand-total">
                    <span>Total:</span>
                    <span>{{ format_currency(invoice.grand_total, invoice.currency_symbol) }}</span>
                </div>
            </div>
        </div>
        
        {% if invoice.notes %}
        <div class="notes-section">
            <h4>Notes:</h4>
            <p>{{ invoice.notes }}</p>
        </div>
        {% endif %}
        
        <div class="footer">
            <div class="generated">Generated on {{ generated_at.strftime('%B %d, %Y') }}</div>
        </div>
    </div>
</body>
</html>"""
    
    def _generate_basic_invoice_css(self) -> str:
        """Generate basic invoice CSS template."""
        return """@page { size: A4; margin: 1.5cm; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 13px; line-height: 1.4; color: #333; }
.invoice-container { max-width: 800px; margin: 0 auto; }
.header-section { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 2px solid #3498db; }
.company-info h1 { font-size: 24px; margin: 10px 0; color: #3498db; }
.logo { max-width: 120px; max-height: 60px; margin-bottom: 10px; }
.address { color: #666; font-size: 12px; }
.invoice-info { text-align: right; }
.invoice-info h2 { font-size: 28px; margin: 0; color: #3498db; }
.invoice-details { margin-top: 10px; font-size: 12px; }
.invoice-details div { margin: 3px 0; }
.client-section { margin-bottom: 30px; }
.client-section h3 { color: #3498db; margin-bottom: 10px; border-bottom: 1px solid #3498db; padding-bottom: 5px; }
.client-name { font-weight: bold; font-size: 16px; margin-bottom: 5px; }
.items-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
.items-table th, .items-table td { padding: 12px 8px; text-align: left; border-bottom: 1px solid #ddd; }
.items-table th { background: #3498db; color: white; font-weight: bold; }
.items-table tbody tr:nth-child(even) { background: #f8f9fa; }
.item-desc { font-weight: 500; }
.item-notes { font-size: 11px; color: #666; font-style: italic; }
.totals-section { display: flex; justify-content: flex-end; margin-bottom: 30px; }
.totals { min-width: 300px; }
.total-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
.total-row.grand-total { font-size: 16px; font-weight: bold; border-top: 2px solid #3498db; border-bottom: 2px solid #3498db; background: #f8f9fa; padding: 12px 0; }
.notes-section { margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-left: 4px solid #3498db; }
.notes-section h4 { margin: 0 0 10px 0; color: #3498db; }
.footer { text-align: center; font-size: 11px; color: #666; border-top: 1px solid #ddd; padding-top: 15px; }"""
    
    def _get_default_invoice_html(self) -> str:
        """Get default invoice HTML template."""
        return self._generate_simple_invoice_html()
    
    def _get_default_invoice_css(self) -> str:
        """Get default invoice CSS template."""
        return self._generate_simple_invoice_css()
    
    # ===== RECEIPT TEMPLATE GENERATORS =====
    
    def _get_classic_receipt_html(self) -> str:
        """Get classic receipt HTML template."""
        template_path = "app/templates/pdf/receipts/classic/template.html"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._get_default_receipt_html()
    
    def _get_classic_receipt_css(self) -> str:
        """Get classic receipt CSS template."""
        template_path = "app/templates/pdf/receipts/classic/style.css"
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._get_default_receipt_css()
    
    def _generate_simple_receipt_html(self) -> str:
        """Generate simple receipt HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Receipt {{ receipt.formatted_receipt_number }}</title>
</head>
<body>
    <div class="receipt-container">
        <div class="header">
            <h1>RECEIPT</h1>
            <div class="receipt-number">{{ receipt.formatted_receipt_number }}</div>
            <div class="receipt-date">{{ format_date(receipt.receipt_date) }}</div>
        </div>
        
        <div class="details">
            <div class="detail-row">
                <span>From:</span>
                <span>{{ receipt.company_name or "Invoice Generator SaaS" }}</span>
            </div>
            <div class="detail-row">
                <span>To:</span>
                <span>{{ receipt.customer_name }}</span>
            </div>
            <div class="detail-row">
                <span>Email:</span>
                <span>{{ receipt.customer_email }}</span>
            </div>
            <div class="detail-row">
                <span>Payment Method:</span>
                <span>{{ receipt.payment_method or 'N/A' }}</span>
            </div>
            {% if receipt.transaction_id %}
            <div class="detail-row">
                <span>Transaction ID:</span>
                <span>{{ receipt.transaction_id }}</span>
            </div>
            {% endif %}
        </div>
        
        <div class="description">
            <h3>Description</h3>
            <div class="desc-text">{{ receipt.title }}</div>
            {% if receipt.description %}
            <div class="desc-details">{{ receipt.description }}</div>
            {% endif %}
        </div>
        
        <div class="amount-section">
            <div class="amount-row">
                <span>Amount:</span>
                <span>{{ format_currency(receipt.amount, receipt.currency_symbol) }}</span>
            </div>
            {% if receipt.tax_amount > 0 %}
            <div class="amount-row">
                <span>Tax:</span>
                <span>{{ format_currency(receipt.tax_amount, receipt.currency_symbol) }}</span>
            </div>
            {% endif %}
            <div class="amount-row total">
                <span>Total Paid:</span>
                <span>{{ format_currency(receipt.total_amount, receipt.currency_symbol) }}</span>
            </div>
        </div>
        
        <div class="footer">
            <div class="thank-you">Thank you for your payment!</div>
            <div class="generated">Generated on {{ format_date(generated_at) }}</div>
        </div>
    </div>
</body>
</html>"""
    
    def _generate_simple_receipt_css(self) -> str:
        """Generate simple receipt CSS template."""
        return """@page { size: A4; margin: 2cm; }
body { font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #333; }
.receipt-container { max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 30px; }
.header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #ddd; }
.header h1 { font-size: 28px; margin: 0; color: #27ae60; }
.receipt-number { font-size: 16px; margin: 10px 0; font-weight: bold; }
.receipt-date { font-size: 14px; color: #666; }
.details { margin-bottom: 25px; }
.detail-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dotted #ccc; }
.detail-row span:first-child { font-weight: bold; color: #555; }
.description { margin-bottom: 25px; }
.description h3 { color: #27ae60; margin-bottom: 10px; border-bottom: 1px solid #27ae60; padding-bottom: 5px; }
.desc-text { font-weight: bold; margin-bottom: 8px; }
.desc-details { color: #666; font-size: 13px; }
.amount-section { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 25px; }
.amount-row { display: flex; justify-content: space-between; padding: 8px 0; }
.amount-row.total { font-size: 18px; font-weight: bold; border-top: 2px solid #27ae60; padding-top: 15px; margin-top: 10px; color: #27ae60; }
.footer { text-align: center; border-top: 1px solid #ddd; padding-top: 20px; }
.thank-you { font-size: 16px; font-weight: bold; color: #27ae60; margin-bottom: 10px; }
.generated { font-size: 12px; color: #666; }"""
    
    def _get_default_receipt_html(self) -> str:
        """Get default receipt HTML template."""
        return self._generate_simple_receipt_html()
    
    def _get_default_receipt_css(self) -> str:
        """Get default receipt CSS template."""
        return self._generate_simple_receipt_css()
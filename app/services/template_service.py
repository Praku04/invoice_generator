"""Template service for managing invoice and receipt templates."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import os
import json
import shutil
from PIL import Image
import io

from app.models.template import Template, TemplateCategory, UserTemplatePreference
from app.models.user import User
from app.models.subscription import Subscription
from app.services.audit_service import AuditService
from app.config import settings


class TemplateService:
    """Service class for template operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.template_base_path = os.path.join("app", "templates", "pdf")
    
    def get_available_templates(
        self, 
        category: TemplateCategory, 
        user_id: int = None,
        include_premium: bool = True
    ) -> List[Template]:
        """Get available templates for a category."""
        
        query = self.db.query(Template).filter(
            Template.category == category,
            Template.is_active == True
        )
        
        # Check user's plan for premium templates
        if user_id and not include_premium:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                subscription = self.db.query(Subscription).filter(
                    Subscription.user_id == user_id,
                    Subscription.status == "active"
                ).first()
                
                # If user doesn't have premium subscription, exclude premium templates
                if not subscription or subscription.plan.price == 0:
                    query = query.filter(Template.is_premium == False)
        
        return query.order_by(Template.sort_order, Template.name).all()
    
    def get_template_by_id(self, template_id: int) -> Optional[Template]:
        """Get template by ID."""
        return self.db.query(Template).filter(Template.id == template_id).first()
    
    def get_template_by_template_id(self, template_id: str) -> Optional[Template]:
        """Get template by template_id string."""
        return self.db.query(Template).filter(Template.template_id == template_id).first()
    
    def get_user_default_template(self, user_id: int, category: TemplateCategory) -> Optional[Template]:
        """Get user's default template for a category."""
        
        preference = self.db.query(UserTemplatePreference).filter(
            UserTemplatePreference.user_id == user_id,
            UserTemplatePreference.category == category
        ).first()
        
        if preference:
            return preference.template
        
        # Return system default template
        return self.get_default_template(category)
    
    def get_default_template(self, category: TemplateCategory) -> Optional[Template]:
        """Get system default template for a category."""
        
        return self.db.query(Template).filter(
            Template.category == category,
            Template.is_active == True,
            Template.is_premium == False
        ).order_by(Template.sort_order).first()
    
    def set_user_default_template(
        self, 
        user_id: int, 
        template_id: int, 
        category: TemplateCategory
    ) -> bool:
        """Set user's default template for a category."""
        
        # Verify template exists and is available
        template = self.get_template_by_id(template_id)
        if not template or not template.is_available or template.category != category:
            return False
        
        # Check if user has access to premium template
        if template.is_premium:
            if not self._user_has_premium_access(user_id):
                return False
        
        # Update or create preference
        preference = self.db.query(UserTemplatePreference).filter(
            UserTemplatePreference.user_id == user_id,
            UserTemplatePreference.category == category
        ).first()
        
        if preference:
            preference.template_id = template_id
        else:
            preference = UserTemplatePreference(
                user_id=user_id,
                template_id=template_id,
                category=category
            )
            self.db.add(preference)
        
        self.db.commit()
        
        # Log audit event
        self.audit_service.log_action(
            action="TEMPLATE_PREFERENCE_UPDATED",
            user_id=user_id,
            description=f"Set default {category.value} template to {template.name}",
            resource_type="template",
            resource_id=template.id,
            metadata={
                "template_id": template.template_id,
                "template_name": template.name,
                "category": category.value
            }
        )
        
        return True
    
    def create_template(
        self,
        template_data: Dict[str, Any],
        html_content: str,
        css_content: str,
        preview_image: bytes = None,
        admin_user_id: int = None
    ) -> Template:
        """Create a new template."""
        
        # Create template directory
        template_dir = os.path.join(
            self.template_base_path,
            template_data['category'] + "s",
            template_data['template_id']
        )
        os.makedirs(template_dir, exist_ok=True)
        
        # Write HTML file
        html_file = "template.html"
        html_path = os.path.join(template_dir, html_file)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Write CSS file
        css_file = "style.css"
        css_path = os.path.join(template_dir, css_file)
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # Save preview image if provided
        preview_file = None
        if preview_image:
            preview_file = "preview.png"
            preview_path = os.path.join(template_dir, preview_file)
            
            # Convert and save image
            image = Image.open(io.BytesIO(preview_image))
            # Resize to standard preview size
            image = image.resize((400, 300), Image.Resampling.LANCZOS)
            image.save(preview_path, "PNG")
        
        # Create template record
        template = Template(
            template_id=template_data['template_id'],
            name=template_data['name'],
            category=TemplateCategory(template_data['category']),
            description=template_data.get('description'),
            version=template_data.get('version', '1.0.0'),
            author=template_data.get('author'),
            html_file=html_file,
            css_file=css_file,
            preview_image=preview_file,
            is_active=template_data.get('is_active', True),
            is_premium=template_data.get('is_premium', False),
            sort_order=template_data.get('sort_order', 0),
            features=json.dumps(template_data.get('features', [])),
            supports_logo=template_data.get('supports_logo', True),
            supports_signature=template_data.get('supports_signature', True),
            supports_watermark=template_data.get('supports_watermark', False),
            page_size=template_data.get('page_size', 'A4'),
            orientation=template_data.get('orientation', 'portrait'),
            margins=template_data.get('margins', '1cm')
        )
        
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        
        # Log audit event
        if admin_user_id:
            self.audit_service.log_admin_action(
                admin_id=admin_user_id,
                action_type="TEMPLATE_MANAGEMENT",
                action_name="Create Template",
                description=f"Created template {template.name}",
                target_resource_type="template",
                target_resource_id=template.id,
                operation_data=template_data
            )
        
        return template
    
    def update_template(
        self,
        template_id: int,
        template_data: Dict[str, Any],
        html_content: str = None,
        css_content: str = None,
        preview_image: bytes = None,
        admin_user_id: int = None
    ) -> Optional[Template]:
        """Update an existing template."""
        
        template = self.get_template_by_id(template_id)
        if not template:
            return None
        
        # Update template files if provided
        if html_content:
            with open(template.html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        if css_content:
            with open(template.css_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
        
        if preview_image:
            preview_path = os.path.join(template.template_path, "preview.png")
            image = Image.open(io.BytesIO(preview_image))
            image = image.resize((400, 300), Image.Resampling.LANCZOS)
            image.save(preview_path, "PNG")
            template.preview_image = "preview.png"
        
        # Update template metadata
        for field, value in template_data.items():
            if hasattr(template, field) and field not in ['id', 'template_id', 'created_at']:
                if field == 'features' and isinstance(value, list):
                    setattr(template, field, json.dumps(value))
                else:
                    setattr(template, field, value)
        
        self.db.commit()
        
        # Log audit event
        if admin_user_id:
            self.audit_service.log_admin_action(
                admin_id=admin_user_id,
                action_type="TEMPLATE_MANAGEMENT",
                action_name="Update Template",
                description=f"Updated template {template.name}",
                target_resource_type="template",
                target_resource_id=template.id,
                operation_data=template_data
            )
        
        return template
    
    def delete_template(self, template_id: int, admin_user_id: int = None) -> bool:
        """Delete a template."""
        
        template = self.get_template_by_id(template_id)
        if not template:
            return False
        
        # Check if template is in use
        if self._template_in_use(template):
            # Just deactivate instead of deleting
            template.is_active = False
            self.db.commit()
            return True
        
        # Remove template files
        template_dir = template.template_path
        if os.path.exists(template_dir):
            shutil.rmtree(template_dir)
        
        # Remove from database
        self.db.delete(template)
        self.db.commit()
        
        # Log audit event
        if admin_user_id:
            self.audit_service.log_admin_action(
                admin_id=admin_user_id,
                action_type="TEMPLATE_MANAGEMENT",
                action_name="Delete Template",
                description=f"Deleted template {template.name}",
                target_resource_type="template",
                target_resource_id=template.id
            )
        
        return True
    
    def get_template_preview_url(self, template: Template) -> Optional[str]:
        """Get URL for template preview image."""
        
        if template.preview_image and os.path.exists(template.preview_path):
            # Return relative URL for serving static files
            return f"/static/templates/{template.category.value}s/{template.template_id}/{template.preview_image}"
        
        return None
    
    def generate_template_preview(self, template: Template, sample_data: Dict[str, Any]) -> str:
        """Generate HTML preview of template with sample data."""
        
        from jinja2 import Environment, FileSystemLoader
        
        # Setup Jinja2 environment
        template_dir = os.path.dirname(template.html_path)
        env = Environment(loader=FileSystemLoader(template_dir))
        
        # Load template
        jinja_template = env.get_template(template.html_file)
        
        # Render with sample data
        html_content = jinja_template.render(**sample_data)
        
        # Add CSS
        css_content = ""
        if os.path.exists(template.css_path):
            with open(template.css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        
        # Combine HTML and CSS
        preview_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                {css_content}
                /* Preview specific styles */
                body {{ 
                    transform: scale(0.8); 
                    transform-origin: top left;
                    width: 125%;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return preview_html
    
    def get_template_gallery_data(self, category: TemplateCategory, user_id: int = None) -> List[Dict[str, Any]]:
        """Get template gallery data for frontend."""
        
        templates = self.get_available_templates(category, user_id)
        gallery_data = []
        
        for template in templates:
            template_data = {
                'id': template.id,
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'is_premium': template.is_premium,
                'features': template.get_features_list(),
                'preview_url': self.get_template_preview_url(template),
                'supports_logo': template.supports_logo,
                'supports_signature': template.supports_signature,
                'supports_watermark': template.supports_watermark
            }
            gallery_data.append(template_data)
        
        return gallery_data
    
    def _user_has_premium_access(self, user_id: int) -> bool:
        """Check if user has access to premium templates."""
        
        subscription = self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()
        
        return subscription and subscription.plan.price > 0
    
    def _template_in_use(self, template: Template) -> bool:
        """Check if template is currently in use."""
        
        if template.category == TemplateCategory.INVOICE:
            from app.models.invoice import Invoice
            return self.db.query(Invoice).filter(Invoice.template_id == template.id).count() > 0
        
        elif template.category == TemplateCategory.RECEIPT:
            from app.models.payment_receipt import PaymentReceipt
            return self.db.query(PaymentReceipt).filter(PaymentReceipt.template_id == template.id).count() > 0
        
        return False
    
    def initialize_default_templates(self):
        """Initialize default templates if none exist."""
        
        # Check if templates already exist
        if self.db.query(Template).count() > 0:
            return
        
        # Create default invoice templates
        self._create_default_invoice_templates()
        
        # Create default receipt templates
        self._create_default_receipt_templates()
    
    def _create_default_invoice_templates(self):
        """Create default invoice templates."""
        
        # Classic Invoice Template
        classic_invoice_data = {
            'template_id': 'classic',
            'name': 'Classic Invoice',
            'category': 'invoice',
            'description': 'Traditional professional invoice template',
            'is_premium': False,
            'sort_order': 1,
            'features': ['Logo support', 'Signature support', 'Tax breakdown', 'Professional layout']
        }
        
        # Modern Invoice Template
        modern_invoice_data = {
            'template_id': 'modern',
            'name': 'Modern Invoice',
            'category': 'invoice',
            'description': 'Clean, modern invoice design',
            'is_premium': True,
            'sort_order': 2,
            'features': ['Modern design', 'Color accents', 'Logo support', 'Signature support']
        }
        
        # Minimal Invoice Template
        minimal_invoice_data = {
            'template_id': 'minimal',
            'name': 'Minimal Invoice',
            'category': 'invoice',
            'description': 'Simple, clean invoice template',
            'is_premium': True,
            'sort_order': 3,
            'features': ['Minimal design', 'Clean typography', 'Logo support']
        }
        
        # Create templates with default HTML/CSS
        for template_data in [classic_invoice_data, modern_invoice_data, minimal_invoice_data]:
            self.create_template(
                template_data=template_data,
                html_content=self._get_default_invoice_html(template_data['template_id']),
                css_content=self._get_default_invoice_css(template_data['template_id'])
            )
    
    def _create_default_receipt_templates(self):
        """Create default receipt templates."""
        
        # Classic Receipt Template
        classic_receipt_data = {
            'template_id': 'classic',
            'name': 'Classic Receipt',
            'category': 'receipt',
            'description': 'Traditional receipt template',
            'is_premium': False,
            'sort_order': 1,
            'features': ['Professional layout', 'Tax breakdown', 'Company branding']
        }
        
        # Horizontal Receipt Template
        horizontal_receipt_data = {
            'template_id': 'horizontal',
            'name': 'Horizontal Receipt',
            'category': 'receipt',
            'description': 'Wide format receipt template',
            'is_premium': True,
            'sort_order': 2,
            'features': ['Horizontal layout', 'Modern design', 'Color accents']
        }
        
        # Compact Receipt Template
        compact_receipt_data = {
            'template_id': 'compact',
            'name': 'Compact Receipt',
            'category': 'receipt',
            'description': 'Space-efficient receipt template',
            'is_premium': True,
            'sort_order': 3,
            'features': ['Compact design', 'Space efficient', 'Clean layout']
        }
        
        # Create templates with default HTML/CSS
        for template_data in [classic_receipt_data, horizontal_receipt_data, compact_receipt_data]:
            self.create_template(
                template_data=template_data,
                html_content=self._get_default_receipt_html(template_data['template_id']),
                css_content=self._get_default_receipt_css(template_data['template_id'])
            )
    
    def _get_default_invoice_html(self, template_id: str) -> str:
        """Get default HTML content for invoice templates."""
        # This will be implemented with actual template content
        return f"<!-- Default {template_id} invoice template HTML -->"
    
    def _get_default_invoice_css(self, template_id: str) -> str:
        """Get default CSS content for invoice templates."""
        # This will be implemented with actual template styles
        return f"/* Default {template_id} invoice template CSS */"
    
    def _get_default_receipt_html(self, template_id: str) -> str:
        """Get default HTML content for receipt templates."""
        # This will be implemented with actual template content
        return f"<!-- Default {template_id} receipt template HTML -->"
    
    def _get_default_receipt_css(self, template_id: str) -> str:
        """Get default CSS content for receipt templates."""
        # This will be implemented with actual template styles
        return f"/* Default {template_id} receipt template CSS */"
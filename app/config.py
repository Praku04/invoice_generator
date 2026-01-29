"""Application configuration settings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://postgres:invoicedb123@localhost:5432/invoicedb"
    
    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    jwt_secret_key: str = "your-jwt-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440  # 24 hours
    
    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_webhook_secret: str = ""
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: str = "noreply@invoicegen.com"
    
    # Application
    app_name: str = "Invoice Generator SaaS"
    app_version: str = "1.0.0"
    app_base_url: str = "http://localhost:8000"
    debug: bool = False
    allowed_hosts: str = "localhost,127.0.0.1"
    
    # File Upload
    max_file_size: int = 5242880  # 5MB
    upload_dir: str = "uploads"
    allowed_extensions: str = "png,jpg,jpeg,svg"
    
    # Subscription
    paid_plan_price: int = 9900  # ₹99 in paise
    free_plan_invoice_limit: int = 3
    
    # PDF
    pdf_timeout: int = 30
    pdf_dpi: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Derived settings
ALLOWED_EXTENSIONS = set(settings.allowed_extensions.split(','))
ALLOWED_HOSTS = set(settings.allowed_hosts.split(','))

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
"""Web interface routes."""

from fastapi import APIRouter, Request, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.database import get_db
from app.core.deps import get_optional_current_user, get_current_active_user
from app.services.user_service import UserService
from app.services.subscription_service import SubscriptionService
from app.services.invoice_service import InvoiceService
from app.models.user import User
from app.models.plan import Plan

router = APIRouter(tags=["Web Interface"])

# Setup templates
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, current_user: Optional[User] = Depends(get_optional_current_user)):
    """Home page."""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    
    return templates.TemplateResponse("pages/home.html", {
        "request": request,
        "title": "Invoice Generator SaaS"
    })


@router.get("/pricing", response_class=HTMLResponse)
def pricing(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Pricing page."""
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    
    return templates.TemplateResponse("pages/pricing.html", {
        "request": request,
        "title": "Pricing",
        "plans": plans,
        "current_user": current_user
    })


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, current_user: Optional[User] = Depends(get_optional_current_user)):
    """Login page."""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "title": "Login"
    })


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, current_user: Optional[User] = Depends(get_optional_current_user)):
    """Register page."""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "title": "Register"
    })


@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, token: str = None):
    """Password reset page."""
    return templates.TemplateResponse("auth/reset_password.html", {
        "request": request,
        "title": "Reset Password",
        "token": token
    })


@router.get("/verify-email", response_class=HTMLResponse)
def verify_email_page(request: Request, token: str = None):
    """Email verification page."""
    return templates.TemplateResponse("auth/verify_email.html", {
        "request": request,
        "title": "Verify Email",
        "token": token
    })


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """User dashboard."""
    subscription_service = SubscriptionService(db)
    invoice_service = InvoiceService(db)
    
    # Get subscription info
    subscription = subscription_service.get_user_subscription(current_user.id)
    can_create, current_count, limit = subscription_service.check_invoice_limit(current_user.id)
    
    # Get recent invoices
    recent_invoices = invoice_service.get_user_invoices(current_user.id, limit=5)
    
    # Calculate stats
    from app.models.invoice import Invoice
    from sqlalchemy import func
    
    total_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.user_id == current_user.id
    ).scalar()
    
    total_revenue = db.query(func.sum(Invoice.grand_total)).filter(
        Invoice.user_id == current_user.id
    ).scalar() or 0
    
    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "title": "Dashboard",
        "current_user": current_user,
        "subscription": subscription,
        "can_create_invoice": can_create,
        "current_invoice_count": current_count,
        "invoice_limit": limit,
        "recent_invoices": recent_invoices,
        "total_invoices": total_invoices,
        "total_revenue": total_revenue
    })


@router.get("/invoices", response_class=HTMLResponse)
def invoices_list(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Invoices list page."""
    invoice_service = InvoiceService(db)
    invoices = invoice_service.get_user_invoices(current_user.id)
    
    return templates.TemplateResponse("invoices/list.html", {
        "request": request,
        "title": "Invoices",
        "current_user": current_user,
        "invoices": invoices
    })


@router.get("/invoices/create", response_class=HTMLResponse)
def create_invoice_page(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create invoice page."""
    subscription_service = SubscriptionService(db)
    can_create, current_count, limit = subscription_service.check_invoice_limit(current_user.id)
    
    if not can_create:
        return templates.TemplateResponse("invoices/limit_exceeded.html", {
            "request": request,
            "title": "Invoice Limit Exceeded",
            "current_user": current_user,
            "current_count": current_count,
            "limit": limit
        })
    
    return templates.TemplateResponse("invoices/create.html", {
        "request": request,
        "title": "Create Invoice",
        "current_user": current_user
    })


@router.get("/invoices/{invoice_id}", response_class=HTMLResponse)
def view_invoice(
    invoice_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """View invoice page."""
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_id(invoice_id, current_user.id)
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return templates.TemplateResponse("invoices/view.html", {
        "request": request,
        "title": f"Invoice {invoice.invoice_number}",
        "current_user": current_user,
        "invoice": invoice
    })


@router.get("/settings", response_class=HTMLResponse)
def settings_page(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Settings page."""
    return templates.TemplateResponse("settings/index.html", {
        "request": request,
        "title": "Settings",
        "current_user": current_user
    })


@router.get("/subscription", response_class=HTMLResponse)
def subscription_page(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Subscription management page."""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_user_subscription(current_user.id)
    
    return templates.TemplateResponse("subscription/index.html", {
        "request": request,
        "title": "Subscription",
        "current_user": current_user,
        "subscription": subscription
    })


# Legal pages
@router.get("/terms", response_class=HTMLResponse)
def terms_of_service(request: Request):
    """Terms of Service page."""
    return templates.TemplateResponse("legal/terms.html", {
        "request": request,
        "title": "Terms of Service"
    })


@router.get("/privacy", response_class=HTMLResponse)
def privacy_policy(request: Request):
    """Privacy Policy page."""
    return templates.TemplateResponse("legal/privacy.html", {
        "request": request,
        "title": "Privacy Policy"
    })


@router.get("/refund", response_class=HTMLResponse)
def refund_policy(request: Request):
    """Refund Policy page."""
    return templates.TemplateResponse("legal/refund.html", {
        "request": request,
        "title": "Refund Policy"
    })


@router.get("/about", response_class=HTMLResponse)
def about_page(request: Request):
    """About page."""
    return templates.TemplateResponse("pages/about.html", {
        "request": request,
        "title": "About Us"
    })


@router.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request):
    """Contact page."""
    return templates.TemplateResponse("pages/contact.html", {
        "request": request,
        "title": "Contact Us"
    })
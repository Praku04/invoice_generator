"""Invoice management API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse
from app.services.invoice_service import InvoiceService
from app.services.pdf_service import PDFService
from app.services.subscription_service import SubscriptionService
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new invoice."""
    invoice_service = InvoiceService(db)
    
    try:
        invoice = invoice_service.create_invoice(current_user.id, invoice_data)
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[InvoiceListResponse])
def get_invoices(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all invoices for current user."""
    invoice_service = InvoiceService(db)
    invoices = invoice_service.get_user_invoices(current_user.id, skip=skip, limit=limit)
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get invoice by ID."""
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_id(invoice_id, current_user.id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an invoice."""
    invoice_service = InvoiceService(db)
    
    try:
        invoice = invoice_service.update_invoice(invoice_id, current_user.id, invoice_data)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an invoice."""
    invoice_service = InvoiceService(db)
    
    try:
        if not invoice_service.delete_invoice(invoice_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        return {"message": "Invoice deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{invoice_id}/finalize")
def finalize_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Finalize an invoice."""
    invoice_service = InvoiceService(db)
    
    try:
        if not invoice_service.finalize_invoice(invoice_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        return {"message": "Invoice finalized successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download invoice as PDF."""
    # Check subscription for PDF access
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_user_subscription(current_user.id)
    
    if not subscription or subscription.plan.price == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="PDF download requires paid subscription"
        )
    
    # Get invoice
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_id(invoice_id, current_user.id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Generate PDF if not exists
    pdf_service = PDFService(db)
    pdf_path = invoice.pdf_file_path
    
    if not pdf_path or not os.path.exists(pdf_path):
        pdf_path = pdf_service.generate_invoice_pdf(invoice_id, current_user.id)
        
        if not pdf_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF"
            )
    
    # Return PDF file
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"invoice_{invoice.invoice_number}.pdf"
    )


@router.get("/{invoice_id}/preview")
def preview_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get invoice preview data."""
    invoice_service = InvoiceService(db)
    invoice = invoice_service.get_invoice_by_id(invoice_id, current_user.id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Return invoice data for preview
    return {
        "invoice": invoice,
        "can_download_pdf": True  # Check subscription in frontend
    }
"""Payment receipt API endpoints."""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User
from app.models.payment_receipt import PaymentReceipt, ReceiptStatus, ReceiptType
from app.models.secure_download_token import SecureDownloadToken
from app.services.payment_receipt_service import PaymentReceiptService
from app.services.audit_service import AuditService
from app.schemas.payment_receipt import (
    PaymentReceiptResponse,
    PaymentReceiptCreate,
    PaymentReceiptUpdate,
    PaymentReceiptListResponse,
    PaymentReceiptStatsResponse,
    AdminReceiptReviewRequest,
    ReceiptEmailRequest,
    ReceiptDownloadResponse
)

router = APIRouter()


@router.get("/", response_model=PaymentReceiptListResponse)
def get_user_receipts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    receipt_type: Optional[ReceiptType] = Query(None),
    status: Optional[ReceiptStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment receipts for the current user."""
    
    receipt_service = PaymentReceiptService(db)
    
    receipts = receipt_service.get_user_receipts(
        user_id=current_user.id,
        limit=limit,
        offset=skip,
        receipt_type=receipt_type,
        status=status
    )
    
    return PaymentReceiptListResponse(
        receipts=[PaymentReceiptResponse.from_orm(r) for r in receipts],
        total_count=len(receipts),
        has_more=len(receipts) == limit
    )


@router.get("/{receipt_id}", response_model=PaymentReceiptResponse)
def get_receipt(
    receipt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific payment receipt."""
    
    receipt_service = PaymentReceiptService(db)
    receipt = receipt_service.get_receipt_by_id(receipt_id, current_user.id)
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Mark as viewed if not already
    if receipt.status in [ReceiptStatus.SENT, ReceiptStatus.GENERATED]:
        receipt.mark_as_viewed()
        db.commit()
    
    return PaymentReceiptResponse.from_orm(receipt)


@router.post("/", response_model=PaymentReceiptResponse)
def create_receipt(
    receipt_data: PaymentReceiptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payment receipt (for invoice payments)."""
    
    receipt_service = PaymentReceiptService(db)
    
    # For invoice payments, create receipt from invoice
    if receipt_data.invoice_id:
        payment_details = {
            'method': receipt_data.payment_method,
            'transaction_id': receipt_data.transaction_id,
            'payment_date': receipt_data.payment_date
        }
        
        receipt = receipt_service.create_receipt_from_invoice_payment(
            invoice_id=receipt_data.invoice_id,
            payment_details=payment_details,
            created_by_user_id=current_user.id
        )
    else:
        raise HTTPException(
            status_code=400, 
            detail="Manual receipt creation not supported. Use payment or invoice endpoints."
        )
    
    return PaymentReceiptResponse.from_orm(receipt)


@router.put("/{receipt_id}", response_model=PaymentReceiptResponse)
def update_receipt(
    receipt_id: int,
    receipt_data: PaymentReceiptUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a payment receipt (only draft receipts)."""
    
    receipt_service = PaymentReceiptService(db)
    
    receipt = receipt_service.update_receipt(
        receipt_id=receipt_id,
        receipt_data=receipt_data,
        user_id=current_user.id
    )
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return PaymentReceiptResponse.from_orm(receipt)


@router.post("/{receipt_id}/generate-pdf")
def generate_receipt_pdf(
    receipt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate PDF for a payment receipt."""
    
    receipt_service = PaymentReceiptService(db)
    
    try:
        pdf_path = receipt_service.generate_receipt_pdf(receipt_id, current_user.id)
        
        return {
            "message": "PDF generated successfully",
            "pdf_generated": True,
            "receipt_id": receipt_id
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate PDF")


@router.post("/{receipt_id}/send-email")
def send_receipt_email(
    receipt_id: int,
    email_request: ReceiptEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send receipt via email."""
    
    receipt_service = PaymentReceiptService(db)
    
    try:
        success = receipt_service.send_receipt_email(
            receipt_id=receipt_id,
            to_email=email_request.to_email,
            user_id=current_user.id
        )
        
        if success:
            return {
                "message": "Receipt sent successfully",
                "email_sent": True,
                "receipt_id": receipt_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{receipt_id}/download-url", response_model=ReceiptDownloadResponse)
def get_receipt_download_url(
    receipt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get secure download URL for receipt PDF."""
    
    receipt_service = PaymentReceiptService(db)
    receipt = receipt_service.get_receipt_by_id(receipt_id, current_user.id)
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Generate PDF if not already generated
    if not receipt.is_pdf_available:
        receipt_service.generate_receipt_pdf(receipt_id, current_user.id)
        db.refresh(receipt)
    
    # Generate secure download token
    download_token = receipt_service._generate_secure_download_token(
        current_user.id, 
        receipt_id=receipt.id
    )
    
    download_url = f"/api/receipts/download/{download_token.token_plain}"
    
    return ReceiptDownloadResponse(
        download_url=download_url,
        expires_at=download_token.expires_at,
        max_downloads=download_token.max_downloads,
        current_downloads=download_token.download_count
    )


@router.get("/download/{token}")
def download_receipt_pdf(
    token: str,
    db: Session = Depends(get_db)
):
    """Download receipt PDF using secure token."""
    
    # Find and validate token
    download_token = db.query(SecureDownloadToken).filter(
        SecureDownloadToken.token_plain == token
    ).first()
    
    if not download_token or not download_token.is_valid:
        raise HTTPException(status_code=404, detail="Invalid or expired download link")
    
    # Get receipt
    if not download_token.receipt_id:
        raise HTTPException(status_code=404, detail="Invalid download link")
    
    receipt = db.query(PaymentReceipt).filter(
        PaymentReceipt.id == download_token.receipt_id
    ).first()
    
    if not receipt or not receipt.is_pdf_available:
        raise HTTPException(status_code=404, detail="Receipt PDF not found")
    
    # Record download
    download_token.record_download()
    db.commit()
    
    # Log audit event
    audit_service = AuditService(db)
    audit_service.log_action(
        action="RECEIPT_PDF_DOWNLOADED",
        user_id=download_token.user_id,
        description=f"Downloaded receipt PDF {receipt.receipt_number}",
        resource_type="receipt",
        resource_id=receipt.id,
        metadata={
            "receipt_number": receipt.receipt_number,
            "download_token": token[:20] + "..."
        }
    )
    
    # Return file
    return FileResponse(
        path=receipt.pdf_file_path,
        filename=f"receipt_{receipt.receipt_number}.pdf",
        media_type="application/pdf"
    )


# Admin endpoints
@router.get("/admin/all", response_model=PaymentReceiptListResponse)
def get_all_receipts_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    receipt_type: Optional[ReceiptType] = Query(None),
    status: Optional[ReceiptStatus] = Query(None),
    user_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all payment receipts for admin management."""
    
    receipt_service = PaymentReceiptService(db)
    
    receipts = receipt_service.get_all_receipts_for_admin(
        limit=limit,
        offset=skip,
        receipt_type=receipt_type,
        status=status,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to
    )
    
    return PaymentReceiptListResponse(
        receipts=[PaymentReceiptResponse.from_orm(r) for r in receipts],
        total_count=len(receipts),
        has_more=len(receipts) == limit
    )


@router.get("/admin/{receipt_id}", response_model=PaymentReceiptResponse)
def get_receipt_admin(
    receipt_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get a specific payment receipt (admin access)."""
    
    receipt_service = PaymentReceiptService(db)
    receipt = receipt_service.get_receipt_by_id(receipt_id)
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return PaymentReceiptResponse.from_orm(receipt)


@router.put("/admin/{receipt_id}/review", response_model=PaymentReceiptResponse)
def admin_review_receipt(
    receipt_id: int,
    review_request: AdminReceiptReviewRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Admin review of payment receipt."""
    
    receipt_service = PaymentReceiptService(db)
    
    receipt = receipt_service.admin_review_receipt(
        receipt_id=receipt_id,
        admin_user_id=current_admin.id,
        notes=review_request.notes,
        approved=review_request.approved
    )
    
    return PaymentReceiptResponse.from_orm(receipt)


@router.delete("/admin/{receipt_id}")
def delete_receipt_admin(
    receipt_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a payment receipt (admin only)."""
    
    receipt_service = PaymentReceiptService(db)
    
    success = receipt_service.delete_receipt(receipt_id, current_admin.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return {"message": "Receipt deleted successfully"}


@router.get("/admin/stats", response_model=PaymentReceiptStatsResponse)
def get_receipt_stats_admin(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get payment receipt statistics for admin dashboard."""
    
    # Get basic stats
    total_receipts = db.query(PaymentReceipt).count()
    
    # Get receipts by type
    receipts_by_type = {}
    for receipt_type in ReceiptType:
        count = db.query(PaymentReceipt).filter(
            PaymentReceipt.receipt_type == receipt_type
        ).count()
        receipts_by_type[receipt_type.value] = count
    
    # Get receipts by status
    receipts_by_status = {}
    for status in ReceiptStatus:
        count = db.query(PaymentReceipt).filter(
            PaymentReceipt.status == status
        ).count()
        receipts_by_status[status.value] = count
    
    # Get total amount
    total_amount = db.query(
        db.func.sum(PaymentReceipt.total_amount)
    ).scalar() or 0
    
    # Get recent receipts
    recent_receipts = db.query(PaymentReceipt).order_by(
        PaymentReceipt.created_at.desc()
    ).limit(10).all()
    
    return PaymentReceiptStatsResponse(
        total_receipts=total_receipts,
        receipts_by_type=receipts_by_type,
        receipts_by_status=receipts_by_status,
        total_amount=total_amount,
        recent_receipts=[PaymentReceiptResponse.from_orm(r) for r in recent_receipts]
    )
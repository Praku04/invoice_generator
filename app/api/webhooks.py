"""Razorpay webhook API routes."""

import json
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.razorpay_event import RazorpayEvent
from app.services.subscription_service import SubscriptionService
from app.config import settings

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/razorpay")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Razorpay webhook events."""
    # Get request body and signature
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")
    
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature"
        )
    
    # Verify webhook signature
    if not _verify_webhook_signature(body, signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    
    # Parse webhook payload
    try:
        payload = json.loads(body.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    # Extract event data
    event_id = payload.get("event")
    event_type = payload.get("event")
    
    if not event_id or not event_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing event data"
        )
    
    # Check if event already processed
    existing_event = db.query(RazorpayEvent).filter(
        RazorpayEvent.event_id == event_id
    ).first()
    
    if existing_event:
        return {"status": "already_processed"}
    
    # Store webhook event
    webhook_event = RazorpayEvent(
        event_id=event_id,
        event_type=event_type,
        payload=body.decode('utf-8'),
        signature=signature
    )
    
    db.add(webhook_event)
    db.commit()
    
    # Process event
    try:
        _process_webhook_event(payload, db)
        webhook_event.processed = True
        webhook_event.processed_at = db.func.now()
    except Exception as e:
        webhook_event.processing_error = str(e)
        webhook_event.processing_attempts += 1
    
    db.commit()
    
    return {"status": "processed"}


def _verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Verify Razorpay webhook signature."""
    if not settings.razorpay_webhook_secret:
        return True  # Skip verification if secret not configured
    
    expected_signature = hmac.new(
        settings.razorpay_webhook_secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def _process_webhook_event(payload: dict, db: Session) -> None:
    """Process Razorpay webhook event."""
    event_type = payload.get("event")
    entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    
    subscription_service = SubscriptionService(db)
    
    if event_type == "payment.authorized":
        # Payment successful
        payment_id = entity.get("id")
        subscription_id = entity.get("notes", {}).get("razorpay_subscription_id")
        
        if payment_id and subscription_id:
            subscription_service.process_payment_success(payment_id, subscription_id)
    
    elif event_type == "payment.failed":
        # Payment failed
        payment_id = entity.get("id")
        subscription_id = entity.get("notes", {}).get("razorpay_subscription_id")
        
        if payment_id and subscription_id:
            subscription_service.process_payment_failure(payment_id, subscription_id)
    
    elif event_type == "subscription.activated":
        # Subscription activated
        subscription_id = entity.get("id")
        if subscription_id:
            # Find and activate subscription
            subscription = db.query(Subscription).filter(
                Subscription.razorpay_subscription_id == subscription_id
            ).first()
            if subscription:
                subscription_service.activate_subscription(subscription.id)
    
    elif event_type == "subscription.cancelled":
        # Subscription cancelled
        subscription_id = entity.get("id")
        if subscription_id:
            # Find and cancel subscription
            subscription = db.query(Subscription).filter(
                Subscription.razorpay_subscription_id == subscription_id
            ).first()
            if subscription:
                subscription_service.cancel_subscription(subscription.id)
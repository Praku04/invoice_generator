"""Subscription management API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.subscription import SubscriptionResponse, SubscriptionCreate
from app.schemas.plan import PlanResponse
from app.services.subscription_service import SubscriptionService
from app.core.deps import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.plan import Plan

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=List[PlanResponse])
def get_available_plans(db: Session = Depends(get_db)):
    """Get all available subscription plans."""
    plans = db.query(Plan).filter(Plan.is_active == True).all()
    return plans


@router.get("/my-subscription", response_model=SubscriptionResponse)
def get_my_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription."""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_user_subscription(current_user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription


@router.post("/subscribe", response_model=SubscriptionResponse)
def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new subscription."""
    subscription_service = SubscriptionService(db)
    
    try:
        subscription = subscription_service.create_subscription(
            current_user.id,
            subscription_data.plan_id
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create subscription"
            )
        
        return subscription
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/cancel/{subscription_id}")
def cancel_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a subscription."""
    subscription_service = SubscriptionService(db)
    
    # Verify subscription belongs to current user
    subscription = subscription_service.get_subscription_by_id(subscription_id)
    if not subscription or subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    if not subscription_service.cancel_subscription(subscription_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel subscription"
        )
    
    return {"message": "Subscription cancelled successfully"}


@router.get("/usage")
def get_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current usage statistics."""
    subscription_service = SubscriptionService(db)
    can_create, current_count, limit = subscription_service.check_invoice_limit(current_user.id)
    
    return {
        "current_invoices": current_count,
        "invoice_limit": limit if limit != -1 else None,
        "can_create_invoice": can_create,
        "unlimited": limit == -1
    }


@router.get("/", response_model=List[SubscriptionResponse])
def get_all_subscriptions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all subscriptions (admin only)."""
    subscription_service = SubscriptionService(db)
    return subscription_service.get_all_subscriptions(skip=skip, limit=limit)
"""Subscription service for managing user subscriptions."""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import razorpay

from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.payment import Payment, PaymentStatus
from app.config import settings


class SubscriptionService:
    """Service class for subscription operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.razorpay_client = razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        ) if settings.razorpay_key_id else None
    
    def get_user_subscription(self, user_id: int) -> Optional[Subscription]:
        """Get active subscription for user."""
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
    
    def get_subscription_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID."""
        return self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
    
    def create_subscription(self, user_id: int, plan_id: int) -> Optional[Subscription]:
        """Create a new subscription."""
        # Check if user already has an active subscription
        existing_subscription = self.get_user_subscription(user_id)
        if existing_subscription:
            # Cancel existing subscription
            self.cancel_subscription(existing_subscription.id)
        
        # Get plan
        plan = self.db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            return None
        
        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            status=SubscriptionStatus.PENDING,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        # Create Razorpay subscription if it's a paid plan
        if plan.price > 0 and self.razorpay_client:
            try:
                razorpay_subscription = self.razorpay_client.subscription.create({
                    "plan_id": plan.razorpay_plan_id,
                    "customer_notify": 1,
                    "total_count": 12,  # 12 months
                    "notes": {
                        "subscription_id": subscription.id,
                        "user_id": user_id
                    }
                })
                
                subscription.razorpay_subscription_id = razorpay_subscription["id"]
                self.db.commit()
                
            except Exception as e:
                # Handle Razorpay error
                subscription.status = SubscriptionStatus.INACTIVE
                self.db.commit()
                return None
        else:
            # Free plan - activate immediately
            subscription.status = SubscriptionStatus.ACTIVE
            self.db.commit()
        
        return subscription
    
    def cancel_subscription(self, subscription_id: int) -> bool:
        """Cancel a subscription."""
        subscription = self.get_subscription_by_id(subscription_id)
        if not subscription:
            return False
        
        # Cancel Razorpay subscription if exists
        if subscription.razorpay_subscription_id and self.razorpay_client:
            try:
                self.razorpay_client.subscription.cancel(subscription.razorpay_subscription_id)
            except Exception:
                pass  # Continue with local cancellation even if Razorpay fails
        
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.cancelled_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def activate_subscription(self, subscription_id: int) -> bool:
        """Activate a subscription."""
        subscription = self.get_subscription_by_id(subscription_id)
        if not subscription:
            return False
        
        subscription.status = SubscriptionStatus.ACTIVE
        self.db.commit()
        return True
    
    def check_invoice_limit(self, user_id: int) -> tuple[bool, int, int]:
        """Check if user can create more invoices.
        
        Returns:
            (can_create, current_count, limit)
        """
        subscription = self.get_user_subscription(user_id)
        if not subscription or not subscription.plan:
            return False, 0, 0
        
        # Get current invoice count for this month (not subscription period)
        from app.models.invoice import Invoice, InvoiceStatus
        from datetime import datetime, timezone
        
        # Calculate start of current month
        now = datetime.now(timezone.utc)
        month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        
        current_count = self.db.query(Invoice).filter(
            Invoice.user_id == user_id,
            Invoice.status != InvoiceStatus.DRAFT,
            Invoice.created_at >= month_start
        ).count()
        
        limit = subscription.plan.invoice_limit
        if limit is None:  # Unlimited
            return True, current_count, -1
        
        return current_count < limit, current_count, limit
    
    def get_all_subscriptions(self, skip: int = 0, limit: int = 100) -> List[Subscription]:
        """Get all subscriptions (admin only)."""
        return self.db.query(Subscription).offset(skip).limit(limit).all()
    
    def process_payment_success(self, razorpay_payment_id: str, razorpay_subscription_id: str) -> bool:
        """Process successful payment."""
        # Find subscription
        subscription = self.db.query(Subscription).filter(
            Subscription.razorpay_subscription_id == razorpay_subscription_id
        ).first()
        
        if not subscription:
            return False
        
        # Activate subscription
        subscription.status = SubscriptionStatus.ACTIVE
        
        # Create payment record
        payment = Payment(
            subscription_id=subscription.id,
            razorpay_payment_id=razorpay_payment_id,
            amount=subscription.plan.price / 100,  # Convert from paise
            currency="INR",
            status=PaymentStatus.SUCCESS,
            payment_date=datetime.utcnow()
        )
        
        self.db.add(payment)
        self.db.commit()
        
        return True
    
    def process_payment_failure(self, razorpay_payment_id: str, razorpay_subscription_id: str) -> bool:
        """Process failed payment."""
        # Find subscription
        subscription = self.db.query(Subscription).filter(
            Subscription.razorpay_subscription_id == razorpay_subscription_id
        ).first()
        
        if not subscription:
            return False
        
        # Create payment record
        payment = Payment(
            subscription_id=subscription.id,
            razorpay_payment_id=razorpay_payment_id,
            amount=subscription.plan.price / 100,  # Convert from paise
            currency="INR",
            status=PaymentStatus.FAILED,
            payment_date=datetime.utcnow()
        )
        
        self.db.add(payment)
        self.db.commit()
        
        return True
    
    def handle_successful_payment(self, payment_id: int) -> bool:
        """Handle successful payment and create receipt."""
        from app.services.payment_receipt_service import PaymentReceiptService
        
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment or payment.status != PaymentStatus.SUCCESS:
            return False
        
        try:
            # Create payment receipt
            receipt_service = PaymentReceiptService(self.db)
            receipt = receipt_service.create_receipt_from_payment(payment_id)
            
            # Generate PDF automatically
            receipt_service.generate_receipt_pdf(receipt.id)
            
            # Send email notification
            receipt_service.send_receipt_email(receipt.id)
            
            return True
            
        except Exception as e:
            print(f"Error handling successful payment {payment_id}: {e}")
            return False
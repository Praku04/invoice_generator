"""User service for user management operations."""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User, UserRole
from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, generate_verification_token, generate_reset_token


class UserService:
    """Service class for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        hashed_password = get_password_hash(user_data.password)
        verification_token = generate_verification_token()
        
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            verification_token=verification_token,
            is_verified=False  # Require email verification
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Create free subscription for new user
        self._create_free_subscription(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_verification_token(self, token: str) -> Optional[User]:
        """Get user by verification token."""
        return self.db.query(User).filter(User.verification_token == token).first()
    
    def get_user_by_reset_token(self, token: str) -> Optional[User]:
        """Get user by reset token."""
        return self.db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def verify_email(self, token: str) -> bool:
        """Verify user email with token."""
        user = self.get_user_by_verification_token(token)
        if not user:
            return False
        
        user.is_verified = True
        user.verification_token = None
        self.db.commit()
        return True
    
    def request_password_reset(self, email: str) -> Optional[str]:
        """Request password reset for user."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        reset_token = generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        
        self.db.commit()
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password with token."""
        user = self.get_user_by_reset_token(token)
        if not user:
            return False
        
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        
        self.db.commit()
        return True
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users (admin only)."""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True
    
    def _create_free_subscription(self, user: User) -> None:
        """Create free subscription for new user."""
        # Get free plan
        free_plan = self.db.query(Plan).filter(Plan.name == "Free").first()
        if not free_plan:
            # Create free plan if it doesn't exist
            free_plan = Plan(
                name="Free",
                description="Free plan with limited features",
                price=0,
                currency="INR",
                interval="monthly",
                invoice_limit=3,
                features='["Basic invoicing", "3 invoices per month"]',
                is_active=True
            )
            self.db.add(free_plan)
            self.db.commit()
            self.db.refresh(free_plan)
        
        # Create subscription
        subscription = Subscription(
            user_id=user.id,
            plan_id=free_plan.id,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=365)  # Free plan never expires
        )
        
        self.db.add(subscription)
        self.db.commit()
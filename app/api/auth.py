"""Authentication API routes."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, PasswordReset, PasswordResetConfirm, EmailVerification
from app.schemas.auth import Token
from app.services.user_service import UserService
from app.core.security import create_access_token, validate_password_strength
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Validate password strength
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, and digit"
        )
    
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(user_data)
        
        # Send welcome and verification emails
        from app.services.email_service import EmailService
        email_service = EmailService(db)
        
        try:
            # Send welcome email
            email_service.send_welcome_email(user)
            
            # Send email verification
            if user.verification_token:
                email_service.send_email_verification(user, user.verification_token)
        except Exception as e:
            # Don't fail registration if email fails
            print(f"Failed to send emails: {e}")
        
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user_service = UserService(db)
    user = user_service.authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expire_minutes * 60
    }


@router.post("/verify-email")
def verify_email(verification_data: EmailVerification, db: Session = Depends(get_db)):
    """Verify user email with token."""
    user_service = UserService(db)
    
    if not user_service.verify_email(verification_data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
def forgot_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """Request password reset."""
    user_service = UserService(db)
    user = user_service.get_user_by_email(reset_data.email)
    
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset link has been sent"}
    
    reset_token = user_service.request_password_reset(reset_data.email)
    
    if reset_token:
        # Send password reset email
        from app.services.email_service import EmailService
        email_service = EmailService(db)
        
        try:
            email_service.send_password_reset_email(user, reset_token)
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            # For now, return the token in the response for testing
            return {
                "message": "Password reset requested",
                "reset_token": reset_token,  # Remove this in production
                "note": "Email not configured. Use this token for testing."
            }
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
def reset_password(reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token."""
    # Validate password strength
    if not validate_password_strength(reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, and digit"
        )
    
    user_service = UserService(db)
    
    if not user_service.reset_password(reset_data.token, reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}
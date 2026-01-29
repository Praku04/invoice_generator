"""Settings management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.company_profile import CompanyProfileCreate, CompanyProfileUpdate, CompanyProfileResponse
from app.schemas.invoice_settings import InvoiceSettingsCreate, InvoiceSettingsUpdate, InvoiceSettingsResponse
from app.models.company_profile import CompanyProfile
from app.models.invoice_settings import InvoiceSettings
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/company", response_model=CompanyProfileResponse)
def get_company_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get company profile."""
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )
    
    return profile


@router.post("/company", response_model=CompanyProfileResponse, status_code=status.HTTP_201_CREATED)
def create_company_profile(
    profile_data: CompanyProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create company profile."""
    # Check if profile already exists
    existing_profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == current_user.id
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile already exists"
        )
    
    profile = CompanyProfile(
        user_id=current_user.id,
        **profile_data.dict()
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile


@router.put("/company", response_model=CompanyProfileResponse)
def update_company_profile(
    profile_data: CompanyProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update company profile."""
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )
    
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.get("/invoice", response_model=InvoiceSettingsResponse)
def get_invoice_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get invoice settings."""
    settings = db.query(InvoiceSettings).filter(
        InvoiceSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        # Create default settings
        settings = InvoiceSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings


@router.put("/invoice", response_model=InvoiceSettingsResponse)
def update_invoice_settings(
    settings_data: InvoiceSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update invoice settings."""
    settings = db.query(InvoiceSettings).filter(
        InvoiceSettings.user_id == current_user.id
    ).first()
    
    if not settings:
        settings = InvoiceSettings(user_id=current_user.id)
        db.add(settings)
        db.flush()
    
    update_data = settings_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    db.commit()
    db.refresh(settings)
    
    return settings


@router.post("/company/logo/{file_id}")
def set_company_logo(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set company logo."""
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )
    
    # Verify file belongs to user
    from app.models.file_asset import FileAsset
    file_asset = db.query(FileAsset).filter(
        FileAsset.id == file_id,
        FileAsset.user_id == current_user.id,
        FileAsset.file_type == "logo"
    ).first()
    
    if not file_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logo file not found"
        )
    
    profile.logo_file_id = file_id
    db.commit()
    
    return {"message": "Logo updated successfully"}


@router.post("/company/stamp/{file_id}")
def set_company_stamp(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set company stamp."""
    profile = db.query(CompanyProfile).filter(
        CompanyProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )
    
    # Verify file belongs to user
    from app.models.file_asset import FileAsset
    file_asset = db.query(FileAsset).filter(
        FileAsset.id == file_id,
        FileAsset.user_id == current_user.id,
        FileAsset.file_type == "stamp"
    ).first()
    
    if not file_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stamp file not found"
        )
    
    profile.stamp_file_id = file_id
    db.commit()
    
    return {"message": "Stamp updated successfully"}
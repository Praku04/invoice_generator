"""File upload and management API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.schemas.file_asset import FileAssetResponse
from app.services.file_service import FileService
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload/{file_type}", response_model=FileAssetResponse)
def upload_file(
    file_type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a file (logo, stamp, etc.)."""
    # Validate file type
    allowed_types = ["logo", "stamp", "document"]
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    file_service = FileService(db)
    
    try:
        file_asset = file_service.upload_file(current_user.id, file, file_type)
        return file_asset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.get("/", response_model=List[FileAssetResponse])
def get_user_files(
    file_type: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all files for current user."""
    file_service = FileService(db)
    files = file_service.get_user_files(current_user.id, file_type)
    return files


@router.get("/{file_id}", response_model=FileAssetResponse)
def get_file_info(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get file information."""
    file_service = FileService(db)
    file_asset = file_service.get_file_by_id(file_id, current_user.id)
    
    if not file_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return file_asset


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download a file."""
    file_service = FileService(db)
    file_asset = file_service.get_file_by_id(file_id, current_user.id)
    
    if not file_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if not os.path.exists(file_asset.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    return FileResponse(
        file_asset.file_path,
        media_type=file_asset.mime_type,
        filename=file_asset.original_filename
    )


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a file."""
    file_service = FileService(db)
    
    if not file_service.delete_file(file_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {"message": "File deleted successfully"}
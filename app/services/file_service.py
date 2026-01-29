"""File upload and management service."""

import os
import uuid
from typing import Optional, List
from PIL import Image
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.file_asset import FileAsset
from app.config import settings, ALLOWED_EXTENSIONS


class FileService:
    """Service class for file operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def upload_file(self, user_id: int, file: UploadFile, file_type: str) -> FileAsset:
        """Upload and save a file."""
        # Validate file
        self._validate_file(file)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Create file path
        file_dir = os.path.join(settings.upload_dir, file_type)
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(file_dir, unique_filename)
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        # Get image dimensions if it's an image
        width, height = None, None
        if file_extension in ['png', 'jpg', 'jpeg']:
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
            except Exception:
                pass  # Not a valid image or couldn't read dimensions
        
        # Create file asset record
        file_asset = FileAsset(
            user_id=user_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content),
            mime_type=file.content_type or 'application/octet-stream',
            file_extension=file_extension,
            file_type=file_type,
            width=width,
            height=height
        )
        
        self.db.add(file_asset)
        self.db.commit()
        self.db.refresh(file_asset)
        
        return file_asset
    
    def get_user_files(self, user_id: int, file_type: Optional[str] = None) -> List[FileAsset]:
        """Get all files for a user."""
        query = self.db.query(FileAsset).filter(
            FileAsset.user_id == user_id,
            FileAsset.is_active == True
        )
        
        if file_type:
            query = query.filter(FileAsset.file_type == file_type)
        
        return query.order_by(FileAsset.created_at.desc()).all()
    
    def get_file_by_id(self, file_id: int, user_id: int) -> Optional[FileAsset]:
        """Get file by ID for specific user."""
        return self.db.query(FileAsset).filter(
            FileAsset.id == file_id,
            FileAsset.user_id == user_id,
            FileAsset.is_active == True
        ).first()
    
    def delete_file(self, file_id: int, user_id: int) -> bool:
        """Delete a file."""
        file_asset = self.get_file_by_id(file_id, user_id)
        if not file_asset:
            return False
        
        # Delete physical file
        try:
            if os.path.exists(file_asset.file_path):
                os.remove(file_asset.file_path)
        except Exception:
            pass  # Continue even if file deletion fails
        
        # Mark as inactive
        file_asset.is_active = False
        self.db.commit()
        
        return True
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        # Validate image files
        if file_extension in ['png', 'jpg', 'jpeg']:
            try:
                # Read a small portion to validate it's a valid image
                content = file.file.read(1024)
                file.file.seek(0)
                
                # Basic image validation
                if not content.startswith(b'\xff\xd8') and not content.startswith(b'\x89PNG'):
                    raise HTTPException(status_code=400, detail="Invalid image file")
                    
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid image file")
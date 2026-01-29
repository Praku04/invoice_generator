"""Authentication schemas."""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data schema for JWT payload."""
    user_id: Optional[int] = None
    email: Optional[str] = None
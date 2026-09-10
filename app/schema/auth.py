"""
Authentication Schemas for Pydantic validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class SignUpRequest(BaseModel):
    """Schema for user signup"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    class Config:
        from_attribute = True


class LoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

    class Config:
        from_attribute = True


class ResetPasswordRequest(BaseModel):
    """Schema for password reset"""
    email: EmailStr
    old_password: str
    new_password: str = Field(..., min_length=8)

    class Config:
        from_attribute = True


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password (sends reset link)"""
    email: EmailStr

    class Config:
        from_attribute = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attribute = True


class ProfileRequest(BaseModel):
    """Schema for creating/updating profile"""
    business_name: str = Field(..., min_length=2, max_length=255)
    company_id: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None

    class Config:
        from_attribute = True


class ProfileResponse(BaseModel):
    """Schema for profile response"""
    id: str
    user_id: str
    business_name: str
    company_id: str
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attribute = True


class UserWithProfileResponse(BaseModel):
    """Schema for user with profile"""
    id: str
    name: str
    email: str
    is_active: bool
    created_at: datetime
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attribute = True

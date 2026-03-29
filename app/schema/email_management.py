from pydantic import BaseModel, EmailStr
from typing import List, Optional
from app.model.email_template import TemplateType


class EmailListResponse(BaseModel):
    total: int
    emails: List[str]


class SendEmailRequest(BaseModel):
    recipient_email: EmailStr
    template_id: str
    variables: Optional[dict] = None  # For dynamic content in templates


class BulkSendEmailRequest(BaseModel):
    recipient_emails: List[EmailStr]
    template_id: str
    variables: Optional[dict] = None


class EmailTemplateCreate(BaseModel):
    name: str
    template_type: TemplateType
    subject: str
    body: str
    description: Optional[str] = None


class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    template_type: Optional[TemplateType] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EmailTemplateResponse(BaseModel):
    id: str
    name: str
    template_type: TemplateType
    subject: str
    body: str
    description: Optional[str] = None
    is_active: bool


class BulkSendResponse(BaseModel):
    total_recipients: int
    successful: int
    failed: int
    errors: List[dict] = []

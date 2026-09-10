from sqlmodel import SQLModel, Field
from uuid import uuid4
from typing import Optional
from enum import Enum


class TemplateType(str, Enum):
    newsletter = "NEWSLETTER"
    promotional = "PROMOTIONAL"
    announcement = "ANNOUNCEMENT"
    product = "PRODUCT"
    event = "EVENT"
    webinar = "WEBINAR"
    onboarding = "ONBOARDING"
    feedback = "FEEDBACK"
    retention = "RETENTION"
    sales = "SALES"


class EmailTemplate(SQLModel, table=True):
    __tablename__ = 'email_templates'
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(index=True)
    template_type: TemplateType
    subject: str
    body: str
    description: Optional[str] = None
    is_active: bool = Field(default=True)
    created_at: str = Field(default_factory=lambda: str(__import__('datetime').datetime.utcnow()))
    updated_at: str = Field(default_factory=lambda: str(__import__('datetime').datetime.utcnow()))


class EmailTemplatePublic(SQLModel):
    id: str
    name: str
    template_type: TemplateType
    subject: str
    body: str
    description: Optional[str] = None
    is_active: bool

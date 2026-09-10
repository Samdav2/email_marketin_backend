from sqlmodel import SQLModel, Field
from uuid import uuid4
from typing import Optional
from enum import Enum

class Category(str, Enum):
    local_services = "LOCAL_SERVICES"
    health_care = "HEALTH_CARE"
    food_hospitality = "FOOD_HOSPITALITY"
    professional_services = "PROFESSIONAL_SERVICES"
    general = "GENERAL"
    web = "WEB"
    marketing = "MARKETING"


class Email(SQLModel, table=True):
    __tablename__ = 'emails'
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(index=True)
    category: str = Field(default="GENERAL", max_length=100)
    subcategory: Optional[str] = Field(default=None, nullable=True)
    domain: Optional[str] = Field(default=None, nullable=True)


class Campaign(SQLModel, table=True):
    __tablename__ = 'campaigns'
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    category: str
    subject: str
    total_recipients: int
    successful: int
    failed: int
    timestamp: str = Field(default_factory=lambda: str(__import__('datetime').datetime.utcnow()))

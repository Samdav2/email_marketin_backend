from sqlmodel import SQLModel, Field
from uuid import uuid4
from typing import Optional
from enum import Enum

class Category(str, Enum):
    web = "WEB"
    marketing = "MARKETING"
    general = "GENERAL"


class Email(SQLModel, table=True):
    __tablename__ = 'emails'
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str
    category: Category = Field(default=Category.web)


class Campaign(SQLModel, table=True):
    __tablename__ = 'campaigns'
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    category: str
    subject: str
    total_recipients: int
    successful: int
    failed: int
    timestamp: str = Field(default_factory=lambda: str(__import__('datetime').datetime.utcnow()))

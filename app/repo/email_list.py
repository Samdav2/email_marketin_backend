from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.model.emails import Email
from typing import List


async def get_all_emails(db: AsyncSession) -> List[str]:
    """Get all emails from database"""
    statement = select(Email.email).distinct()
    result = await db.exec(statement)
    return result.all()


async def get_emails_by_category(category: str, db: AsyncSession) -> List[str]:
    """Get emails by category"""
    statement = select(Email.email).where(Email.category == category).distinct()
    result = await db.exec(statement)
    return result.all()


async def get_total_email_count(db: AsyncSession) -> int:
    """Get total number of unique emails in database"""
    statement = select(Email).distinct(Email.email)
    result = await db.exec(statement)
    return len(result.all())

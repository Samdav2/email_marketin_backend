from app.model.emails import Email
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.schema.email import Email as EmailSchema

async def save_email(email: Email, db: AsyncSession) -> Email:
    """Save a single email to database"""
    db.add(email)
    await db.commit()
    await db.refresh(email)
    return email

async def save_multiple_emails(emails: list[Email], db: AsyncSession) -> list[Email]:
    """Save multiple emails to database"""
    for email in emails:
        db.add(email)
    await db.commit()
    return emails

async def get_all_email(db: AsyncSession) -> list[Email]:
    stmt = select(Email)
    payload = await db.exec(stmt)
    result = payload.all()
    return result

async def get_email_by_category(category: str, db: AsyncSession) -> list[EmailSchema]:
    stmt = select(Email).where(Email.category == category)
    payload = await db.exec(stmt)
    results = payload.all()
    refined_results = [EmailSchema.model_validate(result) for result in results]
    return refined_results

async def email_exists(email_address: str, db: AsyncSession) -> bool:
    """Check if email already exists in database"""
    stmt = select(Email).where(Email.email == email_address)
    payload = await db.exec(stmt)
    return payload.first() is not None

async def get_email_count(db: AsyncSession) -> int:
    """Get total count of emails in database"""
    stmt = select(Email)
    payload = await db.exec(stmt)
    return len(payload.all())

from app.model.emails import Campaign
from sqlalchemy import func

async def save_campaign(campaign: Campaign, db: AsyncSession) -> Campaign:
    """Save a campaign to database"""
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign

async def get_total_sent_count(db: AsyncSession) -> int:
    """Get total number of successful email sends across all campaigns"""
    stmt = select(func.sum(Campaign.successful))
    result = await db.exec(stmt)
    return result.one_or_none() or 0

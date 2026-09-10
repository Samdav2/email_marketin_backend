from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func
from app.model.emails import Email
from typing import List, Optional, Dict


async def get_all_emails(
    db: AsyncSession,
    category: Optional[str] = None,
    subcategory: Optional[str] = None
) -> List[Email]:
    """Get all email records from database, optionally filtered by category and subcategory"""
    statement = select(Email)
    if category and category.upper() != "ALL":
        cat_clean = category.upper()
        if cat_clean == "GENERAL":
            statement = statement.where(
                func.upper(Email.category).in_(["GENERAL", "WEB", "MARKETING"]) | (Email.category == None)
            )
        else:
            statement = statement.where(func.upper(Email.category) == cat_clean)

    if subcategory and subcategory.upper() != "ALL":
        subcat_clean = subcategory.strip()
        statement = statement.where(func.lower(Email.subcategory) == subcat_clean.lower())

    result = await db.exec(statement)
    return result.all()


async def get_all_email_strings(db: AsyncSession) -> List[str]:
    """Get distinct email strings from database"""
    statement = select(Email.email).distinct()
    result = await db.exec(statement)
    return result.all()


async def get_emails_by_category(
    category: str,
    db: AsyncSession,
    subcategory: Optional[str] = None
) -> List[Email]:
    """Get email records by category and optional subcategory"""
    cat_clean = category.upper()
    statement = select(Email)
    if cat_clean == "GENERAL":
        statement = statement.where(
            func.upper(Email.category).in_(["GENERAL", "WEB", "MARKETING"]) | (Email.category == None)
        )
    else:
        statement = statement.where(func.upper(Email.category) == cat_clean)

    if subcategory and subcategory.upper() != "ALL":
        statement = statement.where(func.lower(Email.subcategory) == subcategory.strip().lower())

    result = await db.exec(statement)
    return result.all()


async def get_total_email_count(db: AsyncSession) -> int:
    """Get total number of unique emails in database"""
    statement = select(func.count(func.distinct(Email.email)))
    result = await db.exec(statement)
    return result.one_or_none() or 0


async def get_category_counts(db: AsyncSession) -> Dict[str, int]:
    """Get counts of leads grouped by category"""
    statement = select(Email.category, func.count(Email.id)).group_by(Email.category)
    result = await db.exec(statement)
    counts = {}
    for cat, count in result.all():
        key = cat.upper() if cat else "GENERAL"
        counts[key] = counts.get(key, 0) + count
    return counts

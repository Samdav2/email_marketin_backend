"""
Profile Repository - Database operations for Profile model
"""
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.model.user import Profile
from app.schema.auth import ProfileResponse
import logging

logger = logging.getLogger(__name__)


async def create_profile(
    user_id: str,
    business_name: str,
    company_id: str,
    db: AsyncSession,
    **kwargs
) -> Profile:
    """Create new profile"""
    try:
        profile = Profile(
            user_id=user_id,
            business_name=business_name,
            company_id=company_id,
            **kwargs
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        logger.info(f"Profile created for user: {user_id}")
        return profile
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating profile: {str(e)}")
        raise


async def get_profile_by_user_id(user_id: str, db: AsyncSession) -> Profile:
    """Get profile by user ID"""
    try:
        stmt = select(Profile).where(Profile.user_id == user_id)
        result = await db.exec(stmt)
        profile = result.first()
        return profile
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise


async def get_profile_by_id(profile_id: str, db: AsyncSession) -> Profile:
    """Get profile by profile ID"""
    try:
        stmt = select(Profile).where(Profile.id == profile_id)
        result = await db.exec(stmt)
        profile = result.first()
        return profile
    except Exception as e:
        logger.error(f"Error getting profile by ID: {str(e)}")
        raise


async def update_profile(
    user_id: str,
    db: AsyncSession,
    **kwargs
) -> Profile:
    """Update user profile"""
    try:
        profile = await get_profile_by_user_id(user_id, db)
        if not profile:
            raise ValueError("Profile not found")

        # Update fields
        for key, value in kwargs.items():
            if hasattr(profile, key) and value is not None:
                setattr(profile, key, value)

        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        logger.info(f"Profile updated for user: {user_id}")
        return profile
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating profile: {str(e)}")
        raise


async def profile_exists(user_id: str, db: AsyncSession) -> bool:
    """Check if profile exists for user"""
    try:
        profile = await get_profile_by_user_id(user_id, db)
        return profile is not None
    except Exception as e:
        logger.error(f"Error checking profile existence: {str(e)}")
        return False


async def company_id_exists(company_id: str, db: AsyncSession) -> bool:
    """Check if company ID already exists"""
    try:
        stmt = select(Profile).where(Profile.company_id == company_id)
        result = await db.exec(stmt)
        profile = result.first()
        return profile is not None
    except Exception as e:
        logger.error(f"Error checking company ID existence: {str(e)}")
        return False

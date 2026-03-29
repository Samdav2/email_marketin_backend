"""
User Repository - Database operations for User model
"""
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.model.user import User
from app.schema.auth import UserResponse
import logging

logger = logging.getLogger(__name__)


async def create_user(
    email: str,
    name: str,
    password_hash: str,
    db: AsyncSession
) -> User:
    """Create new user"""
    try:
        user = User(
            email=email,
            name=name,
            password_hash=password_hash
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User created: {email}")
        return user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise


async def get_user_by_email(email: str, db: AsyncSession) -> User:
    """Get user by email"""
    try:
        stmt = select(User).where(User.email == email)
        result = await db.exec(stmt)
        user = result.first()
        return user
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        raise


async def get_user_by_id(user_id: str, db: AsyncSession) -> User:
    """Get user by ID"""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.exec(stmt)
        user = result.first()
        return user
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        raise


async def update_user_password(
    user_id: str,
    password_hash: str,
    db: AsyncSession
) -> User:
    """Update user password"""
    try:
        user = await get_user_by_id(user_id, db)
        if not user:
            raise ValueError("User not found")

        user.password_hash = password_hash
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Password updated for user: {user.email}")
        return user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user password: {str(e)}")
        raise


async def deactivate_user(user_id: str, db: AsyncSession) -> User:
    """Deactivate user account"""
    try:
        user = await get_user_by_id(user_id, db)
        if not user:
            raise ValueError("User not found")

        user.is_active = False
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User deactivated: {user.email}")
        return user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deactivating user: {str(e)}")
        raise


async def user_exists(email: str, db: AsyncSession) -> bool:
    """Check if user exists"""
    try:
        user = await get_user_by_email(email, db)
        return user is not None
    except Exception as e:
        logger.error(f"Error checking user existence: {str(e)}")
        return False

"""
Current User Dependency for FastAPI
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError
from app.dependencies.jwt_handler import verify_token, get_user_id_from_token
from app.repo import user as user_repo
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_session
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials = Depends(security),
    db: AsyncSession = Depends(get_session)
):
    """
    Dependency to get current authenticated user

    Args:
        credentials: HTTP Bearer token from request header
        db: Database session

    Returns:
        Current user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    try:
        # Verify token and get user ID
        user_id = get_user_id_from_token(token)

        # Get user from database
        user = await user_repo.get_user_by_id(user_id, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

        return user

    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Dependency to ensure current user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return current_user

"""
JWT Token Utilities
"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.settings import settings
import logging

logger = logging.getLogger(__name__)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create JWT access token

    Args:
        data: Dictionary containing user information (id, email, etc.)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating token: {str(e)}")
        raise


def verify_token(token: str) -> dict:
    """
    Verify JWT token and return payload

    Args:
        token: JWT token string

    Returns:
        Token payload dictionary

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise


def get_user_id_from_token(token: str) -> str:
    """
    Extract user ID from token

    Args:
        token: JWT token string

    Returns:
        User ID from token
    """
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise JWTError("No user ID in token")
        return user_id
    except Exception as e:
        logger.error(f"Error extracting user ID from token: {str(e)}")
        raise

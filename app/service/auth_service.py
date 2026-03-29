"""
Authentication Service - Business logic for auth operations
"""
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import BackgroundTasks
from app.repo import user as user_repo
from app.repo import profile as profile_repo
from app.dependencies.password_utils import hash_password, verify_password
from app.dependencies.jwt_handler import create_access_token
from app.dependencies.smtp_email import email_service
from app.schema.auth import TokenResponse, UserResponse, ProfileResponse
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)


async def signup(
    name: str,
    email: str,
    password: str,
    db: AsyncSession,
    background_tasks: BackgroundTasks = None
) -> TokenResponse:
    """
    User signup - create new user account

    Args:
        name: User's full name
        email: User's email
        password: User's password
        db: Database session
        background_tasks: FastAPI background tasks for async email sending

    Returns:
        TokenResponse with access token

    Raises:
        ValueError: If email already exists
    """
    try:
        # Check if user already exists
        existing_user = await user_repo.get_user_by_email(email, db)
        if existing_user:
            raise ValueError(f"Email {email} already registered")

        # Hash password
        password_hash = hash_password(password)

        # Create user
        user = await user_repo.create_user(
            email=email,
            name=name,
            password_hash=password_hash,
            db=db
        )

        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        # Send welcome email in background (non-blocking)
        if background_tasks:
            background_tasks.add_task(
                email_service.send_email,
                recipient=email,
                subject="Welcome to Email Marketing!",
                body=f"Hello {name},\n\nWelcome to Email Marketing! Your account has been created successfully.",
                is_html=False
            )
            logger.info(f"Welcome email queued for {email}")
        else:
            try:
                await email_service.send_email(
                    recipient=email,
                    subject="Welcome to Email Marketing!",
                    body=f"Hello {name},\n\nWelcome to Email Marketing! Your account has been created successfully.",
                    is_html=False
                )
            except Exception as e:
                logger.error(f"Failed to send welcome email: {str(e)}")

        logger.info(f"User signed up: {email}")

        return TokenResponse(
            access_token=access_token,
            user=UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at
            )
        )
    except ValueError as ve:
        logger.warning(f"Signup error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise


async def login(
    email: str,
    password: str,
    db: AsyncSession
) -> TokenResponse:
    """
    User login - verify credentials and return token

    Args:
        email: User's email
        password: User's password
        db: Database session

    Returns:
        TokenResponse with access token

    Raises:
        ValueError: If credentials are invalid
    """
    try:
        # Get user by email
        user = await user_repo.get_user_by_email(email, db)
        if not user:
            raise ValueError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is deactivated")

        # Verify password
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )

        logger.info(f"User logged in: {email}")

        return TokenResponse(
            access_token=access_token,
            user=UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at
            )
        )
    except ValueError as ve:
        logger.warning(f"Login error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise


async def reset_password(
    user_id: str,
    old_password: str,
    new_password: str,
    db: AsyncSession
) -> dict:
    """
    Reset user password

    Args:
        user_id: User ID
        old_password: Current password
        new_password: New password
        db: Database session

    Returns:
        Dictionary with success status

    Raises:
        ValueError: If credentials are invalid
    """
    try:
        # Get user
        user = await user_repo.get_user_by_id(user_id, db)
        if not user:
            raise ValueError("User not found")

        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        # Hash new password
        new_password_hash = hash_password(new_password)

        # Update password
        await user_repo.update_user_password(user_id, new_password_hash, db)

        logger.info(f"Password reset for user: {user.email}")

        return {
            "success": True,
            "message": "Password updated successfully"
        }
    except ValueError as ve:
        logger.warning(f"Password reset error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error during password reset: {str(e)}")
        raise


async def forgot_password(
    email: str,
    db: AsyncSession,
    background_tasks: BackgroundTasks = None
) -> dict:
    """
    Handle forgot password - send reset email in background

    Args:
        email: User's email
        db: Database session
        background_tasks: FastAPI background tasks for async email sending

    Returns:
        Dictionary with success status
    """
    try:
        # Get user
        user = await user_repo.get_user_by_email(email, db)
        if not user:
            # Don't reveal if email exists
            logger.info(f"Forgot password request for non-existent email: {email}")
            return {
                "success": True,
                "message": "If email exists, password reset link has been sent"
            }

        # Generate reset token
        reset_token = create_access_token(
            data={"sub": user.id, "email": user.email, "type": "reset"},
            expires_delta=timedelta(hours=24)
        )

        # Send reset email
        reset_url = f"https://yourdomain.com/reset-password?token={reset_token}"
        reset_body = f"""Hello {user.name},

You requested to reset your password. Click the link below to reset:

{reset_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email."""

        # Send reset email in background (non-blocking)
        if background_tasks:
            background_tasks.add_task(
                email_service.send_email,
                recipient=email,
                subject="Password Reset Request",
                body=reset_body,
                is_html=False
            )
            logger.info(f"Password reset email queued for: {email}")
        else:
            await email_service.send_email(
                recipient=email,
                subject="Password Reset Request",
                body=reset_body,
                is_html=False
            )
            logger.info(f"Password reset email sent to: {email}")

        return {
            "success": True,
            "message": "Password reset link has been sent to your email"
        }
    except Exception as e:
        logger.error(f"Error during forgot password: {str(e)}")
        raise


async def create_or_update_profile(
    user_id: str,
    business_name: str,
    company_id: str,
    db: AsyncSession,
    **kwargs
) -> ProfileResponse:
    """
    Create or update user profile

    Args:
        user_id: User ID
        business_name: Business name
        company_id: Company ID
        db: Database session
        **kwargs: Additional profile fields

    Returns:
        ProfileResponse

    Raises:
        ValueError: If user doesn't exist or company_id is duplicate
    """
    try:
        # Check if user exists
        user = await user_repo.get_user_by_id(user_id, db)
        if not user:
            raise ValueError("User not found")

        # Check if profile already exists
        profile_exists = await profile_repo.profile_exists(user_id, db)

        if profile_exists:
            # Update existing profile
            profile = await profile_repo.update_profile(
                user_id=user_id,
                db=db,
                business_name=business_name,
                company_id=company_id,
                **kwargs
            )
        else:
            # Create new profile
            profile = await profile_repo.create_profile(
                user_id=user_id,
                business_name=business_name,
                company_id=company_id,
                db=db,
                **kwargs
            )

        logger.info(f"Profile created/updated for user: {user_id}")

        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            business_name=profile.business_name,
            company_id=profile.company_id,
            phone=profile.phone,
            website=profile.website,
            address=profile.address,
            city=profile.city,
            state=profile.state,
            postal_code=profile.postal_code,
            country=profile.country,
            industry=profile.industry,
            company_size=profile.company_size,
            description=profile.description,
            logo_url=profile.logo_url,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
    except ValueError as ve:
        logger.warning(f"Profile operation error: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error during profile operation: {str(e)}")
        raise

"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_session
from app.schema.auth import (
    SignUpRequest, LoginRequest, ResetPasswordRequest, ForgotPasswordRequest,
    TokenResponse, UserResponse, ProfileRequest, ProfileResponse, UserWithProfileResponse
)
from app.service import auth_service
from app.dependencies.current_user import get_current_active_user
from app.repo import profile as profile_repo
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"], prefix="/auth")


# Response wrapper
class ApiResponse:
    def __init__(self, success: bool, message: str, data=None):
        self.success = success
        self.message = message
        self.data = data


@router.post("/signup", response_model=TokenResponse)
async def signup(
    request: SignUpRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session)
):
    """
    User signup endpoint
    Create new user account
    Send welcome email in background
    """
    try:
        result = await auth_service.signup(
            name=request.name,
            email=request.email,
            password=request.password,
            db=db,
            background_tasks=background_tasks
        )
        return result
    except ValueError as e:
        logger.warning(f"Signup failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during signup"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    User login endpoint
    Verify credentials and return access token
    """
    try:
        result = await auth_service.login(
            email=request.email,
            password=request.password,
            db=db
        )
        return result
    except ValueError as e:
        logger.warning(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login"
        )


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Reset password endpoint
    Requires authentication
    """
    try:
        result = await auth_service.reset_password(
            user_id=current_user.id,
            old_password=request.old_password,
            new_password=request.new_password,
            db=db
        )
        return {
            "success": result["success"],
            "message": result["message"]
        }
    except ValueError as e:
        logger.warning(f"Password reset failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during password reset"
        )


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_session)
):
    """
    Forgot password endpoint
    Send password reset email in background
    """
    try:
        result = await auth_service.forgot_password(
            email=request.email,
            db=db,
            background_tasks=background_tasks
        )
        return {
            "success": result["success"],
            "message": result["message"]
        }
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during password reset request"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user)
):
    """
    Get current user information
    Requires authentication
    """
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/profile", response_model=ProfileResponse)
async def create_or_update_profile(
    request: ProfileRequest,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Create or update user profile
    Requires authentication
    """
    try:
        # Check if company_id already exists (for new profiles)
        profile_exists = await profile_repo.profile_exists(current_user.id, db)
        if not profile_exists:
            company_id_exists = await profile_repo.company_id_exists(request.company_id, db)
            if company_id_exists:
                raise ValueError("Company ID already exists")

        result = await auth_service.create_or_update_profile(
            user_id=current_user.id,
            business_name=request.business_name,
            company_id=request.company_id,
            db=db,
            phone=request.phone,
            website=request.website,
            address=request.address,
            city=request.city,
            state=request.state,
            postal_code=request.postal_code,
            country=request.country,
            industry=request.industry,
            company_size=request.company_size,
            description=request.description,
            logo_url=request.logo_url
        )
        return result
    except ValueError as e:
        logger.warning(f"Profile creation/update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating/updating profile"
        )


@router.get("/profile", response_model=ProfileResponse)
async def get_user_profile(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get user profile
    Requires authentication
    """
    try:
        profile = await profile_repo.get_profile_by_user_id(current_user.id, db)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving profile"
        )


@router.get("/profile/full", response_model=UserWithProfileResponse)
async def get_user_with_profile(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Get user with full profile information
    Requires authentication
    """
    try:
        profile = await profile_repo.get_profile_by_user_id(current_user.id, db)

        profile_response = None
        if profile:
            profile_response = ProfileResponse(
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

        return UserWithProfileResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            profile=profile_response
        )
    except Exception as e:
        logger.error(f"Error getting user with profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user profile information"
        )

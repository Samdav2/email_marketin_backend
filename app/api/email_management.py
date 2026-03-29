from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_session
from app.schema.email_management import (
    EmailListResponse,
    SendEmailRequest,
    BulkSendEmailRequest,
    BulkSendResponse,
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse
)
from app.repo.email_list import get_all_emails, get_total_email_count
from app.repo.email_template import (
    get_all_templates,
    get_template_by_id,
    create_template,
    update_template,
    delete_template
)
from app.service.email_sending_service import send_single_email, send_bulk_emails
from app.service.email_template_service import initialize_default_templates
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["email_management"], prefix="/emails")


# ==================== EMAIL LIST ENDPOINTS ====================

@router.get("/all", response_model=EmailListResponse)
async def get_all_emails_endpoint(
    db: AsyncSession = Depends(get_session)
):
    """
    Get all emails from database

    Returns list of all unique emails collected from scraping
    """
    try:
        emails = await get_all_emails(db)
        total = await get_total_email_count(db)

        return EmailListResponse(
            total=total,
            emails=emails
        )
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching emails: {str(e)}"
        )


# ==================== EMAIL TEMPLATE ENDPOINTS ====================

@router.get("/templates", response_model=list[EmailTemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_session)
):
    """
    Get all available email templates

    Returns list of professional email templates ready to use
    """
    try:
        templates = await get_all_templates(db)
        if not templates:
            # Initialize default templates on first access
            await initialize_default_templates(db)
            templates = await get_all_templates(db)

        return [
            EmailTemplateResponse(
                id=t.id,
                name=t.name,
                template_type=t.template_type,
                subject=t.subject,
                body=t.body,
                description=t.description,
                is_active=t.is_active
            )
            for t in templates
        ]
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching templates: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=EmailTemplateResponse)
async def get_template(
    template_id: str,
    db: AsyncSession = Depends(get_session)
):
    """
    Get specific email template by ID

    Returns template details including subject and HTML body
    """
    try:
        template = await get_template_by_id(template_id, db)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        return EmailTemplateResponse(
            id=template.id,
            name=template.name,
            template_type=template.template_type,
            subject=template.subject,
            body=template.body,
            description=template.description,
            is_active=template.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching template: {str(e)}"
        )


@router.post("/templates", response_model=EmailTemplateResponse)
async def create_new_template(
    request: EmailTemplateCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Create new email template (admin only)

    Create custom email templates for different purposes
    """
    try:
        template = await create_template(
            name=request.name,
            template_type=request.template_type,
            subject=request.subject,
            body=request.body,
            description=request.description,
            db=db
        )

        return EmailTemplateResponse(
            id=template.id,
            name=template.name,
            template_type=template.template_type,
            subject=template.subject,
            body=template.body,
            description=template.description,
            is_active=template.is_active
        )
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating template: {str(e)}"
        )


@router.patch("/templates/{template_id}", response_model=EmailTemplateResponse)
async def update_template_endpoint(
    template_id: str,
    request: EmailTemplateUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Update email template (admin only)

    Modify existing template details
    """
    try:
        update_data = request.model_dump(exclude_unset=True)
        template = await update_template(template_id, db, **update_data)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        return EmailTemplateResponse(
            id=template.id,
            name=template.name,
            template_type=template.template_type,
            subject=template.subject,
            body=template.body,
            description=template.description,
            is_active=template.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating template: {str(e)}"
        )


@router.delete("/templates/{template_id}")
async def delete_template_endpoint(
    template_id: str,
    db: AsyncSession = Depends(get_session)
):
    """
    Delete email template (admin only)

    Remove template from system
    """
    try:
        success = await delete_template(template_id, db)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )

        return {"message": "Template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting template: {str(e)}"
        )


# ==================== EMAIL SENDING ENDPOINTS ====================

@router.post("/send", response_model=dict)
async def send_email_endpoint(
    request: SendEmailRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Send email to single recipient using template (admin only)

    Use a pre-designed template to send professional emails
    """
    try:
        result = await send_single_email(
            recipient_email=request.recipient_email,
            template_id=request.template_id,
            variables=request.variables,
            db=db
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to send email")
            )

        return {
            "success": True,
            "message": f"Email sent to {request.recipient_email}",
            "recipient": request.recipient_email
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {str(e)}"
        )


@router.post("/send-bulk", response_model=BulkSendResponse)
async def send_bulk_emails_endpoint(
    request: BulkSendEmailRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Send emails to multiple recipients using template (admin only)

    Send bulk professional emails to scraped email lists

    - Processed in batches of 10 for optimal performance
    - Supports dynamic template variables
    - Returns detailed success/failure report
    """
    try:
        if not request.recipient_emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipient list cannot be empty"
            )

        if len(request.recipient_emails) > 100000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send to more than 100,000 recipients at once"
            )

        result = await send_bulk_emails(
            recipient_emails=request.recipient_emails,
            template_id=request.template_id,
            variables=request.variables,
            db=db
        )

        return BulkSendResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending bulk emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending bulk emails: {str(e)}"
        )

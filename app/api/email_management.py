from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging
import csv
import io
import re
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_session
from app.core.settings import settings
from fastapi.responses import Response
from app.schema.email_management import (
    EmailItem,
    EmailListResponse,
    CategoryInfo,
    CategorySummaryResponse,
    SendEmailRequest,
    BulkSendEmailRequest,
    BulkSendResponse,
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplateResponse
)
from app.repo.email_list import get_all_emails, get_total_email_count, get_category_counts
from app.repo.email_template import (
    get_all_templates,
    get_template_by_id,
    create_template,
    update_template,
    delete_template
)
from app.service.email_sending_service import send_single_email, send_bulk_emails
from app.service.email_template_service import (
    initialize_default_templates,
    verify_template_spam_risk
)
from app.dependencies.email_dispatcher import unified_email_service
from app.service.website_classifier import CATEGORY_TAXONOMY

logger = logging.getLogger(__name__)

router = APIRouter(tags=["email_management"], prefix="/emails")


class SpamVerifyRequest(BaseModel):
    template_id: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None


class TestSendEmailRequest(BaseModel):
    recipient_email: str
    subject: str = "Test Email Deliverability"
    body: str = "<p>Hello! This is a test email sent from Email Marketing backend.</p>"
    is_html: bool = True


# ==================== EMAIL LIST ENDPOINTS ====================

CATEGORY_DISPLAY_NAMES = {
    "LOCAL_SERVICES": "Local Service Businesses",
    "HEALTH_CARE": "Health and Care Related",
    "FOOD_HOSPITALITY": "Food and Hospitality",
    "PROFESSIONAL_SERVICES": "Professional Services",
    "GENERAL": "General Business",
    "WEB": "General Business",
    "MARKETING": "Marketing"
}


@router.get("/all", response_model=EmailListResponse)
async def get_all_emails_endpoint(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Get emails from database with optional category and subcategory filtering
    """
    try:
        raw_emails = await get_all_emails(db, category=category, subcategory=subcategory)
        total_unique = await get_total_email_count(db)
        counts = await get_category_counts(db)

        items = []
        for e in raw_emails:
            lead_domain = getattr(e, 'domain', None)
            if not lead_domain and '@' in e.email:
                lead_domain = e.email.split('@')[1]

            cat = getattr(e, 'category', 'GENERAL') or 'GENERAL'
            subcat = getattr(e, 'subcategory', None)

            items.append(
                EmailItem(
                    id=e.id,
                    email=e.email,
                    category=cat,
                    subcategory=subcat,
                    domain=lead_domain
                )
            )

        return EmailListResponse(
            total=len(items) if category and category.upper() != "ALL" else total_unique,
            emails=items,
            category_counts=counts
        )
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching emails: {str(e)}"
        )


@router.get("/categories", response_model=CategorySummaryResponse)
async def get_categories_summary_endpoint(
    db: AsyncSession = Depends(get_session)
):
    """
    Get summary of all available email lead categories with current counts
    """
    try:
        total_unique = await get_total_email_count(db)
        counts = await get_category_counts(db)

        category_infos = []
        for cat_key, display_name in CATEGORY_DISPLAY_NAMES.items():
            if cat_key in ("WEB", "MARKETING"):
                continue  # Collapse legacy into General
            subcats = list(CATEGORY_TAXONOMY.get(cat_key, {}).keys())
            count = counts.get(cat_key, 0)
            if cat_key == "GENERAL":
                count += counts.get("WEB", 0) + counts.get("MARKETING", 0)

            category_infos.append(
                CategoryInfo(
                    id=cat_key,
                    name=display_name,
                    count=count,
                    subcategories=subcats
                )
            )

        return CategorySummaryResponse(
            total_leads=total_unique,
            categories=category_infos
        )
    except Exception as e:
        logger.error(f"Error fetching categories summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching categories summary: {str(e)}"
        )


@router.get("/export")
async def export_emails_csv(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Export scraped emails to CSV, optionally filtered by category and subcategory
    """
    try:
        raw_emails = await get_all_emails(db, category=category, subcategory=subcategory)

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Email Address", "Domain", "Category", "Subcategory"])

        for e in raw_emails:
            domain = getattr(e, 'domain', '') or (e.email.split('@')[1] if '@' in e.email else '')
            cat = getattr(e, 'category', 'GENERAL') or 'GENERAL'
            if cat.upper() in ("WEB", "MARKETING"):
                cat = "GENERAL"
            subcat = getattr(e, 'subcategory', '') or ''
            writer.writerow([e.email, domain, cat, subcat])

        csv_content = output.getvalue()

        filename_parts = ["leads"]
        if category and category.upper() != "ALL":
            filename_parts.append(category.lower().replace("_", "-"))
        else:
            filename_parts.append("all")

        if subcategory and subcategory.upper() != "ALL":
            clean_sub = re.sub(r'[^a-zA-Z0-9_-]', '', subcategory.lower().replace(" ", "-"))
            if clean_sub:
                filename_parts.append(clean_sub)

        filename = f"{'-'.join(filename_parts)}.csv"

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        logger.error(f"Error exporting emails CSV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting emails: {str(e)}"
        )


# ==================== EMAIL TEMPLATE ENDPOINTS ====================

@router.get("/templates", response_model=list[EmailTemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_session)
):
    """
    Get all available email templates
    """
    try:
        templates = await get_all_templates(db)
        if not templates:
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
    Create new email template
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
    Update email template
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
    Delete email template
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


@router.post("/templates/verify-spam")
async def verify_template_spam_endpoint(
    request: SpamVerifyRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Verify template content for spam triggers, anti-spam footers, and deliverability risk.
    """
    subject = request.subject or ""
    body = request.body or ""

    if request.template_id:
        template = await get_template_by_id(request.template_id, db)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {request.template_id} not found"
            )
        subject = template.subject
        body = template.body

    if not subject and not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide either template_id or subject and body to verify."
        )

    return verify_template_spam_risk(subject, body)


# ==================== EMAIL SENDING ENDPOINTS ====================

@router.post("/send", response_model=dict)
async def send_email_endpoint(
    request: SendEmailRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Send email to single recipient using template
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
            "recipient": request.recipient_email,
            "provider": settings.EMAIL_PROVIDER
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
    Send emails to multiple recipients using template
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


@router.post("/test-send")
async def test_send_email_endpoint(
    request: TestSendEmailRequest
):
    """
    Test send an email to a single address using configured EMAIL_PROVIDER (Resend, SMTP, Mailjet).
    """
    success = await unified_email_service.send_email(
        recipient=request.recipient_email,
        subject=request.subject,
        body=request.body,
        is_html=request.is_html
    )

    return {
        "success": success,
        "recipient": request.recipient_email,
        "provider": settings.EMAIL_PROVIDER,
        "message": f"Email test sent via {settings.EMAIL_PROVIDER} (success={success})"
    }

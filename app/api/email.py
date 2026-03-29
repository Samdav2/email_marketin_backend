"""
Email API Endpoints
Handles email sending and management operations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import List
from app.db.session import get_session
from app.service.email_service import (
    send_email_campaign,
    send_email_to_specific,
    save_extracted_emails
)
from app.repo.email import (
    get_email_by_category,
    get_all_email,
    get_email_count,
    get_total_sent_count
)
from app.model.emails import Category
from app.service.template_loader import template_loader
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["email"], prefix="/email")


# Request/Response Models
class SendEmailRequest(BaseModel):
    recipient: EmailStr
    subject: str
    body: str = ""
    is_html: bool = False
    template_name: str = None  # Optional template from templates/ folder


class SendCampaignRequest(BaseModel):
    category: str
    subject: str
    body: str = ""
    is_html: bool = False
    template_name: str = None  # Optional template from templates/ folder


class SaveEmailsRequest(BaseModel):
    emails: List[EmailStr]
    category: str = "WEB"


class SendCustomEmailRequest(BaseModel):
    recipient: EmailStr
    subject: str
    title: str
    name: str
    content: str
    button_text: str = "Learn More"
    button_url: str = "#"


class SendCustomBulkEmailRequest(BaseModel):
    category: str = None
    emails: List[EmailStr] = None
    subject: str
    title: str
    content: str
    button_text: str = "Learn More"
    button_url: str = "#"


class EmailResponse(BaseModel):
    success: bool
    message: str
    data: dict = None


@router.post("/send", response_model=EmailResponse)
async def send_email(
    request: SendEmailRequest
) -> EmailResponse:
    """
    Send email to a specific recipient
    """
    try:
        body = request.body
        is_html = request.is_html

        if request.template_name:
            # Try to load from HTML folder first
            content = template_loader.get_template_content("html", request.template_name)
            if content:
                body = content
                is_html = True
            else:
                # Try text folder
                content = template_loader.get_template_content("text", request.template_name)
                if content:
                    body = content
                    is_html = False
                else:
                    raise HTTPException(status_code=404, detail="Template not found")

        success = await send_email_to_specific(
            request.recipient,
            request.subject,
            body,
            is_html
        )

        if success:
            return EmailResponse(
                success=True,
                message=f"Email sent successfully to {request.recipient}"
            )
        else:
            return EmailResponse(
                success=False,
                message=f"Failed to send email to {request.recipient}"
            )
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign", response_model=EmailResponse)
async def send_campaign(
    request: SendCampaignRequest,
    db: AsyncSession = Depends(get_session)
) -> EmailResponse:
    """
    Send email campaign to all emails in a specific category
    """
    try:
        # Validate category
        try:
            category = Category[request.category.lower()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {[c.value for c in Category]}"
            )

        body = request.body
        is_html = request.is_html

        if request.template_name:
            # Try to load from HTML folder first
            content = template_loader.get_template_content("html", request.template_name)
            if content:
                body = content
                is_html = True
            else:
                # Try text folder
                content = template_loader.get_template_content("text", request.template_name)
                if content:
                    body = content
                    is_html = False
                else:
                    raise HTTPException(status_code=404, detail="Template not found")

        results = await send_email_campaign(
            category,
            request.subject,
            body,
            is_html,
            db
        )

        return EmailResponse(
            success=True,
            message=f"Campaign sent to {results['successful']} recipients",
            data=results
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-custom", response_model=EmailResponse)
async def send_custom_email(
    request: SendCustomEmailRequest
) -> EmailResponse:
    """
    Send a custom email wrapped in the professional base template
    """
    try:
        placeholders = {
            "title": request.title,
            "name": request.name,
            "content": request.content,
            "button_text": request.button_text,
            "button_url": request.button_url
        }

        # Render the custom base template
        body = template_loader.render_template("html", "custom_base.html", placeholders)

        if not body:
            raise HTTPException(status_code=500, detail="Failed to render custom template")

        success = await send_email_to_specific(
            request.recipient,
            request.subject,
            body,
            is_html=True
        )

        if success:
            return EmailResponse(
                success=True,
                message=f"Custom email sent successfully to {request.recipient}"
            )
        else:
            return EmailResponse(
                success=False,
                message=f"Failed to send custom email to {request.recipient}"
            )
    except Exception as e:
        logger.error(f"Error sending custom email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-custom-bulk", response_model=EmailResponse)
async def send_custom_bulk_email(
    request: SendCustomBulkEmailRequest,
    db: AsyncSession = Depends(get_session)
) -> EmailResponse:
    """
    Send a custom email wrapped in the professional base template in bulk
    """
    try:
        # Resolve recipients
        recipients = []
        if request.emails:
            recipients.extend([{'email': e, 'name': 'Valued Member'} for e in request.emails])

        if request.category:
            db_emails = await get_email_by_category(request.category, db)
            recipients.extend([{'email': e.email, 'name': 'Valued Member'} for e in db_emails])

        if not recipients:
            raise HTTPException(status_code=400, detail="No recipients provided or found in category")

        # Deduplicate by email
        seen_emails = set()
        unique_recipients = []
        for r in recipients:
            if r['email'] not in seen_emails:
                seen_emails.add(r['email'])
                unique_recipients.append(r)

        results = {
            'total': len(unique_recipients),
            'successful': 0,
            'failed': 0,
            'failed_emails': []
        }

        for recipient in unique_recipients:
            placeholders = {
                "title": request.title,
                "name": recipient['name'],
                "content": request.content,
                "button_text": request.button_text,
                "button_url": request.button_url
            }

            # Render template
            body = template_loader.render_template("html", "custom_base.html", placeholders)

            if not body:
                results['failed'] += 1
                results['failed_emails'].append(recipient['email'])
                continue

            # Send email
            success = await send_email_to_specific(
                recipient['email'],
                request.subject,
                body,
                is_html=True
            )

            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['failed_emails'].append(recipient['email'])

        return EmailResponse(
            success=True,
            message=f"Bulk custom email processing complete. Successful: {results['successful']}, Failed: {results['failed']}",
            data=results
        )
    except Exception as e:
        logger.error(f"Error sending bulk custom email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-batch", response_model=EmailResponse)
async def save_batch_emails(
    request: SaveEmailsRequest,
    db: AsyncSession = Depends(get_session)
) -> EmailResponse:
    """
    Save extracted emails to database
    """
    try:
        # Validate category
        try:
            category = Category[request.category.lower()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {[c.value for c in Category]}"
            )

        results = await save_extracted_emails(
            set(request.emails),
            category,
            db
        )

        return EmailResponse(
            success=True,
            message=f"Saved {results['saved']} emails ({results['duplicates']} duplicates, {results['failed']} failed)",
            data=results
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-category/{category}", response_model=EmailResponse)
async def get_emails_by_category(
    category: str,
    db: AsyncSession = Depends(get_session)
) -> EmailResponse:
    """
    Get all emails by category
    """
    try:
        emails = await get_email_by_category(category, db)
        return EmailResponse(
            success=True,
            message=f"Found {len(emails)} emails in category {category}",
            data={
                'category': category,
                'count': len(emails),
                'emails': [email.dict() for email in emails]
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=EmailResponse)
async def get_all_emails(
    db: AsyncSession = Depends(get_session)
) -> EmailResponse:
    """
    Get all emails from database
    """
    try:
        emails = await get_all_email(db)
        return EmailResponse(
            success=True,
            message=f"Found {len(emails)} total emails",
            data={
                'count': len(emails),
                'emails': [{'email': email.email, 'category': email.category} for email in emails]
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving all emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=EmailResponse)
async def get_email_stats(
    db: AsyncSession = Depends(get_session)
) -> EmailResponse:
    """
    Get email statistics inclusive of total sent
    """
    try:
        total_in_db = await get_email_count(db)
        total_sent = await get_total_sent_count(db)
        return EmailResponse(
            success=True,
            message="Email statistics retrieved",
            data={
                'total_emails_in_db': total_in_db,
                'total_sent_emails': total_sent
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/total-sent", response_model=EmailResponse)
async def get_total_sent_stats(
    db: AsyncSession = Depends(get_session)
) -> EmailResponse:
    """
    Get total number of emails sent across all campaigns
    """
    try:
        total_sent = await get_total_sent_count(db)
        return EmailResponse(
            success=True,
            message="Total sent statistics retrieved",
            data={
                'total_sent': total_sent
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving total sent stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_templates():
    """List all available email templates."""
    try:
        return {
            "success": True,
            "data": template_loader.list_templates()
        }
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_type}/{name}")
async def get_template_content(template_type: str, name: str):
    """Get the content of a specific template."""
    try:
        content = template_loader.get_template_content(template_type, name)
        if not content:
            raise HTTPException(status_code=404, detail="Template not found")
        return {
            "success": True,
            "data": {
                "name": name,
                "type": template_type,
                "content": content
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

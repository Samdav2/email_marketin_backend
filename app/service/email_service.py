"""
Email Service - Business Logic for Email Operations
Handles saving extracted emails and sending campaigns
"""
from typing import List, Set
from app.model.emails import Email, Category, Campaign
from app.repo.email import save_campaign
from app.dependencies.email_dispatcher import unified_email_service
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import logging

logger = logging.getLogger(__name__)


from typing import List, Set, Optional, Union

async def save_extracted_emails(
    emails: Union[Set[str], List[str]],
    category: Union[Category, str],
    db: AsyncSession,
    subcategory: Optional[str] = None,
    domain: Optional[str] = None
) -> dict:
    """
    Save extracted emails to database with category, subcategory, and domain metadata.

    Args:
        emails: Set or List of extracted email addresses
        category: Category for the emails (Enum or str)
        db: Database session
        subcategory: Optional specific niche (e.g. "Care agencies", "Plumbers")
        domain: Optional source domain of the scraped website

    Returns:
        dict: Results with saved, duplicate, and failed counts
    """
    results = {
        'saved': 0,
        'duplicates': 0,
        'failed': 0,
        'saved_emails': []
    }

    cat_str = category.value if hasattr(category, 'value') else str(category)

    for email_addr in emails:
        try:
            email_clean = str(email_addr).strip()
            if not email_clean or '@' not in email_clean:
                continue

            lead_domain = domain
            if not lead_domain and '@' in email_clean:
                lead_domain = email_clean.split('@')[1]

            # Check if email already exists
            stmt = select(Email).where(Email.email == email_clean)
            existing_result = await db.exec(stmt)
            existing = existing_result.first()

            if existing:
                # If existing had default category or no subcategory, enrich it
                enriched = False
                if subcategory and not getattr(existing, 'subcategory', None):
                    existing.subcategory = subcategory
                    enriched = True
                if (not getattr(existing, 'category', None) or existing.category.lower() in ('web', 'general')) and cat_str not in ('WEB', 'GENERAL'):
                    existing.category = cat_str
                    enriched = True
                if lead_domain and not getattr(existing, 'domain', None):
                    existing.domain = lead_domain
                    enriched = True

                if enriched:
                    db.add(existing)

                results['duplicates'] += 1
                logger.info(f"Email {email_clean} already exists in database (enriched: {enriched})")
                continue

            # Create new email record with full classification metadata
            new_email = Email(
                email=email_clean,
                category=cat_str,
                subcategory=subcategory,
                domain=lead_domain
            )
            db.add(new_email)

            results['saved'] += 1
            results['saved_emails'].append(email_clean)
            logger.info(f"Saved email: {email_clean} | category: {cat_str} | subcategory: {subcategory}")

        except Exception as e:
            results['failed'] += 1
            logger.error(f"Failed to save email {email_addr}: {str(e)}")

    # Commit all at once
    try:
        await db.commit()
        logger.info(f"Committed {results['saved']} emails to database")
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to commit emails: {str(e)}")
        results['saved'] = 0
        results['failed'] += len(results['saved_emails'])
        results['saved_emails'] = []

    return results


async def send_email_campaign(
    category: Category,
    subject: str,
    body: str,
    is_html: bool = False,
    db: AsyncSession = None
) -> dict:
    """
    Send email campaign to all emails in a specific category

    Args:
        category: Category of emails to send to
        subject: Email subject
        body: Email body content
        is_html: Whether body is HTML
        db: Database session

    Returns:
        dict: Results of campaign
    """
    results = {
        'total_recipients': 0,
        'successful': 0,
        'failed': 0,
        'failed_emails': []
    }

    try:
        # Get all emails for category
        if db:
            stmt = select(Email).where(Email.category == category)
            payload = await db.exec(stmt)
            emails = payload.all()

            email_addresses = [email.email for email in emails]
            results['total_recipients'] = len(email_addresses)

            if email_addresses:
                # Send bulk email via unified provider
                send_results = await unified_email_service.send_bulk_email(
                    email_addresses,
                    subject,
                    body,
                    is_html
                )

                results['successful'] = send_results['successful']
                results['failed'] = send_results['failed']
                results['failed_emails'] = send_results['failed_emails']

                # Log campaign to database
                try:
                    campaign = Campaign(
                        category=category.value if hasattr(category, 'value') else str(category),
                        subject=subject,
                        total_recipients=results['total_recipients'],
                        successful=results['successful'],
                        failed=results['failed']
                    )
                    await save_campaign(campaign, db)
                    logger.info(f"Campaign logged to database: {campaign.id}")
                except Exception as log_error:
                    logger.error(f"Failed to log campaign: {str(log_error)}")

                logger.info(f"Campaign sent to {results['successful']} recipients")
            else:
                logger.warning(f"No emails found for category: {category}")

    except Exception as e:
        logger.error(f"Failed to send campaign: {str(e)}")
        results['error'] = str(e)

    return results


async def send_email_to_specific(
    recipient: str,
    subject: str,
    body: str,
    is_html: bool = False
) -> bool:
    """
    Send email to a specific recipient

    Args:
        recipient: Email address
        subject: Email subject
        body: Email body
        is_html: Whether body is HTML

    Returns:
        bool: Success status
    """
    return await unified_email_service.send_email(recipient, subject, body, is_html)


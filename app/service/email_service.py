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

from sqlalchemy import func
from app.db.session import engine

INVALID_EMAIL_EXTENSIONS = (
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg',
    '.css', '.js', '.ico', '.woff', '.woff2', '.ttf', '.eot'
)

async def _save_emails_with_session(
    emails: Union[Set[str], List[str]],
    category: Union[Category, str],
    db: AsyncSession,
    subcategory: Optional[str] = None,
    domain: Optional[str] = None,
    country: Optional[str] = None,
    location: Optional[str] = None
) -> dict:
    results = {
        'saved': 0,
        'duplicates': 0,
        'failed': 0,
        'saved_emails': []
    }

    cat_raw = category.value if hasattr(category, 'value') else str(category)
    cat_str = (cat_raw or "GENERAL").strip().upper()

    seen_in_batch = set()

    for email_addr in emails:
        try:
            email_clean = str(email_addr).strip().lower()
            email_clean = email_clean.rstrip('.,;:!?')

            if not email_clean or '@' not in email_clean:
                continue

            # Skip asset/file masquerades
            if any(email_clean.endswith(ext) for ext in INVALID_EMAIL_EXTENSIONS):
                continue

            parts = email_clean.split('@')
            if len(parts) != 2 or not parts[0] or '.' not in parts[1]:
                continue

            # Prevent in-batch duplicate queries
            if email_clean in seen_in_batch:
                continue
            seen_in_batch.add(email_clean)

            lead_domain = domain
            if not lead_domain:
                lead_domain = parts[1]

            # Check if email already exists (case-insensitive) without triggering autoflush
            with db.no_autoflush:
                stmt = select(Email).where(func.lower(Email.email) == email_clean)
                existing_result = await db.exec(stmt)
                existing = existing_result.first()

            if existing:
                enriched = False
                if subcategory and not getattr(existing, 'subcategory', None):
                    existing.subcategory = subcategory
                    enriched = True
                existing_cat = (getattr(existing, 'category', None) or '').upper()
                if (not existing_cat or existing_cat in ('WEB', 'GENERAL')) and cat_str not in ('WEB', 'GENERAL'):
                    existing.category = cat_str
                    enriched = True
                if lead_domain and not getattr(existing, 'domain', None):
                    existing.domain = lead_domain
                    enriched = True
                if country and not getattr(existing, 'country', None):
                    existing.country = country
                    enriched = True
                if location and not getattr(existing, 'location', None):
                    existing.location = location
                    enriched = True

                if enriched:
                    db.add(existing)

                results['duplicates'] += 1
                logger.info(f"Email {email_clean} already exists in database (enriched: {enriched})")
                continue

            new_email = Email(
                email=email_clean,
                category=cat_str,
                subcategory=subcategory,
                domain=lead_domain,
                country=country,
                location=location
            )
            db.add(new_email)

            results['saved'] += 1
            results['saved_emails'].append(email_clean)
            logger.info(f"Saved email: {email_clean} | category: {cat_str} | subcategory: {subcategory} | country: {country} | location: {location}")

        except Exception as e:
            results['failed'] += 1
            logger.error(f"Failed to process email {email_addr}: {str(e)}")

    if results['saved'] > 0 or results['duplicates'] > 0:
        try:
            await db.commit()
            logger.info(f"Committed {results['saved']} emails to database")
        except Exception as e:
            await db.rollback()
            logger.warning(f"Batch commit failed ({e}), attempting individual row saves with savepoints...")
            saved_count = 0
            saved_list = []
            for clean_addr in results['saved_emails']:
                try:
                    async with db.begin_nested():
                        ind_email = Email(
                            email=clean_addr,
                            category=cat_str,
                            subcategory=subcategory,
                            domain=domain or clean_addr.split('@')[1],
                            country=country,
                            location=location
                        )
                        db.add(ind_email)
                    await db.commit()
                    saved_count += 1
                    saved_list.append(clean_addr)
                except Exception as ind_err:
                    logger.error(f"Failed individual save for {clean_addr}: {ind_err}")
                    results['failed'] += 1
            results['saved'] = saved_count
            results['saved_emails'] = saved_list

    return results


async def save_extracted_emails(
    emails: Union[Set[str], List[str]],
    category: Union[Category, str],
    db: Optional[AsyncSession] = None,
    subcategory: Optional[str] = None,
    domain: Optional[str] = None,
    country: Optional[str] = None,
    location: Optional[str] = None
) -> dict:
    """
    Save extracted emails to database with category, subcategory, domain, country, and location metadata.
    Handles session lifecycle: if db is provided, uses it; otherwise opens a dedicated session.
    """
    if db is not None:
        return await _save_emails_with_session(emails, category, db, subcategory, domain, country, location)

    async with AsyncSession(engine) as session:
        return await _save_emails_with_session(emails, category, session, subcategory, domain, country, location)




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


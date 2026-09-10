from typing import Set, Optional, List, Dict
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone
from app.model.emails import ScrapedDomain, ScraperState, Email
import logging

logger = logging.getLogger(__name__)

async def get_known_domains_db(db: AsyncSession) -> Set[str]:
    """
    Returns all domains that have already been scraped or stored in the database.
    Combines both the scraped_domains table and existing emails table domains.
    Persists across all container restarts and Railway deployments!
    """
    known = set()
    try:
        # 1. Scraped domains table
        stmt = select(ScrapedDomain.domain)
        result = await db.exec(stmt)
        for dom in result.all():
            if dom:
                clean_dom = dom.lower().strip()
                if clean_dom.startswith('www.'):
                    clean_dom = clean_dom[4:]
                known.add(clean_dom)

        # 2. Existing domains from saved emails
        stmt_emails = select(Email.domain, Email.email)
        res_emails = await db.exec(stmt_emails)
        for d, e in res_emails.all():
            if d:
                clean_d = d.lower().strip()
                if clean_d.startswith('www.'):
                    clean_d = clean_d[4:]
                known.add(clean_d)
            elif e and '@' in e:
                clean_e_domain = e.split('@')[1].lower().strip()
                if clean_e_domain.startswith('www.'):
                    clean_e_domain = clean_e_domain[4:]
                known.add(clean_e_domain)

    except Exception as err:
        logger.error(f"Error fetching known domains from database: {err}")

    return known


async def record_scraped_domain_db(
    domain: str,
    status: str,
    emails_count: int,
    category: Optional[str],
    db: AsyncSession
) -> None:
    """Records a scraped domain status in PostgreSQL."""
    try:
        clean_dom = domain.lower().strip()
        if clean_dom.startswith('www.'):
            clean_dom = clean_dom[4:]

        stmt = select(ScrapedDomain).where(ScrapedDomain.domain == clean_dom)
        result = await db.exec(stmt)
        existing = result.first()

        now_iso = datetime.now(timezone.utc).isoformat()
        if existing:
            existing.status = status
            existing.emails_count = emails_count
            if category:
                existing.category = category
            existing.scraped_at = now_iso
            db.add(existing)
        else:
            new_rec = ScrapedDomain(
                domain=clean_dom,
                status=status,
                emails_count=emails_count,
                category=category,
                scraped_at=now_iso
            )
            db.add(new_rec)

        await db.commit()
    except Exception as err:
        await db.rollback()
        logger.warning(f"Failed to record scraped domain {domain} to DB: {err}")


async def record_scraped_domains_batch_db(
    records: List[Dict],
    db: AsyncSession
) -> None:
    """Bulk records scraped domain statuses in PostgreSQL."""
    if not records:
        return
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        for r in records:
            domain = r.get("domain", "").lower().strip()
            if domain.startswith("www."):
                domain = domain[4:]
            if not domain:
                continue

            stmt = select(ScrapedDomain).where(ScrapedDomain.domain == domain)
            res = await db.exec(stmt)
            existing = res.first()
            if existing:
                existing.status = r.get("status", "scraped")
                existing.emails_count = r.get("emails_count", 0)
                if r.get("category"):
                    existing.category = r.get("category")
                existing.scraped_at = now_iso
                db.add(existing)
            else:
                new_rec = ScrapedDomain(
                    domain=domain,
                    status=r.get("status", "scraped"),
                    emails_count=r.get("emails_count", 0),
                    category=r.get("category"),
                    scraped_at=now_iso
                )
                db.add(new_rec)
        await db.commit()
    except Exception as err:
        await db.rollback()
        logger.warning(f"Failed to batch record scraped domains to DB: {err}")


async def get_scraper_state_db(key: str, default: str, db: AsyncSession) -> str:
    """Fetches persistent scraper state from PostgreSQL."""
    try:
        stmt = select(ScraperState).where(ScraperState.key == key)
        res = await db.exec(stmt)
        record = res.first()
        if record:
            return record.value
    except Exception as err:
        logger.warning(f"Could not read scraper_state key '{key}': {err}")
    return default


async def set_scraper_state_db(key: str, value: str, db: AsyncSession) -> None:
    """Saves persistent scraper state in PostgreSQL."""
    try:
        stmt = select(ScraperState).where(ScraperState.key == key)
        res = await db.exec(stmt)
        record = res.first()
        now_iso = datetime.now(timezone.utc).isoformat()
        if record:
            record.value = value
            record.updated_at = now_iso
            db.add(record)
        else:
            new_state = ScraperState(key=key, value=value, updated_at=now_iso)
            db.add(new_state)
        await db.commit()
    except Exception as err:
        await db.rollback()
        logger.warning(f"Could not write scraper_state key '{key}': {err}")

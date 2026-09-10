import asyncio
import uuid
from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import engine
from app.model.emails import Category as EmailCategory
from app.service.uk_domain_service import discover_uk_domains
from app.service.scrape_email import AdvancedDomainScraper, process_domain_task
from app.service.email_service import save_extracted_emails
from app.repo.scraped_domain import (
    get_known_domains_db,
    record_scraped_domain_db,
    get_scraper_state_db,
    set_scraper_state_db,
)

logger = logging.getLogger(__name__)


class ScrapeTaskManager:
    """
    Manages background email scraping jobs in separate async tasks / thread pools.
    Prevents blocking the FastAPI main application thread during long domain discovery
    and web scraping operations.
    """

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._running_async_tasks: Dict[str, asyncio.Task] = {}

    def create_scrape_to_db_task(
        self,
        email_limit: int,
        domain_limit: int,
        category: str
    ) -> Dict[str, Any]:
        task_id = str(uuid.uuid4())
        task_info = {
            "task_id": task_id,
            "request_type": "scrape_to_db",
            "status": "pending",
            "email_limit": email_limit,
            "domain_limit": domain_limit,
            "category": category,
            "urls": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "started_at": None,
            "completed_at": None,
            "progress": {
                "domains_scraped": 0,
                "total_domains": 0,
                "emails_found": 0,
                "emails_saved": 0,
                "duplicates_skipped": 0,
                "errors": 0
            },
            "results": [],
            "error": None
        }
        self.tasks[task_id] = task_info

        async_task = asyncio.create_task(
            self._run_scrape_to_db_job(task_id, email_limit, domain_limit, category)
        )
        self._running_async_tasks[task_id] = async_task
        return task_info

    def create_bulk_scrape_task(self, urls: List[str]) -> Dict[str, Any]:
        task_id = str(uuid.uuid4())
        task_info = {
            "task_id": task_id,
            "request_type": "bulk_scrape",
            "status": "pending",
            "email_limit": 0,
            "domain_limit": len(urls),
            "category": "WEB",
            "urls": [str(u) for u in urls],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "started_at": None,
            "completed_at": None,
            "progress": {
                "domains_scraped": 0,
                "total_domains": len(urls),
                "emails_found": 0,
                "emails_saved": 0,
                "duplicates_skipped": 0,
                "errors": 0
            },
            "results": [],
            "error": None
        }
        self.tasks[task_id] = task_info

        async_task = asyncio.create_task(
            self._run_bulk_scrape_job(task_id, urls)
        )
        self._running_async_tasks[task_id] = async_task
        return task_info

    async def _run_scrape_to_db_job(
        self,
        task_id: str,
        email_limit: int,
        domain_limit: int,
        category: str
    ):
        task_info = self.tasks[task_id]
        task_info["status"] = "running"
        task_info["started_at"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"🚀 [Task {task_id}] Started scrape_to_db background job (limit={email_limit}, domains={domain_limit})")

        try:
            # 1. Fetch known domains and CDX resume index directly from PostgreSQL
            logger.info(f"🔍 [Task {task_id}] Loading known scraped domains and resume state from PostgreSQL...")
            known_domains = set()
            cdx_resume_index = 0
            async with AsyncSession(engine) as db_init:
                known_domains = await get_known_domains_db(db_init)
                state_str = await get_scraper_state_db("cdx_resume_index", "0", db_init)
                try:
                    cdx_resume_index = int(state_str)
                except Exception:
                    cdx_resume_index = 0

            logger.info(f"📚 [Task {task_id}] Fast-forwarding past {len(known_domains)} existing domains in DB. Resume index: {cdx_resume_index}")

            # 2. Discover UK domains (fast and non-blocking)
            uk_domains, next_index = await asyncio.to_thread(
                discover_uk_domains,
                target_new_domains=domain_limit,
                known_domains=known_domains,
                records_to_skip=cdx_resume_index
            )

            # Persist updated CDX resume index to DB so redeployments never lose progress
            async with AsyncSession(engine) as db_update:
                await set_scraper_state_db("cdx_resume_index", str(next_index), db_update)

            if not uk_domains:
                task_info["status"] = "failed"
                task_info["error"] = "No new UK domains available to scrape"
                task_info["completed_at"] = datetime.now(timezone.utc).isoformat()
                return

            task_info["progress"]["total_domains"] = len(uk_domains)
            task_info["urls"] = list(uk_domains)

            preferred_cat = category.upper() if category and category.upper() not in ("AUTO", "ALL", "WEB", "GENERAL") else None

            # Concurrency control: 8 parallel workers for high throughput and immediate progress updates
            semaphore = asyncio.Semaphore(8)
            results = []
            total_emails_found = 0
            total_emails_saved = 0
            duplicates_skipped = 0
            errors = 0
            domains_scraped = 0
            progress_lock = asyncio.Lock()

            async def process_single_domain(domain_url: str):
                nonlocal total_emails_found, total_emails_saved, duplicates_skipped, errors, domains_scraped
                if total_emails_found >= email_limit or task_info.get("cancel_requested"):
                    return

                async with semaphore:
                    if total_emails_found >= email_limit or task_info.get("cancel_requested"):
                        return

                    status_str = "no_emails"
                    extracted_emails = set()
                    pages_scanned = 0
                    cat_assigned = preferred_cat or "GENERAL"
                    subcat_assigned = None

                    try:
                        scraper = AdvancedDomainScraper(domain_url, preferred_category=preferred_cat)
                        extracted_emails = await scraper.run()
                        pages_scanned = len(scraper.visited_urls)
                        cat_assigned = preferred_cat if preferred_cat else scraper.category
                        subcat_assigned = scraper.subcategory

                        found_count = len(extracted_emails)
                        if found_count > 0:
                            status_str = "success"
                            save_result = await save_extracted_emails(
                                emails=set(extracted_emails),
                                category=cat_assigned,
                                subcategory=subcat_assigned,
                                domain=scraper.domain_netloc
                            )
                            async with progress_lock:
                                total_emails_found += found_count
                                total_emails_saved += save_result['saved']
                                duplicates_skipped += save_result['duplicates']
                                errors += save_result['failed']

                        async with progress_lock:
                            results.append({
                                "domain": str(domain_url),
                                "emails": list(extracted_emails),
                                "category": cat_assigned,
                                "subcategory": subcat_assigned,
                                "pages_scanned": pages_scanned,
                                "status": status_str
                            })

                    except Exception as dom_err:
                        status_str = "error"
                        async with progress_lock:
                            errors += 1
                            results.append({
                                "domain": str(domain_url),
                                "emails": [],
                                "pages_scanned": 0,
                                "status": "error",
                                "error": str(dom_err)
                            })

                    finally:
                        async with progress_lock:
                            domains_scraped += 1
                            task_info["progress"]["domains_scraped"] = domains_scraped
                            task_info["progress"]["emails_found"] = total_emails_found
                            task_info["progress"]["emails_saved"] = total_emails_saved
                            task_info["progress"]["duplicates_skipped"] = duplicates_skipped
                            task_info["progress"]["errors"] = errors
                            task_info["results"] = results

                        # Persist domain scrape status to PostgreSQL scraped_domains table
                        try:
                            async with AsyncSession(engine) as db_log:
                                await record_scraped_domain_db(
                                    domain=str(domain_url),
                                    status=status_str,
                                    emails_count=len(extracted_emails),
                                    category=cat_assigned,
                                    db=db_log
                                )
                        except Exception as log_err:
                            logger.warning(f"Could not persist scraped domain {domain_url} to DB: {log_err}")

            # Run workers concurrently across all discovered domains
            scrape_workers = [process_single_domain(dom) for dom in uk_domains]
            await asyncio.gather(*scrape_workers)

            task_info["status"] = "completed"
            task_info["completed_at"] = datetime.now(timezone.utc).isoformat()
            logger.info(f"✅ [Task {task_id}] Scrape to DB completed. Saved: {total_emails_saved}, Duplicates: {duplicates_skipped}, Scraped Domains: {domains_scraped}")

        except Exception as job_err:
            logger.error(f"❌ [Task {task_id}] Background scraping failed: {job_err}", exc_info=True)
            task_info["status"] = "failed"
            task_info["error"] = str(job_err)
            task_info["completed_at"] = datetime.now(timezone.utc).isoformat()

    async def _run_bulk_scrape_job(self, task_id: str, urls: List[str]):
        task_info = self.tasks[task_id]
        task_info["status"] = "running"
        task_info["started_at"] = datetime.now(timezone.utc).isoformat()

        try:
            domains = [str(u) for u in urls]
            semaphore = asyncio.Semaphore(3)
            tasks = [process_domain_task(domain, semaphore) for domain in domains]

            results = await asyncio.gather(*tasks)

            successful = sum(1 for r in results if r.get("status") == "success")
            total_emails = sum(len(r.get("emails", [])) for r in results)

            task_info["progress"]["domains_scraped"] = len(results)
            task_info["progress"]["emails_found"] = total_emails
            task_info["results"] = results
            task_info["status"] = "completed"
            task_info["completed_at"] = datetime.now(timezone.utc).isoformat()
            logger.info(f"✅ [Task {task_id}] Bulk scrape completed. Domains: {len(results)}, Successful: {successful}")

        except Exception as err:
            logger.error(f"❌ [Task {task_id}] Bulk scrape failed: {err}", exc_info=True)
            task_info["status"] = "failed"
            task_info["error"] = str(err)
            task_info["completed_at"] = datetime.now(timezone.utc).isoformat()

    def has_active_task(self) -> tuple[bool, Optional[str]]:
        """Check if any scrape task is currently running or pending."""
        for task_id, task_info in self.tasks.items():
            if task_info["status"] in ("running", "pending"):
                return True, task_id
        return False, None

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        return list(self.tasks.values())

    def cancel_task(self, task_id: str) -> bool:
        if task_id in self._running_async_tasks:
            async_task = self._running_async_tasks[task_id]
            if not async_task.done():
                async_task.cancel()
                if task_id in self.tasks:
                    self.tasks[task_id]["status"] = "cancelled"
                    self.tasks[task_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                return True
        return False


# Singleton task manager instance
scrape_task_manager = ScrapeTaskManager()

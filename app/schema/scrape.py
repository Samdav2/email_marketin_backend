from pydantic import BaseModel, HttpUrl
from typing import List

class DiscoverResponse(BaseModel):
    count: int
    domains: List[str]

class BulkScrapeRequest(BaseModel):
    urls: List[HttpUrl]

class LeadData(BaseModel):
    domain: str
    emails: List[str]
    status: str
    category: str | None = None
    subcategory: str | None = None
    country: str | None = None
    location: str | None = None

class BulkScrapeResponse(BaseModel):
    total_processed: int
    successful_leads: int
    results: List[LeadData]


class ScrapeToDBRequest(BaseModel):
    email_limit: int = 1000  # Number of emails to scrape before stopping (can go up to 200000)
    domain_limit: int = 100  # Number of domains to scrape (default 100, can go up to 100000)
    category: str = "AUTO"
    country: str | None = "UK"  # Target country e.g. "UK", "US", "CA", "AU", "DE", "FR", "ALL"
    location: str | None = None  # Optional specific city or place e.g. "London", "Manchester", "New York"

    class Config:
        from_attribute = True


class ScrapeToDBResponse(BaseModel):
    total_processed: int
    successful_leads: int
    total_emails_found: int
    total_emails_saved: int
    duplicates_skipped: int
    errors: int
    results: List[LeadData]


class ScrapeTaskResponse(BaseModel):
    task_id: str
    status: str
    request_type: str
    message: str
    progress: dict
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    results: List[dict] = []


class ScrapeTaskListResponse(BaseModel):
    total: int
    tasks: List[ScrapeTaskResponse]


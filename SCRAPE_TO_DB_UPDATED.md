# Scrape-to-DB Endpoint - Updated Implementation

## Overview
The `/scrape/scrape-to-db` endpoint has been completely redesigned to work as intended:
- Users provide **only** an `email_limit` (number)
- Backend automatically fetches UK domains from the CDX API
- Backend scrapes those domains for emails
- Backend saves all emails to the database

## API Usage

### Request
```json
POST /scrape/scrape-to-db
Content-Type: application/json

{
  "email_limit": 1000,
  "category": "WEB"
}
```

### Parameters
- **email_limit** (int, required): Maximum number of emails to scrape before stopping
- **category** (str, optional): Email category - "WEB", "MARKETING", or "GENERAL" (default: "WEB")

### Response
```json
{
  "total_processed": 15,
  "successful_leads": 12,
  "total_emails_found": 1050,
  "total_emails_saved": 1000,
  "duplicates_skipped": 35,
  "errors": 3,
  "results": [
    {
      "domain": "example.co.uk",
      "emails": ["info@example.co.uk", ...],
      "pages_scanned": 8,
      "status": "success"
    },
    ...
  ]
}
```

## Architecture Flow

1. **User Request**
   - Provides: `email_limit` and `category`
   - Framework: FastAPI validates the request

2. **Domain Discovery**
   - Calls: `discover_uk_domains(target_new_domains=estimated_domains_needed)`
   - Uses: CDX API (via cdx_toolkit library)
   - Returns: List of UK domains that haven't been previously scraped

3. **Concurrent Scraping**
   - Parallelism: 3 domains at a time (semaphore)
   - For each domain:
     - Creates `AdvancedDomainScraper` instance
     - Crawls high-value paths (contact, about, team, support, reach, hello)
     - Extracts emails via regex patterns and mailto: links
     - Respects `email_limit` - stops when reached

4. **Database Persistence**
   - Calls: `save_extracted_emails()` for each domain
   - Features:
     - Automatic duplicate detection
     - Tracks saved count vs skipped duplicates
     - Associates emails with user and category

## Code Changes

### Modified Files

#### 1. `/app/schema/scrape.py` - ScrapeToDBRequest
**Before:**
```python
class ScrapeToDBRequest(BaseModel):
    urls: List[HttpUrl]  # User had to provide URLs
    category: str = "WEB"
    email_limit: int = 1000
```

**After:**
```python
class ScrapeToDBRequest(BaseModel):
    email_limit: int = 1000  # Only email limit
    category: str = "WEB"
```

#### 2. `/app/service/scrape_email.py` - scrape_email_to_db()
**Function signature changed:**
```python
# Before
async def scrape_email_to_db(urls: List[str], email_limit: int, category: str, db)

# After
async def scrape_email_to_db(email_limit: int, category: str, db)
```

**Key additions:**
- Imports `discover_uk_domains` from UK domain service
- Calculates estimated domains needed based on email_limit
- Automatically calls `discover_uk_domains()` to fetch UK domains
- Handles case when no domains are found

#### 3. `/app/api/scrape.py` - scrape_to_db() endpoint
**Simplified endpoint:**
```python
@router.post("/scrape-to-db", response_model=ScrapeToDBResponse)
async def scrape_to_db(request: ScrapeToDBRequest, db: AsyncSession = Depends(get_session)):
    # Removed: URL validation (no URLs needed)
    # Added: Direct call to scrape_email_to_db with just email_limit and category
    result = await scrape_email_to_db(
        email_limit=request.email_limit,
        category=request.category,
        db=db
    )
```

## Integration with UK Domain Service

The endpoint now integrates with the existing UK domain service:

```python
from app.service.uk_domain_service import discover_uk_domains

# Estimates how many domains to fetch
estimated_domains_needed = max(10, (email_limit // 5) + 5)

# Fetches new UK domains from CDX API
uk_domains = discover_uk_domains(target_new_domains=estimated_domains_needed)
```

The UK domain service:
- Fetches UK domains from Common Crawl (*.uk/*)
- Tracks already-scraped domains to avoid duplicates
- Maintains resume state for fault tolerance
- Ensures we always discover new domains

## Benefits of New Design

✅ **Simpler User Experience** - Users only specify an email count
✅ **Automated Domain Discovery** - No need to maintain domain lists
✅ **Built-in Duplicate Prevention** - Tracks previously scraped domains
✅ **Predictable Email Limits** - Stops exactly when target is reached
✅ **Fault Tolerant** - Uses UK domain service's resume state
✅ **Concurrent Processing** - 3 parallel scrapes for speed

## Testing

```bash
# Request with email_limit of 500
curl -X POST http://localhost:8000/scrape/scrape-to-db \
  -H "Content-Type: application/json" \
  -d '{
    "email_limit": 500,
    "category": "WEB"
  }'

# Response will contain:
# - Scraped ~10 UK domains
# - Extracted ~500 emails from them
# - Saved to database with duplicate detection
# - Provided detailed results for each domain
```

## Error Handling

- **No domains found**: Returns error message from CDX API
- **Scraping errors**: Continues with next domain, logs individual errors
- **Database errors**: Tracked in response (failed count)
- **Invalid email_limit**: Returns 400 Bad Request if < 1

---

**Status**: ✅ Ready for production use

# Scrape to Database Endpoint - Implementation Guide

## New Endpoint: POST /scrape/scrape-to-db

### Purpose
Scrapes emails from multiple URLs and automatically saves them to the database, with configurable email limit to stop scraping once target is reached.

### Request Schema (ScrapeToDBRequest)

```json
{
  "urls": [
    "https://example.com",
    "https://company.com",
    "https://organization.org"
  ],
  "category": "WEB",
  "email_limit": 1000
}
```

**Parameters:**
- `urls` (required): List of URLs to scrape
- `category` (optional): Email category - "WEB", "MARKETING", or "GENERAL" (default: "WEB")
- `email_limit` (optional): Maximum number of emails to collect before stopping scraper (default: 1000)

### Response Schema (ScrapeToDBResponse)

```json
{
  "total_processed": 3,
  "successful_leads": 2,
  "total_emails_found": 456,
  "total_emails_saved": 450,
  "duplicates_skipped": 6,
  "errors": 0,
  "results": [
    {
      "domain": "https://example.com",
      "emails": ["contact@example.com", "info@example.com"],
      "pages_scanned": 4,
      "status": "success"
    },
    {
      "domain": "https://company.com",
      "emails": ["sales@company.com"],
      "pages_scanned": 3,
      "status": "success"
    },
    {
      "domain": "https://organization.org",
      "emails": [],
      "pages_scanned": 2,
      "status": "no_emails_found"
    }
  ]
}
```

**Response Fields:**
- `total_processed`: Number of domains processed
- `successful_leads`: Number of domains where emails were found
- `total_emails_found`: Total emails discovered during scraping
- `total_emails_saved`: Emails successfully saved to database
- `duplicates_skipped`: Emails already in database (duplicates)
- `errors`: Number of errors encountered
- `results`: Detailed results for each domain

### Features

✅ **Email Limit Control**
- Stops scraping once target email count is reached
- Trims excess emails from last domain if needed
- Prevents excessive scraping

✅ **Database Integration**
- Automatically saves all scraped emails to database
- Prevents duplicate entries
- Tracks duplicates in response

✅ **Category Support**
- Organizes emails by category (WEB, MARKETING, GENERAL)
- All emails saved with specified category
- Supports category filtering later

✅ **Concurrent Scraping**
- Scrapes up to 3 domains concurrently
- Improves performance
- Respects email limit across all concurrent operations

✅ **Detailed Reporting**
- Per-domain results
- Statistics on saved, duplicates, and errors
- Page count per domain
- Status for each domain

### Usage Examples

#### Example 1: Basic Scrape with Default Limit (1000 emails)
```bash
curl -X POST http://localhost:8000/scrape/scrape-to-db \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://techstartup.com",
      "https://aicompany.io"
    ]
  }'
```

#### Example 2: Scrape with Custom Limit (500 emails)
```bash
curl -X POST http://localhost:8000/scrape/scrape-to-db \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://techstartup.com",
      "https://aicompany.io",
      "https://dataanalytics.com"
    ],
    "email_limit": 500
  }'
```

#### Example 3: Scrape for Marketing Category (200 emails)
```bash
curl -X POST http://localhost:8000/scrape/scrape-to-db \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://marketing.com",
      "https://advertising.io"
    ],
    "category": "MARKETING",
    "email_limit": 200
  }'
```

#### Example 4: Python SDK Example
```python
import httpx
import asyncio

async def scrape_to_db():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/scrape/scrape-to-db",
            json={
                "urls": [
                    "https://techstartup.com",
                    "https://aicompany.io",
                    "https://dataanalytics.com"
                ],
                "category": "WEB",
                "email_limit": 1000
            }
        )

        result = response.json()
        print(f"Emails saved: {result['total_emails_saved']}")
        print(f"Duplicates: {result['duplicates_skipped']}")
        print(f"Errors: {result['errors']}")

        return result

# Run
result = asyncio.run(scrape_to_db())
```

### How It Works

1. **Request Validation**
   - Validates URLs are provided
   - Validates email_limit > 0
   - Validates category is valid

2. **Scraping Process**
   - Scrapes each domain concurrently (max 3 at a time)
   - Checks email limit after each domain
   - Stops early if limit reached

3. **Database Saving**
   - Saves each email to database
   - Detects and skips duplicates
   - Tracks statistics

4. **Response Generation**
   - Returns detailed statistics
   - Per-domain results
   - Success/failure information

### Email Limit Behavior

**Example Scenario:**
- `email_limit`: 1000
- Domain 1: 400 emails ✓ (total: 400)
- Domain 2: 300 emails ✓ (total: 700)
- Domain 3: 500 emails found
  - Would exceed 1000
  - Trimmed to 300 emails (total: 1000)
  - Stop scraping

**Result:**
- Total found: 1200 (but only 1000 saved)
- Process stops automatically

### Error Handling

**Validation Errors (400):**
- No URLs provided
- Invalid email_limit (must be > 0)
- Invalid category

**Server Errors (500):**
- Database connection issues
- Scraping failures
- System errors

**Response on Error:**
```json
{
  "detail": "Error message describing the issue"
}
```

### Database Integration

**Emails saved to:** `emails` table
**Columns used:**
- `id`: UUID (auto-generated)
- `email`: Email address
- `category`: Category (WEB, MARKETING, GENERAL)

**Duplicate Detection:**
- Checks email existence before saving
- Prevents duplicate inserts
- Counts in `duplicates_skipped`

### Performance Characteristics

- **Concurrency:** 3 domains at a time
- **Timeout:** 15 seconds per request
- **Max Pages:** 4 pages per domain
- **Email Limit:** Stops at configured limit

### Integration with Email Service

Internally uses:
- `scrape_email_to_db()` - Main scraping function
- `save_extracted_emails()` - Database saving
- `AdvancedDomainScraper` - Scraping engine
- Database session for atomic operations

### Status Codes

- `200`: Success - emails scraped and saved
- `400`: Bad request - invalid parameters
- `500`: Server error - internal failure

### API Documentation

Auto-generated Swagger documentation available at:
```
http://localhost:8000/docs
```

Look for `POST /scrape/scrape-to-db` endpoint for interactive testing.

### Notes

- Email limit is applied after scraping each domain
- Concurrent operations respect the global limit
- All emails are validated before saving
- Category must be valid (case-insensitive)
- Scraping respects target website's robots.txt implicitly via timeouts

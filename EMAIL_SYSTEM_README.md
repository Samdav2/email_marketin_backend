# Email Marketing System Implementation

This document describes the SMTP email system implementation for the Email Marketing project.

## Overview

The system includes:
- **SMTP Email Service**: Send individual and bulk emails via SMTP
- **Email Repository**: Save extracted emails to the database
- **Email Service Layer**: Business logic for email operations
- **Email API Endpoints**: REST API for email management

## Architecture

### Components

1. **`app/core/settings.py`**
   - SMTP configuration (host, port, username, password, from email)
   - Settings loaded from environment variables

2. **`app/dependencies/smtp_email.py`**
   - `SMTPEmailService` class for SMTP operations
   - `send_email()`: Send email to a single recipient
   - `send_bulk_email()`: Send emails to multiple recipients
   - Singleton instance: `email_service`

3. **`app/service/email_service.py`**
   - `save_extracted_emails()`: Save scraped emails to database
   - `send_email_campaign()`: Send emails to all addresses in a category
   - `send_email_to_specific()`: Send email to specific recipient
   - Duplicate detection and error handling

4. **`app/repo/email.py`** (Updated)
   - `save_email()`: Save single email
   - `save_multiple_emails()`: Save multiple emails
   - `get_all_email()`: Retrieve all emails
   - `get_email_by_category()`: Retrieve emails by category
   - `email_exists()`: Check if email exists
   - `get_email_count()`: Get total email count

5. **`app/api/email.py`**
   - `/email/send` - POST: Send email to specific recipient
   - `/email/campaign` - POST: Send campaign to category
   - `/email/save-batch` - POST: Save batch of emails
   - `/email/by-category/{category}` - GET: Get emails by category
   - `/email/all` - GET: Get all emails
   - `/email/stats` - GET: Get email statistics

## Setup

### 1. Environment Variables

Create a `.env` file with the following SMTP configuration:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost/email_marketing

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=Email Marketing
```

**Note for Gmail Users:**
- Use App Passwords instead of your regular password
- Enable 2-Step Verification on your Google Account
- Generate an App Password at https://myaccount.google.com/apppasswords

### 2. Required Packages

The following packages are required (add to requirements.txt if not already present):
- `fastapi`
- `sqlmodel`
- `sqlalchemy[asyncio]`
- `python-dotenv`
- `pydantic[email]`
- `pydantic-settings`

## API Endpoints

### Send Email to Specific Recipient
```http
POST /email/send
Content-Type: application/json

{
  "recipient": "user@example.com",
  "subject": "Hello",
  "body": "This is a test email",
  "is_html": false
}
```

### Send Email Campaign to Category
```http
POST /email/campaign
Content-Type: application/json

{
  "category": "WEB",
  "subject": "Marketing Campaign",
  "body": "<h1>Welcome!</h1>",
  "is_html": true
}
```

### Save Extracted Emails
```http
POST /email/save-batch
Content-Type: application/json

{
  "emails": ["user1@example.com", "user2@example.com"],
  "category": "WEB"
}
```

### Get Emails by Category
```http
GET /email/by-category/WEB
```

### Get All Emails
```http
GET /email/all
```

### Get Email Statistics
```http
GET /email/stats
```

## Usage Example

### 1. Save Extracted Emails from Scraper
After scraping emails from a domain, save them to the database:

```python
from app.service.email_service import save_extracted_emails
from app.model.emails import Category

# Assume extracted_emails is a Set[str] from scraper
results = await save_extracted_emails(
    extracted_emails,
    Category.web,
    db_session
)

print(f"Saved: {results['saved']}, Duplicates: {results['duplicates']}")
```

### 2. Send Campaign to All Emails in Category
```python
from app.service.email_service import send_email_campaign
from app.model.emails import Category

results = await send_email_campaign(
    category=Category.web,
    subject="Special Offer",
    body="Check out our amazing products!",
    is_html=False,
    db=db_session
)

print(f"Sent: {results['successful']}, Failed: {results['failed']}")
```

### 3. Send Email to Specific Address
```python
from app.service.email_service import send_email_to_specific

success = await send_email_to_specific(
    recipient="user@example.com",
    subject="Test",
    body="This is a test",
    is_html=False
)
```

## Email Categories

Available categories (from `app/model/emails.py`):
- `WEB` - Emails from web scraping
- `MARKETING` - Marketing email list
- `GENERAL` - General emails

## Error Handling

The system includes comprehensive error handling:
- **Duplicate Detection**: Prevents saving duplicate emails
- **SMTP Errors**: Logged and tracked in results
- **Database Errors**: Rolled back on failure
- **Validation**: Email format validation using Pydantic

## Logging

All operations are logged using Python's logging module. Configure logging to monitor:
- Email send operations
- Database saves
- SMTP connection errors
- Duplicate detections

## Integration with Scraper

To integrate with the existing scraper (`app/service/scrape_email.py`):

1. After scraping completes and emails are extracted
2. Call `save_extracted_emails()` to store in database
3. Optionally send campaign or individual emails

## Testing

Use the provided API endpoints with a tool like curl or Postman:

```bash
# Test saving emails
curl -X POST http://localhost:8000/email/save-batch \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["test1@example.com", "test2@example.com"],
    "category": "WEB"
  }'

# Test sending email
curl -X POST http://localhost:8000/email/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "test@example.com",
    "subject": "Test",
    "body": "Test email",
    "is_html": false
  }'

# Get all emails
curl http://localhost:8000/email/all
```

## Performance Considerations

- **Bulk Operations**: Use `send_bulk_email()` for better performance with many recipients
- **Database**: Consider indexing on `email` and `category` fields
- **SMTP Rate Limiting**: Some providers may have rate limits
- **Connection Pooling**: SMTP connections are closed after each send

## Security Notes

1. **Environment Variables**: Keep SMTP credentials in `.env`, never commit to version control
2. **Email Validation**: All recipients are validated with Pydantic
3. **Error Messages**: Detailed errors are logged but generic responses sent to API clients
4. **Sensitive Data**: Passwords are not logged or returned in responses

## Troubleshooting

### "Failed to send email: [Errno 111] Connection refused"
- Verify SMTP_HOST and SMTP_PORT are correct
- Check firewall/network connectivity to SMTP server

### "Failed to send email: 535 5.7.3 Authentication failed"
- Verify SMTP_USERNAME and SMTP_PASSWORD are correct
- For Gmail: Ensure App Password is used, not regular password

### "Duplicate email" warnings
- This is normal and expected
- Duplicates are tracked separately in results

### Emails not appearing in database
- Check database connection string
- Verify Database migrations completed
- Check for roll-back errors in logs

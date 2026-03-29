# Email Management System - Complete Guide

## Overview

The email management system provides three core features:

1. **Email List Management** - Get all scraped emails from the database
2. **Email Templates** - 10 professional, pre-built HTML email templates
3. **Email Sending** - Send personalized emails (single & bulk) using templates

---

## 1. Email List Management

### Get All Emails from Database

**Endpoint:** `GET /emails/all`

Returns all unique emails collected from domain scraping.

**Example Request:**
```bash
curl -X GET http://localhost:8000/emails/all
```

**Example Response:**
```json
{
  "total": 1250,
  "emails": [
    "info@example.co.uk",
    "contact@business.co.uk",
    "sales@company.com",
    ...
  ]
}
```

**Response Fields:**
- `total` (int): Total number of unique emails in database
- `emails` (array): List of all email addresses

---

## 2. Email Templates

### 10 Professional Email Templates Included

The system comes with 10 pre-built, professional HTML email templates:

| # | Template Name | Type | Purpose |
|---|---|---|---|
| 1 | Newsletter - Monthly Digest | Newsletter | Monthly updates and content digest |
| 2 | Promotional - Special Offer | Promotional | Discount and special offers |
| 3 | Announcement - Company Update | Announcement | Important company announcements |
| 4 | Product Launch | Product | New product introductions |
| 5 | Event Invitation | Event | Event invitations with registration |
| 6 | Webinar Invitation | Webinar | Webinar sign-ups and details |
| 7 | Onboarding Welcome | Onboarding | Welcome email for new users |
| 8 | Feedback Request | Feedback | Customer feedback surveys |
| 9 | Retention - Win Back | Retention | Re-engagement campaigns |
| 10 | Sales - Follow Up | Sales | Sales follow-up emails |

### List All Templates

**Endpoint:** `GET /emails/templates`

**Example Request:**
```bash
curl -X GET http://localhost:8000/emails/templates
```

**Example Response:**
```json
[
  {
    "id": "uuid-string",
    "name": "Newsletter - Monthly Digest",
    "template_type": "NEWSLETTER",
    "subject": "Your Monthly Digest - {month}",
    "body": "<html>...</html>",
    "description": "Professional monthly newsletter digest",
    "is_active": true
  },
  ...
]
```

### Get Specific Template

**Endpoint:** `GET /emails/templates/{template_id}`

**Example Request:**
```bash
curl -X GET http://localhost:8000/emails/templates/abc123def456
```

### Create Custom Template

**Endpoint:** `POST /emails/templates`

**Request Body:**
```json
{
  "name": "Custom Template Name",
  "template_type": "NEWSLETTER",
  "subject": "Your Subject Line - {variable}",
  "body": "<html>Your HTML content here</html>",
  "description": "Optional description"
}
```

**Available Template Types:**
- `NEWSLETTER`
- `PROMOTIONAL`
- `ANNOUNCEMENT`
- `PRODUCT`
- `EVENT`
- `WEBINAR`
- `ONBOARDING`
- `FEEDBACK`
- `RETENTION`
- `SALES`

### Update Template

**Endpoint:** `PATCH /emails/templates/{template_id}`

**Request Body (all fields optional):**
```json
{
  "name": "Updated Name",
  "subject": "Updated Subject",
  "body": "<html>Updated HTML</html>",
  "is_active": false
}
```

### Delete Template

**Endpoint:** `DELETE /emails/templates/{template_id}`

---

## 3. Email Sending

### Send Email to Single Recipient

**Endpoint:** `POST /emails/send`

**Request Body:**
```json
{
  "recipient_email": "contact@example.com",
  "template_id": "abc123def456",
  "variables": {
    "name": "John Doe",
    "month": "March",
    "discount": "25",
    "link": "https://example.com/offer"
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "message": "Email sent to contact@example.com",
  "recipient": "contact@example.com"
}
```

### Send Bulk Emails

**Endpoint:** `POST /emails/send-bulk`

Send personalized emails to up to 100,000 recipients in batch.

**Request Body:**
```json
{
  "recipient_emails": [
    "contact1@example.com",
    "contact2@example.com",
    "contact3@example.com"
  ],
  "template_id": "abc123def456",
  "variables": {
    "name": "Customer",
    "discount": "20",
    "offer_link": "https://example.com/promo"
  }
}
```

**Example Response:**
```json
{
  "total_recipients": 3,
  "successful": 3,
  "failed": 0,
  "errors": []
}
```

**Response Fields:**
- `total_recipients`: Number of recipients to send
- `successful`: Number of emails sent successfully
- `failed`: Number of emails that failed
- `errors`: Array of error details (up to 10 errors shown)

---

## Using Template Variables

Templates use `{variable_name}` syntax for dynamic content.

### Examples:

**Template Body:**
```html
<p>Hello {name},</p>
<p>We're offering {discount}% off!</p>
<a href="{link}">Claim Offer</a>
```

**Variables Dict:**
```json
{
  "name": "John",
  "discount": "25",
  "link": "https://example.com/offer"
}
```

**Result:**
```html
<p>Hello John,</p>
<p>We're offering 25% off!</p>
<a href="https://example.com/offer">Claim Offer</a>
```

### Common Variables by Template Type

**Newsletter:**
- `{name}`: Recipient name
- `{month}`: Current/relevant month

**Promotional:**
- `{name}`: Recipient name
- `{discount}`: Discount percentage
- `{link}`: Offer link
- `{expiry_date}`: When offer expires

**Event:**
- `{name}`: Recipient name
- `{event_name}`: Event title
- `{event_location}`: Event location
- `{event_date}`: Event date
- `{event_time}`: Event time
- `{event_link}`: Registration link

**Product Launch:**
- `{name}`: Recipient name
- `{product_name}`: New product name
- `{product_link}`: Product link

**Webinar:**
- `{name}`: Recipient name
- `{topic}`: Webinar topic
- `{webinar_date}`: Webinar date
- `{webinar_time}`: Webinar time
- `{speaker_name}`: Speaker name
- `{duration}`: Session duration
- `{webinar_link}`: Join link

**Sales Follow-up:**
- `{name}`: Recipient name
- `{product}`: Product name
- `{sales_rep_name}`: Sales rep name
- `{calendar_link}`: Calendar/scheduling link

---

## Complete Workflow Example

### Step 1: Get Available Templates

```bash
curl -X GET http://localhost:8000/emails/templates
```

### Step 2: Get Your Email List

```bash
curl -X GET http://localhost:8000/emails/all
```

### Step 3: Send to All Contacts

```bash
curl -X POST http://localhost:8000/emails/send-bulk \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_emails": ["email1@test.com", "email2@test.com"],
    "template_id": "template-uuid-here",
    "variables": {
      "name": "Valued Customer",
      "discount": "30",
      "link": "https://mysite.com/offer"
    }
  }'
```

---

## Error Handling

### Email Not Found
```json
{
  "detail": "Template abc123 not found"
}
```

### Invalid Input
```json
{
  "detail": "Recipient list cannot be empty"
}
```

### Bulk Limit Exceeded
```json
{
  "detail": "Cannot send to more than 100,000 recipients at once"
}
```

---

## Performance Notes

- **Bulk Sending:** Processed in batches of 10 for optimal performance
- **Concurrent Processing:** Uses asyncio for fast, non-blocking execution
- **Template Types:** Organized by purpose for easy selection
- **Variable Rendering:** Supports unlimited custom variables per email

---

## API Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/emails/all` | Get all emails from database |
| GET | `/emails/templates` | List all templates |
| GET | `/emails/templates/{id}` | Get specific template |
| POST | `/emails/templates` | Create new template |
| PATCH | `/emails/templates/{id}` | Update template |
| DELETE | `/emails/templates/{id}` | Delete template |
| POST | `/emails/send` | Send single email |
| POST | `/emails/send-bulk` | Send bulk emails |

---

**Status:** ✅ Production Ready

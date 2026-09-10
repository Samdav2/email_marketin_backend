# Email Marketing Backend - Complete API Documentation

**Version:** 1.1
**Base URL:** `http://localhost:8000`
**Framework:** FastAPI + SQLModel
**Database:** PostgreSQL
**Authentication:** JWT Bearer Tokens

---

## Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
2. [Email Management Endpoints](#email-management-endpoints)
3. [Email Scraping Endpoints](#email-scraping-endpoints)
4. [Data Models & Schemas](#data-models--schemas)
5. [Error Handling](#error-handling)
6. [Template Types](#template-types)
7. [Usage Examples](#usage-examples)

---

## Authentication Endpoints

### Base Path: `/auth`

All endpoints except signup/login/forgot-password require JWT authentication via `Authorization: Bearer <token>` header.

---

#### **POST** `/auth/signup`
**Create New User Account**

Create a new user and automatically send welcome email in background.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Request Schema:**
- `name` (string, required): User's full name, 2-100 characters
- `email` (string, required): Valid email address
- `password` (string, required): Minimum 8 characters

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-string",
    "name": "John Doe",
    "email": "john@example.com",
    "is_active": true,
    "created_at": "2026-03-28T10:30:00"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Email already exists or validation failed
- `500 Internal Server Error`: Server error during signup

**Notes:**
- Welcome email sent asynchronously (non-blocking)
- Password automatically hashed with bcrypt
- JWT token valid for 30 days

---

#### **POST** `/auth/login`
**User Login**

Authenticate user and receive access token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Request Schema:**
- `email` (string, required): User's email
- `password` (string, required): User's password

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-string",
    "name": "John Doe",
    "email": "john@example.com",
    "is_active": true,
    "created_at": "2026-03-28T10:30:00"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid email or password
- `500 Internal Server Error`: Server error

**Notes:**
- Token type is always "bearer"
- Use token in `Authorization: Bearer <token>` header for subsequent requests

---

#### **POST** `/auth/reset-password`
**Reset Password (Authenticated)**

Change password for authenticated user. Requires current password.

**Request Body:**
```json
{
  "email": "john@example.com",
  "old_password": "OldPass123",
  "new_password": "NewPass456"
}
```

**Request Schema:**
- `email` (string, required): User's email
- `old_password` (string, required): Current password
- `new_password` (string, required): New password (minimum 8 characters)

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Old password incorrect or new password validation failed
- `401 Unauthorized`: User not authenticated
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

---

#### **POST** `/auth/forgot-password`
**Forgot Password (Send Reset Email)**

Send password reset email to user. Works without authentication.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Request Schema:**
- `email` (string, required): User's email address

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password reset email sent. Check your inbox."
}
```

**Error Responses:**
- `500 Internal Server Error`: Email sending failed

**Notes:**
- Email sent asynchronously (non-blocking)
- Safe to call even if email doesn't exist (no user enumeration)
- Reset link expires after 24 hours

---

#### **GET** `/auth/me`
**Get Current User Information**

Retrieve authenticated user's profile information.

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "name": "John Doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-03-28T10:30:00"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

---

#### **POST** `/auth/profile`
**Create or Update User Profile**

Create new or update existing user business profile.

**Request Body:**
```json
{
  "business_name": "Acme Corporation",
  "company_id": "ACME001",
  "phone": "+1-555-0100",
  "website": "https://example.com",
  "address": "123 Business St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "United States",
  "industry": "Technology",
  "company_size": "50-100",
  "description": "Leading tech company",
  "logo_url": "https://example.com/logo.png"
}
```

**Request Schema:**
- `business_name` (string, required): 2-255 characters
- `company_id` (string, required): Unique company identifier, 1-50 characters
- `phone` (string, optional): Phone number
- `website` (string, optional): Company website URL
- `address` (string, optional): Street address
- `city` (string, optional): City name
- `state` (string, optional): State/Province
- `postal_code` (string, optional): Zip/Postal code
- `country` (string, optional): Country name
- `industry` (string, optional): Industry type
- `company_size` (string, optional): Employee count range
- `description` (string, optional): Company description
- `logo_url` (string, optional): Logo image URL

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "user_id": "user-uuid",
  "business_name": "Acme Corporation",
  "company_id": "ACME001",
  "phone": "+1-555-0100",
  "website": "https://example.com",
  "address": "123 Business St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "United States",
  "industry": "Technology",
  "company_size": "50-100",
  "description": "Leading tech company",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2026-03-28T10:30:00",
  "updated_at": "2026-03-28T11:45:00"
}
```

**Error Responses:**
- `400 Bad Request`: Company ID already exists or validation failed
- `401 Unauthorized`: User not authenticated
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

**Notes:**
- Company ID must be unique across system
- Updates all provided fields (pass null to clear optional fields)

---

#### **GET** `/auth/profile`
**Get User Profile**

Retrieve authenticated user's profile information.

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "user_id": "user-uuid",
  "business_name": "Acme Corporation",
  "company_id": "ACME001",
  "phone": "+1-555-0100",
  "website": "https://example.com",
  "address": "123 Business St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "United States",
  "industry": "Technology",
  "company_size": "50-100",
  "description": "Leading tech company",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2026-03-28T10:30:00",
  "updated_at": "2026-03-28T11:45:00"
}
```

**Error Responses:**
- `401 Unauthorized`: User not authenticated
- `404 Not Found`: Profile not found
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

---

#### **GET** `/auth/profile/full`
**Get User with Full Profile Information**

Retrieve authenticated user's complete information including profile.

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "name": "John Doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-03-28T10:30:00",
  "profile": {
    "id": "profile-uuid",
    "user_id": "user-uuid",
    "business_name": "Acme Corporation",
    "company_id": "ACME001",
    "phone": "+1-555-0100",
    "website": "https://example.com",
    "address": "123 Business St",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "United States",
    "industry": "Technology",
    "company_size": "50-100",
    "description": "Leading tech company",
    "logo_url": "https://example.com/logo.png",
    "created_at": "2026-03-28T10:30:00",
    "updated_at": "2026-03-28T11:45:00"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: User not authenticated
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

**Notes:**
- Profile field is null if user hasn't created profile yet

---

## Email Management Endpoints

### Base Path: `/emails`

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

---

#### **GET** `/emails/all`
**Get All Scraped Emails**

Retrieve all unique emails collected from scraping operations.

**Response (200 OK):**
```json
{
  "total": 1250,
  "emails": [
    "contact@example1.com",
    "info@example2.com",
    "sales@example3.com",
    ...
  ]
}
```

**Response Schema:**
- `total` (integer): Total count of unique emails
- `emails` (array): List of email addresses

**Error Responses:**
- `401 Unauthorized`: User not authenticated
- `500 Internal Server Error`: Database error

**Authentication:** Required (Bearer Token)

**Use Cases:**
- Display scraped email list in frontend
- Export emails for campaigns
- Manage existing email database

---

#### **GET** `/emails/templates`
**List All Email Templates**

Get all available professional email templates.

**Response (200 OK):**
```json
[
  {
    "id": "template-uuid-1",
    "name": "Newsletter Template",
    "template_type": "NEWSLETTER",
    "subject": "Your Weekly Newsletter",
    "body": "<html>...</html>",
    "description": "Professional weekly newsletter template",
    "is_active": true
  },
  {
    "id": "template-uuid-2",
    "name": "Sales Follow-up",
    "template_type": "SALES",
    "subject": "Special Offer Inside",
    "body": "<html>...</html>",
    "description": "Sales outreach template",
    "is_active": true
  },
  ...
]
```

**Error Responses:**
- `401 Unauthorized`: User not authenticated
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

**Available Template Types:**
- `NEWSLETTER` - Weekly/monthly newsletters
- `PROMOTIONAL` - Marketing promotions
- `ANNOUNCEMENT` - Important announcements
- `PRODUCT` - Product launch/updates
- `EVENT` - Event invitations
- `WEBINAR` - Webinar registrations
- `ONBOARDING` - New user welcome
- `FEEDBACK` - Customer feedback requests
- `RETENTION` - Customer retention offers
- `SALES` - Sales outreach

**Notes:**
- 10 default professional templates pre-loaded
- Templates are automatically initialized on first access
- All templates include HTML/CSS styling

---

#### **GET** `/emails/templates/{template_id}`
**Get Specific Email Template**

Retrieve detailed information about a single template.

**Path Parameters:**
- `template_id` (string, required): UUID of the template

**Response (200 OK):**
```json
{
  "id": "template-uuid",
  "name": "Newsletter Template",
  "template_type": "NEWSLETTER",
  "subject": "Your Weekly Newsletter",
  "body": "<html><body>...</body></html>",
  "description": "Professional weekly newsletter template",
  "is_active": true
}
```

**Error Responses:**
- `401 Unauthorized`: User not authenticated
- `404 Not Found`: Template not found
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

**Use Cases:**
- Preview template before sending
- Get template content for editing
- Check template details

---

#### **POST** `/emails/templates`
**Create New Email Template**

Create a custom email template.

**Request Body:**
```json
{
  "name": "Custom Campaign",
  "template_type": "PROMOTIONAL",
  "subject": "Exclusive Offer - {company_name}",
  "body": "<html><body><h1>Hello {recipient_name}</h1><p>We have an exclusive offer for you...</p></body></html>",
  "description": "Custom promotional template with dynamic variables"
}
```

**Request Schema:**
- `name` (string, required): Template name
- `template_type` (string, required): One of the template types listed above
- `subject` (string, required): Email subject line
- `body` (string, required): HTML email body
- `description` (string, optional): Template description

**Response (201 Created):**
```json
{
  "id": "new-template-uuid",
  "name": "Custom Campaign",
  "template_type": "PROMOTIONAL",
  "subject": "Exclusive Offer - {company_name}",
  "body": "<html><body>...</body></html>",
  "description": "Custom promotional template with dynamic variables",
  "is_active": true
}
```

**Error Responses:**
- `400 Bad Request`: Validation failed
- `401 Unauthorized`: User not authenticated
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

**Notes:**
- Use `{variable_name}` for dynamic content in subject/body
- HTML is stored as-is (include complete HTML tags)
- Templates are immediately active after creation

---

#### **PATCH** `/emails/templates/{template_id}`
**Update Email Template**

Modify an existing template.

**Path Parameters:**
- `template_id` (string, required): UUID of the template

**Request Body (all optional):**
```json
{
  "name": "Updated Template Name",
  "template_type": "PROMOTIONAL",
  "subject": "Updated Subject",
  "body": "<html><body>Updated content</body></html>",
  "description": "Updated description",
  "is_active": false
}
```

**Request Schema:**
- `name` (string, optional): New template name
- `template_type` (string, optional): New template type
- `subject` (string, optional): New subject line
- `body` (string, optional): New HTML body
- `description` (string, optional): New description
- `is_active` (boolean, optional): Activate/deactivate template

**Response (200 OK):**
```json
{
  "id": "template-uuid",
  "name": "Updated Template Name",
  "template_type": "PROMOTIONAL",
  "subject": "Updated Subject",
  "body": "<html><body>Updated content</body></html>",
  "description": "Updated description",
  "is_active": false
}
```

**Error Responses:**
- `400 Bad Request`: Validation failed
- `401 Unauthorized`: User not authenticated
- `404 Not Found`: Template not found
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

**Notes:**
- Only provided fields are updated
- Other fields remain unchanged

---

#### **DELETE** `/emails/templates/{template_id}`
**Delete Email Template**

Remove a template from the system.

**Path Parameters:**
- `template_id` (string, required): UUID of the template

**Response (200 OK):**
```json
{
  "message": "Template deleted successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: User not authenticated
- `404 Not Found`: Template not found
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

**Notes:**
- Deletion is permanent
- Cannot delete system default templates (recommended)

---

#### **POST** `/emails/send`
**Send Single Email**

Send an email to one recipient using a template.

**Request Body:**
```json
{
  "recipient_email": "customer@example.com",
  "template_id": "template-uuid",
  "variables": {
    "recipient_name": "John",
    "company_name": "Acme Corp",
    "offer_percentage": "20%"
  }
}
```

**Request Schema:**
- `recipient_email` (string, required): Valid email address
- `template_id` (string, required): UUID of template to use
- `variables` (object, optional): Dynamic variables for template placeholders

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Email sent to customer@example.com",
  "recipient": "customer@example.com"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid email or template not found
- `401 Unauthorized`: User not authenticated
- `500 Internal Server Error`: Email sending failed

**Authentication:** Required (Bearer Token)

**Use Cases:**
- Send personalized emails
- Follow-up communications
- One-off announcements

**Notes:**
- Email sent immediately (synchronously)
- Uses Mailjet SMTP for delivery
- Variables are case-sensitive

---

#### **POST** `/emails/send-bulk`
**Send Bulk Emails**

Send emails to multiple recipients using a template. Processed in batches of 10.

**Request Body:**
```json
{
  "recipient_emails": [
    "customer1@example.com",
    "customer2@example.com",
    "customer3@example.com",
    ...
  ],
  "template_id": "template-uuid",
  "variables": {
    "company_name": "Acme Corp",
    "sender_name": "Marketing Team"
  }
}
```

**Request Schema:**
- `recipient_emails` (array, required): List of valid email addresses (max 100,000)
- `template_id` (string, required): UUID of template to use
- `variables` (object, optional): Shared variables for all recipients

**Response (200 OK):**
```json
{
  "total_recipients": 1250,
  "successful": 1245,
  "failed": 5,
  "errors": [
    {
      "email": "invalid@example",
      "reason": "Invalid email format"
    },
    {
      "email": "failed@example.com",
      "reason": "SMTP error: Connection timeout"
    }
  ]
}
```

**Response Schema:**
- `total_recipients` (integer): Total emails in request
- `successful` (integer): Successfully sent
- `failed` (integer): Failed to send
- `errors` (array): List of failed email details

**Error Responses:**
- `400 Bad Request`: Invalid request (empty list, > 100k, template not found)
- `401 Unauthorized`: User not authenticated
- `500 Internal Server Error`: Server error

**Authentication:** Required (Bearer Token)

**Use Cases:**
- Newsletter distribution
- Campaign launches
- Bulk promotions

**Notes:**
- Processed in batches of 10 for optimal performance
- Partial success is possible (some emails sent, some failed)
- Failed emails listed in response
- Maximum 100,000 recipients per request
- Individual email variables can be added via variables object

---

## Email Scraping Endpoints

### Base Path: `/scrape`

---

#### **POST** `/scrape/scrape-to-db`
**Scrape UK Domains and Save Emails to Database**

Automatically discover UK domains, scrape emails from them, and save to database.

**Request Body:**
```json
{
  "email_limit": 1000,
  "domain_limit": 100,
  "category": "WEB"
}
```

**Request Schema:**
- `email_limit` (integer, optional, default=1000): Maximum emails to scrape before stopping
- `domain_limit` (integer, optional, default=100): Number of UK domains to process (max 10,000)
- `category` (string, optional, default="WEB"): Email category for classification

**Response (200 OK):**
```json
{
  "total_processed": 100,
  "successful_leads": 95,
  "total_emails_found": 450,
  "total_emails_saved": 380,
  "duplicates_skipped": 70,
  "errors": 5,
  "results": [
    {
      "domain": "example.com",
      "emails": [
        "contact@example.com",
        "info@example.com"
      ],
      "status": "success"
    },
    {
      "domain": "failed-domain.com",
      "emails": [],
      "status": "error"
    }
  ]
}
```

**Response Schema:**
- `total_processed` (integer): Total domains processed
- `successful_leads` (integer): Domains with successful scraping
- `total_emails_found` (integer): Total emails found across all domains
- `total_emails_saved` (integer): New emails added to database
- `duplicates_skipped` (integer): Emails already in database
- `errors` (integer): Failed domain scrapes
- `results` (array): Detailed results per domain

**Error Responses:**
- `400 Bad Request`: Invalid parameters (email_limit < 1, domain_limit > 10000)
- `500 Internal Server Error`: Server error

**Request Validation:**
- `email_limit` must be ≥ 1
- `domain_limit` must be ≥ 1 and ≤ 10,000

**Use Cases:**
- Build email database
- Lead generation
- Market research
- Contact list building

**Features:**
- Uses CDX (Common Crawl) API for domain discovery
- Concurrent scraping with semaphore (3 simultaneous)
- Resume state tracking (cdx_resume_state.txt)
- Automatic duplicate detection
- Email validation

**Notes:**
- Operation may take several minutes depending on domain_limit
- Suspended domains are tracked and skipped on future runs
- Results include success/error details per domain
- Emails stored with WEB category by default

---

## Data Models & Schemas

### User Model

```json
{
  "id": "uuid-string",
  "name": "John Doe",
  "email": "john@example.com",
  "password_hash": "bcrypt-hash",
  "is_active": true,
  "created_at": "2026-03-28T10:30:00"
}
```

### Profile Model

```json
{
  "id": "uuid-string",
  "user_id": "user-uuid",
  "business_name": "Acme Corporation",
  "company_id": "ACME001",
  "phone": "+1-555-0100",
  "website": "https://example.com",
  "address": "123 Business St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "United States",
  "industry": "Technology",
  "company_size": "50-100",
  "description": "Company description",
  "logo_url": "https://example.com/logo.png",
  "created_at": "2026-03-28T10:30:00",
  "updated_at": "2026-03-28T11:45:00"
}
```

### Email Model

```json
{
  "id": "uuid-string",
  "email": "contact@example.com",
  "domain": "example.com",
  "category": "WEB",
  "is_verified": false,
  "created_at": "2026-03-28T10:30:00"
}
```

### Email Template Model

```json
{
  "id": "uuid-string",
  "name": "Template Name",
  "template_type": "NEWSLETTER",
  "subject": "Email Subject",
  "body": "<html>Email HTML Body</html>",
  "description": "Template description",
  "is_active": true,
  "created_at": "2026-03-28T10:30:00",
  "updated_at": "2026-03-28T11:45:00"
}
```

---

## Error Handling

### Standard Error Response

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or validation failed |
| 401 | Unauthorized | Missing or invalid authentication token |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

### Authentication Errors

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

Ensure you're including the token in the `Authorization` header:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Validation Errors

**400 Bad Request:**
```json
{
  "detail": "Email already exists"
}
```

Check request body matches expected schema and constraints.

---

## Template Types

Email templates are organized by type for different communication purposes:

| Type | Purpose | Use Case |
|------|---------|----------|
| **NEWSLETTER** | Regular updates | Weekly/monthly newsletters |
| **PROMOTIONAL** | Marketing offers | Discounts, sales, promotions |
| **ANNOUNCEMENT** | Important news | Product launches, updates |
| **PRODUCT** | Product info | New product features |
| **EVENT** | Event details | Conference, webinar invites |
| **WEBINAR** | Training sessions | Educational webinars |
| **ONBOARDING** | New user welcome | First-time user experience |
| **FEEDBACK** | Customer surveys | Reviews, feedback requests |
| **RETENTION** | Keep customers | Re-engagement campaigns |
| **SALES** | Sales outreach | Lead follow-up, proposals |

---

## Usage Examples

### 1. Complete User Signup Flow

```javascript
// Step 1: Signup
const signupResponse = await fetch('http://localhost:8000/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    password: 'SecurePass123'
  })
});

const { access_token, user } = await signupResponse.json();

// Step 2: Create profile
const profileResponse = await fetch('http://localhost:8000/auth/profile', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    business_name: 'Acme Corporation',
    company_id: 'ACME001',
    website: 'https://acme.com',
    industry: 'Technology'
  })
});

const profile = await profileResponse.json();
```

### 2. Scrape and Send Campaign

```javascript
// Step 1: Scrape UK domains and save emails
const scrapeResponse = await fetch('http://localhost:8000/scrape/scrape-to-db', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    email_limit: 500,
    domain_limit: 50,
    category: 'WEB'
  })
});

const scrapeResult = await scrapeResponse.json();

// Step 2: Get all scraped emails
const emailsResponse = await fetch('http://localhost:8000/emails/all', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});

const { emails } = await emailsResponse.json();

// Step 3: Get newsletter template
const templatesResponse = await fetch('http://localhost:8000/emails/templates', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});

const templates = await templatesResponse.json();
const newsletterTemplate = templates.find(t => t.template_type === 'NEWSLETTER');

// Step 4: Send bulk campaign
const campaignResponse = await fetch('http://localhost:8000/emails/send-bulk', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    recipient_emails: emails,
    template_id: newsletterTemplate.id,
    variables: {
      company_name: 'Acme Corporation',
      sender_name: 'Marketing Team'
    }
  })
});

const campaignResult = await campaignResponse.json();
```

### 3. Create and Send Custom Template

```javascript
// Step 1: Create custom template
const createResponse = await fetch('http://localhost:8000/emails/templates', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    name: 'Special Offer',
    template_type: 'PROMOTIONAL',
    subject: 'Exclusive {discount}% Off for {company}',
    body: '<html><body><h1>Special Offer</h1><p>Get {discount}% off today!</p></body></html>',
    description: 'Limited time promotional offer'
  })
});

const newTemplate = await createResponse.json();

// Step 2: Send email with template
const sendResponse = await fetch('http://localhost:8000/emails/send', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    recipient_email: 'customer@example.com',
    template_id: newTemplate.id,
    variables: {
      discount: '25',
      company: 'TechCorp'
    }
  })
});

const result = await sendResponse.json();
```

### 4. Handle Errors

```javascript
async function makeAuthenticatedRequest(endpoint, options = {}) {
  const response = await fetch(`http://localhost:8000${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${access_token}`,
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

// Usage
try {
  const result = await makeAuthenticatedRequest('/emails/all');
} catch (error) {
  console.error('API Error:', error.message);
}
```

---

## Authentication Notes

### Bearer Token Format

Include token in `Authorization` header for all authenticated endpoints:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLWlkIiwiaWF0IjoxNjc5MDAwMDAwLCJleHAiOjE2ODA4MDAwMDB9.signature
```

### Token Expiration

- Tokens expire after 30 days
- Generate new token via `/auth/login` when expired
- No refresh token endpoint (use login to refresh)

### Password Requirements

- Minimum 8 characters
- No additional complexity requirements (customizable)
- Hashed with bcrypt (never stored in plain text)

---

## Rate Limiting

Currently no rate limiting implemented. Consider adding for production:
- 100 requests per minute per IP
- 1000 requests per hour per user
- 10 bulk email requests per hour per user

---

## Base URL

Depending on deployment:

| Environment | URL |
|-------------|-----|
| Local Development | `http://localhost:8000` |
| Development Server | `https://dev.example.com` |
| Production | `https://api.example.com` |

---

## Support

For API issues or questions:
- Check this documentation
- Review error messages in response
- Check backend logs at `/logs`
- Contact development team

---

**Last Updated:** March 28, 2026
**API Version:** 1.1
**Status:** Production Ready

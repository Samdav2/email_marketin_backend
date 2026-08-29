import re
from typing import List, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from app.model.email_template import EmailTemplate, TemplateType
from app.repo.email_template import get_all_templates, create_template

# Anti-Spam Footer standard block
ANTI_SPAM_FOOTER_HTML = """
<div class="footer" style="text-align: center; color: #888888; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eeeeee;">
    <p>You received this email because you opted in to updates from ThinkEdge Consultancy.</p>
    <p>ThinkEdge Consultancy Ltd &bull; 100 City Road, London, EC1Y 2AB, United Kingdom</p>
    <p><a href="{unsubscribe_url}" style="color: #667eea; text-decoration: underline;">Unsubscribe from this list</a> &bull; <a href="{privacy_url}" style="color: #667eea; text-decoration: underline;">Privacy Policy</a></p>
</div>
"""

# Default professional email templates with anti-spam compliance built in
DEFAULT_TEMPLATES = [
    {
        "name": "Newsletter - Monthly Digest",
        "template_type": TemplateType.newsletter,
        "subject": "Your Monthly Digest - {month}",
        "body": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; color: #333333; line-height: 1.6; background-color: #f4f6f9; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); padding: 30px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
        .content {{ padding: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Monthly Digest</h1>
        </div>
        <div class="content">
            <p>Hello {{name}},</p>
            <p>We've compiled the best content and industry insights from this month just for you.</p>
            <h3>Top Stories:</h3>
            <ul>
                <li>Strategic Insights for Digital Growth</li>
                <li>Email Campaign Optimization Best Practices</li>
                <li>Upcoming Industry Webinars</li>
            </ul>
            <p>Thank you for being a valued member of our community!</p>
        </div>
        {ANTI_SPAM_FOOTER_HTML}
    </div>
</body>
</html>""",
        "description": "Professional monthly newsletter digest with anti-spam compliance"
    },
    {
        "name": "Promotional - Special Offer",
        "template_type": TemplateType.promotional,
        "subject": "Special Offer: {discount}% Off Your Next Order",
        "body": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; color: #333333; background-color: #f4f6f9; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; padding: 30px; }}
        .banner {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 6px; }}
        .offer {{ font-size: 42px; font-weight: bold; margin: 15px 0; }}
        .cta-button {{ background-color: #667eea; color: white; padding: 14px 28px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <h2>Special Member Offer</h2>
            <div class="offer">{{discount}}% OFF</div>
            <p>Save on your next subscription or renewal</p>
        </div>
        <div style="padding: 20px 0; text-align: center;">
            <p>Hi {{name}},</p>
            <p>We're pleased to share an exclusive {{discount}}% discount code for your team.</p>
            <a href="{{link}}" class="cta-button">Claim Special Offer</a>
            <p><small style="color: #777777;">Offer valid through {{expiry_date}}</small></p>
        </div>
        {ANTI_SPAM_FOOTER_HTML}
    </div>
</body>
</html>""",
        "description": "Compliant promotional email template"
    },
    {
        "name": "Announcement - Company Update",
        "template_type": TemplateType.announcement,
        "subject": "Update: {announcement_title}",
        "body": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; color: #333333; line-height: 1.6; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; }}
        .header {{ border-left: 4px solid #2c3e50; padding-left: 15px; margin-bottom: 20px; }}
        .announcement {{ background-color: #e8f4f8; padding: 20px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{{announcement_title}}</h2>
        </div>
        <p>Hello {{name}},</p>
        <div class="announcement">
            <p>{{announcement_content}}</p>
        </div>
        <p>Thank you for your continued partnership.</p>
        <p>Best regards,<br>The Team</p>
        {ANTI_SPAM_FOOTER_HTML}
    </div>
</body>
</html>""",
        "description": "Professional company announcement"
    },
    {
        "name": "Product Launch",
        "template_type": TemplateType.product,
        "subject": "Introducing {product_name} - Now Available",
        "body": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; color: #333333; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; }}
        .hero {{ background-color: #f8f9fa; padding: 30px; text-align: center; border-radius: 6px; }}
        .feature-list {{ list-style: none; padding: 0; }}
        .feature-list li {{ padding: 8px 0; border-bottom: 1px solid #eeeeee; }}
        .button {{ background-color: #2c3e50; color: white; padding: 12px 26px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h2>{{product_name}} is Here</h2>
            <p>Designed to accelerate your workflow</p>
        </div>
        <div style="padding: 20px 0;">
            <p>Hello {{name}},</p>
            <p>We are excited to introduce {{product_name}}.</p>
            <h3>Key Capabilities:</h3>
            <ul class="feature-list">
                <li>Automated workflow processing</li>
                <li>Enhanced security and analytics</li>
                <li>Seamless cloud integration</li>
            </ul>
            <div style="text-align: center; margin-top: 20px;">
                <a href="{{product_link}}" class="button">Explore Features</a>
            </div>
        </div>
        {ANTI_SPAM_FOOTER_HTML}
    </div>
</body>
</html>""",
        "description": "Product release email template"
    },
    {
        "name": "Event Invitation",
        "template_type": TemplateType.event,
        "subject": "Invitation: {event_name}",
        "body": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; color: #333333; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e0e0e0; }}
        .event-details {{ margin: 20px 0; padding: 20px; background-color: #f9f9f9; border-radius: 5px; }}
        .register-btn {{ background-color: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div style="text-align: center;">
            <h2>You're Invited to {{event_name}}</h2>
            <div class="event-details">
                <p>📍 Location: {{event_location}}</p>
                <p>📅 Date: {{event_date}} at {{event_time}}</p>
                <p>{{event_description}}</p>
            </div>
            <a href="{{event_link}}" class="register-btn">Confirm RSVP</a>
        </div>
        {ANTI_SPAM_FOOTER_HTML}
    </div>
</body>
</html>""",
        "description": "Event invitation with registration link"
    }
]


def verify_template_spam_risk(subject: str, body: str) -> Dict[str, Any]:
    """
    Evaluates an email template for spam risk flags, missing anti-spam headers,
    prohibited spam trigger words, and formatting issues.

    Returns:
        Dict with spam_score (0-100), risk_level ("LOW", "MEDIUM", "HIGH"),
        passed_checks (List[str]), and warnings (List[str]).
    """
    warnings = []
    passed_checks = []
    spam_score = 0

    # 1. Subject Line Checks
    if not subject:
        warnings.append("Subject line is missing.")
        spam_score += 30
    else:
        passed_checks.append("Subject line present")
        if subject.isupper() and len(subject) > 5:
            warnings.append("Subject line is in ALL CAPS (high spam risk).")
            spam_score += 25
        if re.search(r'[!$?]{2,}', subject):
            warnings.append("Subject line contains excessive punctuation (e.g. !!!, $$$).")
            spam_score += 15

    # High-risk spam phrases
    spam_keywords = [
        "100% free", "act now", "make money", "cash bonus", "guaranteed profit",
        "no risk", "risk free", "double your income", "winner", "congratulations you won"
    ]
    combined_text = f"{subject} {body}".lower()
    found_keywords = [kw for kw in spam_keywords if kw in combined_text]
    if found_keywords:
        warnings.append(f"Contains high-risk spam keywords: {', '.join(found_keywords)}")
        spam_score += len(found_keywords) * 15
    else:
        passed_checks.append("No high-risk spam keywords detected")

    # 2. Unsubscribe Link Check
    if "unsubscribe" not in combined_text and "{unsubscribe_url}" not in body:
        warnings.append("Missing explicit Unsubscribe link or {unsubscribe_url} placeholder (Required for CAN-SPAM/GDPR).")
        spam_score += 30
    else:
        passed_checks.append("Unsubscribe link / placeholder present")

    # 3. Physical Address / Sender Identification Check
    address_keywords = ["address", "london", "uk", "street", "city", "ltd", "inc", "corp", "privacy"]
    if not any(ak in combined_text for ak in address_keywords):
        warnings.append("Missing sender physical address or privacy notice in footer.")
        spam_score += 20
    else:
        passed_checks.append("Physical address / company identification present")

    # 4. HTML Structure Check
    if "<html" in body.lower() or "<body" in body.lower():
        if "meta name=\"viewport\"" not in body.lower():
            warnings.append("HTML template missing mobile viewport meta tag.")
            spam_score += 10
        else:
            passed_checks.append("Mobile viewport meta tag present")

    # Determine risk level
    if spam_score < 20:
        risk_level = "LOW (Deliverability Excellent)"
    elif spam_score < 50:
        risk_level = "MEDIUM (Minor Deliverability Risk)"
    else:
        risk_level = "HIGH (Likely to end up in SPAM)"

    return {
        "spam_score": min(spam_score, 100),
        "risk_level": risk_level,
        "is_deliverable": spam_score < 40,
        "passed_checks": passed_checks,
        "warnings": warnings,
        "recommendations": [
            "Ensure List-Unsubscribe header is included during dispatch.",
            "Keep subject line concise and avoid aggressive promotional words.",
            "Verify all links use HTTPS with proper SPF/DKIM configured domain."
        ]
    }


async def initialize_default_templates(db: AsyncSession) -> int:
    """Initialize default email templates if they don't exist"""
    existing_templates = await get_all_templates(db)

    if existing_templates:
        print(f"✅ {len(existing_templates)} templates already exist, skipping initialization")
        return len(existing_templates)

    created_count = 0
    for template_data in DEFAULT_TEMPLATES:
        try:
            await create_template(
                name=template_data["name"],
                template_type=template_data["template_type"],
                subject=template_data["subject"],
                body=template_data["body"],
                description=template_data["description"],
                db=db
            )
            created_count += 1
            print(f"✅ Created template: {template_data['name']}")
        except Exception as e:
            print(f"❌ Error creating template {template_data['name']}: {str(e)}")

    print(f"\n✅ Successfully initialized {created_count} email templates")
    return created_count

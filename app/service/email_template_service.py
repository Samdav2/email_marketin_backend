from sqlmodel.ext.asyncio.session import AsyncSession
from app.model.email_template import EmailTemplate, TemplateType
from app.repo.email_template import get_all_templates, create_template
from typing import List


# Default professional email templates
DEFAULT_TEMPLATES = [
    {
        "name": "Newsletter - Monthly Digest",
        "template_type": TemplateType.newsletter,
        "subject": "Your Monthly Digest - {month}",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; border-radius: 5px; }
        .content { padding: 20px; background-color: #f9f9f9; margin: 20px 0; }
        .footer { text-align: center; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Monthly Digest</h1>
        </div>
        <div class="content">
            <p>Hello {name},</p>
            <p>We've compiled the best content and updates from this month just for you.</p>
            <h3>Top Stories:</h3>
            <ul>
                <li>Story 1</li>
                <li>Story 2</li>
                <li>Story 3</li>
            </ul>
            <p>Thank you for being part of our community!</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 Email Marketing. All rights reserved.</p>
        </div>
    </div>
</body>
</html>""",
        "description": "Professional monthly newsletter digest"
    },
    {
        "name": "Promotional - Special Offer",
        "template_type": TemplateType.promotional,
        "subject": "🎉 Exclusive Offer: {discount}% Off!",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; }
        .banner { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }
        .offer { font-size: 48px; font-weight: bold; margin: 20px 0; }
        .cta-button { background-color: #ff6b6b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { text-align: center; color: #999; font-size: 12px; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <h1>Limited Time Offer!</h1>
            <div class="offer">{discount}% OFF</div>
            <p>Don't miss out on this exclusive deal</p>
        </div>
        <div style="padding: 30px; text-align: center;">
            <p>Hi {name},</p>
            <p>We're excited to offer you an exclusive {discount}% discount on your next purchase.</p>
            <a href="{link}" class="cta-button">Claim Your Offer Now</a>
            <p><small>Offer valid until {expiry_date}</small></p>
        </div>
        <div class="footer">
            <p>&copy; 2026 Email Marketing. All rights reserved.</p>
        </div>
    </div>
</body>
</html>""",
        "description": "Eye-catching promotional offer email"
    },
    {
        "name": "Announcement - Company Update",
        "template_type": TemplateType.announcement,
        "subject": "Important Update: {announcement_title}",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; line-height: 1.6; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { border-left: 4px solid #2c3e50; padding-left: 20px; margin-bottom: 30px; }
        .announcement { background-color: #e8f4f8; padding: 20px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{announcement_title}</h2>
        </div>
        <p>Hello {name},</p>
        <div class="announcement">
            <p>{announcement_content}</p>
        </div>
        <p>Thank you for your continued support.</p>
        <p>Best regards,<br>The Team</p>
    </div>
</body>
</html>""",
        "description": "Professional company announcement"
    },
    {
        "name": "Product Launch",
        "template_type": TemplateType.product,
        "subject": "Introducing {product_name} - Now Available!",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; }
        .hero { background-color: #f0f0f0; padding: 40px; text-align: center; }
        .product-info { padding: 30px; }
        .feature-list { list-style: none; padding: 0; }
        .feature-list li { padding: 10px; border-bottom: 1px solid #eee; }
        .cta { text-align: center; margin: 30px 0; }
        .button { background-color: #2c3e50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>🚀 {product_name}</h1>
            <p>Now Available!</p>
        </div>
        <div class="product-info">
            <p>Hello {name},</p>
            <p>We're thrilled to announce the launch of {product_name}!</p>
            <h3>Key Features:</h3>
            <ul class="feature-list">
                <li>✓ Feature One</li>
                <li>✓ Feature Two</li>
                <li>✓ Feature Three</li>
            </ul>
            <div class="cta">
                <a href="{product_link}" class="button">Learn More & Get Started</a>
            </div>
        </div>
    </div>
</body>
</html>""",
        "description": "Product launch announcement"
    },
    {
        "name": "Event Invitation",
        "template_type": TemplateType.event,
        "subject": "You're Invited: {event_name}",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .event-card { border: 2px solid #667eea; border-radius: 10px; padding: 30px; text-align: center; }
        .event-title { font-size: 28px; color: #667eea; margin: 20px 0; }
        .event-details { margin: 20px 0; padding: 20px; background-color: #f9f9f9; }
        .detail-row { margin: 10px 0; }
        .register-btn { background-color: #667eea; color: white; padding: 12px 40px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="event-card">
            <h1>📅 You're Invited!</h1>
            <div class="event-title">{event_name}</div>
            <div class="event-details">
                <div class="detail-row">📍 {event_location}</div>
                <div class="detail-row">📅 {event_date} at {event_time}</div>
                <div class="detail-row">{event_description}</div>
            </div>
            <a href="{event_link}" class="register-btn">Register Now</a>
        </div>
    </div>
</body>
</html>""",
        "description": "Event invitation with registration link"
    },
    {
        "name": "Webinar Invitation",
        "template_type": TemplateType.webinar,
        "subject": "Join Our Webinar: {topic}",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .webinar-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; border-radius: 5px; }
        .webinar-content { padding: 30px; background-color: #f9f9f9; margin-top: 20px; }
        .join-button { background-color: #667eea; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="webinar-header">
            <h1>🎓 Join Our Webinar</h1>
            <p>{topic}</p>
        </div>
        <div class="webinar-content">
            <p>Hello {name},</p>
            <p>You're invited to attend our exclusive webinar on {topic}.</p>
            <p><strong>Date & Time:</strong> {webinar_date} at {webinar_time}</p>
            <p><strong>Speaker:</strong> {speaker_name}</p>
            <p><strong>Duration:</strong> {duration}</p>
            <p>{webinar_description}</p>
            <a href="{webinar_link}" class="join-button">Join Webinar</a>
        </div>
    </div>
</body>
</html>""",
        "description": "Webinar invitation"
    },
    {
        "name": "Onboarding Welcome",
        "template_type": TemplateType.onboarding,
        "subject": "Welcome {name}! Let's Get Started",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .welcome { background-color: #2c3e50; color: white; padding: 40px; text-align: center; border-radius: 5px; }
        .steps { padding: 30px; }
        .step { margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <div class="welcome">
            <h1>Welcome to Our Community! 🎉</h1>
            <p>We're excited to have you on board, {name}!</p>
        </div>
        <div class="steps">
            <h3>Getting Started - Next Steps:</h3>
            <div class="step">
                <strong>Step 1:</strong> Complete your profile setup
            </div>
            <div class="step">
                <strong>Step 2:</strong> Explore our features and resources
            </div>
            <div class="step">
                <strong>Step 3:</strong> Connect with our community
            </div>
            <p>If you have any questions, our support team is here to help!</p>
        </div>
    </div>
</body>
</html>""",
        "description": "Welcome onboarding email for new users"
    },
    {
        "name": "Feedback Request",
        "template_type": TemplateType.feedback,
        "subject": "We'd Love Your Feedback!",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .feedback-box { background-color: #e8f4f8; padding: 30px; border-radius: 5px; text-align: center; }
        .survey-btn { background-color: #667eea; color: white; padding: 12px 40px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="feedback-box">
            <h2>We'd Love Your Feedback! 💬</h2>
            <p>Hello {name},</p>
            <p>Your opinion matters to us. Help us improve by sharing your feedback.</p>
            <p>It takes just 2 minutes!</p>
            <a href="{survey_link}" class="survey-btn">Take Survey</a>
        </div>
    </div>
</body>
</html>""",
        "description": "Customer feedback survey request"
    },
    {
        "name": "Retention - Win Back",
        "template_type": TemplateType.retention,
        "subject": "We Miss You! Here's {incentive} Just for You",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .banner { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px; text-align: center; border-radius: 5px; }
        .offer { padding: 30px; background-color: #f9f9f9; margin-top: 20px; }
        .comeback-btn { background-color: #f5576c; color: white; padding: 12px 40px; text-decoration: none; border-radius: 5px; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="banner">
            <h1>We Miss You!</h1>
            <p>Come back and enjoy exclusive benefits</p>
        </div>
        <div class="offer">
            <p>Hi {name},</p>
            <p>It's been a while since we've seen you. We miss you and would love to welcome you back!</p>
            <p>As a special thank you, we're offering you {incentive}.</p>
            <a href="{comeback_link}" class="comeback-btn">Claim Your Offer</a>
            <p><small>Offer valid until {expiry_date}</small></p>
        </div>
    </div>
</body>
</html>""",
        "description": "Win-back campaign for inactive users"
    },
    {
        "name": "Sales - Follow Up",
        "template_type": TemplateType.sales,
        "subject": "Quick Question About {product}",
        "body": """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; line-height: 1.6; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .greeting { padding: 20px; background-color: #f9f9f9; }
        .value-proposition { margin: 30px 0; }
        .cta-section { text-align: center; margin: 30px 0; }
        .schedule-btn { background-color: #2c3e50; color: white; padding: 12px 40px; text-decoration: none; border-radius: 5px; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="greeting">
            <p>Hi {name},</p>
            <p>I hope you've been doing well!</p>
        </div>
        <div class="value-proposition">
            <p>I noticed you were interested in {product}. I wanted to reach out and see if you had any questions.</p>
            <p>Here's what {product} can do for you:</p>
            <ul>
                <li>Benefit 1</li>
                <li>Benefit 2</li>
                <li>Benefit 3</li>
            </ul>
        </div>
        <div class="cta-section">
            <p>Would you be open to a quick call to discuss how we can help?</p>
            <a href="{calendar_link}" class="schedule-btn">Schedule a Call</a>
        </div>
        <p>Best regards,<br>{sales_rep_name}</p>
    </div>
</body>
</html>""",
        "description": "Sales follow-up email"
    }
]


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

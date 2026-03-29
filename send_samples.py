import asyncio
import os
from app.dependencies.smtp_email import email_service

async def send_all_samples(recipient):
    templates_dir = "templates/html"

    # Sample data for all templates
    sample_data = {
        "newsletter.html": {
            "name": "Jane Doe"
        },
        "promotional.html": {
            "name": "Jane Doe",
            "discount": "25",
            "expiry_date": "April 15, 2026",
            "link": "https://example.com/promo"
        },
        "announcement.html": {
            "name": "Jane Doe",
            "announcement_title": "Huge Platform Milestone!",
            "announcement_content": "We've officially reached 1 million active users! Thank you for being a part of our journey."
        },
        "product_launch.html": {
            "name": "Jane Doe",
            "product_name": "Aero Analytics Pro",
            "product_link": "https://example.com/aero-pro"
        },
        "event_invitation.html": {
            "name": "Jane Doe",
            "event_name": "Global Outreach Summit",
            "event_location": "Grand Ballroom, New York City",
            "event_date": "May 20, 2026",
            "event_time": "10:00 AM EST",
            "event_description": "A full day of networking and learning from the best mind in digital marketing.",
            "event_link": "https://example.com/summit-2026"
        },
        "webinar_invitation.html": {
            "name": "Jane Doe",
            "topic": "Mastering the Art of High-Conversion Emails",
            "webinar_date": "April 10, 2026",
            "webinar_time": "2:00 PM EST",
            "speaker_name": "Alice Johnson",
            "webinar_description": "Learn the exact strategies used by top performers to get 50%+ open rates.",
            "webinar_link": "https://example.com/webinar"
        },
        "onboarding_welcome.html": {
            "name": "Jane Doe"
        },
        "feedback_request.html": {
            "name": "Jane Doe",
            "survey_link": "https://example.com/survey"
        },
        "retention_winback.html": {
            "name": "Jane Doe",
            "incentive": "1 Month of Premium Free",
            "expiry_date": "April 5, 2026",
            "comeback_link": "https://example.com/welcome-back"
        },
        "sales_followup.html": {
            "name": "Jane Doe",
            "product": "AeroMail Core Services",
            "calendar_link": "https://example.com/schedule",
            "sales_rep_name": "Robert Smith"
        }
    }

    print(f"--- Sending 10 sample templates to {recipient} ---")

    for filename, data in sample_data.items():
        file_path = os.path.join(templates_dir, filename)
        if not os.path.exists(file_path):
            print(f"Skipping {filename}: Not found.")
            continue

        with open(file_path, 'r') as f:
            template_content = f.read()

        # Replace placeholders
        body = template_content
        for key, value in data.items():
            body = body.replace(f"{{{key}}}", value)

        subject = f"Sample: {filename.replace('.html', '').replace('_', ' ').title()}"

        print(f"Sending {filename}...")
        success = await email_service.send_email(recipient, subject, body, is_html=True)
        if success:
            print(f"✓ {filename} sent.")
        else:
            print(f"✗ Failed to send {filename}.")

if __name__ == "__main__":
    asyncio.run(send_all_samples("adoxop1@gmail.com"))

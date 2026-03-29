import asyncio
import re
from typing import List, Dict, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from app.dependencies.email import send_email
from app.repo.email_template import get_template_by_id


def render_template(template_body: str, variables: Optional[Dict[str, str]] = None) -> str:
    """
    Replace template variables with actual values
    Variables in template are wrapped in {variable_name}
    """
    if not variables:
        return template_body

    rendered = template_body
    for key, value in variables.items():
        pattern = r'\{' + re.escape(key) + r'\}'
        rendered = re.sub(pattern, str(value), rendered)

    return rendered


async def send_single_email(
    recipient_email: str,
    template_id: str,
    variables: Optional[Dict[str, str]],
    db: AsyncSession
) -> Dict:
    """Send email to single recipient using template"""
    try:
        template = await get_template_by_id(template_id, db)
        if not template:
            return {
                "success": False,
                "error": f"Template {template_id} not found"
            }

        # Render template with variables
        subject = render_template(template.subject, variables)
        body = render_template(template.body, variables)

        # Send email
        await send_email(
            email=recipient_email,
            subject=subject,
            body=body
        )

        return {
            "success": True,
            "recipient": recipient_email,
            "template_name": template.name
        }

    except Exception as e:
        return {
            "success": False,
            "recipient": recipient_email,
            "error": str(e)
        }


async def send_bulk_emails(
    recipient_emails: List[str],
    template_id: str,
    variables: Optional[Dict[str, str]],
    db: AsyncSession,
    batch_size: int = 10
) -> Dict:
    """Send emails to multiple recipients using template"""
    try:
        template = await get_template_by_id(template_id, db)
        if not template:
            return {
                "total_recipients": len(recipient_emails),
                "successful": 0,
                "failed": len(recipient_emails),
                "errors": [{"error": f"Template {template_id} not found"}]
            }

        successful = 0
        failed = 0
        errors = []

        # Process in batches
        for i in range(0, len(recipient_emails), batch_size):
            batch = recipient_emails[i:i + batch_size]
            tasks = [
                send_single_email(email, template_id, variables, db)
                for email in batch
            ]

            results = await asyncio.gather(*tasks)

            for result in results:
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
                    errors.append({
                        "recipient": result.get("recipient", "unknown"),
                        "error": result.get("error", "Unknown error")
                    })

        return {
            "total_recipients": len(recipient_emails),
            "successful": successful,
            "failed": failed,
            "errors": errors[:10] if errors else []  # Return only first 10 errors
        }

    except Exception as e:
        return {
            "total_recipients": len(recipient_emails),
            "successful": 0,
            "failed": len(recipient_emails),
            "errors": [{"error": str(e)}]
        }

import re
import logging
from typing import List, Dict, Optional
import resend
from app.core.settings import settings

logger = logging.getLogger(__name__)


def _html_to_plain_text(html: str) -> str:
    """Helper to convert HTML body into clean plain text for spam compliance."""
    if not html:
        return ""
    # Strip HTML tags
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


class ResendEmailService:
    """
    Service for sending emails via Resend API with built-in deliverability
    headers and anti-spam best practices.
    """

    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.RESEND_FROM_EMAIL
        self.from_name = settings.RESEND_FROM_NAME

    def _get_from_field(self) -> str:
        if self.from_name:
            return f"{self.from_name} <{self.from_email}>"
        return self.from_email

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        is_html: bool = True,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Send an email via Resend API.
        """
        if not self.api_key or self.api_key == "re_123456789_change_me":
            logger.warning("RESEND_API_KEY is not configured or using default placeholder.")

        resend.api_key = self.api_key

        try:
            from_sender = self._get_from_field()
            html_content = body if is_html else f"<pre>{body}</pre>"
            text_content = _html_to_plain_text(body) if is_html else body

            # Deliverability anti-spam headers
            headers = {
                "List-Unsubscribe": f"<mailto:unsubscribe@{self.from_email.split('@')[-1]}?subject=Unsubscribe>, <{settings.FRONTEND_URL}/unsubscribe>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
                "X-Entity-Ref-ID": f"resend-{recipient}"
            }

            params: resend.Emails.SendParams = {
                "from": from_sender,
                "to": [recipient],
                "subject": subject,
                "html": html_content,
                "text": text_content,
                "headers": headers,
            }

            if reply_to:
                params["reply_to"] = reply_to

            response = resend.Emails.send(params)
            logger.info(f"Resend email sent to {recipient}. Response ID: {response.get('id', response)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email via Resend to {recipient}: {str(e)}")
            return False

    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        is_html: bool = True
    ) -> Dict:
        """
        Send email to multiple recipients via Resend.
        """
        results = {
            'successful': 0,
            'failed': 0,
            'failed_emails': []
        }

        for recipient in recipients:
            success = await self.send_email(recipient, subject, body, is_html)
            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['failed_emails'].append(recipient)

        return results


resend_email_service = ResendEmailService()

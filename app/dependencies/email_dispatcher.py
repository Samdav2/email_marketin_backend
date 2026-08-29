import logging
from typing import List, Dict, Optional
from app.core.settings import settings
from app.dependencies.resend_email import resend_email_service, _html_to_plain_text
from app.dependencies.smtp_email import SMTPEmailService

logger = logging.getLogger(__name__)


class UnifiedEmailService:
    """
    Unified Email Dispatcher that dynamically routes outbound emails
    through the configured provider (Resend, SMTP, Mailjet) with built-in
    anti-spam headers and deliverability checks.
    """

    def __init__(self):
        self.smtp_service = SMTPEmailService()

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        provider = settings.EMAIL_PROVIDER.lower()
        logger.info(f"Dispatching email to {recipient} using provider: {provider}")

        if provider == "resend":
            return await resend_email_service.send_email(
                recipient=recipient,
                subject=subject,
                body=body,
                is_html=is_html
            )
        elif provider == "smtp":
            return await self.smtp_service.send_email(
                recipient=recipient,
                subject=subject,
                body=body,
                is_html=is_html
            )
        elif provider == "mailjet":
            return await self._send_via_mailjet(recipient, subject, body, is_html)
        else:
            # Fallback to Resend first, then SMTP
            logger.warning(f"Unknown EMAIL_PROVIDER '{provider}'. Falling back to Resend / SMTP.")
            resend_ok = await resend_email_service.send_email(recipient, subject, body, is_html)
            if resend_ok:
                return True
            return await self.smtp_service.send_email(recipient, subject, body, is_html)

    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        is_html: bool = True
    ) -> Dict:
        provider = settings.EMAIL_PROVIDER.lower()
        logger.info(f"Dispatching bulk email to {len(recipients)} recipients via provider: {provider}")

        if provider == "resend":
            return await resend_email_service.send_bulk_email(recipients, subject, body, is_html)
        elif provider == "smtp":
            return await self.smtp_service.send_bulk_email(recipients, subject, body, is_html)
        else:
            results = {"successful": 0, "failed": 0, "failed_emails": []}
            for recipient in recipients:
                ok = await self.send_email(recipient, subject, body, is_html)
                if ok:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["failed_emails"].append(recipient)
            return results

    async def _send_via_mailjet(
        self,
        recipient: str,
        subject: str,
        body: str,
        is_html: bool = True
    ) -> bool:
        try:
            from mailjet_rest import Client
            mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY), version='v3.1')
            text_part = _html_to_plain_text(body) if is_html else body
            html_part = body if is_html else f"<pre>{body}</pre>"

            message_payload = {
                "From": {
                    "Email": settings.MAIL_FROM,
                    "Name": settings.MAIL_FROM_NAME
                },
                "ReplyTo": {
                    "Email": settings.MAIL_FROM,
                    "Name": settings.MAIL_FROM_NAME
                },
                "To": [{"Email": recipient}],
                "Subject": subject,
                "TextPart": text_part,
                "HTMLPart": html_part,
                "Headers": {
                    "List-Unsubscribe": f"<mailto:unsubscribe@{settings.MAIL_FROM.split('@')[-1]}?subject=Unsubscribe>, <{settings.FRONTEND_URL}/unsubscribe>",
                    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click"
                }
            }

            result = mailjet.send.create(data={'Messages': [message_payload]})
            if result.status_code == 200:
                logger.info(f"Email sent via Mailjet to {recipient}")
                return True
            else:
                logger.error(f"Mailjet send failed: {result.status_code} - {result.json()}")
                return False
        except Exception as e:
            logger.error(f"Exception sending via Mailjet to {recipient}: {str(e)}")
            return False


unified_email_service = UnifiedEmailService()

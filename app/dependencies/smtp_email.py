"""
SMTP Email Service Module
Handles sending emails via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.settings import settings
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SMTPEmailService:
    """Service for sending emails via SMTP"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_pass = settings.SMTP_PASS
        self.from_email = settings.SMTP_FROM
        self.from_name = settings.SMTP_FROM_NAME

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """
        Send an email to a single recipient

        Args:
            recipient: Email address of recipient
            subject: Subject line of email
            body: Body content of email
            is_html: Whether body is HTML content

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = recipient

            # Attach body
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type))

            # Send email
            print(f"Connecting to {self.smtp_host}:{self.smtp_port}...")
            if self.smtp_port == 465:
                server_class = smtplib.SMTP_SSL
            else:
                server_class = smtplib.SMTP

            with server_class(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.smtp_port != 465:
                    print("Starting TLS...")
                    server.starttls()
                print(f"Logging in as {self.smtp_user}...")
                server.login(self.smtp_user, self.smtp_pass)
                print("Sending mail...")
                server.sendmail(self.smtp_user, [recipient], msg.as_string())

            logger.info(f"Email sent successfully to {recipient}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False

    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        is_html: bool = False
    ) -> dict:
        """
        Send email to multiple recipients

        Args:
            recipients: List of recipient email addresses
            subject: Subject line of email
            body: Body content of email
            is_html: Whether body is HTML content

        Returns:
            dict: Dictionary with success and failure counts
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


# Create singleton instance
email_service = SMTPEmailService()

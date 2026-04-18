"""SendGrid v3 mail-send helper (HTTP, no official SDK required)."""

import logging
from typing import List

import httpx

logger = logging.getLogger(__name__)


def send_email_sendgrid(
    *,
    api_key: str,
    from_email: str,
    to_emails: List[str],
    subject: str,
    body_text: str,
) -> None:
    """POST a single plain-text message via SendGrid API."""
    url = "https://api.sendgrid.com/v3/mail/send"
    payload = {
        "personalizations": [{"to": [{"email": e} for e in to_emails]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body_text}],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
    logger.info("SendGrid notification sent to %s", to_emails)

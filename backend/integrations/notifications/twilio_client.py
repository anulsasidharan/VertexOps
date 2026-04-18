"""Twilio Programmable SMS helper."""

import logging
from typing import Dict
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)


def send_sms_twilio(
    *,
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
    body: str,
) -> None:
    """Send SMS via Twilio REST API."""
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = urlencode({"From": from_number, "To": to_number, "Body": body})
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(url, content=data, headers=headers, auth=(account_sid, auth_token))
        resp.raise_for_status()
    logger.info("Twilio SMS sent to %s", to_number)

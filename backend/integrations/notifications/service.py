"""Dispatch optional email/SMS notifications — failures are swallowed."""

import logging
from typing import Any, Dict, List, Tuple

from backend.core.config import get_settings
from backend.integrations.notifications import templates
from backend.integrations.notifications.sendgrid_client import send_email_sendgrid
from backend.integrations.notifications.twilio_client import send_sms_twilio

logger = logging.getLogger(__name__)


def dispatch_notification(event_type: str, payload: Dict[str, Any]) -> None:
    """Fan out a product event to enabled channels. Never raises to callers."""
    settings = get_settings()
    if not settings.notifications_enabled:
        return

    try:
        _dispatch_sendgrid(event_type, payload, settings)
    except Exception as exc:
        logger.warning("SendGrid notification skipped/failed: %s", exc, exc_info=False)

    try:
        _dispatch_twilio(event_type, payload, settings)
    except Exception as exc:
        logger.warning("Twilio notification skipped/failed: %s", exc, exc_info=False)


def _alert_emails(settings) -> List[str]:
    raw = settings.notification_alert_emails
    if isinstance(raw, str) and raw.strip():
        return [e.strip() for e in raw.split(",") if e.strip()]
    return []


def _dispatch_sendgrid(event_type: str, payload: Dict[str, Any], settings) -> None:
    if not settings.notifications_sendgrid_enabled:
        return
    key = settings.sendgrid_api_key
    from_email = settings.sendgrid_from_email
    if key is None or not from_email:
        logger.info("SendGrid enabled but missing API key or from_email.")
        return
    recipients = _alert_emails(settings)
    if not recipients:
        logger.info("SendGrid: no NOTIFICATION_ALERT_EMAILS configured; skip send.")
        return
    subject, body = _email_for_event(event_type, payload)
    send_email_sendgrid(
        api_key=key.get_secret_value(),
        from_email=from_email,
        to_emails=recipients,
        subject=subject,
        body_text=body,
    )


def _dispatch_twilio(event_type: str, payload: Dict[str, Any], settings) -> None:
    if not settings.notifications_twilio_enabled:
        return
    sid = settings.twilio_account_sid
    token = settings.twilio_auth_token
    from_n = settings.twilio_from_number
    to_n = settings.twilio_alert_to_number
    if not sid or token is None or not from_n or not to_n:
        logger.info("Twilio enabled but missing SID, token, from, or alert number.")
        return
    body = _sms_for_event(event_type, payload)
    send_sms_twilio(
        account_sid=sid,
        auth_token=token.get_secret_value(),
        from_number=from_n,
        to_number=to_n,
        body=body,
    )


def _email_for_event(event_type: str, payload: Dict[str, Any]) -> Tuple[str, str]:
    if event_type == "eval_completed":
        return templates.eval_completed_email(payload)
    if event_type == "deployment_changed":
        return templates.deployment_changed_email(payload)
    if event_type == "critical_failure":
        return templates.critical_failure_email(payload)
    return f"[VertexOps] {event_type}", str(payload)


def _sms_for_event(event_type: str, payload: Dict[str, Any]) -> str:
    if event_type == "eval_completed":
        return templates.eval_completed_sms(payload)
    return f"VertexOps: {event_type}"

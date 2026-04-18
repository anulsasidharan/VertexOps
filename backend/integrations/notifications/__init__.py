"""Optional outbound notifications."""

from backend.integrations.notifications.service import dispatch_notification

__all__ = ["dispatch_notification"]

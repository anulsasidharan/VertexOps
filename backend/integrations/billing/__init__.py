"""Optional usage metering for future billing (Stripe-oriented hooks)."""

from backend.integrations.billing.service import record_usage_event

__all__ = ["record_usage_event"]

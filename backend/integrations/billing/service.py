"""Usage metering hooks — optional Stripe Billing meter events, disabled by default."""

from __future__ import annotations

import logging
from typing import Any

from backend.core.config import get_settings
from backend.integrations.billing import stripe_client

logger = logging.getLogger(__name__)


def record_usage_event(
    event_name: str,
    quantity: float,
    *,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Record a usage unit for optional billing. Does not raise; core flows never depend on it."""
    settings = get_settings()
    if not settings.stripe_metering_enabled:
        return

    key = settings.stripe_api_key
    if key is None:
        logger.debug(
            "Stripe metering enabled but stripe_api_key is unset; skipping event %s.", event_name
        )
        return

    stripe_event_name = settings.stripe_meter_event_name or event_name

    try:
        stripe_client.post_meter_usage(
            api_key=key.get_secret_value(),
            event_name=stripe_event_name,
            quantity=quantity,
            metadata=metadata,
        )
    except Exception as exc:
        logger.warning(
            "Stripe metering for %s failed (non-fatal): %s",
            event_name,
            exc,
            exc_info=False,
        )

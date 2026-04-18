"""Thin Stripe Billing Meter Events client — httpx only, no stripe SDK."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

STRIPE_METER_EVENTS_URL = "https://api.stripe.com/v1/billing/meter_events"


def post_meter_usage(
    *,
    api_key: str,
    event_name: str,
    quantity: float,
    metadata: Optional[Dict[str, Any]] = None,
    timeout_seconds: float = 10.0,
) -> None:
    """Send a meter event to Stripe. Raises on HTTP errors; callers should swallow."""
    meta = metadata or {}
    data: Dict[str, str] = {
        "event_name": event_name,
        "payload[value]": str(int(quantity)) if quantity == int(quantity) else str(quantity),
    }
    cust = meta.get("stripe_customer_id")
    if cust:
        data["payload[stripe_customer_id]"] = str(cust)

    with httpx.Client(timeout=timeout_seconds) as client:
        resp = client.post(
            STRIPE_METER_EVENTS_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            data=data,
        )
        if resp.status_code >= 400:
            logger.warning(
                "Stripe meter event HTTP %s: %s",
                resp.status_code,
                resp.text[:500],
            )
        resp.raise_for_status()

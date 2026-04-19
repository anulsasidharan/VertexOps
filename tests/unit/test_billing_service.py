"""Unit tests for optional Stripe usage metering hooks."""

from unittest.mock import MagicMock, patch

from backend.integrations.billing.service import record_usage_event


def test_record_usage_event_noop_when_disabled():
    settings = MagicMock()
    settings.stripe_metering_enabled = False
    with patch("backend.integrations.billing.service.get_settings", return_value=settings):
        with patch(
            "backend.integrations.billing.service.stripe_client.post_meter_usage"
        ) as mock_post:
            record_usage_event("query_completion", 10.0, metadata={"user_id": "u1"})
    mock_post.assert_not_called()


def test_record_usage_event_noop_when_enabled_but_no_key():
    settings = MagicMock()
    settings.stripe_metering_enabled = True
    settings.stripe_api_key = None
    settings.stripe_meter_event_name = None
    with patch("backend.integrations.billing.service.get_settings", return_value=settings):
        with patch(
            "backend.integrations.billing.service.stripe_client.post_meter_usage"
        ) as mock_post:
            record_usage_event("eval_completion", 1.0)
    mock_post.assert_not_called()


@patch("backend.integrations.billing.service.stripe_client.post_meter_usage")
def test_record_usage_event_calls_stripe_when_configured(mock_post):
    settings = MagicMock()
    settings.stripe_metering_enabled = True
    settings.stripe_api_key = MagicMock()
    settings.stripe_api_key.get_secret_value.return_value = "sk_test_xxx"
    settings.stripe_meter_event_name = None

    with patch("backend.integrations.billing.service.get_settings", return_value=settings):
        record_usage_event(
            "query_completion",
            42.0,
            metadata={"user_id": "u-1", "stripe_customer_id": "cus_abc"},
        )

    mock_post.assert_called_once()
    kwargs = mock_post.call_args.kwargs
    assert kwargs["api_key"] == "sk_test_xxx"
    assert kwargs["event_name"] == "query_completion"
    assert kwargs["quantity"] == 42.0
    assert kwargs["metadata"]["stripe_customer_id"] == "cus_abc"


@patch(
    "backend.integrations.billing.service.stripe_client.post_meter_usage",
    side_effect=RuntimeError("network"),
)
def test_record_usage_event_swallows_stripe_errors(mock_post):
    settings = MagicMock()
    settings.stripe_metering_enabled = True
    settings.stripe_api_key = MagicMock()
    settings.stripe_api_key.get_secret_value.return_value = "sk_test_xxx"
    settings.stripe_meter_event_name = "unified_meter"

    with patch("backend.integrations.billing.service.get_settings", return_value=settings):
        record_usage_event("query_completion", 3.0)

    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["event_name"] == "unified_meter"

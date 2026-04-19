"""Unit tests for optional notification dispatch."""

from unittest.mock import MagicMock, patch

from backend.integrations.notifications.service import dispatch_notification


def test_dispatch_noop_when_master_disabled():
    settings = MagicMock()
    settings.notifications_enabled = False
    with patch("backend.integrations.notifications.service.get_settings", return_value=settings):
        dispatch_notification("eval_completed", {"run_id": "r1"})


@patch("backend.integrations.notifications.service.send_email_sendgrid")
@patch("backend.integrations.notifications.service.send_sms_twilio")
def test_eval_completed_sendgrid_path(mock_sms, mock_sg):
    settings = MagicMock()
    settings.notifications_enabled = True
    settings.notifications_sendgrid_enabled = True
    settings.notifications_twilio_enabled = False
    settings.sendgrid_api_key = MagicMock()
    settings.sendgrid_api_key.get_secret_value.return_value = "sg-key"
    settings.sendgrid_from_email = "ops@example.com"
    settings.notification_alert_emails = "a@example.com,b@example.com"
    settings.twilio_account_sid = None
    settings.twilio_auth_token = None
    settings.twilio_from_number = None
    settings.twilio_alert_to_number = None

    with patch("backend.integrations.notifications.service.get_settings", return_value=settings):
        dispatch_notification(
            "eval_completed",
            {"run_id": "run-1", "experiment_id": "exp-1", "status": "completed"},
        )

    mock_sg.assert_called_once()
    kwargs = mock_sg.call_args.kwargs
    assert kwargs["to_emails"] == ["a@example.com", "b@example.com"]
    mock_sms.assert_not_called()


@patch("backend.integrations.notifications.service.send_sms_twilio")
def test_twilio_eval_sms(mock_sms):
    settings = MagicMock()
    settings.notifications_enabled = True
    settings.notifications_sendgrid_enabled = False
    settings.notifications_twilio_enabled = True
    settings.sendgrid_api_key = None
    settings.sendgrid_from_email = None
    settings.notification_alert_emails = None
    settings.twilio_account_sid = "AC123"
    settings.twilio_auth_token = MagicMock()
    settings.twilio_auth_token.get_secret_value.return_value = "tok"
    settings.twilio_from_number = "+10000000000"
    settings.twilio_alert_to_number = "+19999999999"

    with patch("backend.integrations.notifications.service.get_settings", return_value=settings):
        dispatch_notification("eval_completed", {"run_id": "r9", "status": "completed"})

    mock_sms.assert_called_once()
    assert "r9" in mock_sms.call_args.kwargs["body"]


@patch(
    "backend.integrations.notifications.service.send_email_sendgrid",
    side_effect=RuntimeError("down"),
)
def test_sendgrid_failure_does_not_raise(mock_sg):
    settings = MagicMock()
    settings.notifications_enabled = True
    settings.notifications_sendgrid_enabled = True
    settings.notifications_twilio_enabled = False
    settings.sendgrid_api_key = MagicMock()
    settings.sendgrid_api_key.get_secret_value.return_value = "k"
    settings.sendgrid_from_email = "from@example.com"
    settings.notification_alert_emails = "to@example.com"

    with patch("backend.integrations.notifications.service.get_settings", return_value=settings):
        dispatch_notification("eval_completed", {"run_id": "r1", "status": "completed"})

    mock_sg.assert_called_once()

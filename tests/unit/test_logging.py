"""Unit tests for backend.core.logging."""

import json
import logging

from backend.core.logging import (
    JSONFormatter,
    auth_subject_var,
    configure_logging,
    request_id_var,
)


def _make_record(message: str, level: int = logging.INFO, **extra) -> logging.LogRecord:
    record = logging.LogRecord(
        name="test.logger",
        level=level,
        pathname="",
        lineno=0,
        msg=message,
        args=(),
        exc_info=None,
    )
    for k, v in extra.items():
        setattr(record, k, v)
    return record


class TestJSONFormatter:
    def setup_method(self):
        self.fmt = JSONFormatter()

    def _parse(self, record: logging.LogRecord) -> dict:
        return json.loads(self.fmt.format(record))

    def test_base_fields_present(self):
        out = self._parse(_make_record("hello"))
        assert {"timestamp", "level", "logger", "message"}.issubset(out.keys())

    def test_message_content(self):
        out = self._parse(_make_record("test message"))
        assert out["message"] == "test message"

    def test_level_name(self):
        out = self._parse(_make_record("x", level=logging.WARNING))
        assert out["level"] == "WARNING"

    def test_request_id_injected_from_context(self):
        token = request_id_var.set("req-abc-123")
        try:
            out = self._parse(_make_record("ctx"))
            assert out["request_id"] == "req-abc-123"
        finally:
            request_id_var.reset(token)

    def test_request_id_absent_when_not_set(self):
        token = request_id_var.set(None)
        try:
            out = self._parse(_make_record("no ctx"))
            assert "request_id" not in out
        finally:
            request_id_var.reset(token)

    def test_auth_subject_injected_from_context(self):
        token = auth_subject_var.set("user-42")
        try:
            out = self._parse(_make_record("auth"))
            assert out["auth_subject"] == "user-42"
        finally:
            auth_subject_var.reset(token)

    def test_extra_fields_included(self):
        out = self._parse(_make_record("extra", http_status=200))
        assert out["http_status"] == 200

    def test_output_is_valid_json(self):
        raw = self.fmt.format(_make_record("json check"))
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)

    def test_exception_info_included(self):
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            record = _make_record("with exc", exc_info=sys.exc_info())
        out = self._parse(record)
        assert "exception" in out
        assert "ValueError" in out["exception"]


class TestConfigureLogging:
    def test_configure_sets_log_level(self):
        configure_logging("DEBUG")
        assert logging.getLogger().level == logging.DEBUG
        configure_logging("INFO")  # restore

    def test_configure_is_idempotent(self):
        before = len(logging.getLogger().handlers)
        configure_logging("INFO")
        configure_logging("INFO")
        after = len(logging.getLogger().handlers)
        assert after == before

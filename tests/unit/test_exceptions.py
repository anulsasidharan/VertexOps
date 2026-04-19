"""Unit tests for backend.core.exceptions."""

import pytest

from backend.core.exceptions import (
    ConflictError,
    DomainValidationError,
    ErrorCode,
    ErrorEnvelope,
    ForbiddenError,
    InternalError,
    NotFoundError,
    RateLimitError,
    UnauthorizedError,
    VertexOpsError,
)


class TestErrorEnvelope:
    def test_build_sets_code_and_message(self):
        env = ErrorEnvelope.build(ErrorCode.NOT_FOUND, "missing")
        assert env.error.code == "NOT_FOUND"
        assert env.error.message == "missing"
        assert env.error.details == {}

    def test_build_with_details(self):
        env = ErrorEnvelope.build(ErrorCode.VALIDATION_ERROR, "bad", {"field": "x"})
        assert env.error.details == {"field": "x"}

    def test_model_dump_shape(self):
        payload = ErrorEnvelope.build(ErrorCode.FORBIDDEN, "no").model_dump()
        assert set(payload.keys()) == {"error"}
        assert set(payload["error"].keys()) == {"code", "message", "details"}


class TestDomainExceptions:
    @pytest.mark.parametrize(
        "exc_cls, expected_status, expected_code",
        [
            (NotFoundError, 404, ErrorCode.NOT_FOUND),
            (ForbiddenError, 403, ErrorCode.FORBIDDEN),
            (UnauthorizedError, 401, ErrorCode.UNAUTHORIZED),
            (ConflictError, 409, ErrorCode.CONFLICT),
            (DomainValidationError, 422, ErrorCode.VALIDATION_ERROR),
            (RateLimitError, 429, ErrorCode.RATE_LIMIT_EXCEEDED),
            (InternalError, 500, ErrorCode.INTERNAL_ERROR),
        ],
    )
    def test_status_code_and_error_code(self, exc_cls, expected_status, expected_code):
        exc = exc_cls()
        assert exc.status_code == expected_status
        assert exc.error_code == expected_code

    def test_custom_message_is_preserved(self):
        exc = NotFoundError("doc abc not found")
        assert exc.message == "doc abc not found"
        assert str(exc) == "doc abc not found"

    def test_details_stored(self):
        exc = DomainValidationError("bad input", details={"field": "name"})
        assert exc.details == {"field": "name"}

    def test_to_envelope_returns_correct_shape(self):
        exc = ForbiddenError("nope")
        env = exc.to_envelope()
        assert isinstance(env, ErrorEnvelope)
        assert env.error.code == "FORBIDDEN"
        assert env.error.message == "nope"

    def test_base_is_vertex_ops_error(self):
        for cls in (
            NotFoundError,
            ForbiddenError,
            UnauthorizedError,
            ConflictError,
            DomainValidationError,
            RateLimitError,
            InternalError,
        ):
            assert issubclass(cls, VertexOpsError)

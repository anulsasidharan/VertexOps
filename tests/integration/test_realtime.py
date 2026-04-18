"""Integration and contract tests for WebSocket realtime endpoints."""

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.realtime.connection_manager import ConnectionManager
from backend.main import app

_SESSION_ID = str(uuid.uuid4())
_JOB_ID = str(uuid.uuid4())


# ---------------------------------------------------------------------------
# ConnectionManager unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_connection_manager_connect_and_disconnect():
    cm = ConnectionManager()
    ws = MagicMock()
    ws.accept = pytest.mark.asyncio(MagicMock(return_value=None))

    # Simulate accept
    ws.accept = MagicMock()

    async def fake_accept():
        pass

    ws.accept = fake_accept  # type: ignore
    await cm.connect(ws, "chan-1")
    assert cm.channel_size("chan-1") == 1
    cm.disconnect(ws, "chan-1")
    assert cm.channel_size("chan-1") == 0


@pytest.mark.asyncio
async def test_connection_manager_broadcast():
    cm = ConnectionManager()
    ws1, ws2 = MagicMock(), MagicMock()
    sent: list = []

    async def fake_accept():
        pass

    async def fake_send_json(msg):
        sent.append(msg)

    ws1.accept = ws2.accept = fake_accept  # type: ignore
    ws1.send_json = ws2.send_json = fake_send_json  # type: ignore

    await cm.connect(ws1, "chan")
    await cm.connect(ws2, "chan")
    await cm.broadcast("chan", {"type": "test"})

    assert len(sent) == 2
    assert all(m["type"] == "test" for m in sent)


@pytest.mark.asyncio
async def test_connection_manager_broadcast_removes_dead_connections():
    cm = ConnectionManager()
    ws = MagicMock()

    async def fake_accept():
        pass

    async def bad_send(_):
        raise RuntimeError("connection lost")

    ws.accept = fake_accept  # type: ignore
    ws.send_json = bad_send  # type: ignore

    await cm.connect(ws, "chan")
    assert cm.channel_size("chan") == 1
    await cm.broadcast("chan", {"type": "test"})
    assert cm.channel_size("chan") == 0


@pytest.mark.asyncio
async def test_connection_manager_channel_size_unknown_channel():
    cm = ConnectionManager()
    assert cm.channel_size("nonexistent") == 0


# ---------------------------------------------------------------------------
# WebSocket endpoint — connect event (no real WS, contract-level tests)
# ---------------------------------------------------------------------------


def test_ws_query_rejects_missing_token():
    with TestClient(app) as client:
        with pytest.raises(Exception):
            # TestClient WS with no token; server closes with 4401
            with client.websocket_connect(f"/ws/query/{_SESSION_ID}") as ws:
                ws.receive_json()


def test_ws_jobs_rejects_missing_token():
    with TestClient(app) as client:
        with pytest.raises(Exception):
            with client.websocket_connect(f"/ws/jobs/{_JOB_ID}") as ws:
                ws.receive_json()


def test_ws_query_accepts_valid_token():
    from unittest.mock import patch as _patch
    # Patch auth to return a valid user_id
    with _patch("backend.api.realtime.websocket._authenticate_ws", return_value="user-123"):
        with TestClient(app) as client:
            with client.websocket_connect(f"/ws/query/{_SESSION_ID}?token=fake") as ws:
                event = ws.receive_json()
                assert event["type"] == "connected"
                assert event["session_id"] == _SESSION_ID


def test_ws_jobs_accepts_valid_token():
    from unittest.mock import patch as _patch
    with _patch("backend.api.realtime.websocket._authenticate_ws", return_value="user-123"):
        with TestClient(app) as client:
            with client.websocket_connect(f"/ws/jobs/{_JOB_ID}?token=fake") as ws:
                event = ws.receive_json()
                assert event["type"] == "connected"
                assert event["job_id"] == _JOB_ID


def test_ws_query_ping_pong():
    from unittest.mock import patch as _patch
    with _patch("backend.api.realtime.websocket._authenticate_ws", return_value="user-123"):
        with TestClient(app) as client:
            with client.websocket_connect(f"/ws/query/{_SESSION_ID}?token=fake") as ws:
                ws.receive_json()  # "connected" event
                ws.send_text("ping")
                pong = ws.receive_json()
                assert pong["type"] == "pong"


def test_ws_jobs_ping_pong():
    from unittest.mock import patch as _patch
    with _patch("backend.api.realtime.websocket._authenticate_ws", return_value="user-123"):
        with TestClient(app) as client:
            with client.websocket_connect(f"/ws/jobs/{_JOB_ID}?token=fake") as ws:
                ws.receive_json()  # "connected" event
                ws.send_text("ping")
                pong = ws.receive_json()
                assert pong["type"] == "pong"

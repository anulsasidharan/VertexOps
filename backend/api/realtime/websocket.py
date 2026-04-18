"""WebSocket endpoints for streaming query responses and job status updates."""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend.api.realtime.connection_manager import manager
from backend.core.config import get_settings
from backend.core.security import decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter()


def _authenticate_ws(token: Optional[str]) -> Optional[str]:
    """Return user_id string if token is valid, else None."""
    if not token:
        return None
    try:
        settings = get_settings()
        payload = decode_access_token(
            token,
            secret_key=settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        )
        return payload.get("sub")
    except Exception:
        return None


@router.websocket("/ws/query/{session_id}")
async def query_stream(
    websocket: WebSocket,
    session_id: str,
    token: Optional[str] = Query(default=None),
) -> None:
    """Stream query progress events to the client.

    Clients connect with ?token=<jwt> and receive JSON events:
      {"type": "token", "content": "..."}
      {"type": "done", "answer": "...", "sources": [...]}
      {"type": "error", "message": "..."}

    The server streams events published by the generation pipeline.
    """
    user_id = _authenticate_ws(token)
    if not user_id:
        await websocket.close(code=4401, reason="Unauthorized")
        return

    channel = f"query:{session_id}"
    await manager.connect(websocket, channel)
    logger.info("WS query stream: session=%s user=%s", session_id, user_id)

    try:
        await manager.send(websocket, {"type": "connected", "session_id": session_id})
        # Keep connection open; events are pushed via manager.broadcast()
        while True:
            data = await websocket.receive_text()
            # Echo ping/pong for connection health checks
            if data == "ping":
                await manager.send(websocket, {"type": "pong"})
    except WebSocketDisconnect:
        logger.info("WS query disconnect: session=%s", session_id)
    finally:
        manager.disconnect(websocket, channel)


@router.websocket("/ws/jobs/{job_id}")
async def job_status_stream(
    websocket: WebSocket,
    job_id: str,
    token: Optional[str] = Query(default=None),
) -> None:
    """Stream job status updates to the client.

    Clients receive JSON events:
      {"type": "status", "job_id": "...", "status": "running|done|failed", "progress": 0-100}
      {"type": "error", "message": "..."}

    Status events are pushed by Celery task hooks via manager.broadcast().
    """
    user_id = _authenticate_ws(token)
    if not user_id:
        await websocket.close(code=4401, reason="Unauthorized")
        return

    channel = f"job:{job_id}"
    await manager.connect(websocket, channel)
    logger.info("WS job status: job=%s user=%s", job_id, user_id)

    try:
        await manager.send(websocket, {"type": "connected", "job_id": job_id})
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send(websocket, {"type": "pong"})
    except WebSocketDisconnect:
        logger.info("WS job disconnect: job=%s", job_id)
    finally:
        manager.disconnect(websocket, channel)

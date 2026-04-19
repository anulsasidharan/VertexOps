"""WebSocket connection manager — tracks active connections per channel."""

import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Thread-safe registry of active WebSocket connections grouped by channel."""

    def __init__(self) -> None:
        self._channels: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        await websocket.accept()
        self._channels.setdefault(channel, []).append(websocket)
        logger.debug("WS connect: channel=%s total=%d", channel, len(self._channels[channel]))

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        conns = self._channels.get(channel, [])
        if websocket in conns:
            conns.remove(websocket)
        if not conns:
            self._channels.pop(channel, None)
        logger.debug("WS disconnect: channel=%s", channel)

    async def broadcast(self, channel: str, message: dict) -> None:
        """Send JSON message to all connections on a channel."""
        dead: list[WebSocket] = []
        for ws in list(self._channels.get(channel, [])):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, channel)

    async def send(self, websocket: WebSocket, message: dict) -> None:
        """Send JSON message to a single connection."""
        try:
            await websocket.send_json(message)
        except Exception as exc:
            logger.warning("WS send error: %s", exc)

    def channel_size(self, channel: str) -> int:
        return len(self._channels.get(channel, []))


# Module-level singleton shared across the app
manager = ConnectionManager()

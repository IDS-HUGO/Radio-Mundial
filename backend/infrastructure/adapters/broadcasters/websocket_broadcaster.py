"""
Adapter: WebSocketBroadcaster
Implementación concreta de IBroadcaster utilizando FastAPI WebSockets.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from __future__ import annotations

import asyncio
import logging
from typing import Set
from fastapi import WebSocket

from domain.entities import RadioBroadcastMessage
from application.ports.broadcaster import IBroadcaster

logger = logging.getLogger("radio-mundial.broadcaster")


class WebSocketBroadcaster(IBroadcaster):
    """Maneja la lista de clientes WebSocket conectados y difunde mensajes concurrentes."""

    def __init__(self) -> None:
        self._active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    @property
    def listeners_count(self) -> int:
        return len(self._active_connections)

    async def connect(self, client: WebSocket) -> None:
        await client.accept()
        async with self._lock:
            self._active_connections.add(client)
        logger.info(f"Cliente WebSocket conectado. Total oyentes: {self.listeners_count}")

    def disconnect(self, client: WebSocket) -> None:
        self._active_connections.discard(client)
        logger.info(f"Cliente WebSocket desconectado. Total oyentes: {self.listeners_count}")

    async def broadcast(self, message: RadioBroadcastMessage) -> None:
        if not self._active_connections:
            return

        payload = message.model_dump_json()
        dead_sockets: list[WebSocket] = []

        async with self._lock:
            sockets_snapshot = list(self._active_connections)

        for ws in sockets_snapshot:
            try:
                await ws.send_text(payload)
            except Exception:
                dead_sockets.append(ws)

        if dead_sockets:
            async with self._lock:
                for ws in dead_sockets:
                    self._active_connections.discard(ws)
            logger.info(f"Limpieza de {len(dead_sockets)} sockets inactivos.")

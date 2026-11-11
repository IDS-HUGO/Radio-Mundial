"""
Adapter: WebSocketBroadcaster
Implementación concurrente de alta disponibilidad para difusión masiva de WebSocket.
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
    """Maneja la lista de clientes WebSocket conectados y difunde mensajes de manera concurrente y no bloqueante."""

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
        logger.info(f"Cliente WebSocket conectado. Total oyentes activos: {self.listeners_count}")

    def disconnect(self, client: WebSocket) -> None:
        self._active_connections.discard(client)
        logger.info(f"Cliente WebSocket desconectado. Total oyentes activos: {self.listeners_count}")

    async def broadcast(self, message: RadioBroadcastMessage) -> None:
        """Difusión concurrente de ultra alta velocidad a todos los oyentes conectados en paralelo."""
        if not self._active_connections:
            return

        payload = message.model_dump_json()

        async with self._lock:
            sockets_snapshot = list(self._active_connections)

        if not sockets_snapshot:
            return

        async def _safe_send(ws: WebSocket) -> WebSocket | None:
            try:
                await asyncio.wait_for(ws.send_text(payload), timeout=3.0)
                return None
            except Exception:
                return ws

        # Disparo concurrente a todos los sockets simultáneamente con asyncio.gather
        results = await asyncio.gather(*[_safe_send(ws) for ws in sockets_snapshot], return_exceptions=True)
        dead_sockets = [r for r in results if isinstance(r, WebSocket)]

        if dead_sockets:
            async with self._lock:
                for ws in dead_sockets:
                    self._active_connections.discard(ws)
            logger.info(f"Difusión completada. Limpieza concurrente de {len(dead_sockets)} sockets inactivos.")

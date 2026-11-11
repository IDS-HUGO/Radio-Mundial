"""
Adapter: WebSocket API Controller
Controlador de conexión WebSocket para sincronización en tiempo real.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from application.ports.broadcaster import IBroadcaster
from application.ports.station_repository import IStationRepository
from domain.entities import RadioBroadcastMessage, TrackMetadata

logger = logging.getLogger("radio-mundial.websocket-api")
router = APIRouter(tags=["WebSocket"])

_broadcaster: IBroadcaster | None = None
_repository: IStationRepository | None = None


def init_websocket_controller(
    broadcaster: IBroadcaster,
    repository: IStationRepository,
) -> None:
    global _broadcaster, _repository
    _broadcaster = broadcaster
    _repository = repository


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Canal de suscripción en tiempo real de oyentes y metadatos."""
    if _broadcaster is None or _repository is None:
        await websocket.close()
        return

    await _broadcaster.connect(websocket)

    # Enviar estado inicial inmediato al oyente recién conectado
    try:
        default_st = _repository.default_station
        initial_msg = RadioBroadcastMessage(
            type="INITIAL_STATE",
            listeners_count=_broadcaster.listeners_count,
            track=TrackMetadata(
                title=f"En vivo por {default_st.name}",
                artist=f"{default_st.city}, {default_st.country}",
                album=default_st.genre,
                cover_url=default_st.logo_url
            ),
            stream_url=default_st.stream_url,
            station_id=default_st.id
        )
        await websocket.send_text(initial_msg.model_dump_json())

        # Mantener conexión activa escuchando latidos/mensajes del cliente
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        _broadcaster.disconnect(websocket)
    except Exception as e:
        logger.debug(f"Excepción en socket: {e}")
        _broadcaster.disconnect(websocket)

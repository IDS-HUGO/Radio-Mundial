"""
Use Case: BroadcastStateUseCase
Caso de uso para construir y difundir el estado de la radio a los oyentes.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from domain.entities import RadioBroadcastMessage, TrackMetadata, Station
from application.ports.broadcaster import IBroadcaster


class BroadcastStateUseCase:
    """Coordina la difusión de cambios de estado o metadatos de audio."""

    def __init__(self, broadcaster: IBroadcaster) -> None:
        self._broadcaster = broadcaster

    async def execute(self, station: Station, track: TrackMetadata | None = None) -> None:
        if track is None:
            track = TrackMetadata(
                title=f"En vivo por {station.name}",
                artist=f"{station.city}, {station.country}",
                album=station.genre,
                cover_url=station.logo_url
            )

        msg = RadioBroadcastMessage(
            type="RADIO_STATE",
            listeners_count=self._broadcaster.listeners_count,
            track=track,
            stream_url=station.stream_url,
            station_id=station.id
        )
        await self._broadcaster.broadcast(msg)

"""
Use Case: GetStationsUseCase
Caso de uso para consultar y filtrar emisoras de radio del catálogo global.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from domain.entities import Station
from application.ports.station_repository import IStationRepository


class GetStationsUseCase:
    """Ejecuta la búsqueda y filtrado de estaciones de radio."""

    def __init__(self, repository: IStationRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        continent: str | None = None,
        country: str | None = None,
        state: str | None = None,
        city: str | None = None,
        genre: str | None = None,
        band: str | None = None,
        search: str | None = None,
        limit: int = 150
    ) -> list[Station]:
        return await self._repository.get_stations(
            continent=continent,
            country=country,
            state=state,
            city=city,
            genre=genre,
            band=band,
            search=search,
            limit=limit
        )

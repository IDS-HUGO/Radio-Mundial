"""
Use Case: GetStationByIdUseCase
Caso de uso para obtener los detalles de una emisora particular.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from domain.entities import Station
from domain.exceptions import StationNotFoundException
from application.ports.station_repository import IStationRepository


class GetStationByIdUseCase:
    """Ejecuta la búsqueda de una emisora por ID con manejo de excepciones."""

    def __init__(self, repository: IStationRepository) -> None:
        self._repository = repository

    def execute(self, station_id: str) -> Station:
        station = self._repository.find_by_id(station_id)
        if not station:
            raise StationNotFoundException(station_id)
        return station

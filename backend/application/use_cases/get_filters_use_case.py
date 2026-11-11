"""
Use Case: GetFiltersUseCase
Caso de uso para consultar las opciones disponibles de filtros en el cliente.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from domain.entities import FilterOptions
from application.ports.station_repository import IStationRepository


class GetFiltersUseCase:
    """Ejecuta la obtención de los filtros disponibles."""

    def __init__(self, repository: IStationRepository) -> None:
        self._repository = repository

    def execute(self, continent: str | None = None) -> FilterOptions:
        return self._repository.get_filter_options(continent=continent)

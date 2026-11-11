"""
Port: IStationRepository
Puerto abstracto para el repositorio de datos y catálogo de emisoras.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from abc import ABC, abstractmethod
from domain.entities import Station, FilterOptions


class IStationRepository(ABC):
    """Contrato del puerto para acceder al catálogo global de emisoras."""

    @abstractmethod
    async def get_stations(
        self,
        country: str | None = None,
        state: str | None = None,
        city: str | None = None,
        genre: str | None = None,
        band: str | None = None,
        search: str | None = None,
        limit: int = 150
    ) -> list[Station]:
        """Obtiene una lista de estaciones filtradas con resolución dinámica."""
        pass

    @abstractmethod
    def find_by_id(self, station_id: str) -> Station | None:
        """Busca una emisora específica por su identificador único."""
        pass

    @abstractmethod
    def get_filter_options(self) -> FilterOptions:
        """Retorna las opciones disponibles para el filtrado en el cliente."""
        pass

    @abstractmethod
    async def warmup(self) -> None:
        """Pre-carga asíncrona del catálogo de alto volumen."""
        pass

    @property
    @abstractmethod
    def total_count(self) -> int:
        """Número total de emisoras registradas en memoria."""
        pass

    @property
    @abstractmethod
    def default_station(self) -> Station:
        """Emisora inicial predeterminada para el arranque de la radio."""
        pass

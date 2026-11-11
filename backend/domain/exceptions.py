"""
Domain Exceptions - Radio Mundial
Excepciones de dominio tipadas para manejo limpio y desacoplado.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

class DomainException(Exception):
    """Excepción base de dominio."""
    pass


class StationNotFoundException(DomainException):
    """Lanzada cuando una emisora requerida por ID no existe en el catálogo."""
    def __init__(self, station_id: str) -> None:
        self.station_id = station_id
        super().__init__(f"Emisora con ID '{station_id}' no encontrada en el catálogo.")


class StreamUnavailableException(DomainException):
    """Lanzada cuando un enlace de streaming no responde o es inválido."""
    def __init__(self, stream_url: str, reason: str = "Inaccesible") -> None:
        self.stream_url = stream_url
        self.reason = reason
        super().__init__(f"Stream en '{stream_url}' no disponible: {reason}")

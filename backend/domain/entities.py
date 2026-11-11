"""
Domain Entities - Radio Mundial
Core business representations of radio stations, metadata, broadcast events, and filter options.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class Station(BaseModel):
    """Representa una estación de radio sintonizable en el catálogo mundial."""
    id: str = Field(..., description="Identificador único slug")
    name: str = Field(..., description="Nombre comercial de la emisora")
    continent: str = Field("América", description="Continente de origen (América, Europa, Asia, África, Oceanía)")
    country: str = Field(..., description="País de origen")
    country_code: str = Field(..., description="Código ISO 2 letras del país (ej. MX, US)")
    state: str = Field("Nacional", description="Estado, provincia o región")
    city: str = Field(..., description="Ciudad de transmisión")
    locality: str = Field(..., description="Localidad, municipio o alcaldía")
    genre: str = Field(..., description="Género musical o temático principal")
    stream_url: str = Field(..., description="URL directa del streaming de audio")
    logo_url: str = Field(..., description="URL del logotipo de la estación")
    description: str = Field(..., description="Breve descripción de la emisora")
    bitrate: str = Field("128 kbps", description="Calidad de transmisión")
    frequency: float = Field(98.5, description="Frecuencia en MHz (FM) o kHz (AM)")
    band: str = Field("FM", description="Banda de transmisión: FM o AM")


class TrackMetadata(BaseModel):
    """Metadatos de la canción o programa transmitido en el stream."""
    title: str = Field(..., description="Título de la pista actual")
    artist: str = Field(..., description="Nombre del artista o programa")
    album: str | None = Field(default=None, description="Álbum o podcast")
    cover_url: str | None = Field(default=None, description="URL de la portada del álbum")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RadioBroadcastMessage(BaseModel):
    """Evento difundido a los oyentes conectados en tiempo real por WebSocket."""
    type: str = Field("RADIO_STATE", description="Tipo de evento para el frontend")
    listeners_count: int = Field(..., ge=0, description="Oyentes conectados simultáneamente")
    track: TrackMetadata = Field(..., description="Metadata de la pista en curso")
    stream_url: str = Field(..., description="URL directa del streaming de audio")
    station_id: str | None = Field(default=None, description="ID de la estación activa")
    server_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FilterOptions(BaseModel):
    """Opciones dinámicas de filtros disponibles en el catálogo de radio."""
    continents: list[str] = Field(default_factory=lambda: ["América", "Europa", "Asia", "África", "Oceanía"])
    countries: list[str]
    states: list[str]
    cities: list[str]
    localities: list[str]
    genres: list[str]
    total_stations: int

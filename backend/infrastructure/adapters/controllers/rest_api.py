"""
Adapter: REST API Controller
Endpoints REST FastAPI desacoplados mediante casos de uso.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from __future__ import annotations

from fastapi import APIRouter, Query, HTTPException, status
from domain.entities import Station, FilterOptions
from domain.exceptions import StationNotFoundException
from application.use_cases import (
    GetStationsUseCase,
    GetFiltersUseCase,
    GetStationByIdUseCase,
)

router = APIRouter(tags=["Radio API"])

# Las instancias de los casos de uso serán inyectadas por el contenedor principal
_get_stations_uc: GetStationsUseCase | None = None
_get_filters_uc: GetFiltersUseCase | None = None
_get_station_by_id_uc: GetStationByIdUseCase | None = None


def init_rest_controller(
    get_stations_uc: GetStationsUseCase,
    get_filters_uc: GetFiltersUseCase,
    get_station_by_id_uc: GetStationByIdUseCase,
) -> None:
    global _get_stations_uc, _get_filters_uc, _get_station_by_id_uc
    _get_stations_uc = get_stations_uc
    _get_filters_uc = get_filters_uc
    _get_station_by_id_uc = get_station_by_id_uc


@router.get("/health", tags=["Salud"])
@router.get("/api/health", tags=["Salud"])
async def health_check() -> dict[str, str]:
    """Chequeo de salud del servicio para orquestadores y balanceadores."""
    return {"status": "ok", "app": "Radio Mundial API", "version": "4.5"}


@router.get("/api/stations", response_model=list[Station])
async def get_stations(
    continent: str | None = Query(None, description="Filtrar por continente (América, Europa, Asia, África, Oceanía)"),
    country: str | None = Query(None, description="Filtrar por país"),
    state: str | None = Query(None, description="Filtrar por estado o provincia"),
    city: str | None = Query(None, description="Filtrar por ciudad"),
    genre: str | None = Query(None, description="Filtrar por género"),
    band: str | None = Query(None, description="Filtrar por banda (FM o AM)"),
    search: str | None = Query(None, description="Término de búsqueda de texto"),
    limit: int = Query(150, ge=1, le=500, description="Límite máximo de emisoras")
) -> list[Station]:
    """Retorna emisoras filtradas con catálogo pre-calentado y consulta bajo demanda."""
    if _get_stations_uc is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="API inicializando...")
    return await _get_stations_uc.execute(
        continent=continent,
        country=country,
        state=state,
        city=city,
        genre=genre,
        band=band,
        search=search,
        limit=limit
    )


@router.get("/api/filters", response_model=FilterOptions)
async def get_filters(
    continent: str | None = Query(None, description="Filtrar opciones por continente")
) -> FilterOptions:
    """Retorna la lista de continentes, países, estados, ciudades y géneros indexados."""
    if _get_filters_uc is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="API inicializando...")
    return _get_filters_uc.execute(continent=continent)


@router.get("/api/stations/{station_id}", response_model=Station)
async def get_station_by_id(station_id: str) -> Station:
    """Obtiene los detalles de una estación específica por ID."""
    if _get_station_by_id_uc is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="API inicializando...")
    try:
        return _get_station_by_id_uc.execute(station_id)
    except StationNotFoundException as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))

"""
Adapter: REST API Controller
Endpoints REST FastAPI desacoplados mediante casos de uso con soporte de caché perimetral (CDN/Edge).
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from fastapi import APIRouter, Query, HTTPException, Response, status
from domain.entities import Station, FilterOptions, FeedbackSubmission
from domain.exceptions import StationNotFoundException
from application.use_cases import (
    GetStationsUseCase,
    GetFiltersUseCase,
    GetStationByIdUseCase,
)

logger = logging.getLogger("radio-mundial.rest")
router = APIRouter(tags=["Radio API"])
_feedback_lock = asyncio.Lock()


def _get_feedback_path() -> str:
    candidates = ["backend/data/feedback_submissions.json", "data/feedback_submissions.json"]
    for c in candidates:
        parent = os.path.dirname(c)
        if os.path.exists(parent):
            return c
    return "backend/data/feedback_submissions.json"

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
    return {"status": "ok", "app": "Radio Mundial API", "version": "5.0"}


@router.get("/api/stations", response_model=list[Station])
async def get_stations(
    response: Response,
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
    
    # Cabeceras de caché perimetral para alta concurrencia
    response.headers["Cache-Control"] = "public, max-age=1800, s-maxage=86400, stale-while-revalidate=600"
    response.headers["Vary"] = "Accept-Encoding"

    # Sanitizar parámetros contra objetos Query de FastAPI
    c_cont = continent if isinstance(continent, str) else None
    c_country = country if isinstance(country, str) else None
    c_state = state if isinstance(state, str) else None
    c_city = city if isinstance(city, str) else None
    c_genre = genre if isinstance(genre, str) else None
    c_band = band if isinstance(band, str) else None
    c_search = search if isinstance(search, str) else None
    c_limit = limit if isinstance(limit, int) else 150

    return await _get_stations_uc.execute(
        continent=c_cont,
        country=c_country,
        state=c_state,
        city=c_city,
        genre=c_genre,
        band=c_band,
        search=c_search,
        limit=c_limit
    )


@router.get("/api/filters", response_model=FilterOptions)
async def get_filters(
    response: Response,
    continent: str | None = Query(None, description="Filtrar opciones por continente")
) -> FilterOptions:
    """Retorna la lista de continentes, países, estados, ciudades y géneros indexados."""
    if _get_filters_uc is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="API inicializando...")
    
    response.headers["Cache-Control"] = "public, max-age=3600, s-maxage=86400, stale-while-revalidate=1200"
    response.headers["Vary"] = "Accept-Encoding"

    c_cont = continent if isinstance(continent, str) else None
    return _get_filters_uc.execute(continent=c_cont)


@router.get("/api/stations/{station_id}", response_model=Station)
async def get_station_by_id(station_id: str, response: Response) -> Station:
    """Obtiene los detalles de una estación específica por ID."""
    if _get_station_by_id_uc is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="API inicializando...")
    try:
        response.headers["Cache-Control"] = "public, max-age=3600, s-maxage=86400"
        return _get_station_by_id_uc.execute(station_id)
    except StationNotFoundException as ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ex))


@router.post("/api/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(submission: FeedbackSubmission) -> dict[str, str]:
    """Registra un comentario, reporte de estación caída o solicitud de nueva emisora."""
    fpath = _get_feedback_path()
    async with _feedback_lock:
        try:
            records: list[dict] = []
            if os.path.exists(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        records = json.load(f)
                except Exception:
                    records = []
            
            # Serializar submission con formato ISO para fechas
            data = submission.model_dump(mode="json")
            records.append(data)
            
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Feedback recibido: [{submission.category}] id={submission.id} estación={submission.station_name}")
            return {
                "status": "success",
                "id": submission.id,
                "message": "¡Gracias por tu mensaje! Tu sugerencia nos ayuda a que Radio Mundial sea cada día mejor."
            }
        except Exception as e:
            logger.error(f"Error guardando feedback: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo registrar el comentario en el servidor."
            )


@router.get("/api/feedback", response_model=dict)
async def get_all_feedback(limit: int = Query(default=50, ge=1, le=200)) -> dict:
    """Consulta las sugerencias y comentarios registrados para el equipo de administración."""
    max_items = limit if isinstance(limit, int) else getattr(limit, "default", 50)
    if not isinstance(max_items, int):
        max_items = 50
    fpath = _get_feedback_path()
    async with _feedback_lock:
        if not os.path.exists(fpath):
            return {"total": 0, "submissions": []}
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                records = json.load(f)
            # Retornar los más recientes primero
            reversed_records = list(reversed(records))[:max_items]
            return {"total": len(records), "submissions": reversed_records}
        except Exception as e:
            logger.warning(f"Error leyendo feedback: {e}")
            return {"total": 0, "submissions": []}

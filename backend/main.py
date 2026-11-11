"""
Radio Mundial - Backend Application (Clean / Hexagonal Architecture Entrypoint)
Ensamblador y contenedor de inyección de dependencias optimizado para alta concurrencia.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from infrastructure.config.settings import settings
from infrastructure.adapters.repositories.in_memory_station_repository import InMemoryStationRepository
from infrastructure.adapters.broadcasters.websocket_broadcaster import WebSocketBroadcaster
from infrastructure.adapters.controllers.rest_api import router as rest_router, init_rest_controller
from infrastructure.adapters.controllers.websocket_api import router as ws_router, init_websocket_controller
from application.use_cases import (
    GetStationsUseCase,
    GetFiltersUseCase,
    GetStationByIdUseCase,
    BroadcastStateUseCase,
)

# Configuración de Logging Estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("radio-mundial.bootstrap")

# Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["300/minute"])

# -------------------------------------------------------------------------
# Inyección de Dependencias (Composition Root)
# -------------------------------------------------------------------------
repository = InMemoryStationRepository(seed_path=settings.seed_path)
broadcaster = WebSocketBroadcaster()

get_stations_uc = GetStationsUseCase(repository)
get_filters_uc = GetFiltersUseCase(repository)
get_station_by_id_uc = GetStationByIdUseCase(repository)
broadcast_state_uc = BroadcastStateUseCase(broadcaster)

# Inicializar Controladores con los Casos de Uso
init_rest_controller(get_stations_uc, get_filters_uc, get_station_by_id_uc)
init_websocket_controller(broadcaster, repository)


async def background_periodic_broadcaster() -> None:
    """Tarea periódica de difusión de latidos y estado general a oyentes concurrentes."""
    while True:
        try:
            await asyncio.sleep(25)
            if broadcaster.listeners_count > 0:
                default_st = repository.default_station
                await broadcast_state_uc.execute(default_st)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.debug(f"Error en broadcast periódico: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Ciclo de vida de la aplicación con calentamiento del catálogo en segundo plano."""
    logger.info(f"Iniciando {settings.app_name} v5.0 (Arquitectura Hexagonal Limpia)...")
    logger.info("Licencia: Hugo Francisco Luis Inclan - MIT 2026")

    # Iniciar pre-calentamiento del catálogo
    warmup_task = None
    if settings.enable_warmup:
        warmup_task = asyncio.create_task(repository.warmup())

    ticker_task = asyncio.create_task(background_periodic_broadcaster())

    yield

    ticker_task.cancel()
    if warmup_task and not warmup_task.done():
        warmup_task.cancel()
    logger.info("Cierre ordenado de Radio Mundial Backend completado.")


# Creación de la Aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version="5.0.0",
    description="Backend de ultra alta concurrencia y streaming directo CDN de Radio Mundial. Arquitectura Hexagonal.",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Compresión automática GZip para respuestas mayores a 1KB (reduce payloads JSON en ~85%)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

# Registro de Rutas
app.include_router(rest_router)
app.include_router(ws_router)

# ⚙️ Radio Mundial — Backend Service (Hexagonal / Clean Architecture)

> **Autor:** Hugo Francisco Luis Inclan  
> **Copyright (c) 2026 Hugo Francisco Luis Inclan.** Todos los derechos reservados.  
> **Licencia:** MIT License.  
> **Framework:** FastAPI (Python 3.11+ / 3.14) con ASGI Concurrente.  
> **Enfoque Arquitectónico:** Clean Architecture (Robert C. Martin) y Hexagonal Ports & Adapters (Alistair Cockburn).

---

## 🏛️ Arquitectura Hexagonal y Separación de Responsabilidades

El backend está estructurado en 3 capas concéntricas con flujo de dependencias unidireccional hacia el dominio:

```
backend/
├── domain/                                # Capa 1: Núcleo de Reglas de Negocio
│   ├── entities.py                        # Station, TrackMetadata, FilterOptions, RadioBroadcastMessage
│   └── exceptions.py                      # StationNotFoundException, DomainValidationException
│
├── application/                           # Capa 2: Casos de Uso y Puertos Abstractos
│   ├── ports/
│   │   ├── station_repository.py          # Interface IStationRepository
│   │   └── broadcaster.py                 # Interface IBroadcaster
│   └── use_cases/
│       ├── get_stations_use_case.py       # Consulta filtrada con estrategia de fallback
│       ├── get_filters_use_case.py        # Agregación dinámica de opciones disponibles
│       ├── get_station_by_id_use_case.py  # Búsqueda unívoca por identificador
│       └── broadcast_state_use_case.py    # Emisión de latidos y estado global
│
├── infrastructure/                        # Capa 3: Adaptadores Técnicos y Frameworks
│   ├── config/
│   │   └── settings.py                    # Configuración fuertemente tipada (Pydantic BaseSettings)
│   └── adapters/
│       ├── repositories/
│       │   └── in_memory_station_repository.py # Repositorio en memoria con índices O(1)
│       ├── broadcasters/
│       │   └── websocket_broadcaster.py   # Difusión concurrente no bloqueante (asyncio.gather)
│       └── controllers/
│           ├── rest_api.py                # Controladores REST con cabeceras de caché RFC 9111
│           └── websocket_api.py           # Endpoint WebSocket bi-direccional
│
├── data/                                  # Almacenamiento Modular de Catálogo
│   ├── continents/                        # Particiones modulares por continente
│   │   ├── america.json                   # 981 emisoras (53 países)
│   │   ├── europa.json                    # 1,270 emisoras (51 países)
│   │   ├── asia.json                      # 715 emisoras (49 países)
│   │   ├── africa.json                    # 454 emisoras (51 países)
│   │   └── oceania.json                   # 155 emisoras (19 países)
│   ├── seed_stations.json                 # Catálogo unificado maestro (3,575 emisoras)
│   └── global_harvester.py                # Motor de recolección y verificación mundial
│
├── main.py                                # Composition Root e inyección de dependencias
├── Dockerfile                             # Imagen optimizada Alpine / Python Slim
└── requirements.txt                       # Dependencias mínimas auditadas
```

---

## ⚡ Estrategias de Ultra Alta Concurrencia

Diseñado para soportar miles de conexiones simultáneas con recursos mínimos:

1. **Streaming Directo CDN (Zero Audio Proxy):**  
   El backend entrega únicamente metadatos ligeros (JSON). El audio fluye directamente desde redes de transmisión perimetrales (*StreamTheWorld, Akamai, Zeno, Fastly, SonicPanel*), permitiendo atender a millones de oyentes sin saturar el ancho de banda ni la CPU del servidor.
2. **Compresión Automática GZip:**  
   `GZipMiddleware(minimum_size=1000)` comprime las respuestas mayores a 1 KB, reduciendo el peso de la API en un **85-90%** (de ~1.8 MB a ~110 KB).
3. **Caché Perimetral RFC 9111:**  
   Cabeceras `Cache-Control: public, max-age=1800, s-maxage=86400, stale-while-revalidate=600` permiten que proxies inversos (Cloudflare, Nginx, Varnish) sirvan las consultas repetitivas en **0 ms**.
4. **Índices Secundarios O(1):**  
   Mapas indexados en memoria (`_by_continent`, `_by_country`, `_by_band`) resuelven búsquedas en menos de **0.0001 segundos**.
5. **Broadcaster Concurrente con `asyncio.gather`:**  
   Envío simultáneo a todos los clientes WebSocket conectados sin bloquear el bucle de eventos principal.

---

## 🔌 Especificación de la API

### Endpoints REST
| Método | Endpoint | Parámetros | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Ninguno | Estado de salud para monitores y balanceadores |
| `GET` | `/api/stations` | `continent`, `country`, `state`, `city`, `genre`, `band`, `search`, `limit` | Lista paginada y filtrada de emisoras activas |
| `GET` | `/api/filters` | `continent` (opcional) | Lista de continentes, países, estados, ciudades y géneros disponibles |
| `GET` | `/api/stations/{id}`| `station_id` en URL | Detalle de emisora por identificador |

### WebSocket
* **Endpoint:** `/ws/stream`
* **Mensajes Recibidos:** Transmite periódicamente el recuento de oyentes concurrentes y metadatos de reproducción actual en formato JSON.

---

## 🚀 Ejecución Local y Pruebas

```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor de desarrollo
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Documentación OpenAPI interactiva disponible en: `http://localhost:8000/docs`

---

## 🐳 Despliegue con Docker

```bash
docker build -t radio-mundial-backend:latest .
docker run -d -p 8000:8000 --name radio-backend radio-mundial-backend:latest
```

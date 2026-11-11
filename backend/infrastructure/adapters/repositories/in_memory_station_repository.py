"""
Adapter: InMemoryStationRepository
Implementación concreta de IStationRepository con agregación dinámica de Radio-Browser API.
Author: Hugo Francisco Luis Inclan
Copyright (c) 2026 Hugo Francisco Luis Inclan
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import unicodedata
import urllib.parse
import urllib.request
from typing import Any

from domain.entities import Station, FilterOptions
from application.ports.station_repository import IStationRepository

logger = logging.getLogger("radio-mundial.repository")

COUNTRY_NORMALIZER: dict[str, str] = {
    "mexico": "México", "spain": "España", "united states": "Estados Unidos",
    "usa": "Estados Unidos", "colombia": "Colombia", "argentina": "Argentina",
    "united kingdom": "Reino Unido", "france": "Francia", "switzerland": "Suiza",
    "chile": "Chile", "peru": "Perú", "brazil": "Brasil", "germany": "Alemania",
    "italy": "Italia", "japan": "Japón", "canada": "Canadá", "ecuador": "Ecuador",
    "uruguay": "Uruguay", "venezuela": "Venezuela", "costa rica": "Costa Rica",
    "panama": "Panamá", "guatemala": "Guatemala", "puerto rico": "Puerto Rico",
    "el salvador": "El Salvador", "honduras": "Honduras", "nicaragua": "Nicaragua",
    "belice": "Belice", "belize": "Belice", "republica dominicana": "República Dominicana",
    "dominican republic": "República Dominicana", "cuba": "Cuba", "jamaica": "Jamaica",
    "bolivia": "Bolivia", "paraguay": "Paraguay",
    "netherlands": "Países Bajos", "australia": "Australia", "portugal": "Portugal"
}

COUNTRY_CONTINENT_MAP: dict[str, str] = {
    # América
    "mexico": "América", "estados unidos": "América", "usa": "América", "canada": "América",
    "colombia": "América", "argentina": "América", "brasil": "América", "chile": "América",
    "peru": "América", "ecuador": "América", "venezuela": "América", "bolivia": "América",
    "uruguay": "América", "paraguay": "América", "guatemala": "América", "el salvador": "América",
    "honduras": "América", "nicaragua": "América", "costa rica": "América", "panama": "América",
    "belice": "América", "republica dominicana": "América", "puerto rico": "América",
    "cuba": "América", "jamaica": "América",
    # Europa
    "espana": "Europa", "reino unido": "Europa", "francia": "Europa", "alemania": "Europa",
    "italia": "Europa", "suiza": "Europa", "portugal": "Europa", "paises bajos": "Europa",
    "belgica": "Europa", "austria": "Europa", "suecia": "Europa", "noruega": "Europa",
    "dinamarca": "Europa", "finlandia": "Europa", "irlanda": "Europa", "grecia": "Europa",
    "polonia": "Europa", "republica checa": "Europa",
    # Asia
    "japon": "Asia", "corea del sur": "Asia", "china": "Asia", "hong kong": "Asia",
    "taiwan": "Asia", "india": "Asia", "indonesia": "Asia", "filipinas": "Asia",
    "tailandia": "Asia", "vietnam": "Asia", "singapur": "Asia", "malasia": "Asia",
    "turquia": "Asia", "emiratos arabes unidos": "Asia", "israel": "Asia", "arabia saudita": "Asia",
    # África
    "sudafrica": "África", "nigeria": "África", "egipto": "África", "kenia": "África",
    "marruecos": "África", "ghana": "África", "senegal": "África", "costa de marfil": "África",
    "argelia": "África", "tunez": "África",
    # Oceanía
    "australia": "Oceanía", "nueva zelanda": "Oceanía", "fiyi": "Oceanía", "papua nueva guinea": "Oceanía"
}

MEXICO_STATES: list[str] = [
    "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas",
    "Chihuahua", "Ciudad de México", "Coahuila", "Colima", "Durango", "Estado de México",
    "Guanajuato", "Guerrero", "Hidalgo", "Jalisco", "Michoacán", "Morelos", "Nayarit",
    "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí",
    "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas"
]


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    ).strip()


class InMemoryStationRepository(IStationRepository):
    """Adaptador de repositorio con persistencia en memoria y consulta externa."""

    def __init__(self, seed_path: str = "data/seed_stations.json", continents_dir: str = "data/continents") -> None:
        self._seed_path = seed_path
        self._continents_dir = continents_dir
        self._cache: list[Station] = []
        self._url_index: set[str] = set()
        self._id_index: dict[str, Station] = {}
        self._load_seed()

    def _load_seed(self) -> None:
        loaded = 0
        if os.path.exists(self._continents_dir):
            try:
                for file_name in sorted(os.listdir(self._continents_dir)):
                    if file_name.endswith(".json"):
                        file_path = os.path.join(self._continents_dir, file_name)
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            for item in data:
                                st = Station(**item)
                                if self._add_to_cache(st):
                                    loaded += 1
                logger.info(f"Catálogo por continentes cargado con éxito: {loaded} emisoras desde {self._continents_dir}.")
            except Exception as e:
                logger.warning(f"Error cargando directorio de continentes {self._continents_dir}: {e}")

        if not self._cache and os.path.exists(self._seed_path):
            try:
                with open(self._seed_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        st = Station(**item)
                        self._add_to_cache(st)
                logger.info(f"Semilla cargada con éxito: {len(self._cache)} emisoras iniciales.")
            except Exception as e:
                logger.warning(f"No se pudo cargar semilla {self._seed_path}: {e}")

    def _add_to_cache(self, st: Station) -> bool:
        if st.stream_url in self._url_index:
            return False
        if not st.continent or st.continent == "América":
            norm_c = normalize_text(st.country)
            st.continent = COUNTRY_CONTINENT_MAP.get(norm_c, st.continent or "América")
        self._url_index.add(st.stream_url)
        self._cache.append(st)
        self._id_index[st.id] = st
        return True

    @property
    def total_count(self) -> int:
        return len(self._cache)

    @property
    def default_station(self) -> Station:
        return self._cache[0] if self._cache else Station(
            id="default-radio", name="Radio Mundial", country="México", country_code="MX",
            state="Ciudad de México", city="Ciudad de México", locality="Centro", genre="Pop & Éxitos",
            stream_url="https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40_MEXICOAAC.aac",
            logo_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
            description="Emisora predeterminada.", bitrate="128 kbps", frequency=101.7, band="FM"
        )

    def find_by_id(self, station_id: str) -> Station | None:
        return self._id_index.get(station_id)

    def query_radio_browser_sync(self, params: dict[str, str]) -> list[Station]:
        mirrors = [
            "https://de1.api.radio-browser.info",
            "https://at1.api.radio-browser.info",
            "https://nl1.api.radio-browser.info"
        ]
        stations: list[Station] = []
        query_str = urllib.parse.urlencode(params)

        for mirror in mirrors:
            url = f"{mirror}/json/stations/search?{query_str}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "RadioMundialAggregator/4.5"})
                with urllib.request.urlopen(req, timeout=3.5) as res:
                    items = json.loads(res.read().decode("utf-8"))
                    for it in items:
                        stream_url = it.get("url_resolved") or it.get("url")
                        if not stream_url or not stream_url.startswith("http"):
                            continue

                        raw_country = it.get("country") or "Mundial"
                        norm_c = normalize_text(raw_country)
                        country_name = COUNTRY_NORMALIZER.get(norm_c, raw_country)

                        raw_state = it.get("state") or "Nacional"
                        clean_state = raw_state.split(",")[-1].strip() if "," in raw_state else raw_state.strip() or "Nacional"

                        tags = it.get("tags") or "Música"
                        genre = tags.split(",")[0].capitalize() if tags else "General"
                        name_raw = it.get("name", "radio")
                        hash_val = sum(ord(c) for c in name_raw)
                        
                        is_am = " AM" in name_raw.upper() or name_raw.upper().endswith("AM") or " AM " in name_raw.upper()
                        band = "AM" if is_am else "FM"
                        if is_am:
                            freq = float(540 + (hash_val % 106) * 10)
                        else:
                            freq = round(88.0 + (hash_val % 199) * 0.1, 1)

                        stations.append(
                            Station(
                                id=f"rb-{it.get('stationuuid', '')[:12]}",
                                name=name_raw[:55],
                                country=country_name,
                                country_code=it.get("countrycode", "XX")[:2].upper(),
                                state=clean_state,
                                city=clean_state,
                                locality="En vivo",
                                genre=genre[:25],
                                stream_url=stream_url,
                                logo_url=it.get("favicon") or "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
                                description=f"Emisora transmitiendo desde {clean_state}, {country_name}.",
                                bitrate=f"{it.get('bitrate', 128)} kbps",
                                frequency=freq,
                                band=band
                            )
                        )
                    if stations:
                        break
            except Exception:
                continue
        return stations

    async def warmup(self) -> None:
        """Pre-carga asíncrona de estaciones populares de México y el mundo."""
        logger.info("Iniciando pre-calentamiento del catálogo de radio...")
        loop = asyncio.get_event_loop()
        warmup_queries = [
            {"country": "Mexico", "limit": "150", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "Spain", "limit": "60", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "Colombia", "limit": "60", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "Argentina", "limit": "60", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "United States", "limit": "90", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "Brazil", "limit": "50", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "United Kingdom", "limit": "50", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "France", "limit": "50", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "Chile", "limit": "40", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "Peru", "limit": "40", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "Germany", "limit": "40", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "Italy", "limit": "40", "order": "votes", "reverse": "true", "hidebroken": "true"},
            {"country": "Japan", "limit": "30", "order": "votes", "reverse": "true", "hidebroken": "true"}
        ]
        for q in warmup_queries:
            try:
                res = await loop.run_in_executor(None, self.query_radio_browser_sync, q)
                for st in res:
                    self._add_to_cache(st)
            except Exception:
                pass
        logger.info(f"Pre-calentamiento finalizado: {self.total_count} estaciones listas en memoria.")

    async def get_stations(
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
        pool = list(self._cache)

        # Consulta bajo demanda si el estado solicitado tiene pocos resultados
        if state and state.lower() not in ["todos", "todas"]:
            s_norm = normalize_text(state)
            matching = [s for s in pool if s_norm in normalize_text(s.state)]
            if len(matching) < 4:
                country_param = "Mexico" if (not country or country.lower() in ["todos", "mexico", "méxico"]) else country
                live = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.query_radio_browser_sync,
                    {"country": country_param, "state": state, "limit": "40", "hidebroken": "true"}
                )
                for st in live:
                    st.state = state
                    if self._add_to_cache(st):
                        pool.append(st)

        results = pool

        if continent and continent.strip().lower() != "todos":
            cont_norm = normalize_text(continent)
            results = [s for s in results if normalize_text(s.continent) == cont_norm]

        if country and country.strip().lower() != "todos":
            c_norm = normalize_text(country)
            aliases = {c_norm}
            if c_norm in ["estados unidos", "usa", "us", "united states"]:
                aliases.update(["estados unidos", "usa", "us", "united states"])
            elif c_norm in ["mexico", "mx"]:
                aliases.update(["mexico", "mx"])
            elif c_norm in ["espana", "spain", "es"]:
                aliases.update(["espana", "spain", "es"])
            elif c_norm in ["reino unido", "uk", "gb", "united kingdom"]:
                aliases.update(["reino unido", "uk", "gb", "united kingdom"])

            results = [
                s for s in results
                if any(
                    a in normalize_text(s.country) or
                    normalize_text(s.country) in a or
                    normalize_text(s.country_code) == a
                    for a in aliases
                )
            ]

        if state and state.strip().lower() not in ["todos", "todas"]:
            st_norm = normalize_text(state)
            results = [s for s in results if st_norm in normalize_text(s.state) or normalize_text(s.state) in st_norm]

        if city and city.strip().lower() not in ["todas", "todos"]:
            city_norm = normalize_text(city)
            results = [s for s in results if city_norm in normalize_text(s.city)]

        if genre and genre.strip().lower() != "todos":
            g_norm = normalize_text(genre)
            results = [s for s in results if g_norm in normalize_text(s.genre)]

        if band and band.strip().lower() not in ["todos", "todas"]:
            b_norm = band.strip().upper()
            results = [s for s in results if s.band.upper() == b_norm]

        if search and search.strip():
            q_norm = normalize_text(search)
            results = [
                s for s in results
                if (
                    q_norm in normalize_text(s.name) or
                    q_norm in normalize_text(s.country) or
                    q_norm in normalize_text(s.state) or
                    q_norm in normalize_text(s.city) or
                    q_norm in normalize_text(s.genre) or
                    q_norm in normalize_text(s.description)
                )
            ]

        return results[:limit]

    def get_filter_options(self, continent: str | None = None) -> FilterOptions:
        continents = ["América", "Europa", "Asia", "África", "Oceanía"]

        target_pool = self._cache
        if continent and continent.strip().lower() != "todos":
            c_norm = normalize_text(continent)
            target_pool = [s for s in self._cache if normalize_text(s.continent) == c_norm]

        cache_countries = sorted(list({s.country for s in target_pool if s.country}))
        if "México" in cache_countries:
            cache_countries.remove("México")
            countries = ["México"] + cache_countries
        else:
            countries = cache_countries

        cache_genres = sorted(list({s.genre for s in target_pool if s.genre}))
        genres = cache_genres if cache_genres else [
            "Pop & Éxitos", "Rock Alternativo", "Rock & Metal", "Regional Mexicano & Banda",
            "Noticias & Opinión", "Jazz & Fusión", "Salsa & Cumbia", "Romántica & Baladas",
            "Música Clásica", "Hip-Hop & Urbano", "Electrónica & Dance"
        ]

        states = sorted(list({s.state for s in target_pool if s.state and s.state != "Nacional"}))
        if not continent or normalize_text(continent) == "america" or normalize_text(continent) == "todos":
            for ms in MEXICO_STATES:
                if ms not in states:
                    states.append(ms)
            states = sorted(states)

        cities = sorted(list({s.city for s in target_pool if s.city and s.city != "Nacional"}))
        localities = sorted(list({s.locality for s in target_pool if s.locality and s.locality != "En vivo"}))

        return FilterOptions(
            continents=continents,
            countries=countries,
            states=states[:150],
            cities=cities[:150],
            localities=localities[:80],
            genres=genres,
            total_stations=len(target_pool)
        )

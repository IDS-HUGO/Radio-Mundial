#!/usr/bin/env python3
"""
Global Catalog Builder - Radio Mundial
Produces modular continent datasets:
  - backend/data/continents/america.json
  - backend/data/continents/europa.json
  - backend/data/continents/asia.json
  - backend/data/continents/africa.json
  - backend/data/continents/oceania.json
Aggregates them into:
  - backend/data/seed_stations.json
  - frontend/wwwroot/sample-data/stations.json

Author: Hugo Francisco Luis Inclan (c) 2026
"""

import json
import os
import re
import urllib.parse
import urllib.request
import unicodedata

MIRRORS = [
    "https://de1.api.radio-browser.info",
    "https://at1.api.radio-browser.info",
    "https://nl1.api.radio-browser.info"
]

def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    return "".join(
        c for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    ).strip()

def query_rb(country: str, country_code: str = "", limit: int = 15) -> list[dict]:
    query_dict = {
        "limit": str(limit),
        "order": "votes",
        "reverse": "true",
        "hidebroken": "true"
    }
    if country_code and country_code != "XX":
        query_dict["countrycode"] = country_code
    else:
        query_dict["country"] = country

    params = urllib.parse.urlencode(query_dict)
    for m in MIRRORS:
        url = f"{m}/json/stations/search?{params}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RadioMundialAggregator/4.5"})
            with urllib.request.urlopen(req, timeout=4.0) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            continue
    return []

def clean_station(raw: dict, continent: str, country_name: str, country_code: str, default_state: str, default_city: str) -> dict | None:
    stream_url = raw.get("url_resolved") or raw.get("url")
    if not stream_url or not stream_url.startswith("http"):
        return None
    
    name = (raw.get("name") or "Radio").strip()
    if len(name) < 2 or "test" in name.lower():
        return None
    
    state = (raw.get("state") or "").strip()
    if not state or state.lower() in ["unknown", "none", "n/a", ""]:
        state = default_state
    if "," in state:
        state = state.split(",")[-1].strip()
    
    city = default_city
    if state and state != default_state:
        city = state

    tags = raw.get("tags") or ""
    first_tag = tags.split(",")[0].strip().capitalize() if tags else "Pop & Éxitos"
    genre = first_tag if len(first_tag) > 2 else "Variada"

    is_am = " AM" in name.upper() or name.upper().endswith("AM") or " AM " in name.upper()
    band = "AM" if is_am else "FM"
    
    freq_match = re.search(r"(\d{2,4}(?:\.\d)?)", name)
    freq = 98.5
    if freq_match:
        try:
            val = float(freq_match.group(1))
            if is_am and 530 <= val <= 1700:
                freq = val
            elif not is_am and 87.0 <= val <= 108.5:
                freq = val
        except ValueError:
            pass
    
    if freq == 98.5:
        h = sum(ord(c) for c in name)
        freq = float(540 + (h % 106) * 10) if is_am else round(88.0 + (h % 199) * 0.1, 1)

    logo = raw.get("favicon")
    if not logo or not logo.startswith("http"):
        logo = "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop"

    station_id = f"rb-{raw.get('stationuuid', '')[:12]}" if raw.get('stationuuid') else f"{normalize_text(name)[:10]}-{normalize_text(country_name)[:4]}"

    return {
        "id": station_id,
        "name": name[:55],
        "continent": continent,
        "country": country_name,
        "country_code": country_code,
        "state": state[:40],
        "city": city[:40],
        "locality": "En vivo",
        "genre": genre[:25],
        "stream_url": stream_url,
        "logo_url": logo,
        "description": f"Emisora transmitiendo en vivo desde {city}, {country_name}.",
        "bitrate": f"{raw.get('bitrate', 128)} kbps",
        "frequency": freq,
        "band": band
    }

# 1. AMERICA: Use the existing 159 high-quality stations
with open("backend/data/continents/america.json", "r", encoding="utf-8") as f:
    america_stations = json.load(f)
for s in america_stations:
    s["continent"] = "América"

# 2. SEED TEMPLATES FOR OTHER CONTINENTS
EUROPA_COUNTRIES = [
    ("Spain", "España", "ES", "Madrid", "Madrid"),
    ("United Kingdom", "Reino Unido", "GB", "Inglaterra", "Londres"),
    ("France", "Francia", "FR", "Île-de-France", "París"),
    ("Germany", "Alemania", "DE", "Baviera", "Múnich"),
    ("Italy", "Italia", "IT", "Lacio", "Roma"),
    ("Switzerland", "Suiza", "CH", "Berna", "Berna"),
    ("Portugal", "Portugal", "PT", "Lisboa", "Lisboa"),
    ("Netherlands", "Países Bajos", "NL", "Holanda del Norte", "Ámsterdam"),
    ("Belgium", "Bélgica", "BE", "Bruselas", "Bruselas"),
    ("Austria", "Austria", "AT", "Viena", "Viena"),
    ("Sweden", "Suecia", "SE", "Estocolmo", "Estocolmo"),
    ("Norway", "Noruega", "NO", "Oslo", "Oslo"),
    ("Denmark", "Dinamarca", "DK", "Copenhague", "Copenhague"),
    ("Finland", "Finlandia", "FI", "Helsinki", "Helsinki"),
    ("Ireland", "Irlanda", "IE", "Leinster", "Dublín"),
    ("Greece", "Grecia", "GR", "Ática", "Atenas"),
    ("Poland", "Polonia", "PL", "Mazovia", "Varsovia"),
    ("Czech Republic", "República Checa", "CZ", "Praga", "Praga")
]

ASIA_COUNTRIES = [
    ("Japan", "Japón", "JP", "Kantō", "Tokio"),
    ("South Korea", "Corea del Sur", "KR", "Gyeonggi", "Seúl"),
    ("China", "China", "CN", "Beijing", "Pekín"),
    ("Hong Kong", "Hong Kong", "HK", "Hong Kong Island", "Hong Kong"),
    ("Taiwan", "Taiwán", "TW", "Taipei", "Taipéi"),
    ("India", "India", "IN", "Maharashtra", "Bombay"),
    ("Indonesia", "Indonesia", "ID", "Java Occidental", "Yakarta"),
    ("Philippines", "Filipinas", "PH", "Gran Manila", "Manila"),
    ("Thailand", "Tailandia", "TH", "Bangkok", "Bangkok"),
    ("Vietnam", "Vietnam", "VN", "Hanoi", "Hanói"),
    ("Singapore", "Singapur", "SG", "Singapur", "Singapur"),
    ("Malaysia", "Malasia", "MY", "Kuala Lumpur", "Kuala Lumpur"),
    ("Turkey", "Turquía", "TR", "Mármara", "Estambul"),
    ("United Arab Emirates", "Emiratos Árabes Unidos", "AE", "Dubái", "Dubái"),
    ("Israel", "Israel", "IL", "Tel Aviv", "Tel Aviv"),
    ("Saudi Arabia", "Arabia Saudita", "SA", "Riad", "Riad")
]

AFRICA_COUNTRIES = [
    ("South Africa", "Sudáfrica", "ZA", "Gauteng", "Johannesburgo"),
    ("Nigeria", "Nigeria", "NG", "Lagos", "Lagos"),
    ("Egypt", "Egipto", "EG", "El Cairo", "El Cairo"),
    ("Kenya", "Kenia", "KE", "Nairobi", "Nairobi"),
    ("Morocco", "Marruecos", "MA", "Casablanca-Settat", "Casablanca"),
    ("Ghana", "Ghana", "GH", "Gran Acra", "Acra"),
    ("Senegal", "Senegal", "SN", "Dakar", "Dakar"),
    ("Ivory Coast", "Costa de Marfil", "CI", "Abiyán", "Abiyán"),
    ("Algeria", "Argelia", "DZ", "Argel", "Argel"),
    ("Tunisia", "Túnez", "TN", "Túnez", "Túnez")
]

OCEANIA_COUNTRIES = [
    ("Australia", "Australia", "AU", "Nueva Gales del Sur", "Sídney"),
    ("New Zealand", "Nueva Zelanda", "NZ", "Auckland", "Auckland"),
    ("Fiji", "Fiyi", "FJ", "Central", "Suva"),
    ("Papua New Guinea", "Papúa Nueva Guinea", "PG", "Distrito Capital", "Puerto Moresby")
]

def harvest_continent(continent_name: str, countries_spec: list) -> list[dict]:
    stations = []
    seen_urls = set()
    print(f"\n--- Recolectando estaciones para {continent_name} ---")
    for q_country, c_name, c_code, def_state, def_city in countries_spec:
        print(f"Consultando {c_name} ({q_country})...")
        raw_list = query_rb(q_country, country_code=c_code, limit=10)
        added_for_country = 0
        for raw in raw_list:
            st = clean_station(raw, continent_name, c_name, c_code, def_state, def_city)
            if st and st["stream_url"] not in seen_urls:
                seen_urls.add(st["stream_url"])
                stations.append(st)
                added_for_country += 1
                if added_for_country >= 6:
                    break
        print(f"  -> {added_for_country} emisoras agregadas para {c_name}")
    return stations

# 3. BUILD CONTINENT CATALOGS
europa_stations = harvest_continent("Europa", EUROPA_COUNTRIES)
asia_stations = harvest_continent("Asia", ASIA_COUNTRIES)
africa_stations = harvest_continent("África", AFRICA_COUNTRIES)
oceania_stations = harvest_continent("Oceanía", OCEANIA_COUNTRIES)

# Ensure fallback stations if API returned fewer than desired
EUROPA_FALLBACKS = [
    {
        "id": "cadena-ser-es", "name": "Cadena SER Madrid 105.4 FM", "continent": "Europa",
        "country": "España", "country_code": "ES", "state": "Comunidad de Madrid", "city": "Madrid",
        "locality": "Gran Vía", "genre": "Noticias & Debate", "stream_url": "https://playerservices.streamtheworld.com/api/livestream-redirect/CADENASER.mp3",
        "logo_url": "https://cadenaser.com/favicon.ico", "description": "Emisora generalista líder de España.",
        "bitrate": "128 kbps", "frequency": 105.4, "band": "FM"
    },
    {
        "id": "los40-espana", "name": "Los 40 España 93.9 FM", "continent": "Europa",
        "country": "España", "country_code": "ES", "state": "Comunidad de Madrid", "city": "Madrid",
        "locality": "Centro", "genre": "Pop & Éxitos", "stream_url": "https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40.mp3",
        "logo_url": "https://los40.com/favicon.ico", "description": "Los éxitos musicales número uno en España.",
        "bitrate": "128 kbps", "frequency": 93.9, "band": "FM"
    },
    {
        "id": "radio-swiss-pop", "name": "Radio Swiss Pop 103.8 FM", "continent": "Europa",
        "country": "Suiza", "country_code": "CH", "state": "Berna", "city": "Berna",
        "locality": "SRG SSR", "genre": "Pop Clásico", "stream_url": "http://stream.srg-ssr.ch/m/rsp/mp3_128",
        "logo_url": "https://www.radioswisspop.ch/favicon.ico", "description": "Música pop continua de Suiza.",
        "bitrate": "128 kbps", "frequency": 103.8, "band": "FM"
    },
    {
        "id": "bbc-world-service", "name": "BBC World Service 100.2 FM", "continent": "Europa",
        "country": "Reino Unido", "country_code": "GB", "state": "Inglaterra", "city": "Londres",
        "locality": "Broadcasting House", "genre": "Noticias Globales", "stream_url": "https://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
        "logo_url": "https://www.bbc.co.uk/favicon.ico", "description": "El servicio mundial de la BBC desde Londres.",
        "bitrate": "128 kbps", "frequency": 100.2, "band": "FM"
    },
    {
        "id": "france-inter-paris", "name": "France Inter 87.8 FM", "continent": "Europa",
        "country": "Francia", "country_code": "FR", "state": "Île-de-France", "city": "París",
        "locality": "Maison de la Radio", "genre": "Cultura & Noticias", "stream_url": "https://stream.radiofrance.fr/franceinter/franceinter_hifi.m3u8",
        "logo_url": "https://www.radiofrance.fr/favicon.ico", "description": "Radio pública nacional francesa.",
        "bitrate": "128 kbps", "frequency": 87.8, "band": "FM"
    }
]

for fb in EUROPA_FALLBACKS:
    if not any(s["stream_url"] == fb["stream_url"] for s in europa_stations):
        europa_stations.append(fb)

# Write all continent files
os.makedirs("backend/data/continents", exist_ok=True)

with open("backend/data/continents/america.json", "w", encoding="utf-8") as f:
    json.dump(america_stations, f, indent=2, ensure_ascii=False)

with open("backend/data/continents/europa.json", "w", encoding="utf-8") as f:
    json.dump(europa_stations, f, indent=2, ensure_ascii=False)

with open("backend/data/continents/asia.json", "w", encoding="utf-8") as f:
    json.dump(asia_stations, f, indent=2, ensure_ascii=False)

with open("backend/data/continents/africa.json", "w", encoding="utf-8") as f:
    json.dump(africa_stations, f, indent=2, ensure_ascii=False)

with open("backend/data/continents/oceania.json", "w", encoding="utf-8") as f:
    json.dump(oceania_stations, f, indent=2, ensure_ascii=False)

# Aggregate all stations into single master seed and frontend copy
all_global_stations = america_stations + europa_stations + asia_stations + africa_stations + oceania_stations
# Deduplicate by stream_url
unique_global = []
seen = set()
for st in all_global_stations:
    url = st["stream_url"]
    if url not in seen:
        seen.add(url)
        unique_global.append(st)

with open("backend/data/seed_stations.json", "w", encoding="utf-8") as f:
    json.dump(unique_global, f, indent=2, ensure_ascii=False)

with open("frontend/wwwroot/sample-data/stations.json", "w", encoding="utf-8") as f:
    json.dump(unique_global, f, indent=2, ensure_ascii=False)

print("\n=======================================================")
print(f"Catálogo Mundial Generado con Éxito:")
print(f"  - América: {len(america_stations)} emisoras")
print(f"  - Europa:  {len(europa_stations)} emisoras")
print(f"  - Asia:    {len(asia_stations)} emisoras")
print(f"  - África:  {len(africa_stations)} emisoras")
print(f"  - Oceanía: {len(oceania_stations)} emisoras")
print(f"Total estaciones únicas globales: {len(unique_global)}")
print(f"Archivos guardados en backend/data/continents/, backend/data/seed_stations.json y frontend/wwwroot/sample-data/stations.json")
print("=======================================================")

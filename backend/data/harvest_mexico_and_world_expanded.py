#!/usr/bin/env python3
"""
Radio Mundial - Expanded Harvester for Mexico & Worldwide Stations
Author: Hugo Francisco Luis Inclan (c) 2026
"""

import concurrent.futures
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
import unicodedata

# Import helper functions from global_harvester
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from global_harvester import (
    SSL_CTX, HEADERS, MIRRORS, GLOBAL_COUNTRIES,
    MEXICO_STATES, NORM_MEXICO_STATES, KNOWN_MEXICO_MUNICIPALITIES,
    normalize_text, resolve_mexico_geography, clean_station
)

def fetch_json(url, timeout=12):
    for m in MIRRORS:
        try:
            full_url = url.replace("https://de1.api.radio-browser.info", m)
            req = urllib.request.Request(full_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            continue
    return []

def main():
    print("=== Iniciando Cosecha de Expansión México & Mundo (Radio Mundial) ===")
    
    # 1. Cargar catálogo actual existente
    existing_path = "frontend/wwwroot/sample-data/stations.json"
    existing_stations = []
    if os.path.exists(existing_path):
        with open(existing_path, "r", encoding="utf-8") as f:
            existing_stations = json.load(f)
    print(f"Estaciones iniciales en catálogo: {len(existing_stations)}")
    
    seen_urls = set()
    master_stations = []
    
    for st in existing_stations:
        u = (st.get("stream_url") or "").strip()
        if u and u.lower() not in seen_urls:
            seen_urls.add(u.lower())
            master_stations.append(st)
            
    print(f"Estaciones base únicas: {len(master_stations)}")
    initial_mx = sum(1 for s in master_stations if s.get("country") in ("México", "Mexico") or s.get("country_code") == "MX")
    print(f"Estaciones base de México: {initial_mx}")
    
    new_stations = []
    
    # 2. Cosechar intensivamente MÉXICO
    print("\n--- Cosechando Emisoras de MÉXICO ---")
    mx_queries = [
        "https://de1.api.radio-browser.info/json/stations/search?countrycode=MX&limit=5000",
        "https://de1.api.radio-browser.info/json/stations/search?country=Mexico&limit=5000",
        "https://de1.api.radio-browser.info/json/stations/bycountry/Mexico?limit=5000"
    ]
    
    for st_name in MEXICO_STATES:
        q = urllib.parse.quote(st_name)
        mx_queries.append(f"https://de1.api.radio-browser.info/json/stations/search?state={q}&countrycode=MX&limit=500")
        mx_queries.append(f"https://de1.api.radio-browser.info/json/stations/search?name={q}&countrycode=MX&limit=500")
        
    mexican_tags = [
        "mexico", "regional mexicano", "cumbia", "norteño", "banda", "ranchera",
        "mariachi", "grupera", "corridos", "boleros", "trova", "mexicana",
        "guadalajara", "monterrey", "puebla", "tijuana", "oaxaca", "chiapas",
        "veracruz", "merida", "queretaro", "leon", "toluca", "chihuahua",
        "cancun", "acapulco", "morelia", "hermosillo", "culiacan", "aguascalientes",
        "san luis potosi", "torreon", "saltillo", "durango", "zacatecas", "pachuca"
    ]
    for tag in mexican_tags:
        q = urllib.parse.quote(tag)
        mx_queries.append(f"https://de1.api.radio-browser.info/json/stations/bytag/{q}?limit=500")
        
    print(f"Total consultas para México: {len(mx_queries)}")
    
    def process_mx_query(q_url):
        raws = fetch_json(q_url)
        results = []
        for r in raws:
            c_code = (r.get("countrycode") or "").upper()
            c_name = r.get("country") or ""
            # Si es de México o tag mexicano
            is_mx = c_code == "MX" or "mexico" in c_name.lower() or "méxico" in c_name.lower()
            if not is_mx:
                # Comprobar tags o nombre
                comb = f"{r.get('name', '')} {r.get('tags', '')}".lower()
                if any(mt in comb for mt in ["regional mexicano", "mariachi", "norteño", "banda sinaloense", "ranchera mexicana"]):
                    is_mx = True
            if is_mx:
                st = clean_station(r, "América", "México", "MX", "Ciudad de México", "Ciudad de México")
                if st:
                    results.append(st)
        return results

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        fut_to_url = {executor.submit(process_mx_query, q): q for q in mx_queries}
        for fut in concurrent.futures.as_completed(fut_to_url):
            try:
                res = fut.result()
                for st in res:
                    u = st["stream_url"].strip()
                    if u.lower() not in seen_urls:
                        seen_urls.add(u.lower())
                        new_stations.append(st)
            except Exception:
                pass
                
    added_mx = sum(1 for s in new_stations if s.get("country") in ("México", "Mexico") or s.get("country_code") == "MX")
    print(f"Nuevas estaciones de México agregadas: +{added_mx}")
    
    # 3. Cosechar a nivel MUNDIAL (Topvotes, Topclicks y principales países)
    print("\n--- Cosechando Emisoras del RESTO DEL MUNDO ---")
    world_queries = [
        "https://de1.api.radio-browser.info/json/stations/topvote/3000",
        "https://de1.api.radio-browser.info/json/stations/topclick/3000",
        "https://de1.api.radio-browser.info/json/stations/lastclick/2000"
    ]
    
    # Países clave mundiales con límites ampliados
    key_countries = [
        ("US", "Estados Unidos", "América", "Nueva York", "Nueva York"),
        ("ES", "España", "Europa", "Madrid", "Madrid"),
        ("AR", "Argentina", "América", "Buenos Aires", "Buenos Aires"),
        ("CO", "Colombia", "América", "Bogotá", "Bogotá"),
        ("BR", "Brasil", "América", "São Paulo", "São Paulo"),
        ("CL", "Chile", "América", "Santiago", "Santiago"),
        ("PE", "Perú", "América", "Lima", "Lima"),
        ("VE", "Venezuela", "América", "Caracas", "Caracas"),
        ("EC", "Ecuador", "América", "Quito", "Quito"),
        ("GT", "Guatemala", "América", "Ciudad de Guatemala", "Ciudad de Guatemala"),
        ("CR", "Costa Rica", "América", "San José", "San José"),
        ("PA", "Panamá", "América", "Ciudad de Panamá", "Ciudad de Panamá"),
        ("DO", "República Dominicana", "América", "Santo Domingo", "Santo Domingo"),
        ("CU", "Cuba", "América", "La Habana", "La Habana"),
        ("GB", "Reino Unido", "Europa", "Londres", "Londres"),
        ("FR", "Francia", "Europa", "París", "París"),
        ("DE", "Alemania", "Europa", "Berlín", "Berlín"),
        ("IT", "Italia", "Europa", "Roma", "Roma"),
        ("JP", "Japón", "Asia", "Tokio", "Tokio"),
        ("KR", "Corea del Sur", "Asia", "Seúl", "Seúl"),
        ("AU", "Australia", "Oceanía", "Sídney", "Sídney"),
        ("NZ", "Nueva Zelanda", "Oceanía", "Auckland", "Auckland"),
        ("CA", "Canadá", "América", "Ontario", "Toronto"),
        ("IE", "Irlanda", "Europa", "Dublín", "Dublín"),
        ("PT", "Portugal", "Europa", "Lisboa", "Lisboa"),
        ("NL", "Países Bajos", "Europa", "Ámsterdam", "Ámsterdam"),
        ("BE", "Bélgica", "Europa", "Bruselas", "Bruselas"),
        ("CH", "Suiza", "Europa", "Zúrich", "Zúrich"),
        ("AT", "Austria", "Europa", "Viena", "Viena"),
        ("SE", "Suecia", "Europa", "Estocolmo", "Estocolmo"),
        ("NO", "Noruega", "Europa", "Oslo", "Oslo"),
        ("DK", "Dinamarca", "Europa", "Copenhague", "Copenhague"),
        ("FI", "Finlandia", "Europa", "Helsinki", "Helsinki"),
        ("PL", "Polonia", "Europa", "Varsovia", "Varsovia"),
        ("RU", "Rusia", "Europa", "Moscú", "Moscú"),
        ("TR", "Turquía", "Asia", "Estambul", "Estambul"),
        ("GR", "Grecia", "Europa", "Atenas", "Atenas"),
        ("IN", "India", "Asia", "Nueva Delhi", "Nueva Delhi"),
        ("ZA", "Sudáfrica", "África", "Johannesburgo", "Johannesburgo"),
        ("EG", "Egipto", "África", "El Cairo", "El Cairo"),
        ("MA", "Marruecos", "África", "Casablanca", "Casablanca")
    ]
    
    for code, c_name, cont, st, city in key_countries:
        world_queries.append(f"https://de1.api.radio-browser.info/json/stations/search?countrycode={code}&limit=500")
        
    print(f"Total consultas para el mundo: {len(world_queries)}")
    
    def process_world_query(q_url):
        raws = fetch_json(q_url)
        results = []
        for r in raws:
            code = (r.get("countrycode") or "").upper()
            c_name = r.get("country") or "Internacional"
            cont = "América"
            def_st = "Principal"
            def_city = "Principal"
            
            if code in GLOBAL_COUNTRIES:
                c_name, cont, def_st, def_city, _ = GLOBAL_COUNTRIES[code]
            st = clean_station(r, cont, c_name, code, def_st, def_city)
            if st:
                results.append(st)
        return results

    with concurrent.futures.ThreadPoolExecutor(max_workers=14) as executor:
        fut_to_url = {executor.submit(process_world_query, q): q for q in world_queries}
        for fut in concurrent.futures.as_completed(fut_to_url):
            try:
                res = fut.result()
                for st in res:
                    u = st["stream_url"].strip()
                    if u.lower() not in seen_urls:
                        seen_urls.add(u.lower())
                        new_stations.append(st)
            except Exception:
                pass
                
    print(f"Total nuevas estaciones recolectadas: +{len(new_stations)}")
    
    # 4. Combinar y estructurar el catálogo final
    # Prioridad: Estaciones de México van al frente para que tengan máxima visibilidad
    all_combined = master_stations + new_stations
    
    # Separar México y el resto para ordenar
    mx_all = [s for s in all_combined if s.get("country") in ("México", "Mexico") or s.get("country_code") == "MX"]
    world_all = [s for s in all_combined if not (s.get("country") in ("México", "Mexico") or s.get("country_code") == "MX")]
    
    # Ordenar estaciones mexicanas por importancia/estado
    print(f"Total final de estaciones en México: {len(mx_all)}")
    print(f"Total final de estaciones en el Mundo: {len(world_all)}")
    
    final_master = mx_all + world_all
    print(f"Total final catálogo maestro: {len(final_master)}")
    
    # 5. Guardar archivos
    print("\nGuardando catálogo en frontend y backend...")
    with open("frontend/wwwroot/sample-data/stations.json", "w", encoding="utf-8") as f:
        json.dump(final_master, f, indent=2, ensure_ascii=False)
        
    with open("backend/data/seed_stations.json", "w", encoding="utf-8") as f:
        json.dump(final_master, f, indent=2, ensure_ascii=False)
        
    # Guardar particiones por continente
    continents_map = {"América": [], "Europa": [], "Asia": [], "África": [], "Oceanía": []}
    for s in final_master:
        c = s.get("continent", "América")
        if c not in continents_map:
            continents_map[c] = []
        continents_map[c].append(s)
        
    for c_name, fname in [
        ("América", "america.json"), ("Europa", "europa.json"),
        ("Asia", "asia.json"), ("África", "africa.json"), ("Oceanía", "oceania.json")
    ]:
        fpath = os.path.join("backend/data/continents", fname)
        if c_name in continents_map:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(continents_map[c_name], f, indent=2, ensure_ascii=False)
            print(f"  ✓ {c_name}: {len(continents_map[c_name])} emisoras -> {fpath}")

    print("=== ¡Cosecha y expansión completada con éxito! ===")

if __name__ == "__main__":
    main()

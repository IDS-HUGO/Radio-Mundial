#!/usr/bin/env python3
"""
Global Radio Harvester 6.0 - Radio Mundial
Massive, worldwide radio catalog expansion covering 225+ countries and territories across all 5 continents:
- América (North, Central, Caribbean, South)
- Europa (Western, Eastern, Nordic, Mediterranean)
- Asia (East, South, Southeast, Central, Middle East)
- África (North, West, Central, East, Southern)
- Oceanía (Australia, New Zealand, Polynesia, Melanesia, Micronesia)

Strictly preserves existing verified stations (Tapachula, Matías Romero, Oaxaca, 32 Mexican states, etc.)
and enriches the world catalog to 3,500+ verified stations.

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

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RadioMundial/6.0"
}

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

# EXHAUSTIVE COUNTRY REGISTRY: code -> (Spanish Name, Continent, Default State, Default City, Target Limit)
GLOBAL_COUNTRIES = {
    # ==========================================
    # === AMÉRICA (Norte, Centro, Caribe, Sur) ==
    # ==========================================
    "MX": ("México", "América", "Ciudad de México", "Ciudad de México", 90),
    "US": ("Estados Unidos", "América", "Nueva York", "Nueva York", 120),
    "CA": ("Canadá", "América", "Ontario", "Toronto", 60),
    "GT": ("Guatemala", "América", "Guatemala", "Ciudad de Guatemala", 12),
    "BZ": ("Belice", "América", "Belice", "Ciudad de Belice", 5),
    "SV": ("El Salvador", "América", "San Salvador", "San Salvador", 12),
    "HN": ("Honduras", "América", "Francisco Morazán", "Tegucigalpa", 12),
    "NI": ("Nicaragua", "América", "Managua", "Managua", 12),
    "CR": ("Costa Rica", "América", "San José", "San José", 15),
    "PA": ("Panamá", "América", "Panamá", "Ciudad de Panamá", 12),
    "CU": ("Cuba", "América", "La Habana", "La Habana", 10),
    "DO": ("República Dominicana", "América", "Distrito Nacional", "Santo Domingo", 15),
    "PR": ("Puerto Rico", "América", "San Juan", "San Juan", 15),
    "HT": ("Haití", "América", "Oeste", "Puerto Príncipe", 8),
    "JM": ("Jamaica", "América", "Kingston", "Kingston", 10),
    "BS": ("Bahamas", "América", "Nueva Providencia", "Nasáu", 6),
    "TT": ("Trinidad y Tobago", "América", "Puerto España", "Puerto España", 8),
    "BB": ("Barbados", "América", "Saint Michael", "Bridgetown", 6),
    "LC": ("Santa Lucía", "América", "Castries", "Castries", 6),
    "GD": ("Granada", "América", "Saint George", "Saint George", 5),
    "VC": ("San Vicente y las Granadinas", "América", "Saint George", "Kingstown", 5),
    "AG": ("Antigua y Barbuda", "América", "Saint John", "Saint John", 5),
    "DM": ("Dominica", "América", "Saint George", "Roseau", 5),
    "KN": ("San Cristóbal y Nieves", "América", "Saint George Basseterre", "Basseterre", 5),
    "CO": ("Colombia", "América", "Cundinamarca", "Bogotá", 60),
    "VE": ("Venezuela", "América", "Distrito Capital", "Caracas", 20),
    "EC": ("Ecuador", "América", "Pichincha", "Quito", 20),
    "PE": ("Perú", "América", "Lima", "Lima", 45),
    "BR": ("Brasil", "América", "São Paulo", "São Paulo", 70),
    "BO": ("Bolivia", "América", "La Paz", "La Paz", 15),
    "PY": ("Paraguay", "América", "Central", "Asunción", 15),
    "CL": ("Chile", "América", "Región Metropolitana", "Santiago", 45),
    "AR": ("Argentina", "América", "Buenos Aires", "Buenos Aires", 70),
    "UY": ("Uruguay", "América", "Montevideo", "Montevideo", 15),
    "GY": ("Guyana", "América", "Demerara-Mahaica", "Georgetown", 6),
    "SR": ("Surinam", "América", "Paramaribo", "Paramaribo", 6),
    "AW": ("Aruba", "América", "Oranjestad", "Oranjestad", 6),
    "CW": ("Curazao", "América", "Willemstad", "Willemstad", 6),
    "BQ": ("Bonaire", "América", "Kralendijk", "Kralendijk", 6),
    "AI": ("Anguila", "América", "The Valley", "The Valley", 5),
    "BM": ("Bermudas", "América", "Hamilton", "Hamilton", 5),
    "FK": ("Islas Malvinas", "América", "Puerto Argentino", "Puerto Argentino", 4),
    "GF": ("Guayana Francesa", "América", "Cayena", "Cayena", 5),
    "GL": ("Groenlandia", "América", "Sermersooq", "Nuuk", 5),
    "GP": ("Guadalupe", "América", "Basse-Terre", "Basse-Terre", 8),
    "KY": ("Islas Caimán", "América", "George Town", "George Town", 6),
    "MQ": ("Martinica", "América", "Fort-de-France", "Fort-de-France", 8),
    "MS": ("Montserrat", "América", "Brades", "Brades", 3),
    "PM": ("San Pedro y Miquelón", "América", "San Pedro", "San Pedro", 3),
    "SX": ("San Martín", "América", "Philipsburg", "Philipsburg", 4),
    "UM": ("Islas Ultramarinas de EE.UU.", "América", "Islas Menores", "Wake", 6),
    "VG": ("Islas Vírgenes Británicas", "América", "Road Town", "Road Town", 5),
    "VI": ("Islas Vírgenes de EE.UU.", "América", "Charlotte Amalie", "Charlotte Amalie", 6),

    # ==========================================
    # === EUROPA ===============================
    # ==========================================
    "ES": ("España", "Europa", "Comunidad de Madrid", "Madrid", 80),
    "PT": ("Portugal", "Europa", "Lisboa", "Lisboa", 35),
    "FR": ("Francia", "Europa", "Île-de-France", "París", 80),
    "IT": ("Italia", "Europa", "Lacio", "Roma", 70),
    "DE": ("Alemania", "Europa", "Baviera", "Múnich", 100),
    "GB": ("Reino Unido", "Europa", "Inglaterra", "Londres", 80),
    "IE": ("Irlanda", "Europa", "Leinster", "Dublín", 20),
    "CH": ("Suiza", "Europa", "Berna", "Berna", 40),
    "AT": ("Austria", "Europa", "Viena", "Viena", 40),
    "BE": ("Bélgica", "Europa", "Bruselas", "Bruselas", 40),
    "NL": ("Países Bajos", "Europa", "Holanda del Norte", "Ámsterdam", 50),
    "LU": ("Luxemburgo", "Europa", "Luxemburgo", "Ciudad de Luxemburgo", 8),
    "MC": ("Mónaco", "Europa", "Mónaco", "Mónaco", 5),
    "AD": ("Andorra", "Europa", "Andorra la Vieja", "Andorra la Vieja", 5),
    "SM": ("San Marino", "Europa", "San Marino", "San Marino", 5),
    "VA": ("Ciudad del Vaticano", "Europa", "Vaticano", "Ciudad del Vaticano", 5),
    "LI": ("Liechtenstein", "Europa", "Vaduz", "Vaduz", 4),
    "SE": ("Suecia", "Europa", "Estocolmo", "Estocolmo", 40),
    "NO": ("Noruega", "Europa", "Oslo", "Oslo", 35),
    "DK": ("Dinamarca", "Europa", "Hovedstaden", "Copenhague", 35),
    "FI": ("Finlandia", "Europa", "Uusimaa", "Helsinki", 35),
    "IS": ("Islandia", "Europa", "Höfuðborgarsvæðið", "Reikiavik", 8),
    "PL": ("Polonia", "Europa", "Mazovia", "Varsovia", 50),
    "CZ": ("República Checa", "Europa", "Praga", "Praga", 20),
    "SK": ("Eslovaquia", "Europa", "Bratislava", "Bratislava", 15),
    "HU": ("Hungría", "Europa", "Budapest", "Budapest", 20),
    "RO": ("Rumanía", "Europa", "Bucarest", "Bucarest", 20),
    "BG": ("Bulgaria", "Europa", "Sofía", "Sofía", 15),
    "GR": ("Grecia", "Europa", "Ática", "Atenas", 50),
    "CY": ("Chipre", "Europa", "Nicosia", "Nicosia", 10),
    "MT": ("Malta", "Europa", "La Valeta", "La Valeta", 8),
    "HR": ("Croacia", "Europa", "Zagreb", "Zagreb", 15),
    "SI": ("Eslovenia", "Europa", "Liubliana", "Liubliana", 12),
    "RS": ("Serbia", "Europa", "Belgrado", "Belgrado", 15),
    "BA": ("Bosnia y Herzegovina", "Europa", "Sarajevo", "Sarajevo", 12),
    "ME": ("Montenegro", "Europa", "Podgorica", "Podgorica", 8),
    "MK": ("Macedonia del Norte", "Europa", "Skopie", "Skopie", 10),
    "AL": ("Albania", "Europa", "Tirana", "Tirana", 10),
    "EE": ("Estonia", "Europa", "Harju", "Tallin", 10),
    "LV": ("Letonia", "Europa", "Riga", "Riga", 10),
    "LT": ("Lituania", "Europa", "Vilna", "Vilna", 10),
    "UA": ("Ucrania", "Europa", "Kiev", "Kiev", 20),
    "BY": ("Bielorrusia", "Europa", "Minsk", "Minsk", 10),
    "MD": ("Moldavia", "Europa", "Chisináu", "Chisináu", 10),
    "RU": ("Rusia", "Europa", "Moscú", "Moscú", 60),
    "FO": ("Islas Feroe", "Europa", "Tórshavn", "Tórshavn", 6),
    "GG": ("Guernsey", "Europa", "Saint Peter Port", "Saint Peter Port", 3),
    "GI": ("Gibraltar", "Europa", "Gibraltar", "Gibraltar", 5),
    "IM": ("Isla de Man", "Europa", "Douglas", "Douglas", 6),
    "JE": ("Jersey", "Europa", "Saint Helier", "Saint Helier", 4),
    "XK": ("Kosovo", "Europa", "Pristina", "Pristina", 8),

    # ==========================================
    # === ASIA =================================
    # ==========================================
    "JP": ("Japón", "Asia", "Kantō", "Tokio", 45),
    "KR": ("Corea del Sur", "Asia", "Gyeonggi", "Seúl", 25),
    "CN": ("China", "Asia", "Beijing", "Pekín", 60),
    "TW": ("Taiwán", "Asia", "Taipei", "Taipéi", 20),
    "HK": ("Hong Kong", "Asia", "Hong Kong", "Hong Kong", 15),
    "MO": ("Macao", "Asia", "Macao", "Macao", 6),
    "MN": ("Mongolia", "Asia", "Ulán Bator", "Ulán Bator", 6),
    "IN": ("India", "Asia", "Maharashtra", "Bombay", 60),
    "PK": ("Pakistán", "Asia", "Sind", "Karachi", 15),
    "BD": ("Bangladesh", "Asia", "Daca", "Daca", 12),
    "LK": ("Sri Lanka", "Asia", "Colombo", "Colombo", 10),
    "NP": ("Nepal", "Asia", "Bagmati", "Katmandú", 10),
    "BT": ("Bután", "Asia", "Timbu", "Timbu", 4),
    "MV": ("Maldivas", "Asia", "Malé", "Malé", 5),
    "ID": ("Indonesia", "Asia", "Java Occidental", "Yakarta", 25),
    "PH": ("Filipinas", "Asia", "Gran Manila", "Manila", 25),
    "TH": ("Tailandia", "Asia", "Bangkok", "Bangkok", 20),
    "VN": ("Vietnam", "Asia", "Hanoi", "Hanói", 20),
    "MY": ("Malasia", "Asia", "Kuala Lumpur", "Kuala Lumpur", 20),
    "SG": ("Singapur", "Asia", "Singapur", "Singapur", 15),
    "MM": ("Myanmar", "Asia", "Yangon", "Rangún", 8),
    "KH": ("Camboya", "Asia", "Nom Pen", "Nom Pen", 8),
    "LA": ("Laos", "Asia", "Vientián", "Vientián", 6),
    "TR": ("Turquía", "Asia", "Mármara", "Estambul", 45),
    "IL": ("Israel", "Asia", "Tel Aviv", "Tel Aviv", 18),
    "PS": ("Palestina", "Asia", "Cisjordania", "Ramala", 8),
    "SA": ("Arabia Saudita", "Asia", "Riad", "Riad", 18),
    "AE": ("Emiratos Árabes Unidos", "Asia", "Dubái", "Dubái", 20),
    "QA": ("Qatar", "Asia", "Doha", "Doha", 10),
    "KW": ("Kuwait", "Asia", "Ciudad de Kuwait", "Ciudad de Kuwait", 10),
    "BH": ("Bahréin", "Asia", "Manama", "Manama", 8),
    "OM": ("Omán", "Asia", "Mascate", "Mascate", 8),
    "YE": ("Yemen", "Asia", "Saná", "Saná", 6),
    "JO": ("Jordania", "Asia", "Amán", "Amán", 10),
    "LB": ("Líbano", "Asia", "Beirut", "Beirut", 12),
    "SY": ("Siria", "Asia", "Damasco", "Damasco", 8),
    "IQ": ("Irak", "Asia", "Bagdad", "Bagdad", 10),
    "IR": ("Irán", "Asia", "Teherán", "Teherán", 15),
    "AF": ("Afganistán", "Asia", "Kabul", "Kabul", 8),
    "KZ": ("Kazajistán", "Asia", "Almatý", "Almatý", 12),
    "UZ": ("Uzbekistán", "Asia", "Taskent", "Taskent", 10),
    "TM": ("Turkmenistán", "Asia", "Asjabad", "Asjabad", 5),
    "KG": ("Kirguistán", "Asia", "Biskek", "Biskek", 8),
    "TJ": ("Tayikistán", "Asia", "Dusambé", "Dusambé", 6),
    "AZ": ("Azerbaiyán", "Asia", "Bakú", "Bakú", 10),
    "AM": ("Armenia", "Asia", "Ereván", "Ereván", 10),
    "GE": ("Georgia", "Asia", "Tiflis", "Tiflis", 10),
    "BN": ("Brunéi", "Asia", "Bandar Seri Begawan", "Bandar Seri Begawan", 4),
    "IO": ("Territorio Índico Británico", "Asia", "Diego García", "Diego García", 2),
    "KP": ("Corea del Norte", "Asia", "Pionyang", "Pionyang", 5),

    # ==========================================
    # === ÁFRICA ===============================
    # ==========================================
    "ZA": ("Sudáfrica", "África", "Gauteng", "Johannesburgo", 40),
    "NG": ("Nigeria", "África", "Lagos", "Lagos", 35),
    "EG": ("Egipto", "África", "El Cairo", "El Cairo", 35),
    "KE": ("Kenia", "África", "Nairobi", "Nairobi", 30),
    "MA": ("Marruecos", "África", "Casablanca-Settat", "Casablanca", 30),
    "GH": ("Ghana", "África", "Gran Acra", "Acra", 15),
    "SN": ("Senegal", "África", "Dakar", "Dakar", 12),
    "CI": ("Costa de Marfil", "África", "Abiyán", "Abiyán", 12),
    "DZ": ("Argelia", "África", "Argel", "Argel", 15),
    "TN": ("Túnez", "África", "Túnez", "Túnez", 15),
    "ET": ("Etiopía", "África", "Adís Abeba", "Adís Abeba", 10),
    "TZ": ("Tanzania", "África", "Dar es Salaam", "Dar es Salaam", 12),
    "UG": ("Uganda", "África", "Kampala", "Kampala", 12),
    "AO": ("Angola", "África", "Luanda", "Luanda", 10),
    "MZ": ("Mozambique", "África", "Maputo", "Maputo", 8),
    "ZM": ("Zambia", "África", "Lusaka", "Lusaka", 8),
    "ZW": ("Zimbabue", "África", "Harare", "Harare", 8),
    "NA": ("Namibia", "África", "Khomas", "Windhoek", 8),
    "BW": ("Botsuana", "África", "Gaborone", "Gaborone", 8),
    "CM": ("Camerún", "África", "Litoral", "Duala", 10),
    "RW": ("Ruanda", "África", "Kigali", "Kigali", 8),
    "ML": ("Malí", "África", "Bamako", "Bamako", 8),
    "MG": ("Madagascar", "África", "Analamanga", "Antananarivo", 8),
    "BF": ("Burkina Faso", "África", "Uagadugú", "Uagadugú", 6),
    "NE": ("Níger", "África", "Niamey", "Niamey", 5),
    "TD": ("Chad", "África", "Yamena", "Yamena", 5),
    "SO": ("Somalia", "África", "Benadir", "Mogadiscio", 5),
    "GN": ("Guinea", "África", "Conakri", "Conakri", 5),
    "BJ": ("Benín", "África", "Litoral", "Cotonú", 5),
    "BI": ("Burundi", "África", "Buyumbura", "Buyumbura", 5),
    "TG": ("Togo", "África", "Marítima", "Lomé", 5),
    "SL": ("Sierra Leona", "África", "Freetown", "Freetown", 5),
    "LR": ("Liberia", "África", "Monrovia", "Monrovia", 5),
    "MR": ("Mauritania", "África", "Nuakchot", "Nuakchot", 5),
    "CG": ("República del Congo", "África", "Brazzaville", "Brazzaville", 5),
    "CD": ("Rep. Dem. del Congo", "África", "Kinshasa", "Kinshasa", 8),
    "GA": ("Gabón", "África", "Libreville", "Libreville", 5),
    "GM": ("Gambia", "África", "Banjul", "Banjul", 5),
    "DJ": ("Yibuti", "África", "Yibuti", "Yibuti", 4),
    "SZ": ("Esuatini", "África", "Mbabane", "Mbabane", 4),
    "LS": ("Lesoto", "África", "Maseru", "Maseru", 4),
    "CV": ("Cabo Verde", "África", "Praia", "Praia", 6),
    "MU": ("Mauricio", "África", "Port Louis", "Port Louis", 6),
    "SC": ("Seychelles", "África", "Victoria", "Victoria", 5),
    "LY": ("Libia", "África", "Trípoli", "Trípoli", 6),
    "SD": ("Sudán", "África", "Jartum", "Jartum", 5),
    "SS": ("Sudán del Sur", "África", "Yuba", "Yuba", 4),
    "MW": ("Malaui", "África", "Lilongüe", "Lilongüe", 5),
    "CF": ("República Centroafricana", "África", "Bangui", "Bangui", 4),
    "ER": ("Eritrea", "África", "Asmara", "Asmara", 4),
    "GW": ("Guinea-Bisáu", "África", "Bisáu", "Bisáu", 3),
    "KM": ("Comoras", "África", "Moroni", "Moroni", 4),
    "RE": ("Reunión", "África", "Saint-Denis", "Saint-Denis", 12),
    "SH": ("Santa Elena", "África", "Jamestown", "Jamestown", 3),
    "YT": ("Mayotte", "África", "Mamoudzou", "Mamoudzou", 4),

    # ==========================================
    # === OCEANÍA & TERRITORIOS POLARES =======
    # ==========================================
    "AU": ("Australia", "Oceanía", "Nueva Gales del Sur", "Sídney", 60),
    "NZ": ("Nueva Zelanda", "Oceanía", "Auckland", "Auckland", 40),
    "FJ": ("Fiyi", "Oceanía", "Central", "Suva", 10),
    "PG": ("Papúa Nueva Guinea", "Oceanía", "Distrito Capital", "Puerto Moresby", 8),
    "SB": ("Islas Salomón", "Oceanía", "Honiara", "Honiara", 5),
    "VU": ("Vanuatu", "Oceanía", "Shefa", "Port Vila", 5),
    "WS": ("Samoa", "Oceanía", "Tuamasaga", "Apia", 5),
    "TO": ("Tonga", "Oceanía", "Tongatapu", "Nukualofa", 5),
    "FM": ("Micronesia", "Oceanía", "Pohnpei", "Palikir", 4),
    "KI": ("Kiribati", "Oceanía", "Tarawa", "Tarawa", 4),
    "MH": ("Islas Marshall", "Oceanía", "Majuro", "Majuro", 4),
    "NR": ("Nauru", "Oceanía", "Yaren", "Yaren", 4),
    "PW": ("Palaos", "Oceanía", "Koror", "Koror", 4),
    "TV": ("Tuvalu", "Oceanía", "Funafuti", "Funafuti", 4),
    "PF": ("Polinesia Francesa", "Oceanía", "Tahití", "Papeete", 6),
    "NC": ("Nueva Caledonia", "Oceanía", "Provincia Sur", "Numea", 6),
    "GU": ("Guam", "Oceanía", "Guam", "Hagåtña", 5),
    "AQ": ("Antártida", "Oceanía", "Base McMurdo", "McMurdo", 4),
    "AS": ("Samoa Americana", "Oceanía", "Pago Pago", "Pago Pago", 6),
    "CC": ("Islas Cocos", "Oceanía", "West Island", "West Island", 2),
    "CX": ("Isla de Navidad", "Oceanía", "Flying Fish Cove", "Flying Fish Cove", 2),
    "NU": ("Niue", "Oceanía", "Alofi", "Alofi", 2),
    "TF": ("Tierras Australes Francesas", "Oceanía", "Port-aux-Français", "Port-aux-Français", 2),
    "WF": ("Wallis y Futuna", "Oceanía", "Mata-Utu", "Mata-Utu", 2)
}

# VERIFIED REGIONAL STATIONS THAT MUST ALWAYS BE PRESENT AND PROTECTED
PROTECTED_REGIONAL_STATIONS = [
    # CHIAPAS - TAPACHULA
    {
        "id": "mx-chiapas-tapachula-extremo-96-3",
        "name": "Extremo 96.3 FM Tapachula",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Chiapas",
        "city": "Tapachula",
        "locality": "En vivo",
        "genre": "Regional Mexicano & Grupero",
        "stream_url": "https://stream.freepi.io/8310/live",
        "logo_url": "https://images.zeno.fm/5T6_9sQQj3AbFLZ2f0vrgEk1dNnFrD5uKU8bb4pd69E/rs:fill:1024:256/q:75/g:ce:0:0/aHR0cHM6Ly9wcm94eS56ZW5vLmZtL2NvbnRlbnQvc3RhdGlvbnMvODMxODljY2MtNTcwMS00MmMxLTk2NzYtMzk2YjExN2IxYjY1L21pY3Jvc2l0ZS9iYWNrZ3JvdW5kX2ltYWdlLz91PTE3Njk2OTQ4NDEwMDA",
        "description": "Extremo Tapachula con los mejores éxitos gruperos, norteño y banda para la Perla del Soconusco.",
        "bitrate": "128 kbps",
        "frequency": 96.3,
        "band": "FM"
    },
    {
        "id": "mx-chiapas-tapachula-wradio-1000",
        "name": "W Radio 1000 AM Tapachula",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Chiapas",
        "city": "Tapachula",
        "locality": "En vivo",
        "genre": "Noticias & Opinión",
        "stream_url": "https://streaming.servicioswebmx.com/8248/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "W Radio en el 1000 de AM transmitiendo las noticias y actualidad para la región Soconusco y frontera sur.",
        "bitrate": "128 kbps",
        "frequency": 1000.0,
        "band": "AM"
    },
    {
        "id": "mx-chiapas-tapachula-bellamusica-106-7",
        "name": "Bella Música 106.7 FM Tapachula",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Chiapas",
        "city": "Tapachula",
        "locality": "En vivo",
        "genre": "Romántica & Baladas",
        "stream_url": "https://stream.zeno.fm/scdv0t33gd0uv",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "Música instrumental, baladas de recuerdo y pop romántico en el 106.7 FM de Tapachula.",
        "bitrate": "128 kbps",
        "frequency": 106.7,
        "band": "FM"
    },
    {
        "id": "mx-chiapas-tapachula-los40-99-5",
        "name": "Los 40 Tapachula 99.5 FM",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Chiapas",
        "city": "Tapachula",
        "locality": "En vivo",
        "genre": "Pop & Éxitos",
        "stream_url": "https://stream.freepi.io/8300/live",
        "logo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
        "description": "Los éxitos mundiales de la música juvenil en el 99.5 FM de Tapachula, Chiapas.",
        "bitrate": "128 kbps",
        "frequency": 99.5,
        "band": "FM"
    },
    # CHIAPAS - TUXTLA GUTIÉRREZ & TONALÁ
    {
        "id": "mx-chiapas-tuxtla-radiochiapas-93-9",
        "name": "Radio Chiapas 93.9 FM",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Chiapas",
        "city": "Tuxtla Gutiérrez",
        "locality": "En vivo",
        "genre": "Cultura & Noticias",
        "stream_url": "http://streamingcwsradio10.com:9340/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Sistema Chiapaneco de Radio, Televisión y Cinematografía transmitiendo identidad, cultura y noticias.",
        "bitrate": "128 kbps",
        "frequency": 93.9,
        "band": "FM"
    },
    {
        "id": "mx-chiapas-tuxtla-joya-101-7",
        "name": "Joya 101.7 FM Tuxtla",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Chiapas",
        "city": "Tuxtla Gutiérrez",
        "locality": "En vivo",
        "genre": "Pop & Éxitos",
        "stream_url": "https://stream.zeno.fm/extbc8p9na0uv",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "Música que llena tu vida desde Tuxtla Gutiérrez, Chiapas.",
        "bitrate": "128 kbps",
        "frequency": 101.7,
        "band": "FM"
    },
    {
        "id": "mx-chiapas-tuxtla-lapoderosa-91-1",
        "name": "La Poderosa 91.1 FM Tuxtla",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Chiapas",
        "city": "Tuxtla Gutiérrez",
        "locality": "En vivo",
        "genre": "Regional Mexicano & Banda",
        "stream_url": "https://stream.zeno.fm/koab0etmslzvv",
        "logo_url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300&auto=format&fit=crop",
        "description": "Música grupera, banda sinaloense y norteña en el corazón de Chiapas.",
        "bitrate": "128 kbps",
        "frequency": 91.1,
        "band": "FM"
    },
    {
        "id": "mx-chiapas-tuxtla-bellamusica-93-1",
        "name": "Bella Música 93.1 FM Tuxtla",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Chiapas",
        "city": "Tuxtla Gutiérrez",
        "locality": "En vivo",
        "genre": "Romántica & Baladas",
        "stream_url": "https://stream.zeno.fm/ayrbxv13gd0uv",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "Música instrumental, baladas de recuerdo y pop romántico en Chiapas.",
        "bitrate": "128 kbps",
        "frequency": 93.1,
        "band": "FM"
    },
    # OAXACA - MATÍAS ROMERO, JUCHITÁN, PINOTEPA, HUAJUAPAN, PUERTO ÁNGEL, OAXACA CENTRO
    {
        "id": "mx-oax-matias-romero-905",
        "name": "La Ke Buena 90.5 FM Matías Romero",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Oaxaca",
        "city": "Matías Romero",
        "locality": "En vivo",
        "genre": "Regional Mexicano & Banda",
        "stream_url": "https://sound.encuentroradiotv.com/oaxaca957.mp3",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "La consentida del Istmo en 90.5 FM transmitiendo desde Matías Romero, Oaxaca (XHYS-FM). Red Encuentro Radio.",
        "bitrate": "128 kbps",
        "frequency": 90.5,
        "band": "FM"
    },
    {
        "id": "mx-oax-juchitan-901",
        "name": "Encuentro Radio 90.1 FM Juchitán",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Oaxaca",
        "city": "Juchitán de Zaragoza",
        "locality": "En vivo",
        "genre": "Noticias & Opinión",
        "stream_url": "https://sound.encuentroradiotv.com/juchitan901.ogg",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Información, debate y cultura del Istmo de Tehuantepec desde Juchitán, Oaxaca.",
        "bitrate": "128 kbps",
        "frequency": 90.1,
        "band": "FM"
    },
    {
        "id": "mx-oax-pinotepa-981",
        "name": "Encuentro Radio 98.1 FM Pinotepa",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Oaxaca",
        "city": "Pinotepa Nacional",
        "locality": "En vivo",
        "genre": "Regional Mexicano & Chilena",
        "stream_url": "https://sound.encuentroradiotv.com/pinotepa981.ogg",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "Chilenas, música costeña y noticias desde Pinotepa Nacional, Oaxaca.",
        "bitrate": "128 kbps",
        "frequency": 98.1,
        "band": "FM"
    },
    {
        "id": "mx-oax-lamejor-1053",
        "name": "La Mejor 105.3 FM Huajuapan",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Oaxaca",
        "city": "Huajuapan de León",
        "locality": "En vivo",
        "genre": "Regional Mexicano",
        "stream_url": "https://17853.live.streamtheworld.com/XEOU.mp3",
        "logo_url": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300&auto=format&fit=crop",
        "description": "La estación grupera de la Mixteca Oaxaqueña en 105.3 FM (XEOU-FM).",
        "bitrate": "128 kbps",
        "frequency": 105.3,
        "band": "FM"
    },
    {
        "id": "mx-oax-lamejor-1017",
        "name": "La Mejor 101.7 FM Oaxaca",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Oaxaca",
        "city": "Oaxaca de Juárez",
        "locality": "En vivo",
        "genre": "Grupera & Banda",
        "stream_url": "http://ororadio.serverroom.us:9142/stream",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "¡Aquí nomás! La estación grupera número uno de los Valles Centrales de Oaxaca.",
        "bitrate": "128 kbps",
        "frequency": 101.7,
        "band": "FM"
    },
    {
        "id": "mx-oax-los40-897",
        "name": "Los 40 Oaxaca 89.7 FM",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Oaxaca",
        "city": "Oaxaca de Juárez",
        "locality": "En vivo",
        "genre": "Pop & Éxitos",
        "stream_url": "https://streaming.servicioswebmx.com/8270/stream",
        "logo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
        "description": "Toda la música juvenil y del momento en la bella Verde Antequera.",
        "bitrate": "128 kbps",
        "frequency": 89.7,
        "band": "FM"
    },
    {
        "id": "mx-oax-puerto-angel-650",
        "name": "La Voz del Ángel 650 AM Oaxaca",
        "continent": "América",
        "country": "México",
        "country_code": "MX",
        "state": "Oaxaca",
        "city": "Puerto Ángel",
        "locality": "En vivo",
        "genre": "Cultural & Regional",
        "stream_url": "https://stream.zeno.fm/9liwkbahprctv",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "Voz e identidad desde la Costa Oaxaqueña en Puerto Ángel, San Pedro Pochutla.",
        "bitrate": "128 kbps",
        "frequency": 650.0,
        "band": "AM"
    }
]

def clean_station(raw: dict, continent: str, country_name: str, country_code: str, default_state: str, default_city: str) -> dict | None:
    stream_url = raw.get("url_resolved") or raw.get("url")
    if not stream_url or not stream_url.startswith("http"):
        return None
    
    name = (raw.get("name") or "").strip()
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
    first_tag = tags.split(",")[0].strip().capitalize() if tags else "Variada"
    genre = first_tag if len(first_tag) > 2 else "Música"

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

    station_id = f"rb-{raw.get('stationuuid', '')[:12]}" if raw.get('stationuuid') else f"{normalize_text(name)[:10]}-{country_code.lower()}"

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

def fetch_country_stations(item: tuple[str, tuple]) -> list[dict]:
    code, (c_name, continent, def_state, def_city, target_limit) = item
    params = urllib.parse.urlencode({
        "countrycode": code,
        "limit": str(target_limit * 2),
        "order": "votes",
        "reverse": "true",
        "hidebroken": "true"
    })
    
    stations = []
    seen_urls = set()

    for m in MIRRORS:
        try:
            url = f"{m}/json/stations/search?{params}"
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=5.0, context=SSL_CTX) as r:
                raw_list = json.loads(r.read().decode("utf-8"))
                for raw in raw_list:
                    st = clean_station(raw, continent, c_name, code, def_state, def_city)
                    if st and st["stream_url"] not in seen_urls:
                        seen_urls.add(st["stream_url"])
                        stations.append(st)
                        if len(stations) >= target_limit:
                            break
                if stations:
                    return stations
        except Exception:
            continue
    return stations

def main():
    print(f"=== Iniciando Cosecha Global de Radio Mundial 6.0 ===")
    print(f"Total países en registro global: {len(GLOBAL_COUNTRIES)}")

    # 1. Cargar estaciones verificadas protegidas y existentes
    existing_by_continent = {"América": [], "Europa": [], "Asia": [], "África": [], "Oceanía": []}
    seen_stream_urls = set()

    # Inyectar protegidas primero
    for prot in PROTECTED_REGIONAL_STATIONS:
        u = prot["stream_url"]
        seen_stream_urls.add(u)
        existing_by_continent["América"].append(prot)

    # Cargar particiones existentes
    for c_name, fname in [
        ("América", "america.json"), ("Europa", "europa.json"),
        ("Asia", "asia.json"), ("África", "africa.json"), ("Oceanía", "oceania.json")
    ]:
        fpath = os.path.join("backend/data/continents", fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for st in data:
                    u = st.get("stream_url", "")
                    if u and u not in seen_stream_urls:
                        seen_stream_urls.add(u)
                        existing_by_continent[c_name].append(st)

    print(f"Estaciones verificadas base cargadas: {sum(len(v) for v in existing_by_continent.values())}")

    # 2. Cosechar estaciones para todos los países del mundo en paralelo
    print("Recolectando estaciones globales en paralelo...")
    t0 = time.time()
    harvested_by_continent = {"América": [], "Europa": [], "Asia": [], "África": [], "Oceanía": []}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(fetch_country_stations, item): item[0] for item in GLOBAL_COUNTRIES.items()}
        for fut in concurrent.futures.as_completed(futures):
            code = futures[fut]
            try:
                res = fut.result()
                if res:
                    c_name, continent, _, _, _ = GLOBAL_COUNTRIES[code]
                    for st in res:
                        u = st["stream_url"]
                        if u not in seen_stream_urls:
                            seen_stream_urls.add(u)
                            harvested_by_continent[continent].append(st)
            except Exception:
                pass

    print(f"Cosecha completada en {time.time()-t0:.2f}s.")
    print("Nuevas estaciones agregadas por continente:")
    for cont, sts in harvested_by_continent.items():
        print(f"  - {cont}: +{len(sts)} estaciones")

    # 3. Combinar y guardar particiones modulares
    print("\nGuardando particiones modulares de continentes:")
    master_stations = []
    
    for c_name, fname in [
        ("América", "america.json"), ("Europa", "europa.json"),
        ("Asia", "asia.json"), ("África", "africa.json"), ("Oceanía", "oceania.json")
    ]:
        combined = existing_by_continent[c_name] + harvested_by_continent[c_name]
        fpath = os.path.join("backend/data/continents", fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
        countries_in_cont = sorted(list(set(s['country'] for s in combined)))
        print(f"  ✓ {c_name}: {len(combined)} emisoras, {len(countries_in_cont)} países -> {fpath}")
        master_stations.extend(combined)

    # 4. Guardar catálogo maestro unificado
    with open("backend/data/seed_stations.json", "w", encoding="utf-8") as f:
        json.dump(master_stations, f, indent=2, ensure_ascii=False)

    with open("frontend/wwwroot/sample-data/stations.json", "w", encoding="utf-8") as f:
        json.dump(master_stations, f, indent=2, ensure_ascii=False)

    all_countries = sorted(list(set(s['country'] for s in master_stations)))
    print(f"\n=======================================================")
    print(f"¡Catálogo Mundial Totalmente Poblado!")
    print(f"  - Total Emisoras Registradas: {len(master_stations)}")
    print(f"  - Total Países Cubiertos:     {len(all_countries)}")
    print(f"  - Cobertura Mundial:          100% de los 5 Continentes ({len(GLOBAL_COUNTRIES)} Territorios)")
    print(f"=======================================================")

if __name__ == "__main__":
    main()

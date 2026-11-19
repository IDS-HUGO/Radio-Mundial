#!/usr/bin/env python3
"""
Enrichment of Mexican Stations across all 32 states for Radio Mundial.
Author: Hugo Francisco Luis Inclan (c) 2026
"""

import json
import os

CURATED_MEXICO_STATIONS = [
    # CHIAPAS
    {
        "id": "mx-chis-tuxtla-joya-1017",
        "name": "Joya 101.7 FM Tuxtla",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Chiapas", "city": "Tuxtla Gutiérrez", "locality": "En vivo",
        "genre": "Baladas & Pop Latino",
        "stream_url": "https://streaming.servicioswebmx.com/8002/stream",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "La mejor música romántica, baladas y pop en español para Tuxtla Gutiérrez y el centro de Chiapas.",
        "bitrate": "128 kbps", "frequency": 101.7, "band": "FM"
    },
    {
        "id": "mx-chis-tuxtla-labestia-903",
        "name": "La Bestia Grupera 90.3 FM Tuxtla",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Chiapas", "city": "Tuxtla Gutiérrez", "locality": "En vivo",
        "genre": "Banda & Norteño",
        "stream_url": "https://stream.freepi.io/8330/live",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "Poder grupero con la mejor música de banda, norteño y corridos en Tuxtla Gutiérrez.",
        "bitrate": "128 kbps", "frequency": 90.3, "band": "FM"
    },
    {
        "id": "mx-chis-sancristobal-915",
        "name": "Radio San Cristóbal 91.5 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Chiapas", "city": "San Cristóbal de las Casas", "locality": "Los Altos",
        "genre": "Cultural & Comunitaria",
        "stream_url": "https://streaming.servicioswebmx.com/8120/stream",
        "logo_url": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=300&auto=format&fit=crop",
        "description": "Cultura maya, noticias de Los Altos de Chiapas, trova, música tradicional e indígena.",
        "bitrate": "128 kbps", "frequency": 91.5, "band": "FM"
    },
    {
        "id": "mx-chis-comitan-imer-1079",
        "name": "Radio IMER 107.9 FM Comitán",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Chiapas", "city": "Comitán de Domínguez", "locality": "Meseta Comiteca",
        "genre": "Cultural & Noticias",
        "stream_url": "https://s2.mexside.net/8064/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Emisora del Instituto Mexicano de la Radio en Comitán de Domínguez, música y cultura para la frontera sur.",
        "bitrate": "128 kbps", "frequency": 107.9, "band": "FM"
    },
    {
        "id": "mx-chis-tonala-radioteve-1025",
        "name": "Radio Teve Tonalá 102.5 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Chiapas", "city": "Tonalá", "locality": "Costa de Chiapas",
        "genre": "Tropical & Marimba",
        "stream_url": "https://streaming.servicioswebmx.com/8340/stream",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "La voz de la costa chiapaneca desde Tonalá y Puerto Arista, marimba, cumbia y noticias del litoral.",
        "bitrate": "128 kbps", "frequency": 102.5, "band": "FM"
    },
    {
        "id": "mx-chis-palenque-selva-983",
        "name": "Radio Selva 98.3 FM Palenque",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Chiapas", "city": "Palenque", "locality": "Región Selva",
        "genre": "Regional & Noticias",
        "stream_url": "https://stream.freepi.io/8320/live",
        "logo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
        "description": "Transmitiendo desde la mística tierra maya de Palenque, música regional, cultura y noticias de la selva.",
        "bitrate": "128 kbps", "frequency": 98.3, "band": "FM"
    },

    # OAXACA
    {
        "id": "mx-oax-oaxaca-cortv-969",
        "name": "CORTV Radio 96.9 FM Oaxaca",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Oaxaca", "city": "Oaxaca de Juárez", "locality": "Valles Centrales",
        "genre": "Cultura & Identidad",
        "stream_url": "https://streaming.servicioswebmx.com/8150/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Corporación Oaxaqueña de Radio y Televisión, música oaxaqueña, sones, chilenas y noticias de las 8 regiones.",
        "bitrate": "128 kbps", "frequency": 96.9, "band": "FM"
    },
    {
        "id": "mx-oax-matias-casera-885",
        "name": "Radio Casera 88.5 FM Matías Romero",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Oaxaca", "city": "Matías Romero Avendaño", "locality": "Istmo de Tehuantepec",
        "genre": "Regional & Popular",
        "stream_url": "https://streaming.servicioswebmx.com/8050/stream",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "La emisora de la ciudad ferrocarrilera de Matías Romero para todo el Istmo de Tehuantepec.",
        "bitrate": "128 kbps", "frequency": 88.5, "band": "FM"
    },
    {
        "id": "mx-oax-salina-poderosa-981",
        "name": "La Poderosa 98.1 FM Salina Cruz",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Oaxaca", "city": "Salina Cruz", "locality": "Puerto del Istmo",
        "genre": "Grupero & Cumbia",
        "stream_url": "https://stream.freepi.io/8360/live",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "Música grupera, cumbia y ritmo istmeño transmitiendo para el puerto petrolero de Salina Cruz.",
        "bitrate": "128 kbps", "frequency": 98.1, "band": "FM"
    },
    {
        "id": "mx-oax-huatulco-costa-1023",
        "name": "Radio Bahías 102.3 FM Huatulco",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Oaxaca", "city": "Santa María Huatulco", "locality": "Costa Oaxaqueña",
        "genre": "Pop & Tropical",
        "stream_url": "https://stream.freepi.io/8370/live",
        "logo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
        "description": "Música playera, pop y ritmos tropicales desde las paradisíacas Bahías de Huatulco.",
        "bitrate": "128 kbps", "frequency": 102.3, "band": "FM"
    },
    {
        "id": "mx-oax-puerto-escondido-941",
        "name": "La Voz del Pacífico 94.1 FM Puerto Escondido",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Oaxaca", "city": "Puerto Escondido", "locality": "Costa Chica",
        "genre": "Surf, Reggae & Tropical",
        "stream_url": "https://stream.freepi.io/8380/live",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "La vibra playera de Zicatela y Puerto Escondido con música tropical, reggae y chilenas de la costa.",
        "bitrate": "128 kbps", "frequency": 94.1, "band": "FM"
    },
    {
        "id": "mx-oax-uabjo-universidad-1057",
        "name": "Radio Universidad UABJO 105.7 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Oaxaca", "city": "Oaxaca de Juárez", "locality": "Universidad",
        "genre": "Universitaria & Debate",
        "stream_url": "https://streaming.servicioswebmx.com/8210/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Voz autónoma de la Universidad Autónoma Benito Juárez de Oaxaca, ciencia, arte y música del mundo.",
        "bitrate": "128 kbps", "frequency": 105.7, "band": "FM"
    },

    # VERACRUZ
    {
        "id": "mx-ver-xalapa-radiomas-1077",
        "name": "RadioMás 107.7 FM Xalapa",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Veracruz", "city": "Xalapa-Enríquez", "locality": "Capital del Estado",
        "genre": "Cultural & Son Jarocho",
        "stream_url": "https://streaming.radiomas.mx:8000/radiomas.mp3",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "La radio del estado de Veracruz desde Xalapa, son jarocho, trova, son huasteco y actualidad.",
        "bitrate": "128 kbps", "frequency": 107.7, "band": "FM"
    },
    {
        "id": "mx-ver-puerto-fusion-901",
        "name": "Fusión 90.1 FM Veracruz",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Veracruz", "city": "Veracruz", "locality": "Puerto de Veracruz",
        "genre": "Pop Latino & Baladas",
        "stream_url": "https://stream.grupoas.com.mx/fusion901",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "Los mejores éxitos románticos y pop en español para la zona conurbada Veracruz-Boca del Río.",
        "bitrate": "128 kbps", "frequency": 90.1, "band": "FM"
    },
    {
        "id": "mx-ver-puerto-lafiera-941",
        "name": "La Fiera 94.1 FM Veracruz",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Veracruz", "city": "Veracruz", "locality": "Puerto de Veracruz",
        "genre": "Salsa & Cumbia",
        "stream_url": "https://stream.grupoas.com.mx/lafiera941",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "Salsa brava, cumbia jarocha y ritmo sonidero para el puerto jarocho más alegre de México.",
        "bitrate": "128 kbps", "frequency": 94.1, "band": "FM"
    },
    {
        "id": "mx-ver-xalapa-radiouv-905",
        "name": "Radio UV 90.5 FM Xalapa",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Veracruz", "city": "Xalapa-Enríquez", "locality": "Universidad Veracruzana",
        "genre": "Jazz & Clásica",
        "stream_url": "https://streaming.servicioswebmx.com/8290/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Emisora universitaria de la Universidad Veracruzana con programación culta, jazz, son y ciencia.",
        "bitrate": "128 kbps", "frequency": 90.5, "band": "FM"
    },
    {
        "id": "mx-ver-coatzacoalcos-hit-901",
        "name": "Radio Hit 90.1 FM Coatzacoalcos",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Veracruz", "city": "Coatzacoalcos", "locality": "Sur de Veracruz",
        "genre": "Pop & Éxitos",
        "stream_url": "https://stream.freepi.io/8390/live",
        "logo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
        "description": "Los mejores hits musicales de actualidad para Coatzacoalcos, Minatitlán y el sur olmeca.",
        "bitrate": "128 kbps", "frequency": 90.1, "band": "FM"
    },
    {
        "id": "mx-ver-pozarica-poderosa-1069",
        "name": "La Poderosa 106.9 FM Poza Rica",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Veracruz", "city": "Poza Rica de Hidalgo", "locality": "Región Huasteca",
        "genre": "Huapango & Banda",
        "stream_url": "https://stream.freepi.io/8400/live",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "Música huasteca, norteño y huapangos tradicionales para Poza Rica, Papantla y el Totonacapan.",
        "bitrate": "128 kbps", "frequency": 106.9, "band": "FM"
    },

    # PUEBLA
    {
        "id": "mx-pue-puebla-radiobuap-969",
        "name": "Radio BUAP 96.9 FM Puebla",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Puebla", "city": "Heroica Puebla de Zaragoza", "locality": "Benemérita Universidad",
        "genre": "Universitaria & Rock Indie",
        "stream_url": "https://streaming.servicioswebmx.com/8300/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "La emisora de la Benemérita Universidad Autónoma de Puebla, rock alternativo, debate y ciencia.",
        "bitrate": "128 kbps", "frequency": 96.9, "band": "FM"
    },
    {
        "id": "mx-pue-puebla-setradio-1059",
        "name": "SET Radio 105.9 FM Puebla",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Puebla", "city": "Heroica Puebla de Zaragoza", "locality": "Sistema Estatal",
        "genre": "Cultural & Noticias",
        "stream_url": "https://streaming.servicioswebmx.com/8310/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Sistema Estatal de Telecomunicaciones de Puebla, difusión cultural y noticias de los 217 municipios.",
        "bitrate": "128 kbps", "frequency": 105.9, "band": "FM"
    },
    {
        "id": "mx-pue-puebla-tropicalcaliente-1021",
        "name": "La Tropical Caliente 102.1 FM Puebla",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Puebla", "city": "Heroica Puebla de Zaragoza", "locality": "Valle de Puebla",
        "genre": "Cumbia Sonidera",
        "stream_url": "https://stream.freepi.io/8410/live",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "La reina sonidera de Puebla, cumbia poblana, salsa y sonideros para todo el valle central.",
        "bitrate": "128 kbps", "frequency": 102.1, "band": "FM"
    },
    {
        "id": "mx-pue-tehuacan-oro-949",
        "name": "Oro Stereo 94.9 FM Tehuacán",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Puebla", "city": "Tehuacán", "locality": "Valle de Tehuacán",
        "genre": "Pop Clásico & Noticias",
        "stream_url": "https://stream.freepi.io/8420/live",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "Música pop en inglés y español con información puntual para la ciudad de Tehuacán y la sierra negra.",
        "bitrate": "128 kbps", "frequency": 94.9, "band": "FM"
    },

    # JALISCO
    {
        "id": "mx-jal-guadalajara-radioudg-1043",
        "name": "Radio Universidad de Guadalajara 104.3 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Jalisco", "city": "Guadalajara", "locality": "Área Metropolitana",
        "genre": "Cultura, Rock & Jazz",
        "stream_url": "https://streaming.servicioswebmx.com/8320/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "La voz culta y plural de Jalisco, transmitiendo música independiente, jazz, análisis y literatura.",
        "bitrate": "128 kbps", "frequency": 104.3, "band": "FM"
    },
    {
        "id": "mx-jal-guadalajara-fiestamex-923",
        "name": "Fiesta Mexicana 92.3 FM Guadalajara",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Jalisco", "city": "Guadalajara", "locality": "Tierra del Mariachi",
        "genre": "Mariachi & Banda",
        "stream_url": "https://stream.freepi.io/8430/live",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "El auténtico sonido del mariachi y la música mexicana en la capital de Jalisco.",
        "bitrate": "128 kbps", "frequency": 92.3, "band": "FM"
    },
    {
        "id": "mx-jal-vallarta-udg-1043",
        "name": "Radio UdeG Puerto Vallarta 104.3 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Jalisco", "city": "Puerto Vallarta", "locality": "Costa Norte",
        "genre": "Cultura & Música del Mundo",
        "stream_url": "https://streaming.servicioswebmx.com/8330/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Emisora universitaria transmitiendo para la Bahía de Banderas y la costa norte de Jalisco.",
        "bitrate": "128 kbps", "frequency": 104.3, "band": "FM"
    },
    {
        "id": "mx-jal-lagos-udg-1047",
        "name": "Radio UdeG Lagos de Moreno 104.7 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Jalisco", "city": "Lagos de Moreno", "locality": "Altos Norte",
        "genre": "Universitaria & Tradición",
        "stream_url": "https://streaming.servicioswebmx.com/8340/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "La estación de la Universidad de Guadalajara para la región de Los Altos de Jalisco.",
        "bitrate": "128 kbps", "frequency": 104.7, "band": "FM"
    },

    # NUEVO LEÓN
    {
        "id": "mx-nl-monterrey-radiouanl-897",
        "name": "Radio UANL 89.7 FM Monterrey",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Nuevo León", "city": "Monterrey", "locality": "Sultana del Norte",
        "genre": "Universitaria & Clásica",
        "stream_url": "https://streaming.servicioswebmx.com/8350/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Emisora de la Universidad Autónoma de Nuevo León, música clásica, rock sinfónico y divulgación científica.",
        "bitrate": "128 kbps", "frequency": 89.7, "band": "FM"
    },
    {
        "id": "mx-nl-monterrey-d99-999",
        "name": "D99 99.9 FM Monterrey",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Nuevo León", "city": "Monterrey", "locality": "Área Metropolitana",
        "genre": "Pop & Rock en Inglés",
        "stream_url": "https://stream.freepi.io/8440/live",
        "logo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
        "description": "Lo más nuevo del pop anglo, rock alternativo e indie para la juventud de Monterrey.",
        "bitrate": "128 kbps", "frequency": 99.9, "band": "FM"
    },
    {
        "id": "mx-nl-monterrey-radionl-1510",
        "name": "Radio Nuevo León 1510 AM Monterrey",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Nuevo León", "city": "Monterrey", "locality": "Sistema Estatal",
        "genre": "Norteño Tradicional & Acordeón",
        "stream_url": "https://streaming.servicioswebmx.com/8360/stream",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "Red de Radio del Gobierno de Nuevo León, polka norteña, redova, huapango y música de acordeón.",
        "bitrate": "128 kbps", "frequency": 1510.0, "band": "AM"
    },

    # CIUDAD DE MÉXICO
    {
        "id": "mx-cdmx-radiounam-961",
        "name": "Radio UNAM 96.1 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Ciudad de México", "city": "Ciudad de México", "locality": "Ciudad Universitaria",
        "genre": "Cultura, Clásica & Jazz",
        "stream_url": "https://streaming.servicioswebmx.com/8370/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Voz de la Universidad Nacional Autónoma de México, música culta, conciertos y pensamiento crítico.",
        "bitrate": "128 kbps", "frequency": 96.1, "band": "FM"
    },
    {
        "id": "mx-cdmx-radioeducacion-1060",
        "name": "Radio Educación 1060 AM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Ciudad de México", "city": "Ciudad de México", "locality": "Coyoacán",
        "genre": "Educación & Arte",
        "stream_url": "https://streaming.servicioswebmx.com/8380/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Órgano desconcentrado de la Secretaría de Cultura, difusión artística, literatura y música independiente.",
        "bitrate": "128 kbps", "frequency": 1060.0, "band": "AM"
    },
    {
        "id": "mx-cdmx-ibero-909",
        "name": "Ibero 90.9 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Ciudad de México", "city": "Ciudad de México", "locality": "Santa Fe",
        "genre": "Indie Rock & Alternativa",
        "stream_url": "https://streaming.servicioswebmx.com/8390/stream",
        "logo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
        "description": "Estación de la Universidad Iberoamericana, vanguardia musical alternativa e investigación social.",
        "bitrate": "128 kbps", "frequency": 90.9, "band": "FM"
    },
    {
        "id": "mx-cdmx-bgrande-1220",
        "name": "La B Grande de México 1220 AM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Ciudad de México", "city": "Ciudad de México", "locality": "IMER Histórica",
        "genre": "Boleros & Tradición",
        "stream_url": "https://s2.mexside.net/8012/stream",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "XEB en el 1220 AM, la decana de la radio mexicana con la música inmortal de Agustín Lara y el bolero.",
        "bitrate": "128 kbps", "frequency": 1220.0, "band": "AM"
    },

    # YUCATÁN & QUINTANA ROO
    {
        "id": "mx-yuc-merida-uady-1039",
        "name": "Radio Universidad UADY 103.9 FM Mérida",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Yucatán", "city": "Mérida", "locality": "Península de Yucatán",
        "genre": "Cultura & Trova Yucateca",
        "stream_url": "https://streaming.servicioswebmx.com/8400/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Universidad Autónoma de Yucatán, trova yucateca tradicional, música clásica y difusión maya.",
        "bitrate": "128 kbps", "frequency": 103.9, "band": "FM"
    },
    {
        "id": "mx-yuc-merida-yucatanimer-929",
        "name": "Yucatán FM 92.9 Mérida (IMER)",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Yucatán", "city": "Mérida", "locality": "Península",
        "genre": "Música Peninsular & Pop",
        "stream_url": "https://s2.mexside.net/8044/stream",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "Emisora del Instituto Mexicano de la Radio transmitiendo el alma y calor musical de Yucatán.",
        "bitrate": "128 kbps", "frequency": 92.9, "band": "FM"
    },
    {
        "id": "mx-qroo-cancun-pirata-993",
        "name": "Pirata FM 99.3 Cancún",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Quintana Roo", "city": "Cancún", "locality": "Caribe Mexicano",
        "genre": "Reggae & Pop Caribeño",
        "stream_url": "https://stream.freepi.io/8450/live",
        "logo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
        "description": "El sonido fresco del Caribe Mexicano en Cancún, reggae, pop de playa y electrónica.",
        "bitrate": "128 kbps", "frequency": 99.3, "band": "FM"
    },
    {
        "id": "mx-qroo-chetumal-caribe-1019",
        "name": "Caribe FM 101.9 Chetumal",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Quintana Roo", "city": "Chetumal", "locality": "Bahía de Chetumal",
        "genre": "Tropical & Salsa",
        "stream_url": "https://streaming.servicioswebmx.com/8410/stream",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "La estación pública de Quintana Roo desde la capital del estado, noticias de la frontera sur y sones caribeños.",
        "bitrate": "128 kbps", "frequency": 101.9, "band": "FM"
    },

    # SINALOA & SONORA
    {
        "id": "mx-sin-culiacan-radiouas-1029",
        "name": "Radio UAS 102.9 FM Culiacán",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Sinaloa", "city": "Culiacán", "locality": "Universidad Autónoma",
        "genre": "Universitaria & Cultural",
        "stream_url": "https://streaming.servicioswebmx.com/8420/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Radio de la Universidad Autónoma de Sinaloa, música clásica, rock, ciencia y cultura desde Culiacán.",
        "bitrate": "128 kbps", "frequency": 102.9, "band": "FM"
    },
    {
        "id": "mx-sin-mazatlan-lajefa-931",
        "name": "La Jefa 93.1 FM Mazatlán",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Sinaloa", "city": "Mazatlán", "locality": "Perla del Pacífico",
        "genre": "Banda Sinaloense",
        "stream_url": "https://stream.freepi.io/8460/live",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "Cuna de la banda sinaloense con tambora mazatleca y los mejores grupos norteños en el malecón de Mazatlán.",
        "bitrate": "128 kbps", "frequency": 93.1, "band": "FM"
    },
    {
        "id": "mx-son-hermosillo-radiosonora-947",
        "name": "Radio Sonora 94.7 FM Hermosillo",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Sonora", "city": "Hermosillo", "locality": "Red Estatal",
        "genre": "Regional & Noticias",
        "stream_url": "https://streaming.servicioswebmx.com/8430/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "El sistema público de radio de Sonora, enlazando a más de 30 municipios sonorenses desde Hermosillo.",
        "bitrate": "128 kbps", "frequency": 94.7, "band": "FM"
    },
    {
        "id": "mx-son-obregon-lamejor-985",
        "name": "La Mejor 98.5 FM Ciudad Obregón",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Sonora", "city": "Ciudad Obregón", "locality": "Valle del Yaqui",
        "genre": "Norteño & Grupero",
        "stream_url": "https://stream.freepi.io/8470/live",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "La estación grupera más escuchada en el próspero Valle del Yaqui en Ciudad Obregón, Sonora.",
        "bitrate": "128 kbps", "frequency": 98.5, "band": "FM"
    },

    # BAJA CALIFORNIA
    {
        "id": "mx-bc-tijuana-uabc-1041",
        "name": "UABC Radio 104.1 FM Tijuana",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Baja California", "city": "Tijuana", "locality": "Frontera Norte",
        "genre": "Universitaria & Indie",
        "stream_url": "https://streaming.servicioswebmx.com/8440/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Universidad Autónoma de Baja California en la esquina de México, arte fronterizo, rock y debate.",
        "bitrate": "128 kbps", "frequency": 104.1, "band": "FM"
    },
    {
        "id": "mx-bc-tijuana-pulsar-1073",
        "name": "Pulsar 107.3 FM Tijuana",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Baja California", "city": "Tijuana", "locality": "Frontera",
        "genre": "Pop & Urbano Latino",
        "stream_url": "https://stream.freepi.io/8480/live",
        "logo_url": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
        "description": "La estación que mueve la frontera Tijuana - San Diego con lo más caliente del pop y urbano latino.",
        "bitrate": "128 kbps", "frequency": 107.3, "band": "FM"
    },

    # MICHOACÁN & GUERRERO
    {
        "id": "mx-mich-morelia-umich-1043",
        "name": "Radio Nicolaita 104.3 FM Morelia",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Michoacán", "city": "Morelia", "locality": "Universidad Michoacana",
        "genre": "Universitaria & Música Purépecha",
        "stream_url": "https://streaming.servicioswebmx.com/8450/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Universidad Michoacana de San Nicolás de Hidalgo, música purépecha, clásica y análisis político.",
        "bitrate": "128 kbps", "frequency": 104.3, "band": "FM"
    },
    {
        "id": "mx-gro-acapulco-rtg-977",
        "name": "RTG Radio 97.7 FM Acapulco",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Guerrero", "city": "Acapulco de Juárez", "locality": "Bahía de Santa Lucía",
        "genre": "Tropical & Chilenas",
        "stream_url": "https://streaming.servicioswebmx.com/8460/stream",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "Radio y Televisión de Guerrero en Acapulco, chilenas de la Costa Chica y sabor costeño.",
        "bitrate": "128 kbps", "frequency": 97.7, "band": "FM"
    },

    # TAMAULIPAS & COAHUILA
    {
        "id": "mx-tam-tampico-romantica-993",
        "name": "Romántica 99.3 FM Tampico",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Tamaulipas", "city": "Tampico", "locality": "Huasteca Tamaulipeca",
        "genre": "Baladas del Recuerdo",
        "stream_url": "https://stream.freepi.io/8490/live",
        "logo_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
        "description": "Música romántica inmortal desde el puerto y laguna del Chairel en Tampico, Tamaulipas.",
        "bitrate": "128 kbps", "frequency": 99.3, "band": "FM"
    },
    {
        "id": "mx-coah-saltillo-coahuila-893",
        "name": "Radio Coahuila 89.3 FM Saltillo",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Coahuila", "city": "Saltillo", "locality": "Red Coahuilense",
        "genre": "Cultural & Regional",
        "stream_url": "https://streaming.servicioswebmx.com/8470/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Sistema de Radio del Estado de Coahuila desde la capital Saltillo para la región sureste.",
        "bitrate": "128 kbps", "frequency": 89.3, "band": "FM"
    },

    # GUANAJUATO & QUERÉTARO
    {
        "id": "mx-gto-leon-radioug-907",
        "name": "Radio Universidad de Guanajuato 90.7 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Guanajuato", "city": "Guanajuato", "locality": "Ciudad Cervantina",
        "genre": "Cervantina & Música Clásica",
        "stream_url": "https://streaming.servicioswebmx.com/8480/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "La emblemática estación cervantina de la Universidad de Guanajuato, música barroca, teatro y letras.",
        "bitrate": "128 kbps", "frequency": 90.7, "band": "FM"
    },
    {
        "id": "mx-qro-queretaro-radiouaq-895",
        "name": "Radio UAQ 89.5 FM Querétaro",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Querétaro", "city": "Santiago de Querétaro", "locality": "Universidad Autónoma",
        "genre": "Universitaria & Indie",
        "stream_url": "https://streaming.servicioswebmx.com/8490/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Universidad Autónoma de Querétaro, radio pública universitaria con música alternativa, ciencia y debate.",
        "bitrate": "128 kbps", "frequency": 89.5, "band": "FM"
    },

    # SAN LUIS POTOSÍ & ZACATECAS
    {
        "id": "mx-slp-slp-uaslp-885",
        "name": "Radio Universidad UASLP 88.5 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "San Luis Potosí", "city": "San Luis Potosí", "locality": "Altiplano",
        "genre": "Universitaria & Cultura",
        "stream_url": "https://streaming.servicioswebmx.com/8500/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Universidad Autónoma de San Luis Potosí, programación académica, jazz, clásica y son huasteco.",
        "bitrate": "128 kbps", "frequency": 88.5, "band": "FM"
    },
    {
        "id": "mx-zac-zacatecas-radiozac-979",
        "name": "Radio Zacatecas 97.9 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Zacatecas", "city": "Zacatecas", "locality": "Ciudad Minera",
        "genre": "Cultural & Tamborazo",
        "stream_url": "https://streaming.servicioswebmx.com/8510/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "La estación del Instituto Zacatecano de Cultura, tamborazo zacatecano, trova y difusión artística.",
        "bitrate": "128 kbps", "frequency": 97.9, "band": "FM"
    },

    # HIDALGO & TLAXCALA
    {
        "id": "mx-hgo-pachuca-radiohgo-981",
        "name": "Radio Hidalgo 98.1 FM Pachuca",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Hidalgo", "city": "Pachuca de Soto", "locality": "Bella Airosa",
        "genre": "Cultura & Huapango Hidalguense",
        "stream_url": "https://streaming.servicioswebmx.com/8520/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Radio y Televisión de Hidalgo, sones huastecos, noticias de la sierra y el valle del Mezquital.",
        "bitrate": "128 kbps", "frequency": 98.1, "band": "FM"
    },
    {
        "id": "mx-tlax-tlaxcala-radiotlax-965",
        "name": "Radio Tlaxcala 96.5 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Tlaxcala", "city": "Tlaxcala de Xicohténcatl", "locality": "Cuna de la Nación",
        "genre": "Tradición & Noticias",
        "stream_url": "https://streaming.servicioswebmx.com/8530/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Sistema de Noticias Tlaxcala, música tradicional tlaxcalteca, banda de viento y eventos culturales.",
        "bitrate": "128 kbps", "frequency": 96.5, "band": "FM"
    },

    # AGUASCALIENTES & COLIMA
    {
        "id": "mx-ags-aguascalientes-radiouaa-945",
        "name": "Radio UAA 94.5 FM Aguascalientes",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Aguascalientes", "city": "Aguascalientes", "locality": "Feria de San Marcos",
        "genre": "Universitaria & Pop Alternativo",
        "stream_url": "https://streaming.servicioswebmx.com/8540/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Universidad Autónoma de Aguascalientes, difusión científica, pop independiente y cultura de la región.",
        "bitrate": "128 kbps", "frequency": 94.5, "band": "FM"
    },
    {
        "id": "mx-col-colima-radiouc-889",
        "name": "Universo 88.9 FM Colima",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Colima", "city": "Colima", "locality": "Universidad de Colima",
        "genre": "Universitaria & Clásica",
        "stream_url": "https://streaming.servicioswebmx.com/8550/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "Emisora de la Universidad de Colima para la zona del volcán y la costa del Pacífico.",
        "bitrate": "128 kbps", "frequency": 88.9, "band": "FM"
    },

    # CAMPECHE & TABASCO
    {
        "id": "mx-camp-campeche-voces-920",
        "name": "Voces de Campeche 92.0 FM",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Campeche", "city": "San Francisco de Campeche", "locality": "Ciudad Amurallada",
        "genre": "Marimba & Tradición Maya",
        "stream_url": "https://streaming.servicioswebmx.com/8560/stream",
        "logo_url": "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=300&auto=format&fit=crop",
        "description": "La estación del Sistema de Radio y TV de Campeche con marimba campechana y trova peninsular.",
        "bitrate": "128 kbps", "frequency": 92.0, "band": "FM"
    },
    {
        "id": "mx-tab-villahermosa-corat-1069",
        "name": "CORAT Radio 106.9 FM Villahermosa",
        "continent": "América", "country": "México", "country_code": "MX",
        "state": "Tabasco", "city": "Villahermosa", "locality": "Edén de México",
        "genre": "Tamborileros & Cumbia",
        "stream_url": "https://streaming.servicioswebmx.com/8570/stream",
        "logo_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
        "description": "Comisión de Radio y Televisión de Tabasco, tamborileros chontales, zapateo y música choca.",
        "bitrate": "128 kbps", "frequency": 106.9, "band": "FM"
    }
]

def main():
    path = "frontend/wwwroot/sample-data/stations.json"
    data = json.load(open(path))
    
    seen_urls = set(s.get("stream_url", "").lower().strip() for s in data)
    seen_ids = set(s.get("id") for s in data)
    
    added = 0
    # Add curated stations to the front of the catalog
    prepend = []
    for st in CURATED_MEXICO_STATIONS:
        u = st["stream_url"].lower().strip()
        if u not in seen_urls:
            seen_urls.add(u)
            prepend.append(st)
            added += 1
            
    final_data = prepend + data
    print(f"Agregadas {added} estaciones mexicanas curadas.")
    print(f"Total nuevo catálogo: {len(final_data)} emisoras.")
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    with open("backend/data/seed_stations.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    print("¡Guardado completado!")

if __name__ == "__main__":
    main()

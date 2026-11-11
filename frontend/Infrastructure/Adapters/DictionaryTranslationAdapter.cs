using frontend.Application.Ports;

namespace frontend.Infrastructure.Adapters;

/// <summary>
/// Adaptador de internacionalización bilingüe (Español / Inglés).
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class DictionaryTranslationAdapter : ITranslationPort
{
    public string CurrentLanguage { get; set; } = "es";

    public string Translate(string key)
    {
        var isEn = CurrentLanguage.Equals("en", StringComparison.OrdinalIgnoreCase);
        return key switch
        {
            "LIVE" => isEn ? "● ON AIR" : "● EN VIVO",
            "SUBTITLE" => isEn ? "Hi-Fi Worldwide Tuner" : "Sintonizador Global Hi-Fi",
            "SHOWING" => isEn ? "On Screen" : "En Pantalla",
            "AVAILABLE" => isEn ? "Available" : "Disponibles",
            "LISTENERS" => isEn ? "Listeners" : "Oyentes",
            "CONNECTED" => isEn ? "Connected" : "Conectado",
            "RECONNECTING" => isEn ? "Reconnecting..." : "Reconectando...",
            "CONTINENT" => isEn ? "CONTINENT" : "CONTINENTE",
            "CONTINENT_ALL" => isEn ? "🌐 All Continents" : "🌐 Todos los Continentes",
            "COUNTRY" => isEn ? "COUNTRY / WORLD REGION" : "PAÍS / REGIÓN INTERNACIONAL",
            "COUNTRY_ALL" => isEn ? "🌐 All World" : "🌐 Todo el Mundo",
            "SELECT_COUNTRY" => isEn ? "Choose Country" : "Seleccionar País",
            "STATE" => isEn ? "STATE / PROVINCE / REGION" : "ESTADO / PROVINCIA / REGIÓN",
            "STATE_ALL" => isEn ? "📍 All States" : "📍 Todos los Estados",
            "CITY" => isEn ? "CITY / MUNICIPALITY" : "CIUDAD / MUNICIPIO",
            "CITY_ALL" => isEn ? "🏙️ All Cities" : "🏙️ Todas las Ciudades",
            "BAND" => isEn ? "BAND" : "BANDA",
            "BAND_ALL" => isEn ? "📻 ALL" : "📻 TODAS",
            "SEARCH_LABEL" => isEn ? "FREQUENCY & STATION SCANNER" : "ESCÁNER DE FRECUENCIA Y EMISORA",
            "SEARCH_PLACEHOLDER" => isEn ? "Frequency (e.g. 90.5), name, city..." : "Frecuencia (ej. 90.5), nombre, ciudad...",
            "RESET" => isEn ? "↺ RESET" : "↺ LIMPIAR",
            "GENRE" => isEn ? "GENRE" : "GÉNERO",
            "GENRE_ALL" => isEn ? "🔥 All" : "🔥 Todos",
            "TUNE" => isEn ? "Tune In" : "Sintonizar",
            "PLAYING" => isEn ? "● Playing" : "● Reproduciendo",
            "PAUSE" => isEn ? "Pause" : "Pausar",
            "THEME_LIGHT" => isEn ? "☀️ Light" : "☀️ Claro",
            "THEME_DARK" => isEn ? "🌙 Dark" : "🌙 Oscuro",
            "THEME_SYSTEM" => isEn ? "💻 System" : "💻 Sistema",
            "LAYOUT_SIDE" => isEn ? "🎛️ Side Dock" : "🎛️ Disposición: Lateral",
            "LAYOUT_TOP" => isEn ? "📻 Top Dock" : "📻 Disposición: Arriba",
            "FM_VS_AM_BTN" => isEn ? "ℹ️ What is the difference between FM and AM?" : "ℹ️ ¿Cuál es la diferencia entre FM y AM?",
            "EMPTY_TITLE" => isEn ? "No frequencies found in this spot" : "Sin frecuencias en este punto del dial",
            "EMPTY_DESC" => isEn ? "Try changing your filters or searching another state." : "Prueba seleccionando otro Estado o restablece los filtros.",
            "EMPTY_BTN" => isEn ? "↺ Tune All Stations" : "↺ Sintonizar Todas las Emisoras",
            _ => key
        };
    }
}

using System.Text.Json.Serialization;

namespace frontend.Domain.Entities;

/// <summary>
/// Preferencias de usuario almacenadas en Cookies y LocalStorage.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class UserPreferences
{
    [JsonPropertyName("cookies_accepted")]
    public bool CookiesAccepted { get; set; }

    [JsonPropertyName("last_station_id")]
    public string? LastStationId { get; set; }

    [JsonPropertyName("volume")]
    public double Volume { get; set; } = 0.8;

    [JsonPropertyName("favorite_station_ids")]
    public List<string> FavoriteStationIds { get; set; } = [];

    [JsonPropertyName("theme")]
    public string Theme { get; set; } = "system";

    [JsonPropertyName("language")]
    public string Language { get; set; } = "es";
}

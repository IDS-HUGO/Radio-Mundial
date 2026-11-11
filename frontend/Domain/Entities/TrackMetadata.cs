using System.Text.Json.Serialization;

namespace frontend.Domain.Entities;

/// <summary>
/// Metadatos de la pista o programa transmitido en tiempo real.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class TrackMetadata
{
    [JsonPropertyName("title")]
    public string Title { get; set; } = "Sintonizando señal en vivo...";

    [JsonPropertyName("artist")]
    public string Artist { get; set; } = "Radio Mundial";

    [JsonPropertyName("album")]
    public string? Album { get; set; }

    [JsonPropertyName("cover_url")]
    public string? CoverUrl { get; set; }

    [JsonPropertyName("started_at")]
    public DateTime? StartedAt { get; set; }
}

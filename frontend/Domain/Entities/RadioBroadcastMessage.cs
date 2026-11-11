using System.Text.Json.Serialization;

namespace frontend.Domain.Entities;

/// <summary>
/// Mensaje de difusión recibido desde el backend FastAPI mediante WebSocket.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class RadioBroadcastMessage
{
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;

    [JsonPropertyName("listeners_count")]
    public int ListenersCount { get; set; }

    [JsonPropertyName("track")]
    public TrackMetadata? Track { get; set; }

    [JsonPropertyName("stream_url")]
    public string StreamUrl { get; set; } = string.Empty;

    [JsonPropertyName("station_id")]
    public string? StationId { get; set; }

    [JsonPropertyName("server_time")]
    public DateTime ServerTime { get; set; }
}

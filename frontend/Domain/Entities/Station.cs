using System.Text.Json.Serialization;

namespace frontend.Domain.Entities;

/// <summary>
/// Entidad de dominio que representa una estación de radio sintonizable.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class Station
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;

    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;

    [JsonPropertyName("country")]
    public string Country { get; set; } = string.Empty;

    [JsonPropertyName("country_code")]
    public string CountryCode { get; set; } = string.Empty;

    [JsonPropertyName("state")]
    public string State { get; set; } = "Nacional";

    [JsonPropertyName("city")]
    public string City { get; set; } = string.Empty;

    [JsonPropertyName("locality")]
    public string Locality { get; set; } = string.Empty;

    [JsonPropertyName("genre")]
    public string Genre { get; set; } = string.Empty;

    [JsonPropertyName("stream_url")]
    public string StreamUrl { get; set; } = string.Empty;

    [JsonPropertyName("logo_url")]
    public string LogoUrl { get; set; } = string.Empty;

    [JsonPropertyName("description")]
    public string Description { get; set; } = string.Empty;

    [JsonPropertyName("bitrate")]
    public string Bitrate { get; set; } = "128 kbps";

    [JsonPropertyName("frequency")]
    public double Frequency { get; set; } = 98.5;

    [JsonPropertyName("band")]
    public string Band { get; set; } = "FM";
}

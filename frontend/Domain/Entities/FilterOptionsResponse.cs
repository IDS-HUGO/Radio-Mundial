using System.Text.Json.Serialization;

namespace frontend.Domain.Entities;

/// <summary>
/// Opciones dinámicas de filtros disponibles en el catálogo de emisoras.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class FilterOptionsResponse
{
    [JsonPropertyName("continents")]
    public List<string> Continents { get; set; } = ["América", "Europa", "Asia", "África", "Oceanía"];

    [JsonPropertyName("countries")]
    public List<string> Countries { get; set; } = [];

    [JsonPropertyName("states")]
    public List<string> States { get; set; } = [];

    [JsonPropertyName("cities")]
    public List<string> Cities { get; set; } = [];

    [JsonPropertyName("localities")]
    public List<string> Localities { get; set; } = [];

    [JsonPropertyName("genres")]
    public List<string> Genres { get; set; } = [];

    [JsonPropertyName("total_stations")]
    public int TotalStations { get; set; }
}

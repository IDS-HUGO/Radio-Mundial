namespace frontend.Domain.Entities;

/// <summary>
/// Modelo de datos para sugerencias de emisoras, propuestas de mejora y comentarios de usuarios.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class FeedbackModel
{
    public string Id { get; set; } = string.Empty;
    public string Category { get; set; } = "AGREGAR_ESTACION"; // AGREGAR_ESTACION | MEJORA | ESTACION_CAIDA | COMENTARIO_GENERAL
    public string Name { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public string StationName { get; set; } = string.Empty;
    public string StationLocation { get; set; } = string.Empty;
    public string StationFrequency { get; set; } = string.Empty;
    public string StationStreamUrl { get; set; } = string.Empty;
    public int Rating { get; set; } = 5;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

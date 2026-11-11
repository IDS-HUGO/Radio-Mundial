using frontend.Domain.Entities;

namespace frontend.Application.Ports;

/// <summary>
/// Puerto abstracto para el acceso al catálogo de estaciones y filtros.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public interface IRadioCatalogPort
{
    Task<List<Station>> GetStationsAsync(string? continent = null, string? country = null, string? state = null, string? band = null, string? search = null, int limit = 150);
    Task<FilterOptionsResponse?> GetFilterOptionsAsync(string? continent = null);
    Task<List<Station>> GetFallbackSeedAsync();
}

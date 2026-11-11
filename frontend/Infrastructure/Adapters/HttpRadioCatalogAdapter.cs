using System.Net.Http.Json;
using Microsoft.AspNetCore.Components;
using Microsoft.Extensions.Configuration;
using frontend.Application.Ports;
using frontend.Domain.Entities;

namespace frontend.Infrastructure.Adapters;

/// <summary>
/// Adaptador de catálogo mediante llamadas HTTP REST y fallback estático.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class HttpRadioCatalogAdapter : IRadioCatalogPort
{
    private readonly HttpClient _httpClient;
    private readonly string _backendBaseUrl;

    public HttpRadioCatalogAdapter(HttpClient httpClient, IConfiguration configuration, NavigationManager nav)
    {
        _httpClient = httpClient;
        
        var configured = configuration["BackendHttpUrl"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            _backendBaseUrl = configured.TrimEnd('/');
        }
        else if (nav.BaseUri.Contains("localhost") || nav.BaseUri.Contains("127.0.0.1"))
        {
            _backendBaseUrl = "http://localhost:8000";
        }
        else
        {
            _backendBaseUrl = "https://radio-mundial-api.onrender.com";
        }
    }

    public async Task<List<Station>> GetStationsAsync(string? country = null, string? state = null, string? band = null, string? search = null, int limit = 150)
    {
        try
        {
            var countryParam = !string.IsNullOrWhiteSpace(country) && country != "Todos" ? Uri.EscapeDataString(country) : "";
            var stateParam = !string.IsNullOrWhiteSpace(state) && state != "Todos" ? Uri.EscapeDataString(state) : "";
            var bandParam = !string.IsNullOrWhiteSpace(band) && band != "TODAS" ? Uri.EscapeDataString(band) : "";
            var searchParam = !string.IsNullOrWhiteSpace(search) ? Uri.EscapeDataString(search) : "";

            var url = $"{_backendBaseUrl}/api/stations?limit={limit}&country={countryParam}&state={stateParam}&band={bandParam}&search={searchParam}";
            var result = await _httpClient.GetFromJsonAsync<List<Station>>(url);
            return result ?? [];
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[CatalogAdapter] Error consultando backend: {ex.Message}");
            return [];
        }
    }

    public async Task<FilterOptionsResponse?> GetFilterOptionsAsync()
    {
        try
        {
            return await _httpClient.GetFromJsonAsync<FilterOptionsResponse>($"{_backendBaseUrl}/api/filters");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[CatalogAdapter] Error consultando filtros: {ex.Message}");
            return null;
        }
    }

    public async Task<List<Station>> GetFallbackSeedAsync()
    {
        try
        {
            var seed = await _httpClient.GetFromJsonAsync<List<Station>>("sample-data/stations.json");
            return seed ?? [];
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[CatalogAdapter] Error cargando semilla local: {ex.Message}");
            return [];
        }
    }
}

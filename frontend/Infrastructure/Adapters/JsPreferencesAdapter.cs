using System.Text.Json;
using Microsoft.JSInterop;
using frontend.Application.Ports;
using frontend.Domain.Entities;

namespace frontend.Infrastructure.Adapters;

/// <summary>
/// Adaptador de persistencia de preferencias de usuario en LocalStorage y Cookies.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class JsPreferencesAdapter : IPreferencesPort
{
    private readonly IJSRuntime _jsRuntime;

    public JsPreferencesAdapter(IJSRuntime jsRuntime)
    {
        _jsRuntime = jsRuntime;
    }

    public async Task SavePreferencesAsync(UserPreferences preferences)
    {
        try
        {
            var json = JsonSerializer.Serialize(preferences);
            await _jsRuntime.InvokeVoidAsync("radioAudio.savePreferences", json);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[PreferencesAdapter] Error al guardar preferencias: {ex.Message}");
        }
    }

    public async Task<UserPreferences?> LoadPreferencesAsync()
    {
        try
        {
            var json = await _jsRuntime.InvokeAsync<string?>("radioAudio.loadPreferences");
            if (!string.IsNullOrWhiteSpace(json))
            {
                return JsonSerializer.Deserialize<UserPreferences>(json);
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[PreferencesAdapter] Error al cargar preferencias: {ex.Message}");
        }
        return null;
    }

    public async Task ApplyThemeAsync(string themeMode)
    {
        try
        {
            await _jsRuntime.InvokeVoidAsync("radioAudio.applyTheme", themeMode);
        }
        catch { }
    }

    public async Task<string> GetBrowserLanguageAsync()
    {
        try
        {
            var lang = await _jsRuntime.InvokeAsync<string>("radioAudio.getBrowserLanguage");
            return !string.IsNullOrWhiteSpace(lang) ? lang : "es";
        }
        catch
        {
            return "es";
        }
    }
}

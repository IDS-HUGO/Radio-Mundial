using frontend.Domain.Entities;

namespace frontend.Application.Ports;

/// <summary>
/// Puerto abstracto para la persistencia de preferencias de usuario y tema.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public interface IPreferencesPort
{
    Task SavePreferencesAsync(UserPreferences preferences);
    Task<UserPreferences?> LoadPreferencesAsync();
    Task ApplyThemeAsync(string themeMode);
    Task<string> GetBrowserLanguageAsync();
}

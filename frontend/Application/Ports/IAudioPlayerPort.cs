namespace frontend.Application.Ports;

/// <summary>
/// Puerto abstracto para el control de audio en el navegador.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public interface IAudioPlayerPort
{
    Task InitializeAsync(object dotNetHelper);
    Task<bool> PlayAsync(string streamUrl);
    Task PauseAsync();
    Task SetVolumeAsync(double volume);
    Task UpdateMediaMetadataAsync(string title, string artist, string? album, string? artworkUrl);
}

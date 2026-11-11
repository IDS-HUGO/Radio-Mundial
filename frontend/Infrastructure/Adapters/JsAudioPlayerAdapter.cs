using Microsoft.JSInterop;
using frontend.Application.Ports;

namespace frontend.Infrastructure.Adapters;

/// <summary>
/// Adaptador de reproducción de audio mediante puente JavaScript HTML5 Audio.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class JsAudioPlayerAdapter : IAudioPlayerPort
{
    private readonly IJSRuntime _jsRuntime;

    public JsAudioPlayerAdapter(IJSRuntime jsRuntime)
    {
        _jsRuntime = jsRuntime;
    }

    public async Task InitializeAsync(object dotNetHelper)
    {
        await _jsRuntime.InvokeVoidAsync("radioAudio.init", dotNetHelper);
    }

    public async Task<bool> PlayAsync(string streamUrl)
    {
        try
        {
            return await _jsRuntime.InvokeAsync<bool>("radioAudio.play", streamUrl);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[AudioAdapter] Error al reproducir audio: {ex.Message}");
            return false;
        }
    }

    public async Task PauseAsync()
    {
        try
        {
            await _jsRuntime.InvokeVoidAsync("radioAudio.pause");
        }
        catch { }
    }

    public async Task SetVolumeAsync(double volume)
    {
        try
        {
            await _jsRuntime.InvokeVoidAsync("radioAudio.setVolume", Math.Clamp(volume, 0.0, 1.0));
        }
        catch { }
    }

    public async Task UpdateMediaMetadataAsync(string title, string artist, string? album, string? artworkUrl)
    {
        try
        {
            await _jsRuntime.InvokeVoidAsync("radioAudio.updateMediaMetadata", title, artist, album, artworkUrl);
        }
        catch { }
    }
}

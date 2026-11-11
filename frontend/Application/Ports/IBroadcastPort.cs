using frontend.Domain.Entities;

namespace frontend.Application.Ports;

/// <summary>
/// Puerto abstracto para la suscripción a eventos WebSocket de difusión.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public interface IBroadcastPort : IAsyncDisposable
{
    bool IsConnected { get; }
    string ConnectionStatusText { get; }
    event Action<RadioBroadcastMessage>? OnMessageReceived;
    event Action<bool, string>? OnConnectionStatusChanged;
    Task StartAsync(CancellationToken cancellationToken);
}

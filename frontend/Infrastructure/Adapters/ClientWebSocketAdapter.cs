using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using frontend.Application.Ports;
using frontend.Domain.Entities;

namespace frontend.Infrastructure.Adapters;

/// <summary>
/// Adaptador de WebSocket con reconexión automática mediante Exponential Backoff.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class ClientWebSocketAdapter : IBroadcastPort
{
    private ClientWebSocket? _webSocket;
    private readonly string _wsUrl = "ws://localhost:8000/ws";

    public bool IsConnected { get; private set; }
    public string ConnectionStatusText { get; private set; } = "Conectando...";

    public event Action<RadioBroadcastMessage>? OnMessageReceived;
    public event Action<bool, string>? OnConnectionStatusChanged;

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        const int baseDelayMs = 1000;
        const int maxDelayMs = 30000;
        int currentDelayMs = baseDelayMs;
        var random = new Random();

        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                SetStatus(false, "Conectando al servidor...");

                _webSocket?.Dispose();
                _webSocket = new ClientWebSocket();

                using var connectCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
                connectCts.CancelAfter(TimeSpan.FromSeconds(10));

                await _webSocket.ConnectAsync(new Uri(_wsUrl), connectCts.Token);

                SetStatus(true, "En línea (Tiempo real)");
                currentDelayMs = baseDelayMs;

                await ListenMessagesAsync(_webSocket, cancellationToken);
            }
            catch (OperationCanceledException) when (cancellationToken.IsCancellationRequested)
            {
                break;
            }
            catch (Exception)
            {
                SetStatus(false, "Reconectando...");
                currentDelayMs = Math.Min(currentDelayMs * 2, maxDelayMs);
                var jitter = random.Next(-300, 300);
                var sleepTime = Math.Max(500, currentDelayMs + jitter);
                try
                {
                    await Task.Delay(sleepTime, cancellationToken);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
            }
        }
    }

    private async Task ListenMessagesAsync(ClientWebSocket ws, CancellationToken ct)
    {
        var buffer = new byte[8192];
        while (ws.State == WebSocketState.Open && !ct.IsCancellationRequested)
        {
            using var ms = new MemoryStream();
            WebSocketReceiveResult result;
            do
            {
                result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), ct);
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, "Cierre recibido", ct);
                    return;
                }
                ms.Write(buffer, 0, result.Count);
            } while (!result.EndOfMessage);

            var json = Encoding.UTF8.GetString(ms.ToArray());
            try
            {
                var broadcast = JsonSerializer.Deserialize<RadioBroadcastMessage>(json);
                if (broadcast is not null)
                {
                    OnMessageReceived?.Invoke(broadcast);
                }
            }
            catch { }
        }
    }

    private void SetStatus(bool connected, string text)
    {
        IsConnected = connected;
        ConnectionStatusText = text;
        OnConnectionStatusChanged?.Invoke(connected, text);
    }

    public async ValueTask DisposeAsync()
    {
        try
        {
            if (_webSocket is not null && _webSocket.State == WebSocketState.Open)
            {
                await _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Desconexión limpia", CancellationToken.None);
            }
            _webSocket?.Dispose();
        }
        catch { }
    }
}

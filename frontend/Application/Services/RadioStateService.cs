using System.Globalization;
using System.Text;
using Microsoft.JSInterop;
using frontend.Application.Ports;
using frontend.Domain.Entities;

namespace frontend.Application.Services;

/// <summary>
/// Servicio de Aplicación para Radio Mundial (Arquitectura Hexagonal).
/// Orquesta los puertos de catálogo, audio, preferencias, difusión y traducción.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public class RadioStateService : IAsyncDisposable
{
    private readonly IRadioCatalogPort _catalogPort;
    private readonly IAudioPlayerPort _audioPort;
    private readonly IPreferencesPort _preferencesPort;
    private readonly IBroadcastPort _broadcastPort;
    private readonly ITranslationPort _translationPort;
    private DotNetObjectReference<RadioStateService>? _dotNetRef;
    private CancellationTokenSource? _cts;

    // Catálogo y Filtros Reactivos
    public List<Station> AllStations { get; private set; } = [];
    public List<Station> FilteredStations { get; private set; } = [];
    public FilterOptionsResponse FilterOptions { get; private set; } = new();

    public string SelectedContinent { get; private set; } = "Todos";
    public string SelectedCountry { get; private set; } = "Todos";
    public string SelectedState { get; private set; } = "Todos";
    public string SelectedCity { get; private set; } = "Todas";
    public string SelectedLocality { get; private set; } = "Todas";
    public string SelectedGenre { get; private set; } = "Todos";
    public string SelectedBand { get; private set; } = "TODAS";
    public string SearchQuery { get; private set; } = string.Empty;

    // Estado del Reproductor
    public Station? ActiveStation { get; private set; }
    public bool IsPlaying { get; private set; }
    public double Volume { get; private set; } = 0.8;
    public bool IsMuted { get; private set; }
    public int ListenersCount => _broadcastPort.IsConnected ? _remoteListenersCount : 1;
    private int _remoteListenersCount = 1;
    public bool IsConnected => _broadcastPort.IsConnected;
    public string ConnectionStatusText => _broadcastPort.ConnectionStatusText;
    public TrackMetadata CurrentTrack { get; private set; } = new();

    // Preferencias y Cookies
    public bool CookiesAccepted { get; private set; }
    public HashSet<string> FavoriteStationIds { get; private set; } = [];
    public string CurrentTheme { get; private set; } = "system";
    public string CurrentLanguage
    {
        get => _translationPort.CurrentLanguage;
        private set => _translationPort.CurrentLanguage = value;
    }

    public event Action? OnStateChanged;

    public RadioStateService(
        IRadioCatalogPort catalogPort,
        IAudioPlayerPort audioPort,
        IPreferencesPort preferencesPort,
        IBroadcastPort broadcastPort,
        ITranslationPort translationPort
    )
    {
        _catalogPort = catalogPort;
        _audioPort = audioPort;
        _preferencesPort = preferencesPort;
        _broadcastPort = broadcastPort;
        _translationPort = translationPort;

        // Estación predeterminada inmediata
        ActiveStation = new Station
        {
            Id = "los40-mx", Name = "Los 40 México 101.7 FM", Country = "México", CountryCode = "MX",
            State = "Ciudad de México", City = "Ciudad de México", Locality = "Cuauhtémoc", Genre = "Pop & Éxitos",
            StreamUrl = "https://playerservices.streamtheworld.com/api/livestream-redirect/LOS40_MEXICOAAC.aac",
            LogoUrl = "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
            Description = "La cadena de éxitos juveniles número uno de México.", Bitrate = "128 kbps AAC", Frequency = 101.7, Band = "FM"
        };
        AllStations = [ActiveStation];
        FilteredStations = [ActiveStation];

        _broadcastPort.OnMessageReceived += HandleBroadcastMessage;
        _broadcastPort.OnConnectionStatusChanged += (_, _) => NotifyStateChanged();
    }

    public async Task InitializeAsync()
    {
        _dotNetRef = DotNetObjectReference.Create(this);
        await _audioPort.InitializeAsync(_dotNetRef);

        await LoadPreferencesAsync();
        await _audioPort.SetVolumeAsync(Volume);

        // 1. Cargar catálogo estático para disponibilidad instantánea offline
        var seed = await _catalogPort.GetFallbackSeedAsync();
        if (seed.Count > 0)
        {
            MergeStations(seed);
            ApplyFilters();
        }

        // 2. Cargar filtros y estaciones desde backend
        var filters = await _catalogPort.GetFilterOptionsAsync();
        if (filters is not null) FilterOptions = filters;

        var backendStations = await _catalogPort.GetStationsAsync(limit: 250);
        if (backendStations.Count > 0)
        {
            MergeStations(backendStations);
            ApplyFilters();
        }

        if (ActiveStation is not null && !string.IsNullOrWhiteSpace(ActiveStation.StreamUrl))
        {
            CurrentTrack = new TrackMetadata
            {
                Title = $"En vivo por {ActiveStation.Name}",
                Artist = $"{ActiveStation.City}, {ActiveStation.Country}",
                Album = ActiveStation.Genre,
                CoverUrl = ActiveStation.LogoUrl
            };
        }

        _cts = new CancellationTokenSource();
        _ = Task.Run(() => _broadcastPort.StartAsync(_cts.Token));

        NotifyStateChanged();
    }

    #region Normalización de Texto

    public static string NormalizeText(string? text)
    {
        if (string.IsNullOrWhiteSpace(text)) return string.Empty;
        var normalized = text.Normalize(NormalizationForm.FormD);
        var sb = new StringBuilder();
        foreach (var c in normalized)
        {
            var uc = CharUnicodeInfo.GetUnicodeCategory(c);
            if (uc != UnicodeCategory.NonSpacingMark)
            {
                sb.Append(c);
            }
        }
        return sb.ToString().Normalize(NormalizationForm.FormC).Trim().ToLowerInvariant();
    }

    #endregion

    #region Traducción y Localización

    public string T(string key) => _translationPort.Translate(key);

    public async Task SetLanguageAsync(string lang)
    {
        CurrentLanguage = lang?.ToLowerInvariant() == "en" ? "en" : "es";
        await SavePreferencesAsync();
        NotifyStateChanged();
    }

    #endregion

    #region Temas y Preferencias

    public async Task SetThemeAsync(string theme)
    {
        CurrentTheme = theme switch
        {
            "light" => "light",
            "dark" => "dark",
            _ => "system"
        };
        await _preferencesPort.ApplyThemeAsync(CurrentTheme);
        await SavePreferencesAsync();
        NotifyStateChanged();
    }

    public async Task AcceptCookiesAsync()
    {
        CookiesAccepted = true;
        await SavePreferencesAsync();
        NotifyStateChanged();
    }

    private async Task SavePreferencesAsync()
    {
        var prefs = new UserPreferences
        {
            CookiesAccepted = CookiesAccepted,
            LastStationId = ActiveStation?.Id,
            Volume = Volume,
            FavoriteStationIds = [.. FavoriteStationIds],
            Theme = CurrentTheme,
            Language = CurrentLanguage
        };
        await _preferencesPort.SavePreferencesAsync(prefs);
    }

    private async Task LoadPreferencesAsync()
    {
        var prefs = await _preferencesPort.LoadPreferencesAsync();
        if (prefs is not null)
        {
            CookiesAccepted = prefs.CookiesAccepted;
            Volume = Math.Clamp(prefs.Volume, 0.0, 1.0);
            FavoriteStationIds = new HashSet<string>(prefs.FavoriteStationIds ?? []);
            if (!string.IsNullOrWhiteSpace(prefs.Theme)) CurrentTheme = prefs.Theme;
            if (!string.IsNullOrWhiteSpace(prefs.Language)) CurrentLanguage = prefs.Language;

            if (!string.IsNullOrWhiteSpace(prefs.LastStationId))
            {
                var last = AllStations.FirstOrDefault(s => s.Id == prefs.LastStationId);
                if (last is not null) ActiveStation = last;
            }
        }
        await _preferencesPort.ApplyThemeAsync(CurrentTheme);
    }

    #endregion

    #region Filtros Reactivos

    public void SetContinentFilter(string continent)
    {
        SelectedContinent = continent;
        SelectedCountry = "Todos";
        SelectedState = "Todos";
        SelectedCity = "Todas";
        SelectedLocality = "Todas";
        ApplyFilters();
        _ = FetchDynamicStationsAsync();
    }

    public void SetCountryFilter(string country)
    {
        SelectedCountry = country;
        SelectedState = "Todos";
        SelectedCity = "Todas";
        SelectedLocality = "Todas";
        ApplyFilters();
        _ = FetchDynamicStationsAsync();
    }

    public void SetStateFilter(string state)
    {
        SelectedState = state;
        SelectedCity = "Todas";
        SelectedLocality = "Todas";
        ApplyFilters();
        _ = FetchDynamicStationsAsync();
    }

    public void SetCityFilter(string city)
    {
        SelectedCity = city;
        SelectedLocality = "Todas";
        ApplyFilters();
    }

    public void SetLocalityFilter(string locality)
    {
        SelectedLocality = locality;
        ApplyFilters();
    }

    public void SetGenreFilter(string genre)
    {
        SelectedGenre = genre;
        ApplyFilters();
    }

    public void SetBandFilter(string band)
    {
        SelectedBand = string.IsNullOrWhiteSpace(band) ? "TODAS" : band.Trim().ToUpperInvariant();
        ApplyFilters();
    }

    public void SetSearchQuery(string query)
    {
        SearchQuery = query;
        ApplyFilters();
        if (query.Length > 2)
        {
            _ = FetchDynamicStationsAsync();
        }
    }

    public void ResetFilters()
    {
        SelectedContinent = "Todos";
        SelectedCountry = "Todos";
        SelectedState = "Todos";
        SelectedCity = "Todas";
        SelectedLocality = "Todas";
        SelectedGenre = "Todos";
        SelectedBand = "TODAS";
        SearchQuery = string.Empty;
        ApplyFilters();
    }

    public async Task FetchDynamicStationsAsync()
    {
        var fetched = await _catalogPort.GetStationsAsync(
            continent: SelectedContinent,
            country: SelectedCountry,
            state: SelectedState,
            band: SelectedBand,
            search: SearchQuery,
            limit: 150
        );
        if (fetched.Count > 0)
        {
            MergeStations(fetched);
            ApplyFilters();
        }
    }

    private void MergeStations(List<Station> newStations)
    {
        var existingUrls = new HashSet<string>(AllStations.Select(s => s.StreamUrl));
        foreach (var st in newStations)
        {
            if (!existingUrls.Contains(st.StreamUrl))
            {
                AllStations.Add(st);
                existingUrls.Add(st.StreamUrl);
            }
        }
    }

    public List<string> GetAvailableContinents()
    {
        var list = AllStations.Select(s => s.Continent).Where(c => !string.IsNullOrWhiteSpace(c)).Distinct().OrderBy(c => c).ToList();
        if (list.Count == 0) return ["América", "Europa", "Asia", "África", "Oceanía"];
        return list;
    }

    public List<string> GetAvailableCountries()
    {
        var query = AllStations.AsEnumerable();
        if (SelectedContinent != "Todos" && !string.IsNullOrWhiteSpace(SelectedContinent))
        {
            var normCont = NormalizeText(SelectedContinent);
            query = query.Where(s => NormalizeText(s.Continent) == normCont);
        }
        var countries = query.Select(s => s.Country).Where(c => !string.IsNullOrWhiteSpace(c)).Distinct().OrderBy(c => c).ToList();
        if (countries.Contains("México"))
        {
            countries.Remove("México");
            countries.Insert(0, "México");
        }
        return countries;
    }

    public List<string> GetAvailableStates()
    {
        var query = AllStations.AsEnumerable();
        if (SelectedContinent != "Todos" && !string.IsNullOrWhiteSpace(SelectedContinent))
        {
            var normCont = NormalizeText(SelectedContinent);
            query = query.Where(s => NormalizeText(s.Continent) == normCont);
        }
        if (SelectedCountry != "Todos" && !string.IsNullOrWhiteSpace(SelectedCountry))
        {
            var normCountry = NormalizeText(SelectedCountry);
            query = query.Where(s => NormalizeText(s.Country) == normCountry);
        }
        return query.Select(s => s.State)
                    .Where(st => !string.IsNullOrWhiteSpace(st) && st != "Nacional")
                    .Distinct()
                    .OrderBy(st => st)
                    .ToList();
    }

    public List<string> GetAvailableCities()
    {
        var query = AllStations.AsEnumerable();
        if (SelectedContinent != "Todos" && !string.IsNullOrWhiteSpace(SelectedContinent))
        {
            var normCont = NormalizeText(SelectedContinent);
            query = query.Where(s => NormalizeText(s.Continent) == normCont);
        }
        if (SelectedCountry != "Todos" && !string.IsNullOrWhiteSpace(SelectedCountry))
        {
            var normCountry = NormalizeText(SelectedCountry);
            query = query.Where(s => NormalizeText(s.Country) == normCountry);
        }
        if (SelectedState != "Todos" && !string.IsNullOrWhiteSpace(SelectedState))
        {
            var normState = NormalizeText(SelectedState);
            query = query.Where(s => NormalizeText(s.State) == normState);
        }
        return query.Select(s => s.City)
                    .Where(c => !string.IsNullOrWhiteSpace(c) && c != "Nacional")
                    .Distinct()
                    .OrderBy(c => c)
                    .ToList();
    }

    private void ApplyFilters()
    {
        var normContinent = NormalizeText(SelectedContinent);
        var normCountry = NormalizeText(SelectedCountry);
        var normState = NormalizeText(SelectedState);
        var normCity = NormalizeText(SelectedCity);
        var normLocality = NormalizeText(SelectedLocality);
        var normGenre = NormalizeText(SelectedGenre);
        var normSearch = NormalizeText(SearchQuery);

        var q = AllStations.AsEnumerable();

        if (normContinent != "todos" && !string.IsNullOrEmpty(normContinent))
        {
            q = q.Where(s => NormalizeText(s.Continent) == normContinent);
        }

        if (normCountry != "todos" && !string.IsNullOrEmpty(normCountry))
        {
            var aliases = new HashSet<string> { normCountry };
            if (normCountry is "estados unidos" or "usa" or "us" or "united states")
                aliases.UnionWith(["estados unidos", "usa", "us", "united states"]);
            else if (normCountry is "mexico" or "mx")
                aliases.UnionWith(["mexico", "mx"]);
            else if (normCountry is "espana" or "spain" or "es")
                aliases.UnionWith(["espana", "spain", "es"]);
            else if (normCountry is "reino unido" or "uk" or "gb" or "united kingdom")
                aliases.UnionWith(["reino unido", "uk", "gb", "united kingdom"]);

            q = q.Where(s =>
            {
                var sc = NormalizeText(s.Country);
                var scc = NormalizeText(s.CountryCode);
                return aliases.Any(a => sc == a || scc == a || sc.Contains(a) || a.Contains(sc));
            });
        }

        if (normState != "todos" && normState != "todas" && !string.IsNullOrEmpty(normState))
        {
            q = q.Where(s =>
            {
                var ss = NormalizeText(s.State);
                return ss == normState || ss.Contains(normState) || normState.Contains(ss);
            });
        }

        if (normCity != "todas" && !string.IsNullOrEmpty(normCity))
        {
            q = q.Where(s => NormalizeText(s.City) == normCity);
        }

        if (normLocality != "todas" && !string.IsNullOrEmpty(normLocality))
        {
            q = q.Where(s => NormalizeText(s.Locality) == normLocality);
        }

        if (normGenre != "todos" && !string.IsNullOrEmpty(normGenre))
        {
            q = q.Where(s => NormalizeText(s.Genre).Contains(normGenre));
        }

        if (SelectedBand != "TODAS" && !string.IsNullOrWhiteSpace(SelectedBand))
        {
            var bNorm = SelectedBand.ToUpperInvariant();
            q = q.Where(s =>
                string.Equals(s.Band, bNorm, StringComparison.OrdinalIgnoreCase) ||
                (bNorm == "AM" && s.Frequency > 150) ||
                (bNorm == "FM" && s.Frequency <= 108)
            );
        }

        if (!string.IsNullOrWhiteSpace(normSearch))
        {
            q = q.Where(s =>
                NormalizeText(s.Name).Contains(normSearch) ||
                NormalizeText(s.Country).Contains(normSearch) ||
                NormalizeText(s.State).Contains(normSearch) ||
                NormalizeText(s.City).Contains(normSearch) ||
                NormalizeText(s.Genre).Contains(normSearch) ||
                NormalizeText(s.Description).Contains(normSearch)
            );
        }

        FilteredStations = q.ToList();
        NotifyStateChanged();
    }

    #endregion

    #region Reproducción y Controles de Audio

    public async Task TuneStationAsync(Station station)
    {
        ActiveStation = station;
        CurrentTrack = new TrackMetadata
        {
            Title = $"En vivo por {station.Name}",
            Artist = $"{station.City}, {station.State}",
            Album = station.Genre,
            CoverUrl = station.LogoUrl
        };
        await _audioPort.PlayAsync(station.StreamUrl);
        await _audioPort.UpdateMediaMetadataAsync(station.Name, $"{station.City}, {station.State}", station.Genre, station.LogoUrl);
        await SavePreferencesAsync();
        NotifyStateChanged();
    }

    public async Task TogglePlayAsync()
    {
        if (ActiveStation is null) return;
        if (IsPlaying)
        {
            await _audioPort.PauseAsync();
            IsPlaying = false;
        }
        else
        {
            await _audioPort.PlayAsync(ActiveStation.StreamUrl);
            IsPlaying = true;
        }
        NotifyStateChanged();
    }

    public async Task TuneNextStationAsync()
    {
        if (FilteredStations.Count == 0) return;
        var idx = ActiveStation is not null ? FilteredStations.FindIndex(s => s.Id == ActiveStation.Id) : -1;
        var nextIdx = (idx + 1) % FilteredStations.Count;
        await TuneStationAsync(FilteredStations[nextIdx]);
    }

    public async Task TunePreviousStationAsync()
    {
        if (FilteredStations.Count == 0) return;
        var idx = ActiveStation is not null ? FilteredStations.FindIndex(s => s.Id == ActiveStation.Id) : -1;
        var prevIdx = idx <= 0 ? FilteredStations.Count - 1 : idx - 1;
        await TuneStationAsync(FilteredStations[prevIdx]);
    }

    public async Task SetVolumeAsync(double newVolume)
    {
        Volume = Math.Clamp(newVolume, 0.0, 1.0);
        IsMuted = Volume == 0.0;
        await _audioPort.SetVolumeAsync(Volume);
        await SavePreferencesAsync();
        NotifyStateChanged();
    }

    public async Task AdjustVolumeRelativeAsync(double delta)
    {
        await SetVolumeAsync(Volume + delta);
    }

    public async Task ToggleMuteAsync()
    {
        IsMuted = !IsMuted;
        await _audioPort.SetVolumeAsync(IsMuted ? 0.0 : Volume);
        NotifyStateChanged();
    }

    public async Task ToggleFavoriteAsync(string stationId)
    {
        if (FavoriteStationIds.Contains(stationId))
            FavoriteStationIds.Remove(stationId);
        else
            FavoriteStationIds.Add(stationId);

        await SavePreferencesAsync();
        NotifyStateChanged();
    }

    #endregion

    #region Invocaciones desde JavaScript (JSInvokable)

    [JSInvokable]
    public void OnNativeAudioPlay()
    {
        IsPlaying = true;
        NotifyStateChanged();
    }

    [JSInvokable]
    public void OnNativeAudioPause()
    {
        IsPlaying = false;
        NotifyStateChanged();
    }

    [JSInvokable]
    public void OnNativeAudioError(string errorMessage)
    {
        Console.WriteLine($"[AudioBridge] Error: {errorMessage}");
        NotifyStateChanged();
    }

    #endregion

    private void HandleBroadcastMessage(RadioBroadcastMessage msg)
    {
        if (msg.ListenersCount > 0)
        {
            _remoteListenersCount = msg.ListenersCount;
        }
        if (msg.Track is not null)
        {
            CurrentTrack = msg.Track;
        }
        NotifyStateChanged();
    }

    private void NotifyStateChanged() => OnStateChanged?.Invoke();

    public async ValueTask DisposeAsync()
    {
        _cts?.Cancel();
        _cts?.Dispose();
        await _broadcastPort.DisposeAsync();
        _dotNetRef?.Dispose();
    }
}

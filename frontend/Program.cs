using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using frontend;
using frontend.Application.Ports;
using frontend.Application.Services;
using frontend.Infrastructure.Adapters;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

builder.Services.AddScoped(sp => new HttpClient { BaseAddress = new Uri(builder.HostEnvironment.BaseAddress) });

// =========================================================================
// Inyección de Dependencias - Arquitectura Hexagonal (Ports & Adapters)
// Autor: Hugo Francisco Luis Inclan (c) 2026
// =========================================================================
builder.Services.AddScoped<IRadioCatalogPort, HttpRadioCatalogAdapter>();
builder.Services.AddScoped<IAudioPlayerPort, JsAudioPlayerAdapter>();
builder.Services.AddScoped<IPreferencesPort, JsPreferencesAdapter>();
builder.Services.AddScoped<IBroadcastPort, ClientWebSocketAdapter>();
builder.Services.AddScoped<ITranslationPort, DictionaryTranslationAdapter>();

// Servicio de Aplicación Coordinador (Application Service)
builder.Services.AddScoped<RadioStateService>();

await builder.Build().RunAsync();

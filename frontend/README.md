# 📻 Radio Mundial — Frontend Client (Blazor WebAssembly .NET 10)

> **Autor:** Hugo Francisco Luis Inclan  
> **Copyright (c) 2026 Hugo Francisco Luis Inclan.** Todos los derechos reservados.  
> **Licencia:** MIT License.  
> **Tecnología:** C# / .NET 10.0 Blazor WebAssembly (Single Page Application).  
> **Enfoque Arquitectónico:** Clean Architecture (Hexagonal Ports & Adapters) con Desacoplamiento Total.

---

## 🏛️ Estructura y Arquitectura Hexagonal

El cliente frontend implementa Clean Architecture para desacoplar por completo la lógica de negocio, el control de audio y la presentación en pantalla:

```
frontend/
├── Domain/                                # Capa 1: Entidades y Modelos de Negocio
│   └── Entities/
│       ├── Station.cs                     # Modelo inmutable de emisora
│       ├── TrackMetadata.cs               # Metadatos del tema y carátula
│       └── FilterOptionsResponse.cs       # Estructura de opciones de filtrado
│
├── Application/                           # Capa 2: Puertos Abstractos y Orquestación
│   ├── Ports/
│   │   ├── IRadioCatalogPort.cs           # Puerto para obtención de emisoras
│   │   ├── IAudioPlayerPort.cs            # Puerto para control de reproducción
│   │   ├── IRadioBroadcastPort.cs         # Puerto para conexión WebSocket
│   │   ├── IPreferencesPort.cs            # Puerto para persistencia de tema y favoritos
│   │   └── ITranslationPort.cs            # Puerto de internacionalización (ES/EN)
│   └── Services/
│       └── RadioStateService.cs           # Coordinador central y reactivo de estado (Singleton)
│
├── Infrastructure/                        # Capa 3: Adaptadores de Entrada/Salida
│   └── Adapters/
│       ├── HttpRadioCatalogAdapter.cs     # Cliente HTTP con fallback a semilla local
│       ├── JsAudioPlayerAdapter.cs        # Puente con HTML5 Audio y MediaSession API
│       ├── ClientWebSocketAdapter.cs      # Conexión WebSocket resiliente con auto-reconexión
│       ├── JsPreferencesAdapter.cs        # Almacenamiento en LocalStorage y Cookies
│       └── DictionaryTranslationAdapter.cs# Diccionario reactivo bilingüe español/inglés
│
├── Components/                            # Componentes Reutilizables de Presentación
│   ├── RetroRadio.razor                   # Radio Vintage "Café Viejo" con dial analógico y aguja física
│   ├── RadioPlayer.razor                  # Barra de reproducción persistente inferior
│   └── CookieConsent.razor                # Banner de privacidad y consentimiento
│
├── Layout/                                # Disposición Estructural de Página
│   ├── MainLayout.razor                   # Barra superior con nuevo logotipo y estado global
│   └── MainLayout.razor.css               # Estilos de encabezado y dock
│
├── Pages/                                 # Vistas Principales
│   ├── Home.razor                         # Cockpit de sintonización y consola de filtros
│   └── Home.razor.css                     # Estilos de cuadrícula y tarjetas retro
│
├── wwwroot/                               # Activos Estáticos Listos para Producción
│   ├── img/                               # Nuevos logotipos oficiales de alta resolución
│   │   ├── radio-mundial-icono.svg        # Ícono vectorial escalable SVG (radio vintage)
│   │   ├── radio-mundial-icono.png        # Ícono PNG 1024x1024 de alta resolución
│   │   └── radio-mundial-logo-horizontal.png # Banner horizontal 2100x660 para OpenGraph
│   ├── css/                               # Sistema de diseño "Café Viejo" y Bootstrap
│   ├── js/radioAudio.js                   # Motor de audio nativo y MediaSession API
│   ├── sample-data/stations.json          # Semilla local desconectada de 3,575 emisoras
│   ├── sitemap.xml                        # Mapa de sitio optimizado para Google y Bing
│   ├── robots.txt                         # Directivas de indexación SEO prioritarias
│   └── index.html                         # Punto de entrada HTML5 con JSON-LD Schema.org
│
├── Program.cs                             # Registro del contenedor de dependencias (IoC)
└── frontend.csproj                        # Proyecto .NET 10 WebAssembly
```

---

## 🎨 Sistema de Diseño Vintage "Café Viejo"

* **Cero Colores Neón:** Inspirado en receptores Hi-Fi clásicos de válvulas termoiónicas y transistores analógicos de los años 70.
* **Paleta de Materiales Nobles:**
  * Madera Nogal / Caoba Profundo (`#442413` a `#170904`).
  * Bisel de Latón Envejecido (`#c5a059` a `#8c6721`).
  * Rejilla de Lino y Arpillera Acústica (`#dfd2be` a `#cebd9f`).
  * Aguja del Dial Carmesí Físico (`#d63a2a`).
  * Marfil Cálido / Pergamino para el Modo Claro (`#f4ecdf`).
* **Soporte de Tema:** `🌙 Oscuro`, `☀️ Claro` y `💻 Sistema` (sincronizado con las preferencias del sistema operativo mediante `prefers-color-scheme`).
* **Soporte Bilingüe:** Español (`ES`) e Inglés (`EN`) con cambio instantáneo en caliente sin recargar la página.

---

## 🚀 Paginación Virtual y Rendimiento 60 FPS

Al manejar un catálogo de **3,575 estaciones**, el renderizado directo saturaría el DOM del navegador. Se implementó una arquitectura de **Paginación Virtual Progresiva**:
* Lote inicial de **48 estaciones** renderizado en menos de 16 ms.
* Botón de carga progresiva: **"➕ Cargar más emisoras"**.
* El árbol DOM se mantiene ligero (< 600 nodos), logrando un desplazamiento a **60 cuadros por segundo (FPS)** incluso en teléfonos móviles de gama de entrada.

---

## 🔍 Optimización SEO para Primera Plana en Motores de Búsqueda

Configurado para posicionar en primer lugar ante las búsquedas más competidas:
1. **Title & Meta Tags:** Enfocados en términos de alto volumen: *"radio"*, *"radio mundial"*, *"radio en vivo"*, *"radio online gratis"*, *"emisoras fm y am"*.
2. **JSON-LD Schema.org Completo:**
   * Esquema `WebSite` con `SearchAction` (cuadro de búsqueda de Google integrado directamente en las SERPs).
   * Esquema `WebApplication` (Categoría multimedia, compatible con navegadores modernos).
   * Esquema `Organization` con fundador **Hugo Francisco Luis Inclan**.
   * Esquemas `BroadcastService` para emisoras locales destacadas (Matías Romero 90.5 FM, Tapachula Chiapas, etc.).
3. **HTML5 MediaSession API:** Control nativo de reproducción en pantallas de bloqueo y centros de control multimedia de Android, iOS, Windows y macOS.
4. **PWA (Progressive Web App):** Instalable en teléfonos móviles y ordenadores como una aplicación nativa.

---

## 🛠️ Compilación y Ejecución Local

```bash
# 1. Restaurar y compilar
dotnet build

# 2. Ejecutar en modo desarrollo
dotnet run
```
La aplicación iniciará en `http://localhost:5296`.

### Publicación para Producción:
```bash
dotnet publish -c Release -o output
# Los archivos estáticos listos para subir a Cloudflare Pages se encuentran en output/wwwroot
```

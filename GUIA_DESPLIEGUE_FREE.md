# 🚀 Guía Maestra de Despliegue en Servicios 100% Gratuitos

## Radio Mundial — Arquitectura Hexagonal Hi-Fi Transistor Streaming

---

## 📌 ÍNDICE RÁPIDO

1. [¿Qué se sube a Git? ¿Todo junto o por separado?](#1-qué-se-sube-a-git-todo-junto-o-por-separado)
2. [Matriz de Configuración: ¿Qué se configura, en qué archivo y dónde?](#2-matriz-de-configuración-qué-se-configura-en-qué-archivo-y-dónde)
3. [Paso 1: Subir el Proyecto a GitHub](#paso-1-subir-el-proyecto-a-github)
4. [Paso 2: Desplegar el Backend en Render.com (100% Gratis)](#paso-2-desplegar-el-backend-en-rendercom-100-gratis)
5. [Paso 3: Conectar el Frontend con tu Backend en Producción](#paso-3-conectar-el-frontend-con-tu-backend-en-producción)
6. [Paso 4: Desplegar el Frontend en Cloudflare Pages (100% Gratis)](#paso-4-desplegar-el-frontend-en-cloudflare-pages-100-gratis)
7. [Paso 5: Mantener el Backend Despierto 24/7 (Cero Hibernación)](#paso-5-mantener-el-backend-despierto-247-cero-hibernación)
8. [Paso 6: Configurar Dominio Personalizado y SSL Gratis](#paso-6-configurar-dominio-personalizado-y-ssl-gratis)
9. [Paso 7: SEO para Aparecer en Primeros Resultados de Búsqueda](#paso-7-seo-para-aparecer-en-primeros-resultados-de-búsqueda)
10. [Diagnóstico de Problemas Comunes (Troubleshooting)](#diagnóstico-de-problemas-comunes)

---

## 1. ¿Qué se sube a Git? ¿Todo junto o por separado?

### 🏆 Opción Recomendada: Todo en UN solo repositorio (Monorepo)

**Recomendación profesional:** Sube **todo el proyecto junto en un solo repositorio** en GitHub.

```
Radio-Mundial/ (Repositorio Único en GitHub)
├── backend/            --> Render compila únicamente esta carpeta (Root Dir: backend)
├── frontend/           --> Cloudflare Pages compila únicamente esta carpeta (Root Dir: frontend)
├── img/                --> Logos y recursos gráficos
├── .gitignore          --> Filtra ejecutables y archivos temporales
├── README.md           --> Documentación general
└── GUIA_DESPLIEGUE_FREE.md
```

#### ¿Por qué es la mejor opción?

1. **Soporte Nativo de Monorepo:** Tanto **Render** como **Cloudflare Pages** tienen la casilla **`Root Directory`**. Le indicas a Render que su raíz es `backend`, y a Cloudflare que su raíz es `frontend`. Ambos leen del mismo repositorio sin estorbarse.
2. **Sincronización Atómica:** Cuando agregas nuevas emisoras, un solo `git commit` y `git push` actualiza frontend y backend simultáneamente.
3. **Cero Mantenimiento Doble:** No tienes que clonar, configurar ni autenticar dos repositorios diferentes.

---

### 📦 ¿Qué archivos se suben y cuáles se ignoran?

El archivo `.gitignore` ya está preconfigurado en la raíz del proyecto para protegerte:

| Directorio / Archivo                                                    |    ¿Se sube a Git?    | Razón                                       |
| :---------------------------------------------------------------------- | :---------------------: | :------------------------------------------- |
| `backend/main.py`, `domain/`, `application/`, `infrastructure/` |      **SÍ**      | Código fuente del servidor FastAPI          |
| `backend/data/seed_stations.json`                                     |      **SÍ**      | Catálogo mundial con las 18,300+ estaciones |
| `backend/requirements.txt`, `Dockerfile`                            |      **SÍ**      | Instrucciones de compilación para la nube   |
| `backend/venv/`, `__pycache__/`, `.env`                           | **NO (Ignorado)** | Binarios locales y claves privadas           |
| `frontend/Pages/`, `Components/`, `Layout/`, `Domain/`          |      **SÍ**      | Código fuente Blazor WASM C#                |
| `frontend/wwwroot/` (css, index.html, sample-data)                    |      **SÍ**      | Recursos estáticos y catálogo offline      |
| `frontend/bin/`, `frontend/obj/`                                    | **NO (Ignorado)** | Archivos compilados temporales de .NET       |
| `img/`                                                                |      **SÍ**      | Logos vectoriales e íconos de la radio      |

---

### (Alternativa) ¿Y si prefieres separarlo en dos repositorios?

Si por política o preferencia personal deseas tener 2 repositorios en GitHub (`radio-mundial-backend` y `radio-mundial-frontend`), puedes hacerlo con los siguientes comandos:

```bash
# Para el backend:
cd backend
git init
git remote add origin https://github.com/TU_USUARIO/radio-mundial-backend.git
git add . && git commit -m "feat: backend api"
git push -u origin master

# Para el frontend:
cd ../frontend
git init
git remote add origin https://github.com/TU_USUARIO/radio-mundial-frontend.git
git add . && git commit -m "feat: frontend blazor wasm"
git push -u origin master
```

*(Nota: En Render y Cloudflare Pages simplemente conectarías cada repositorio por separado y dejarías `Root Directory` en blanco).*

---

## 2. Matriz de Configuración: ¿Qué se configura, en qué archivo y dónde?

Para evitar confusiones, aquí tienes la tabla exacta de configuraciones:

| Qué Configurar                          | En Qué Archivo / Pantalla                       | Qué Valor Poner en Producción                                             |
| :--------------------------------------- | :----------------------------------------------- | :-------------------------------------------------------------------------- |
| **URL de la API en Frontend**      | `frontend/wwwroot/appsettings.json`            | `"BackendHttpUrl": "https://radio-mundial-api.onrender.com"`              |
| **URL WebSocket en Frontend**      | `frontend/wwwroot/appsettings.json`            | `"BackendWsUrl": "wss://radio-mundial-api.onrender.com/ws"`               |
| **Orígenes Permitidos (CORS)**    | `backend/infrastructure/config/settings.py`    | `"https://radio-mundial.pages.dev"`, `"https://tudominio.com"`, `"*"` |
| **Directorio Raíz en Render**     | Panel Render -> Settings -> Root Directory       | `backend`                                                                 |
| **Comando Build en Render**        | Panel Render -> Settings -> Build Command        | `pip install -r requirements.txt`                                         |
| **Comando Start en Render**        | Panel Render -> Settings -> Start Command        | `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2`                |
| **Directorio Raíz en Cloudflare** | Panel Cloudflare -> Settings -> Root Directory   | `frontend`                                                                |
| **Comando Build en Cloudflare**    | Panel Cloudflare -> Settings -> Build Command    | `dotnet publish -c Release -o output`                                     |
| **Directorio Salida Cloudflare**   | Panel Cloudflare -> Settings -> Output Directory | `output/wwwroot`                                                          |

---

## PASO 1: Subir el Proyecto a GitHub

1. Abre tu terminal en la carpeta principal del proyecto:

```bash
cd /home/productdeath/Documentos/UNIVERSAL/PERSONAL/Radio-Mundial
```

2. Crea tu repositorio en [github.com/new](https://github.com/new) con el nombre `Radio-Mundial` (puede ser público o privado).
3. Conecta y sube tu código:

```bash
git add -A
git commit -m "feat: Radio Mundial v6.0 - 18,300+ emisoras, paginado y diseno vintage"
git branch -M master
git remote add origin https://github.com/TU_USUARIO/Radio-Mundial.git
git push -u origin master
```

---

## PASO 2: Desplegar el Backend en Render.com (100% Gratis)

En la pantalla que tienes abierta en Render (`New Web Service`), llena cada campo exactamente de la siguiente manera:

### 2.1 Campos de la Pantalla Actualizada de Render (Paso a Paso):

1. **Name:**  
   Escribe: `radio-mundial-api` (o el nombre que prefieras).

2. **Language:**  
   Render detecta automáticamente **`Docker`** porque el proyecto incluye un Dockerfile multi-stage optimizado para producción.  
   * **Opción A (Recomendada con Docker):** Déjalo en `Docker`. El Dockerfile ya está 100% configurado con Python 3.11 y Uvicorn.
   * **Opción B (Python Nativo):** Si prefieres cambiar el selector a `Python 3`, Render te pedirá dos comandos:
     * *Build Command:* `pip install -r requirements.txt`
     * *Start Command:* `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2`

3. **Branch:**  
   Selecciona tu rama activa: **`main`**

4. **Region:**  
   Déjalo en: **`Oregon (US West)`** (o la región más cercana a ti).

5. **Root Directory (⚠️ CRÍTICO - NO DEJAR VACÍO):**  
   Escribe: **`backend`**  
   *(Esto le indica a Render que compile únicamente la subcarpeta del backend dentro de tu repositorio monorepo).*

6. **Dockerfile Path:**  
   Déjalo como viene por defecto: **`./Dockerfile`**  
   *(Al haber colocado `backend` en Root Directory, Render buscará el Dockerfile directamente dentro de esa carpeta).*

7. **Compute Plan (⚠️ ¡IMPORTANTE PARA QUE SEA $0.00!):**  
   Render preselecciona por defecto la opción de pago de `$7 / month`.  
   * **Haz clic sobre la opción gratuita:** **`$0 / month - Free (0.1 CPU, 512 MB RAM)`**.  
   * Debe quedar marcada la tarjeta de **$0 Free** para que no te genere ningún cobro.

8. **Environment Variables (Variables de Entorno):**  
   Haz clic en el botón **"Add Environment Variable"** y añade las siguientes filas (Key y Value):

   | Key (Clave) | Value (Valor) | Propósito |
   | :--- | :--- | :--- |
   | `PYTHONUNBUFFERED` | `1` | Emite los logs de FastAPI de inmediato en la consola de Render |
   | `ENABLE_WARMUP` | `true` | Carga las 18,331 emisoras en memoria RAM al iniciar |
   | `ALLOWED_ORIGINS` | `["*"]` | Habilita CORS para conectar con tu frontend de Cloudflare |
   | `NOTIFICATION_EMAIL` | `hugofranciscoluisinclan@gmail.com` | Correo donde recibirás los reportes del buzón |

9. **Desplegar:**  
   Haz clic en el botón inferior **"Deploy web service"**.

10. **Resultado:**  
    Render comenzará a construir tu contenedor Docker y en aproximadamente 2 a 3 minutos verás el indicador en verde **`Live`**.  
    En la parte superior izquierda de la pantalla de Render aparecerá tu URL pública segura:  
    👉 **`https://radio-mundial-api.onrender.com`**

---

## PASO 3: Conectar el Frontend con tu Backend en Producción

Una vez que tengas la URL de Render, asegúrate de que el frontend apunte a ella:

1. Abre [`frontend/wwwroot/appsettings.json`](file:///home/productdeath/Documentos/UNIVERSAL/PERSONAL/Radio-Mundial/frontend/wwwroot/appsettings.json):

```json
{
  "BackendHttpUrl": "https://radio-mundial-api.onrender.com",
  "BackendWsUrl": "wss://radio-mundial-api.onrender.com/ws"
}
```

*(Si tu servicio en Render tiene otro nombre, reemplázalo con tu URL).*

2. Guarda y confirma el cambio en git:

```bash
git add frontend/wwwroot/appsettings.json
git commit -m "config: conectar frontend con backend de render"
git push origin master
```

---

## PASO 4: Desplegar el Frontend en Cloudflare Pages (100% Gratis)

Cloudflare Pages es la red perimetral más rápida del mundo, con CDN Anycast en más de 300 ciudades, **ancho de banda ilimitado y costo $0.00**.

### Método Recomendado: Despliegue Automático desde GitHub

1. Inicia sesión en [dash.cloudflare.com](https://dash.cloudflare.com/).
2. En el menú lateral izquierdo, haz clic en **Compute (Workers) > Workers & Pages**.
3. Haz clic en **Create application** y ve a la pestaña **Pages** -> **Connect to Git**.
4. Selecciona tu cuenta de GitHub y elige el repositorio `Radio-Mundial`.
5. En la pantalla **Set up builds and deployments**, configura:
   * **Project name:** `radio-mundial`
   * **Production branch:** `master`
   * **Framework preset:** `None`
   * **Root directory:** `frontend` ⚠️ *(Indica que el frontend está en esa subcarpeta)*
   * **Build command:**
     ```bash
     dotnet publish -c Release -o output
     ```
   * **Build output directory:** `output/wwwroot`
6. En **Environment variables (advanced)**, añade:
   * `DOTNET_CLI_TELEMETRY_OPTOUT` = `1`
7. Haz clic en **"Save and Deploy"**.

En 60 segundos tu sitio web estará disponible mundialmente en:
👉 **`https://radio-mundial.pages.dev`**

---

### Método Alternativo: Despliegue Inmediato por Terminal (Wrangler CLI)

Si prefieres compilar en tu máquina y subirlo en 15 segundos sin configurar el builder de Cloudflare:

```bash
# 1. Compilar frontend en modo producción
cd frontend
dotnet publish -c Release -o dist

# 2. Publicar directamente a Cloudflare Pages
npx wrangler pages deploy dist/wwwroot --project-name radio-mundial
```

---

## PASO 5: Mantener el Backend Despierto 24/7 (Cero Hibernación)

Los servidores gratuitos de Render entran en suspensión tras 15 minutos de inactividad. Para que tu radio responda al instante en todo momento:

1. Ve a [cron-job.org](https://cron-job.org/) (servicio gratuito de monitoreo).
2. Crea una cuenta gratuita y haz clic en **"Create Cronjob"**.
3. Configura:
   * **Title:** `KeepAlive Radio Mundial`
   * **URL:** `https://radio-mundial-api.onrender.com/api/health`
   * **Schedule:** Cada **10 minutos** (Every 10 minutes).
4. Haz clic en **Save**.

> [!TIP]
> El endpoint `/api/health` responde en menos de 3 milisegundos con `{"status":"ok"}`. Este ping ligero mantendrá el catálogo en memoria RAM 100% caliente sin consumir cuotas.

---

## PASO 6: Configurar Dominio Personalizado y SSL Gratis

Si compraste o tienes un dominio propio (ejemplo: `radiomundial.fm`, `radiomundial.com` o `radiomundial.org`):

1. En el panel de **Cloudflare Pages**, entra a tu proyecto `radio-mundial`.
2. Ve a la pestaña **Custom domains** y haz clic en **Set up a custom domain**.
3. Escribe tu dominio (ej. `radiomundial.fm`).
4. Si tu dominio está gestionado en Cloudflare, se configurará con 1 solo clic. Si está en otro registrador (Namecheap, GoDaddy, Hostinger), añade el registro CNAME que Cloudflare te indique:
   ```
   CNAME  @  radio-mundial.pages.dev
   ```
5. Cloudflare generará automáticamente tu certificado **SSL/TLS universal con candado verde** y renovación automática gratuita.

---

## PASO 7: SEO para Aparecer en Primeros Resultados de Búsqueda

Radio Mundial ya incluye las etiquetas meta OpenGraph, Twitter Cards, manifiesto PWA y datos estructurados JSON-LD Schema.org (`BroadcastService` y `WebApplication`).

Para indexar de inmediato en los motores de búsqueda:

1. **Google Search Console ([search.google.com/search-console](https://search.google.com/search-console)):**
   * Agrega tu propiedad (ej. `https://radio-mundial.pages.dev` o tu dominio personalizado).
   * En el menú lateral, haz clic en **Sitemaps**.
   * Envía: `sitemap.xml`.
   * En la barra superior de **Inspección de URLs**, pega tu dominio y haz clic en **"Solicitar indexación"**.
2. **Bing Webmaster Tools ([bing.com/webmasters](https://www.bing.com/webmasters)):**
   * Importa la verificación desde Google Search Console con un solo clic.
   * Envía igualmente tu `sitemap.xml`.

---

## Diagnóstico de Problemas Comunes

### 1. Error de CORS al consultar la API

* **Síntoma:** En la consola del navegador aparece: `Access-Control-Allow-Origin missing`.
* **Solución:** Verifica que en Render la variable de entorno `ALLOWED_ORIGINS` contenga `["*"]` o incluya exactamente la URL de tu frontend: `https://radio-mundial.pages.dev`.

### 2. Error 404 al recargar una ruta en Blazor WASM

* **Síntoma:** Al entrar directo a una subpágina aparece `404 Not Found` de Cloudflare.
* **Solución:** El archivo [`frontend/wwwroot/404.html`](file:///home/productdeath/Documentos/UNIVERSAL/PERSONAL/Radio-Mundial/frontend/wwwroot/404.html) ya está incluido en el proyecto para redirigir automáticamente todas las rutas a `index.html` sin recargar la aplicación.

### 3. El audio no reproduce en algunos navegadores

* **Causa:** Algunos navegadores bloquean la reproducción automática (*autoplay*) si el usuario no ha interactuado antes con la pantalla.
* **Solución:** Radio Mundial requiere que el oyente haga clic en el botón de encendido o en cualquier perilla/tarjeta para iniciar el flujo de audio con permisos del navegador.

---

## 📊 Arquitectura de Costos Final

| Componente                           | Proveedor                  | Nivel de Servicio                          |       Costo Mensual       |
| :----------------------------------- | :------------------------- | :----------------------------------------- | :-----------------------: |
| **Alojamiento Frontend WASM**  | Cloudflare Pages           | Edge Global Anycast (300+ ciudades)        |      **$0.00**      |
| **Ancho de Banda Web**         | Cloudflare                 | Ilimitado                                  |      **$0.00**      |
| **Servidor API & WebSocket**   | Render.com                 | Free Web Service (512 MB RAM)              |      **$0.00**      |
| **Catálogo de Estaciones**    | In-Memory JSON             | 18,331 estaciones precargadas              |      **$0.00**      |
| **Certificados SSL/TLS HTTPS** | Cloudflare / Let's Encrypt | Renovación automática de por vida        |      **$0.00**      |
| **Ping Keep-Alive 24/7**       | Cron-Job.org               | 1 petición cada 10 min                    |      **$0.00**      |
| **Streaming de Audio en Vivo** | CDN de las emisoras        | Tráfico directo al oyente                 |      **$0.00**      |
| **TOTAL**                      |                            | **Nivel de Producción Profesional** | **$0.00 USD / mes** |

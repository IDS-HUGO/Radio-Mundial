# ==============================================================================
# Dockerfile Multi-Stage para Radio Mundial Frontend (Blazor WebAssembly)
# Autor: Hugo Francisco Luis Inclan (c) 2026
# ==============================================================================

# --- Etapa 1: Compilación SDK ---
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY frontend.csproj .
RUN dotnet restore frontend.csproj

COPY . .
RUN dotnet publish frontend.csproj -c Release -o /app/publish /p:UseAppHost=false

# --- Etapa 2: Servidor Web Nginx Alpine de Alta Velocidad ---
FROM nginx:alpine AS final
WORKDIR /usr/share/nginx/html

# Copiar archivos estáticos publicados
COPY --from=build /app/publish/wwwroot .
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

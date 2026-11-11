# ==============================================================================
# Dockerfile Multi-Stage Optimizado para Radio-Mundial Backend
# ==============================================================================

# --- Etapa 1: Builder ---
FROM python:3.11-slim AS builder

WORKDIR /build

# Instalar dependencias del sistema mínimas requeridas para compilar ruedas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Etapa 2: Imagen Final de Producción ---
FROM python:3.11-slim AS runner

# Variables de entorno para Python en contenedores
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    PORT=8000

# Crear usuario sin privilegios por seguridad (Non-Root User)
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m -s /bin/bash appuser

WORKDIR /app

# Copiar dependencias instaladas desde el builder
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código fuente y arquitectura hexagonal
COPY main.py .
COPY domain/ ./domain/
COPY application/ ./application/
COPY infrastructure/ ./infrastructure/
COPY data/ ./data/

# Asignar permisos al usuario no root
RUN chown -R appuser:appgroup /app /home/appuser/.local

USER appuser

EXPOSE 8000

# Healthcheck nativo sin depender de curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando de arranque con workers asíncronos en Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]

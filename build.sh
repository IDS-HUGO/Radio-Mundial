#!/usr/bin/env bash
set -e

echo "=== Compilando Radio Mundial Frontend ==="

if ! command -v dotnet &> /dev/null; then
    echo "Instalando .NET SDK 10.0 en el contenedor..."
    curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel 10.0 -InstallDir "$HOME/.dotnet"
    export PATH="$HOME/.dotnet:$PATH"
    export DOTNET_ROOT="$HOME/.dotnet"
fi

echo "Version de .NET:"
dotnet --version

echo "Limpiando y ejecutando dotnet publish..."
rm -rf frontend/dist
dotnet publish frontend/frontend.csproj -c Release -o frontend/dist

echo "=== Compilacion completada con exito ==="

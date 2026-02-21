#!/bin/bash
# Startup script para Render

echo "🚀 Iniciando Stremio Balandro Addon..."

# Variables de entorno
export PORT=${PORT:-8000}

# Ejecutar servidor
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info

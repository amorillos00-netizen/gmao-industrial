#!/usr/bin/env bash
# ========================================================================
# GMAO Industrial Pro - Script de arranque para Servidores Linux / Unix
# ========================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "========================================================================"
echo "          INICIANDO GMAO INDUSTRIAL PRO (CMMS ENTERPRISE)               "
echo "========================================================================"

# Verificar entorno virtual o python3
if [ -d "venv" ]; then
    echo "Activando entorno virtual venv..."
    source venv/bin/activate
fi

python3 run.py --host 0.0.0.0 --port 8000

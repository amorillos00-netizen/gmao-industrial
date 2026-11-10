"""
GMAO Industrial Pro - Configuración Global
Estándar de arquitectura de software para aplicaciones industriales de alta disponibilidad.
"""
from pathlib import Path
import os

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = APP_DIR / "static"
UPLOADS_DIR = DATA_DIR / "uploads"

# Asegurar existencia de directorios operativos
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Base de datos
DB_PATH = DATA_DIR / "gmao_enterprise.db"
JSON_BACKUP_PATH = DATA_DIR / "gmao_database.json"

# Configuración del servidor
SERVER_HOST = os.getenv("HOST", os.getenv("GMAO_HOST", "0.0.0.0"))
SERVER_PORT = int(os.getenv("PORT", os.getenv("GMAO_PORT", "8000")))
DEBUG = os.getenv("GMAO_DEBUG", "False").lower() in ("true", "1", "t")

# Parámetros de confiabilidad industrial
DEFAULT_MONTHLY_HOURS = 720.0  # Base mensual estándar para cálculo de disponibilidad
AVAILABILITY_TARGET_PCT = 95.0 # Meta SMRP clase mundial

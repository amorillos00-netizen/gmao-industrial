# -*- coding: utf-8 -*-
"""
Script de generación del Frontend SPA Monolítico v3.3.0
Empresa: SALTYSNACK TUYERO C.A. - Departamento de Mantenimiento e Infraestructura
Implementación completa de los 11 requerimientos industriales y corporativos.
"""
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_INDEX = BASE_DIR / "app" / "static" / "index.html"
ROOT_INDEX = BASE_DIR / "index.html"

# Vamos a generar index.html por secciones modulares para máxima calidad y robustez.
print("Generando index.html actualizado...")

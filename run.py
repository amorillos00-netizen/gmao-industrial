#!/usr/bin/env python3
"""
GMAO Industrial Pro - Launcher Universal y Servidor Local
Ejecuta la plataforma en producción o desarrollo local con detección automática de IP de red.

Uso:
    python run.py [--port 8000] [--host 0.0.0.0] [--reload]
"""
import sys
import os
import socket
import argparse
from pathlib import Path

# Agregar raíz al PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.config import SERVER_HOST, SERVER_PORT, DEBUG
from app.database import init_db

def get_local_ip() -> str:
    """Detecta la dirección IP de la interfaz de red local (LAN/Wi-Fi de planta)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No envía paquetes reales, solo resuelve la interfaz activa
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def print_banner(host: str, port: int, local_ip: str):
    print("=" * 72)
    print("       [*] GMAO INDUSTRIAL PRO (CMMS ENTERPRISE v3.3)")
    print("       SALTYSNACK TUYERO C.A. - Confiabilidad y Mantenimiento")
    print("       Estandares SMRP / ISO 14224 / ISO 55000")
    print("=" * 72)
    print(f"  [+] Acceso Local (esta maquina):   http://localhost:{port}")
    if host in ("0.0.0.0", "::"):
        print(f"  [+] Acceso Movil / Red de Planta: http://{local_ip}:{port}")
    print(f"  [+] Documentacion API Interactiva: http://localhost:{port}/api/docs")
    print(f"  [+] Base de Datos Persistente:    data/gmao_enterprise.db (SQLite WAL)")
    print("-" * 72)
    print("  Usuarios productivos autorizados:")
    print("    - Gerente / Jefe de Mantenimiento: admin / 1234")
    print("    - Encargada de Compras:           compras1 / 1234")
    print("    - Tecnico Electromecanico:        tecnico1 / 1234")
    print("    - Tecnico Instrumentista:         tecnico2 / 1234")
    print("    - Solicitante de Planta:          solicitante1 / 1234")
    print("    - Jefe SSL (Seguridad y Salud):   jefessl / 1234")
    print("=" * 72)
    print("  Presione CTRL + C para detener el servidor de manera segura.")
    print("=" * 72)
    print()


def free_port(port: int):
    """Detecta y libera automáticamente el puerto si está ocupado por un proceso previo o zombie."""
    import socket
    import subprocess
    import time
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', port))
        s.close()
        return  # Puerto libre
    except OSError:
        pass  # Puerto en uso, proceder a liberar

    print(f"[!] Puerto {port} en uso. Liberando proceso previo para arranque limpio...")
    try:
        if sys.platform == "win32":
            cmd = f'powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique"'
            output = subprocess.check_output(cmd, shell=True, text=True).strip()
            my_pid = os.getpid()
            for line in output.splitlines():
                pid_str = line.strip()
                if pid_str.isdigit() and int(pid_str) != my_pid:
                    subprocess.run(f"taskkill /F /PID {pid_str}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        else:
            subprocess.run(f"fuser -k {port}/tcp", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
    except Exception as e:
        print(f"[!] Aviso al liberar puerto: {e}")

def run():
    parser = argparse.ArgumentParser(description="GMAO Industrial Pro Server")
    parser.add_argument("--host", default=SERVER_HOST, help="Interfaz de red (0.0.0.0 para todas)")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help="Puerto de escucha (default: 8000)")
    parser.add_argument("--reload", action="store_true", default=DEBUG, help="Recarga en caliente para desarrollo")
    args = parser.parse_args()

    # Inicializar Base de Datos Relacional y Tablas
    print("[1/2] Inicializando esquema de base de datos relacional...")
    free_port(args.port)
    init_db()
    print("      [OK] Tablas verificadas y datos maestros cargados.")

    local_ip = get_local_ip()
    print_banner(args.host, args.port, local_ip)

    # Iniciar con Uvicorn (FastAPI)
    try:
        import uvicorn
        uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)
    except ImportError:
        print("Uvicorn no disponible, iniciando servidor estándar alternativo...")
        from http.server import HTTPServer
        from server import GMAORequestHandler
        server = HTTPServer((args.host, args.port), GMAORequestHandler)
        server.serve_forever()

if __name__ == "__main__":
    run()

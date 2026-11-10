#!/usr/bin/env python3
"""
GMAO Industrial Pro - Servidor Autónomo en Python
No requiere instalar dependencias adicionales (usa la librería estándar de Python 3).
Permite servir el frontend web y sincronizar la base de datos JSON en tiempo real.

Uso:
    python server.py [puerto]
Ejemplo:
    python server.py 8080
"""

import os
import sys
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gmao_database.json')

class GMAORequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Habilitar CORS y evitar caché estricta para sincronización en tiempo real
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/sync':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            data = {}
            if os.path.exists(DATA_FILE):
                try:
                    with open(DATA_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception as e:
                    print(f"Error leyendo {DATA_FILE}: {e}")
            self.wfile.write(json.dumps({'success': True, 'data': data}).encode('utf-8'))
            return
        elif self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"UP"}')
            return

        # Servir archivos estáticos normales (index.html, etc.)
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/sync':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                payload = json.loads(body)
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success":true,"message":"Sincronizado en servidor"}')
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

def run():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, GMAORequestHandler)
    print("=" * 65)
    print(f"🚀 Servidor Python GMAO Industrial Pro activo en el puerto {PORT}")
    print(f"   Acceso local: http://localhost:{PORT}")
    print(f"   Acceso desde celulares y tablets en la red Wi-Fi/LAN de planta:")
    print(f"   http://<IP-DE-ESTE-EQUIPO>:{PORT}")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")

if __name__ == '__main__':
    run()

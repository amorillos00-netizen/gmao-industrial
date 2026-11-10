# GMAO Industrial Pro (CMMS Enterprise v3.2 - Python Edition)

Sistema de Gestión de Mantenimiento Asistido por Ordenador diseñado bajo estándares internacionales de ingeniería de confiabilidad y ciclo de vida de activos (**ISO 14224**, **ISO 55000**, **SMRP**).

Desarrollado en **Python 3.11+** con arquitectura asíncrona de alto rendimiento (**FastAPI / Uvicorn**) y capa relacional de persistencia en disco (**SQLite WAL / PostgreSQL**).

---

## 🏛️ 1. Arquitectura de Software y Estructura del Proyecto

El proyecto está diseñado siguiendo las mejores prácticas de arquitectura limpia (Clean Architecture / Domain-Driven Design), separando la capa de presentación, servicios de ingeniería, modelos y controladores:

```text
📁 GMAO/
├── 📁 app/                             # Código fuente del backend Python
│   ├── 📄 __init__.py                  # Versión y metadatos del paquete
│   ├── 📄 config.py                    # Configuración de entorno, puertos y rutas
│   ├── 📄 database.py                  # Conexión relacional SQLite (WAL) y sembrado de datos
│   ├── 📄 main.py                      # Aplicación FastAPI, routers y endpoints RESTful
│   ├── 📁 services/                    # Lógica de negocio y fórmulas industriales
│   │   ├── 📄 __init__.py
│   │   ├── 📄 kpi_service.py           # Fórmulas SMRP: Disponibilidad, MTBF, MTTR, Cumplimiento
│   │   └── 📄 inventory_service.py     # Conciliación de stock y alertas de punto de reorden
│   └── 📁 static/                      # Frontend SPA optimizado para dispositivos móviles
│       └── 📄 index.html               # Interfaz responsiva multi-dispositivo (PWA ready)
├── 📁 data/                            # Datos operativos persistentes
│   ├── 📄 gmao_enterprise.db           # Base de datos relacional SQLite (concurrente)
│   └── 📁 uploads/                     # Almacén de evidencias fotográficas de intervenciones
├── 📁 database/                        # Diseños y scripts SQL
│   └── 📄 schema.sql                   # Esquema DDL para PostgreSQL / MySQL / SQLite
├── 📁 scripts/                         # Lanzadores automáticos
│   ├── 📄 run_server.bat               # Ejecución directa en Windows (Doble clic)
│   ├── 📄 run_server.ps1               # Script nativo de PowerShell
│   └── 📄 run_server.sh                # Script para servidores Linux / Debian / Ubuntu
├── 📁 tests/                           # Pruebas automatizadas
│   ├── 📄 __init__.py
│   └── 📄 test_kpi.py                  # Pruebas unitarias de confiabilidad (MTBF/MTTR)
├── 📄 run.py                           # Launcher universal con detección de IP de red
├── 📄 requirements.txt                 # Dependencias oficiales de Python
├── 📄 Dockerfile                       # Contenedor enterprise para Docker / Podman
├── 📄 docker-compose.yml               # Orquestación con persistencia de volúmenes
└── 📄 README.md                        # Documentación técnica completa
```

---

## ⚡ 2. ¿Por qué este sistema supera a SAP PM, Odoo, Fractal y GMAO Cloud?

| Característica / Criterio | SAP PM (Plant Maintenance) | Odoo Maintenance | Fractal One / GMAO Cloud | **GMAO Industrial Pro (Este Proyecto)** |
| :--- | :--- | :--- | :--- | :--- |
| **Velocidad y Agilidad** | Extremadamente pesado y lento; requiere múltiples transacciones (`IW31`, `IW21`, `IP10`). | Básico en edición gratuita; requiere módulos de pago para jerarquía real. | Dependiente de conexión a internet constante. | **Instantáneo (<0.3s):** 1 solo clic para crear o cerrar una OT. |
| **Alojamiento Local (On-Premise)** | Requiere infraestructura de servidores masiva y costosa. | Requiere servidor PostgreSQL complejo y mantenimiento de módulos. | Nube obligatoria (pago recurrente por usuario/mes). | **100% Autónomo:** Listo para correr en cualquier PC, servidor local o nube sin dependencias forzosas. |
| **Resiliencia Offline en Planta** | Nula en dispositivos móviles estándar. | No sincroniza si se cae el Wi-Fi en salas blindadas o sótanos. | La app se bloquea o pierde datos si se corta la conexión. | **Híbrido Inteligente:** Sigue operando localmente si se pierde la señal y sincroniza al reconectar. |
| **Tratamiento de Fotografías** | Almacenamiento torpe en servidores SAP. | Sin optimización de imagen en el navegador. | Puede saturar el ancho de banda del canal industrial. | **Compresión Canvas en el cliente:** Reduce fotos de 10 MB a ~70 KB antes de viajar por la red. |
| **Especialidad en Refrigeración** | Requiere desarrollo a la medida (Z-tables). | Inexistente de fábrica. | Campos genéricos no normalizados. | **Nativo para Frío Industrial:** Seguimiento de gases (R-22, R-410A, Amoniaco), cargas y fugas. |
| **Descuento Automático de Stock** | Complejo flujo MM (Material Management) con reservas. | Solo en versión Enterprise con inventario enlazado. | Módulo separado con costo adicional. | **Transaccional Directo:** Descuenta piezas del almacén al cerrar la OT y activa alertas de stock crítico. |

---

## 🚀 3. Instrucciones de Arranque en Servidor Local

### Opción 1: En Windows Server o PC de Planta (1 Clic)
1. Simplemente haz doble clic en:
   ```text
   scripts\run_server.bat
   ```
2. O desde PowerShell:
   ```powershell
   python run.py --host 0.0.0.0 --port 8000
   ```

### Opción 2: En Servidor Linux (Ubuntu, Debian, CentOS)
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar servidor
python3 run.py --host 0.0.0.0 --port 8000
```

### Opción 3: Despliegue con Docker / Podman
```bash
docker compose up -d
```

---

## 📱 4. Acceso Multi-Dispositivo (Smartphones, Tablets y PCs)

El servidor escucha en `0.0.0.0`, lo que permite que cualquier dispositivo en la red Wi-Fi o Intranet de la planta ingrese directamente:

1. **Desde la computadora local:** `http://localhost:8000`
2. **Desde el teléfono o tablet de un técnico:**
   El terminal de arranque mostrará automáticamente la dirección IP local de tu máquina:
   ```text
   http://192.168.1.X:8000
   ```
3. **Documentación Swagger de la API:** `http://localhost:8000/api/docs`

---

## 👥 5. Credenciales Preconfiguradas

| Usuario | Contraseña | Rol Operativo | Capacidades |
| :--- | :--- | :--- | :--- |
| `admin` | `1234` | **Gerente / Jefe de Mantenimiento** | Control maestro: KPIs, OTs, Almacén, Proveedores, Compras, Informes y Auditoría. |
| `tecnico1` | `1234` | **Técnico Electromecánico** | Vista móvil optimizada: Mis OTs, Bitácora técnica con fotos antes/después y cierre. |
| `tecnico2` | `1234` | **Técnico Instrumentista** | Vista móvil simplificada y reporte de averías imprevistas. |
| `solicitante1` | `1234` | **Solicitante de Planta (Jefe Turno)** | Helpdesk de averías: Reportar requerimientos y consultar estado de atención. |

---

## 🧪 6. Ejecución de Pruebas Automatizadas

Para validar la precisión matemática de las fórmulas de confiabilidad SMRP:
```bash
python tests/test_kpi.py
```
Salida esperada:
```text
[OK] Todas las pruebas de confiabilidad y formulas SMRP pasaron con exito.
```

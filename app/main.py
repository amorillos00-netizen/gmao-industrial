"""
GMAO Industrial Pro - Aplicación Principal FastAPI
Arquitectura RESTful con documentación interactiva Swagger (/api/docs) y Redoc (/api/redoc).
Empresa: SALTYSNACK TUYERO C.A. - Departamento de Mantenimiento e Infraestructura
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query, status, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import io
import asyncio

from app.config import STATIC_DIR, APP_DIR, BASE_DIR
from app.database import get_db, init_db
from app.services.kpi_service import calculate_reliability_kpis
from app.services.inventory_service import deduct_spare_parts_from_db, check_low_stock_alerts
from app.services.excel_service import generate_matriz_control_ot_excel, generate_cronograma_anual_excel, generate_informe_periodico_excel, generate_informe_ssl_excel
from app.services.word_service import generate_informe_periodico_docx

# Inicializar aplicación FastAPI
app = FastAPI(
    title="GMAO Industrial Pro API - SALTYSNACK TUYERO C.A.",
    description="API REST Empresarial de Mantenimiento Asistido por Ordenador y Confiabilidad (ISO 14224 / SMRP)",
    version="3.3.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middlewares de producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Control de versión y difusor reactivo en tiempo real (SSE) para sincronización LAN
DB_VERSION = int(datetime.now().timestamp() * 1000)

class EventBroadcaster:
    def __init__(self):
        self._listeners: List[asyncio.Queue] = []

    async def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._listeners.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._listeners:
            try:
                self._listeners.remove(q)
            except ValueError:
                pass

    async def broadcast(self, message: str):
        for q in list(self._listeners):
            try:
                await q.put(message)
            except Exception:
                pass

broadcaster = EventBroadcaster()

def notify_clients():
    """Notifica a todos los clientes conectados en la LAN que la base de datos se ha actualizado."""
    global DB_VERSION
    DB_VERSION = int(datetime.now().timestamp() * 1000)
    msg = json.dumps({"type": "sync", "version": DB_VERSION, "timestamp": datetime.now().isoformat()})
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(broadcaster.broadcast(msg))
    except RuntimeError:
        pass

@app.middleware("http")
async def add_anti_cache_headers(request: Request, call_next):
    """Evita almacenamiento en caché erróneo en navegadores móviles o clientes de red local y difunde cambios."""
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        if request.method in ("POST", "PUT", "DELETE", "PATCH") and 200 <= response.status_code < 300:
            if not request.url.path.startswith("/api/auth/login"):
                notify_clients()
    return response

# --- ENDPOINTS DE SINCRONIZACIÓN REACTIVA Y TIEMPO REAL ---

@app.get("/api/sync/version")
def get_sync_version():
    """Retorna la versión actual de la BD para chequeo ultraligero de sincronización en LAN."""
    return {"version": DB_VERSION, "timestamp": datetime.now().isoformat()}

@app.get("/api/events")
async def sse_events():
    """Canal Server-Sent Events (SSE) para notificación reactiva en tiempo real (<50ms)."""
    async def event_generator():
        q = await broadcaster.subscribe()
        try:
            yield f"data: {json.dumps({'type': 'init', 'version': DB_VERSION})}\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"data: {msg}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            broadcaster.unsubscribe(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.on_event("startup")
def startup_event():
    """Garantiza la inicialización de tablas, migraciones y datos semilla al arrancar."""
    init_db()

# --- 1. ENDPOINTS DE AUTENTICACIÓN Y SEGURIDAD ---

@app.post("/api/auth/login")
def login(payload: Dict[str, str]):
    username = payload.get("username", "").strip()
    password = payload.get("password", "").strip()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.nombre_completo as name, r.nombre as role, u.password_hash as pass, u.departamento, u.cargo
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE LOWER(u.username) = LOWER(?);
        """, (username,))
        user = cursor.fetchone()
        
        if not user or user["pass"] != password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
        
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "name": user["name"],
                "role": user["role"],
                "cargo": user["cargo"] or user["role"],
                "departamento": user["departamento"]
            }
        }

@app.get("/api/users")
def get_technicians():
    """Lista los técnicos disponibles para asignación y apoyo en órdenes de trabajo."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.nombre_completo as name, r.nombre as role, 
                   u.departamento, u.cargo
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE r.nombre = 'Tecnico' OR u.cargo LIKE '%Tecnico%' OR u.cargo LIKE '%Técnico%'
            ORDER BY u.nombre_completo;
        """)
        return [dict(r) for r in cursor.fetchall()]

@app.get("/api/users")
def get_users():
    """Lista todos los usuarios autorizados del sistema."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.nombre_completo as name, r.nombre as role, 
                   u.password_hash as pass, u.departamento, u.cargo
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            ORDER BY u.id;
        """)
        return [dict(r) for r in cursor.fetchall()]

@app.post("/api/users")
def create_or_update_user(payload: Dict[str, Any]):
    """Crea o actualiza un usuario en la base de datos central de SQLite."""
    u_id = payload.get("id") or f"u{uuid.uuid4().hex[:6]}"
    username = payload.get("username", "").strip()
    name = payload.get("name", "").strip() or payload.get("nombre_completo", "").strip() or username
    password = payload.get("pass", "").strip() or payload.get("password", "").strip() or "1234"
    role_name = payload.get("role", "").strip() or payload.get("rol", "Tecnico")
    cargo = payload.get("cargo", "").strip() or role_name
    departamento = payload.get("departamento", "").strip() or "Mantenimiento"

    if not username:
        raise HTTPException(status_code=400, detail="El nombre de usuario es obligatorio.")

    role_map = {
        "Gerente": "ROL-GER",
        "Tecnico": "ROL-TEC",
        "Solicitante": "ROL-SOL",
        "Jefe SSL": "ROL-SSL",
        "Almacenista": "ROL-ALM",
        "Departamento de Compras": "ROL-COM",
        "Compras": "ROL-COM"
    }
    rol_id = role_map.get(role_name, "ROL-TEC")

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (id, username, password_hash, nombre_completo, email, rol_id, cargo, departamento)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username=excluded.username,
                password_hash=excluded.password_hash,
                nombre_completo=excluded.nombre_completo,
                rol_id=excluded.rol_id,
                cargo=excluded.cargo,
                departamento=excluded.departamento;
        """, (u_id, username, password, name, f"{username}@empresa.com", rol_id, cargo, departamento))
        conn.commit()
    
    notify_clients()
    return {"success": True, "id": u_id, "username": username}

@app.delete("/api/users/{user_id}")
def delete_user(user_id: str):
    """Elimina un usuario del sistema (excepto el administrador u1)."""
    if user_id in ("u1", "admin"):
        raise HTTPException(status_code=400, detail="No se puede eliminar el usuario administrador principal.")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?;", (user_id,))
        conn.commit()
    
    notify_clients()
    return {"success": True, "id": user_id}

# --- 2. ENDPOINTS DE ACTIVOS Y EQUIPOS (ISO 14224) ---

@app.get("/api/assets")
def get_assets():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre as name, planta, linea, subensamble, criticidad, status, es_refrigeracion, tipo_refrigerante FROM activos_equipos ORDER BY id;")
        return [dict(r) for r in cursor.fetchall()]

@app.post("/api/assets")
def create_or_update_asset(asset: Dict[str, Any]):
    # Verificación de permisos de seguridad estricta:
    # Solo Jefe de Mantenimiento y Gerente de Planta pueden crear o modificar activos
    user_role = asset.get("userRole")
    user_cargo = asset.get("userCargo") or ""
    if user_role:
        es_autorizado = (user_role == "Gerente") or ("mantenimiento" in user_cargo.lower()) or ("planta" in user_cargo.lower())
        if not es_autorizado:
            raise HTTPException(
                status_code=403,
                detail="Acceso Denegado: La modificación de equipos y activos queda reservada únicamente para los roles de Gerente de Planta y Jefe de Mantenimiento."
            )

    tag = asset.get("id", "").strip()
    nombre = asset.get("name", "").strip()
    if not tag or not nombre:
        raise HTTPException(status_code=400, detail="Tag y Nombre de equipo son obligatorios")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activos_equipos (id, nombre, planta, linea, subensamble, criticidad, status, es_refrigeracion, tipo_refrigerante, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                nombre=excluded.nombre,
                planta=excluded.planta,
                linea=excluded.linea,
                subensamble=excluded.subensamble,
                criticidad=excluded.criticidad,
                status=excluded.status,
                updated_at=CURRENT_TIMESTAMP;
        """, (
            tag, nombre, 
            asset.get("planta", "Planta Central"), 
            asset.get("linea", "General"),
            asset.get("subensamble", "General"),
            asset.get("criticidad", "Media"),
            asset.get("status", "Operativo"),
            bool(asset.get("es_refrigeracion", False)),
            asset.get("tipo_refrigerante")
        ))
        conn.commit()
    return {"success": True, "id": tag}

@app.delete("/api/assets/{asset_id}")
def delete_asset(asset_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activos_equipos WHERE id = ?;", (asset_id,))
        conn.commit()
    return {"success": True}

# --- 3. ENDPOINTS DE ÓRDENES DE TRABAJO (OT) ---

@app.get("/api/work-orders")
def get_work_orders():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tipo, prioridad, equipo_id as equipoId, descripcion, 
                   tecnicos_ids, tecnico_acompanante as tecnicoAcompanante,
                   fecha_asignacion as fechaAsignacion, fecha_programada as fechaProgramada,
                   fecha_inicio as fechaInicio, fecha_fin as fechaFin,
                   status, actividades, tiempo_intervencion as tiempoIntervencion,
                   tiempo_parada as tiempoParada, foto_antes as fotoAntes, foto_despues as fotoDespues,
                   repuestos_usados
            FROM ordenes_trabajo ORDER BY id DESC;
        """)
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            try:
                d["tecnicoIds"] = json.loads(d.pop("tecnicos_ids") or "[]")
            except:
                d["tecnicoIds"] = []
            try:
                d["repuestosUsados"] = json.loads(d.pop("repuestos_usados") or "[]")
            except:
                d["repuestosUsados"] = []
            rows.append(d)
        return rows

@app.post("/api/work-orders")
def save_work_order(ot: Dict[str, Any]):
    ot_id = ot.get("id")
    with get_db() as conn:
        cursor = conn.cursor()
        if ot_id:
            cursor.execute("SELECT 1 FROM ordenes_trabajo WHERE id = ?;", (ot_id,))
            es_nueva = (cursor.fetchone() is None)
        else:
            cursor.execute("SELECT COUNT(*) FROM ordenes_trabajo;")
            count = cursor.fetchone()[0] + 1
            ot_id = f"OT-2026-{str(count).zfill(3)}"
            ot["id"] = ot_id
            es_nueva = True

        # Descontar stock automáticamente si la orden se cierra
        if ot.get("status") in ("Concluida", "Completada") and ot.get("repuestosUsados"):
            deduct_spare_parts_from_db(cursor, ot.get("repuestosUsados", []))

        cursor.execute("""
            INSERT INTO ordenes_trabajo (
                id, tipo, prioridad, equipo_id, descripcion, tecnicos_ids, tecnico_acompanante,
                fecha_asignacion, fecha_programada, fecha_inicio, fecha_fin, status,
                actividades, tiempo_intervencion, tiempo_parada, foto_antes, foto_despues, repuestos_usados, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                tipo=excluded.tipo,
                prioridad=excluded.prioridad,
                equipo_id=excluded.equipo_id,
                descripcion=excluded.descripcion,
                tecnicos_ids=excluded.tecnicos_ids,
                tecnico_acompanante=excluded.tecnico_acompanante,
                fecha_asignacion=excluded.fecha_asignacion,
                fecha_programada=excluded.fecha_programada,
                fecha_inicio=excluded.fecha_inicio,
                fecha_fin=excluded.fecha_fin,
                status=excluded.status,
                actividades=excluded.actividades,
                tiempo_intervencion=excluded.tiempo_intervencion,
                tiempo_parada=excluded.tiempo_parada,
                foto_antes=excluded.foto_antes,
                foto_despues=excluded.foto_despues,
                repuestos_usados=excluded.repuestos_usados,
                updated_at=CURRENT_TIMESTAMP;
        """, (
            ot_id,
            ot.get("tipo", "Correctivo"),
            ot.get("prioridad", "Media"),
            ot.get("equipoId", ""),
            ot.get("descripcion", ""),
            json.dumps(ot.get("tecnicoIds", [])),
            ot.get("tecnicoAcompanante", ""),
            ot.get("fechaAsignacion", datetime.now().strftime("%Y-%m-%d")),
            ot.get("fechaProgramada", datetime.now().strftime("%Y-%m-%d")),
            ot.get("fechaInicio", ""),
            ot.get("fechaFin", ""),
            ot.get("status", "Pendiente"),
            ot.get("actividades", ""),
            float(ot.get("tiempoIntervencion") or 0.0),
            float(ot.get("tiempoParada") or 0.0),
            ot.get("fotoAntes", ""),
            ot.get("fotoDespues", ""),
            json.dumps(ot.get("repuestosUsados", []))
        ))

        # Disparar notificaciones dinámicas según el evento
        tecnicos = ot.get("tecnicoIds", [])
        if es_nueva and tecnicos:
            for tid in tecnicos:
                notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
                cursor.execute("""
                    INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                    VALUES (?, ?, 'Tecnico', 'Nueva Orden Asignada', ?, 'info', ?, 'ot', ?);
                """, (notif_id, tid, f"Se le ha asignado la orden {ot_id}: {ot.get('descripcion')[:60]}", datetime.now().strftime("%Y-%m-%d %H:%M"), ot_id))

        # Flujo de cambio automático de estatus al vincular solicitud
        sol_id = ot.get("solicitudId")
        if sol_id:
            cursor.execute("""
                UPDATE solicitudes_mantenimiento
                SET ot_vinculada = ?, status = 'En proceso', updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status != 'Culminada';
            """, (ot_id, sol_id))
            # Sincronización bidireccional estricta: Notificar al Solicitante
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES (?, NULL, 'Solicitante', 'OT Asignada a su Solicitud', ?, 'info', ?, 'solicitud', ?);
            """, (notif_id, f"Mantenimiento generó la orden {ot_id} para atender su solicitud {sol_id}.", datetime.now().strftime("%Y-%m-%d %H:%M"), sol_id))

        ssl_id = ot.get("sslReportId")
        if ssl_id:
            cursor.execute("""
                UPDATE solicitudes_ssl
                SET ot_vinculada = ?, status = 'En Corrección', updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status != 'Corregida';
            """, (ot_id, ssl_id))
            # Sincronización bidireccional estricta: Notificar al Jefe SSL
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                SELECT ?, solicitante_id, 'Jefe SSL', 'OT de Mitigación Generada (SSL)', ?, 'info', ?, 'ssl', id
                FROM solicitudes_ssl WHERE id = ?;
            """, (notif_id, f"Se generó la OT {ot_id} para mitigar la condición de seguridad {ssl_id}.", datetime.now().strftime("%Y-%m-%d %H:%M"), ssl_id))

        if ot.get("status") in ("Concluida", "Completada"):
            # 1. Desactivación reactiva y purga de alertas vinculadas a la OT
            cursor.execute("""
                UPDATE notificaciones
                SET activa = 0, leido = 1
                WHERE (enlace_tipo = 'ot' AND enlace_id = ?)
                   OR id LIKE ?
                   OR (enlace_id = ? AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent')));
            """, (ot_id, f"NOTIF-OT-%{ot_id}%", ot_id))
            cursor.execute("""
                DELETE FROM notificaciones
                WHERE (enlace_tipo = 'ot' AND enlace_id = ?)
                   OR id LIKE ?
                   OR (enlace_id = ? AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent')));
            """, (ot_id, f"NOTIF-OT-%{ot_id}%", ot_id))

            # 2. Actualización automática de actividades preventivas y cancelación de alertas de vencimiento
            plan_id = ot.get("planId") or ot.get("plan_id")
            fecha_cierre = (ot.get("fechaFin") or ot.get("fechaProgramada") or datetime.now().strftime("%Y-%m-%d"))[:10]
            if ot.get("tipo") == "Preventivo" or plan_id:
                if plan_id:
                    # Obtener periodicidad del plan preventivo para avanzar su próxima fecha de ejecución
                    cursor.execute("SELECT frecuencia_tipo, frecuencia_valor FROM planes_preventivos WHERE id = ?;", (plan_id,))
                    p_info = cursor.fetchone()
                    prox_calc = None
                    if p_info:
                        ftipo = p_info["frecuencia_tipo"] or "meses"
                        fval = p_info["frecuencia_valor"] or 1
                        try:
                            base_dt = datetime.strptime(fecha_cierre, "%Y-%m-%d")
                            if ftipo == "dias":
                                base_dt += timedelta(days=int(fval))
                            elif ftipo == "semanas":
                                base_dt += timedelta(weeks=int(fval))
                            elif ftipo == "meses":
                                m = base_dt.month + int(fval)
                                y = base_dt.year + (m - 1) // 12
                                m = ((m - 1) % 12) + 1
                                d = min(base_dt.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
                                base_dt = base_dt.replace(year=y, month=m, day=d)
                            prox_calc = base_dt.strftime("%Y-%m-%d")
                        except Exception:
                            prox_calc = None

                    if prox_calc:
                        cursor.execute("""
                            UPDATE planes_preventivos
                            SET status = 'Completado', ultima_fecha = ?, proxima_fecha = ?
                            WHERE id = ?;
                        """, (fecha_cierre, prox_calc, plan_id))
                    else:
                        cursor.execute("""
                            UPDATE planes_preventivos
                            SET status = 'Completado', ultima_fecha = ?
                            WHERE id = ?;
                        """, (fecha_cierre, plan_id))

                    cursor.execute("""
                        UPDATE notificaciones
                        SET activa = 0, leido = 1
                        WHERE (enlace_id = ? OR id LIKE ? OR id LIKE ? OR mensaje LIKE ?)
                          AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent') OR enlace_tipo IN ('plan', 'cronograma-anual'));
                    """, (plan_id, f"NOTIF-PREV%{plan_id}%", f"%{plan_id}%", f"%{plan_id}%"))
                    cursor.execute("""
                        DELETE FROM notificaciones
                        WHERE (enlace_id = ? OR id LIKE ? OR id LIKE ? OR mensaje LIKE ?)
                          AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent') OR enlace_tipo IN ('plan', 'cronograma-anual'));
                    """, (plan_id, f"NOTIF-PREV%{plan_id}%", f"%{plan_id}%", f"%{plan_id}%"))
                else:
                    eq_id = ot.get("equipoId")
                    if eq_id:
                        cursor.execute("""
                            UPDATE planes_preventivos
                            SET status = 'Completado', ultima_fecha = ?
                            WHERE equipo_id = ?;
                        """, (fecha_cierre, eq_id))
                        cursor.execute("""
                            UPDATE notificaciones
                            SET activa = 0, leido = 1
                            WHERE (enlace_id IN (SELECT id FROM planes_preventivos WHERE equipo_id = ?) OR id LIKE 'NOTIF-PREV%')
                              AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR mensaje LIKE ?);
                        """, (eq_id, f"%{eq_id}%"))

            # Limpieza global de notificaciones huérfanas de OTs concluidas
            cursor.execute("""
                UPDATE notificaciones
                SET activa = 0, leido = 1
                WHERE enlace_tipo = 'ot' AND enlace_id IN (
                    SELECT id FROM ordenes_trabajo WHERE status IN ('Concluida', 'Completada')
                ) AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent'));
            """)

            # Cambio automático de estatus: Solicitudes vinculadas pasan a 'Culminada'
            cursor.execute("""
                UPDATE solicitudes_mantenimiento
                SET status = 'Culminada', updated_at = CURRENT_TIMESTAMP
                WHERE ot_vinculada = ?;
            """, (ot_id,))

            # Cambio automático de estatus: Condiciones SSL vinculadas pasan a 'Corregida'
            cursor.execute("""
                UPDATE solicitudes_ssl
                SET status = 'Corregida', fecha_correccion = ?, updated_at = CURRENT_TIMESTAMP
                WHERE ot_vinculada = ?;
            """, (datetime.now().strftime("%Y-%m-%d %H:%M"), ot_id))

            # Marcar notificaciones vinculadas como leídas y desactivadas
            cursor.execute("""
                UPDATE notificaciones
                SET activa = 0, leido = 1
                WHERE enlace_id IN (SELECT id FROM solicitudes_mantenimiento WHERE status = 'Culminada')
                   OR enlace_id IN (SELECT id FROM solicitudes_ssl WHERE status IN ('Corregida', 'Desestimada'));
            """)

            # Notificar al Jefe de Mantenimiento
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id, activa)
                VALUES (?, NULL, 'Gerente', 'OT Concluida por Técnico', ?, 'success', ?, 'ot', ?, 1);
            """, (notif_id, f"La orden {ot_id} en {ot.get('equipoId')} ha sido culminada.", datetime.now().strftime("%Y-%m-%d %H:%M"), ot_id))

            # Sincronización bidireccional estricta: Notificar al Solicitante sobre culminación
            cursor.execute("""
                SELECT id FROM solicitudes_mantenimiento WHERE ot_vinculada = ?;
            """, (ot_id,))
            for s_row in cursor.fetchall():
                notif_sol = f"NOTIF-{uuid.uuid4().hex[:8]}"
                cursor.execute("""
                    INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id, activa)
                    VALUES (?, NULL, 'Solicitante', 'Solicitud Culminada por Mantenimiento', ?, 'success', ?, 'solicitud', ?, 1);
                """, (notif_sol, f"La orden {ot_id} vinculada a su solicitud {s_row['id']} ha concluido exitosamente.", datetime.now().strftime("%Y-%m-%d %H:%M"), s_row["id"]))

            # Sincronización bidireccional estricta: Notificar al Jefe SSL sobre corrección
            cursor.execute("""
                SELECT id, solicitante_id, codigo FROM solicitudes_ssl WHERE ot_vinculada = ?;
            """, (ot_id,))
            for ssl_row in cursor.fetchall():
                notif_ssl = f"NOTIF-{uuid.uuid4().hex[:8]}"
                cursor.execute("""
                    INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id, activa)
                    VALUES (?, ?, 'Jefe SSL', 'Condición SSL Mitigada y Corregida', ?, 'success', ?, 'ssl', ?, 1);
                """, (notif_ssl, ssl_row["solicitante_id"], f"La condición {ssl_row['codigo'] or ssl_row['id']} ha sido corregida tras concluir la OT {ot_id}.", datetime.now().strftime("%Y-%m-%d %H:%M"), ssl_row["id"]))
        conn.commit()
    notify_clients()
    return {"success": True, "id": ot_id}

@app.delete("/api/work-orders/{ot_id}")
def delete_work_order(ot_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE salidas_materiales SET ot_id = NULL WHERE ot_id = ?;", (ot_id,))
        cursor.execute("UPDATE solicitudes_mantenimiento SET ot_vinculada = NULL WHERE ot_vinculada = ?;", (ot_id,))
        cursor.execute("UPDATE solicitudes_ssl SET ot_vinculada = NULL WHERE ot_vinculada = ?;", (ot_id,))
        cursor.execute("DELETE FROM notificaciones WHERE (enlace_tipo = 'ot' AND enlace_id = ?) OR mensaje LIKE ?;", (ot_id, f"%{ot_id}%"))
        cursor.execute("DELETE FROM ordenes_trabajo WHERE id = ?;", (ot_id,))
        conn.commit()
    notify_clients()
    return {"success": True, "id": ot_id}

# --- 4. ENDPOINTS DE ALMACÉN Y REPUESTOS ---

@app.get("/api/inventory")
def get_inventory():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nombre as name, stock, stock_minimo as stockMin, unidad_medida as um, costo_unitario as costo, proveedor_id as proveedorId FROM repuestos_materiales ORDER BY codigo;")
        return [dict(r) for r in cursor.fetchall()]

@app.get("/api/inventory/alerts")
def get_inventory_alerts():
    with get_db() as conn:
        cursor = conn.cursor()
        return check_low_stock_alerts(cursor)

@app.post("/api/inventory")
def save_spare_part(rep: Dict[str, Any]):
    rep_id = rep.get("id")
    with get_db() as conn:
        cursor = conn.cursor()
        if not rep_id:
            cursor.execute("SELECT COUNT(*) FROM repuestos_materiales;")
            rep_id = f"REP-{str(cursor.fetchone()[0] + 1).zfill(2)}"
        
        cursor.execute("""
            INSERT INTO repuestos_materiales (id, codigo, nombre, stock, stock_minimo, unidad_medida, costo_unitario, proveedor_id, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                codigo=excluded.codigo,
                nombre=excluded.nombre,
                stock=excluded.stock,
                stock_minimo=excluded.stock_minimo,
                unidad_medida=excluded.unidad_medida,
                costo_unitario=excluded.costo_unitario,
                proveedor_id=excluded.proveedor_id,
                updated_at=CURRENT_TIMESTAMP;
        """, (
            rep_id,
            rep.get("codigo", ""),
            rep.get("name", ""),
            int(rep.get("stock", 0)),
            int(rep.get("stockMin", 2)),
            rep.get("um", "pza"),
            float(rep.get("costo", 0.0)),
            rep.get("proveedorId")
        ))
        conn.commit()
    return {"success": True, "id": rep_id}

@app.delete("/api/inventory/{item_id}")
def delete_spare_part(item_id: str):
    """Elimina un repuesto o material del inventario y desvincula salidas asociadas."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE salidas_materiales SET repuesto_id = NULL WHERE repuesto_id = ?;", (item_id,))
        cursor.execute("DELETE FROM repuestos_materiales WHERE id = ?;", (item_id,))
        conn.commit()
    return {"success": True, "id": item_id}

# --- 5. ENDPOINTS DE PROVEEDORES ---

@app.get("/api/suppliers")
def get_suppliers():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, rif, nombre, categoria, contacto, telefono, email FROM proveedores ORDER BY nombre;")
        return [dict(r) for r in cursor.fetchall()]

@app.post("/api/suppliers")
def save_supplier(prv: Dict[str, Any]):
    prv_id = prv.get("id")
    with get_db() as conn:
        cursor = conn.cursor()
        if not prv_id:
            cursor.execute("SELECT COUNT(*) FROM proveedores;")
            prv_id = f"PRV-{str(cursor.fetchone()[0] + 1).zfill(2)}"
        
        cursor.execute("""
            INSERT INTO proveedores (id, rif, nombre, categoria, contacto, telefono, email, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                rif=excluded.rif,
                nombre=excluded.nombre,
                categoria=excluded.categoria,
                contacto=excluded.contacto,
                telefono=excluded.telefono,
                email=excluded.email,
                updated_at=CURRENT_TIMESTAMP;
        """, (
            prv_id,
            prv.get("rif", ""),
            prv.get("nombre", ""),
            prv.get("categoria", "General"),
            prv.get("contacto", ""),
            prv.get("telefono", ""),
            prv.get("email", "")
        ))
        conn.commit()
    return {"success": True, "id": prv_id}

# --- 6. ENDPOINTS DE KPIS Y CONFIABILIDAD CON FILTRADO DE PERIODO ---

@app.get("/api/kpis")
def get_kpis(
    equipo: str = Query("TODOS"),
    periodo_tipo: str = Query("Mensual"),
    periodo_valor: Optional[str] = Query(None)
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tipo, prioridad, equipo_id as equipoId, status, 
                   tiempo_intervencion as tiempoIntervencion, tiempo_parada as tiempoParada,
                   fecha_programada as fechaProgramada, fecha_asignacion as fechaAsignacion
            FROM ordenes_trabajo;
        """)
        ots = [dict(r) for r in cursor.fetchall()]

        # Obtener umbral configurable de MTTR
        cursor.execute("SELECT valor FROM configuracion_sistema WHERE clave = 'mttr_target_hours';")
        row = cursor.fetchone()
        mttr_target = float(row[0]) if (row and row[0]) else 2.0

        return calculate_reliability_kpis(ots, equipo, periodo_tipo, periodo_valor, mttr_target_hours=mttr_target)

# --- 6.1 ENDPOINTS DE CONFIGURACIÓN Y PARÁMETROS DEL SISTEMA (MTTR, UMBRALES) ---

@app.get("/api/config")
def get_system_config():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT clave, valor, descripcion FROM configuracion_sistema;")
        return {r["clave"]: {"valor": r["valor"], "descripcion": r["descripcion"]} for r in cursor.fetchall()}

@app.post("/api/config")
def update_system_config(payload: Dict[str, Any]):
    with get_db() as conn:
        cursor = conn.cursor()
        for k, v in payload.items():
            cursor.execute("""
                INSERT INTO configuracion_sistema (clave, valor, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor, updated_at=CURRENT_TIMESTAMP;
            """, (str(k), str(v)))
        conn.commit()
    return {"success": True, "config": payload}

# --- 6.2 ENDPOINTS DE SOLICITUDES Y REQUISICIONES DE COMPRAS ---

@app.get("/api/purchases")
def get_purchases(role: Optional[str] = Query(None), creado_por: Optional[str] = Query(None)):
    with get_db() as conn:
        cursor = conn.cursor()
        if role in ("Departamento de Compras", "Compras") or (creado_por and "jefe" in creado_por.lower()):
            cursor.execute("""
                SELECT id, fecha, descripcion, cant_solicitada as cantSolicitada, cant_recibida as cantRecibida,
                       moneda, precio, proveedor_id as proveedorId, observaciones, COALESCE(status, 'Pendiente') as status,
                       COALESCE(creado_por, 'Jefe de Mantenimiento') as creadoPor
                FROM compras_materiales
                WHERE creado_por LIKE '%Jefe%' OR creado_por LIKE '%Mantenimiento%' OR creado_por IS NULL
                ORDER BY id DESC;
            """)
        else:
            cursor.execute("""
                SELECT id, fecha, descripcion, cant_solicitada as cantSolicitada, cant_recibida as cantRecibida,
                       moneda, precio, proveedor_id as proveedorId, observaciones, COALESCE(status, 'Pendiente') as status,
                       COALESCE(creado_por, 'Jefe de Mantenimiento') as creadoPor
                FROM compras_materiales ORDER BY id DESC;
            """)
        return [dict(r) for r in cursor.fetchall()]

@app.post("/api/purchases")
def save_purchase(compra: Dict[str, Any]):
    user_role = compra.get("rol") or compra.get("role") or ""
    if user_role in ("Departamento de Compras", "Compras"):
        if compra.get("status") == "Recibida":
            raise HTTPException(status_code=403, detail="Acceso denegado: El estado 'Recibida' es exclusivo para Jefe de Mantenimiento y Almacén.")
        if compra.get("status") and compra.get("status") not in ("Pendiente", "Aprobada", "En Tránsito", "En tránsito"):
            raise HTTPException(status_code=403, detail="Acceso denegado: Compras solo puede asignar estados: Pendiente, Aprobada o En tránsito.")
    com_id = compra.get("id")
    with get_db() as conn:
        cursor = conn.cursor()
        if not com_id:
            cursor.execute("SELECT COUNT(*) FROM compras_materiales;")
            count = cursor.fetchone()[0] + 1
            com_id = f"COM-{str(count).zfill(2)}"
            compra["id"] = com_id
        
        creador = compra.get("creadoPor") or "Jefe de Mantenimiento"
        cursor.execute("""
            INSERT INTO compras_materiales (
                id, fecha, descripcion, cant_solicitada, cant_recibida, moneda, precio, proveedor_id, observaciones, status, creado_por, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                fecha=excluded.fecha,
                descripcion=excluded.descripcion,
                cant_solicitada=excluded.cant_solicitada,
                cant_recibida=excluded.cant_recibida,
                precio=excluded.precio,
                proveedor_id=excluded.proveedor_id,
                observaciones=excluded.observaciones,
                status=excluded.status,
                creado_por=COALESCE(excluded.creado_por, compras_materiales.creado_por),
                updated_at=CURRENT_TIMESTAMP;
        """, (
            com_id,
            compra.get("fecha", datetime.now().strftime("%Y-%m-%d")),
            compra.get("descripcion", "").strip(),
            int(compra.get("cantSolicitada", 1)),
            int(compra.get("cantRecibida", 0)),
            compra.get("moneda", "$"),
            float(compra.get("precio", 0.0)),
            compra.get("proveedorId"),
            compra.get("observaciones", "").strip(),
            compra.get("status", "Pendiente"),
            creador
        ))
        conn.commit()
    return {"success": True, "id": com_id, "compra": compra}

@app.delete("/api/purchases/{compra_id}")
def delete_purchase(compra_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM compras_materiales WHERE id = ?;", (compra_id,))
        conn.commit()
    notify_clients()
    return {"success": True}

@app.patch("/api/purchases/{compra_id}/status")
@app.put("/api/purchases/{compra_id}/status")
def update_purchase_status(compra_id: str, payload: Dict[str, Any]):
    new_status = payload.get("status", "Pendiente")
    user_role = payload.get("rol") or payload.get("role") or ""
    if user_role in ("Departamento de Compras", "Compras"):
        if new_status == "Recibida":
            raise HTTPException(status_code=403, detail="Acceso denegado: El estado 'Recibida' es exclusivo para Jefe de Mantenimiento y Almacén.")
        if new_status not in ("Pendiente", "Aprobada", "En Tránsito", "En tránsito"):
            raise HTTPException(status_code=403, detail="Acceso denegado: Compras solo puede asignar estados: Pendiente, Aprobada o En tránsito.")
    cant_rec = payload.get("cantRecibida")
    obs = payload.get("observaciones")
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, descripcion, cant_solicitada, status FROM compras_materiales WHERE id = ?;", (compra_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Solicitud de compra no encontrada")
        
        if cant_rec is not None:
            cursor.execute("UPDATE compras_materiales SET status = ?, cant_recibida = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (new_status, int(cant_rec), compra_id))
        else:
            cursor.execute("UPDATE compras_materiales SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (new_status, compra_id))
        
        if obs:
            cursor.execute("UPDATE compras_materiales SET observaciones = ? WHERE id = ?;", (obs, compra_id))

        # Notificar cambio a Gerencia y Almacén
        notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
            VALUES (?, NULL, 'Gerente', 'Estatus de Compra Actualizado', ?, 'info', ?, 'compras', ?);
        """, (notif_id, f"Compra {compra_id} ({row['descripcion'][:35]}): nuevo estatus '{new_status}'", datetime.now().strftime("%Y-%m-%d %H:%M"), compra_id))
        conn.commit()
    notify_clients()
    return {"success": True, "id": compra_id, "status": new_status}

# --- 6.3 ALERTADOR ANTICIPADO DE PREVENTIVOS A 5 DÍAS ---


@app.post("/api/alerts/recalculate")
def recalculate_preventive_alerts():
    """Recalcula las alertas preventivas en tiempo real e invalida la caché de notificaciones vencidas/concluidas."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notificaciones
            SET activa = 0, leido = 1
            WHERE (
                (enlace_tipo = 'ot' AND enlace_id IN (SELECT id FROM ordenes_trabajo WHERE status IN ('Concluida', 'Completada')))
                OR (enlace_tipo IN ('plan', 'cronograma-anual') AND enlace_id IN (SELECT id FROM planes_preventivos WHERE status IN ('Completado', 'Ejecutado')))
            ) AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent'));
        """)
        conn.commit()
    notify_clients()
    return {"success": True, "message": "Alertas preventivas recalculadas e invalidación de caché ejecutada exitosamente."}

@app.get("/api/alerts/preventive-check")
def check_preventive_alerts():
    """Genera alertas y notificaciones automáticas para mantenimientos programados con 5 días de anticipación o vencidos no completados."""
    alerts = []
    hoy = datetime.now().date()
    with get_db() as conn:
        cursor = conn.cursor()
        # 1. Revisar planes preventivos activos no completados ni con OT concluida
        cursor.execute("""
            SELECT p.id, p.nombre, p.equipo_id, p.proxima_fecha, e.nombre as equipo_nombre
            FROM planes_preventivos p
            LEFT JOIN activos_equipos e ON p.equipo_id = e.id
            WHERE COALESCE(p.status, 'Pendiente') NOT IN ('Completado', 'Ejecutado')
              AND p.id NOT IN (
                  SELECT DISTINCT plan_id FROM ordenes_trabajo 
                  WHERE plan_id IS NOT NULL AND status IN ('Concluida', 'Completada')
              );
        """)
        for p in cursor.fetchall():
            prox = p["proxima_fecha"]
            if prox:
                try:
                    p_date = datetime.strptime(prox[:10], "%Y-%m-%d").date()
                    diff = (p_date - hoy).days
                    if diff <= 5:
                        notif_id = f"NOTIF-PREV-5D-{p['id']}-{prox[:10]}"
                        tit = 'Alerta Preventiva (En 5 días)' if diff == 5 else ('¡Atención! Preventivo Vencido' if diff < 0 else '¡Atención! Preventivo Próximo')
                        tip = 'urgent' if diff <= 0 else 'warning'
                        msg = f"Rutina preventiva ({prox[:10]}): {p['equipo_id']} - {p['equipo_nombre'] or ''} ({p['nombre']})."
                        cursor.execute("""
                            INSERT OR IGNORE INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id, activa)
                            VALUES (?, NULL, 'Gerente', ?, ?, ?, ?, 'plan', ?, 1);
                        """, (notif_id, tit, msg, tip, datetime.now().strftime("%Y-%m-%d %H:%M"), p["id"]))
                        alerts.append({"tipo": "plan", "id": p["id"], "equipo": p["equipo_id"], "fecha": prox[:10], "dias": diff})
                except Exception:
                    pass

        # 2. Revisar OTs preventivas programadas no concluidas
        cursor.execute("""
            SELECT o.id, o.descripcion, o.equipo_id, o.fecha_programada, e.nombre as equipo_nombre
            FROM ordenes_trabajo o
            LEFT JOIN activos_equipos e ON o.equipo_id = e.id
            WHERE o.tipo = 'Preventivo' AND o.status NOT IN ('Concluida', 'Completada', 'Cancelada');
        """)
        for o in cursor.fetchall():
            fprog = o["fecha_programada"]
            if fprog:
                try:
                    o_date = datetime.strptime(fprog[:10], "%Y-%m-%d").date()
                    diff = (o_date - hoy).days
                    if diff == 5:
                        notif_id = f"NOTIF-OT-5D-{o['id']}-{fprog[:10]}"
                        msg = f"OT Preventiva {o['id']} programada en exactamente 5 días ({fprog[:10]}): {o['equipo_id']} - {o['equipo_nombre'] or ''} ({o['descripcion'][:50]})."
                        cursor.execute("""
                            INSERT OR IGNORE INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id, activa)
                            VALUES (?, NULL, 'Gerente', 'Alerta Preventiva (En 5 días)', ?, 'warning', ?, 'ot', ?, 1);
                        """, (notif_id, msg, datetime.now().strftime("%Y-%m-%d %H:%M"), o["id"]))
                        alerts.append({"tipo": "ot", "id": o["id"], "equipo": o["equipo_id"], "fecha": fprog[:10], "dias": 5})
                except Exception:
                    pass

        conn.commit()
    return {"success": True, "count": len(alerts), "alerts": alerts}

# --- 7. EXPORTACIÓN PROFESIONAL A EXCEL (MATRIZ OT Y CRONOGRAMA ANUAL) ---


# --- RESTRICCIÓN Y ENDPOINT DE RESPALDO (BACKUP DB) POR ROLES ---

def check_backup_role_permission(user_role: Optional[str] = None, user_cargo: Optional[str] = None, username: Optional[str] = None) -> bool:
    """Verifica si el usuario posee permiso exclusivo para ejecutar respaldos (Gerente o Jefe de Mantenimiento)."""
    if not isinstance(user_role, str): user_role = None
    if not isinstance(user_cargo, str): user_cargo = None
    if not isinstance(username, str): username = None
    if user_role and user_role.lower() == "gerente":
        return True
    if user_cargo and ("jefe de mantenimiento" in user_cargo.lower() or "gerente" in user_cargo.lower()):
        return True
    if username and username.lower() in ("admin", "gerente_planta"):
        return True
    if username:
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT u.username, r.nombre as role, u.cargo
                    FROM usuarios u
                    JOIN roles r ON u.rol_id = r.id
                    WHERE LOWER(u.username) = LOWER(?);
                """, (username,))
                row = cursor.fetchone()
                if row:
                    r_nom = (row["role"] or "").lower()
                    u_cargo = (row["cargo"] or "").lower()
                    if r_nom == "gerente" or "jefe de mantenimiento" in u_cargo or "gerente" in u_cargo:
                        return True
        except Exception:
            pass
    return False

@app.get("/api/backup")
def get_database_backup(
    user_role: Optional[str] = Query(None),
    user_cargo: Optional[str] = Query(None),
    username: Optional[str] = Query(None)
):
    """Descarga de respaldo (backup) exclusivo para Gerente o Jefe de Mantenimiento."""
    if not check_backup_role_permission(user_role, user_cargo, username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso Denegado: La función de respaldo (backup) está reservada exclusivamente para usuarios con el rol de 'Gerente' o 'Jefe de Mantenimiento'."
        )
    sync_res = get_full_sync()
    db_data = sync_res["data"]
    json_bytes = json.dumps(db_data, ensure_ascii=False, indent=2).encode("utf-8")
    filename = f"GMAO_BACKUP_SALTYSNACK_{datetime.now().strftime('%Y_%m_%d')}.json"
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/backup")
def post_database_backup(payload: Dict[str, Any] = None):
    """Descarga de respaldo vía POST con verificación de credenciales/rol."""
    payload = payload or {}
    user_role = payload.get("userRole") or payload.get("role")
    user_cargo = payload.get("userCargo") or payload.get("cargo")
    username = payload.get("username")
    if not check_backup_role_permission(user_role, user_cargo, username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso Denegado: La función de respaldo (backup) está reservada exclusivamente para usuarios con el rol de 'Gerente' o 'Jefe de Mantenimiento'."
        )
    sync_res = get_full_sync()
    db_data = sync_res["data"]
    json_bytes = json.dumps(db_data, ensure_ascii=False, indent=2).encode("utf-8")
    filename = f"GMAO_BACKUP_SALTYSNACK_{datetime.now().strftime('%Y_%m_%d')}.json"
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/reports/matriz-ot-excel")
def export_matriz_ot_excel():
    """Descarga el Excel corporativo 'MATRIZ CONTROL DE O.T.xlsx' idéntico a SALTYSNACK TUYERO C.A."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo, prioridad, equipo_id as equipoId, descripcion, tecnicos_ids, fecha_asignacion as fechaAsignacion, fecha_programada as fechaProgramada, status, actividades, tiempo_intervencion as tiempoIntervencion, repuestos_usados FROM ordenes_trabajo ORDER BY id DESC;")
        ots = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT u.id, u.nombre_completo as name, r.nombre as role, u.username FROM usuarios u JOIN roles r ON u.rol_id = r.id;")
        users = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, nombre as name, linea, planta FROM activos_equipos;")
        equipos = [dict(r) for r in cursor.fetchall()]

    excel_bytes = generate_matriz_control_ot_excel(ots, users, equipos)
    filename = f"MATRIZ_CONTROL_DE_OT_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/reports/ssl-excel")
def export_ssl_excel():
    """Descarga el informe oficial en Excel (.xlsx) de Condiciones Inseguras (SSL) con evidencias fotográficas."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, codigo, fecha_hora as fechaHora, area, ubicacion, equipo_id as equipoId,
                   nivel_riesgo as nivelRiesgo, descripcion, accion_propuesta as accionPropuesta,
                   solicitante_id as solicitanteId, solicitante_nombre as solicitanteNombre,
                   foto_evidencia as fotoEvidencia, status, fecha_correccion as fechaCorreccion,
                   ot_vinculada as otVinculada, observaciones_cierre as observacionesCierre
            FROM solicitudes_ssl ORDER BY id DESC;
        """)
        ssl_requests = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT id, nombre_completo as name, username FROM usuarios;")
        users = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT id, nombre as name FROM activos_equipos;")
        equipos = [dict(r) for r in cursor.fetchall()]

    excel_bytes = generate_informe_ssl_excel(ssl_requests, users, equipos)
    filename = f"INFORME_CONDICIONES_INSEGURAS_SSL_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.post("/api/reports/ssl-excel")
def export_ssl_excel_post(payload: Dict[str, Any]):
    """Permite exportar a Excel enviando los registros SSL actuales desde el cliente."""
    client_ssl = payload.get("solicitudesSSL", [])
    with get_db() as conn:
        cursor = conn.cursor()
        if not client_ssl:
            cursor.execute("""
                SELECT id, codigo, fecha_hora as fechaHora, area, ubicacion, equipo_id as equipoId,
                       nivel_riesgo as nivelRiesgo, descripcion, accion_propuesta as accionPropuesta,
                       solicitante_id as solicitanteId, solicitante_nombre as solicitanteNombre,
                       foto_evidencia as fotoEvidencia, status, fecha_correccion as fechaCorreccion,
                       ot_vinculada as otVinculada, observaciones_cierre as observacionesCierre
                FROM solicitudes_ssl ORDER BY id DESC;
            """)
            client_ssl = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT id, nombre_completo as name, username FROM usuarios;")
        users = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT id, nombre as name FROM activos_equipos;")
        equipos = [dict(r) for r in cursor.fetchall()]

    excel_bytes = generate_informe_ssl_excel(client_ssl, users, equipos)
    filename = f"INFORME_CONDICIONES_INSEGURAS_SSL_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.get("/api/reports/cronograma-anual-excel")
def export_cronograma_anual_excel(anio: int = Query(2026)):
    """Descarga el Excel corporativo del Cronograma Anual Preventivo."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, equipo_id as equipoId, nombre, frecuencia, ultima_fecha as ultimaFecha, proxima_fecha as proximaFecha, es_refrigeracion FROM planes_preventivos;")
        planes = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, nombre as name, planta, linea FROM activos_equipos;")
        equipos = [dict(r) for r in cursor.fetchall()]

    excel_bytes = generate_cronograma_anual_excel(planes, equipos, anio)
    filename = f"Cronograma_Anual_Mantenimiento_Preventivo_{anio}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/reports/informe-periodico-excel")
def export_informe_periodico_excel(
    periodo_tipo: str = Query("Mensual"),
    periodo_valor: str = Query("2026-10"),
    equipo_id: str = Query("TODOS")
):
    """Descarga el Excel corporativo del Informe Periódico de Mantenimiento y Confiabilidad."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tipo, prioridad, equipo_id as equipoId, descripcion, tecnicos_ids,
                   tecnico_acompanante as tecnicoAcompanante, fecha_asignacion as fechaAsignacion,
                   fecha_programada as fechaProgramada, fecha_inicio as fechaInicio, fecha_fin as fechaFin,
                   status, actividades, tiempo_intervencion as tiempoIntervencion, tiempo_parada as tiempoParada,
                   repuestos_usados FROM ordenes_trabajo ORDER BY id DESC;
        """)
        raw_ots = [dict(r) for r in cursor.fetchall()]
        ots = []
        for o in raw_ots:
            o["tecnicoIds"] = json.loads(o.pop("tecnicos_ids") or "[]")
            o["repuestosUsados"] = json.loads(o.pop("repuestos_usados") or "[]")
            ots.append(o)

        cursor.execute("SELECT id, nombre as name, linea, planta FROM activos_equipos;")
        equipos = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT u.id, u.nombre_completo as name, r.nombre as role, u.cargo FROM usuarios u JOIN roles r ON u.rol_id = r.id;")
        users = [dict(r) for r in cursor.fetchall()]

    jefe = next((u["name"] for u in users if "jefe de mantenimiento" in (u.get("cargo") or "").lower() or u.get("role") == "Gerente"), "Ing. Carlos Mendoza")
    gerente = next((u["name"] for u in users if "gerente de planta" in (u.get("cargo") or "").lower()), "Ing. Roberto Navarro")

    excel_bytes = generate_informe_periodico_excel(
        ots=ots,
        equipos=equipos,
        periodo_tipo=periodo_tipo,
        periodo_valor=periodo_valor,
        equipo_filtro=equipo_id,
        nombre_jefe=jefe,
        nombre_gerente=gerente
    )
    filename = f"INFORME_PERIODICO_{periodo_valor.replace('-', '_')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/api/reports/informe-periodico-word")
def export_informe_periodico_word(
    periodo_tipo: str = Query("Mensual"),
    periodo_valor: str = Query("2026-10"),
    equipo_id: str = Query("TODOS")
):
    """Descarga el Word (.docx) corporativo del Informe Periódico de Mantenimiento y Confiabilidad."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, tipo, prioridad, equipo_id as equipoId, descripcion, tecnicos_ids,
                   tecnico_acompanante as tecnicoAcompanante, fecha_asignacion as fechaAsignacion,
                   fecha_programada as fechaProgramada, fecha_inicio as fechaInicio, fecha_fin as fechaFin,
                   status, actividades, tiempo_intervencion as tiempoIntervencion, tiempo_parada as tiempoParada,
                   repuestos_usados FROM ordenes_trabajo ORDER BY id DESC;
        """)
        raw_ots = [dict(r) for r in cursor.fetchall()]
        ots = []
        for o in raw_ots:
            o["tecnicoIds"] = json.loads(o.pop("tecnicos_ids") or "[]")
            o["repuestosUsados"] = json.loads(o.pop("repuestos_usados") or "[]")
            ots.append(o)

        cursor.execute("SELECT id, nombre as name, linea, planta FROM activos_equipos;")
        equipos = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT u.id, u.nombre_completo as name, r.nombre as role, u.cargo FROM usuarios u JOIN roles r ON u.rol_id = r.id;")
        users = [dict(r) for r in cursor.fetchall()]

    jefe = next((u["name"] for u in users if "jefe de mantenimiento" in (u.get("cargo") or "").lower() or u.get("role") == "Gerente"), "Ing. Carlos Mendoza")
    gerente = next((u["name"] for u in users if "gerente de planta" in (u.get("cargo") or "").lower()), "Ing. Roberto Navarro")

    docx_bytes = generate_informe_periodico_docx(
        ots=ots,
        equipos=equipos,
        periodo_tipo=periodo_tipo,
        periodo_valor=periodo_valor,
        equipo_filtro=equipo_id,
        nombre_jefe=jefe,
        nombre_gerente=gerente
    )
    filename = f"INFORME_PERIODICO_{periodo_valor.replace('-', '_')}.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.post("/api/reports/informe-periodico-excel")
def export_informe_periodico_excel_post(payload: Dict[str, Any]):
    """Descarga el Excel corporativo del Informe Periódico vía POST permitiendo datos personalizados."""
    periodo_tipo = payload.get("periodo_tipo") or payload.get("periodoTipo") or "Mensual"
    periodo_valor = payload.get("periodo_valor") or payload.get("periodoValor") or "2026-10"
    equipo_id = payload.get("equipo_id") or payload.get("equipoId") or "TODOS"
    
    ots = payload.get("ots")
    equipos = payload.get("equipos")

    with get_db() as conn:
        cursor = conn.cursor()
        if ots is None:
            cursor.execute("""
                SELECT id, tipo, prioridad, equipo_id as equipoId, descripcion, tecnicos_ids,
                       tecnico_acompanante as tecnicoAcompanante, fecha_asignacion as fechaAsignacion,
                       fecha_programada as fechaProgramada, fecha_inicio as fechaInicio, fecha_fin as fechaFin,
                       status, actividades, tiempo_intervencion as tiempoIntervencion, tiempo_parada as tiempoParada,
                       repuestos_usados FROM ordenes_trabajo ORDER BY id DESC;
            """)
            raw_ots = [dict(r) for r in cursor.fetchall()]
            ots = []
            for o in raw_ots:
                o["tecnicoIds"] = json.loads(o.pop("tecnicos_ids") or "[]")
                o["repuestosUsados"] = json.loads(o.pop("repuestos_usados") or "[]")
                ots.append(o)

        if equipos is None:
            cursor.execute("SELECT id, nombre as name, linea, planta FROM activos_equipos;")
            equipos = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT u.id, u.nombre_completo as name, r.nombre as role, u.cargo FROM usuarios u JOIN roles r ON u.rol_id = r.id;")
        users = [dict(r) for r in cursor.fetchall()]

    jefe = next((u["name"] for u in users if "jefe de mantenimiento" in (u.get("cargo") or "").lower() or u.get("role") == "Gerente"), "Ing. Carlos Mendoza")
    gerente = next((u["name"] for u in users if "gerente de planta" in (u.get("cargo") or "").lower()), "Ing. Roberto Navarro")

    excel_bytes = generate_informe_periodico_excel(
        ots=ots,
        equipos=equipos,
        periodo_tipo=periodo_tipo,
        periodo_valor=periodo_valor,
        equipo_filtro=equipo_id,
        nombre_jefe=jefe,
        nombre_gerente=gerente
    )
    safe_periodo = str(periodo_valor).replace("-", "_").replace(" ", "_")
    filename = f"INFORME_PERIODICO_{safe_periodo}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/reports/informe-periodico-word")
def export_informe_periodico_word_post(payload: Dict[str, Any]):
    """Descarga el Word (.docx) corporativo del Informe Periódico vía POST."""
    periodo_tipo = payload.get("periodo_tipo") or payload.get("periodoTipo") or "Mensual"
    periodo_valor = payload.get("periodo_valor") or payload.get("periodoValor") or "2026-10"
    equipo_id = payload.get("equipo_id") or payload.get("equipoId") or "TODOS"
    
    ots = payload.get("ots")
    equipos = payload.get("equipos")

    with get_db() as conn:
        cursor = conn.cursor()
        if ots is None:
            cursor.execute("""
                SELECT id, tipo, prioridad, equipo_id as equipoId, descripcion, tecnicos_ids,
                       tecnico_acompanante as tecnicoAcompanante, fecha_asignacion as fechaAsignacion,
                       fecha_programada as fechaProgramada, fecha_inicio as fechaInicio, fecha_fin as fechaFin,
                       status, actividades, tiempo_intervencion as tiempoIntervencion, tiempo_parada as tiempoParada,
                       repuestos_usados FROM ordenes_trabajo ORDER BY id DESC;
            """)
            raw_ots = [dict(r) for r in cursor.fetchall()]
            ots = []
            for o in raw_ots:
                o["tecnicoIds"] = json.loads(o.pop("tecnicos_ids") or "[]")
                o["repuestosUsados"] = json.loads(o.pop("repuestos_usados") or "[]")
                ots.append(o)

        if equipos is None:
            cursor.execute("SELECT id, nombre as name, linea, planta FROM activos_equipos;")
            equipos = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT u.id, u.nombre_completo as name, r.nombre as role, u.cargo FROM usuarios u JOIN roles r ON u.rol_id = r.id;")
        users = [dict(r) for r in cursor.fetchall()]

    jefe = next((u["name"] for u in users if "jefe de mantenimiento" in (u.get("cargo") or "").lower() or u.get("role") == "Gerente"), "Ing. Carlos Mendoza")
    gerente = next((u["name"] for u in users if "gerente de planta" in (u.get("cargo") or "").lower()), "Ing. Roberto Navarro")

    docx_bytes = generate_informe_periodico_docx(
        ots=ots,
        equipos=equipos,
        periodo_tipo=periodo_tipo,
        periodo_valor=periodo_valor,
        equipo_filtro=equipo_id,
        nombre_jefe=jefe,
        nombre_gerente=gerente
    )
    safe_periodo = str(periodo_valor).replace("-", "_").replace(" ", "_")
    filename = f"INFORME_PERIODICO_{safe_periodo}.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# --- MÓDULO DE SEGUIMIENTO DE EQUIPOS EN TALLER EXTERNO ---

@app.get("/api/external-services")
def get_external_services():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, equipo_id as equipoId, proveedor_id as proveedorId, proveedor_nombre as proveedorNombre,
                   fecha_salida as fechaSalida, fecha_estimada_retorno as fechaEstimadaRetorno,
                   fecha_retorno_real as fechaRetornoReal, motivo_servicio as motivoServicio,
                   costo_estimado as costoEstimado, costo_final as costoFinal, status,
                   condicion_recepcion as condicionRecepcion, recibido_por as recibidoPor,
                   observaciones, creado_en as creadoEn
            FROM equipos_taller_externo ORDER BY id DESC;
        """)
        return [dict(r) for r in cursor.fetchall()]

@app.post("/api/external-services")
def save_external_service(srv: Dict[str, Any]):
    srv_id = srv.get("id")
    with get_db() as conn:
        cursor = conn.cursor()
        es_nuevo = False
        if not srv_id:
            cursor.execute("SELECT COUNT(*) FROM equipos_taller_externo;")
            count = cursor.fetchone()[0] + 1
            srv_id = f"EXT-2026-{str(count).zfill(3)}"
            srv["id"] = srv_id
            es_nuevo = True

        eq_id = srv.get("equipoId", "").strip()
        registrar_activo = bool(srv.get("registrarComoActivo") or srv.get("agregarAInventario"))
        es_manual = bool(srv.get("esManual", False))

        if registrar_activo and eq_id:
            # Registrar permanentemente en inventario general de activos si no existe
            cursor.execute("SELECT id FROM activos_equipos WHERE id = ? OR nombre = ?;", (eq_id, eq_id))
            row_eq = cursor.fetchone()
            if not row_eq:
                cursor.execute("SELECT COUNT(*) FROM activos_equipos;")
                next_num = cursor.fetchone()[0] + 1
                new_asset_id = f"EQ-{str(next_num).zfill(3)}"
                cursor.execute("""
                    INSERT INTO activos_equipos (id, nombre, planta, linea, subensamble, criticidad, status)
                    VALUES (?, ?, 'Planta Central', 'General', 'General', 'Media', 'En Mantenimiento');
                """, (new_asset_id, eq_id))
                eq_id = new_asset_id
                srv["equipoId"] = new_asset_id
                es_manual = False
            else:
                eq_id = row_eq[0]
                srv["equipoId"] = eq_id

        cursor.execute("""
            INSERT INTO equipos_taller_externo (
                id, equipo_id, proveedor_id, proveedor_nombre, fecha_salida,
                fecha_estimada_retorno, fecha_retorno_real, motivo_servicio,
                costo_estimado, costo_final, status, condicion_recepcion,
                recibido_por, observaciones, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                proveedor_id=excluded.proveedor_id,
                proveedor_nombre=excluded.proveedor_nombre,
                fecha_salida=excluded.fecha_salida,
                fecha_estimada_retorno=excluded.fecha_estimada_retorno,
                fecha_retorno_real=excluded.fecha_retorno_real,
                motivo_servicio=excluded.motivo_servicio,
                costo_estimado=excluded.costo_estimado,
                costo_final=excluded.costo_final,
                status=excluded.status,
                condicion_recepcion=excluded.condicion_recepcion,
                recibido_por=excluded.recibido_por,
                observaciones=excluded.observaciones,
                updated_at=CURRENT_TIMESTAMP;
        """, (
            srv_id,
            eq_id,
            srv.get("proveedorId"),
            srv.get("proveedorNombre", "Taller Externo"),
            srv.get("fechaSalida", datetime.now().strftime("%Y-%m-%d")),
            srv.get("fechaEstimadaRetorno"),
            srv.get("fechaRetornoReal"),
            srv.get("motivoServicio", "Mantenimiento / Reparación Especializada"),
            float(srv.get("costoEstimado") or 0.0),
            float(srv.get("costoFinal") or 0.0),
            srv.get("status", "En diagnóstico"),
            srv.get("condicionRecepcion"),
            srv.get("recibidoPor"),
            srv.get("observaciones")
        ))

        # Al despachar equipo a taller externo, actualizar su estado en planta a En Mantenimiento
        if srv.get("status") != "Recibido en Planta" and eq_id:
            cursor.execute("UPDATE activos_equipos SET status = 'En Mantenimiento', updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (eq_id,))

        if es_nuevo:
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES (?, NULL, 'Gerente', 'Equipo Enviado a Taller Externo', ?, 'info', ?, 'taller-externo', ?);
            """, (notif_id, f"El equipo {eq_id} fue enviado a {srv.get('proveedorNombre')}: {srv.get('motivoServicio')[:50]}", datetime.now().strftime("%Y-%m-%d %H:%M"), srv_id))

        conn.commit()
    return {"success": True, "id": srv_id}

@app.post("/api/external-services/{service_id}/reception")
def receive_external_service(service_id: str, payload: Dict[str, Any]):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT equipo_id FROM equipos_taller_externo WHERE id = ?;", (service_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Registro de taller externo no encontrado")
        eq_id = row["equipo_id"]

        f_retorno = payload.get("fechaRetornoReal") or datetime.now().strftime("%Y-%m-%d")
        condicion = payload.get("condicionRecepcion", "Conforme")
        recibido_por = payload.get("recibidoPor", "Jefe de Mantenimiento")
        costo_final = float(payload.get("costoFinal") or 0.0)
        obs = payload.get("observaciones", "")

        cursor.execute("""
            UPDATE equipos_taller_externo
            SET status = 'Recibido en Planta',
                fecha_retorno_real = ?,
                condicion_recepcion = ?,
                recibido_por = ?,
                costo_final = ?,
                observaciones = CASE WHEN ? != '' THEN observaciones || ' | Recepción: ' || ? ELSE observaciones END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (f_retorno, condicion, recibido_por, costo_final, obs, obs, service_id))

        # Reincorporar equipo a estatus Operativo
        if eq_id:
            cursor.execute("UPDATE activos_equipos SET status = 'Operativo', updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (eq_id,))

        # Notificar recepción
        notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
            VALUES (?, NULL, 'Gerente', 'Equipo Recibido de Taller Externo', ?, 'success', ?, 'taller-externo', ?);
        """, (notif_id, f"Equipo {eq_id} recibido en planta conforme de taller externo por {recibido_por}.", datetime.now().strftime("%Y-%m-%d %H:%M"), service_id))

        conn.commit()
    notify_clients()
    return {"success": True, "message": f"Equipo {eq_id} reincorporado a planta operativamente"}

@app.delete("/api/external-services/{service_id}")
def delete_external_service(service_id: str):
    """Elimina un registro de envío a taller externo."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM equipos_taller_externo WHERE id = ?;", (service_id,))
        conn.commit()
    notify_clients()
    return {"success": True, "id": service_id}

# --- SALIDAS DE MATERIALES Y REPUESTOS (ROL ALMACENISTA) ---

@app.get("/api/inventory/dispatches")
def get_inventory_dispatches():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, fecha, ot_id as otId, solicitud_id as solicitudId,
                   repuesto_id as repuestoId, repuesto_nombre as repuestoNombre,
                   cantidad, despachado_por as despachadoPor, receptor, observaciones
            FROM salidas_materiales ORDER BY id DESC;
        """)
        return [dict(r) for r in cursor.fetchall()]

@app.post("/api/inventory/dispatches")
def create_inventory_dispatch(disp: Dict[str, Any]):
    with get_db() as conn:
        cursor = conn.cursor()
        rep_id = disp.get("repuestoId")
        cant = int(disp.get("cantidad") or 1)

        cursor.execute("SELECT id, codigo, nombre, stock, stock_minimo as stockMin, unidad_medida as um, costo_unitario as costo FROM repuestos_materiales WHERE id = ?;", (rep_id,))
        rep = cursor.fetchone()
        if not rep:
            raise HTTPException(status_code=404, detail="Repuesto no encontrado en catálogo de almacén")

        stock_actual = int(rep["stock"])
        if stock_actual < cant:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente ({stock_actual} disponibles) para despachar {cant} unidades")

        nuevo_stock = stock_actual - cant
        cursor.execute("UPDATE repuestos_materiales SET stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (nuevo_stock, rep_id))

        cursor.execute("SELECT COUNT(*) FROM salidas_materiales;")
        count = cursor.fetchone()[0] + 1
        disp_id = f"SAL-2026-{str(count).zfill(3)}"

        ot_id = disp.get("otId")
        sol_id = disp.get("solicitudId")

        cursor.execute("""
            INSERT INTO salidas_materiales (
                id, fecha, ot_id, solicitud_id, repuesto_id, repuesto_nombre,
                cantidad, despachado_por, receptor, observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            disp_id,
            disp.get("fecha", datetime.now().strftime("%Y-%m-%d %H:%M")),
            ot_id,
            sol_id,
            rep_id,
            rep["nombre"],
            cant,
            disp.get("despachadoPor", "Almacenista"),
            disp.get("receptor", "Técnico Ejecutor"),
            disp.get("observaciones")
        ))

        # Si está vinculado a una OT, añadir a su lista de repuestos usados
        if ot_id:
            cursor.execute("SELECT repuestos_usados FROM ordenes_trabajo WHERE id = ?;", (ot_id,))
            ot_row = cursor.fetchone()
            if ot_row:
                reps_list = json.loads(ot_row["repuestos_usados"] or "[]")
                reps_list.append({"id": rep_id, "name": rep["nombre"], "cant": cant, "costo": float(rep["costo"])})
                cursor.execute("UPDATE ordenes_trabajo SET repuestos_usados = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (json.dumps(reps_list), ot_id))

        # Si está vinculado a una Solicitud en espera de materiales, pasarla automáticamente a En proceso
        if sol_id:
            cursor.execute("""
                UPDATE solicitudes_mantenimiento
                SET status = 'En proceso', updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'En espera de materiales';
            """, (sol_id,))

        # Si el stock llegó al mínimo, disparar notificación
        if nuevo_stock <= int(rep["stockMin"]):
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES (?, NULL, 'Gerente', 'Alerta de Stock Mínimo', ?, 'warning', ?, 'almacen', ?);
            """, (notif_id, f"El repuesto {rep['nombre']} ha llegado a su stock mínimo ({nuevo_stock} {rep['um']}).", datetime.now().strftime("%Y-%m-%d %H:%M"), rep_id))

        conn.commit()
    notify_clients()
    return {"success": True, "id": disp_id, "nuevoStock": nuevo_stock}

@app.delete("/api/inventory/dispatches/{dispatch_id}")
def delete_inventory_dispatch(dispatch_id: str):
    """Elimina un registro de salida de materiales y reintegra el stock al almacén."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT repuesto_id, cantidad FROM salidas_materiales WHERE id = ?;", (dispatch_id,))
        row = cursor.fetchone()
        if row and row["repuesto_id"]:
            cursor.execute("UPDATE repuestos_materiales SET stock = stock + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;", (int(row["cantidad"]), row["repuesto_id"]))
        cursor.execute("DELETE FROM salidas_materiales WHERE id = ?;", (dispatch_id,))
        conn.commit()
    notify_clients()
    return {"success": True, "id": dispatch_id}

# --- 8. SOLICITUDES INTERDEPARTAMENTALES (FLUJO DE 4 ESTADOS ESTRICTOS) ---

VALID_SOLICITUD_STATUSES = ["Aprobada", "En espera de materiales", "En proceso", "Culminada"]

@app.get("/api/solicitudes")
def get_solicitudes():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo, urgencia, area, ubicacion, descripcion, solicitante, fecha_hora as fechaHora, status, ot_vinculada as otVinculada FROM solicitudes_mantenimiento ORDER BY id DESC;")
        return [dict(r) for r in cursor.fetchall()]

@app.post("/api/solicitudes")
def save_solicitud(sol: Dict[str, Any]):
    sol_id = sol.get("id")
    status_val = sol.get("status", "Aprobada")
    if status_val not in VALID_SOLICITUD_STATUSES:
        status_val = "Aprobada"

    with get_db() as conn:
        cursor = conn.cursor()
        if sol_id:
            cursor.execute("SELECT 1 FROM solicitudes_mantenimiento WHERE id = ?;", (sol_id,))
            es_nueva = (cursor.fetchone() is None)
        else:
            cursor.execute("SELECT COUNT(*) FROM solicitudes_mantenimiento;")
            count = cursor.fetchone()[0] + 1
            sol_id = f"SOL-2026-{str(count).zfill(3)}"
            sol["id"] = sol_id
            es_nueva = True

        cursor.execute("""
            INSERT INTO solicitudes_mantenimiento (
                id, tipo, urgencia, area, ubicacion, descripcion, solicitante, fecha_hora, status, ot_vinculada, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                tipo=excluded.tipo,
                urgencia=excluded.urgencia,
                area=excluded.area,
                ubicacion=excluded.ubicacion,
                descripcion=excluded.descripcion,
                solicitante=excluded.solicitante,
                status=excluded.status,
                ot_vinculada=excluded.ot_vinculada,
                updated_at=CURRENT_TIMESTAMP;
        """, (
            sol_id,
            sol.get("tipo", "Maquinaria / Equipo"),
            sol.get("urgencia", "Media"),
            sol.get("area", ""),
            sol.get("ubicacion", ""),
            sol.get("descripcion", ""),
            sol.get("solicitante", "Producción"),
            sol.get("fechaHora", datetime.now().strftime("%Y-%m-%d %H:%M")),
            status_val,
            sol.get("otVinculada")
        ))

        # Notificar al Jefe de Mantenimiento si es nueva solicitud
        if es_nueva:
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES (?, NULL, 'Gerente', 'Nueva Solicitud Interdepartamental', ?, 'warning', ?, 'solicitud', ?);
            """, (notif_id, f"Nueva solicitud emitida por {sol.get('solicitante')}: {sol.get('descripcion')[:60]}", datetime.now().strftime("%Y-%m-%d %H:%M"), sol_id))
        else:
            # Sincronización bidireccional estricta: Notificar al Solicitante sobre actualización
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES (?, NULL, 'Solicitante', 'Actualización de Solicitud de Mantenimiento', ?, 'info', ?, 'solicitud', ?);
            """, (notif_id, f"Su solicitud {sol_id} ha sido actualizada: Estado '{status_val}'.", datetime.now().strftime("%Y-%m-%d %H:%M"), sol_id))

        conn.commit()
    return {"success": True, "id": sol_id}

@app.delete("/api/solicitudes/{sol_id}")
def delete_solicitud(sol_id: str):
    """Elimina una solicitud interdepartamental y desvincula registros asociados."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE salidas_materiales SET solicitud_id = NULL WHERE solicitud_id = ?;", (sol_id,))
        cursor.execute("DELETE FROM notificaciones WHERE (enlace_tipo = 'solicitud' AND enlace_id = ?) OR mensaje LIKE ?;", (sol_id, f"%{sol_id}%"))
        cursor.execute("DELETE FROM solicitudes_mantenimiento WHERE id = ?;", (sol_id,))
        conn.commit()
    notify_clients()
    return {"success": True, "id": sol_id}

# --- 9. MÓDULO SSL (CONDICIONES INSEGURAS - JEFE SSL) ---

@app.get("/api/ssl")
def get_ssl_requests():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, codigo, fecha_hora as fechaHora, area, ubicacion, equipo_id as equipoId,
                   nivel_riesgo as nivelRiesgo, descripcion, accion_propuesta as accionPropuesta,
                   solicitante_id as solicitanteId, solicitante_nombre as solicitanteNombre,
                   foto_evidencia as fotoEvidencia, status, fecha_correccion as fechaCorreccion,
                   ot_vinculada as otVinculada, observaciones_cierre as observacionesCierre
            FROM solicitudes_ssl ORDER BY id DESC;
        """)
        return [dict(r) for r in cursor.fetchall()]

@app.post("/api/ssl")
def save_ssl_request(ssl_req: Dict[str, Any]):
    ssl_id = ssl_req.get("id")
    foto = ssl_req.get("fotoEvidencia", "").strip()
    if not foto:
        raise HTTPException(status_code=400, detail="La carga de fotografía de evidencia es obligatoria para Solicitudes SSL")

    with get_db() as conn:
        cursor = conn.cursor()
        if ssl_id:
            cursor.execute("SELECT 1 FROM solicitudes_ssl WHERE id = ?;", (ssl_id,))
            es_nueva = (cursor.fetchone() is None)
        else:
            cursor.execute("SELECT COUNT(*) FROM solicitudes_ssl;")
            count = cursor.fetchone()[0] + 1
            ssl_id = f"SSL-2026-{str(count).zfill(3)}"
            ssl_req["id"] = ssl_id
            es_nueva = True

        cursor.execute("""
            INSERT INTO solicitudes_ssl (
                id, codigo, fecha_hora, area, ubicacion, equipo_id, nivel_riesgo, descripcion,
                accion_propuesta, solicitante_id, solicitante_nombre, foto_evidencia, status,
                fecha_correccion, ot_vinculada, observaciones_cierre, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                codigo=excluded.codigo,
                area=excluded.area,
                ubicacion=excluded.ubicacion,
                equipo_id=excluded.equipo_id,
                nivel_riesgo=excluded.nivel_riesgo,
                descripcion=excluded.descripcion,
                accion_propuesta=excluded.accion_propuesta,
                foto_evidencia=excluded.foto_evidencia,
                status=excluded.status,
                fecha_correccion=excluded.fecha_correccion,
                ot_vinculada=excluded.ot_vinculada,
                observaciones_cierre=excluded.observaciones_cierre,
                updated_at=CURRENT_TIMESTAMP;
        """, (
            ssl_id,
            ssl_req.get("codigo", f"COND-{ssl_id[-3:]}"),
            ssl_req.get("fechaHora", datetime.now().strftime("%Y-%m-%d %H:%M")),
            ssl_req.get("area", ""),
            ssl_req.get("ubicacion", ""),
            ssl_req.get("equipoId"),
            ssl_req.get("nivelRiesgo", "Alto"),
            ssl_req.get("descripcion", ""),
            ssl_req.get("accionPropuesta", ""),
            ssl_req.get("solicitanteId"),
            ssl_req.get("solicitanteNombre", "Jefe SSL"),
            foto,
            ssl_req.get("status", "Pendiente"),
            ssl_req.get("fechaCorreccion"),
            ssl_req.get("otVinculada"),
            ssl_req.get("observacionesCierre")
        ))

        # Notificaciones:
        if es_nueva:
            # Notificar al Jefe de Mantenimiento sobre condición insegura
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES (?, NULL, 'Gerente', 'Condición Insegura Reportada (SSL)', ?, 'urgent', ?, 'ssl', ?);
            """, (notif_id, f"Jefe SSL reportó condición {ssl_req.get('nivelRiesgo')} en {ssl_req.get('area')}: {ssl_req.get('descripcion')[:60]}", datetime.now().strftime("%Y-%m-%d %H:%M"), ssl_id))
        else:
            # Sincronización bidireccional estricta: Notificar al Jefe SSL ante cualquier cambio de estado
            notif_id = f"NOTIF-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES (?, ?, 'Jefe SSL', 'Actualización de Condición SSL', ?, 'info', ?, 'ssl', ?);
            """, (notif_id, ssl_req.get("solicitanteId"), f"La condición {ssl_id} ha sido actualizada: Estado '{ssl_req.get('status')}'.", datetime.now().strftime("%Y-%m-%d %H:%M"), ssl_id))

        conn.commit()
    return {"success": True, "id": ssl_id}

@app.delete("/api/ssl/{ssl_id}")
def delete_ssl_request(ssl_id: str):
    """Elimina una condición insegura SSL y sus notificaciones asociadas."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notificaciones WHERE (enlace_tipo = 'ssl' AND enlace_id = ?) OR mensaje LIKE ?;", (ssl_id, f"%{ssl_id}%"))
        cursor.execute("DELETE FROM solicitudes_ssl WHERE id = ?;", (ssl_id,))
        conn.commit()
    notify_clients()
    return {"success": True, "id": ssl_id}

# --- 10. MOTOR DE NOTIFICACIONES ---

@app.get("/api/notificaciones")
def get_notificaciones(rol: Optional[str] = None, usuario_id: Optional[str] = None):
    # Asegurar tipos si es invocado directamente o vía FastAPI
    if not isinstance(rol, str): rol = None
    if not isinstance(usuario_id, str): usuario_id = None
    with get_db() as conn:
        cursor = conn.cursor()
        # Filtro de alertas activas y exclusión reactiva de OTs y planes ya concluidos
        base_filter = """
            COALESCE(activa, 1) = 1
            AND NOT (
                enlace_tipo = 'ot' AND enlace_id IN (SELECT id FROM ordenes_trabajo WHERE status IN ('Concluida', 'Completada'))
                AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent'))
            )
            AND NOT (
                enlace_tipo IN ('plan', 'cronograma-anual') AND enlace_id IN (SELECT id FROM planes_preventivos WHERE status IN ('Completado', 'Ejecutado'))
                AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent'))
            )
        """
        if rol == "Tecnico":
            query = f"""
                SELECT id, usuario_id as usuarioId, rol_destino as rolDestino, titulo, mensaje, tipo, leido, fecha_hora as fechaHora, enlace_tipo as enlaceTipo, enlace_id as enlaceId, COALESCE(activa, 1) as activa
                FROM notificaciones
                WHERE {base_filter}
                  AND (usuario_id = ? OR (rol_destino = 'Tecnico' AND (usuario_id IS NULL OR usuario_id = ?)))
                  AND (enlace_tipo IN ('ot', 'tarea', 'actividad') OR titulo LIKE '%Orden%' OR titulo LIKE '%OT%' OR titulo LIKE '%Tarea%' OR titulo LIKE '%Asignad%')
                ORDER BY fecha_hora DESC LIMIT 50;
            """
            cursor.execute(query, (usuario_id or "", usuario_id or ""))
            return [dict(r) for r in cursor.fetchall()]

        query = f"SELECT id, usuario_id as usuarioId, rol_destino as rolDestino, titulo, mensaje, tipo, leido, fecha_hora as fechaHora, enlace_tipo as enlaceTipo, enlace_id as enlaceId, COALESCE(activa, 1) as activa FROM notificaciones WHERE {base_filter}"
        params = []
        if rol and usuario_id:
            query += " AND (rol_destino = ? OR usuario_id = ? OR (rol_destino IS NULL AND ? = 'Gerente'))"
            params.extend([rol, usuario_id, rol])
        elif rol:
            query += " AND (rol_destino = ? OR (rol_destino IS NULL AND ? = 'Gerente'))"
            params.extend([rol, rol])
        elif usuario_id:
            query += " AND (usuario_id = ?)"
            params.append(usuario_id)

        query += " ORDER BY fecha_hora DESC LIMIT 50;"
        cursor.execute(query, params)
        return [dict(r) for r in cursor.fetchall()]

@app.post("/api/notificaciones/{notif_id}/marcar-leida")
def mark_notification_read(notif_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE notificaciones SET leido = 1 WHERE id = ?;", (notif_id,))
        conn.commit()
    return {"success": True}

@app.post("/api/notificaciones/marcar-todas")
def mark_all_notifications_read():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE notificaciones SET leido = 1;")
        conn.commit()
    notify_clients()
    return {"success": True}

@app.delete("/api/notificaciones/limpiar")
def clear_notifications(rol: Optional[str] = None, usuario_id: Optional[str] = None):
    """Elimina las notificaciones del usuario o rol solicitante."""
    with get_db() as conn:
        cursor = conn.cursor()
        if rol == "Tecnico" and usuario_id:
            cursor.execute("DELETE FROM notificaciones WHERE usuario_id = ? OR (rol_destino = 'Tecnico' AND (usuario_id IS NULL OR usuario_id = ?));", (usuario_id, usuario_id))
        elif rol and rol != "Gerente":
            cursor.execute("DELETE FROM notificaciones WHERE rol_destino = ? OR usuario_id = ?;", (rol, usuario_id or ""))
        elif usuario_id and rol != "Gerente":
            cursor.execute("DELETE FROM notificaciones WHERE usuario_id = ?;", (usuario_id,))
        else:
            # Gerente o limpieza global
            cursor.execute("DELETE FROM notificaciones;")
        conn.commit()
    notify_clients()
    return {"success": True}

# --- 11. ENDPOINTS DE PLANES PREVENTIVOS ---

@app.get("/api/preventive-plans")
def get_preventive_plans():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, equipo_id as equipoId, nombre, frecuencia, frecuencia_tipo as frecuenciaTipo, frecuencia_valor as frecuenciaValor, ultima_fecha as ultimaFecha, proxima_fecha as proximaFecha, tecnicos_ids, es_refrigeracion as esRefrigeracion, COALESCE(status, 'Pendiente') as status FROM planes_preventivos ORDER BY id;")
        rows = []
        for r in cursor.fetchall():
            d = dict(r)
            try:
                d["tecnicoIds"] = json.loads(d.pop("tecnicos_ids") or "[]")
            except:
                d["tecnicoIds"] = []
            rows.append(d)
        return rows

@app.post("/api/preventive-plans")
def save_preventive_plan(plan: Dict[str, Any]):
    p_id = plan.get("id")
    with get_db() as conn:
        cursor = conn.cursor()
        if not p_id:
            prefix = "PLR" if plan.get("esRefrigeracion") else "PLN"
            cursor.execute("SELECT COUNT(*) FROM planes_preventivos WHERE es_refrigeracion = ?;", (bool(plan.get("esRefrigeracion")),))
            count = cursor.fetchone()[0] + 1
            p_id = f"{prefix}-{str(count).zfill(2)}"
            plan["id"] = p_id

        cursor.execute("""
            INSERT INTO planes_preventivos (
                id, equipo_id, nombre, frecuencia, frecuencia_tipo, frecuencia_valor,
                ultima_fecha, proxima_fecha, tecnicos_ids, es_refrigeracion, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                equipo_id=excluded.equipo_id,
                nombre=excluded.nombre,
                frecuencia=excluded.frecuencia,
                frecuencia_tipo=excluded.frecuencia_tipo,
                frecuencia_valor=excluded.frecuencia_valor,
                ultima_fecha=excluded.ultima_fecha,
                proxima_fecha=excluded.proxima_fecha,
                tecnicos_ids=excluded.tecnicos_ids,
                updated_at=CURRENT_TIMESTAMP;
        """, (
            p_id,
            plan.get("equipoId", ""),
            plan.get("nombre", ""),
            plan.get("frecuencia", "Mensual"),
            plan.get("frecuenciaTipo", "meses"),
            int(plan.get("frecuenciaValor") or 1),
            plan.get("ultimaFecha", datetime.now().strftime("%Y-%m-%d")),
            plan.get("proximaFecha", datetime.now().strftime("%Y-%m-%d")),
            json.dumps(plan.get("tecnicoIds", [])),
            bool(plan.get("esRefrigeracion", False))
        ))
        conn.commit()
    return {"success": True, "id": p_id}

@app.delete("/api/preventive-plans/{plan_id}")
def delete_preventive_plan(plan_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM planes_preventivos WHERE id = ?;", (plan_id,))
        conn.commit()
    return {"success": True}

# --- 12. ENDPOINT DE SINCRONIZACIÓN MAESTRA ROBUSTA (/api/sync) ---

@app.get("/api/sync")
def get_full_sync():
    """Retorna el estado consolidado de la base de datos para clientes móviles y offline."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT u.id, u.username, u.nombre_completo as name, r.nombre as role, u.password_hash as pass, u.departamento, u.cargo FROM usuarios u JOIN roles r ON u.rol_id = r.id;")
        users = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, nombre as name, planta, linea, subensamble, criticidad, status, es_refrigeracion, tipo_refrigerante FROM activos_equipos;")
        equipos = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, codigo, nombre as name, stock, stock_minimo as stockMin, unidad_medida as um, costo_unitario as costo, proveedor_id as proveedorId FROM repuestos_materiales;")
        repuestos = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, rif, nombre, categoria, contacto, telefono, email FROM proveedores;")
        proveedores = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, fecha, descripcion, cant_solicitada as cantSolicitada, cant_recibida as cantRecibida, moneda, precio, proveedor_id as proveedorId, observaciones, COALESCE(status, 'Pendiente') as status FROM compras_materiales;")
        compras = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, equipo_id as equipoId, nombre, frecuencia, frecuencia_tipo as frecuenciaTipo, frecuencia_valor as frecuenciaValor, ultima_fecha as ultimaFecha, proxima_fecha as proximaFecha, tecnicos_ids, es_refrigeracion, COALESCE(status, 'Pendiente') as status FROM planes_preventivos;")
        planes_raw = [dict(r) for r in cursor.fetchall()]
        planes_prev = []
        planes_refr = []
        for p in planes_raw:
            p["tecnicoIds"] = json.loads(p.pop("tecnicos_ids") or "[]")
            if p.get("es_refrigeracion"):
                planes_refr.append(p)
            else:
                planes_prev.append(p)

        cursor.execute("SELECT id, tipo, urgencia, area, ubicacion, descripcion, solicitante, fecha_hora as fechaHora, status, ot_vinculada as otVinculada FROM solicitudes_mantenimiento;")
        solicitudes = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT id, tipo, prioridad, equipo_id as equipoId, descripcion, tecnicos_ids, tecnico_acompanante as tecnicoAcompanante, fecha_asignacion as fechaAsignacion, fecha_programada as fechaProgramada, fecha_inicio as fechaInicio, fecha_fin as fechaFin, status, actividades, tiempo_intervencion as tiempoIntervencion, tiempo_parada as tiempoParada, foto_antes as fotoAntes, foto_despues as fotoDespues, repuestos_usados FROM ordenes_trabajo;")
        ots = []
        for r in cursor.fetchall():
            d = dict(r)
            d["tecnicoIds"] = json.loads(d.pop("tecnicos_ids") or "[]")
            d["repuestosUsados"] = json.loads(d.pop("repuestos_usados") or "[]")
            ots.append(d)

        cursor.execute("SELECT id, codigo, fecha_hora as fechaHora, area, ubicacion, equipo_id as equipoId, nivel_riesgo as nivelRiesgo, descripcion, accion_propuesta as accionPropuesta, solicitante_id as solicitanteId, solicitante_nombre as solicitanteNombre, foto_evidencia as fotoEvidencia, status, fecha_correccion as fechaCorreccion, ot_vinculada as otVinculada, observaciones_cierre as observacionesCierre FROM solicitudes_ssl;")
        solicitudes_ssl = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT id, equipo_id as equipoId, proveedor_id as proveedorId, proveedor_nombre as proveedorNombre,
                   fecha_salida as fechaSalida, fecha_estimada_retorno as fechaEstimadaRetorno,
                   fecha_retorno_real as fechaRetornoReal, motivo_servicio as motivoServicio,
                   costo_estimado as costoEstimado, costo_final as costoFinal, status,
                   condicion_recepcion as condicionRecepcion, recibido_por as recibidoPor,
                   observaciones, creado_en as creadoEn
            FROM equipos_taller_externo ORDER BY id DESC;
        """)
        equipos_taller = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT id, fecha, ot_id as otId, solicitud_id as solicitudId,
                   repuesto_id as repuestoId, repuesto_nombre as repuestoNombre,
                   cantidad, despachado_por as despachadoPor, receptor, observaciones
            FROM salidas_materiales ORDER BY fecha DESC;
        """)
        salidas_materiales = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT id, usuario_id as usuarioId, rol_destino as rolDestino, titulo, mensaje, tipo, leido, fecha_hora as fechaHora, enlace_tipo as enlaceTipo, enlace_id as enlaceId, COALESCE(activa, 1) as activa
            FROM notificaciones
            WHERE COALESCE(activa, 1) = 1
              AND NOT (
                  enlace_tipo = 'ot' AND enlace_id IN (SELECT id FROM ordenes_trabajo WHERE status IN ('Concluida', 'Completada'))
                  AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent'))
              )
              AND NOT (
                  enlace_tipo IN ('plan', 'cronograma-anual') AND enlace_id IN (SELECT id FROM planes_preventivos WHERE status IN ('Completado', 'Ejecutado'))
                  AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent'))
              )
            ORDER BY fecha_hora DESC LIMIT 50;
        """)
        notificaciones = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT clave, valor, descripcion FROM configuracion_sistema;")
        config_rows = cursor.fetchall()
        config_dict = {r["clave"]: r["valor"] for r in config_rows}

        return {
            "success": True,
            "data": {
                "users": users,
                "equipos": equipos,
                "repuestos": repuestos,
                "proveedores": proveedores,
                "comprasMateriales": compras,
                "planesPreventivos": planes_prev,
                "planesRefrigeracion": planes_refr,
                "solicitudesInterdepartamentales": solicitudes,
                "ots": ots,
                "solicitudesSSL": solicitudes_ssl,
                "equiposTallerExterno": equipos_taller,
                "salidasMateriales": salidas_materiales,
                "notificaciones": notificaciones,
                "config": config_dict,
                "syncTimestamp": datetime.now().isoformat()
            }
        }

@app.post("/api/sync")
def post_full_sync(payload: Dict[str, Any]):
    """Persiste y reconcilia la base de datos enviada desde cualquier dispositivo (PC / Android Offline)."""
    data = payload
    if not data or not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Estructura de datos inválida")

    with get_db() as conn:
        cursor = conn.cursor()

        # 0. Actualizar usuarios en la BD central si vienen en payload de sincronización
        role_map = {
            "Gerente": "ROL-GER",
            "Tecnico": "ROL-TEC",
            "Solicitante": "ROL-SOL",
            "Jefe SSL": "ROL-SSL",
            "Almacenista": "ROL-ALM"
        }
        for u in data.get("users", []):
            u_id = u.get("id") or f"u{uuid.uuid4().hex[:6]}"
            u_user = u.get("username", "").strip()
            if not u_user:
                continue
            u_name = u.get("name") or u.get("nombre_completo") or u_user
            u_pass = u.get("pass") or u.get("password") or "1234"
            u_role = u.get("role") or u.get("rol") or "Tecnico"
            u_dept = u.get("departamento") or "Mantenimiento"
            u_cargo = u.get("cargo") or u_role
            rol_id = role_map.get(u_role, "ROL-TEC")
            cursor.execute("""
                INSERT INTO usuarios (id, username, password_hash, nombre_completo, email, rol_id, cargo, departamento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username=excluded.username,
                    password_hash=excluded.password_hash,
                    nombre_completo=excluded.nombre_completo,
                    rol_id=excluded.rol_id,
                    cargo=excluded.cargo,
                    departamento=excluded.departamento;
            """, (u_id, u_user, u_pass, u_name, f"{u_user}@empresa.com", rol_id, u_cargo, u_dept))

        # 0.1 Actualizar proveedores
        for p in data.get("proveedores", []):
            cursor.execute("""
                INSERT INTO proveedores (id, rif, nombre, categoria, contacto, telefono, email, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    rif=excluded.rif, nombre=excluded.nombre, categoria=excluded.categoria,
                    contacto=excluded.contacto, telefono=excluded.telefono, email=excluded.email,
                    updated_at=CURRENT_TIMESTAMP;
            """, (p["id"], p.get("rif", "J-00000000-0"), p.get("nombre", ""), p.get("categoria", "General"), p.get("contacto", ""), p.get("telefono", ""), p.get("email", "")))

        # Actualizar configuración del sistema si viene en payload
        if "config" in data and isinstance(data["config"], dict):
            for k, v in data["config"].items():
                cursor.execute("""
                    INSERT INTO configuracion_sistema (clave, valor, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor, updated_at=CURRENT_TIMESTAMP;
                """, (str(k), str(v)))

        # Actualizar equipos
        for eq in data.get("equipos", []):
            cursor.execute("""
                INSERT INTO activos_equipos (id, nombre, planta, linea, subensamble, criticidad, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    nombre=excluded.nombre, planta=excluded.planta, linea=excluded.linea,
                    criticidad=excluded.criticidad, status=excluded.status, updated_at=CURRENT_TIMESTAMP;
            """, (eq["id"], eq["name"], eq.get("planta", "Planta Central"), eq.get("linea", "General"), eq.get("subensamble", "General"), eq.get("criticidad", "Media"), eq.get("status", "Operativo")))

        # Actualizar repuestos
        for r in data.get("repuestos", []):
            cursor.execute("""
                INSERT INTO repuestos_materiales (id, codigo, nombre, stock, stock_minimo, unidad_medida, costo_unitario, proveedor_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    codigo=excluded.codigo, nombre=excluded.nombre, stock=excluded.stock,
                    stock_minimo=excluded.stock_minimo, costo_unitario=excluded.costo_unitario, updated_at=CURRENT_TIMESTAMP;
            """, (r["id"], r["codigo"], r["name"], int(r.get("stock", 0)), int(r.get("stockMin", 2)), r.get("um", "pza"), float(r.get("costo", 0.0)), r.get("proveedorId")))

        # Actualizar compras de materiales
        for c in data.get("comprasMateriales", []):
            cursor.execute("""
                INSERT INTO compras_materiales (
                    id, fecha, descripcion, cant_solicitada, cant_recibida, moneda, precio, proveedor_id, observaciones, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    fecha=excluded.fecha,
                    descripcion=excluded.descripcion,
                    cant_solicitada=excluded.cant_solicitada,
                    cant_recibida=excluded.cant_recibida,
                    precio=excluded.precio,
                    proveedor_id=excluded.proveedor_id,
                    observaciones=excluded.observaciones,
                    updated_at=CURRENT_TIMESTAMP;
            """, (
                c["id"], c.get("fecha", datetime.now().strftime("%Y-%m-%d")), c.get("descripcion", ""),
                int(c.get("cantSolicitada", 1)), int(c.get("cantRecibida", 0)), c.get("moneda", "$"),
                float(c.get("precio", 0.0)), c.get("proveedorId"), c.get("observaciones", "")
            ))

        # Actualizar planes preventivos
        todos_planes = data.get("planesPreventivos", []) + data.get("planesRefrigeracion", [])
        for p in todos_planes:
            cursor.execute("""
                INSERT INTO planes_preventivos (
                    id, equipo_id, nombre, frecuencia, frecuencia_tipo, frecuencia_valor,
                    ultima_fecha, proxima_fecha, tecnicos_ids, es_refrigeracion, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    equipo_id=excluded.equipo_id,
                    nombre=excluded.nombre,
                    frecuencia=excluded.frecuencia,
                    frecuencia_tipo=excluded.frecuencia_tipo,
                    frecuencia_valor=excluded.frecuencia_valor,
                    ultima_fecha=excluded.ultima_fecha,
                    proxima_fecha=excluded.proxima_fecha,
                    tecnicos_ids=excluded.tecnicos_ids,
                    updated_at=CURRENT_TIMESTAMP;
            """, (
                p["id"], p.get("equipoId", ""), p.get("nombre", ""), p.get("frecuencia", "Mensual"),
                p.get("frecuenciaTipo", "meses"), int(p.get("frecuenciaValor") or 1),
                p.get("ultimaFecha", datetime.now().strftime("%Y-%m-%d")),
                p.get("proximaFecha", datetime.now().strftime("%Y-%m-%d")),
                json.dumps(p.get("tecnicoIds", [])),
                bool(p.get("esRefrigeracion", False))
            ))

        # Actualizar OTs con persistencia de TODOS los campos
        for ot in data.get("ots", []):
            cursor.execute("""
                INSERT INTO ordenes_trabajo (
                    id, tipo, prioridad, equipo_id, descripcion, tecnicos_ids, tecnico_acompanante,
                    fecha_asignacion, fecha_programada, fecha_inicio, fecha_fin, status,
                    actividades, tiempo_intervencion, tiempo_parada, foto_antes, foto_despues, repuestos_usados, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    tipo=excluded.tipo,
                    prioridad=excluded.prioridad,
                    equipo_id=excluded.equipo_id,
                    descripcion=excluded.descripcion,
                    tecnicos_ids=excluded.tecnicos_ids,
                    tecnico_acompanante=excluded.tecnico_acompanante,
                    fecha_asignacion=excluded.fecha_asignacion,
                    fecha_programada=excluded.fecha_programada,
                    fecha_inicio=excluded.fecha_inicio,
                    fecha_fin=excluded.fecha_fin,
                    status=excluded.status,
                    actividades=excluded.actividades,
                    tiempo_intervencion=excluded.tiempo_intervencion,
                    tiempo_parada=excluded.tiempo_parada,
                    foto_antes=excluded.foto_antes,
                    foto_despues=excluded.foto_despues,
                    repuestos_usados=excluded.repuestos_usados,
                    updated_at=CURRENT_TIMESTAMP;
            """, (
                ot["id"], ot.get("tipo", "Correctivo"), ot.get("prioridad", "Media"), ot.get("equipoId", ""),
                ot.get("descripcion", ""), json.dumps(ot.get("tecnicoIds", [])), ot.get("tecnicoAcompanante", ""),
                ot.get("fechaAsignacion", "2026-11-01"), ot.get("fechaProgramada", "2026-11-01"),
                ot.get("fechaInicio", ""), ot.get("fechaFin", ""), ot.get("status", "Pendiente"),
                ot.get("actividades", ""), float(ot.get("tiempoIntervencion") or 0.0), float(ot.get("tiempoParada") or 0.0),
                ot.get("fotoAntes", ""), ot.get("fotoDespues", ""), json.dumps(ot.get("repuestosUsados", []))
            ))

        # Actualizar Solicitudes Interdepartamentales
        for s in data.get("solicitudesInterdepartamentales", []):
            st = s.get("status", "Aprobada")
            if st not in VALID_SOLICITUD_STATUSES:
                st = "Aprobada"
            cursor.execute("""
                INSERT INTO solicitudes_mantenimiento (id, tipo, urgencia, area, ubicacion, descripcion, solicitante, fecha_hora, status, ot_vinculada, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET status=excluded.status, ot_vinculada=excluded.ot_vinculada, updated_at=CURRENT_TIMESTAMP;
            """, (s["id"], s.get("tipo", "Maquinaria / Equipo"), s.get("urgencia", "Media"), s.get("area", ""), s.get("ubicacion", ""), s.get("descripcion", ""), s.get("solicitante", "Producción"), s.get("fechaHora", ""), st, s.get("otVinculada")))

        # Actualizar Solicitudes SSL
        for ssl in data.get("solicitudesSSL", []):
            if ssl.get("fotoEvidencia"):
                cursor.execute("""
                    INSERT INTO solicitudes_ssl (
                        id, codigo, fecha_hora, area, ubicacion, equipo_id, nivel_riesgo, descripcion,
                        accion_propuesta, solicitante_id, solicitante_nombre, foto_evidencia, status,
                        fecha_correccion, ot_vinculada, observaciones_cierre, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(id) DO UPDATE SET
                        status=excluded.status, fecha_correccion=excluded.fecha_correccion,
                        ot_vinculada=excluded.ot_vinculada, observaciones_cierre=excluded.observaciones_cierre,
                        updated_at=CURRENT_TIMESTAMP;
                """, (
                    ssl["id"], ssl.get("codigo", f"COND-{ssl['id'][-3:]}"), ssl.get("fechaHora", ""),
                    ssl.get("area", ""), ssl.get("ubicacion", ""), ssl.get("equipoId"),
                    ssl.get("nivelRiesgo", "Alto"), ssl.get("descripcion", ""), ssl.get("accionPropuesta", ""),
                    ssl.get("solicitanteId"), ssl.get("solicitanteNombre", "Jefe SSL"), ssl.get("fotoEvidencia", ""),
                    ssl.get("status", "Pendiente"), ssl.get("fechaCorreccion"), ssl.get("otVinculada"), ssl.get("observacionesCierre")
                ))

        # Actualizar Equipos en Taller Externo
        for ext in data.get("equiposTallerExterno", []):
            cursor.execute("""
                INSERT INTO equipos_taller_externo (
                    id, equipo_id, proveedor_id, proveedor_nombre, fecha_salida, fecha_estimada_retorno,
                    fecha_retorno_real, motivo_servicio, costo_estimado, costo_final, status,
                    condicion_recepcion, recibido_por, observaciones, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    status=excluded.status, fecha_retorno_real=excluded.fecha_retorno_real,
                    condicion_recepcion=excluded.condicion_recepcion, recibido_por=excluded.recibido_por,
                    costo_final=excluded.costo_final, observaciones=excluded.observaciones,
                    updated_at=CURRENT_TIMESTAMP;
            """, (
                ext["id"], ext.get("equipoId", ""), ext.get("proveedorId"), ext.get("proveedorNombre", "Taller Externo"),
                ext.get("fechaSalida", ""), ext.get("fechaEstimadaRetorno"), ext.get("fechaRetornoReal"),
                ext.get("motivoServicio", ""), float(ext.get("costoEstimado") or 0.0), float(ext.get("costoFinal") or 0.0),
                ext.get("status", "En diagnóstico"), ext.get("condicionRecepcion"), ext.get("recibidoPor"), ext.get("observaciones")
            ))

        # Actualizar Salidas de Materiales
        for sal in data.get("salidasMateriales", []):
            cursor.execute("""
                INSERT OR IGNORE INTO salidas_materiales (
                    id, fecha, ot_id, solicitud_id, repuesto_id, repuesto_nombre, cantidad,
                    despachado_por, receptor, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                sal["id"], sal.get("fecha", ""), sal.get("otId"), sal.get("solicitudId"),
                sal.get("repuestoId", ""), sal.get("repuestoNombre", ""), int(sal.get("cantidad") or 1),
                sal.get("despachadoPor", ""), sal.get("receptor", ""), sal.get("observaciones")
            ))

        conn.commit()

    notify_clients()
    return {"success": True, "message": "Base de datos sincronizada y reconciliada con éxito en el servidor Python"}

# --- 13. SERVIR FRONTEND ESTÁTICO DE ALTO RENDIMIENTO ---

@app.get("/")
def serve_root():
    static_index = STATIC_DIR / "index.html"
    base_index = BASE_DIR / "index.html"
    if static_index.exists():
        return FileResponse(str(static_index))
    elif base_index.exists():
        return FileResponse(str(base_index))
    return {"message": "GMAO Industrial Pro Backend activo. Coloque index.html en la carpeta static."}

# Montar carpeta estática
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=SERVER_PORT, reload=DEBUG)

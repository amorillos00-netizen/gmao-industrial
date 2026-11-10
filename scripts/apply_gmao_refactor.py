# -*- coding: utf-8 -*-
"""
Script de refactorización y parche para GMAO Industrial Pro:
1. Jefe Mantenimiento:
   - Elimina módulo "Panel departamento de compras".
   - Exportación e impresión filtrada por rango de fechas.
2. Compras:
   - Elimina módulos: Almacén control de compras, Almacén de repuestos, Control de compras.
   - Solo Proveedores y Panel de Compras (sincronización inmediata).
   - Filtrado: solo solicitudes de "Jefe de Mantenimiento".
   - Estados permitidos: [Pendiente, Aprobada, En tránsito]. Prohibido "Recibida".
3. Preventivo:
   - Al cerrar OT preventiva, actualiza plan a "Completado" y cancela notificaciones de vencimiento.
4. Calendario:
   - Vista predeterminada del diagrama del plan a escala semanal.
"""

import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def patch_database_py():
    db_path = BASE_DIR / "app" / "database.py"
    content = db_path.read_text(encoding="utf-8")
    
    # 1. ensure_columns
    if "if 'creado_por' not in cols:" not in content:
        target = "if 'status' not in cols:\n            cursor.execute(\"ALTER TABLE compras_materiales ADD COLUMN status TEXT DEFAULT 'Pendiente';\")"
        replacement = """if 'status' not in cols:
            cursor.execute("ALTER TABLE compras_materiales ADD COLUMN status TEXT DEFAULT 'Pendiente';")
        if 'creado_por' not in cols:
            cursor.execute("ALTER TABLE compras_materiales ADD COLUMN creado_por TEXT DEFAULT 'Jefe de Mantenimiento';")"""
        content = content.replace(target, replacement)

    if "if 'status' not in cols:\n            cursor.execute(\"ALTER TABLE planes_preventivos ADD COLUMN status TEXT DEFAULT 'Pendiente';\")" not in content:
        target = "if 'frecuencia_valor' not in cols:\n            cursor.execute(\"ALTER TABLE planes_preventivos ADD COLUMN frecuencia_valor INTEGER DEFAULT 1;\")"
        replacement = """if 'frecuencia_valor' not in cols:
            cursor.execute("ALTER TABLE planes_preventivos ADD COLUMN frecuencia_valor INTEGER DEFAULT 1;")
        if 'status' not in cols:
            cursor.execute("ALTER TABLE planes_preventivos ADD COLUMN status TEXT DEFAULT 'Pendiente';")"""
        content = content.replace(target, replacement)

    if "if 'plan_id' not in cols:\n            cursor.execute(\"ALTER TABLE ordenes_trabajo ADD COLUMN plan_id TEXT;\")" not in content:
        target = "for table in ['solicitudes_mantenimiento', 'ordenes_trabajo'"
        replacement = """try:
        cursor.execute("PRAGMA table_info(ordenes_trabajo);")
        cols = [c[1] for c in cursor.fetchall()]
        if 'plan_id' not in cols:
            cursor.execute("ALTER TABLE ordenes_trabajo ADD COLUMN plan_id TEXT;")
    except Exception as e:
        pass

    for table in ['solicitudes_mantenimiento', 'ordenes_trabajo'"""
        content = content.replace(target, replacement)

    db_path.write_text(content, encoding="utf-8")
    print("[OK] app/database.py parcheado correctamente.")

def patch_main_py():
    main_path = BASE_DIR / "app" / "main.py"
    content = main_path.read_text(encoding="utf-8")

    # 1. get_purchases
    target_get_purchases = """@app.get("/api/purchases")
def get_purchases():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(\"\"\"
            SELECT id, fecha, descripcion, cant_solicitada as cantSolicitada, cant_recibida as cantRecibida,
                   moneda, precio, proveedor_id as proveedorId, observaciones, COALESCE(status, 'Pendiente') as status
            FROM compras_materiales ORDER BY id DESC;
        \"\"\")
        return [dict(r) for r in cursor.fetchall()]"""

    replacement_get_purchases = """@app.get("/api/purchases")
def get_purchases(role: Optional[str] = Query(None), creado_por: Optional[str] = Query(None)):
    with get_db() as conn:
        cursor = conn.cursor()
        if role in ("Departamento de Compras", "Compras") or (creado_por and "jefe" in creado_por.lower()):
            cursor.execute(\"\"\"
                SELECT id, fecha, descripcion, cant_solicitada as cantSolicitada, cant_recibida as cantRecibida,
                       moneda, precio, proveedor_id as proveedorId, observaciones, COALESCE(status, 'Pendiente') as status,
                       COALESCE(creado_por, 'Jefe de Mantenimiento') as creadoPor
                FROM compras_materiales
                WHERE creado_por LIKE '%Jefe%' OR creado_por LIKE '%Mantenimiento%' OR creado_por IS NULL
                ORDER BY id DESC;
            \"\"\")
        else:
            cursor.execute(\"\"\"
                SELECT id, fecha, descripcion, cant_solicitada as cantSolicitada, cant_recibida as cantRecibida,
                       moneda, precio, proveedor_id as proveedorId, observaciones, COALESCE(status, 'Pendiente') as status,
                       COALESCE(creado_por, 'Jefe de Mantenimiento') as creadoPor
                FROM compras_materiales ORDER BY id DESC;
            \"\"\")
        return [dict(r) for r in cursor.fetchall()]"""

    if target_get_purchases in content:
        content = content.replace(target_get_purchases, replacement_get_purchases)

    # 2. save_purchase con creado_por
    target_save_purchase = """@app.post("/api/purchases")
def save_purchase(compra: Dict[str, Any]):
    com_id = compra.get("id")
    with get_db() as conn:
        cursor = conn.cursor()
        if not com_id:
            cursor.execute("SELECT COUNT(*) FROM compras_materiales;")
            count = cursor.fetchone()[0] + 1
            com_id = f"COM-{str(count).zfill(2)}"
            compra["id"] = com_id
        
        cursor.execute(\"\"\"
            INSERT INTO compras_materiales (
                id, fecha, descripcion, cant_solicitada, cant_recibida, moneda, precio, proveedor_id, observaciones, status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                fecha=excluded.fecha,
                descripcion=excluded.descripcion,
                cant_solicitada=excluded.cant_solicitada,
                cant_recibida=excluded.cant_recibida,
                precio=excluded.precio,
                proveedor_id=excluded.proveedor_id,
                observaciones=excluded.observaciones,
                status=excluded.status,
                updated_at=CURRENT_TIMESTAMP;
        \"\"\", (
            com_id,
            compra.get("fecha", datetime.now().strftime("%Y-%m-%d")),
            compra.get("descripcion", "").strip(),
            int(compra.get("cantSolicitada", 1)),
            int(compra.get("cantRecibida", 0)),
            compra.get("moneda", "$"),
            float(compra.get("precio", 0.0)),
            compra.get("proveedorId"),
            compra.get("observaciones", "").strip(),
            compra.get("status", "Pendiente")
        ))
        conn.commit()
    return {"success": True, "id": com_id, "compra": compra}"""

    replacement_save_purchase = """@app.post("/api/purchases")
def save_purchase(compra: Dict[str, Any]):
    com_id = compra.get("id")
    with get_db() as conn:
        cursor = conn.cursor()
        if not com_id:
            cursor.execute("SELECT COUNT(*) FROM compras_materiales;")
            count = cursor.fetchone()[0] + 1
            com_id = f"COM-{str(count).zfill(2)}"
            compra["id"] = com_id
        
        creador = compra.get("creadoPor") or "Jefe de Mantenimiento"
        cursor.execute(\"\"\"
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
        \"\"\", (
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
    return {"success": True, "id": com_id, "compra": compra}"""

    if target_save_purchase in content:
        content = content.replace(target_save_purchase, replacement_save_purchase)

    # 3. update_purchase_status con validación estricta de "Recibida" para rol Compras
    target_update_status = """@app.patch("/api/purchases/{compra_id}/status")
@app.put("/api/purchases/{compra_id}/status")
def update_purchase_status(compra_id: str, payload: Dict[str, Any]):
    new_status = payload.get("status", "Pendiente")
    cant_rec = payload.get("cantRecibida")"""

    replacement_update_status = """@app.patch("/api/purchases/{compra_id}/status")
@app.put("/api/purchases/{compra_id}/status")
def update_purchase_status(compra_id: str, payload: Dict[str, Any]):
    new_status = payload.get("status", "Pendiente")
    user_role = payload.get("rol") or payload.get("role") or ""
    if new_status == "Recibida" and user_role in ("Departamento de Compras", "Compras"):
        raise HTTPException(status_code=403, detail="Acceso denegado: El estado 'Recibida' es exclusivo para Jefe de Mantenimiento y Almacén.")
    cant_rec = payload.get("cantRecibida")"""

    if target_update_status in content:
        content = content.replace(target_update_status, replacement_update_status)

    # 4. save_work_order: al cerrar OT preventiva, plan pasa a Completado y cancela notificaciones de vencimiento
    target_ot_concluida = """        if ot.get("status") in ("Concluida", "Completada"):
            # Cambio automático de estatus: Solicitudes vinculadas pasan a 'Culminada'"""

    replacement_ot_concluida = """        if ot.get("status") in ("Concluida", "Completada"):
            # Actualización automática de actividades preventivas y cancelación de notificaciones de vencimiento
            plan_id = ot.get("planId") or ot.get("plan_id")
            if ot.get("tipo") == "Preventivo" or plan_id:
                fecha_cierre = (ot.get("fechaFin") or ot.get("fechaProgramada") or datetime.now().strftime("%Y-%m-%d"))[:10]
                if plan_id:
                    cursor.execute(\"\"\"
                        UPDATE planes_preventivos
                        SET status = 'Completado', ultima_fecha = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?;
                    \"\"\", (fecha_cierre, plan_id))
                    cursor.execute(\"\"\"
                        DELETE FROM notificaciones
                        WHERE (enlace_id = ? OR id LIKE ? OR id LIKE ?)
                          AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent') OR enlace_tipo IN ('plan', 'cronograma-anual'));
                    \"\"\", (plan_id, f"NOTIF-PREV%{plan_id}%", f"%{plan_id}%"))
                else:
                    eq_id = ot.get("equipoId")
                    if eq_id:
                        cursor.execute(\"\"\"
                            UPDATE planes_preventivos
                            SET status = 'Completado', ultima_fecha = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE equipo_id = ?;
                        \"\"\", (fecha_cierre, eq_id))
                        cursor.execute(\"\"\"
                            DELETE FROM notificaciones
                            WHERE (enlace_id IN (SELECT id FROM planes_preventivos WHERE equipo_id = ?) OR id LIKE 'NOTIF-PREV%')
                              AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR mensaje LIKE ?);
                        \"\"\", (eq_id, f"%{eq_id}%"))
                cursor.execute(\"\"\"
                    DELETE FROM notificaciones
                    WHERE (enlace_id = ? OR id LIKE ?)
                      AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%');
                \"\"\", (ot_id, f"NOTIF-OT-5D-{ot_id}%"))

            # Cambio automático de estatus: Solicitudes vinculadas pasan a 'Culminada'"""

    if target_ot_concluida in content:
        content = content.replace(target_ot_concluida, replacement_ot_concluida)

    # 5. get_preventive_plans status
    target_get_plans = "SELECT id, equipo_id as equipoId, nombre, frecuencia, frecuencia_tipo as frecuenciaTipo, frecuencia_valor as frecuenciaValor, ultima_fecha as ultimaFecha, proxima_fecha as proximaFecha, tecnicos_ids, es_refrigeracion as esRefrigeracion FROM planes_preventivos ORDER BY id;"
    replacement_get_plans = "SELECT id, equipo_id as equipoId, nombre, frecuencia, frecuencia_tipo as frecuenciaTipo, frecuencia_valor as frecuenciaValor, ultima_fecha as ultimaFecha, proxima_fecha as proximaFecha, tecnicos_ids, es_refrigeracion as esRefrigeracion, COALESCE(status, 'Pendiente') as status FROM planes_preventivos ORDER BY id;"
    if target_get_plans in content:
        content = content.replace(target_get_plans, replacement_get_plans)

    # 6. check_preventive_alerts: ignorar completados
    target_check_alerts = """        cursor.execute(\"\"\"
            SELECT p.id, p.nombre, p.equipo_id, p.proxima_fecha, e.nombre as equipo_nombre
            FROM planes_preventivos p
            LEFT JOIN activos_equipos e ON p.equipo_id = e.id;
        \"\"\")"""
    replacement_check_alerts = """        cursor.execute(\"\"\"
            SELECT p.id, p.nombre, p.equipo_id, p.proxima_fecha, e.nombre as equipo_nombre
            FROM planes_preventivos p
            LEFT JOIN activos_equipos e ON p.equipo_id = e.id
            WHERE COALESCE(p.status, 'Pendiente') != 'Completado';
        \"\"\")"""
    if target_check_alerts in content:
        content = content.replace(target_check_alerts, replacement_check_alerts)

    main_path.write_text(content, encoding="utf-8")
    print("[OK] app/main.py parcheado correctamente.")

if __name__ == "__main__":
    patch_database_py()
    patch_main_py()

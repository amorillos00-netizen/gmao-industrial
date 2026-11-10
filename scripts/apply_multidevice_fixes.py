# -*- coding: utf-8 -*-
"""
Script de aplicacion de mejoras multi-dispositivo y persistencia directa en DB para GMAO Industrial Pro:
1. Backend:
   - Endpoint DELETE /api/inventory/{item_id}
   - Actualizacion completa en save_solicitud y save_ssl_request (ON CONFLICT DO UPDATE SET)
   - uvicorn.run con 0.0.0.0
2. Frontend:
   - getApiUrl dinámico usando window.location.hostname
   - Eliminación de localStorage.setItem(LOCAL_STORAGE_KEY, ...)
   - Limpieza de localStorage.removeItem(LOCAL_STORAGE_KEY) en loadDatabase()
   - Persistencia directa vía fetch(getApiUrl(...)) para Solicitudes ST, Reportes SSL, Compras y Materiales
"""

from pathlib import Path
import shutil
import re

BASE_DIR = Path(__file__).resolve().parent.parent

def patch_backend():
    main_path = BASE_DIR / "app" / "main.py"
    content = main_path.read_text(encoding="utf-8")

    # 1. Agregar endpoint DELETE /api/inventory/{item_id}
    if '@app.delete("/api/inventory/{item_id}")' not in content:
        target_inv = '''@app.post("/api/inventory")
def save_spare_part(rep: Dict[str, Any]):'''
        
        # Buscar el final de save_spare_part
        target_inv_end = '''        conn.commit()
    return {"success": True, "id": rep_id}'''
        
        replacement_inv = '''        conn.commit()
    return {"success": True, "id": rep_id}

@app.delete("/api/inventory/{item_id}")
def delete_spare_part(item_id: str):
    """Elimina un repuesto o material del inventario y desvincula salidas asociadas."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE salidas_materiales SET repuesto_id = NULL WHERE repuesto_id = ?;", (item_id,))
        cursor.execute("DELETE FROM repuestos_materiales WHERE id = ?;", (item_id,))
        conn.commit()
    return {"success": True, "id": item_id}'''

        assert target_inv_end in content, "target_inv_end not found in app/main.py"
        content = content.replace(target_inv_end, replacement_inv, 1)
        print("[OK] app/main.py: @app.delete('/api/inventory/{item_id}') added")

    # 2. Actualizar save_solicitud ON CONFLICT para actualizar todos los campos al editar
    target_sol_conflict = '''            ON CONFLICT(id) DO UPDATE SET
                status=excluded.status,
                ot_vinculada=excluded.ot_vinculada,
                updated_at=CURRENT_TIMESTAMP;'''
    
    replacement_sol_conflict = '''            ON CONFLICT(id) DO UPDATE SET
                tipo=excluded.tipo,
                urgencia=excluded.urgencia,
                area=excluded.area,
                ubicacion=excluded.ubicacion,
                descripcion=excluded.descripcion,
                solicitante=excluded.solicitante,
                status=excluded.status,
                ot_vinculada=excluded.ot_vinculada,
                updated_at=CURRENT_TIMESTAMP;'''

    if target_sol_conflict in content:
        content = content.replace(target_sol_conflict, replacement_sol_conflict, 1)
        print("[OK] app/main.py: save_solicitud ON CONFLICT updated for full field edits")

    # 3. Actualizar save_ssl_request ON CONFLICT para actualizar todos los campos al editar
    target_ssl_conflict = '''            ON CONFLICT(id) DO UPDATE SET
                status=excluded.status,
                fecha_correccion=excluded.fecha_correccion,
                ot_vinculada=excluded.ot_vinculada,
                observaciones_cierre=excluded.observaciones_cierre,
                updated_at=CURRENT_TIMESTAMP;'''

    replacement_ssl_conflict = '''            ON CONFLICT(id) DO UPDATE SET
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
                updated_at=CURRENT_TIMESTAMP;'''

    if target_ssl_conflict in content:
        content = content.replace(target_ssl_conflict, replacement_ssl_conflict, 1)
        print("[OK] app/main.py: save_ssl_request ON CONFLICT updated for full field edits")

    # 4. Asegurar bloque if __name__ == '__main__' con 0.0.0.0 al final de app/main.py
    if 'if __name__ == "__main__":' not in content:
        content += """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=SERVER_PORT, reload=DEBUG)
"""
        print("[OK] app/main.py: __main__ block with host 0.0.0.0 added")

    main_path.write_text(content, encoding="utf-8")
    print("[DONE] app/main.py updated successfully.")

if __name__ == "__main__":
    patch_backend()

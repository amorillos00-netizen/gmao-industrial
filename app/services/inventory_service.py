"""
Servicio de Gestión de Inventario y Conciliación Automática de Stock (Kardex)
"""
import sqlite3
from typing import List, Dict, Any

def deduct_spare_parts_from_db(cursor: sqlite3.Cursor, repuestos_usados: List[Dict[str, Any]]):
    """
    Descuenta de forma transaccional los repuestos utilizados en una Orden de Trabajo.
    Si el repuesto no tiene ID pero coincide por nombre o código, también lo concilia.
    """
    for item in repuestos_usados:
        rep_id = item.get("repuestoId") or item.get("repuesto_id")
        nombre = item.get("name") or item.get("nombre")
        cant = int(item.get("cant") or item.get("cantidad") or 0)
        
        if cant <= 0:
            continue

        if rep_id:
            cursor.execute("""
                UPDATE repuestos_materiales 
                SET stock = MAX(0, stock - ?) 
                WHERE id = ?;
            """, (cant, rep_id))
        elif nombre:
            cursor.execute("""
                UPDATE repuestos_materiales 
                SET stock = MAX(0, stock - ?) 
                WHERE LOWER(nombre) = LOWER(?) OR LOWER(codigo) = LOWER(?);
            """, (cant, nombre, nombre))

def check_low_stock_alerts(cursor: sqlite3.Cursor) -> List[Dict[str, Any]]:
    """Obtiene todos los artículos que se encuentran en o por debajo de su stock de seguridad."""
    cursor.execute("""
        SELECT r.id, r.codigo, r.nombre, r.stock, r.stock_minimo, r.unidad_medida, r.costo_unitario, p.nombre as proveedor_nombre
        FROM repuestos_materiales r
        LEFT JOIN proveedores p ON r.proveedor_id = p.id
        WHERE r.stock <= r.stock_minimo;
    """)
    alerts = []
    for row in cursor.fetchall():
        alerts.append({
            "id": row["id"],
            "codigo": row["codigo"],
            "nombre": row["nombre"],
            "stock_actual": row["stock"],
            "stock_minimo": row["stock_minimo"],
            "unidad_medida": row["unidad_medida"],
            "costo_unitario": row["costo_unitario"],
            "proveedor": row["proveedor_nombre"] or "No asignado",
            "deficit": max(0, row["stock_minimo"] - row["stock"])
        })
    return alerts

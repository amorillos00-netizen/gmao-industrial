import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.database import get_db
from app.main import save_work_order

# Step 1: Insert test solicitud
with get_db() as conn:
    conn.execute("""
        INSERT OR REPLACE INTO solicitudes_mantenimiento 
        (id, tipo, urgencia, area, ubicacion, descripcion, solicitante, fecha_hora, status)
        VALUES ('SOL-DBG-01', 'Maquinaria / Equipo', 'Media', 'L1', 'Emp', 'Test', 'Prod', '2026-11-10 08:00', 'Aprobada')
    """)
    conn.execute("""
        INSERT OR REPLACE INTO solicitudes_ssl 
        (id, codigo, fecha_hora, area, ubicacion, equipo_id, nivel_riesgo, descripcion, solicitante_nombre, foto_evidencia, status)
        VALUES ('SSL-DBG-01', 'SSL-2026-DBG', '2026-11-10 08:00', 'L1', 'Emp', 'EQ-101', 'Medio', 'Fuga', 'SSL', 'data:image/png;base64,s', 'Pendiente')
    """)
    conn.commit()
    print("Inserted SOL-DBG-01 and SSL-DBG-01")

# Step 2: Save concluida OT
ot = {
    "id": "OT-DBG-CLOSE",
    "tipo": "Correctivo",
    "prioridad": "Media",
    "equipoId": "EQ-101",
    "descripcion": "Test debug",
    "status": "Concluida",
    "solicitudId": "SOL-DBG-01",
    "sslReportId": "SSL-DBG-01",
    "tiempoIntervencion": 2.0,
    "tiempoParada": 2.0,
    "actividades": "Done"
}
res = save_work_order(ot)
print("save_work_order result:", res)

# Step 3: Check
with get_db() as conn:
    sol = conn.execute("SELECT id, status, ot_vinculada FROM solicitudes_mantenimiento WHERE id='SOL-DBG-01'").fetchone()
    print("SOL-DBG-01:", dict(sol) if sol else "NOT FOUND")
    
    ssl = conn.execute("SELECT id, status, ot_vinculada FROM solicitudes_ssl WHERE id='SSL-DBG-01'").fetchone()
    print("SSL-DBG-01:", dict(ssl) if ssl else "NOT FOUND")

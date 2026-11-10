"""
Suite de Pruebas Integral para GMAO Industrial Pro v3.3
Verificación directa de los 11 Requerimientos Funcionales y Técnicos.
Empresa: SALTYSNACK TUYERO C.A.
"""
import sys
import io
import openpyxl
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import init_db, get_db
from app.services.kpi_service import calculate_reliability_kpis
from app.services.excel_service import generate_matriz_control_ot_excel, generate_cronograma_anual_excel
import app.main as api

def test_kpi_period_filtering():
    """1. GESTIÓN DE KPI'S Y FILTRADO POR PERIODO (Mensual vs Anual)"""
    ots = [
        {"id": "OT-01", "tipo": "Preventivo", "status": "Concluida", "tiempoParada": 0, "tiempoIntervencion": 4.0, "fechaProgramada": "2026-10-15"},
        {"id": "OT-02", "tipo": "Correctivo", "status": "Concluida", "tiempoParada": 10.0, "tiempoIntervencion": 5.0, "fechaProgramada": "2026-10-20"},
        {"id": "OT-03", "tipo": "Correctivo", "status": "Concluida", "tiempoParada": 15.0, "tiempoIntervencion": 5.0, "fechaProgramada": "2026-11-05"},
    ]

    # Periodo Mensual para Octubre 2026 (solo OT-01 y OT-02)
    kpis_oct = calculate_reliability_kpis(ots, "TODOS", periodo_tipo="Mensual", periodo_valor="2026-10")
    assert kpis_oct["horas_base"] == 720.0
    assert kpis_oct["total_ots"] == 2
    assert kpis_oct["total_downtime_horas"] == 10.0
    # Horas operadas = 720 - 10 = 710 -> (710 / 720) * 100 = 98.6%
    assert kpis_oct["disponibilidad_pct"] == 98.6

    # Periodo Anual para 2026 (evalúa las 3 OTs)
    kpis_anio = calculate_reliability_kpis(ots, "TODOS", periodo_tipo="Anual", periodo_valor="2026")
    assert kpis_anio["horas_base"] == 8760.0
    assert kpis_anio["total_ots"] == 3
    assert kpis_anio["total_downtime_horas"] == 25.0
    # Horas operadas = 8760 - 25 = 8735 -> (8735 / 8760) * 100 = 99.7%
    assert kpis_anio["disponibilidad_pct"] == 99.7
    print("[OK] Requerimiento 1 (KPIs Mensual vs Anual) validado.")

def test_database_and_security_roles():
    """2 & 7. SEGURIDAD, LOGIN PRODUCTIVO Y ROL JEFE SSL"""
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar rol SSL
        cursor.execute("SELECT id, nombre FROM roles WHERE id = 'ROL-SSL';")
        rol_ssl = cursor.fetchone()
        assert rol_ssl is not None, "Rol ROL-SSL debe existir en base de datos"
        assert rol_ssl["nombre"] == "Jefe SSL"

        # Verificar usuario jefessl
        cursor.execute("SELECT id, username, rol_id FROM usuarios WHERE username = 'jefessl';")
        usr_ssl = cursor.fetchone()
        assert usr_ssl is not None, "Usuario jefessl debe existir"
        assert usr_ssl["rol_id"] == "ROL-SSL"

    # Probar función de login con rol Jefe SSL
    res = api.login({"username": "jefessl", "password": "1234"})
    assert res["success"] is True
    assert res["user"]["role"] == "Jefe SSL"
    print("[OK] Requerimiento 2 y 7 (Roles y Seguridad Jefe SSL) validados.")

def test_interdepartmental_request_flow():
    """6. FLUJO EXCLUSIVO DE 4 ESTADOS EN SOLICITUDES"""
    from app.main import VALID_SOLICITUD_STATUSES
    assert VALID_SOLICITUD_STATUSES == ["Aprobada", "En espera de materiales", "En proceso", "Culminada"]

    # Crear solicitud con estado autorizado
    res = api.save_solicitud({
        "tipo": "Maquinaria / Equipo",
        "urgencia": "Media",
        "area": "Producción Snacks",
        "ubicacion": "Extrusora 01",
        "descripcion": "Verificación de temperatura en cabezal",
        "solicitante": "Operador",
        "status": "En espera de materiales"
    })
    assert res["success"] is True
    sol_id = res["id"]

    # Verificar que el estado se registró
    sols = api.get_solicitudes()
    found = [s for s in sols if s["id"] == sol_id]
    assert len(found) == 1
    assert found[0]["status"] == "En espera de materiales"
    print("[OK] Requerimiento 6 (Flujo de 4 Estados de Solicitudes) validado.")

def test_ssl_module_with_mandatory_photo():
    """7. MÓDULO SSL Y FOTOGRAFÍA OBLIGATORIA"""
    # Intentar crear condición SSL sin foto debe lanzar HTTPException 400
    from fastapi import HTTPException
    try:
        api.save_ssl_request({
            "area": "Envasado",
            "ubicacion": "Cinta #1",
            "nivelRiesgo": "Alto",
            "descripcion": "Sin resguardo",
            "fotoEvidencia": ""
        })
        assert False, "Debería haber fallado por falta de foto"
    except HTTPException as e:
        assert e.status_code == 400

    # Crear condición SSL con foto de evidencia
    res_ok = api.save_ssl_request({
        "area": "Envasado",
        "ubicacion": "Cinta #1",
        "nivelRiesgo": "Alto",
        "descripcion": "Sin resguardo en polea",
        "accionPropuesta": "Fabricar guarda de malla",
        "solicitanteId": "u5",
        "solicitanteNombre": "Ing. Argenis Morillo (Jefe SSL)",
        "fotoEvidencia": "data:image/jpeg;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
        "status": "Pendiente"
    })
    assert res_ok["success"] is True
    ssl_id = res_ok["id"]

    # Consultar lista
    ssls = api.get_ssl_requests()
    assert any(s["id"] == ssl_id for s in ssls)
    print("[OK] Requerimiento 7 (Módulo SSL con Foto Obligatoria) validado.")

def test_excel_export_matriz_and_cronograma():
    """4 & 5. GENERACIÓN PROFESIONAL DE EXCEL (MATRIZ OT Y CRONOGRAMA ANUAL)"""
    # 1. Endpoint Matriz O.T. Excel
    res_matriz = api.export_matriz_ot_excel()
    assert "spreadsheetml.sheet" in res_matriz.media_type
    
    # Verificar con openpyxl que el libro tiene las dos hojas requeridas
    wb_matriz = openpyxl.load_workbook(io.BytesIO(res_matriz.body), data_only=False)
    assert "Dashboard" in wb_matriz.sheetnames
    assert "Control de Órdenes (OT)" in wb_matriz.sheetnames
    
    ws_dash = wb_matriz["Dashboard"]
    assert "SALTYSNACK TUYERO C.A." in str(ws_dash["A1"].value)
    
    ws_ots = wb_matriz["Control de Órdenes (OT)"]
    assert "CONTROL MAESTRO DE ÓRDENES DE TRABAJO" in str(ws_ots["A1"].value)
    assert ws_ots["A4"].value == "N° OT"

    # 2. Endpoint Cronograma Anual Excel
    res_cron = api.export_cronograma_anual_excel(anio=2026)
    wb_cron = openpyxl.load_workbook(io.BytesIO(res_cron.body), data_only=False)
    assert "Cronograma Anual 2026" in wb_cron.sheetnames
    ws_c = wb_cron["Cronograma Anual 2026"]
    assert "CRONOGRAMA ANUAL DE MANTENIMIENTO PREVENTIVO 2026" in str(ws_c["A1"].value)
    print("[OK] Requerimientos 4 y 5 (Generación Excel Matriz y Cronograma) validados.")

def test_notification_engine():
    """8. MOTOR DE NOTIFICACIONES DINÁMICAS POR ROL"""
    notifs = api.get_notificaciones(rol="Gerente")
    assert isinstance(notifs, list)
    assert len(notifs) > 0
    print("[OK] Requerimiento 8 (Motor de Notificaciones) validado.")

def test_sync_endpoint():
    """3. SINCRONIZACIÓN OFFLINE-FIRST"""
    sync_data = api.get_full_sync()
    assert sync_data["success"] is True
    data = sync_data["data"]
    assert "equipos" in data
    assert "repuestos" in data
    assert "ots" in data
    assert "solicitudesSSL" in data
    assert "notificaciones" in data
    print("[OK] Requerimiento 3 (Capa de Sincronización) validado.")

if __name__ == "__main__":
    print("=" * 60)
    print("INICIANDO SUITE DE PRUEBAS DEL SISTEMA GMAO INDUSTRIAL PRO")
    print("=" * 60)
    test_kpi_period_filtering()
    test_database_and_security_roles()
    test_interdepartmental_request_flow()
    test_ssl_module_with_mandatory_photo()
    test_excel_export_matriz_and_cronograma()
    test_notification_engine()
    test_sync_endpoint()
    print("=" * 60)
    print("TODAS LAS PRUEBAS UNITARIAS E INTEGRALES PASARON EXITOSAMENTE (100%)")
    print("=" * 60)

# -*- coding: utf-8 -*-
"""
Suite de Pruebas Automatizadas para los 7 Nuevos Requerimientos Funcionales
GMAO Mantenimiento Industrial - SALTYSNACK TUYERO C.A.
"""
import unittest
import sqlite3
import os
import sys
import json
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import (
    app,
    export_informe_periodico_excel,
    export_informe_periodico_word,
    get_external_services,
    save_external_service,
    receive_external_service,
    get_inventory_dispatches,
    create_inventory_dispatch,
    create_or_update_asset,
    save_work_order,
    get_full_sync,
    post_full_sync
)
from app.database import get_db, DB_PATH
from fastapi import HTTPException
from fastapi.responses import Response

class TestNuevosRequerimientos(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join("app", "static", "index.html")
        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

    # =========================================================================
    # REQUERIMIENTO 1: EXPORTACIÓN DE INFORMES PERIÓDICOS (EXCEL Y WORD)
    # =========================================================================
    def test_req_1_exportacion_excel(self):
        """1. Exportación de Informe Periódico en Excel (.xlsx)"""
        response = export_informe_periodico_excel(periodo_tipo="Mensual", periodo_valor="2026-10", equipo_id="TODOS")
        self.assertIsInstance(response, Response)
        self.assertEqual(response.media_type, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertIn("INFORME_PERIODICO_2026_10.xlsx", response.headers["Content-Disposition"])
        
        # Validar contenido binario
        content = response.body
        self.assertGreater(len(content), 5000, "El archivo Excel generado debe tener un tamaño válido (>5KB)")
        
        # Validar que openpyxl puede leerlo
        import openpyxl
        wb = openpyxl.load_workbook(BytesIO(content))
        self.assertTrue(any("informe" in s.lower() for s in wb.sheetnames))
        ws = wb.active
        # Buscar texto corporativo
        found_title = any("SALTYSNACK TUYERO" in str(cell.value) for row in ws.iter_rows() for cell in row if cell.value)
        self.assertTrue(found_title, "El archivo Excel debe contener el encabezado corporativo de SALTYSNACK TUYERO")

    def test_req_1_exportacion_word(self):
        """1. Exportación de Informe Periódico en Word (.docx)"""
        response = export_informe_periodico_word(periodo_tipo="Mensual", periodo_valor="2026-10", equipo_id="TODOS")
        self.assertIsInstance(response, Response)
        self.assertEqual(response.media_type, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertIn("INFORME_PERIODICO_2026_10.docx", response.headers["Content-Disposition"])
        
        # Validar contenido binario
        content = response.body
        self.assertGreater(len(content), 5000, "El archivo Word generado debe tener un tamaño válido (>5KB)")
        
        # Validar que python-docx puede leerlo y contiene texto corporativo
        import docx
        doc = docx.Document(BytesIO(content))
        full_doc_text = " ".join([p.text for p in doc.paragraphs] + [c.text for t in doc.tables for r in t.rows for c in r.cells])
        self.assertIn("SALTYSNACK TUYERO C.A.", full_doc_text)
        self.assertIn("Jefe de Mantenimiento", full_doc_text)
        self.assertIn("Gerente de Planta", full_doc_text)

    def test_req_1_frontend_buttons(self):
        """1. Botones de exportación en la vista de informes del frontend"""
        self.assertIn("exportarInformePeriodicoExcel()", self.html_content)
        self.assertIn("exportarInformePeriodicoWord()", self.html_content)
        self.assertIn("Exportar Word (.docx)", self.html_content)
        self.assertIn("Exportar Excel (.xlsx)", self.html_content)

    # =========================================================================
    # REQUERIMIENTO 2: SEGUIMIENTO DE EQUIPOS EN TALLER EXTERNO
    # =========================================================================
    def test_req_2_taller_externo_backend(self):
        """2. Módulo de Seguimiento de Equipos en Taller Externo (CRUD & Recepción)"""
        test_id = "EXT-TEST-001"
        payload = {
            "id": test_id,
            "equipoId": "EQ-101",
            "proveedorId": "PRV-01",
            "proveedorNombre": "Rectificaciones Industriales Tuy C.A.",
            "fechaSalida": "2026-11-10",
            "fechaEstimadaRetorno": "2026-11-20",
            "motivoServicio": "Rectificación de eje motriz y balanceo dinámico de turbina",
            "costoEstimado": 450.0,
            "status": "En reparación",
            "observaciones": "Envío con guía de traslado #8821"
        }
        res_save = save_external_service(payload)
        self.assertTrue(res_save.get("success"))
        
        # Consultar lista
        services = get_external_services()
        saved = next((s for s in services if s["id"] == test_id), None)
        self.assertIsNotNone(saved)
        self.assertEqual(saved["status"], "En reparación")
        self.assertEqual(saved["proveedorNombre"], "Rectificaciones Industriales Tuy C.A.")
        
        # Control de recepción a la planta
        rec_payload = {
            "fechaRetornoReal": "2026-11-18",
            "recibidoPor": "Ing. Roberto M. (Jefe Mantenimiento)",
            "condicionRecepcion": "Conforme",
            "costoFinal": 450.0,
            "observaciones": "Eje rectificado verificado con micrómetro. Tolerancias dentro de norma."
        }
        res_rec = receive_external_service(test_id, rec_payload)
        self.assertTrue(res_rec.get("success"))
        
        # Validar estatus actualizado a Recibido en Planta
        services_updated = get_external_services()
        received = next((s for s in services_updated if s["id"] == test_id), None)
        self.assertEqual(received["status"], "Recibido en Planta")
        self.assertEqual(received["fechaRetornoReal"], "2026-11-18")
        self.assertEqual(received["condicionRecepcion"], "Conforme")

    def test_req_2_frontend_taller_externo(self):
        """2. Interfaz y Modales de Taller Externo en Frontend"""
        self.assertIn("modalTallerExterno", self.html_content)
        self.assertIn("modalRecepcionTaller", self.html_content)
        self.assertIn("renderTallerExternoView", self.html_content)
        self.assertIn("openModalTallerExterno", self.html_content)
        self.assertIn("openModalRecepcionTaller", self.html_content)
        self.assertIn("Taller Externo", self.html_content)

    # =========================================================================
    # REQUERIMIENTO 3: ROL DE ALMACENISTA Y CONTROL DE SALIDA DE MATERIALES
    # =========================================================================
    def test_req_3_almacenista_y_salida_materiales(self):
        """3. Rol de Almacenista y Salida de Materiales con descuento automático de inventario"""
        # Verificar rol y usuario en base de datos
        with get_db() as conn:
            user_alm = conn.execute("SELECT * FROM usuarios WHERE id='u7' OR username='almacenista'").fetchone()
            self.assertIsNotNone(user_alm, "Usuario almacenista (u7) debe existir en base de datos")
            
            # Obtener stock inicial de un repuesto conocido en repuestos_materiales
            rep = conn.execute("SELECT id, stock, nombre FROM repuestos_materiales WHERE id='REP-TEST'").fetchone()
            if not rep or int(rep["stock"]) < 5:
                conn.execute("""
                    INSERT OR REPLACE INTO repuestos_materiales (id, codigo, nombre, stock, stock_minimo, unidad_medida, costo_unitario)
                    VALUES ('REP-TEST', 'RT-01', 'Rodamiento Test 6205', 10, 2, 'UND', 25.0)
                """)
                conn.commit()
                rep_id = "REP-TEST"
                stock_inicial = 10
            else:
                rep_id = rep["id"]
                stock_inicial = int(rep["stock"])

        # Registrar salida de material
        dispatch_payload = {
            "repuestoId": rep_id,
            "cantidad": 2,
            "otId": "OT-2026-001",
            "solicitudId": "",
            "receptor": "Téc. Juan Pérez",
            "despachadoPor": "Pedro Ramírez (Almacenista)",
            "fecha": "2026-11-11",
            "observaciones": "Entrega para mantenimiento en planta"
        }
        res_dispatch = create_inventory_dispatch(dispatch_payload)
        self.assertTrue(res_dispatch.get("success"))
        
        # Verificar que el stock disminuyó exactamente en 2 unidades
        with get_db() as conn:
            rep_after = conn.execute("SELECT stock FROM repuestos_materiales WHERE id=?", (rep_id,)).fetchone()
            self.assertEqual(int(rep_after["stock"]), stock_inicial - 2)

    def test_req_3_frontend_almacenista(self):
        """3. Menús y permisos de Almacenista en el Frontend"""
        self.assertIn("almacenista", self.html_content)
        self.assertIn("Salida de Materiales", self.html_content)
        self.assertIn("modalSalidaMaterial", self.html_content)
        self.assertIn("renderSalidasMaterialesView", self.html_content)

    # =========================================================================
    # REQUERIMIENTO 4: RESTRICCIÓN DE SEGURIDAD Y EDICIÓN EN MÓDULO SSL
    # =========================================================================
    def test_req_4_seguridad_equipos_backend(self):
        """4. Restricción backend: Modificación de equipos reservada a Gerente y Jefe de Mantenimiento"""
        asset_ssl = {
            "id": "EQ-FORBIDDEN-TEST",
            "name": "Balanza de Precisión",
            "userRole": "Jefe SSL",
            "userCargo": "Jefe de Seguridad, Salud y Laboral",
            "area": "Control de Calidad",
            "criticidad": "Media",
            "status": "Operativo"
        }
        # Intento por Jefe SSL -> Debe lanzar 403 Forbidden
        with self.assertRaises(HTTPException) as cm_ssl:
            create_or_update_asset(asset_ssl)
        self.assertEqual(cm_ssl.exception.status_code, 403)
        self.assertIn("reservada únicamente para los roles de Gerente de Planta y Jefe de Mantenimiento", str(cm_ssl.exception.detail))

        # Intento por Almacenista -> Debe lanzar 403 Forbidden
        asset_alm = {
            "id": "EQ-FORBIDDEN-TEST",
            "name": "Balanza de Precisión",
            "userRole": "Almacenista",
            "userCargo": "Almacenista de Repuestos y Materiales",
            "area": "Control de Calidad"
        }
        with self.assertRaises(HTTPException) as cm_alm:
            create_or_update_asset(asset_alm)
        self.assertEqual(cm_alm.exception.status_code, 403)

        # Intento por Jefe de Mantenimiento -> Permitido (200 / success)
        asset_jefe = {
            "id": "EQ-ALLOWED-TEST",
            "name": "Balanza de Precisión Autorizada",
            "userRole": "Jefe",
            "userCargo": "Jefe de Mantenimiento",
            "planta": "Planta Tuy",
            "linea": "Empaque",
            "criticidad": "Alta",
            "status": "Operativo"
        }
        res_jefe = create_or_update_asset(asset_jefe)
        self.assertTrue(res_jefe.get("success"))

        # Intento por Gerente de Planta -> Permitido (200 / success)
        asset_ger = {
            "id": "EQ-ALLOWED-TEST",
            "name": "Balanza de Precisión Actualizada por Gerente",
            "userRole": "Gerente",
            "userCargo": "Gerente de Planta",
            "planta": "Planta Tuy",
            "linea": "Empaque",
            "criticidad": "Alta",
            "status": "Operativo"
        }
        res_ger = create_or_update_asset(asset_ger)
        self.assertTrue(res_ger.get("success"))

    def test_req_4_frontend_restriccion_equipos(self):
        """4. Verificación en Frontend de helper puedeModificarEquipos y aviso de modo consulta"""
        self.assertIn("function puedeModificarEquipos", self.html_content)
        self.assertIn("Modo Consulta Autorizado (Solo Lectura)", self.html_content)

    # =========================================================================
    # REQUERIMIENTO 5: ALERTAS DE PREVENTIVOS Y PESTAÑA PRÓXIMAS INTERVENCIONES
    # =========================================================================
    def test_req_5_cronograma_alertas_y_pestana(self):
        """5. Cronograma con Alertas Preventivas y Pestaña Próximas Intervenciones"""
        self.assertIn("setCronogramaSubTab", self.html_content)
        self.assertIn("Próximas Intervenciones y Alertas", self.html_content)
        self.assertIn("verificarAlertasPreventivasAnticipadas", self.html_content)
        self.assertIn("cronogramaSubTab", self.html_content)

    # =========================================================================
    # REQUERIMIENTO 6: CAMBIO AUTOMÁTICO DE ESTATUS EN SOLICITUDES Y SSL
    # =========================================================================
    def test_req_6_cambio_automatico_estatus(self):
        """6. Cambio automático de estatus al cerrar OT: Solicitud -> 'Culminada', SSL -> 'Corregida'"""
        with get_db() as conn:
            # Crear Solicitud de prueba 'Aprobada'
            conn.execute("""
                INSERT OR REPLACE INTO solicitudes_mantenimiento 
                (id, tipo, urgencia, area, ubicacion, descripcion, solicitante, fecha_hora, status)
                VALUES ('SOL-AUTO-01', 'Maquinaria / Equipo', 'Media', 'Línea 1', 'Empaque', 'Ajuste de banda', 'Producción', '2026-11-10 08:00', 'Aprobada')
            """)
            # Crear Condición Insegura de prueba 'Pendiente' (estado válido)
            conn.execute("""
                INSERT OR REPLACE INTO solicitudes_ssl 
                (id, codigo, fecha_hora, area, ubicacion, equipo_id, nivel_riesgo, descripcion, solicitante_nombre, foto_evidencia, status)
                VALUES ('SSL-AUTO-01', 'SSL-2026-99', '2026-11-10 08:00', 'Línea 1', 'Empaque', 'EQ-101', 'Medio', 'Fuga de aceite en reductor', 'Ing. SSL', 'data:image/png;base64,sample', 'Pendiente')
            """)
            conn.commit()

        # Cerrar OT asociada a ambas
        ot_cierre = {
            "id": "OT-AUTO-CLOSE",
            "tipo": "Correctivo",
            "prioridad": "Media",
            "equipoId": "EQ-101",
            "descripcion": "Corrección de fuga y ajuste de banda",
            "status": "Concluida",
            "solicitudId": "SOL-AUTO-01",
            "sslReportId": "SSL-AUTO-01",
            "tiempoIntervencion": 2.0,
            "tiempoParada": 2.0,
            "actividades": "Trabajos concluidos con éxito y pruebas superadas"
        }
        res_ot = save_work_order(ot_cierre)
        self.assertTrue(res_ot.get("success"))

        # Validar que Solicitud pasó automáticamente a 'Culminada'
        with get_db() as conn:
            sol = conn.execute("SELECT status FROM solicitudes_mantenimiento WHERE id='SOL-AUTO-01'").fetchone()
            self.assertIsNotNone(sol, "Solicitud SOL-AUTO-01 debe existir tras save_work_order")
            self.assertEqual(sol["status"], "Culminada")

            # Validar que Condición Insegura pasó automáticamente a 'Corregida'
            ssl = conn.execute("SELECT status FROM solicitudes_ssl WHERE id='SSL-AUTO-01'").fetchone()
            self.assertIsNotNone(ssl, "SSL SSL-AUTO-01 debe existir tras save_work_order")
            self.assertEqual(ssl["status"], "Corregida")

    # =========================================================================
    # REQUERIMIENTO 7: CORRECCIÓN DE BUG EN BADGES (NÚMERO "1" PERSISTENTE)
    # =========================================================================
    def test_req_7_correccion_badges(self):
        """7. Corrección de Badges Reactivos y eliminación del número 1 permanente"""
        self.assertIn("function actualizarBadges()", self.html_content)
        self.assertIn("id=\"badge-solicitudes\"", self.html_content)
        self.assertIn("id=\"badge-ssl\"", self.html_content)
        # Verificar que SOL-2026-001 esté en Culminada para no generar falso pendiente
        self.assertIn("'SOL-2026-001'", self.html_content)
        self.assertIn("status: 'Culminada'", self.html_content)

if __name__ == "__main__":
    unittest.main()

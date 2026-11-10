# -*- coding: utf-8 -*-
import unittest
import json
import os
from app.main import (
    delete_work_order,
    delete_solicitud,
    delete_ssl_request,
    get_technicians
)
from app.database import get_db

class TestSeniorFixes(unittest.TestCase):
    def test_1_delete_ot_with_foreign_keys(self):
        """Prueba que eliminar una OT vinculada a salidas_materiales no falle por FK."""
        test_ot_id = "OT-TEST-DEL"
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO ordenes_trabajo (id, tipo, prioridad, equipo_id, descripcion, fecha_asignacion, status)
                VALUES (?, 'Correctivo', 'Alta', 'EQ-101', 'OT de prueba para borrado con FK', '2026-11-01', 'Pendiente')
            """, (test_ot_id,))
            cursor.execute("""
                INSERT OR REPLACE INTO salidas_materiales (id, fecha, ot_id, repuesto_id, repuesto_nombre, cantidad, despachado_por, receptor)
                VALUES ('SAL-TEST-01', '2026-11-01', ?, 'REP-01', 'Rodamiento', 1, 'Almacenista', 'Tecnico')
            """, (test_ot_id,))
            cursor.execute("""
                INSERT OR REPLACE INTO solicitudes_mantenimiento (id, tipo, urgencia, area, ubicacion, descripcion, solicitante, fecha_hora, status, ot_vinculada)
                VALUES ('SOL-TEST-01', 'Maquinaria', 'Alta', 'Area 1', 'Ubic 1', 'Falla', 'Solicitante', '2026-11-01 10:00', 'En proceso', ?)
            """, (test_ot_id,))
            cursor.execute("""
                INSERT OR REPLACE INTO notificaciones (id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES ('NOTIF-TEST-01', 'Tecnico', 'OT Asignada', 'Mensaje OT', 'info', '2026-11-01 10:00', 'ot', ?)
            """, (test_ot_id,))
            conn.commit()

        # Ejecutar función de eliminación
        res = delete_work_order(test_ot_id)
        self.assertTrue(res.get("success"))

        # Verificar en base de datos que se borró y se desvinculó de salidas
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM ordenes_trabajo WHERE id = ?", (test_ot_id,))
            self.assertIsNone(cursor.fetchone())

            cursor.execute("SELECT ot_id FROM salidas_materiales WHERE id = 'SAL-TEST-01'")
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertIsNone(row["ot_id"])

            cursor.execute("SELECT ot_vinculada FROM solicitudes_mantenimiento WHERE id = 'SOL-TEST-01'")
            row_sol = cursor.fetchone()
            self.assertIsNone(row_sol["ot_vinculada"])

            # Limpiar registros temporales
            cursor.execute("DELETE FROM salidas_materiales WHERE id = 'SAL-TEST-01'")
            cursor.execute("DELETE FROM solicitudes_mantenimiento WHERE id = 'SOL-TEST-01'")
            conn.commit()

    def test_2_delete_solicitudes_and_ssl(self):
        """Prueba los nuevos endpoints de eliminación para Solicitudes Interdepartamentales y Condiciones SSL."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO solicitudes_mantenimiento (id, tipo, urgencia, area, ubicacion, descripcion, solicitante, fecha_hora, status)
                VALUES ('SOL-TEST-DEL', 'Infraestructura', 'Media', 'Area X', 'Ubic X', 'Falla en iluminaria', 'Solicitante X', '2026-11-01 10:00', 'Aprobada')
            """)
            cursor.execute("""
                INSERT OR REPLACE INTO notificaciones (id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES ('NOTIF-SOL-DEL', 'Gerente', 'Nueva Solicitud', 'Solicitud nueva', 'warning', '2026-11-01 10:00', 'solicitud', 'SOL-TEST-DEL')
            """)
            cursor.execute("""
                INSERT OR REPLACE INTO solicitudes_ssl (id, codigo, fecha_hora, area, ubicacion, nivel_riesgo, descripcion, foto_evidencia, status, solicitante_nombre)
                VALUES ('SSL-TEST-DEL', 'COND-TEST', '2026-11-01 10:00', 'Area SSL', 'Ubic SSL', 'Alto', 'Cable pelado', 'data:image/svg+xml;base64,AAA', 'Pendiente', 'Ing. Argenis Morillo')
            """)
            cursor.execute("""
                INSERT OR REPLACE INTO notificaciones (id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES ('NOTIF-SSL-DEL', 'Gerente', 'Condición SSL', 'Condicion nueva', 'urgent', '2026-11-01 10:00', 'ssl', 'SSL-TEST-DEL')
            """)
            conn.commit()

        # Delete solicitud
        res_sol = delete_solicitud("SOL-TEST-DEL")
        self.assertTrue(res_sol.get("success"))

        # Delete ssl
        res_ssl = delete_ssl_request("SSL-TEST-DEL")
        self.assertTrue(res_ssl.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM solicitudes_mantenimiento WHERE id = 'SOL-TEST-DEL'")
            self.assertIsNone(cursor.fetchone())
            cursor.execute("SELECT id FROM solicitudes_ssl WHERE id = 'SSL-TEST-DEL'")
            self.assertIsNone(cursor.fetchone())
            cursor.execute("SELECT id FROM notificaciones WHERE enlace_id IN ('SOL-TEST-DEL', 'SSL-TEST-DEL')")
            self.assertEqual(len(cursor.fetchall()), 0)

    def test_3_technicians_endpoint(self):
        """Prueba que el endpoint get_technicians retorne únicamente técnicos válidos."""
        tecnicos = get_technicians()
        self.assertIsInstance(tecnicos, list)
        self.assertGreaterEqual(len(tecnicos), 2)
        for t in tecnicos:
            is_tec = t["role"] == "Tecnico" or "tecnico" in (t.get("cargo") or "").lower() or "técnico" in (t.get("cargo") or "").lower()
            self.assertTrue(is_tec)

    def test_4_html_content_integrity(self):
        """Verifica que index.html contenga las correcciones requeridas."""
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()

        # 1. Filtro en renderMisOTsView no debe tener || currentUser.role === 'Tecnico'
        self.assertNotIn("currentUser.role === 'Tecnico'", html[html.find("function renderMisOTsView"):html.find("function renderAlmacenView")])
        self.assertIn("o.tecnicoAcompanante === currentUser.id", html)

        # 2. Funciones eliminarSSL y eliminarSolicitud
        self.assertIn("function eliminarSSL(sslId)", html)
        self.assertIn("function eliminarSolicitud(solId)", html)

        # 3. Selector y persistencia de acompañante
        self.assertIn("cierreTecnicoAcompanante", html)
        self.assertIn("ot.tecnicoAcompanante = ", html)

if __name__ == "__main__":
    unittest.main()

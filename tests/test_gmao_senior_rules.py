# -*- coding: utf-8 -*-
"""
Suite de Pruebas Unitarias e Integración para las Reglas Senior de GMAO/CMMS:
1. Jefe Mantenimiento:
   - Eliminación del módulo "Panel departamento de compras".
   - Exportación e impresión de informes filtrados por rango de fechas (desde/hasta) en módulo compras ya existente.
2. Compras:
   - Eliminación de módulos: Almacén de repuestos, Control de compras.
   - Solo Proveedores y Panel de Compras (con sincronización inmediata).
   - Filtrado exclusivo de solicitudes creadas por el "Jefe de Mantenimiento".
   - Estados permitidos: [Pendiente, Aprobada, En tránsito]. Prohibido "Recibida".
3. Preventivo:
   - Bandeja de "Próximas intervenciones activas" sincronizada con el plan preventivo (excluye completadas y duplicadas).
   - Al cerrar la OT vinculada a preventiva: actualiza estado a 'Completado' y remueve alerta de vencimiento reactivamente.
4. Calendario (Cronogramas Preventivos):
   - Escala semanal en diagrama de cronograma.
   - Cabecera estructurada de 2 filas: Meses en fila superior (colspan) y semanas correspondientes en fila inferior.
"""

import unittest
import json
import os
import sys
from pathlib import Path
from fastapi.exceptions import HTTPException

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.main import (
    app,
    save_work_order,
    save_purchase,
    get_purchases,
    update_purchase_status,
    get_preventive_plans,
    check_preventive_alerts
)
from app.database import get_db, init_db

class TestGMAOSeniorRules(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        base_dir = Path(__file__).resolve().parent.parent
        cls.html_content = (base_dir / "index.html").read_text(encoding="utf-8")

    # =========================================================================
    # REGLA 1: JEFE MANTENIMIENTO
    # =========================================================================
    def test_1_1_jefe_mantenimiento_sin_panel_compras(self):
        """1.1 Verifica que Jefe Mantenimiento (Gerente) NO tenga el módulo Panel Dpto. Compras en sidebar"""
        gerente_block_start = self.html_content.find("if (currentUser.role === 'Gerente') {")
        almacen_block_start = self.html_content.find("else if (currentUser.role === 'Almacenista') {")
        self.assertGreater(gerente_block_start, 0)
        self.assertGreater(almacen_block_start, gerente_block_start)
        gerente_nav = self.html_content[gerente_block_start:almacen_block_start]

        self.assertNotIn("nav-compras-panel", gerente_nav)
        self.assertNotIn("Panel Dpto. Compras", gerente_nav)

    def test_1_2_informes_filtrados_rango_fechas_modulo_compras(self):
        """1.2 Verifica controles y lógica de exportación/impresión por rango de fechas en módulo compras ya existente"""
        self.assertIn("function exportarInformeComprasExcel()", self.html_content)
        self.assertIn("function imprimirInformeCompras()", self.html_content)
        self.assertIn("exportarInformeComprasExcel()", self.html_content)
        self.assertIn("imprimirInformeCompras()", self.html_content)
        # Verifica presencia en barra de acciones de compras
        self.assertIn("Exportar Excel", self.html_content)
        self.assertIn("Imprimir Informe", self.html_content)

    # =========================================================================
    # REGLA 2: COMPRAS
    # =========================================================================
    def test_2_1_compras_solo_panel_y_proveedores(self):
        """2.1 Compras elimina Almacén y Control de Compras; deja solo Panel de Compras y Proveedores"""
        sidebar_idx = self.html_content.find("function renderSidebar()")
        compras_block_start = self.html_content.find("currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras'", sidebar_idx)
        self.assertGreater(compras_block_start, 0)
        compras_block_end = self.html_content.find("document.getElementById('backupContainer')", compras_block_start)
        compras_nav = self.html_content[compras_block_start:compras_block_end]

        self.assertIn("nav-compras-panel", compras_nav)
        self.assertIn("nav-proveedores", compras_nav)
        self.assertNotIn("nav-almacen", compras_nav)
        self.assertNotIn("nav-compras\"", compras_nav)

    def test_2_2_compras_filtrado_creadas_por_jefe_mantenimiento(self):
        """2.2 Backend y Frontend filtran compras para que Compras solo vea las de Jefe de Mantenimiento"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO compras_materiales (id, fecha, descripcion, cant_solicitada, cant_recibida, status, creado_por)
                VALUES ('COM-TEST-JEFE', '2026-11-01', 'Rodamiento Motor Jefe', 2, 0, 'Pendiente', 'Ing. Carlos Mendoza (Jefe de Mantenimiento)');
            """)
            cursor.execute("""
                INSERT OR REPLACE INTO compras_materiales (id, fecha, descripcion, cant_solicitada, cant_recibida, status, creado_por)
                VALUES ('COM-TEST-OTRO', '2026-11-01', 'Cinta Embalaje Produccion', 10, 0, 'Pendiente', 'Operador Empaque (Producción)');
            """)
            conn.commit()

        # Al consultar compras como Compras:
        compras_res = get_purchases(role="Departamento de Compras")
        ids = [c["id"] for c in compras_res]
        self.assertIn("COM-TEST-JEFE", ids)
        self.assertNotIn("COM-TEST-OTRO", ids)

    def test_2_3_compras_gestion_estados_permitidos_y_prohibido_recibida(self):
        """2.3 Compras solo puede asignar [Pendiente, Aprobada, En tránsito]; Prohibido 'Recibida'"""
        # Intentar asignar 'Recibida' como rol Compras debe arrojar 403 Forbidden
        with self.assertRaises(HTTPException) as ctx:
            update_purchase_status("COM-TEST-JEFE", {"status": "Recibida", "rol": "Departamento de Compras"})
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("exclusivo para Jefe de Mantenimiento y Almacén", ctx.exception.detail)

        # Intentar guardar una compra directamente con status Recibida como Compras debe arrojar 403
        with self.assertRaises(HTTPException) as ctx_save:
            save_purchase({"id": "COM-TEST-INVALID", "descripcion": "Test", "cantSolicitada": 1, "status": "Recibida", "rol": "Compras"})
        self.assertEqual(ctx_save.exception.status_code, 403)

        # Actualizar a 'Aprobada' y 'En Tránsito' debe ser exitoso
        res_aprob = update_purchase_status("COM-TEST-JEFE", {"status": "Aprobada", "rol": "Departamento de Compras"})
        self.assertTrue(res_aprob.get("success"))

        res_trans = update_purchase_status("COM-TEST-JEFE", {"status": "En Tránsito", "rol": "Departamento de Compras"})
        self.assertTrue(res_trans.get("success"))

        # Jefe de Mantenimiento o Almacenista Sí pueden asignar 'Recibida'
        res_recibida = update_purchase_status("COM-TEST-JEFE", {"status": "Recibida", "rol": "Gerente"})
        self.assertTrue(res_recibida.get("success"))

    # =========================================================================
    # REGLA 3: PREVENTIVO (BANDEJA ACTIVAS & CIERRE OT REACTIVO)
    # =========================================================================
    def test_3_1_cierre_ot_preventiva_actualiza_plan_y_cancela_alertas(self):
        """3.1 Al cerrar OT preventiva vinculada, plan pasa a 'Completado' y remueve alerta de vencimiento"""
        plan_id = "PLN-TEST-PREV"
        ot_id = "OT-TEST-PREV"
        equipo_id = "EQ-101"

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO planes_preventivos (id, equipo_id, nombre, frecuencia, ultima_fecha, proxima_fecha, status)
                VALUES (?, ?, 'Mantenimiento Preventivo Bomba', 'Mensual', '2026-10-01', '2026-11-01', 'Pendiente');
            """, (plan_id, equipo_id))
            cursor.execute("""
                INSERT OR REPLACE INTO notificaciones (id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES ('NOTIF-PREV-PLN-TEST-PREV-2026-11-01', 'Gerente', 'Alerta Preventiva Próxima / Vencida', 'Rutina preventiva vencida', 'urgent', '2026-11-01 08:00', 'cronograma-anual', ?);
            """, (plan_id,))
            cursor.execute("""
                INSERT OR REPLACE INTO notificaciones (id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id)
                VALUES ('NOTIF-OT-5D-OT-TEST-PREV-2026-11-01', 'Gerente', 'Alerta Preventiva (En 5 días)', 'OT Preventiva programada', 'warning', '2026-11-01 08:00', 'ot', ?);
            """, (ot_id,))
            conn.commit()

        # Cerrar OT preventiva vinculada al plan
        ot_data = {
            "id": ot_id,
            "tipo": "Preventivo",
            "prioridad": "Alta",
            "equipoId": equipo_id,
            "descripcion": "Ejecución preventiva de bomba",
            "status": "Concluida",
            "planId": plan_id,
            "fechaFin": "2026-11-02",
            "actividades": "Mantenimiento preventivo completado con éxito"
        }
        res_close = save_work_order(ot_data)
        self.assertTrue(res_close.get("success"))

        # Validar en base de datos: Plan actualizado a 'Completado'
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, ultima_fecha FROM planes_preventivos WHERE id = ?;", (plan_id,))
            plan_row = cursor.fetchone()
            self.assertIsNotNone(plan_row)
            self.assertEqual(plan_row["status"], "Completado")
            self.assertEqual(plan_row["ultima_fecha"][:10], "2026-11-02")

            # Validar que las notificaciones de vencimiento fueron canceladas / eliminadas
            cursor.execute("""
                SELECT id FROM notificaciones 
                WHERE (enlace_id = ? OR enlace_id = ?) 
                  AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent'));
            """, (plan_id, ot_id))
            notifs = cursor.fetchall()
            self.assertEqual(len(notifs), 0, "Las notificaciones de vencimiento deben haber sido canceladas")

    def test_3_2_bandeja_proximas_intervenciones_sincronizada(self):
        """3.2 Verifica que la bandeja de próximas intervenciones activas filtre planes completados y ejecute sincronización"""
        self.assertIn("p.status !== 'Completado' && p.status !== 'Ejecutado'", self.html_content)
        self.assertIn("const planesActivosSinOT", self.html_content)
        self.assertIn("otPlanId", self.html_content)

    # =========================================================================
    # REGLA 4: VISTA DE CALENDARIO (ESTRUCTURA DE CABECERA Y ESCALA SEMANAL)
    # =========================================================================
    def test_4_1_calendario_escala_semanal_predeterminada(self):
        """4.1 La vista predeterminada del diagrama del plan es a escala semanal"""
        self.assertIn("let cronogramaEscala = 'semanal';", self.html_content)
        self.assertIn("function setCronogramaEscala(escala)", self.html_content)
        self.assertIn("Escala Semanal", self.html_content)
        self.assertIn("cronogramaEscala === 'semanal'", self.html_content)

    def test_4_2_estructura_cabecera_dos_filas_meses_y_semanas(self):
        """4.2 Cabecera estructurada: Meses en fila superior (colspan) y semanas correspondientes en fila inferior"""
        self.assertIn("mesesConfig.map(m => `<th colspan=\"${m.semanas.length}\"", self.html_content)
        self.assertIn("mesesConfig.flatMap(m => m.semanas.map(sNum =>", self.html_content)
        self.assertIn("rowspan=\"2\"", self.html_content)
        self.assertIn("Semana ${String(sNum).padStart(2,'0')}", self.html_content)

if __name__ == "__main__":
    unittest.main()

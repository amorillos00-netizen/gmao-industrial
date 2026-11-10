# Comprehensive Verification Script for GMAO Maintenance System Requirements
import unittest
import sqlite3
import os

from app.main import (
    save_work_order,
    get_system_config,
    update_system_config,
    save_purchase,
    delete_purchase,
    check_preventive_alerts,
    get_kpis,
    get_full_sync,
    post_full_sync
)

class TestGMAORequirements(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join("app", "static", "index.html")
        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

    def test_req_1_ot_persistence_and_update(self):
        """1. CORRECCIÓN DE PERSISTENCIA Y ACTUALIZACIÓN EN ÓRDENES DE TRABAJO (OT)"""
        ot_payload = {
            "id": "OT-TEST-PERSISTENCE",
            "tipo": "Correctivo",
            "prioridad": "Alta",
            "equipoId": "EQ-101",
            "descripcion": "Falla en motor principal",
            "tecnicoIds": ["u2"],
            "fechaProgramada": "2026-11-15",
            "fechaAsignacion": "2026-11-15",
            "status": "En Proceso",
            "tiempoIntervencion": 3.5,
            "tiempoParada": 4.0,
            "actividades": "Reemplazo de rodamientos",
            "repuestosUsados": [{"id": "REP-01", "name": "Rodamiento SKF 6205", "cant": 2}]
        }
        res1 = save_work_order(ot_payload)
        self.assertTrue(res1.get("success"))

        # Update OT with new fields - verify none are overwritten or reset
        ot_payload["status"] = "Concluida"
        ot_payload["tiempoIntervencion"] = 4.2
        ot_payload["tiempoParada"] = 4.5
        ot_payload["actividades"] = "Reemplazo de rodamientos y prueba de vibración superada"
        res2 = save_work_order(ot_payload)
        self.assertTrue(res2.get("success"))

        # Verify from database that fields were preserved and updated
        conn = sqlite3.connect(os.path.join("data", "gmao_enterprise.db"))
        cur = conn.cursor()
        cur.execute("SELECT status, tiempo_intervencion, tiempo_parada, actividades FROM ordenes_trabajo WHERE id = ?", ("OT-TEST-PERSISTENCE",))
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Concluida")
        self.assertEqual(row[1], 4.2)
        self.assertEqual(row[2], 4.5)
        self.assertEqual(row[3], "Reemplazo de rodamientos y prueba de vibración superada")

        # Frontend check: Ensure formOT submit merges with existing record
        self.assertIn("const existing = db.ots.find(x => x.id === editId) || {}", self.html_content)
        self.assertIn("fetch('/api/work-orders'", self.html_content)

    def test_req_2_multiannual_cronograma_and_5day_alerts(self):
        """2. CRONOGRAMA ANUAL MULTIANUAL Y ALERTAS DE 5 DÍAS"""
        # Test backend 5-day alert endpoint
        data = check_preventive_alerts()
        self.assertTrue(data.get("success"))
        self.assertIn("alerts", data)

        # Frontend checks
        self.assertIn("cronogramaAnioSeleccionado", self.html_content)
        self.assertIn("cambiarCronogramaAnio", self.html_content)
        self.assertIn("verificarAlertasPreventivasAnticipadas", self.html_content)

    def test_req_3_kpi_dashboard_print_button(self):
        """3. CORRECCIÓN DE BOTÓN DE IMPRESIÓN EN DASHBOARD KPI"""
        self.assertIn("imprimirDashboardKPI()", self.html_content)
        self.assertIn("function imprimirDashboardKPI()", self.html_content)
        self.assertIn("window.print()", self.html_content)

    def test_req_4_mttr_configurable_threshold(self):
        """4. CONFIGURACIÓN DEL MÍNIMO DE MTTR"""
        # Test API config GET and POST
        cfg = get_system_config()
        self.assertIn("mttr_target_hours", cfg)

        # Modify MTTR target to 1.8 hours
        res_post = update_system_config({"mttr_target_hours": 1.8})
        self.assertTrue(res_post.get("success"))
        self.assertEqual(res_post["config"]["mttr_target_hours"], 1.8)

        # Frontend checks
        self.assertIn("modalConfiguracionMTTR", self.html_content)
        self.assertIn("guardarConfiguracionMTTR", self.html_content)
        self.assertIn("openModalConfiguracionMTTR", self.html_content)

    def test_req_5_advanced_ot_filters(self):
        """5. FILTROS AVANZADOS EN ÓRDENES DE TRABAJO (OT)"""
        self.assertIn("otFiltroEquipo", self.html_content)
        self.assertIn("otFiltroPeriodo", self.html_content)
        self.assertIn("setOtFiltroEquipo", self.html_content)
        self.assertIn("setOtFiltroPeriodo", self.html_content)
        self.assertIn("limpiarFiltrosOT", self.html_content)

    def test_req_6_periodic_report_and_completed_ot_history(self):
        """6. MEJORAS EN INFORME PERIÓDICO Y HISTORIAL DE OTS CULMINADAS (NOVIEMBRE.DOCX)"""
        # Filter checks
        self.assertIn("informeFiltroEquipo", self.html_content)
        self.assertIn("informeFiltroPeriodo", self.html_content)
        self.assertIn("setInformeFiltroEquipo", self.html_content)
        self.assertIn("setInformePeriodoTipo", self.html_content)

        # Structure checks matching Noviembre.docx
        self.assertIn("Resumen Ejecutivo", self.html_content)
        self.assertIn("2.1 Mantenimiento Preventivo", self.html_content)
        self.assertIn("2.2 Mantenimiento Correctivo", self.html_content)
        self.assertIn("3. Otras Actividades", self.html_content)
        self.assertIn("Falla o Requerimiento", self.html_content)
        self.assertIn("Materiales Utilizados", self.html_content)

        # Strict signatures: strictly Jefe de Mantenimiento and Gerente de Planta
        self.assertIn("Jefe de Mantenimiento", self.html_content)
        self.assertIn("Gerente de Planta", self.html_content)
        self.assertIn("nombreJefe", self.html_content)
        self.assertIn("nombreGerentePlanta", self.html_content)

    def test_req_7_purchase_requests_modification(self):
        """7. GESTIÓN Y MODIFICACIÓN DE SOLICITUDES DE COMPRA"""
        # Test backend purchases CRUD
        comp_payload = {
            "id": "COM-TEST-MOD",
            "descripcion": "Correa trapezoidal B-54",
            "cantSolicitada": 4,
            "cantRecibida": 0,
            "precio": 25.50,
            "observaciones": "Línea de freidoras"
        }
        res1 = save_purchase(comp_payload)
        self.assertTrue(res1.get("success"))

        # Modify purchase
        comp_payload["cantSolicitada"] = 6
        comp_payload["precio"] = 28.00
        comp_payload["observaciones"] = "Urgente para freidora 2"
        res2 = save_purchase(comp_payload)
        self.assertTrue(res2.get("success"))

        # Verify modification in DB
        conn = sqlite3.connect(os.path.join("data", "gmao_enterprise.db"))
        cur = conn.cursor()
        cur.execute("SELECT cant_solicitada, precio, observaciones FROM compras_materiales WHERE id = ?", ("COM-TEST-MOD",))
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 6)
        self.assertEqual(row[1], 28.00)
        self.assertEqual(row[2], "Urgente para freidora 2")

        # Frontend check: presence of edit button and edit logic
        self.assertIn("openModalCompra('${c.id}')", self.html_content)
        self.assertIn("Modificar Solicitud de Compra", self.html_content)

    def test_req_8_ot_print_format_correction(self):
        """8. CORRECCIÓN EN FORMATO DE IMPRESIÓN DE OT"""
        # Ensure "Recepción Conforme" is completely removed from OT print format
        imprimir_ot_start = self.html_content.find("function imprimirOT(otId)")
        imprimir_ot_end = self.html_content.find("window.print();", imprimir_ot_start)
        ot_print_section = self.html_content[imprimir_ot_start:imprimir_ot_end]

        self.assertNotIn("Recepción Conforme", ot_print_section)
        self.assertNotIn("Recepcin Conforme", ot_print_section)
        self.assertIn("Jefe de Mantenimiento", ot_print_section)

    def test_req_9_alphanumeric_natural_sorting(self):
        """9. ORDENAMIENTO ALFANUMÉRICO EN ACTIVOS Y UBICACIONES"""
        self.assertIn("function naturalCompare", self.html_content)
        self.assertIn("toggleEquiposSortOrder", self.html_content)
        self.assertIn("equiposSortOrder", self.html_content)
        self.assertIn("naturalCompare(a.id, b.id, equiposSortOrder === 'ASC')", self.html_content)

if __name__ == "__main__":
    unittest.main()

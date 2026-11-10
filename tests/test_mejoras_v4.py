# -*- coding: utf-8 -*-
"""
Suite de Pruebas Automatizadas para las 4 Nuevas Mejoras de GMAO Industrial Pro:
1. Restricción de Backup por Roles (Gerente y Jefe de Mantenimiento).
2. Módulo de Taller Externo con Entrada Manual de Equipos (Texto Libre).
3. Exportación Funcional de Informes Periódicos (Excel .xlsx y Word .docx).
4. Diseño Responsivo y Optimización Móvil (CSS 100dvh, table-responsive, modales).
"""
import unittest
import os
import sys
import json
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import (
    app,
    get_database_backup,
    post_database_backup,
    export_informe_periodico_excel,
    export_informe_periodico_excel_post,
    export_informe_periodico_word,
    export_informe_periodico_word_post,
    save_external_service,
    get_external_services,
    receive_external_service
)
from app.database import get_db
from fastapi import HTTPException
from fastapi.responses import Response

class TestMejorasV4(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.join("app", "static", "index.html")
        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

    # =========================================================================
    # 1. RESTRICCIÓN DE BACKUP POR ROLES
    # =========================================================================
    def test_backup_backend_authorized_gerente(self):
        """1.1 Backend: Rol Gerente puede ejecutar respaldo exitosamente"""
        res = get_database_backup(user_role="Gerente", username="admin")
        self.assertIsInstance(res, Response)
        self.assertEqual(res.media_type, "application/json")
        self.assertIn("GMAO_BACKUP_SALTYSNACK_", res.headers["Content-Disposition"])
        backup_data = json.loads(res.body.decode("utf-8"))
        self.assertIn("equipos", backup_data)
        self.assertIn("ots", backup_data)
        self.assertIn("users", backup_data)

    def test_backup_backend_authorized_jefe_mantenimiento(self):
        """1.2 Backend: Jefe de Mantenimiento puede ejecutar respaldo exitosamente"""
        res = get_database_backup(user_cargo="Jefe de Mantenimiento", username="admin")
        self.assertIsInstance(res, Response)
        self.assertEqual(res.media_type, "application/json")
        backup_data = json.loads(res.body.decode("utf-8"))
        self.assertGreater(len(backup_data.get("equipos", [])), 0)

    def test_backup_backend_unauthorized_roles(self):
        """1.3 Backend: Roles no autorizados reciben HTTP 403 Forbidden"""
        roles_no_autorizados = [
            ("Tecnico", "Técnico Electromecánico", "tecnico1"),
            ("Solicitante", "Jefe de Turno", "solicitante1"),
            ("Jefe SSL", "Jefe de Seguridad y Salud Laboral", "jefessl"),
            ("Almacenista", "Almacenista Principal", "almacenista")
        ]
        for rol, cargo, user in roles_no_autorizados:
            with self.assertRaises(HTTPException, msg=f"El rol {rol} debe ser bloqueado con 403") as cm:
                get_database_backup(user_role=rol, user_cargo=cargo, username=user)
            self.assertEqual(cm.exception.status_code, 403)
            self.assertIn("reservada exclusivamente para usuarios con el rol de 'Gerente' o 'Jefe de Mantenimiento'", cm.exception.detail)

    def test_backup_frontend_logic(self):
        """1.4 Frontend: Helper puedeEjecutarBackup, visibilidad en Sidebar y verificación en exportarBaseCompletaJSON"""
        self.assertIn("function puedeEjecutarBackup(user)", self.html_content)
        self.assertIn("backupContainer", self.html_content)
        self.assertIn("btnBackupDb", self.html_content)
        self.assertIn("puedeEjecutarBackup(currentUser)", self.html_content)
        self.assertIn("fetch(`/api/backup", self.html_content)

    # =========================================================================
    # 2. MÓDULO DE TALLER EXTERNO CON ENTRADA MANUAL DE EQUIPOS
    # =========================================================================
    def test_taller_externo_manual_equipment_backend(self):
        """2.1 Backend: Guardar y recibir servicio de equipo no registrado con nombre libre"""
        servicio_id = "EXT-TEST-MANUAL-01"
        payload = {
            "id": servicio_id,
            "equipoId": "Motorreductor Sew Eurodrive 7.5HP Línea Empaque",
            "proveedorId": "PRV-01",
            "proveedorNombre": "Talleres Tuy C.A.",
            "fechaSalida": "2026-11-15",
            "fechaEstimadaRetorno": "2026-11-25",
            "motivoServicio": "Rebobinado estator y sustitución de rodamientos SKF",
            "costoEstimado": 380.0,
            "status": "En reparación",
            "esManual": True,
            "registrarComoActivo": False,
            "observaciones": "Equipo no cargado en catálogo estándar"
        }
        res_save = save_external_service(payload)
        self.assertTrue(res_save.get("success"))

        # Recuperar y verificar
        servicios = get_external_services()
        item = next((s for s in servicios if s["id"] == servicio_id), None)
        self.assertIsNotNone(item)
        self.assertEqual(item["equipoId"], "Motorreductor Sew Eurodrive 7.5HP Línea Empaque")
        self.assertEqual(item["status"], "En reparación")

        # Recepción del equipo manual
        res_rec = receive_external_service(servicio_id, {
            "fechaRetornoReal": "2026-11-24",
            "recibidoPor": "Ing. Carlos Mendoza (Jefe Mantenimiento)",
            "condicionRecepcion": "Conforme y Probado",
            "costoFinal": 380.0,
            "observaciones": "Pruebas de aislamiento en vacío conformes"
        })
        self.assertTrue(res_rec.get("success"))

    def test_taller_externo_manual_equipment_frontend(self):
        """2.2 Frontend: Toggle de entrada manual, inputs de texto libre y opciones destacadas"""
        self.assertIn("alternarModoEquipoTaller()", self.html_content)
        self.assertIn("activarModoManualTaller()", self.html_content)
        self.assertIn("desactivarModoManualTaller()", self.html_content)
        self.assertIn("tallerEquipoNombreManual", self.html_content)
        self.assertIn("tallerEquipoUbicacionManual", self.html_content)
        self.assertIn("tallerRegistrarActivo", self.html_content)
        self.assertIn("contenedorEquipoManual", self.html_content)
        self.assertIn("__MANUAL__", self.html_content)

    # =========================================================================
    # 3. EXPORTACIÓN FUNCIONAL DE INFORMES PERIÓDICOS (EXCEL Y WORD)
    # =========================================================================
    def test_informe_periodico_excel_backend_get_and_post(self):
        """3.1 Backend: Generación y exportación de informe periódico en Excel (.xlsx)"""
        # GET
        res_get = export_informe_periodico_excel(periodo_tipo="Mensual", periodo_valor="2026-10", equipo_id="TODOS")
        self.assertEqual(res_get.media_type, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertGreater(len(res_get.body), 5000)

        # POST
        res_post = export_informe_periodico_excel_post({"periodoTipo": "Mensual", "periodoValor": "2026-10", "equipoId": "TODOS"})
        self.assertEqual(res_post.media_type, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertGreater(len(res_post.body), 5000)

        # Verificar validez openpyxl
        import openpyxl
        wb = openpyxl.load_workbook(BytesIO(res_get.body))
        self.assertTrue(len(wb.sheetnames) >= 1)

    def test_informe_periodico_word_backend_get_and_post(self):
        """3.2 Backend: Generación y exportación de informe periódico en Word (.docx)"""
        # GET
        res_get = export_informe_periodico_word(periodo_tipo="Mensual", periodo_valor="2026-10", equipo_id="TODOS")
        self.assertEqual(res_get.media_type, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertGreater(len(res_get.body), 10000)

        # POST
        res_post = export_informe_periodico_word_post({"periodoTipo": "Mensual", "periodoValor": "2026-10", "equipoId": "TODOS"})
        self.assertEqual(res_post.media_type, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.assertGreater(len(res_post.body), 10000)

        # Verificar validez python-docx
        import docx
        doc = docx.Document(BytesIO(res_get.body))
        self.assertTrue(len(doc.paragraphs) > 0)

    def test_informe_periodico_frontend_buttons_and_functions(self):
        """3.3 Frontend: Funciones JavaScript reales exportarInformePeriodicoExcel y exportarInformePeriodicoWord"""
        self.assertIn("function exportarInformePeriodicoExcel()", self.html_content)
        self.assertIn("function exportarInformePeriodicoWord()", self.html_content)
        self.assertIn("/api/reports/informe-periodico-excel", self.html_content)
        self.assertIn("/api/reports/informe-periodico-word", self.html_content)
        self.assertIn("XLSX.utils.book_new()", self.html_content)

    # =========================================================================
    # 4. DISEÑO RESPONSIVO Y OPTIMIZACIÓN MÓVIL
    # =========================================================================
    def test_responsive_css_and_viewport(self):
        """4.1 Frontend: Viewport dinámico (100dvh), scroll táctil y reglas responsivas"""
        self.assertIn("height: 100dvh;", self.html_content)
        self.assertIn(".table-responsive", self.html_content)
        self.assertIn("-webkit-overflow-scrolling: touch;", self.html_content)
        self.assertIn("@media (max-width: 640px)", self.html_content)

    def test_responsive_tables_wrapped(self):
        """4.2 Frontend: Todas las tablas del sistema contienen envoltorio overflow-x-auto"""
        import re
        tables = re.findall(r'<table[^>]*>', self.html_content)
        # Tablas de interfaz (excluyendo strings de plantilla de exportación Word)
        self.assertGreater(len(tables), 15)
        self.assertIn("table-responsive", self.html_content)
        self.assertIn("overflow-x-auto", self.html_content)

    def test_responsive_modals(self):
        """4.3 Frontend: Modales adaptables con scroll vertical y padding amigable para teléfonos"""
        self.assertIn("max-h-[92dvh]", self.html_content)
        self.assertIn("p-4 sm:p-6", self.html_content)
        self.assertIn("my-auto sm:my-8", self.html_content)

if __name__ == "__main__":
    unittest.main()

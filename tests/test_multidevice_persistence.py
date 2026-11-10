# -*- coding: utf-8 -*-
"""
Test Suite de Persistencia Centralizada en DB y Conectividad Multi-dispositivo (Android / Windows)
Valida los requerimientos de la actualizacion multiplataforma de GMAO Industrial Pro.
"""

import unittest
from pathlib import Path
from app.config import SERVER_HOST, SERVER_PORT
from app.database import get_db
from app.main import (
    save_solicitud,
    get_solicitudes,
    delete_solicitud,
    save_ssl_request,
    get_ssl_requests,
    delete_ssl_request,
    save_purchase,
    get_purchases,
    delete_purchase,
    save_spare_part,
    get_inventory,
    delete_spare_part
)

class TestMultiDevicePersistence(unittest.TestCase):

    def test_backend_0_0_0_0_binding(self):
        """Verifica que el servidor este configurado para escuchar en 0.0.0.0 para acceso multi-dispositivo."""
        self.assertEqual(SERVER_HOST, "0.0.0.0", "SERVER_HOST debe ser 0.0.0.0 para aceptar conexiones LAN/Android")

    def test_solicitudes_st_crud_persistence(self):
        """Verifica creacion, edicion y eliminacion directa en BD para Solicitudes ST."""
        test_id = "SOL-TEST-LAN-01"
        sol_data = {
            "id": test_id,
            "tipo": "Maquinaria / Equipo",
            "urgencia": "Alta",
            "area": "Linea Envasado 1",
            "ubicacion": "Bomba Centrifuga",
            "descripcion": "Fuga por sello mecanico",
            "solicitante": "Roberto Gomez",
            "fechaHora": "2026-11-06 14:00",
            "status": "Aprobada",
            "otVinculada": None
        }

        # 1. Crear
        res_create = save_solicitud(sol_data)
        self.assertTrue(res_create.get("success"))
        self.assertEqual(res_create.get("id"), test_id)

        # Verificar en DB
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT area, descripcion, status FROM solicitudes_mantenimiento WHERE id = ?;", (test_id,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["area"], "Linea Envasado 1")
            self.assertEqual(row["status"], "Aprobada")

        # 2. Editar
        sol_data["descripcion"] = "Fuga corregida en prueba de edicion"
        sol_data["status"] = "En proceso"
        res_edit = save_solicitud(sol_data)
        self.assertTrue(res_edit.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT descripcion, status FROM solicitudes_mantenimiento WHERE id = ?;", (test_id,))
            row = cursor.fetchone()
            self.assertEqual(row["descripcion"], "Fuga corregida en prueba de edicion")
            self.assertEqual(row["status"], "En proceso")

        # 3. Eliminar
        res_del = delete_solicitud(test_id)
        self.assertTrue(res_del.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM solicitudes_mantenimiento WHERE id = ?;", (test_id,))
            self.assertIsNone(cursor.fetchone())

    def test_reportes_ssl_crud_persistence(self):
        """Verifica creacion, edicion y eliminacion directa en BD para Reportes SSL."""
        test_id = "SSL-TEST-LAN-01"
        ssl_data = {
            "id": test_id,
            "codigo": "COND-TEST-99",
            "fechaHora": "2026-11-06 14:10",
            "area": "Planta Central",
            "ubicacion": "Galpon de Empaque",
            "nivelRiesgo": "Alto",
            "descripcion": "Riesgo de atrapamiento en transportador",
            "accionPropuesta": "Instalar guarda perimetral",
            "solicitanteId": "u5",
            "solicitanteNombre": "Ing. Argenis Morillo",
            "fotoEvidencia": "data:image/svg+xml;utf8,<svg></svg>",
            "status": "Pendiente"
        }

        # 1. Crear
        res_create = save_ssl_request(ssl_data)
        self.assertTrue(res_create.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nivel_riesgo, status FROM solicitudes_ssl WHERE id = ?;", (test_id,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["codigo"], "COND-TEST-99")
            self.assertEqual(row["status"], "Pendiente")

        # 2. Editar
        ssl_data["descripcion"] = "Riesgo mitigado mediante enclavamiento electrico"
        ssl_data["status"] = "Corregida"
        res_edit = save_ssl_request(ssl_data)
        self.assertTrue(res_edit.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT descripcion, status FROM solicitudes_ssl WHERE id = ?;", (test_id,))
            row = cursor.fetchone()
            self.assertEqual(row["descripcion"], "Riesgo mitigado mediante enclavamiento electrico")
            self.assertEqual(row["status"], "Corregida")

        # 3. Eliminar
        res_del = delete_ssl_request(test_id)
        self.assertTrue(res_del.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM solicitudes_ssl WHERE id = ?;", (test_id,))
            self.assertIsNone(cursor.fetchone())

    def test_compras_crud_persistence(self):
        """Verifica creacion, edicion y eliminacion directa en BD para Compras."""
        test_id = "COM-TEST-LAN-01"
        compra_data = {
            "id": test_id,
            "fecha": "2026-11-06",
            "descripcion": "Kit de rodamientos de repuesto",
            "cantSolicitada": 4,
            "cantRecibida": 2,
            "moneda": "$",
            "precio": 50.0,
            "proveedorId": "PRV-01",
            "observaciones": "Entrega parcial"
        }

        # 1. Crear
        res_create = save_purchase(compra_data)
        self.assertTrue(res_create.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT descripcion, cant_solicitada, precio FROM compras_materiales WHERE id = ?;", (test_id,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["cant_solicitada"], 4)
            self.assertEqual(row["precio"], 50.0)

        # 2. Editar
        compra_data["cantRecibida"] = 4
        compra_data["observaciones"] = "Entrega completa en almacen"
        res_edit = save_purchase(compra_data)
        self.assertTrue(res_edit.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cant_recibida, observaciones FROM compras_materiales WHERE id = ?;", (test_id,))
            row = cursor.fetchone()
            self.assertEqual(row["cant_recibida"], 4)
            self.assertEqual(row["observaciones"], "Entrega completa en almacen")

        # 3. Eliminar
        res_del = delete_purchase(test_id)
        self.assertTrue(res_del.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM compras_materiales WHERE id = ?;", (test_id,))
            self.assertIsNone(cursor.fetchone())

    def test_materiales_inventario_crud_persistence(self):
        """Verifica creacion, edicion y eliminacion directa en BD para Materiales / Repuestos."""
        test_id = "REP-TEST-LAN-01"
        rep_data = {
            "id": test_id,
            "codigo": "TEST-ROD-01",
            "name": "Rodamiento de Rodillos Test",
            "stock": 10,
            "stockMin": 3,
            "um": "pza",
            "costo": 25.5,
            "proveedorId": "PRV-01"
        }

        # 1. Crear
        res_create = save_spare_part(rep_data)
        self.assertTrue(res_create.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nombre, stock, costo_unitario FROM repuestos_materiales WHERE id = ?;", (test_id,))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["codigo"], "TEST-ROD-01")
            self.assertEqual(row["stock"], 10)

        # 2. Editar
        rep_data["stock"] = 18
        rep_data["costo"] = 28.0
        res_edit = save_spare_part(rep_data)
        self.assertTrue(res_edit.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stock, costo_unitario FROM repuestos_materiales WHERE id = ?;", (test_id,))
            row = cursor.fetchone()
            self.assertEqual(row["stock"], 18)
            self.assertEqual(row["costo_unitario"], 28.0)

        # 3. Eliminar
        res_del = delete_spare_part(test_id)
        self.assertTrue(res_del.get("success"))

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM repuestos_materiales WHERE id = ?;", (test_id,))
            self.assertIsNone(cursor.fetchone())

    def test_frontend_no_localstorage_operational_and_dynamic_hostname(self):
        """Verifica que index.html elimine almacenamiento local para datos operativos y use window.location.hostname."""
        base_dir = Path(__file__).resolve().parent.parent
        index_content = (base_dir / "index.html").read_text(encoding="utf-8")

        # 1. getApiUrl debe existir y usar window.location.hostname dinámico
        self.assertIn("function getApiUrl(endpoint)", index_content)
        self.assertIn("loc.hostname", index_content)

        # 2. No debe guardar el objeto db en localStorage
        self.assertNotIn("localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(db))", index_content)

        # 3. loadDatabase debe limpiar claves operativas anteriores
        self.assertIn("localStorage.removeItem(LOCAL_STORAGE_KEY);", index_content)

        # 4. Endpoints de persistencia directa para los 4 modulos
        self.assertIn("fetch(getApiUrl('/api/solicitudes')", index_content)
        self.assertIn("fetch(getApiUrl('/api/ssl')", index_content)
        self.assertIn("fetch(getApiUrl('/api/purchases')", index_content)
        self.assertIn("fetch(getApiUrl('/api/inventory')", index_content)
        self.assertIn("fetch(getApiUrl(`/api/inventory/${id}`)", index_content)

if __name__ == "__main__":
    unittest.main()

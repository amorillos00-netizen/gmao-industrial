# -*- coding: utf-8 -*-
"""
Test Suite de Sincronización en Red Local y Persistencia Real
Verifica persistencia en SQLite, control de versiones y funciones de usuarios.
"""
import unittest
import sqlite3
import os

from app.main import (
    create_or_update_user,
    get_users,
    delete_user,
    get_full_sync,
    post_full_sync,
    get_sync_version
)
from app.database import get_db

class TestSyncAndRealTime(unittest.TestCase):

    def test_sync_version_endpoint(self):
        """Verifica que get_sync_version responda correctamente."""
        res = get_sync_version()
        self.assertIn("version", res)
        self.assertIn("timestamp", res)
        self.assertIsInstance(res["version"], int)

    def test_users_crud_and_persistence(self):
        """Verifica creación, consulta y eliminación de usuarios directamente en SQLite."""
        test_user = {
            "id": "u_test_lan_99",
            "username": "operador_lan",
            "name": "Operador de Planta LAN",
            "pass": "1234",
            "role": "Tecnico",
            "departamento": "Mantenimiento"
        }
        # 1. Crear usuario
        res_post = create_or_update_user(test_user)
        self.assertTrue(res_post.get("success"))

        # 2. Verificar persistencia real en la BD SQLite
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, nombre_completo, rol_id FROM usuarios WHERE id = ?;", ("u_test_lan_99",))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["username"], "operador_lan")
            self.assertEqual(row["rol_id"], "ROL-TEC")

        # 3. Consultar via get_users()
        users = get_users()
        self.assertTrue(any(u["id"] == "u_test_lan_99" for u in users))

        # 4. Eliminar usuario
        res_del = delete_user("u_test_lan_99")
        self.assertTrue(res_del.get("success"))

        # 5. Verificar que ya no está en SQLite
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE id = ?;", ("u_test_lan_99",))
            self.assertIsNone(cursor.fetchone())

    def test_sync_reconciliation_with_users(self):
        """Verifica que post_full_sync guarde usuarios en SQLite y get_full_sync los devuelva."""
        sync_payload = {
            "users": [
                {
                    "id": "u_sync_lan_88",
                    "username": "tecnico_guardia",
                    "name": "Técnico de Guardia LAN",
                    "pass": "1234",
                    "role": "Tecnico",
                    "departamento": "Mantenimiento"
                }
            ],
            "equipos": [],
            "repuestos": [],
            "ots": []
        }
        res_post = post_full_sync(sync_payload)
        self.assertTrue(res_post.get("success"))

        # Verificar que get_full_sync devuelve al usuario sincronizado
        full_data = get_full_sync()
        self.assertTrue(full_data.get("success"))
        data = full_data["data"]
        self.assertIn("users", data)
        self.assertTrue(any(u["id"] == "u_sync_lan_88" for u in data["users"]))

        # Limpiar
        with get_db() as conn:
            conn.execute("DELETE FROM usuarios WHERE id = 'u_sync_lan_88';")
            conn.commit()

if __name__ == "__main__":
    unittest.main()

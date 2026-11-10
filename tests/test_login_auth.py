# -*- coding: utf-8 -*-
"""
Test Suite de Autenticacion y Login
Valida el funcionamiento robusto del login en backend y frontend.
"""

import unittest
from pathlib import Path
from fastapi.exceptions import HTTPException
from app.main import login

class TestLoginAuth(unittest.TestCase):

    def test_login_authorized_roles(self):
        """Verifica autenticacion exitosa para todos los roles autorizados."""
        roles_to_test = [
            ("admin", "Gerente"),
            ("tecnico1", "Tecnico"),
            ("solicitante1", "Solicitante"),
            ("jefessl", "Jefe SSL"),
            ("gerente_planta", "Gerente"),
            ("almacenista", "Almacenista")
        ]
        for username, expected_role in roles_to_test:
            res = login({"username": username, "password": "1234"})
            self.assertTrue(res.get("success"), f"Fallo login para {username}")
            self.assertEqual(res["user"]["role"], expected_role)
            self.assertIn("cargo", res["user"])
            self.assertIn("name", res["user"])

    def test_login_invalid_credentials(self):
        """Verifica rechazo con 401 ante credenciales invalidas."""
        with self.assertRaises(HTTPException) as ctx:
            login({"username": "admin", "password": "wrong_password"})
        self.assertEqual(ctx.exception.status_code, 401)

        with self.assertRaises(HTTPException) as ctx2:
            login({"username": "non_existent_user", "password": "1234"})
        self.assertEqual(ctx2.exception.status_code, 401)

    def test_frontend_login_implementation(self):
        """Verifica que index.html oculte el modal con display:none y soporte API login."""
        base_dir = Path(__file__).resolve().parent.parent
        content = (base_dir / "index.html").read_text(encoding="utf-8")

        # 1. db inicializado de inmediato sin ser null
        self.assertIn("let db = JSON.parse(JSON.stringify(initialData));", content)

        # 2. Soporte de API /api/auth/login
        self.assertIn("/api/auth/login", content)

        # 3. Ocultamiento forzado del modal removiendo clase flex y aplicando display: none
        self.assertIn("modal.classList.remove('flex');", content)
        self.assertIn("modal.style.display = 'none';", content)

        # 4. Verificacion de startApp y document.readyState
        self.assertIn("function startApp()", content)
        self.assertIn("document.readyState === 'loading'", content)

if __name__ == "__main__":
    unittest.main()

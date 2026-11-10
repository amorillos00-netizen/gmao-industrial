"""
Unit and Integration Tests for GMAO Maintenance System Critical Modules:
1. Persistencia de Alertas en Mantenimiento Preventivo
2. Selección de Fotografías desde Galería y Cámara
"""
import unittest
import sqlite3
import os
import json
from datetime import datetime, timedelta

from app.database import get_db, init_db
from app.main import (
    save_work_order,
    check_preventive_alerts,
    get_notificaciones,
    recalculate_preventive_alerts,
    get_full_sync
)

class TestCriticalModulesAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        with open("index.html", "r", encoding="utf-8") as f:
            cls.html_content = f.read()
        with open(os.path.join("app", "static", "index.html"), "r", encoding="utf-8") as f:
            cls.static_html_content = f.read()

    def test_module1_activa_column_and_table_schema(self):
        """Verifica existencia de columna 'activa' y estado en notificaciones y planes"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(notificaciones);")
            cols = [c[1] for c in cursor.fetchall()]
            self.assertIn("activa", cols, "La tabla notificaciones debe contar con la columna booleana 'activa'")

            cursor.execute("PRAGMA table_info(planes_preventivos);")
            p_cols = [c[1] for c in cursor.fetchall()]
            self.assertIn("status", p_cols, "La tabla planes_preventivos debe contar con columna 'status'")

    def test_module1_cierre_ot_reactivo_desactiva_alertas_y_avanza_ciclo(self):
        """Al cerrar una OT preventiva, el plan se completa, avanza su fecha futura y desactiva las alertas"""
        plan_id = "PLN-TEST-AUDIT-01"
        ot_id = "OT-TEST-AUDIT-01"
        equipo_id = "EQ-101"
        fecha_prog = "2026-11-01"

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO planes_preventivos (id, equipo_id, nombre, frecuencia, frecuencia_tipo, frecuencia_valor, ultima_fecha, proxima_fecha, status)
                VALUES (?, ?, 'Inspección de Motores Críticos', 'Mensual', 'meses', 1, '2026-10-01', ?, 'Pendiente');
            """, (plan_id, equipo_id, fecha_prog))

            cursor.execute("""
                INSERT OR REPLACE INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id, activa)
                VALUES (?, NULL, 'Gerente', 'Alerta Preventiva (En 5 días)', 'Preventivo por vencer', 'warning', '2026-10-27 08:00', 'plan', ?, 1);
            """, (f"NOTIF-PREV-5D-{plan_id}-2026-11-01", plan_id))

            cursor.execute("""
                INSERT OR REPLACE INTO notificaciones (id, usuario_id, rol_destino, titulo, mensaje, tipo, fecha_hora, enlace_tipo, enlace_id, activa)
                VALUES (?, NULL, 'Gerente', 'Alerta Preventiva (En 5 días)', 'OT Preventiva programada', 'warning', '2026-10-27 08:00', 'ot', ?, 1);
            """, (f"NOTIF-OT-5D-{ot_id}-2026-11-01", ot_id))
            conn.commit()

        # Cerrar y completar la OT
        ot_payload = {
            "id": ot_id,
            "tipo": "Preventivo",
            "prioridad": "Alta",
            "equipoId": equipo_id,
            "planId": plan_id,
            "descripcion": "Inspección completada satisfactoriamente",
            "fechaProgramada": fecha_prog,
            "fechaFin": "2026-11-01",
            "status": "Concluida",
            "actividades": "Revisión y lubricación general"
        }
        res = save_work_order(ot_payload)
        self.assertTrue(res.get("success"))

        # Validar base de datos
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, ultima_fecha, proxima_fecha FROM planes_preventivos WHERE id = ?;", (plan_id,))
            plan = cursor.fetchone()
            self.assertEqual(plan["status"], "Completado")
            self.assertEqual(plan["ultima_fecha"][:10], "2026-11-01")
            self.assertEqual(plan["proxima_fecha"][:10], "2026-12-01")  # Avanzó 1 mes automáticamente

            # Validar que las alertas de vencimiento ya no son activas
            cursor.execute("""
                SELECT id FROM notificaciones 
                WHERE (enlace_id = ? OR enlace_id = ?) 
                  AND COALESCE(activa, 1) = 1
                  AND (titulo LIKE '%Preventiv%' OR titulo LIKE '%Vencid%' OR tipo IN ('warning', 'urgent'));
            """, (plan_id, ot_id))
            active_notifs = cursor.fetchall()
            self.assertEqual(len(active_notifs), 0, "No deben quedar alertas preventivas activas tras el cierre de OT")

    def test_module1_recalculate_cache_invalidation_endpoint(self):
        """Endpoint /api/alerts/recalculate invalida y purga notificaciones de OTs concluidas"""
        res = recalculate_preventive_alerts()
        self.assertTrue(res.get("success"))
        self.assertIn("message", res)

    def test_module1_preventive_check_ignores_concluded_ots(self):
        """check_preventive_alerts no genera alertas para planes completados o con OT concluida"""
        res = check_preventive_alerts()
        self.assertTrue(res.get("success"))
        alert_ids = [a["id"] for a in res.get("alerts", [])]
        self.assertNotIn("PLN-TEST-AUDIT-01", alert_ids)
        self.assertNotIn("OT-TEST-AUDIT-01", alert_ids)

    def test_module2_frontend_gallery_camera_dual_inputs(self):
        """Frontend dispone de opciones explícitas para Cámara y Galería local en evidencias fotográficas"""
        for content in [self.html_content, self.static_html_content]:
            # Evidencia inicial OT
            self.assertIn('inputFotoInicialOT_cam', content)
            self.assertIn('inputFotoInicialOT_gal', content)
            self.assertIn('Subir de Galería', content)

            # Evidencias de Cierre OT (Antes y Después)
            self.assertIn('inputFotoAntes_cam', content)
            self.assertIn('inputFotoAntes_gal', content)
            self.assertIn('inputFotoDespues_cam', content)
            self.assertIn('inputFotoDespues_gal', content)

            # Evidencia SSL
            self.assertIn('inputFotoSSL_cam', content)
            self.assertIn('inputFotoSSL_gal', content)

            # Función de compresión con validación y thumbnail
            self.assertIn('file.type.startsWith(\'image/\')', content)
            self.assertIn('file.size > 25 * 1024 * 1024', content)
            self.assertIn('canvas.toDataURL(\'image/jpeg\', 0.75)', content)
            self.assertIn('eliminarFotoEvidencia', content)

    def test_module2_android_permissions_and_chooser(self):
        """Android app solicita permiso READ_MEDIA_IMAGES en Android 13+ y soporta Chooser"""
        with open("android/app/src/main/java/com/gmao/cmms/MainActivity.java", "r", encoding="utf-8") as f:
            java_code = f.read()

        self.assertIn("Manifest.permission.READ_MEDIA_IMAGES", java_code)
        self.assertIn("Intent.ACTION_CHOOSER", java_code)
        self.assertIn("Intent.ACTION_GET_CONTENT", java_code)

        with open("android/app/src/main/AndroidManifest.xml", "r", encoding="utf-8") as f:
            manifest_code = f.read()
        self.assertIn("android.permission.READ_MEDIA_IMAGES", manifest_code)
        self.assertIn("android.permission.READ_EXTERNAL_STORAGE", manifest_code)

if __name__ == "__main__":
    unittest.main()

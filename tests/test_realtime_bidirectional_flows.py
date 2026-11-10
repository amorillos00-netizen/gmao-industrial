# -*- coding: utf-8 -*-
"""
Test Suite de Sincronizacion Realtime y Flujos Bidireccionales Estrictos:
Solicitante <-> Jefe Mantenimiento y Jefe SSL <-> Jefe Mantenimiento.
"""

import unittest
from datetime import datetime
from app.database import get_db
from app.main import (
    save_solicitud,
    delete_solicitud,
    save_ssl_request,
    delete_ssl_request,
    save_work_order,
    delete_work_order,
    get_notificaciones,
    get_sync_version
)

class TestRealtimeBidirectionalFlows(unittest.TestCase):

    def test_flow_solicitante_jefe_mantenimiento(self):
        """Flujo bidireccional estricto Solicitante <-> Jefe Mantenimiento."""
        sol_id = "SOL-TEST-FLOW-01"
        ot_id = "OT-TEST-FLOW-01"

        try:
            # 1. Solicitante emite Solicitud ST
            res_sol = save_solicitud({
                "id": sol_id,
                "tipo": "Maquinaria / Equipo",
                "urgencia": "Alta",
                "area": "Empaque",
                "ubicacion": "Selladora",
                "descripcion": "Falla en mordaza termica",
                "solicitante": "Roberto Gomez (Solicitante)",
                "status": "Aprobada"
            })
            self.assertTrue(res_sol.get("success"))

            # Verificar que Jefe de Mantenimiento (Gerente) recibio notificacion
            notifs_gerente = get_notificaciones(rol="Gerente")
            self.assertTrue(any(n["enlaceId"] == sol_id and "Solicitud" in n["titulo"] for n in notifs_gerente))

            # 2. Jefe de Mantenimiento actualiza estatus de la Solicitud
            save_solicitud({
                "id": sol_id,
                "area": "Empaque",
                "ubicacion": "Selladora",
                "descripcion": "Falla en mordaza termica",
                "solicitante": "Roberto Gomez (Solicitante)",
                "status": "En espera de materiales"
            })

            # Verificar que Solicitante recibe notificacion de actualizacion
            notifs_sol = get_notificaciones(rol="Solicitante")
            self.assertTrue(any(n["enlaceId"] == sol_id and "En espera de materiales" in n["mensaje"] for n in notifs_sol))

            # 3. Jefe de Mantenimiento genera OT vinculada a la Solicitud
            res_ot = save_work_order({
                "id": ot_id,
                "tipo": "Correctivo",
                "prioridad": "Alta",
                "equipoId": "EQ-103",
                "descripcion": f"[Requerimiento {sol_id}] Reparar mordaza",
                "tecnicoIds": ["u2"],
                "status": "Pendiente",
                "solicitudId": sol_id
            })
            self.assertTrue(res_ot.get("success"))

            # Verificar en DB que la Solicitud paso a 'En proceso' y vinculo la OT
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT status, ot_vinculada FROM solicitudes_mantenimiento WHERE id = ?;", (sol_id,))
                row = cursor.fetchone()
                self.assertEqual(row["status"], "En proceso")
                self.assertEqual(row["ot_vinculada"], ot_id)

            # Verificar que Solicitante recibio notificacion con el numero de OT
            notifs_sol = get_notificaciones(rol="Solicitante")
            self.assertTrue(any(ot_id in n["mensaje"] and n["enlaceId"] == sol_id for n in notifs_sol))

            # 4. Mantenimiento concluye la OT
            save_work_order({
                "id": ot_id,
                "tipo": "Correctivo",
                "prioridad": "Alta",
                "equipoId": "EQ-103",
                "descripcion": f"[Requerimiento {sol_id}] Reparar mordaza",
                "status": "Concluida",
                "actividades": "Resistencia reemplazada exitosamente",
                "tiempoIntervencion": 1.5,
                "tiempoParada": 1.5
            })

            # Verificar transicion automatica a 'Culminada' en la Solicitud
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT status FROM solicitudes_mantenimiento WHERE id = ?;", (sol_id,))
                self.assertEqual(cursor.fetchone()["status"], "Culminada")

            # Verificar notificacion de culminacion para el Solicitante
            notifs_sol = get_notificaciones(rol="Solicitante")
            self.assertTrue(any("Culminada" in n["titulo"] for n in notifs_sol))

        finally:
            delete_work_order(ot_id)
            delete_solicitud(sol_id)

    def test_flow_jefe_ssl_jefe_mantenimiento(self):
        """Flujo bidireccional estricto Jefe SSL <-> Jefe Mantenimiento."""
        ssl_id = "SSL-TEST-FLOW-01"
        ot_id = "OT-TEST-FLOW-SSL-01"

        try:
            # 1. Jefe SSL reporta Condicion Insegura (nivelRiesgo valido: 'Crítico')
            res_ssl = save_ssl_request({
                "id": ssl_id,
                "codigo": "COND-FLOW-01",
                "fechaHora": "2026-11-06 15:00",
                "area": "Planta Norte",
                "ubicacion": "Pasillo 4",
                "nivelRiesgo": "Crítico",
                "descripcion": "Falta de conexion a tierra en motor",
                "accionPropuesta": "Instalar jabalina y cable de puesta a tierra",
                "solicitanteId": "u5",
                "solicitanteNombre": "Ing. Argenis Morillo (Jefe SSL)",
                "fotoEvidencia": "data:image/svg+xml;utf8,<svg></svg>",
                "status": "Pendiente"
            })
            self.assertTrue(res_ssl.get("success"))

            # Verificar notificacion urgente al Jefe de Mantenimiento (Gerente)
            notifs_gerente = get_notificaciones(rol="Gerente")
            self.assertTrue(any(n["enlaceId"] == ssl_id and "SSL" in n["titulo"] for n in notifs_gerente))

            # 2. Jefe de Mantenimiento genera OT de Mitigacion
            res_ot = save_work_order({
                "id": ot_id,
                "tipo": "Correctivo",
                "prioridad": "Alta",
                "equipoId": "EQ-104",
                "descripcion": f"[SSL COND-FLOW-01] Mitigacion puesta a tierra",
                "tecnicoIds": ["u3"],
                "status": "Pendiente",
                "sslReportId": ssl_id
            })
            self.assertTrue(res_ot.get("success"))

            # Verificar transicion automatica a 'En Correccion' y vinculo de OT
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT status, ot_vinculada FROM solicitudes_ssl WHERE id = ?;", (ssl_id,))
                row = cursor.fetchone()
                self.assertEqual(row["status"], "En Corrección")
                self.assertEqual(row["ot_vinculada"], ot_id)

            # Verificar que Jefe SSL recibe notificacion con la OT generada
            notifs_ssl = get_notificaciones(rol="Jefe SSL")
            self.assertTrue(any(ot_id in n["mensaje"] and n["enlaceId"] == ssl_id for n in notifs_ssl))

            # 3. Mantenimiento concluye la OT
            save_work_order({
                "id": ot_id,
                "tipo": "Correctivo",
                "prioridad": "Alta",
                "equipoId": "EQ-104",
                "descripcion": f"[SSL COND-FLOW-01] Mitigacion puesta a tierra",
                "status": "Concluida",
                "actividades": "Conexion a tierra instalada y probada bajo norma",
                "tiempoIntervencion": 2.0
            })

            # Verificar transicion automatica a 'Corregida' con fecha de correccion
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT status, fecha_correccion FROM solicitudes_ssl WHERE id = ?;", (ssl_id,))
                row = cursor.fetchone()
                self.assertEqual(row["status"], "Corregida")
                self.assertIsNotNone(row["fecha_correccion"])

            # Verificar notificacion de exito para el Jefe SSL
            notifs_ssl = get_notificaciones(rol="Jefe SSL")
            self.assertTrue(any("Corregida" in n["titulo"] or "Mitigada" in n["titulo"] for n in notifs_ssl))

        finally:
            delete_work_order(ot_id)
            delete_ssl_request(ssl_id)

if __name__ == "__main__":
    unittest.main()

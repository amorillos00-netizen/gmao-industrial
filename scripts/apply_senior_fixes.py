# -*- coding: utf-8 -*-
"""
Script de aplicación de correcciones senior para los 3 problemas específicos:
1. Error al eliminar OTs (desvinculación de FK en BD y corrección del filtro de rol de técnicos).
2. Funcionalidad y permisos de eliminación para Condiciones Inseguras (SSL) y Solicitudes Interdepartamentales.
3. Carga y persistencia del selector 'Técnico de apoyo / Acompañante' en el formulario de reporte de cierre.
"""
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent

def patch_main_py():
    path = BASE_DIR / "app" / "main.py"
    content = path.read_text(encoding="utf-8")

    # 1. Endpoint /api/technicians
    if "/api/technicians" not in content:
        target = 'def get_users():'
        replacement = '''def get_technicians():
    """Lista los técnicos disponibles para asignación y apoyo en órdenes de trabajo."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.nombre_completo as name, r.nombre as role, 
                   u.departamento, u.cargo
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE r.nombre = 'Tecnico' OR u.cargo LIKE '%Tecnico%' OR u.cargo LIKE '%Técnico%'
            ORDER BY u.nombre_completo;
        """)
        return [dict(r) for r in cursor.fetchall()]

@app.get("/api/users")
def get_users():'''
        assert target in content, "target 'def get_users():' not found in app/main.py"
        content = content.replace(target, replacement, 1)
        print("[OK] app/main.py: /api/technicians added")

    # 2. Desvinculación atómica en delete_work_order
    if "UPDATE salidas_materiales SET ot_id = NULL" not in content:
        target_ot_del = '''@app.delete("/api/work-orders/{ot_id}")
def delete_work_order(ot_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ordenes_trabajo WHERE id = ?;", (ot_id,))
        conn.commit()
    return {"success": True}'''

        replacement_ot_del = '''@app.delete("/api/work-orders/{ot_id}")
def delete_work_order(ot_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE salidas_materiales SET ot_id = NULL WHERE ot_id = ?;", (ot_id,))
        cursor.execute("UPDATE solicitudes_mantenimiento SET ot_vinculada = NULL WHERE ot_vinculada = ?;", (ot_id,))
        cursor.execute("UPDATE solicitudes_ssl SET ot_vinculada = NULL WHERE ot_vinculada = ?;", (ot_id,))
        cursor.execute("DELETE FROM notificaciones WHERE (enlace_tipo = 'ot' AND enlace_id = ?) OR mensaje LIKE ?;", (ot_id, f"%{ot_id}%"))
        cursor.execute("DELETE FROM ordenes_trabajo WHERE id = ?;", (ot_id,))
        conn.commit()
    notify_clients()
    return {"success": True, "id": ot_id}'''

        assert target_ot_del in content, "target_ot_del not found in app/main.py"
        content = content.replace(target_ot_del, replacement_ot_del, 1)
        print("[OK] app/main.py: delete_work_order patched")

    # 3. Endpoints delete_solicitud y delete_ssl_request
    if "/api/solicitudes/{sol_id}" not in content:
        target_save_sol = 'return {"success": True, "id": sol_id}'
        replacement_save_sol = '''return {"success": True, "id": sol_id}

@app.delete("/api/solicitudes/{sol_id}")
def delete_solicitud(sol_id: str):
    """Elimina una solicitud interdepartamental y desvincula registros asociados."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE salidas_materiales SET solicitud_id = NULL WHERE solicitud_id = ?;", (sol_id,))
        cursor.execute("DELETE FROM notificaciones WHERE (enlace_tipo = 'solicitud' AND enlace_id = ?) OR mensaje LIKE ?;", (sol_id, f"%{sol_id}%"))
        cursor.execute("DELETE FROM solicitudes_mantenimiento WHERE id = ?;", (sol_id,))
        conn.commit()
    notify_clients()
    return {"success": True, "id": sol_id}'''
        assert target_save_sol in content, "target_save_sol not found in app/main.py"
        content = content.replace(target_save_sol, replacement_save_sol, 1)
        print("[OK] app/main.py: delete_solicitud added")

    if "/api/ssl/{ssl_id}" not in content:
        target_save_ssl = 'return {"success": True, "id": ssl_id}'
        replacement_save_ssl = '''return {"success": True, "id": ssl_id}

@app.delete("/api/ssl/{ssl_id}")
def delete_ssl_request(ssl_id: str):
    """Elimina una condición insegura SSL y sus notificaciones asociadas."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notificaciones WHERE (enlace_tipo = 'ssl' AND enlace_id = ?) OR mensaje LIKE ?;", (ssl_id, f"%{ssl_id}%"))
        cursor.execute("DELETE FROM solicitudes_ssl WHERE id = ?;", (ssl_id,))
        conn.commit()
    notify_clients()
    return {"success": True, "id": ssl_id}'''
        assert target_save_ssl in content, "target_save_ssl not found in app/main.py"
        content = content.replace(target_save_ssl, replacement_save_ssl, 1)
        print("[OK] app/main.py: delete_ssl_request added")

    path.write_text(content, encoding="utf-8")
    print("[DONE] app/main.py updated successfully.")

def patch_database_py():
    path = BASE_DIR / "app" / "database.py"
    content = path.read_text(encoding="utf-8")

    old_fk = "FOREIGN KEY (ot_id) REFERENCES ordenes_trabajo(id)"
    new_fk = "FOREIGN KEY (ot_id) REFERENCES ordenes_trabajo(id) ON DELETE SET NULL"
    if old_fk in content:
        content = content.replace(old_fk, new_fk, 1)
        path.write_text(content, encoding="utf-8")
        print("[OK] app/database.py: salidas_materiales FK updated with ON DELETE SET NULL")
    else:
        print("[INFO] app/database.py: already has ON DELETE SET NULL")

def patch_html_file(file_path):
    content = file_path.read_text(encoding="utf-8")

    # 1. Filtro en renderMisOTsView
    old_mis_ots = "const misOTs = db.ots.filter(o => (o.tecnicoIds && o.tecnicoIds.includes(currentUser.id)) || currentUser.role === 'Tecnico');"
    new_mis_ots = "const misOTs = db.ots.filter(o => (o.tecnicoIds && o.tecnicoIds.includes(currentUser.id)) || o.tecnicoAcompanante === currentUser.id);"
    if old_mis_ots in content:
        content = content.replace(old_mis_ots, new_mis_ots, 1)
        print(f"[OK] {file_path.name}: renderMisOTsView filter fixed")

    # 2. Desvinculación en eliminarOT
    old_eliminar_ot = """        function eliminarOT(otId) {
            if (!confirm(`¿Eliminar la orden ${otId}?`)) return;
            db.ots = db.ots.filter(o => o.id !== otId);
            saveDatabase();"""
    new_eliminar_ot = """        function eliminarOT(otId) {
            if (!confirm(`¿Eliminar la orden ${otId}?`)) return;
            db.ots = db.ots.filter(o => o.id !== otId);
            db.solicitudesInterdepartamentales.forEach(s => { if (s.otVinculada === otId) s.otVinculada = null; });
            db.solicitudesSSL.forEach(s => { if (s.otVinculada === otId) s.otVinculada = null; });
            db.notificaciones = db.notificaciones.filter(n => !(n.enlaceTipo === 'ot' && n.enlaceId === otId));
            saveDatabase();"""
    if old_eliminar_ot in content:
        content = content.replace(old_eliminar_ot, new_eliminar_ot, 1)
        print(f"[OK] {file_path.name}: eliminarOT cleaned up")

    # 3. Botón de eliminación en renderSSLView (para Jefe de Mantenimiento / Gerente y Jefe SSL)
    old_ssl_actions = """                            ${currentUser.role === 'Jefe SSL' ? `
                                <button onclick="openModalSSL('${s.id}')" class="text-blue-600 hover:text-blue-800 p-1" title="Ver / Editar"><i class="fas fa-edit"></i></button>
                            ` : ''}
                        </td>"""
    new_ssl_actions = """                            ${currentUser.role === 'Jefe SSL' ? `
                                <button onclick="openModalSSL('${s.id}')" class="text-blue-600 hover:text-blue-800 p-1" title="Ver / Editar"><i class="fas fa-edit"></i></button>
                            ` : ''}
                            ${(currentUser.role === 'Gerente' || currentUser.role === 'Jefe SSL') ? `
                                <button onclick="eliminarSSL('${s.id}')" class="text-red-500 hover:text-red-700 p-1" title="Eliminar Condición Insegura"><i class="fas fa-trash"></i></button>
                            ` : ''}
                        </td>"""
    if old_ssl_actions in content:
        content = content.replace(old_ssl_actions, new_ssl_actions, 1)
        print(f"[OK] {file_path.name}: delete button added to renderSSLView")

    # 4. Botón de eliminación en renderSolicitudesGerenteView (para Jefe de Mantenimiento / Gerente)
    old_sol_gerente = """                                <button onclick="generarOTDesdeSolicitud('${s.id}')" class="bg-indigo-600 hover:bg-indigo-700 text-white px-2 py-1 rounded text-[11px] font-semibold shadow">
                                    <i class="fas fa-clipboard-check mr-1"></i> Generar OT
                                </button>
                            ` : (s.otVinculada ? `<span class="text-[10px] font-mono text-blue-600 font-bold">${s.otVinculada}</span>` : '')}
                        </td>"""
    new_sol_gerente = """                                <button onclick="generarOTDesdeSolicitud('${s.id}')" class="bg-indigo-600 hover:bg-indigo-700 text-white px-2 py-1 rounded text-[11px] font-semibold shadow">
                                    <i class="fas fa-clipboard-check mr-1"></i> Generar OT
                                </button>
                            ` : (s.otVinculada ? `<span class="text-[10px] font-mono text-blue-600 font-bold">${s.otVinculada}</span>` : '')}
                            ${currentUser.role === 'Gerente' ? `
                                <button onclick="eliminarSolicitud('${s.id}')" class="text-red-500 hover:text-red-700 p-1" title="Eliminar Solicitud"><i class="fas fa-trash"></i></button>
                            ` : ''}
                        </td>"""
    if old_sol_gerente in content:
        content = content.replace(old_sol_gerente, new_sol_gerente, 1)
        print(f"[OK] {file_path.name}: delete button added to renderSolicitudesGerenteView")

    # 5. Botón de eliminación y columna de acciones en renderMisSolicitudesView (para Solicitante)
    old_mis_sol_th = """                                    <th class="p-2.5">Solicitante</th>
                                    <th class="p-2.5 text-center">Estatus del Flujo</th>
                                    <th class="p-2.5 text-right">OT Vinculada</th>
                                </tr>"""
    new_mis_sol_th = """                                    <th class="p-2.5">Solicitante</th>
                                    <th class="p-2.5 text-center">Estatus del Flujo</th>
                                    <th class="p-2.5 text-center">OT Vinculada</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>"""
    if old_mis_sol_th in content:
        content = content.replace(old_mis_sol_th, new_mis_sol_th, 1)

    old_mis_sol_row = """                        <td class="p-2.5 text-center">
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${badgeStatus}">${s.status}</span>
                        </td>
                        <td class="p-2.5 text-right font-mono text-xs font-bold text-blue-600">${s.otVinculada || 'En Gestión'}</td>
                    </tr>"""
    new_mis_sol_row = """                        <td class="p-2.5 text-center">
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${badgeStatus}">${s.status}</span>
                        </td>
                        <td class="p-2.5 text-center font-mono text-xs font-bold text-blue-600">${s.otVinculada || 'En Gestión'}</td>
                        <td class="p-2.5 text-right space-x-1 whitespace-nowrap">
                            ${(currentUser.role === 'Solicitante' || currentUser.role === 'Gerente') ? `
                                <button onclick="eliminarSolicitud('${s.id}')" class="text-red-500 hover:text-red-700 p-1" title="Eliminar Solicitud"><i class="fas fa-trash"></i></button>
                            ` : ''}
                        </td>
                    </tr>"""
    if old_mis_sol_row in content:
        content = content.replace(old_mis_sol_row, new_mis_sol_row, 1)
        print(f"[OK] {file_path.name}: delete button added to renderMisSolicitudesView")

    # 6. Funciones eliminarSSL y eliminarSolicitud
    if "function eliminarSSL(" not in content:
        target_fn_loc = "function cambiarStatusSolicitud("
        new_fns = """        function eliminarSSL(sslId) {
            if (currentUser.role !== 'Gerente' && currentUser.role !== 'Jefe SSL') {
                mostrarToast('No Autorizado', 'Solo el Jefe de Mantenimiento o el Jefe SSL pueden eliminar condiciones inseguras.', 'error');
                return;
            }
            if (!confirm(`¿Está seguro de eliminar la condición insegura ${sslId}?`)) return;
            db.solicitudesSSL = db.solicitudesSSL.filter(s => s.id !== sslId);
            db.notificaciones = db.notificaciones.filter(n => !(n.enlaceTipo === 'ssl' && n.enlaceId === sslId));
            saveDatabase();
            if (navigator.onLine) {
                fetch(`/api/ssl/${sslId}`, { method: 'DELETE' }).catch(e => console.warn(e));
            }
            actualizarBadges();
            renderSidebar();
            renderSSLView(document.getElementById('mainView'));
            mostrarToast('Condición Eliminada', `La condición insegura ${sslId} ha sido eliminada exitosamente.`, 'info');
        }

        function eliminarSolicitud(solId) {
            if (currentUser.role !== 'Gerente' && currentUser.role !== 'Solicitante') {
                mostrarToast('No Autorizado', 'Solo el Jefe de Mantenimiento o el Solicitante pueden eliminar solicitudes.', 'error');
                return;
            }
            if (!confirm(`¿Está seguro de eliminar la solicitud ${solId}?`)) return;
            db.solicitudesInterdepartamentales = db.solicitudesInterdepartamentales.filter(s => s.id !== solId);
            db.notificaciones = db.notificaciones.filter(n => !(n.enlaceTipo === 'solicitud' && n.enlaceId === solId));
            saveDatabase();
            if (navigator.onLine) {
                fetch(`/api/solicitudes/${solId}`, { method: 'DELETE' }).catch(e => console.warn(e));
            }
            actualizarBadges();
            renderSidebar();
            if (currentUser.role === 'Solicitante') {
                renderMisSolicitudesView(document.getElementById('mainView'));
            } else {
                renderSolicitudesGerenteView(document.getElementById('mainView'));
            }
            mostrarToast('Solicitud Eliminada', `La solicitud ${solId} ha sido eliminada exitosamente.`, 'info');
        }

        function cambiarStatusSolicitud("""
        assert target_fn_loc in content, f"target_fn_loc not found in {file_path}"
        content = content.replace(target_fn_loc, new_fns, 1)
        print(f"[OK] {file_path.name}: eliminarSSL and eliminarSolicitud added")

    # 7. Carga del selector de Técnico de Apoyo / Acompañante en openModalCierreOT
    old_cierre_rep = """            // Select de almacén
            const selAlm = document.getElementById('selectRepuestoAlmacen');"""
    new_cierre_rep = """            // Cargar selector de Técnico de Apoyo / Acompañante
            const selAcomp = document.getElementById('cierreTecnicoAcompanante');
            if (selAcomp) {
                const tecnicosDisponibles = (db.users || []).filter(u => u.role === 'Tecnico' || (u.cargo && u.cargo.toLowerCase().includes('técnico')));
                selAcomp.innerHTML = '<option value="">-- Ninguno (Sin acompañante) --</option>' + 
                    tecnicosDisponibles.map(t => `<option value="${t.id}">${t.name} (${t.cargo || 'Técnico'})</option>`).join('');
                selAcomp.value = ot.tecnicoAcompanante || '';
            }

            // Select de almacén
            const selAlm = document.getElementById('selectRepuestoAlmacen');"""
    if old_cierre_rep in content:
        content = content.replace(old_cierre_rep, new_cierre_rep, 1)
        print(f"[OK] {file_path.name}: openModalCierreOT populates cierreTecnicoAcompanante")

    # 8. Guardado de técnico de apoyo en submit de formCierreOT
    old_cierre_submit = """            ot.status = document.getElementById('cierreEstadoFinal').value;
            ot.repuestosUsados = otRepuestosCierre;"""
    new_cierre_submit = """            ot.status = document.getElementById('cierreEstadoFinal').value;
            ot.tecnicoAcompanante = (document.getElementById('cierreTecnicoAcompanante') ? document.getElementById('cierreTecnicoAcompanante').value : '') || '';
            ot.repuestosUsados = otRepuestosCierre;"""
    if old_cierre_submit in content:
        content = content.replace(old_cierre_submit, new_cierre_submit, 1)
        print(f"[OK] {file_path.name}: formCierreOT persists cierreTecnicoAcompanante")

    file_path.write_text(content, encoding="utf-8")
    print(f"[DONE] {file_path.name} patched successfully.")

if __name__ == "__main__":
    patch_main_py()
    patch_database_py()
    patch_html_file(BASE_DIR / "index.html")
    # Copy to static
    shutil.copyfile(BASE_DIR / "index.html", BASE_DIR / "app" / "static" / "index.html")
    print("[DONE] Copied index.html to app/static/index.html")

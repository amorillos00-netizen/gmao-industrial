# -*- coding: utf-8 -*-
"""
Script de actualización Fase 3 para Frontend SPA GMAO Industrial Pro
Empresa: SALTYSNACK TUYERO C.A.
Implementa:
- Vistas completas para Seguimiento en Taller Externo y Salida de Materiales (Almacenista)
- Protección estricta en openModalEquipo y formEquipo
- Flujo de cambio automático de estatus e integración de actualizarBadges()
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_INDEX = BASE_DIR / "app" / "static" / "index.html"
ROOT_INDEX = BASE_DIR / "index.html"

with open(STATIC_INDEX, "r", encoding="utf-8") as f:
    text = f.read()

# -----------------------------------------------------------------------------
# 1. PROTEGER OPENMODALEQUIPO Y FORMEQUIPO
# -----------------------------------------------------------------------------
target_open_eq = """        function openModalEquipo(eqId = false) {
            document.getElementById('formEquipo').reset();"""

replacement_open_eq = """        function openModalEquipo(eqId = false) {
            if (!puedeModificarEquipos(currentUser)) {
                mostrarToast('Acceso Restringido', 'La creación o edición de equipos queda reservada únicamente para Gerente de Planta y Jefe de Mantenimiento.', 'warning');
                return;
            }
            document.getElementById('formEquipo').reset();"""

if target_open_eq in text:
    text = text.replace(target_open_eq, replacement_open_eq)
    print("[OK] Protección en openModalEquipo() agregada.")

target_form_eq = """        document.getElementById('formEquipo').addEventListener('submit', function(e) {
            e.preventDefault();"""

replacement_form_eq = """        document.getElementById('formEquipo').addEventListener('submit', function(e) {
            e.preventDefault();
            if (!puedeModificarEquipos(currentUser)) {
                mostrarToast('Acceso Restringido', 'La modificación de equipos y activos está reservada para Gerente de Planta y Jefe de Mantenimiento.', 'warning');
                return;
            }"""

if target_form_eq in text:
    text = text.replace(target_form_eq, replacement_form_eq)
    print("[OK] Protección en formEquipo submit agregada.")

# -----------------------------------------------------------------------------
# 2. ACTUALIZAR CAMBIARSTATUSSOLICITUD Y CAMBIARSTATUSSSL CON BADGES Y REACTIVIDAD
# -----------------------------------------------------------------------------
target_cambiar_sol = """        function cambiarStatusSolicitud(solId, nuevoStatus) {
            const s = db.solicitudesInterdepartamentales.find(x => x.id === solId);
            if (!s) return;
            s.status = nuevoStatus;
            saveDatabase();
            mostrarToast('Estatus Actualizado', `La solicitud ${solId} ahora está en: ${nuevoStatus}`, 'info');
            renderSolicitudesGerenteView(document.getElementById('mainView'));
        }"""

replacement_cambiar_sol = """        function cambiarStatusSolicitud(solId, nuevoStatus) {
            const s = db.solicitudesInterdepartamentales.find(x => x.id === solId);
            if (!s) return;
            s.status = nuevoStatus;
            saveDatabase();
            actualizarBadges();
            renderSidebar();
            mostrarToast('Estatus Actualizado', `La solicitud ${solId} ahora está en: ${nuevoStatus}`, 'info');
            renderSolicitudesGerenteView(document.getElementById('mainView'));
        }"""

if target_cambiar_sol in text:
    text = text.replace(target_cambiar_sol, replacement_cambiar_sol)
    print("[OK] cambiarStatusSolicitud() actualizado con actualización de badges y sidebar.")

target_cambiar_ssl = """        function cambiarStatusSSL(sslId, nuevoStatus) {
            const s = db.solicitudesSSL.find(x => x.id === sslId);
            if (!s) return;
            s.status = nuevoStatus;
            saveDatabase();
            // Notificar al Jefe SSL
            dispararNotificacion('Jefe SSL', s.solicitanteId, 'Condición Insegura Actualizada', `La condición ${s.codigo} ha sido marcada como ${nuevoStatus}`, 'success', 'ssl', s.id);
            renderSSLView(document.getElementById('mainView'));
        }"""

replacement_cambiar_ssl = """        function cambiarStatusSSL(sslId, nuevoStatus) {
            const s = db.solicitudesSSL.find(x => x.id === sslId);
            if (!s) return;
            s.status = nuevoStatus;
            if (nuevoStatus === 'Corregida') {
                s.fechaCorreccion = new Date().toISOString().replace('T', ' ').slice(0, 16);
            }
            saveDatabase();
            actualizarBadges();
            renderSidebar();
            // Notificar al Jefe SSL
            dispararNotificacion('Jefe SSL', s.solicitanteId, 'Condición Insegura Actualizada', `La condición ${s.codigo} ha sido marcada como ${nuevoStatus}`, 'success', 'ssl', s.id);
            renderSSLView(document.getElementById('mainView'));
        }"""

if target_cambiar_ssl in text:
    text = text.replace(target_cambiar_ssl, replacement_cambiar_ssl)
    print("[OK] cambiarStatusSSL() actualizado con actualización de badges y sidebar.")

# -----------------------------------------------------------------------------
# 3. ACTUALIZAR FORMOT Y FORMCIERREOT CON CAMBIO AUTOMÁTICO DE ESTATUS
# -----------------------------------------------------------------------------
target_form_ot = """                // Si proviene de solicitud interdepartamental, vincularla
                if (solId) {
                    const sol = db.solicitudesInterdepartamentales.find(s => s.id === solId);
                    if (sol) { sol.otVinculada = payload.id; sol.status = 'En proceso'; }
                }"""

replacement_form_ot = """                // Si proviene de solicitud interdepartamental, vincularla y cambiar automáticamente a 'En proceso'
                if (solId) {
                    const sol = db.solicitudesInterdepartamentales.find(s => s.id === solId);
                    if (sol) { 
                        sol.otVinculada = payload.id; 
                        sol.status = 'En proceso'; 
                        dispararNotificacion('Solicitante', null, 'Solicitud En Proceso', `La solicitud ${sol.id} ha pasado a En Proceso vinculada a la ${payload.id}.`, 'info', 'solicitud', sol.id);
                    }
                }"""

if target_form_ot in text:
    text = text.replace(target_form_ot, replacement_form_ot)
    print("[OK] formOT submit actualizado con notificación y cambio automático a 'En proceso'.")

target_form_ot_save = """            // Persistencia local inmediata en base de datos offline
            saveDatabase();"""

replacement_form_ot_save = """            // Persistencia local inmediata en base de datos offline
            saveDatabase();
            actualizarBadges();
            renderSidebar();"""

if target_form_ot_save in text:
    text = text.replace(target_form_ot_save, replacement_form_ot_save, 1)
    print("[OK] formOT submit refresca badges reactivamente.")

target_cierre_ot = """                // Notificar al Jefe de Mantenimiento sobre cierre
                dispararNotificacion('Gerente', null, 'OT Concluida', `La orden ${ot.id} fue cerrada por ${currentUser.name}. Downtime: ${ot.tiempoParada}h`, 'success', 'ot', ot.id);
            }

            saveDatabase();
            closeModal('modalCierreOT');"""

replacement_cierre_ot = """                // CAMBIO AUTOMÁTICO DE ESTATUS EN SOLICITUDES VINCULADAS (REQUERIMIENTO 6)
                db.solicitudesInterdepartamentales.forEach(s => {
                    if (s.otVinculada === ot.id && s.status !== 'Culminada') {
                        s.status = 'Culminada';
                        dispararNotificacion('Solicitante', null, 'Solicitud Culminada', `La solicitud ${s.id} vinculada a la OT ${ot.id} ha sido culminada exitosamente.`, 'success', 'solicitud', s.id);
                    }
                });

                // CAMBIO AUTOMÁTICO DE ESTATUS EN CONDICIONES SSL VINCULADAS (REQUERIMIENTO 6)
                db.solicitudesSSL.forEach(ssl => {
                    if (ssl.otVinculada === ot.id && ssl.status !== 'Corregida') {
                        ssl.status = 'Corregida';
                        ssl.fechaCorreccion = new Date().toISOString().replace('T', ' ').slice(0, 16);
                        dispararNotificacion('Jefe SSL', ssl.solicitanteId, 'Condición SSL Corregida', `La condición ${ssl.codigo} vinculada a la OT ${ot.id} ha sido mitigada y corregida.`, 'success', 'ssl', ssl.id);
                    }
                });

                // Notificar al Jefe de Mantenimiento sobre cierre
                dispararNotificacion('Gerente', null, 'OT Concluida', `La orden ${ot.id} fue cerrada por ${currentUser.name}. Downtime: ${ot.tiempoParada}h`, 'success', 'ot', ot.id);
            }

            saveDatabase();
            actualizarBadges();
            renderSidebar();
            closeModal('modalCierreOT');"""

if target_cierre_ot in text:
    text = text.replace(target_cierre_ot, replacement_cierre_ot)
    print("[OK] formCierreOT submit actualizado con cierre automático de solicitudes vinculadas y badges.")

# -----------------------------------------------------------------------------
# 4. BOTÓN DESPACHAR / SALIDA DE MATERIALES EN RENDERALMACENVIEW
# -----------------------------------------------------------------------------
target_almacen_hdr = """                    <div class="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                        <div>
                            <h2 class="text-base font-bold text-slate-800">Almacén de Repuestos e Insumos Industriales</h2>
                            <p class="text-xs text-slate-500">Control de Existencias y Descuento Automático por OT</p>
                        </div>
                        <button onclick="openModalRepuesto(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow">
                            <i class="fas fa-plus mr-1"></i> + Registrar Repuesto
                        </button>
                    </div>"""

replacement_almacen_hdr = """                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm gap-3">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-yellow-50 text-yellow-600 flex items-center justify-center text-xl shadow-sm">
                                <i class="fas fa-boxes"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-bold text-slate-800">Almacén de Repuestos e Insumos Industriales</h2>
                                <p class="text-xs text-slate-500">Control de Existencias y Descuento Automático por OT / Solicitud</p>
                            </div>
                        </div>
                        <div class="flex flex-wrap items-center gap-2">
                            <button onclick="openModalSalidaMaterial()" class="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-dolly-flatbed"></i>
                                <span>+ Salida de Materiales</span>
                            </button>
                            <button onclick="navigate('salidas-materiales')" class="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-lg text-xs font-semibold border flex items-center space-x-1.5 transition">
                                <i class="fas fa-list-alt text-slate-500"></i>
                                <span>Ver Historial de Salidas</span>
                            </button>
                            <button onclick="openModalRepuesto(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1">
                                <i class="fas fa-plus mr-1"></i> + Registrar Repuesto
                            </button>
                        </div>
                    </div>"""

if target_almacen_hdr in text:
    text = text.replace(target_almacen_hdr, replacement_almacen_hdr)
    print("[OK] Cabecera de Almacén enriquecida con Salida de Materiales.")

# -----------------------------------------------------------------------------
# 5. IMPLEMENTACIÓN COMPLETA DE VISTAS Y CONTROLADORES DE TALLER EXTERNO Y SALIDAS
# -----------------------------------------------------------------------------
new_views_code = """
        // =============================================================================
        // --- 18. MÓDULO DE SEGUIMIENTO DE EQUIPOS EN TALLER EXTERNO (REQUERIMIENTO 2) ---
        // =============================================================================
        function renderTallerExternoView(container) {
            const records = db.equiposTallerExterno || [];
            const enTaller = records.filter(r => r.status !== 'Recibido en Planta');
            const recibidos = records.filter(r => r.status === 'Recibido en Planta');
            const listosRetiro = records.filter(r => r.status === 'Listo para retiro');
            const costoTotal = records.reduce((acc, r) => acc + (parseFloat(r.costoFinal) || parseFloat(r.costoEstimado) || 0), 0);

            const rowsHtml = records.map(r => {
                let badgeStatus = 'bg-blue-100 text-blue-800';
                if (r.status === 'En diagnóstico') badgeStatus = 'bg-amber-100 text-amber-800';
                if (r.status === 'Esperando repuestos') badgeStatus = 'bg-purple-100 text-purple-800';
                if (r.status === 'Listo para retiro') badgeStatus = 'bg-cyan-100 text-cyan-800';
                if (r.status === 'Recibido en Planta') badgeStatus = 'bg-emerald-100 text-emerald-800';

                const eq = (db.equipos || []).find(e => e.id === r.equipoId) || { name: r.equipoId };
                const estaRecibido = r.status === 'Recibido en Planta';

                return `
                    <tr class="hover:bg-slate-50 transition border-b border-slate-100">
                        <td class="p-2.5 font-mono font-bold text-blue-700 text-xs">${r.id}</td>
                        <td class="p-2.5 text-xs font-semibold text-slate-800">
                            ${eq.name}
                            <span class="block text-[10px] font-mono text-slate-400 font-bold">${r.equipoId}</span>
                        </td>
                        <td class="p-2.5 text-xs text-slate-700 font-medium">${r.proveedorNombre}</td>
                        <td class="p-2.5 text-xs text-slate-600 font-mono whitespace-nowrap">
                            <span>Salida: ${r.fechaSalida}</span>
                            <span class="block text-[10px] text-slate-400">Est. Retorno: ${r.fechaEstimadaRetorno || '-'}</span>
                        </td>
                        <td class="p-2.5 text-xs text-slate-600 max-w-xs truncate" title="${r.motivoServicio}">${r.motivoServicio}</td>
                        <td class="p-2.5 text-xs font-mono font-bold text-right text-slate-800">$${(parseFloat(r.costoFinal) || parseFloat(r.costoEstimado) || 0).toFixed(2)}</td>
                        <td class="p-2.5 text-center">
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${badgeStatus}">${r.status}</span>
                            ${estaRecibido && r.fechaRetornoReal ? `<span class="block text-[9px] text-emerald-700 font-mono mt-0.5 font-semibold">Retornado: ${r.fechaRetornoReal}</span>` : ''}
                        </td>
                        <td class="p-2.5 text-right space-x-1 whitespace-nowrap">
                            ${!estaRecibido ? `
                                <button onclick="openModalRecepcionTaller('${r.id}')" class="bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-1 rounded text-[11px] font-semibold shadow" title="Registrar Recepción en Planta">
                                    <i class="fas fa-check mr-1"></i> Recibir en Planta
                                </button>
                                <button onclick="openModalTallerExterno('${r.id}')" class="text-blue-600 hover:text-blue-800 p-1" title="Editar"><i class="fas fa-edit"></i></button>
                            ` : `
                                <span class="text-[10px] font-bold text-emerald-600 mr-1"><i class="fas fa-check-circle mr-1"></i>En Planta</span>
                                <button onclick="openModalTallerExterno('${r.id}')" class="text-slate-400 hover:text-slate-600 p-1" title="Ver Detalle"><i class="fas fa-eye"></i></button>
                            `}
                        </td>
                    </tr>
                `;
            }).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-xl shadow-sm">
                                <i class="fas fa-truck-pickup"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-bold text-slate-800">Seguimiento de Equipos en Taller Externo</h2>
                                <p class="text-xs text-slate-500">Mantenimiento Mayor, Rectificaciones y Servicios Especializados Fuera de Planta</p>
                            </div>
                        </div>
                        <button onclick="openModalTallerExterno(false)" class="bg-amber-600 hover:bg-amber-700 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                            <i class="fas fa-plus"></i>
                            <span>+ Enviar Equipo a Taller</span>
                        </button>
                    </div>

                    <!-- TARJETAS DE SEGUIMIENTO -->
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                            <div class="text-[10px] uppercase font-bold text-slate-500">Actualmente en Taller</div>
                            <div class="text-xl font-black text-amber-600">${enTaller.length}</div>
                        </div>
                        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                            <div class="text-[10px] uppercase font-bold text-slate-500">Listos para Retiro</div>
                            <div class="text-xl font-black text-cyan-600">${listosRetiro.length}</div>
                        </div>
                        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                            <div class="text-[10px] uppercase font-bold text-slate-500">Recibidos en Planta</div>
                            <div class="text-xl font-black text-emerald-600">${recibidos.length}</div>
                        </div>
                        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                            <div class="text-[10px] uppercase font-bold text-slate-500">Costo Total Invertido</div>
                            <div class="text-xl font-black text-slate-800">$${costoTotal.toFixed(2)}</div>
                        </div>
                    </div>

                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">Folio</th>
                                    <th class="p-2.5">Equipo / Tag</th>
                                    <th class="p-2.5">Taller / Proveedor</th>
                                    <th class="p-2.5">Salida / Retorno Est.</th>
                                    <th class="p-2.5">Motivo del Servicio</th>
                                    <th class="p-2.5 text-right">Costo</th>
                                    <th class="p-2.5 text-center">Estatus</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                ${rowsHtml.length > 0 ? rowsHtml : `<tr><td colspan="8" class="p-6 text-center text-slate-400">No hay registros de equipos enviados a taller externo.</td></tr>`}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        function openModalTallerExterno(editId = false) {
            document.getElementById('formTallerExterno').reset();
            document.getElementById('tallerExternoId').value = editId || '';

            // Llenar select de equipos
            const eqSelect = document.getElementById('tallerEquipoId');
            eqSelect.innerHTML = (db.equipos || []).map(e => `<option value="${e.id}">${e.id} - ${e.name}</option>`).join('');

            // Llenar select de proveedores
            const prvSelect = document.getElementById('tallerProveedorSelect');
            prvSelect.innerHTML = '<option value="">-- Proveedor Registrado --</option>' + (db.proveedores || []).map(p => `<option value="${p.id}">${p.nombre} (${p.categoria})</option>`).join('');

            const hoy = new Date().toISOString().slice(0, 10);
            document.getElementById('tallerFechaSalida').value = hoy;

            if (editId) {
                const r = (db.equiposTallerExterno || []).find(x => x.id === editId);
                if (r) {
                    eqSelect.value = r.equipoId;
                    document.getElementById('tallerProveedorSelect').value = r.proveedorId || '';
                    document.getElementById('tallerProveedorNombre').value = r.proveedorNombre || '';
                    document.getElementById('tallerFechaSalida').value = r.fechaSalida || hoy;
                    document.getElementById('tallerFechaEstimada').value = r.fechaEstimadaRetorno || '';
                    document.getElementById('tallerMotivo').value = r.motivoServicio || '';
                    document.getElementById('tallerCostoEstimado').value = r.costoEstimado || 0;
                    document.getElementById('tallerStatus').value = r.status || 'En diagnóstico';
                    document.getElementById('tallerObservaciones').value = r.observaciones || '';
                }
            } else {
                const en15 = new Date(Date.now() + 15 * 86400000).toISOString().slice(0, 10);
                document.getElementById('tallerFechaEstimada').value = en15;
            }

            document.getElementById('modalTallerExterno').classList.remove('hidden');
        }

        function seleccionarProveedorTaller(prvId) {
            if (!prvId) return;
            const p = (db.proveedores || []).find(x => x.id === prvId);
            if (p) document.getElementById('tallerProveedorNombre').value = p.nombre;
        }

        document.getElementById('formTallerExterno').addEventListener('submit', function(e) {
            e.preventDefault();
            const editId = document.getElementById('tallerExternoId').value;
            const eqId = document.getElementById('tallerEquipoId').value;
            const statusVal = document.getElementById('tallerStatus').value;

            const payload = {
                id: editId || `EXT-2026-${String((db.equiposTallerExterno || []).length + 1).padStart(3, '0')}`,
                equipoId: eqId,
                proveedorId: document.getElementById('tallerProveedorSelect').value || null,
                proveedorNombre: document.getElementById('tallerProveedorNombre').value.trim(),
                fechaSalida: document.getElementById('tallerFechaSalida').value,
                fechaEstimadaRetorno: document.getElementById('tallerFechaEstimada').value,
                fechaRetornoReal: null,
                motivoServicio: document.getElementById('tallerMotivo').value.trim(),
                costoEstimado: parseFloat(document.getElementById('tallerCostoEstimado').value) || 0.0,
                costoFinal: 0.0,
                status: statusVal,
                condicionRecepcion: null,
                recibidoPor: null,
                observaciones: document.getElementById('tallerObservaciones').value.trim()
            };

            if (!db.equiposTallerExterno) db.equiposTallerExterno = [];
            if (editId) {
                const idx = db.equiposTallerExterno.findIndex(x => x.id === editId);
                if (idx !== -1) db.equiposTallerExterno[idx] = { ...db.equiposTallerExterno[idx], ...payload };
            } else {
                db.equiposTallerExterno.unshift(payload);
                // Si el equipo se envía a taller, poner su estado en 'En Mantenimiento'
                const eq = (db.equipos || []).find(e => e.id === eqId);
                if (eq && statusVal !== 'Recibido en Planta') {
                    eq.status = 'En Mantenimiento';
                }
                dispararNotificacion('Gerente', null, 'Equipo Enviado a Taller Externo', `El equipo ${eqId} fue despachado a ${payload.proveedorNombre}.`, 'info', 'taller-externo', payload.id);
            }

            saveDatabase();
            closeModal('modalTallerExterno');
            renderTallerExternoView(document.getElementById('mainView'));
            mostrarToast('Registro de Taller', `El servicio para el equipo ${eqId} ha sido registrado exitosamente.`, 'success');
        });

        function openModalRecepcionTaller(id) {
            const r = (db.equiposTallerExterno || []).find(x => x.id === id);
            if (!r) return;
            document.getElementById('formRecepcionTaller').reset();
            document.getElementById('recTallerId').value = r.id;

            const eq = (db.equipos || []).find(e => e.id === r.equipoId) || { name: r.equipoId };
            document.getElementById('recTallerEquipo').textContent = `Equipo: ${r.equipoId} - ${eq.name}`;
            document.getElementById('recTallerProveedor').textContent = `Taller / Proveedor: ${r.proveedorNombre} | Motivo: ${r.motivoServicio}`;
            document.getElementById('recFechaRetorno').value = new Date().toISOString().slice(0, 10);
            document.getElementById('recCostoFinal').value = r.costoEstimado || 0;
            document.getElementById('recRecibidoPor').value = currentUser ? currentUser.name : '';

            document.getElementById('modalRecepcionTaller').classList.remove('hidden');
        }

        document.getElementById('formRecepcionTaller').addEventListener('submit', function(e) {
            e.preventDefault();
            const id = document.getElementById('recTallerId').value;
            const r = (db.equiposTallerExterno || []).find(x => x.id === id);
            if (!r) return;

            r.status = 'Recibido en Planta';
            r.fechaRetornoReal = document.getElementById('recFechaRetorno').value;
            r.costoFinal = parseFloat(document.getElementById('recCostoFinal').value) || 0.0;
            r.condicionRecepcion = document.getElementById('recCondicion').value;
            r.recibidoPor = document.getElementById('recRecibidoPor').value.trim();
            const obs = document.getElementById('recObservaciones').value.trim();
            if (obs) {
                r.observaciones = (r.observaciones ? r.observaciones + ' | ' : '') + `Recepción (${r.condicionRecepcion}): ${obs}`;
            }

            // Reincorporar equipo a estatus Operativo
            const eq = (db.equipos || []).find(e => e.id === r.equipoId);
            if (eq) {
                eq.status = 'Operativo';
            }

            dispararNotificacion('Gerente', null, 'Equipo Recibido en Planta', `El equipo ${r.equipoId} retornó del taller externo en condición: ${r.condicionRecepcion}.`, 'success', 'taller-externo', r.id);

            saveDatabase();
            closeModal('modalRecepcionTaller');
            renderTallerExternoView(document.getElementById('mainView'));
            mostrarToast('Recepción Exitosa', `El equipo ${r.equipoId} ha sido recibido en planta y reincorporado operativamente.`, 'success');
        });

        // =============================================================================
        // --- 19. MÓDULO DE SALIDA DE MATERIALES Y REPUESTOS (ROL ALMACENISTA) ---
        // =============================================================================
        function renderSalidasMaterialesView(container) {
            const salidas = db.salidasMateriales || [];
            const rowsHtml = salidas.map(s => {
                return `
                    <tr class="hover:bg-slate-50 transition border-b border-slate-100">
                        <td class="p-2.5 font-mono font-bold text-blue-700 text-xs">${s.id}</td>
                        <td class="p-2.5 text-xs text-slate-500 font-mono">${s.fecha}</td>
                        <td class="p-2.5 text-xs font-semibold text-slate-800">
                            ${s.repuestoNombre}
                            <span class="block text-[10px] font-mono text-slate-400 font-bold">${s.repuestoId}</span>
                        </td>
                        <td class="p-2.5 text-center font-bold text-xs text-emerald-700">${s.cantidad} pza</td>
                        <td class="p-2.5 text-xs font-mono font-bold text-indigo-700">${s.otId || s.solicitudId || 'Uso General'}</td>
                        <td class="p-2.5 text-xs text-slate-700 font-medium">${s.despachadoPor}</td>
                        <td class="p-2.5 text-xs text-slate-800 font-semibold">${s.receptor}</td>
                        <td class="p-2.5 text-xs text-slate-500 max-w-xs truncate" title="${s.observaciones || ''}">${s.observaciones || '-'}</td>
                    </tr>
                `;
            }).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-yellow-50 text-yellow-600 flex items-center justify-center text-xl shadow-sm">
                                <i class="fas fa-dolly-flatbed"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-bold text-slate-800">Control de Salida y Despacho de Materiales</h2>
                                <p class="text-xs text-slate-500">Gestión de Almacén | Descuento Automático de Stock Vinculado a OTs</p>
                            </div>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button onclick="navigate('almacen')" class="bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-lg text-xs font-semibold border flex items-center space-x-1.5 transition">
                                <i class="fas fa-boxes text-slate-500"></i>
                                <span>Ver Catálogo de Stock</span>
                            </button>
                            <button onclick="openModalSalidaMaterial()" class="bg-yellow-600 hover:bg-yellow-700 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-plus"></i>
                                <span>+ Nueva Salida de Materiales</span>
                            </button>
                        </div>
                    </div>

                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">Folio</th>
                                    <th class="p-2.5">Fecha / Hora</th>
                                    <th class="p-2.5">Material / Repuesto</th>
                                    <th class="p-2.5 text-center">Cantidad</th>
                                    <th class="p-2.5">OT / Solicitud</th>
                                    <th class="p-2.5">Despachado Por</th>
                                    <th class="p-2.5">Receptor</th>
                                    <th class="p-2.5">Observaciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                ${rowsHtml.length > 0 ? rowsHtml : `<tr><td colspan="8" class="p-6 text-center text-slate-400">No se registran salidas de materiales aún.</td></tr>`}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        function openModalSalidaMaterial() {
            document.getElementById('formSalidaMaterial').reset();

            // Llenar select de repuestos
            const repSelect = document.getElementById('salidaRepuestoId');
            repSelect.innerHTML = (db.repuestos || []).map(r => `<option value="${r.id}">${r.codigo} - ${r.name} (Stock: ${r.stock} ${r.um})</option>`).join('');

            // Llenar select de OTs activas/aprobadas
            const otSelect = document.getElementById('salidaOtId');
            const otsActivas = (db.ots || []).filter(o => o.status !== 'Concluida' && o.status !== 'Completada');
            otSelect.innerHTML = '<option value="">-- Sin OT Vinculada --</option>' + otsActivas.map(o => `<option value="${o.id}">${o.id} [${o.tipo}] - ${o.equipoId}: ${o.descripcion.slice(0, 40)}</option>`).join('');

            // Llenar select de solicitudes
            const solSelect = document.getElementById('salidaSolicitudId');
            const solsPend = (db.solicitudesInterdepartamentales || []).filter(s => s.status !== 'Culminada');
            solSelect.innerHTML = '<option value="">-- Sin Solicitud --</option>' + solsPend.map(s => `<option value="${s.id}">${s.id} (${s.status}) - ${s.area}: ${s.descripcion.slice(0, 35)}</option>`).join('');

            if (db.repuestos && db.repuestos.length > 0) {
                actualizarInfoStockDespacho(db.repuestos[0].id);
            }

            document.getElementById('salidaReceptor').value = '';
            document.getElementById('modalSalidaMaterial').classList.remove('hidden');
        }

        function actualizarInfoStockDespacho(repId) {
            const rep = (db.repuestos || []).find(r => r.id === repId);
            const info = document.getElementById('salidaStockInfo');
            if (rep && info) {
                info.innerHTML = `Stock Disponible en Almacén: <strong class="${rep.stock <= rep.stockMin ? 'text-red-600' : 'text-emerald-700'}">${rep.stock} ${rep.um}</strong> (Mínimo: ${rep.stockMin})`;
                document.getElementById('salidaCantidad').max = rep.stock;
            }
        }

        document.getElementById('formSalidaMaterial').addEventListener('submit', function(e) {
            e.preventDefault();
            const repId = document.getElementById('salidaRepuestoId').value;
            const cant = parseInt(document.getElementById('salidaCantidad').value, 10);
            const rep = (db.repuestos || []).find(r => r.id === repId);

            if (!rep) {
                alert("Seleccione un repuesto válido.");
                return;
            }

            if (cant > rep.stock) {
                alert(`Existencias insuficientes. Stock actual disponible: ${rep.stock} ${rep.um}`);
                return;
            }

            const otId = document.getElementById('salidaOtId').value || null;
            const solId = document.getElementById('salidaSolicitudId').value || null;
            const receptor = document.getElementById('salidaReceptor').value.trim();
            const obs = document.getElementById('salidaObservaciones').value.trim();

            // 1. Descontar existencias automáticamente del inventario
            rep.stock = Math.max(0, rep.stock - cant);

            // 2. Notificación si llegó al mínimo
            if (rep.stock <= rep.stockMin) {
                dispararNotificacion('Gerente', null, 'Alerta de Stock Mínimo', `El repuesto ${rep.name} llegó a su stock mínimo (${rep.stock} ${rep.um}).`, 'warning', 'almacen', rep.id);
            }

            // 3. Crear registro transaccional de salida
            if (!db.salidasMateriales) db.salidasMateriales = [];
            const dispId = `SAL-2026-${String(db.salidasMateriales.length + 1).padStart(3, '0')}`;
            const dispatchRecord = {
                id: dispId,
                fecha: new Date().toISOString().replace('T', ' ').slice(0, 16),
                otId: otId,
                solicitudId: solId,
                repuestoId: rep.id,
                repuestoNombre: rep.name,
                cantidad: cant,
                despachadoPor: currentUser ? currentUser.name : 'Almacenista',
                receptor: receptor,
                observaciones: obs
            };
            db.salidasMateriales.unshift(dispatchRecord);

            // 4. Si se vinculó a una OT, agregar automáticamente a repuestosUsados de la OT
            if (otId) {
                const ot = (db.ots || []).find(o => o.id === otId);
                if (ot) {
                    if (!ot.repuestosUsados) ot.repuestosUsados = [];
                    ot.repuestosUsados.push({ id: rep.id, name: rep.name, cant: cant, costo: rep.costo });
                }
            }

            // 5. Si se vinculó a una solicitud en espera de materiales, cambiar automáticamente a En proceso
            if (solId) {
                const sol = (db.solicitudesInterdepartamentales || []).find(s => s.id === solId);
                if (sol && sol.status === 'En espera de materiales') {
                    sol.status = 'En proceso';
                    dispararNotificacion('Gerente', null, 'Materiales Entregados', `Materiales entregados para ${sol.id}. La solicitud avanzó a En proceso.`, 'info', 'solicitud', sol.id);
                }
            }

            saveDatabase();
            actualizarBadges();
            renderSidebar();
            closeModal('modalSalidaMaterial');

            if (currentActiveView === 'salidas-materiales') {
                renderSalidasMaterialesView(document.getElementById('mainView'));
            } else if (currentActiveView === 'almacen') {
                renderAlmacenView(document.getElementById('mainView'));
            }
            mostrarToast('Despacho Confirmado', `Se retiraron ${cant} ${rep.um} de ${rep.name}. Stock restante: ${rep.stock}.`, 'success');
        });
"""

# Añadir el bloque de nuevas vistas antes del DOMContentLoaded
target_dom_loaded = "        // --- 17. INICIALIZACIÓN GENERAL AL CARGAR PÁGINA ---"
if target_dom_loaded in text:
    text = text.replace(target_dom_loaded, new_views_code + "\n" + target_dom_loaded)
    print("[OK] Vistas y controladores de Taller Externo y Salida de Materiales agregados.")
else:
    print("[ERROR] target_dom_loaded no encontrado.")

# Guardar progreso en app/static/index.html y sincronizar con index.html en raíz
with open(STATIC_INDEX, "w", encoding="utf-8") as f:
    f.write(text)

with open(ROOT_INDEX, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Archivos guardados exitosamente. Longitud final: {len(text)} caracteres.")

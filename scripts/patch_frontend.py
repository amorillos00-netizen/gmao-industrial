# -*- coding: utf-8 -*-
"""
Script para aplicar los 4 requerimientos industriales en index.html y app/static/index.html:
1. Jefe Mantenimiento:
   - Elimina módulo "Panel departamento de compras".
   - Exportación e impresión de informes filtrados por rango de fechas.
2. Compras:
   - Elimina módulos: Almacén control de compras, Almacén de repuestos, Control de compras.
   - Deja solo: Proveedores y Panel de Compras (sincronización inmediata).
   - Filtrado: solo solicitudes de "Jefe de Mantenimiento".
   - Estados permitidos: [Pendiente, Aprobada, En tránsito]. Prohibido "Recibida".
3. Preventivo:
   - Al cerrar OT preventiva, actualiza plan a "Completado" y cancela notificaciones de vencimiento.
4. Calendario:
   - Vista predeterminada del diagrama del plan a escala semanal.
"""

from pathlib import Path
import re
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "index.html"
STATIC_INDEX_FILE = BASE_DIR / "app" / "static" / "index.html"

content = INDEX_FILE.read_text(encoding="utf-8")

# =========================================================================
# REQUERIMIENTO 1 & 2: ROLES Y PERMISOS EN SIDEBAR
# =========================================================================

# 1. Jefe Mantenimiento (Gerente): Eliminar botón Panel Dpto. Compras
gerente_panel_compras = """                    <button onclick="navigate('compras-panel')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition text-emerald-300" id="nav-compras-panel">
                        <i class="fas fa-store w-4 text-emerald-400"></i><span>Panel Dpto. Compras</span>
                    </button>
"""
if gerente_panel_compras in content:
    content = content.replace(gerente_panel_compras, "")
    print("[OK] Removido Panel Dpto. Compras de Jefe Mantenimiento")

# 2. Compras: Dejar SOLO Panel de Compras y Proveedores (Eliminar Almacén y Control de Compras)
compras_sidebar_old = """            } else if (currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras') {
                nav.innerHTML = `
                    <button onclick="navigate('compras-panel')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-compras-panel">
                        <i class="fas fa-store w-4 text-emerald-400"></i><span>Panel de Compras</span>
                    </button>
                    <button onclick="navigate('compras')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-compras">
                        <i class="fas fa-shopping-cart w-4 text-pink-400"></i><span>${t('navCompras')}</span>
                    </button>
                    <button onclick="navigate('almacen')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-almacen">
                        <i class="fas fa-boxes w-4 text-yellow-400"></i><span>${t('navAlmacen')}</span>
                    </button>
                    <button onclick="navigate('proveedores')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-proveedores">
                        <i class="fas fa-truck w-4 text-teal-400"></i><span>${t('navProveedores')}</span>
                    </button>
                    <button onclick="openModalCompra(false)" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white transition mt-4 shadow">
                        <i class="fas fa-cart-plus w-4"></i><span>+ Nueva Solicitud</span>
                    </button>
                `;"""

compras_sidebar_new = """            } else if (currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras') {
                nav.innerHTML = `
                    <button onclick="navigate('compras-panel')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition text-emerald-300" id="nav-compras-panel">
                        <i class="fas fa-store w-4 text-emerald-400"></i><span>Panel de Compras</span>
                    </button>
                    <button onclick="navigate('proveedores')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-proveedores">
                        <i class="fas fa-truck w-4 text-teal-400"></i><span>${t('navProveedores')}</span>
                    </button>
                `;"""

if compras_sidebar_old in content:
    content = content.replace(compras_sidebar_old, compras_sidebar_new)
    print("[OK] Reemplazado menú de Compras para dejar solo Panel de Compras y Proveedores")

# 3. Restricción de navegación en navigate()
navigate_old = """        function navigate(viewName) {
            currentActiveView = viewName;"""

navigate_new = """        function navigate(viewName) {
            // Restricciones de roles estrictas
            if (currentUser && currentUser.role === 'Gerente' && viewName === 'compras-panel') {
                viewName = 'compras';
            }
            if (currentUser && (currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras')) {
                if (viewName !== 'compras-panel' && viewName !== 'proveedores') {
                    viewName = 'compras-panel';
                }
            }
            currentActiveView = viewName;"""

if navigate_old in content and "Restricciones de roles estrictas" not in content:
    content = content.replace(navigate_old, navigate_new)
    print("[OK] Agregada restricción de navegación en navigate()")

# =========================================================================
# REQUERIMIENTO 1: EXPORTACIÓN/IMPRESIÓN FILTRADA POR RANGO DE FECHAS (JEFE MANTENIMIENTO)
# =========================================================================

# Corrección de filtrado por rango en renderInformesView
filtro_rango_old = """            } else if (informeFiltroPeriodo === 'Rango') {
                if (informeFechaInicio) {
                    otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '') >= informeFechaInicio);
                }
                if (informeFechaFin) {
                    otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '') <= informeFechaFin);
                }
                periodoTexto = `${informeFechaInicio || 'Inicio'} al ${informeFechaFin || 'Fin'}`;
            }"""

filtro_rango_new = """            } else if (informeFiltroPeriodo === 'Rango') {
                otsEvaluadas = otsEvaluadas.filter(o => {
                    const d = (o.fechaProgramada || o.fechaAsignacion || o.fechaFin || o.fechaInicio || '').slice(0, 10);
                    if (informeFechaInicio && d < informeFechaInicio) return false;
                    if (informeFechaFin && d > informeFechaFin) return false;
                    return true;
                });
                periodoTexto = `Rango: ${informeFechaInicio || 'Inicio'} al ${informeFechaFin || 'Fin'}`;
            }"""

if filtro_rango_old in content:
    content = content.replace(filtro_rango_old, filtro_rango_new)
    print("[OK] Corregido filtro de rango en renderInformesView")

# Botones de exportación e impresión específicos de Rango de Fechas
selector_rango_ui_old = """                                ${informeFiltroPeriodo === 'Rango' ? `
                                    <label class="block text-xs font-semibold text-slate-600 mb-1">Rango de Fechas:</label>
                                    <div class="grid grid-cols-2 gap-2">
                                        <input type="date" value="${informeFechaInicio}" onchange="setInformeFechaInicio(this.value)" class="border rounded-lg p-1.5 text-xs outline-none">
                                        <input type="date" value="${informeFechaFin}" onchange="setInformeFechaFin(this.value)" class="border rounded-lg p-1.5 text-xs outline-none">
                                    </div>
                                ` : ''}"""

selector_rango_ui_new = """                                ${informeFiltroPeriodo === 'Rango' ? `
                                    <label class="block text-xs font-semibold text-slate-600 mb-1">Rango de Fechas (Informe Filtrado):</label>
                                    <div class="grid grid-cols-2 gap-2">
                                        <input type="date" value="${informeFechaInicio}" onchange="setInformeFechaInicio(this.value)" class="border rounded-lg p-1.5 text-xs outline-none">
                                        <input type="date" value="${informeFechaFin}" onchange="setInformeFechaFin(this.value)" class="border rounded-lg p-1.5 text-xs outline-none">
                                    </div>
                                    <div class="mt-2 flex flex-wrap gap-1.5">
                                        <button onclick="exportarInformePeriodicoExcel()" class="bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-1 rounded text-[11px] font-semibold flex items-center space-x-1 shadow-sm" title="Exportar informe filtrado por rango a Excel">
                                            <i class="fas fa-file-excel text-[10px]"></i><span>Excel Rango</span>
                                        </button>
                                        <button onclick="exportarInformePeriodicoWord()" class="bg-blue-800 hover:bg-blue-900 text-white px-2 py-1 rounded text-[11px] font-semibold flex items-center space-x-1 shadow-sm" title="Exportar informe filtrado por rango a Word">
                                            <i class="fas fa-file-word text-[10px]"></i><span>Word Rango</span>
                                        </button>
                                        <button onclick="imprimirInforme()" class="bg-slate-800 hover:bg-slate-900 text-white px-2 py-1 rounded text-[11px] font-semibold flex items-center space-x-1 shadow-sm" title="Imprimir informe filtrado por rango a PDF">
                                            <i class="fas fa-print text-[10px]"></i><span>Imprimir Rango</span>
                                        </button>
                                    </div>
                                ` : ''}"""

if selector_rango_ui_old in content:
    content = content.replace(selector_rango_ui_old, selector_rango_ui_new)
    print("[OK] Agregados controles de exportación e impresión por rango de fechas")

# =========================================================================
# REQUERIMIENTO 2: COMPRAS (PANEL DE COMPRAS, FILTRADO Y ESTADOS PERMITIDOS)
# =========================================================================

# 1. En renderComprasPanel: sincronización inmediata y filtro creados por Jefe de Mantenimiento
render_panel_old = """        function renderComprasPanel(container) {
            let compras = db.comprasMateriales || [];

            // Filtrado por fecha y estado"""

render_panel_new = """        function renderComprasPanel(container) {
            // Sincronización inmediata de datos con servidor central
            if (navigator.onLine) {
                setTimeout(() => sincronizarConServidorRemoto(true, true), 30);
            }
            let compras = db.comprasMateriales || [];

            // Filtrado estricto: Compras SOLO ve solicitudes creadas por "Jefe de Mantenimiento"
            if (currentUser && (currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras')) {
                compras = compras.filter(c => {
                    const creador = (c.creadoPor || c.solicitante || 'Jefe de Mantenimiento').toLowerCase();
                    return creador.includes('jefe') || creador.includes('mantenimiento') || creador.includes('carlos mendoza') || creador.includes('admin');
                });
            }

            // Filtrado por fecha y estado"""

if render_panel_old in content:
    content = content.replace(render_panel_old, render_panel_new)
    print("[OK] Agregado filtrado de creador y sincronización inmediata en renderComprasPanel")

# 2. Selector de estatus en filas de renderComprasPanel:
# Estados permitidos para compras: [Pendiente, Aprobada, En tránsito]. Prohibido "Recibida".
compras_selector_old = """                        <td class="p-2.5 text-center whitespace-nowrap">
                            <!-- SELECTOR RÁPIDO DEDICADO PARA DEPARTAMENTO DE COMPRAS -->
                            <select onchange="actualizarEstatusCompra('${c.id}', this.value)" class="text-xs font-bold rounded-lg px-2.5 py-1 border transition shadow-sm outline-none cursor-pointer ${
                                st === 'Pendiente' ? 'bg-amber-50 text-amber-800 border-amber-300' :
                                st === 'En Cotización' ? 'bg-indigo-50 text-indigo-800 border-indigo-300' :
                                st === 'Aprobada' ? 'bg-blue-50 text-blue-800 border-blue-300' :
                                st === 'En Tránsito' ? 'bg-purple-50 text-purple-800 border-purple-300' :
                                st === 'Recibida' ? 'bg-emerald-50 text-emerald-800 border-emerald-300' :
                                'bg-rose-50 text-rose-800 border-rose-300'
                            }">
                                <option value="Pendiente" ${st === 'Pendiente' ? 'selected' : ''}>⏳ Pendiente</option>
                                <option value="En Cotización" ${st === 'En Cotización' ? 'selected' : ''}>📄 En Cotización</option>
                                <option value="Aprobada" ${st === 'Aprobada' ? 'selected' : ''}>✅ Aprobada</option>
                                <option value="En Tránsito" ${st === 'En Tránsito' ? 'selected' : ''}>🚚 En Tránsito</option>
                                <option value="Recibida" ${st === 'Recibida' ? 'selected' : ''}>📦 Recibida en Planta</option>
                                <option value="Rechazada" ${st === 'Rechazada' ? 'selected' : ''}>❌ Rechazada</option>
                            </select>
                        </td>"""

compras_selector_new = """                        <td class="p-2.5 text-center whitespace-nowrap">
                            ${(currentUser && (currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras')) ? (
                                st === 'Recibida' ? `
                                    <span class="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                                        📦 Recibida (Exclusivo Jefe Mantenimiento/Almacén)
                                    </span>
                                ` : `
                                    <select onchange="actualizarEstatusCompra('${c.id}', this.value)" class="text-xs font-bold rounded-lg px-2.5 py-1 border transition shadow-sm outline-none cursor-pointer ${
                                        st === 'Pendiente' ? 'bg-amber-50 text-amber-800 border-amber-300' :
                                        st === 'Aprobada' ? 'bg-blue-50 text-blue-800 border-blue-300' :
                                        'bg-purple-50 text-purple-800 border-purple-300'
                                    }">
                                        <option value="Pendiente" ${st === 'Pendiente' ? 'selected' : ''}>⏳ Pendiente</option>
                                        <option value="Aprobada" ${st === 'Aprobada' ? 'selected' : ''}>✅ Aprobada</option>
                                        <option value="En Tránsito" ${(st === 'En Tránsito' || st === 'En tránsito') ? 'selected' : ''}>🚚 En tránsito</option>
                                    </select>
                                `
                            ) : `
                                <select onchange="actualizarEstatusCompra('${c.id}', this.value)" class="text-xs font-bold rounded-lg px-2.5 py-1 border transition shadow-sm outline-none cursor-pointer ${
                                    st === 'Pendiente' ? 'bg-amber-50 text-amber-800 border-amber-300' :
                                    st === 'En Cotización' ? 'bg-indigo-50 text-indigo-800 border-indigo-300' :
                                    st === 'Aprobada' ? 'bg-blue-50 text-blue-800 border-blue-300' :
                                    (st === 'En Tránsito' || st === 'En tránsito') ? 'bg-purple-50 text-purple-800 border-purple-300' :
                                    st === 'Recibida' ? 'bg-emerald-50 text-emerald-800 border-emerald-300' :
                                    'bg-rose-50 text-rose-800 border-rose-300'
                                }">
                                    <option value="Pendiente" ${st === 'Pendiente' ? 'selected' : ''}>⏳ Pendiente</option>
                                    <option value="En Cotización" ${st === 'En Cotización' ? 'selected' : ''}>📄 En Cotización</option>
                                    <option value="Aprobada" ${st === 'Aprobada' ? 'selected' : ''}>✅ Aprobada</option>
                                    <option value="En Tránsito" ${(st === 'En Tránsito' || st === 'En tránsito') ? 'selected' : ''}>🚚 En tránsito</option>
                                    <option value="Recibida" ${st === 'Recibida' ? 'selected' : ''}>📦 Recibida en Planta</option>
                                    <option value="Rechazada" ${st === 'Rechazada' ? 'selected' : ''}>❌ Rechazada</option>
                                </select>
                            `}
                        </td>"""

if compras_selector_old in content:
    content = content.replace(compras_selector_old, compras_selector_new)
    print("[OK] Corregido selector de estatus en Panel de Compras para restringir 'Recibida'")

# 3. Restricción en actualizarEstatusCompra
actualizar_estatus_old = """        // ACTUALIZACIÓN DIRECTA DE ESTATUS DE COMPRA
        async function actualizarEstatusCompra(id, nuevoEstatus) {
            const comp = (db.comprasMateriales || []).find(c => c.id === id);
            if (!comp) return;
            comp.status = nuevoEstatus;
            saveDatabase();"""

actualizar_estatus_new = """        // ACTUALIZACIÓN DIRECTA DE ESTATUS DE COMPRA
        async function actualizarEstatusCompra(id, nuevoEstatus) {
            const comp = (db.comprasMateriales || []).find(c => c.id === id);
            if (!comp) return;

            // Validación estricta para rol Compras: Prohibido "Recibida"
            const isComprasUser = (currentUser && (currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras'));
            if (isComprasUser) {
                if (nuevoEstatus === 'Recibida') {
                    mostrarToast('Acceso Denegado', 'El estado "Recibida" es exclusivo para Jefe de Mantenimiento y Almacén.', 'urgent');
                    if (currentActiveView === 'compras-panel') renderComprasPanel(document.getElementById('mainView'));
                    return;
                }
                const permitidosCompras = ['Pendiente', 'Aprobada', 'En Tránsito', 'En tránsito'];
                if (!permitidosCompras.includes(nuevoEstatus)) {
                    mostrarToast('Estado No Permitido', 'Compras solo puede asignar: Pendiente, Aprobada o En tránsito.', 'warning');
                    if (currentActiveView === 'compras-panel') renderComprasPanel(document.getElementById('mainView'));
                    return;
                }
            }

            comp.status = nuevoEstatus;
            saveDatabase();"""

if actualizar_estatus_old in content and "Validación estricta para rol Compras: Prohibido \"Recibida\"" not in content:
    content = content.replace(actualizar_estatus_old, actualizar_estatus_new)
    print("[OK] Agregada validación estricta de estados en actualizarEstatusCompra()")

# 4. En modal de compras openModalCompra: ajustar selector de status si es Compras
open_modal_compra_hook = """            if (comId) {
                const comp = db.comprasMateriales.find(c => c.id === comId);"""

open_modal_compra_patched = """            // Ajuste dinámico de opciones de estatus según rol
            const statusSelect = document.getElementById('compraStatus');
            if (statusSelect) {
                const isComprasUser = (currentUser && (currentUser.role === 'Departamento de Compras' || currentUser.role === 'Compras'));
                if (isComprasUser) {
                    statusSelect.innerHTML = `
                        <option value="Pendiente">Pendiente</option>
                        <option value="Aprobada">Aprobada</option>
                        <option value="En Tránsito">En tránsito</option>
                    `;
                } else {
                    statusSelect.innerHTML = `
                        <option value="Pendiente">Pendiente</option>
                        <option value="En Cotización">En Cotización</option>
                        <option value="Aprobada">Aprobada</option>
                        <option value="En Tránsito">En tránsito</option>
                        <option value="Recibida">Recibida</option>
                        <option value="Rechazada">Rechazada</option>
                    `;
                }
            }

            if (comId) {
                const comp = db.comprasMateriales.find(c => c.id === comId);"""

if open_modal_compra_hook in content and "Ajuste dinámico de opciones de estatus según rol" not in content:
    content = content.replace(open_modal_compra_hook, open_modal_compra_patched)
    print("[OK] Ajustadas opciones del modal de compras según rol")

# =========================================================================
# REQUERIMIENTO 3: PREVENTIVO (CIERRE DE OT VINCULADA -> PLAN COMPLETADO & CANCELA VENCIMIENTO)
# =========================================================================

# 1. En formCierreOT submit:
form_cierre_ot_old = """                // CAMBIO AUTOMÁTICO DE ESTATUS EN SOLICITUDES VINCULADAS (REQUERIMIENTO 6)"""

form_cierre_ot_new = """                // ACTUALIZACIÓN AUTOMÁTICA DEL PLAN PREVENTIVO Y CANCELACIÓN DE VENCIMIENTO (REQUERIMIENTO 3)
                if (ot.tipo === 'Preventivo' || ot.planId) {
                    const planIdMatch = ot.planId;
                    const linkedPlan = (db.planesPreventivos || []).find(p => (planIdMatch && p.id === planIdMatch) || p.equipoId === ot.equipoId) ||
                                       (db.planesRefrigeracion || []).find(p => (planIdMatch && p.id === planIdMatch) || p.equipoId === ot.equipoId);
                    if (linkedPlan) {
                        linkedPlan.status = 'Completado';
                        linkedPlan.ultimaFecha = (ot.fechaFin || ot.fechaProgramada || new Date().toISOString()).slice(0, 10);
                        
                        // Cancelar notificaciones de vencimiento del plan y de la OT
                        db.notificaciones = (db.notificaciones || []).filter(n => {
                            const isPlanNotif = (n.enlaceId === linkedPlan.id || (n.id && n.id.includes(linkedPlan.id)));
                            const isOtNotif = (n.enlaceId === ot.id || (n.id && n.id.includes(ot.id)));
                            const isVencimiento = /vencid|preventiv|alerta preventiva/i.test(n.titulo || '') || /vencid|preventiv/i.test(n.mensaje || '');
                            return !( (isPlanNotif || isOtNotif) && isVencimiento );
                        });
                        
                        dispararNotificacion('Gerente', null, 'Preventivo Completado', `La rutina preventiva ${linkedPlan.id} (${linkedPlan.nombre}) en ${ot.equipoId} ha sido completada tras concluir la OT.`, 'success', 'cronograma-anual', linkedPlan.id);
                    }
                }

                // CAMBIO AUTOMÁTICO DE ESTATUS EN SOLICITUDES VINCULADAS (REQUERIMIENTO 6)"""

if form_cierre_ot_old in content and "ACTUALIZACIÓN AUTOMÁTICA DEL PLAN PREVENTIVO" not in content:
    content = content.replace(form_cierre_ot_old, form_cierre_ot_new)
    print("[OK] Agregada actualización automática de plan preventivo y cancelación de alertas en formCierreOT")

# 2. En sincronizarEstadosVinculados:
sync_estados_hook = """            // Reconciliar Condiciones SSL vinculadas a OTs concluidas"""

sync_estados_patched = """            // Reconciliar planes preventivos vinculados a OTs concluidas (Requerimiento 3)
            const otsPrevConcluidas = (db.ots || []).filter(o => o.tipo === 'Preventivo' && (o.status === 'Concluida' || o.status === 'Completada'));
            otsPrevConcluidas.forEach(ot => {
                const plan = (db.planesPreventivos || []).find(p => (ot.planId && p.id === ot.planId) || p.equipoId === ot.equipoId) ||
                             (db.planesRefrigeracion || []).find(p => (ot.planId && p.id === ot.planId) || p.equipoId === ot.equipoId);
                if (plan && plan.status !== 'Completado') {
                    plan.status = 'Completado';
                }
                // Cancelar notificaciones de vencimiento
                db.notificaciones = (db.notificaciones || []).filter(n => {
                    const isPlanNotif = plan && (n.enlaceId === plan.id || (n.id && n.id.includes(plan.id)));
                    const isOtNotif = (n.enlaceId === ot.id || (n.id && n.id.includes(ot.id)));
                    const isVenc = /vencid|preventiv|alerta preventiva/i.test(n.titulo || '') || /vencid|preventiv/i.test(n.mensaje || '');
                    return !( (isPlanNotif || isOtNotif) && isVenc );
                });
            });

            // Reconciliar Condiciones SSL vinculadas a OTs concluidas"""

if sync_estados_hook in content and "Reconciliar planes preventivos vinculados a OTs concluidas" not in content:
    content = content.replace(sync_estados_hook, sync_estados_patched)
    print("[OK] Agregada reconciliación preventiva en sincronizarEstadosVinculados")

# 3. En verificarAlertasPreventivasAnticipadas: omitir planes completados
alertas_hook_old = """            // 1. Revisar Planes Preventivos (para alertar exactamente 5 días previos a la proximaFecha)
            (db.planesPreventivos || []).forEach(p => {
                if (!p.proximaFecha) return;"""

alertas_hook_new = """            // 1. Revisar Planes Preventivos (para alertar exactamente 5 días previos a la proximaFecha)
            (db.planesPreventivos || []).forEach(p => {
                if (!p.proximaFecha || p.status === 'Completado') return;"""

if alertas_hook_old in content:
    content = content.replace(alertas_hook_old, alertas_hook_new)
    print("[OK] Ajustado verificarAlertasPreventivasAnticipadas para omitir planes con status 'Completado'")

# =========================================================================
# REQUERIMIENTO 4: CALENDARIO (ESCALA SEMANAL PREDETERMINADA DEL DIAGRAMA)
# =========================================================================

# 1. Definir cronogramaEscala = 'semanal'
escala_var_old = """        // --- 8. VISTA CRONOGRAMA ANUAL PREVENTIVO MULTIANUAL CON LÓGICA DE FRECUENCIAS ---
        let cronogramaAnioSeleccionado = 2026;"""

escala_var_new = """        // --- 8. VISTA CRONOGRAMA ANUAL PREVENTIVO MULTIANUAL CON LÓGICA DE FRECUENCIAS ---
        let cronogramaAnioSeleccionado = 2026;
        let cronogramaEscala = 'semanal'; // 'semanal' (PREDETERMINADA) | 'mensual'

        function setCronogramaEscala(escala) {
            cronogramaEscala = escala;
            renderCronogramaAnualView(document.getElementById('mainView'));
        }

        function getNumeroSemanaISO(d) {
            const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
            date.setUTCDate(date.getUTCDate() + 4 - (date.getUTCDay() || 7));
            const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
            return Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
        }"""

if escala_var_old in content and "let cronogramaEscala = 'semanal';" not in content:
    content = content.replace(escala_var_old, escala_var_new)
    print("[OK] Declarada escala semanal predeterminada para el diagrama del plan")

# 2. Renderizar matriz con escala semanal y selector de escala
render_cronograma_head_old = """        function renderCronogramaAnualView(container) {
            const anio = cronogramaAnioSeleccionado || 2026;
            const mesesNombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

            const rowsHtml = db.planesPreventivos.map(p => {"""

render_cronograma_head_new = """        function renderCronogramaAnualView(container) {
            const anio = cronogramaAnioSeleccionado || 2026;
            const mesesNombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
            const semanasAnio = Array.from({length: 52}, (_, i) => i + 1);

            const rowsHtml = db.planesPreventivos.map(p => {
                const eq = db.equipos.find(e => e.id === p.equipoId) || { name: p.equipoId, linea: 'General' };
                const isPlanCompletado = (p.status === 'Completado');

                if (cronogramaEscala === 'semanal') {
                    // ESCALA SEMANAL (PREDETERMINADA): Semanas 1 a 52
                    const semanasProyectadas = new Set();
                    let stepSemanas = 4;
                    if (p.frecuenciaTipo === 'semanas') {
                        stepSemanas = Math.max(1, parseInt(p.frecuenciaValor || 1));
                    } else if (p.frecuenciaTipo === 'dias') {
                        stepSemanas = Math.max(1, Math.round((p.frecuenciaValor || 7) / 7));
                    } else {
                        stepSemanas = Math.max(1, parseInt(p.frecuenciaValor || 1) * 4);
                    }

                    let startSemana = 1;
                    if (p.proximaFecha && p.proximaFecha.length >= 10) {
                        try {
                            const pDate = new Date(p.proximaFecha.slice(0, 10) + 'T00:00:00');
                            startSemana = getNumeroSemanaISO(pDate);
                        } catch(e) { startSemana = 1; }
                    }

                    for (let s = startSemana; s <= 52; s += stepSemanas) {
                        if (s >= 1 && s <= 52) semanasProyectadas.add(s);
                    }

                    const semanasColsHtml = semanasAnio.map(sNum => {
                        const isProgramada = semanasProyectadas.has(sNum);
                        if (!isProgramada) {
                            return `<td class="p-0.5 text-center border border-slate-200 bg-slate-50 text-[9px] text-slate-300">-</td>`;
                        }

                        // Verificar OT concluida en esa semana
                        const otConcluidaSemana = db.ots.find(o => {
                            if (o.equipoId !== p.equipoId || (o.status !== 'Concluida' && o.status !== 'Completada')) return false;
                            const fOT = o.fechaFin || o.fechaProgramada || o.fechaAsignacion;
                            if (!fOT || !fOT.startsWith(String(anio))) return false;
                            try {
                                return getNumeroSemanaISO(new Date(fOT.slice(0, 10) + 'T00:00:00')) === sNum;
                            } catch(e) { return false; }
                        });

                        if (otConcluidaSemana || isPlanCompletado) {
                            return `
                                <td class="p-0.5 text-center border border-slate-200 bg-emerald-50 text-emerald-700 font-bold text-[9px]" title="Ejecutada en Semana ${sNum}">
                                    <span class="bg-emerald-600 text-white px-1 py-0.2 rounded text-[8px] shadow-sm">E</span>
                                </td>
                            `;
                        } else {
                            return `
                                <td class="p-0.5 text-center border border-slate-200 bg-blue-50 text-blue-700 font-semibold text-[9px] hover:bg-blue-100 cursor-pointer" onclick="crearOTDesdeCronograma('${p.id}', '${anio}-W${String(sNum).padStart(2,'0')}')" title="Click para generar OT en Semana ${sNum}">
                                    <span class="bg-blue-600 text-white px-1 py-0.2 rounded text-[8px] shadow-sm">P</span>
                                </td>
                            `;
                        }
                    }).join('');

                    return `
                        <tr class="hover:bg-slate-50 transition">
                            <td class="p-2 border border-slate-200 font-mono font-bold text-blue-700 text-xs">${p.equipoId}</td>
                            <td class="p-2 border border-slate-200 text-xs font-semibold text-slate-800">${eq.name}</td>
                            <td class="p-2 border border-slate-200 text-[11px] text-slate-600">${p.nombre}</td>
                            <td class="p-2 border border-slate-200 text-center text-[11px] font-semibold text-slate-700">${p.frecuencia}</td>
                            <td class="p-2 border border-slate-200 text-center text-[11px] font-mono">${p.ultimaFecha || '-'}</td>
                            <td class="p-2 border border-slate-200 text-center text-[11px] font-mono font-bold text-blue-600">${p.proximaFecha || '-'}</td>
                            <td class="p-2 border border-slate-200 text-center text-[10px]">
                                <span class="px-1.5 py-0.5 rounded font-bold ${isPlanCompletado ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
                                    ${isPlanCompletado ? 'Completado' : (p.status || 'Pendiente')}
                                </span>
                            </td>
                            ${semanasColsHtml}
                            <td class="p-2 border border-slate-200 text-center text-xs whitespace-nowrap">
                                <button onclick="openModalPlanPreventivo('${p.id}', false)" class="text-blue-600 hover:text-blue-800 p-1" title="Editar Frecuencia"><i class="fas fa-edit"></i></button>
                                <button onclick="eliminarPlanPreventivo('${p.id}', false)" class="text-red-500 hover:text-red-700 p-1" title="Eliminar"><i class="fas fa-trash"></i></button>
                            </td>
                        </tr>
                    `;
                }

                // ESCALA MENSUAL (ALTERNA):"""

if render_cronograma_head_old in content:
    content = content.replace(render_cronograma_head_old, render_cronograma_head_new)
    print("[OK] Integrada escala semanal en generación de filas del cronograma")

# 3. Encabezado de la tabla para soportar Escala Semanal y selector de Escala en la UI
ui_escala_old = """                            <div class="flex items-center space-x-1.5 bg-slate-100 p-1 rounded-lg border">
                                <button onclick="cambiarCronogramaAnio(${anio - 1})" class="px-2 py-1 bg-white hover:bg-slate-200 text-slate-700 rounded text-xs font-bold shadow-sm" title="Año Anterior">
                                    <i class="fas fa-chevron-left"></i>
                                </button>
                                <select onchange="cambiarCronogramaAnio(this.value)" class="bg-white border rounded px-2.5 py-1 text-xs font-bold text-blue-700 outline-none cursor-pointer">
                                    ${listaAnios.map(y => `<option value="${y}" ${y === anio ? 'selected' : ''}>Año ${y}</option>`).join('')}
                                </select>
                                <button onclick="cambiarCronogramaAnio(${anio + 1})" class="px-2 py-1 bg-white hover:bg-slate-200 text-slate-700 rounded text-xs font-bold shadow-sm" title="Año Siguiente">
                                    <i class="fas fa-chevron-right"></i>
                                </button>
                            </div>"""

ui_escala_new = """                            <!-- SELECTOR DE ESCALA DE DIAGRAMA: SEMANAL (PREDETERMINADA) / MENSUAL -->
                            <div class="flex items-center space-x-1 bg-slate-100 p-1 rounded-lg border">
                                <button onclick="setCronogramaEscala('semanal')" class="px-2.5 py-1 rounded text-xs font-bold transition ${cronogramaEscala === 'semanal' ? 'bg-emerald-600 text-white shadow' : 'text-slate-600 hover:text-slate-900'}">
                                    <i class="fas fa-calendar-week mr-1"></i> Escala Semanal
                                </button>
                                <button onclick="setCronogramaEscala('mensual')" class="px-2.5 py-1 rounded text-xs font-bold transition ${cronogramaEscala === 'mensual' ? 'bg-emerald-600 text-white shadow' : 'text-slate-600 hover:text-slate-900'}">
                                    <i class="fas fa-calendar-alt mr-1"></i> Escala Mensual
                                </button>
                            </div>

                            <div class="flex items-center space-x-1.5 bg-slate-100 p-1 rounded-lg border">
                                <button onclick="cambiarCronogramaAnio(${anio - 1})" class="px-2 py-1 bg-white hover:bg-slate-200 text-slate-700 rounded text-xs font-bold shadow-sm" title="Año Anterior">
                                    <i class="fas fa-chevron-left"></i>
                                </button>
                                <select onchange="cambiarCronogramaAnio(this.value)" class="bg-white border rounded px-2.5 py-1 text-xs font-bold text-blue-700 outline-none cursor-pointer">
                                    ${listaAnios.map(y => `<option value="${y}" ${y === anio ? 'selected' : ''}>Año ${y}</option>`).join('')}
                                </select>
                                <button onclick="cambiarCronogramaAnio(${anio + 1})" class="px-2 py-1 bg-white hover:bg-slate-200 text-slate-700 rounded text-xs font-bold shadow-sm" title="Año Siguiente">
                                    <i class="fas fa-chevron-right"></i>
                                </button>
                            </div>"""

if ui_escala_old in content:
    content = content.replace(ui_escala_old, ui_escala_new)
    print("[OK] Agregado selector de escala Semanal/Mensual en la UI")

# 4. Encabezado thead de la tabla de cronograma según escala
thead_old = """                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2 border border-slate-800 text-[11px]">Código</th>
                                    <th class="p-2 border border-slate-800 text-[11px]">Equipo / Sistema</th>
                                    <th class="p-2 border border-slate-800 text-[11px]">Actividad Preventiva</th>
                                    <th class="p-2 border border-slate-800 text-center text-[11px]">Frecuencia</th>
                                    <th class="p-2 border border-slate-800 text-center text-[11px]">Última</th>
                                    <th class="p-2 border border-slate-800 text-center text-[11px]">Próxima</th>
                                    ${mesesNombres.map(m => `<th class="p-1 border border-slate-800 text-center text-[10px] w-8">${m}</th>`).join('')}
                                    <th class="p-2 border border-slate-800 text-center text-[11px]">Acciones</th>
                                </tr>
                            </thead>"""

thead_new = """                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2 border border-slate-800 text-[11px]">Código</th>
                                    <th class="p-2 border border-slate-800 text-[11px]">Equipo / Sistema</th>
                                    <th class="p-2 border border-slate-800 text-[11px]">Actividad Preventiva</th>
                                    <th class="p-2 border border-slate-800 text-center text-[11px]">Frecuencia</th>
                                    <th class="p-2 border border-slate-800 text-center text-[11px]">Última</th>
                                    <th class="p-2 border border-slate-800 text-center text-[11px]">Próxima</th>
                                    ${cronogramaEscala === 'semanal' ? '<th class="p-2 border border-slate-800 text-center text-[11px]">Estado</th>' : ''}
                                    ${cronogramaEscala === 'semanal' ? 
                                        Array.from({length: 52}, (_, i) => `<th class="p-0.5 border border-slate-800 text-center text-[8px] font-mono" title="Semana ${i+1}">S${String(i+1).padStart(2,'0')}</th>`).join('') :
                                        mesesNombres.map(m => `<th class="p-1 border border-slate-800 text-center text-[10px] w-8">${m}</th>`).join('')
                                    }
                                    <th class="p-2 border border-slate-800 text-center text-[11px]">Acciones</th>
                                </tr>
                            </thead>"""

if thead_old in content:
    content = content.replace(thead_old, thead_new)
    print("[OK] Encabezado dinámico thead actualizado para escala semanal")

# Guardar cambios en index.html y sincronizar app/static/index.html
INDEX_FILE.write_text(content, encoding="utf-8")
STATIC_INDEX_FILE.write_text(content, encoding="utf-8")
print("[COMPLETO] index.html y app/static/index.html actualizados y sincronizados con éxito.")

# -*- coding: utf-8 -*-
"""
Script de actualización integral de GMAO Industrial Pro v3.3
SALTYSNACK TUYERO C.A. - Confiabilidad y Gestión de Mantenimiento
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_INDEX = BASE_DIR / "app" / "static" / "index.html"
ROOT_INDEX = BASE_DIR / "index.html"

with open(STATIC_INDEX, "r", encoding="utf-8") as f:
    text = f.read()

# -----------------------------------------------------------------------------
# 1. AGREGAR LOS 3 NUEVOS MODALES (Taller Externo, Recepción Taller, Salida Material)
# -----------------------------------------------------------------------------
modals_html = """
    <!-- MODAL SEGUIMIENTO DE EQUIPOS EN TALLER EXTERNO -->
    <div id="modalTallerExterno" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 my-8 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center">
                    <i class="fas fa-truck-pickup text-amber-600 mr-2"></i> Envío a Servicio / Taller Externo
                </h3>
                <button onclick="closeModal('modalTallerExterno')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formTallerExterno" class="space-y-3.5">
                <input type="hidden" id="tallerExternoId">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Equipo / Activo a Enviar *</label>
                    <select id="tallerEquipoId" required class="w-full border rounded-lg p-2 text-xs bg-white font-medium outline-none">
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Taller / Proveedor Especializado Contratado *</label>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <select id="tallerProveedorSelect" onchange="seleccionarProveedorTaller(this.value)" class="w-full border rounded-lg p-2 text-xs bg-white font-medium outline-none">
                            <option value="">-- Proveedor Registrado --</option>
                        </select>
                        <input type="text" id="tallerProveedorNombre" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Nombre / Razón Social del Taller">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Fecha de Salida *</label>
                        <input type="date" id="tallerFechaSalida" required class="w-full border rounded-lg p-2 text-xs outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Fecha Estimada de Retorno *</label>
                        <input type="date" id="tallerFechaEstimada" required class="w-full border rounded-lg p-2 text-xs outline-none">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Motivo del Servicio / Reparación / Rectificación *</label>
                    <textarea id="tallerMotivo" rows="2" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Ej: Rectificación de cigüeñal, rebobinado de motor eléctrico trifásico, mecanizado de eje..."></textarea>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Costo Estimado / Presupuesto ($)</label>
                        <input type="number" id="tallerCostoEstimado" step="0.01" min="0" value="0.00" class="w-full border rounded-lg p-2 text-xs outline-none font-mono">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Estatus del Trabajo *</label>
                        <select id="tallerStatus" required class="w-full border rounded-lg p-2 text-xs bg-white font-bold outline-none">
                            <option value="En diagnóstico">En diagnóstico</option>
                            <option value="En reparación">En reparación</option>
                            <option value="Esperando repuestos">Esperando repuestos</option>
                            <option value="Listo para retiro">Listo para retiro</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Observaciones / Guía de Despacho</label>
                    <textarea id="tallerObservaciones" rows="2" class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="N° de guía de salida de planta, persona que retiró el equipo, accesorios entregados..."></textarea>
                </div>
                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalTallerExterno')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-semibold hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-5 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-bold shadow">Guardar Registro</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL CONTROL DE RECEPCIÓN DE EQUIPO DESDE TALLER EXTERNO -->
    <div id="modalRecepcionTaller" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 my-8">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center">
                    <i class="fas fa-clipboard-check text-emerald-600 mr-2"></i> Recepción de Equipo a Planta
                </h3>
                <button onclick="closeModal('modalRecepcionTaller')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formRecepcionTaller" class="space-y-3.5">
                <input type="hidden" id="recTallerId">
                <div class="p-3 bg-slate-50 border rounded-lg text-xs space-y-1">
                    <div class="font-bold text-slate-800" id="recTallerEquipo">Equipo: -</div>
                    <div class="text-slate-600" id="recTallerProveedor">Taller: -</div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Fecha de Retorno Real *</label>
                        <input type="date" id="recFechaRetorno" required class="w-full border rounded-lg p-2 text-xs outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Costo Final Facturado ($)</label>
                        <input type="number" id="recCostoFinal" step="0.01" min="0" value="0.00" class="w-full border rounded-lg p-2 text-xs outline-none font-mono">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Condición de Recepción / Pruebas *</label>
                    <select id="recCondicion" required class="w-full border rounded-lg p-2 text-xs bg-white font-bold outline-none">
                        <option value="Conforme y Operativo">Conforme y Operativo (Instalado / Probado)</option>
                        <option value="Pruebas en Planta Pendientes">Pruebas en Planta Pendientes (Recibido sin instalar)</option>
                        <option value="Conforme en Almacén">Conforme en Almacén (En custodia de repuestos)</option>
                        <option value="No Conforme / Garantía">No Conforme (Reclamo en Garantía)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Recibido en Planta por *</label>
                    <input type="text" id="recRecibidoPor" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Nombre del inspector o técnico receptor">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Observaciones de Recepción / N° Factura</label>
                    <textarea id="recObservaciones" rows="2" class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="N° de factura fiscal, reporte de pruebas del taller, recomendaciones operativas..."></textarea>
                </div>
                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalRecepcionTaller')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-semibold hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow">Confirmar Recepción</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL CONTROL DE SALIDA DE MATERIALES Y REPUESTOS (ROL ALMACENISTA) -->
    <div id="modalSalidaMaterial" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 my-8 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center">
                    <i class="fas fa-dolly-flatbed text-yellow-600 mr-2"></i> Despacho / Salida de Materiales y Repuestos
                </h3>
                <button onclick="closeModal('modalSalidaMaterial')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formSalidaMaterial" class="space-y-3.5">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Repuesto / Material a Despachar *</label>
                    <select id="salidaRepuestoId" required onchange="actualizarInfoStockDespacho(this.value)" class="w-full border rounded-lg p-2 text-xs bg-white font-medium outline-none">
                    </select>
                    <div id="salidaStockInfo" class="text-[11px] font-bold text-blue-700 mt-1">Stock Disponible: -</div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Vincular a Orden de Trabajo (OT)</label>
                        <select id="salidaOtId" class="w-full border rounded-lg p-2 text-xs bg-white font-medium outline-none">
                            <option value="">-- Sin OT Vinculada --</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Vincular a Solicitud Interdepartamental</label>
                        <select id="salidaSolicitudId" class="w-full border rounded-lg p-2 text-xs bg-white font-medium outline-none">
                            <option value="">-- Sin Solicitud --</option>
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Cantidad a Despachar *</label>
                        <input type="number" id="salidaCantidad" required min="1" value="1" class="w-full border rounded-lg p-2 text-xs font-bold outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Receptor (Técnico / Personal) *</label>
                        <input type="text" id="salidaReceptor" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Nombre de quien recibe">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Observaciones / Justificación</label>
                    <textarea id="salidaObservaciones" rows="2" class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Detalle de instalación o motivo del retiro del almacén..."></textarea>
                </div>

                <div class="p-2.5 bg-yellow-50 border border-yellow-200 rounded-lg text-[11px] text-yellow-800 flex items-center space-x-2">
                    <i class="fas fa-info-circle text-yellow-600"></i>
                    <span>El stock del inventario se descontará automáticamente de forma transaccional.</span>
                </div>

                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalSalidaMaterial')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-semibold hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-5 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg text-xs font-bold shadow">Confirmar Despacho</button>
                </div>
            </form>
        </div>
    </div>
"""

target_modal_anchor = "    <!-- MODAL VINCULACIÓN ANDROID / QR -->"
if target_modal_anchor in text:
    text = text.replace(target_modal_anchor, modals_html + "\n" + target_modal_anchor)
    print("[OK] Modales de Taller Externo y Salida de Materiales agregados.")
else:
    print("[ERROR] target_modal_anchor no encontrado.")

# -----------------------------------------------------------------------------
# 2. ACTUALIZAR INITIALDATA CON ROL ALMACENISTA, TALLER EXTERNO Y SALIDAS
# -----------------------------------------------------------------------------
target_users_seed = """                { id: 'u6', username: 'gerente_planta', pass: '1234', name: 'Ing. Roberto Navarro', role: 'Gerente', cargo: 'Gerente de Planta', departamento: 'Gerencia General' }"""
replacement_users_seed = """                { id: 'u6', username: 'gerente_planta', pass: '1234', name: 'Ing. Roberto Navarro', role: 'Gerente', cargo: 'Gerente de Planta', departamento: 'Gerencia General' },
                { id: 'u7', username: 'almacenista', pass: '1234', name: 'Pedro Ramírez (Almacenista)', role: 'Almacenista', cargo: 'Almacenista Principal', departamento: 'Almacén y Suministros' }"""

if target_users_seed in text:
    text = text.replace(target_users_seed, replacement_users_seed)
    print("[OK] Usuario y Rol Almacenista agregados a initialData.users.")

# Corregir estatus de SOL-2026-001 a Culminada en initialData para consistencia reactiva
target_sol1 = "{ id: 'SOL-2026-001', tipo: 'Maquinaria / Equipo', urgencia: 'Alta', area: 'Producción - Envasado', ubicacion: 'Cinta Transportadora #3', descripcion: 'Fuga de aceite en reductor principal y vibración anormal.', solicitante: 'Roberto Gómez (Jefe Producción)', fechaHora: '2026-10-29 10:15', status: 'Aprobada', otVinculada: 'OT-2026-001' }"
replacement_sol1 = "{ id: 'SOL-2026-001', tipo: 'Maquinaria / Equipo', urgencia: 'Alta', area: 'Producción - Envasado', ubicacion: 'Cinta Transportadora #3', descripcion: 'Fuga de aceite en reductor principal y vibración anormal.', solicitante: 'Roberto Gómez (Jefe Producción)', fechaHora: '2026-10-29 10:15', status: 'Culminada', otVinculada: 'OT-2026-001' }"

if target_sol1 in text:
    text = text.replace(target_sol1, replacement_sol1)
    print("[OK] SOL-2026-001 corregida a Culminada en initialData.")

# Agregar colecciones equiposTallerExterno y salidasMateriales en initialData
target_sol_ssl = "            solicitudesSSL: ["
replacement_sol_ssl = """            equiposTallerExterno: [
                { id: 'EXT-2026-001', equipoId: 'EQ-102', proveedorId: 'PRV-03', proveedorNombre: 'ElectroMotores & Automatización del Centro', fechaSalida: '2026-11-01', fechaEstimadaRetorno: '2026-11-15', fechaRetornoReal: null, motivoServicio: 'Rebobinado de motor trifásico 15HP y balanceo dinámico de rotor', costoEstimado: 350.00, costoFinal: 0.0, status: 'En reparación', condicionRecepcion: null, recibidoPor: null, observaciones: 'Enviado por falla de aislamiento térmico tras sobrecarga.' }
            ],
            salidasMateriales: [
                { id: 'SAL-2026-001', fecha: '2026-10-20 08:30', otId: 'OT-2026-001', solicitudId: 'SOL-2026-001', repuestoId: 'REP-06', repuestoNombre: 'Kit de juntas / Limpiador mordazas', cantidad: 1, despachadoPor: 'Pedro Ramírez (Almacenista)', receptor: 'Juan Pérez (Técnico)', observaciones: 'Despacho para mantenimiento preventivo de mordazas' }
            ],
            solicitudesSSL: ["""

if target_sol_ssl in text:
    text = text.replace(target_sol_ssl, replacement_sol_ssl, 1)
    print("[OK] Colecciones iniciales de Taller Externo y Salidas agregadas a initialData.")

# -----------------------------------------------------------------------------
# 3. ACTUALIZAR LOADDATABASE() Y SAVEDATABASE()
# -----------------------------------------------------------------------------
target_load_db = "if (!db.solicitudesSSL) db.solicitudesSSL = initialData.solicitudesSSL;"
replacement_load_db = """if (!db.solicitudesSSL) db.solicitudesSSL = initialData.solicitudesSSL;
                    if (!db.equiposTallerExterno) db.equiposTallerExterno = initialData.equiposTallerExterno;
                    if (!db.salidasMateriales) db.salidasMateriales = initialData.salidasMateriales;"""

if target_load_db in text:
    text = text.replace(target_load_db, replacement_load_db)
    print("[OK] loadDatabase() enriquecido con colecciones de taller y salidas.")

target_save_db = """                    solicitudesInterdepartamentales: db.solicitudesInterdepartamentales,
                    solicitudesSSL: db.solicitudesSSL,"""
replacement_save_db = """                    solicitudesInterdepartamentales: db.solicitudesInterdepartamentales,
                    solicitudesSSL: db.solicitudesSSL,
                    equiposTallerExterno: db.equiposTallerExterno,
                    salidasMateriales: db.salidasMateriales,"""

if target_save_db in text:
    text = text.replace(target_save_db, replacement_save_db)
    print("[OK] saveDatabase() actualizado para persistir taller y salidas.")

# Agregar sincronización de taller y salidas en sync
target_sync_get = """if (sData.data.solicitudesSSL) db.solicitudesSSL = sData.data.solicitudesSSL;"""
replacement_sync_get = """if (sData.data.solicitudesSSL) db.solicitudesSSL = sData.data.solicitudesSSL;
                        if (sData.data.equiposTallerExterno) db.equiposTallerExterno = sData.data.equiposTallerExterno;
                        if (sData.data.salidasMateriales) db.salidasMateriales = sData.data.salidasMateriales;"""

if target_sync_get in text:
    text = text.replace(target_sync_get, replacement_sync_get)
    print("[OK] Sincronización offline-first actualizada con nuevos módulos.")

# -----------------------------------------------------------------------------
# 4. FUNCIÓN CENTRALIZADA ACTUALIZARBADGES() Y MEJORA DE ALERTAS PREVENTIVAS
# -----------------------------------------------------------------------------
target_alertas_prev = """        // --- SISTEMA DE ALERTAS PREVENTIVAS A 5 DÍAS ---
        function verificarAlertasPreventivasAnticipadas() {"""

replacement_alertas_prev = """        // --- CONTROL REACTIVO DE BADGES Y CONTADORES ---
        function actualizarBadges() {
            if (!db) return;

            // 1. Solicitudes pendientes: solicitudes cuyo estatus NO es 'Culminada'
            const pendSolicitudes = (db.solicitudesInterdepartamentales || []).filter(s => s.status !== 'Culminada').length;

            // 2. SSL pendientes: condiciones cuyo estatus es 'Pendiente' o 'En Corrección'
            const pendSSL = (db.solicitudesSSL || []).filter(s => s.status === 'Pendiente' || s.status === 'En Corrección').length;

            // Auto-marcar notificaciones leídas si el ítem vinculado ya culminó o se corrigió
            if (db.notificaciones) {
                db.notificaciones.forEach(n => {
                    if (!n.leido) {
                        if (n.enlaceTipo === 'solicitud' && n.enlaceId) {
                            const sol = (db.solicitudesInterdepartamentales || []).find(s => s.id === n.enlaceId);
                            if (sol && sol.status === 'Culminada') n.leido = true;
                        } else if (n.enlaceTipo === 'ssl' && n.enlaceId) {
                            const ssl = (db.solicitudesSSL || []).find(s => s.id === n.enlaceId);
                            if (ssl && (ssl.status === 'Corregida' || ssl.status === 'Desestimada')) n.leido = true;
                        }
                    }
                });
            }

            // Actualizar elemento DOM badge-solicitudes
            const bSol = document.getElementById('badge-solicitudes');
            if (bSol) {
                if (pendSolicitudes > 0) {
                    bSol.textContent = pendSolicitudes;
                    bSol.classList.remove('hidden');
                    bSol.style.display = 'inline-block';
                } else {
                    bSol.textContent = '0';
                    bSol.classList.add('hidden');
                    bSol.style.display = 'none';
                }
            }

            // Actualizar elemento DOM badge-ssl
            const bSSL = document.getElementById('badge-ssl');
            if (bSSL) {
                if (pendSSL > 0) {
                    bSSL.textContent = pendSSL;
                    bSSL.classList.remove('hidden');
                    bSSL.style.display = 'inline-block';
                } else {
                    bSSL.textContent = '0';
                    bSSL.classList.add('hidden');
                    bSSL.style.display = 'none';
                }
            }

            renderNotificaciones();
        }

        // --- SISTEMA DE ALERTAS PREVENTIVAS Y OTs PROGRAMADAS (REQUERIMIENTO 5) ---
        function verificarAlertasPreventivasAnticipadas() {"""

if target_alertas_prev in text:
    text = text.replace(target_alertas_prev, replacement_alertas_prev)
    print("[OK] Función centralizada actualizarBadges() insertada.")

# Reemplazar la lógica de alertas a 5 días para abarcar <= 5 días, hoy y vencidos (para Planes y OTs)
old_alert_loop = """                if (diffDays === 5) {
                    const notifId = `NOTIF-PREV-5D-${p.id}-${p.proximaFecha.slice(0, 10)}`;
                    const yaExiste = (db.notificaciones || []).some(n => n.id === notifId);
                    if (!yaExiste) {
                        const eq = db.equipos.find(e => e.id === p.equipoId) || { name: p.equipoId };
                        const nuevaNotif = {
                            id: notifId,
                            usuarioId: null,
                            rolDestino: 'Gerente',
                            titulo: 'Alerta Preventiva (En 5 días)',
                            mensaje: `Mantenimiento preventivo en exactamente 5 días (${p.proximaFecha.slice(0,10)}): ${p.equipoId} - ${eq.name} (${p.nombre}).`,
                            tipo: 'warning',
                            leido: false,
                            fechaHora: new Date().toISOString().slice(0, 16).replace('T', ' '),
                            enlaceTipo: 'cronograma-anual',
                            enlaceId: p.id
                        };
                        db.notificaciones.unshift(nuevaNotif);
                        nuevasAlertas++;
                    }
                }"""

new_alert_loop = """                if (diffDays <= 5) {
                    const notifId = `NOTIF-PREV-${p.id}-${p.proximaFecha.slice(0, 10)}`;
                    const yaExiste = (db.notificaciones || []).some(n => n.id === notifId);
                    if (!yaExiste) {
                        const eq = (db.equipos || []).find(e => e.id === p.equipoId) || { name: p.equipoId };
                        let titulo = 'Alerta Preventiva Próxima';
                        let tipo = 'warning';
                        let msg = `Rutina preventiva en ${diffDays} días (${p.proximaFecha.slice(0,10)}): ${p.equipoId} - ${eq.name} (${p.nombre}).`;
                        if (diffDays < 0) {
                            titulo = '¡Atención! Preventivo Vencido';
                            tipo = 'urgent';
                            msg = `Rutina preventiva vencida hace ${Math.abs(diffDays)} días (${p.proximaFecha.slice(0,10)}): ${p.equipoId} - ${eq.name}. Requiere atención inmediata.`;
                        } else if (diffDays === 0) {
                            titulo = '¡Hoy! Preventivo Programado';
                            tipo = 'urgent';
                            msg = `Rutina preventiva programada para HOY: ${p.equipoId} - ${eq.name} (${p.nombre}).`;
                        }
                        const nuevaNotif = {
                            id: notifId,
                            usuarioId: null,
                            rolDestino: 'Gerente',
                            titulo: titulo,
                            mensaje: msg,
                            tipo: tipo,
                            leido: false,
                            fechaHora: new Date().toISOString().slice(0, 16).replace('T', ' '),
                            enlaceTipo: 'cronograma-anual',
                            enlaceId: p.id
                        };
                        db.notificaciones.unshift(nuevaNotif);
                        nuevasAlertas++;
                    }
                }"""

if old_alert_loop in text:
    text = text.replace(old_alert_loop, new_alert_loop)
    print("[OK] Alertas automáticas ampliadas para preventivos próximos y vencidos.")

# -----------------------------------------------------------------------------
# 5. REESTRUCTURACIÓN DE RENDERSIDEBAR() CON ROL ALMACENISTA Y BADGES DINÁMICOS
# -----------------------------------------------------------------------------
old_sidebar_code = """        function renderSidebar() {
            const nav = document.getElementById('navigationTabs');
            if (!nav || !currentUser) return;
            nav.innerHTML = '';

            if (currentUser.role === 'Gerente') {
                const pendSolicitudes = db.solicitudesInterdepartamentales.filter(s => s.status !== 'Culminada').length;
                const pendSSL = db.solicitudesSSL.filter(s => s.status === 'Pendiente' || s.status === 'En Corrección').length;

                nav.innerHTML = `
                    <button onclick="navigate('dashboard')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-dashboard">
                        <i class="fas fa-chart-line w-4 text-blue-400"></i><span>${t('navDashboard')}</span>
                    </button>
                    <button onclick="navigate('solicitudes-gerente')" class="sidebar-btn w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-solicitudes-gerente">
                        <div class="flex items-center space-x-3">
                            <i class="fas fa-inbox w-4 text-amber-400"></i><span>${t('navSolicitudes')}</span>
                        </div>
                        ${pendSolicitudes > 0 ? `<span class="bg-amber-500 text-white font-bold text-[10px] px-1.5 py-0.2 rounded-full">${pendSolicitudes}</span>` : ''}
                    </button>
                    <button onclick="navigate('cronograma-anual')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-cronograma-anual">
                        <i class="fas fa-calendar-check w-4 text-emerald-400"></i><span>${t('navCronogramaAnual')}</span>
                    </button>
                    <button onclick="navigate('ssl')" class="sidebar-btn w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-ssl">
                        <div class="flex items-center space-x-3">
                            <i class="fas fa-hard-hat w-4 text-orange-400"></i><span>${t('navSSL')}</span>
                        </div>
                        ${pendSSL > 0 ? `<span class="bg-red-500 text-white font-bold text-[10px] px-1.5 py-0.2 rounded-full">${pendSSL}</span>` : ''}
                    </button>
                    <button onclick="navigate('ots')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-ots">
                        <i class="fas fa-clipboard-list w-4 text-indigo-400"></i><span>${t('navOTs')}</span>
                    </button>
                    <button onclick="navigate('cronograma-refrigeracion')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-cronograma-refrigeracion">
                        <i class="fas fa-snowflake w-4 text-cyan-400"></i><span>${t('navRefrigeracion')}</span>
                    </button>
                    <button onclick="navigate('equipos')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-equipos">
                        <i class="fas fa-sitemap w-4 text-purple-400"></i><span>${t('navEquipos')}</span>
                    </button>
                    <button onclick="navigate('almacen')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-almacen">
                        <i class="fas fa-boxes w-4 text-yellow-400"></i><span>${t('navAlmacen')}</span>
                    </button>
                    <button onclick="navigate('proveedores')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-proveedores">
                        <i class="fas fa-truck w-4 text-teal-400"></i><span>${t('navProveedores')}</span>
                    </button>
                    <button onclick="navigate('compras')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-compras">
                        <i class="fas fa-shopping-cart w-4 text-pink-400"></i><span>${t('navCompras')}</span>
                    </button>
                    <button onclick="navigate('informes')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-informes">
                        <i class="fas fa-file-invoice w-4 text-orange-400"></i><span>${t('navInformes')}</span>
                    </button>
                    <button onclick="navigate('usuarios')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-usuarios">
                        <i class="fas fa-users-cog w-4 text-slate-400"></i><span>${t('navUsuarios')}</span>
                    </button>
                    <button onclick="openModalConfiguracionMTTR()" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition text-emerald-300" id="nav-config-mttr">
                        <i class="fas fa-sliders-h w-4 text-emerald-400"></i><span>Configuración y Metas</span>
                    </button>
                `;
            } else if (currentUser.role === 'Jefe SSL') {
                const pendSSL = db.solicitudesSSL.filter(s => s.status === 'Pendiente' || s.status === 'En Corrección').length;
                nav.innerHTML = `
                    <button onclick="navigate('ssl')" class="sidebar-btn w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-ssl">
                        <div class="flex items-center space-x-3">
                            <i class="fas fa-hard-hat w-4 text-orange-400"></i><span>${t('navSSL')}</span>
                        </div>
                        ${pendSSL > 0 ? `<span class="bg-red-500 text-white font-bold text-[10px] px-1.5 py-0.2 rounded-full">${pendSSL}</span>` : ''}
                    </button>
                    <button onclick="openModalSSL(false)" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold bg-amber-600 hover:bg-amber-700 text-white transition mt-4 shadow">
                        <i class="fas fa-plus-circle w-4"></i><span>+ Reportar Condición Insegura</span>
                    </button>
                    <button onclick="navigate('equipos')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition mt-2" id="nav-equipos">
                        <i class="fas fa-sitemap w-4 text-purple-400"></i><span>${t('navEquipos')}</span>
                    </button>
                `;
            } else if (currentUser.role === 'Tecnico') {"""

new_sidebar_code = """        function renderSidebar() {
            const nav = document.getElementById('navigationTabs');
            if (!nav || !currentUser) return;
            nav.innerHTML = '';

            const pendSolicitudes = (db.solicitudesInterdepartamentales || []).filter(s => s.status !== 'Culminada').length;
            const pendSSL = (db.solicitudesSSL || []).filter(s => s.status === 'Pendiente' || s.status === 'En Corrección').length;

            if (currentUser.role === 'Gerente') {
                nav.innerHTML = `
                    <button onclick="navigate('dashboard')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-dashboard">
                        <i class="fas fa-chart-line w-4 text-blue-400"></i><span>${t('navDashboard')}</span>
                    </button>
                    <button onclick="navigate('solicitudes-gerente')" class="sidebar-btn w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-solicitudes-gerente">
                        <div class="flex items-center space-x-3">
                            <i class="fas fa-inbox w-4 text-amber-400"></i><span>${t('navSolicitudes')}</span>
                        </div>
                        <span id="badge-solicitudes" class="${pendSolicitudes > 0 ? '' : 'hidden'} bg-amber-500 text-white font-bold text-[10px] px-1.5 py-0.2 rounded-full">${pendSolicitudes}</span>
                    </button>
                    <button onclick="navigate('cronograma-anual')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-cronograma-anual">
                        <i class="fas fa-calendar-check w-4 text-emerald-400"></i><span>${t('navCronogramaAnual')}</span>
                    </button>
                    <button onclick="navigate('ssl')" class="sidebar-btn w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-ssl">
                        <div class="flex items-center space-x-3">
                            <i class="fas fa-hard-hat w-4 text-orange-400"></i><span>${t('navSSL')}</span>
                        </div>
                        <span id="badge-ssl" class="${pendSSL > 0 ? '' : 'hidden'} bg-red-500 text-white font-bold text-[10px] px-1.5 py-0.2 rounded-full">${pendSSL}</span>
                    </button>
                    <button onclick="navigate('ots')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-ots">
                        <i class="fas fa-clipboard-list w-4 text-indigo-400"></i><span>${t('navOTs')}</span>
                    </button>
                    <button onclick="navigate('taller-externo')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-taller-externo">
                        <i class="fas fa-truck-pickup w-4 text-amber-400"></i><span>Taller Externo</span>
                    </button>
                    <button onclick="navigate('cronograma-refrigeracion')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-cronograma-refrigeracion">
                        <i class="fas fa-snowflake w-4 text-cyan-400"></i><span>${t('navRefrigeracion')}</span>
                    </button>
                    <button onclick="navigate('equipos')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-equipos">
                        <i class="fas fa-sitemap w-4 text-purple-400"></i><span>${t('navEquipos')}</span>
                    </button>
                    <button onclick="navigate('almacen')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-almacen">
                        <i class="fas fa-boxes w-4 text-yellow-400"></i><span>${t('navAlmacen')}</span>
                    </button>
                    <button onclick="navigate('salidas-materiales')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-salidas-materiales">
                        <i class="fas fa-dolly-flatbed w-4 text-amber-400"></i><span>Salida de Materiales</span>
                    </button>
                    <button onclick="navigate('proveedores')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-proveedores">
                        <i class="fas fa-truck w-4 text-teal-400"></i><span>${t('navProveedores')}</span>
                    </button>
                    <button onclick="navigate('compras')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-compras">
                        <i class="fas fa-shopping-cart w-4 text-pink-400"></i><span>${t('navCompras')}</span>
                    </button>
                    <button onclick="navigate('informes')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-informes">
                        <i class="fas fa-file-invoice w-4 text-orange-400"></i><span>${t('navInformes')}</span>
                    </button>
                    <button onclick="navigate('usuarios')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-usuarios">
                        <i class="fas fa-users-cog w-4 text-slate-400"></i><span>${t('navUsuarios')}</span>
                    </button>
                    <button onclick="openModalConfiguracionMTTR()" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition text-emerald-300" id="nav-config-mttr">
                        <i class="fas fa-sliders-h w-4 text-emerald-400"></i><span>Configuración y Metas</span>
                    </button>
                `;
            } else if (currentUser.role === 'Almacenista') {
                nav.innerHTML = `
                    <button onclick="navigate('almacen')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-almacen">
                        <i class="fas fa-boxes w-4 text-yellow-400"></i><span>${t('navAlmacen')}</span>
                    </button>
                    <button onclick="navigate('salidas-materiales')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-salidas-materiales">
                        <i class="fas fa-dolly-flatbed w-4 text-amber-400"></i><span>Salida de Materiales</span>
                    </button>
                    <button onclick="navigate('taller-externo')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-taller-externo">
                        <i class="fas fa-truck-pickup w-4 text-teal-400"></i><span>Taller Externo</span>
                    </button>
                    <button onclick="navigate('proveedores')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-proveedores">
                        <i class="fas fa-truck w-4 text-cyan-400"></i><span>${t('navProveedores')}</span>
                    </button>
                    <button onclick="navigate('compras')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-compras">
                        <i class="fas fa-shopping-cart w-4 text-pink-400"></i><span>${t('navCompras')}</span>
                    </button>
                    <button onclick="navigate('ots')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-ots">
                        <i class="fas fa-clipboard-list w-4 text-indigo-400"></i><span>Consulta de OTs</span>
                    </button>
                `;
            } else if (currentUser.role === 'Jefe SSL') {
                nav.innerHTML = `
                    <button onclick="navigate('ssl')" class="sidebar-btn w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-ssl">
                        <div class="flex items-center space-x-3">
                            <i class="fas fa-hard-hat w-4 text-orange-400"></i><span>${t('navSSL')}</span>
                        </div>
                        <span id="badge-ssl" class="${pendSSL > 0 ? '' : 'hidden'} bg-red-500 text-white font-bold text-[10px] px-1.5 py-0.2 rounded-full">${pendSSL}</span>
                    </button>
                    <button onclick="openModalSSL(false)" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold bg-amber-600 hover:bg-amber-700 text-white transition mt-4 shadow">
                        <i class="fas fa-plus-circle w-4"></i><span>+ Reportar Condición Insegura</span>
                    </button>
                    <button onclick="navigate('equipos')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition mt-2" id="nav-equipos">
                        <i class="fas fa-sitemap w-4 text-purple-400"></i><span>${t('navEquipos')} (Consulta)</span>
                    </button>
                `;
            } else if (currentUser.role === 'Tecnico') {"""

if old_sidebar_code in text:
    text = text.replace(old_sidebar_code, new_sidebar_code)
    print("[OK] renderSidebar() actualizado con rol Almacenista, Taller Externo y Badges reactivos.")

# -----------------------------------------------------------------------------
# 6. ENLACES EN NAVIGATE() Y FUNCIÓN PUEDEMODIFICAREQUIPOS()
# -----------------------------------------------------------------------------
old_navigate = """                case 'informes': renderInformesView(main); break;
                case 'usuarios': renderUsuariosView(main); break;
                case 'solicitudes-gerente': renderSolicitudesGerenteView(main); break;
                case 'mis-solicitudes': renderMisSolicitudesView(main); break;
                default: renderDashboardView(main);
            }
        }"""

new_navigate = """                case 'informes': renderInformesView(main); break;
                case 'usuarios': renderUsuariosView(main); break;
                case 'solicitudes-gerente': renderSolicitudesGerenteView(main); break;
                case 'mis-solicitudes': renderMisSolicitudesView(main); break;
                case 'taller-externo': renderTallerExternoView(main); break;
                case 'salidas-materiales': renderSalidasMaterialesView(main); break;
                default: renderDashboardView(main);
            }
            actualizarBadges();
        }

        // --- VERIFICACIÓN DE SEGURIDAD ESTRICTA: MODIFICACIÓN DE EQUIPOS/ACTIVOS ---
        // Exclusivo para Gerente de Planta y Jefe de Mantenimiento
        function puedeModificarEquipos(user) {
            if (!user) return false;
            const cargo = (user.cargo || '').toLowerCase();
            const name = (user.name || '').toLowerCase();
            const role = user.role || '';
            const depto = (user.departamento || '').toLowerCase();
            
            // Jefe de Mantenimiento
            if (cargo.includes('jefe de mantenimiento') || user.username === 'admin' || (role === 'Gerente' && !cargo.includes('planta') && !depto.includes('seguridad'))) {
                return true;
            }
            // Gerente de Planta
            if (cargo.includes('gerente de planta') || name.includes('gerente de planta') || user.username === 'gerente_planta') {
                return true;
            }
            return false;
        }"""

if old_navigate in text:
    text = text.replace(old_navigate, new_navigate)
    print("[OK] navigate() y puedeModificarEquipos() implementados.")

# Guardar progreso
with open(STATIC_INDEX, "w", encoding="utf-8") as f:
    f.write(text)
print("Archivo index.html guardado exitosamente.")

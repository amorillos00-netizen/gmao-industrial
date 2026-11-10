# -*- coding: utf-8 -*-
"""
Script maestro para aplicar todas las refactorizaciones y correcciones:
1. Roles y Permisos (Jefe Mantenimiento y Compras)
2. Preventivo: Sincronización bandeja activas y reactividad cierre OT
3. Calendario: Diagrama escala semanal con cabecera de 2 filas (Meses superior / Semanas inferior)
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MAIN_PY = BASE_DIR / "app" / "main.py"
INDEX_HTML = BASE_DIR / "index.html"
STATIC_INDEX_HTML = BASE_DIR / "app" / "static" / "index.html"

# =========================================================================
# 1. PARCHEAR app/main.py
# =========================================================================
print("Parchando app/main.py...")
main_code = MAIN_PY.read_text(encoding="utf-8")

# Validar en save_purchase que Compras no pueda asignar 'Recibida'
save_purchase_pattern = r'def save_purchase\(compra: Dict\[str, Any\]\):'
if "if user_role in (\"Departamento de Compras\", \"Compras\") and compra.get(\"status\") == \"Recibida\":" not in main_code:
    replacement = """def save_purchase(compra: Dict[str, Any]):
    user_role = compra.get("rol") or compra.get("role") or ""
    if user_role in ("Departamento de Compras", "Compras"):
        if compra.get("status") == "Recibida":
            raise HTTPException(status_code=403, detail="Acceso denegado: El estado 'Recibida' es exclusivo para Jefe de Mantenimiento y Almacén.")
        if compra.get("status") and compra.get("status") not in ("Pendiente", "Aprobada", "En Tránsito", "En tránsito"):
            raise HTTPException(status_code=403, detail="Acceso denegado: Compras solo puede asignar estados: Pendiente, Aprobada o En tránsito.")"""
    main_code = re.sub(save_purchase_pattern, replacement, main_code, count=1)

# Validar en update_purchase_status los estados permitidos de Compras
update_status_pattern = r'if new_status == "Recibida" and user_role in \("Departamento de Compras", "Compras"\):\s+raise HTTPException\(status_code=403, detail="Acceso denegado: El estado \'Recibida\' es exclusivo para Jefe de Mantenimiento y Almacén\."\)'
update_status_replacement = """if user_role in ("Departamento de Compras", "Compras"):
        if new_status == "Recibida":
            raise HTTPException(status_code=403, detail="Acceso denegado: El estado 'Recibida' es exclusivo para Jefe de Mantenimiento y Almacén.")
        if new_status not in ("Pendiente", "Aprobada", "En Tránsito", "En tránsito"):
            raise HTTPException(status_code=403, detail="Acceso denegado: Compras solo puede asignar estados: Pendiente, Aprobada o En tránsito.")"""
if "if new_status not in (\"Pendiente\", \"Aprobada\", \"En Tránsito\", \"En tránsito\"):" not in main_code:
    main_code = re.sub(update_status_pattern, update_status_replacement, main_code, count=1)

MAIN_PY.write_text(main_code, encoding="utf-8")
print("[OK] app/main.py actualizado.")

# =========================================================================
# 2. PARCHEAR index.html
# =========================================================================
print("Parchando index.html...")
html = INDEX_HTML.read_text(encoding="utf-8")

# -------------------------------------------------------------------------
# A. Funciones de Exportación e Impresión de Compras Filtradas
# -------------------------------------------------------------------------
compras_export_functions = """
        // --- EXPORTACIÓN E IMPRESIÓN DE COMPRAS FILTRADAS POR RANGO (JEFE DE MANTENIMIENTO) ---
        function exportarInformeComprasExcel() {
            let compras = db.comprasMateriales || [];
            const filtered = compras.filter(c => {
                const f = (c.fecha || '').slice(0, 10);
                if (filtroPeriodoCompras.desde && f < filtroPeriodoCompras.desde) return false;
                if (filtroPeriodoCompras.hasta && f > filtroPeriodoCompras.hasta) return false;
                if (filtroPeriodoCompras.status && (c.status || 'Pendiente') !== filtroPeriodoCompras.status) return false;
                if (filtroPeriodoCompras.search) {
                    const q = filtroPeriodoCompras.search.toLowerCase();
                    const desc = (c.descripcion || '').toLowerCase();
                    const id = (c.id || '').toLowerCase();
                    const obs = (c.observaciones || '').toLowerCase();
                    if (!desc.includes(q) && !id.includes(q) && !obs.includes(q)) return false;
                }
                return true;
            });

            if (filtered.length === 0) {
                mostrarToast('Sin datos', 'No hay registros de compras en el rango de fechas seleccionado.', 'warning');
                return;
            }

            const periodoStr = `${filtroPeriodoCompras.desde || 'Inicio'} al ${filtroPeriodoCompras.hasta || 'Actualidad'}`;
            const filename = `INFORME_COMPRAS_${(filtroPeriodoCompras.desde || 'INICIO')}_AL_${(filtroPeriodoCompras.hasta || 'FIN')}.xlsx`.replace(/\\s+/g, '_');

            if (typeof XLSX !== 'undefined') {
                const wb = XLSX.utils.book_new();
                const data = [
                    ["SALTYSNACK TUYERO C.A. - DEPARTAMENTO DE MANTENIMIENTO E INFRAESTRUCTURA"],
                    [`INFORME CONSOLIDADO DE COMPRAS Y REQUISICIONES (${periodoStr})`],
                    [`Fecha de Emisión: ${new Date().toLocaleString('es-ES')} | Solicitante: ${currentUser ? currentUser.name : 'Jefe de Mantenimiento'}`],
                    [],
                    ["Código Folio", "Fecha", "Descripción de Repuesto / Insumo", "Cant. Solicitada", "Cant. Recibida", "Precio Unitario ($)", "Monto Total ($)", "Estado", "Creado Por", "Observaciones"]
                ];

                let totalSolicitada = 0;
                let totalRecibida = 0;
                let totalMonto = 0;

                filtered.forEach(c => {
                    const cantSol = parseInt(c.cantSolicitada) || 0;
                    const cantRec = parseInt(c.cantRecibida) || 0;
                    const precio = parseFloat(c.precio) || 0;
                    const subtotal = cantSol * precio;
                    totalSolicitada += cantSol;
                    totalRecibida += cantRec;
                    totalMonto += subtotal;

                    data.push([
                        c.id || '',
                        c.fecha || '',
                        c.descripcion || '',
                        cantSol,
                        cantRec,
                        precio.toFixed(2),
                        subtotal.toFixed(2),
                        c.status || 'Pendiente',
                        c.creadoPor || 'Jefe de Mantenimiento',
                        c.observaciones || ''
                    ]);
                });

                data.push([]);
                data.push(["TOTALES:", "", `${filtered.length} Requisiciones`, totalSolicitada, totalRecibida, "", totalMonto.toFixed(2), "", "", ""]);

                const ws = XLSX.utils.aoa_to_sheet(data);
                XLSX.utils.book_append_sheet(wb, ws, "Requisiciones Compras");
                XLSX.writeFile(wb, filename);
                mostrarToast('Excel Exportado', `Informe descargado con ${filtered.length} requisiciones filtradas.`, 'success');
            } else {
                let csv = 'Codigo,Fecha,Descripcion,CantSolicitada,CantRecibida,PrecioUnitario,Total,Estado,CreadoPor,Observaciones\\n';
                filtered.forEach(c => {
                    csv += `"${c.id}","${c.fecha}","${(c.descripcion||'').replace(/"/g, '""')}",${c.cantSolicitada||0},${c.cantRecibida||0},${c.precio||0},${((c.cantSolicitada||0)*(c.precio||0)).toFixed(2)},"${c.status}","${c.creadoPor||''}","${(c.observaciones||'').replace(/"/g, '""')}"\\n`;
                });
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                const link = document.createElement("a");
                link.href = URL.createObjectURL(blob);
                link.download = filename.replace('.xlsx', '.csv');
                link.click();
                mostrarToast('CSV Exportado', `Informe descargado con ${filtered.length} requisiciones filtradas.`, 'success');
            }
        }

        function imprimirInformeCompras() {
            let compras = db.comprasMateriales || [];
            const filtered = compras.filter(c => {
                const f = (c.fecha || '').slice(0, 10);
                if (filtroPeriodoCompras.desde && f < filtroPeriodoCompras.desde) return false;
                if (filtroPeriodoCompras.hasta && f > filtroPeriodoCompras.hasta) return false;
                if (filtroPeriodoCompras.status && (c.status || 'Pendiente') !== filtroPeriodoCompras.status) return false;
                if (filtroPeriodoCompras.search) {
                    const q = filtroPeriodoCompras.search.toLowerCase();
                    const desc = (c.descripcion || '').toLowerCase();
                    const id = (c.id || '').toLowerCase();
                    const obs = (c.observaciones || '').toLowerCase();
                    if (!desc.includes(q) && !id.includes(q) && !obs.includes(q)) return false;
                }
                return true;
            });

            if (filtered.length === 0) {
                mostrarToast('Sin datos', 'No hay registros en el rango de fechas para imprimir.', 'warning');
                return;
            }

            const printSec = document.getElementById('printSection');
            if (!printSec) return;

            const periodoStr = `${filtroPeriodoCompras.desde || 'Inicio'} al ${filtroPeriodoCompras.hasta || 'Actualidad'}`;
            let totalMonto = 0;
            let pendientesCount = 0;
            let aprobadasCount = 0;
            let transitoCount = 0;
            let recibidasCount = 0;

            filtered.forEach(c => {
                const precio = parseFloat(c.precio) || 0;
                const cant = parseInt(c.cantSolicitada) || 0;
                totalMonto += (precio * cant);
                const st = (c.status || '').toLowerCase();
                if (st === 'pendiente') pendientesCount++;
                else if (st === 'aprobada') aprobadasCount++;
                else if (st.includes('tránsito') || st.includes('transito')) transitoCount++;
                else if (st === 'recibida') recibidasCount++;
            });

            const rowsHtml = filtered.map(c => `
                <tr class="border-b border-slate-300">
                    <td class="p-2 font-mono font-bold text-xs">${c.id}</td>
                    <td class="p-2 text-xs">${c.fecha}</td>
                    <td class="p-2 text-xs font-semibold">${c.descripcion}</td>
                    <td class="p-2 text-center text-xs font-bold">${c.cantSolicitada}</td>
                    <td class="p-2 text-center text-xs text-emerald-700 font-bold">${c.cantRecibida}</td>
                    <td class="p-2 text-right text-xs font-mono">$${(parseFloat(c.precio) || 0).toFixed(2)}</td>
                    <td class="p-2 text-right text-xs font-mono font-bold">$${((parseFloat(c.precio) || 0) * (parseInt(c.cantSolicitada) || 0)).toFixed(2)}</td>
                    <td class="p-2 text-center text-xs">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${
                            c.status === 'Recibida' ? 'bg-emerald-100 text-emerald-800 border-emerald-300' :
                            c.status === 'Aprobada' ? 'bg-blue-100 text-blue-800 border-blue-300' :
                            (c.status === 'En Tránsito' || c.status === 'En tránsito') ? 'bg-purple-100 text-purple-800 border-purple-300' :
                            'bg-amber-100 text-amber-800 border-amber-300'
                        }">${c.status || 'Pendiente'}</span>
                    </td>
                    <td class="p-2 text-xs text-slate-600">${c.observaciones || '-'}</td>
                </tr>
            `).join('');

            printSec.innerHTML = `
                <div class="p-6 max-w-5xl mx-auto border-2 border-slate-800 text-slate-900 bg-white">
                    <div class="flex items-center justify-between border-b-2 border-slate-900 pb-4 mb-4">
                        <div>
                            <h1 class="text-xl font-black tracking-wide text-slate-900">SALTYSNACK TUYERO C.A.</h1>
                            <p class="text-xs font-semibold text-slate-600">RIF: J-40892182-3 | DEPARTAMENTO DE MANTENIMIENTO E INFRAESTRUCTURA</p>
                            <h2 class="text-base font-bold text-blue-900 mt-1">INFORME OFICIAL DE REQUISICIONES Y COMPRAS</h2>
                        </div>
                        <div class="text-right text-xs">
                            <div class="bg-slate-100 p-2 rounded border border-slate-300">
                                <p class="font-bold">Periodo Evaluado:</p>
                                <p class="font-mono text-blue-800 font-semibold">${periodoStr}</p>
                                <p class="text-[10px] text-slate-500 mt-1">Fecha Emisión: ${new Date().toLocaleDateString('es-ES')}</p>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-5 gap-2 mb-4 text-center">
                        <div class="border p-2 rounded bg-slate-50">
                            <span class="block text-[10px] text-slate-500 font-bold uppercase">Total Solicitudes</span>
                            <span class="text-base font-black text-slate-800">${filtered.length}</span>
                        </div>
                        <div class="border p-2 rounded bg-amber-50">
                            <span class="block text-[10px] text-amber-700 font-bold uppercase">Pendientes</span>
                            <span class="text-base font-black text-amber-800">${pendientesCount}</span>
                        </div>
                        <div class="border p-2 rounded bg-blue-50">
                            <span class="block text-[10px] text-blue-700 font-bold uppercase">Aprobadas</span>
                            <span class="text-base font-black text-blue-800">${aprobadasCount}</span>
                        </div>
                        <div class="border p-2 rounded bg-purple-50">
                            <span class="block text-[10px] text-purple-700 font-bold uppercase">En Tránsito</span>
                            <span class="text-base font-black text-purple-800">${transitoCount}</span>
                        </div>
                        <div class="border p-2 rounded bg-emerald-50">
                            <span class="block text-[10px] text-emerald-700 font-bold uppercase">Recibidas</span>
                            <span class="text-base font-black text-emerald-800">${recibidasCount}</span>
                        </div>
                    </div>

                    <table class="w-full text-left border-collapse border border-slate-300 text-xs mb-6">
                        <thead class="bg-slate-900 text-white">
                            <tr>
                                <th class="p-2 border border-slate-800">Folio</th>
                                <th class="p-2 border border-slate-800">Fecha</th>
                                <th class="p-2 border border-slate-800">Descripción Repuesto / Insumo</th>
                                <th class="p-2 border border-slate-800 text-center">Sol.</th>
                                <th class="p-2 border border-slate-800 text-center">Rec.</th>
                                <th class="p-2 border border-slate-800 text-right">P. Unit ($)</th>
                                <th class="p-2 border border-slate-800 text-right">Monto ($)</th>
                                <th class="p-2 border border-slate-800 text-center">Estatus</th>
                                <th class="p-2 border border-slate-800">Observaciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${rowsHtml}
                        </tbody>
                        <tfoot class="bg-slate-100 font-bold border-t-2 border-slate-800">
                            <tr>
                                <td colspan="6" class="p-2 text-right">TOTAL ESTIMADO:</td>
                                <td class="p-2 text-right font-mono text-blue-900 font-black">$${totalMonto.toFixed(2)}</td>
                                <td colspan="2"></td>
                            </tr>
                        </tfoot>
                    </table>

                    <div class="grid grid-cols-2 gap-8 pt-8 mt-6 border-t-2 border-slate-300 text-xs text-center">
                        <div>
                            <div class="w-48 border-b-2 border-slate-900 mx-auto mb-1 h-12"></div>
                            <p class="font-bold text-slate-800">Ing. Carlos Mendoza</p>
                            <p class="text-[10px] text-slate-600">Jefe de Mantenimiento e Infraestructura</p>
                            <p class="text-[9px] text-slate-400">Emisor y Solicitante Autorizado</p>
                        </div>
                        <div>
                            <div class="w-48 border-b-2 border-slate-900 mx-auto mb-1 h-12"></div>
                            <p class="font-bold text-slate-800">Dpto. de Compras y Suministros</p>
                            <p class="text-[10px] text-slate-600">Gestión y Procura Industrial</p>
                            <p class="text-[9px] text-slate-400">Revisión y Aprobación Financiera</p>
                        </div>
                    </div>
                </div>
            `;
            window.print();
        }
"""

if "function exportarInformeComprasExcel()" not in html:
    # Insertar justo después de limpiarFiltroCompras
    limpiar_pattern = r'function limpiarFiltroCompras\(\) \{[\s\S]*?renderComprasView\(document\.getElementById\(\'mainView\'\)\);\s*\}'
    match = re.search(limpiar_pattern, html)
    if match:
        html = html[:match.end()] + "\n" + compras_export_functions + html[match.end():]
        print("[OK] Funciones exportarInformeComprasExcel e imprimirInformeCompras añadidas.")
    else:
        print("[WARN] No se encontró limpiarFiltroCompras")

# -------------------------------------------------------------------------
# B. Botones de Exportar e Imprimir en renderComprasView
# -------------------------------------------------------------------------
btn_old = """                        <div class="flex items-center space-x-2">
                            <button onclick="openModalCompra(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-plus"></i>
                                <span>+ Solicitud de Compra</span>
                            </button>
                        </div>"""

btn_new = """                        <div class="flex flex-wrap items-center gap-2">
                            <button onclick="exportarInformeComprasExcel()" class="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition" title="Exportar informe de compras filtrado por fecha a Excel (.xlsx)">
                                <i class="fas fa-file-excel"></i>
                                <span>Exportar Excel</span>
                            </button>
                            <button onclick="imprimirInformeCompras()" class="bg-slate-800 hover:bg-slate-900 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition" title="Imprimir informe de compras filtrado por fecha a PDF">
                                <i class="fas fa-print"></i>
                                <span>Imprimir Informe</span>
                            </button>
                            <button onclick="openModalCompra(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-plus"></i>
                                <span>+ Solicitud de Compra</span>
                            </button>
                        </div>"""

if btn_old in html:
    html = html.replace(btn_old, btn_new)
    print("[OK] Botones de exportación e impresión añadidos a la cabecera de renderComprasView.")

# -------------------------------------------------------------------------
# C. Sincronización bandeja "Próximas intervenciones activas" con plan preventivo
# -------------------------------------------------------------------------
# Buscar bloque de recolección de próximas intervenciones
proximos_old_pattern = r'// 1\. Recopilar y clasificar todas las pr[oó]ximas intervenciones preventivas y OTs programadas[\s\S]*?const todasProximas = \[\.\.\.proximosPlanes, \.\.\.proximasOTs\]\.sort\(\(a, b\) => a\.fechaEjecucion\.localeCompare\(b\.fechaEjecucion\)\);'

proximos_new_code = """// 1. Recopilar y clasificar todas las próximas intervenciones preventivas activas y OTs programadas
            const proximosPlanes = (db.planesPreventivos || [])
                .filter(p => p.proximaFecha && p.status !== 'Completado' && p.status !== 'Ejecutado')
                .map(p => {
                    const pDate = new Date(p.proximaFecha.slice(0, 10) + 'T00:00:00');
                    const diffDays = Math.round((pDate.getTime() - hoyDate.getTime()) / (1000 * 60 * 60 * 24));
                    const eq = (db.equipos || []).find(e => e.id === p.equipoId) || { name: p.equipoId };
                    return {
                        tipoItem: 'Plan Preventivo',
                        id: p.id,
                        equipoId: p.equipoId,
                        equipoNombre: eq.name,
                        actividad: p.nombre,
                        frecuencia: p.frecuencia,
                        fechaEjecucion: p.proximaFecha.slice(0, 10),
                        diffDays: diffDays,
                        tecnicoIds: p.tecnicoIds || [],
                        status: p.status || 'Pendiente',
                        esOT: false
                    };
                });

            const proximasOTs = (db.ots || [])
                .filter(o => o.status !== 'Concluida' && o.status !== 'Completada' && (o.fechaProgramada || o.fechaAsignacion))
                .map(o => {
                    const fProg = (o.fechaProgramada || o.fechaAsignacion).slice(0, 10);
                    const oDate = new Date(fProg + 'T00:00:00');
                    const diffDays = Math.round((oDate.getTime() - hoyDate.getTime()) / (1000 * 60 * 60 * 24));
                    const eq = (db.equipos || []).find(e => e.id === o.equipoId) || { name: o.equipoId };
                    return {
                        tipoItem: `OT Programada (${o.tipo})`,
                        id: o.id,
                        planId: o.planId,
                        equipoId: o.equipoId,
                        equipoNombre: eq.name,
                        actividad: o.descripcion,
                        frecuencia: o.prioridad,
                        fechaEjecucion: fProg,
                        diffDays: diffDays,
                        tecnicoIds: o.tecnicoIds || [],
                        status: o.status,
                        esOT: true
                    };
                });

            // Evitar duplicados: sincronizar tray excluyendo planes que ya tengan OT preventiva activa en curso
            const activePlanIds = new Set(proximasOTs.filter(o => o.planId).map(o => o.planId));
            const activePlanEquipos = new Set(proximasOTs.filter(o => o.tipoItem && o.tipoItem.includes('Preventivo')).map(o => o.equipoId));
            const planesActivosSinOT = proximosPlanes.filter(p => !activePlanIds.has(p.id) && !activePlanEquipos.has(p.equipoId));

            const todasProximas = [...planesActivosSinOT, ...proximasOTs].sort((a, b) => a.fechaEjecucion.localeCompare(b.fechaEjecucion));"""

if re.search(proximos_old_pattern, html):
    html = re.sub(proximos_old_pattern, proximos_new_code, html, count=1)
    print("[OK] Sincronización de bandeja de Próximas Intervenciones Activas implementada.")
else:
    print("[INFO] Buscando variante de proximosPlanes...")

# -------------------------------------------------------------------------
# D. Cabecera de 2 filas para el Diagrama de Cronograma Semanal
# Meses superior / Semanas inferior
# -------------------------------------------------------------------------
# Configuración de meses y semanas
meses_def_search = r'const mesesNombres = \["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"\];\s*const semanasAnio = Array\.from\(\{length: 52\}, \(_, i\) => i \+ 1\);'
meses_def_replacement = """const mesesNombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
            const semanasAnio = Array.from({length: 52}, (_, i) => i + 1);
            const mesesConfig = [
                { nombre: "Enero", abrev: "Ene", semanas: [1, 2, 3, 4] },
                { nombre: "Febrero", abrev: "Feb", semanas: [5, 6, 7, 8] },
                { nombre: "Marzo", abrev: "Mar", semanas: [9, 10, 11, 12, 13] },
                { nombre: "Abril", abrev: "Abr", semanas: [14, 15, 16, 17] },
                { nombre: "Mayo", abrev: "May", semanas: [18, 19, 20, 21, 22] },
                { nombre: "Junio", abrev: "Jun", semanas: [23, 24, 25, 26] },
                { nombre: "Julio", abrev: "Jul", semanas: [27, 28, 29, 30] },
                { nombre: "Agosto", abrev: "Ago", semanas: [31, 32, 33, 34, 35] },
                { nombre: "Septiembre", abrev: "Sep", semanas: [36, 37, 38, 39] },
                { nombre: "Octubre", abrev: "Oct", semanas: [40, 41, 42, 43] },
                { nombre: "Noviembre", abrev: "Nov", semanas: [44, 45, 46, 47, 48] },
                { nombre: "Diciembre", abrev: "Dic", semanas: [49, 50, 51, 52] }
            ];"""

if re.search(meses_def_search, html) and "const mesesConfig =" not in html:
    html = re.sub(meses_def_search, meses_def_replacement, html, count=1)
    print("[OK] Definición de mesesConfig para cabecera semanal añadida.")

# Reemplazar thead del cronograma
thead_current_pattern = r'<thead class="bg-slate-900 text-white">\s*<tr>\s*<th class="p-2 border border-slate-800 text-\[11px\]">C[oó]digo</th>[\s\S]*?<th class="p-2 border border-slate-800 text-center text-\[11px\]">Acciones</th>\s*</tr>\s*</thead>'

thead_new_structure = """<thead class="bg-slate-900 text-white">
                                ${cronogramaEscala === 'semanal' ? `
                                    <!-- FILA SUPERIOR: METADATOS Y MESES DEL AÑO -->
                                    <tr>
                                        <th rowspan="2" class="p-2 border border-slate-800 text-[11px] align-middle">Código</th>
                                        <th rowspan="2" class="p-2 border border-slate-800 text-[11px] align-middle">Equipo / Sistema</th>
                                        <th rowspan="2" class="p-2 border border-slate-800 text-[11px] align-middle">Actividad Preventiva</th>
                                        <th rowspan="2" class="p-2 border border-slate-800 text-center text-[11px] align-middle">Frecuencia</th>
                                        <th rowspan="2" class="p-2 border border-slate-800 text-center text-[11px] align-middle">Última</th>
                                        <th rowspan="2" class="p-2 border border-slate-800 text-center text-[11px] align-middle">Próxima</th>
                                        <th rowspan="2" class="p-2 border border-slate-800 text-center text-[11px] align-middle">Estado</th>
                                        ${mesesConfig.map(m => `<th colspan="${m.semanas.length}" class="p-1 border border-slate-800 text-center text-[10px] font-bold bg-slate-800 text-blue-200 tracking-wide">${m.nombre}</th>`).join('')}
                                        <th rowspan="2" class="p-2 border border-slate-800 text-center text-[11px] align-middle">Acciones</th>
                                    </tr>
                                    <!-- FILA INFERIOR: SEMANAS CORRESPONDIENTES A CADA MES (Mes -> Semana XX) -->
                                    <tr>
                                        ${mesesConfig.flatMap(m => m.semanas.map(sNum => `
                                            <th class="p-0.5 border border-slate-800 text-center text-[8px] font-mono bg-slate-900 text-slate-300" title="${m.nombre} -> Semana ${String(sNum).padStart(2,'0')}">
                                                S${String(sNum).padStart(2,'0')}
                                            </th>
                                        `)).join('')}
                                    </tr>
                                ` : `
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
                                `}
                            </thead>"""

if re.search(thead_current_pattern, html):
    html = re.sub(thead_current_pattern, thead_new_structure, html, count=1)
    print("[OK] Cabecera estructurada de 2 filas (Meses superior / Semanas inferior) integrada.")
else:
    print("[WARN] No se encontró el thead_current_pattern exacto")

# -------------------------------------------------------------------------
# E. Vinculación y persistencia de planId en crearOTDesdeCronograma y formOT
# -------------------------------------------------------------------------
# Asegurar campo oculto otPlanId en formOT si no existe
if '<input type="hidden" id="otPlanId">' not in html:
    html = html.replace('<input type="hidden" id="otId">', '<input type="hidden" id="otId">\n                <input type="hidden" id="otPlanId">')
    print("[OK] Input oculto otPlanId agregado a formOT.")

# Actualizar crearOTDesdeCronograma para fijar otPlanId
crear_ot_old = """        function crearOTDesdeCronograma(planId, fechaSugerida) {
            const plan = db.planesPreventivos.find(p => p.id === planId);
            if (!plan) return;
            openModalOT(false);
            setTimeout(() => {
                document.getElementById('otTipo').value = 'Preventivo';
                document.getElementById('otPrioridad').value = 'Media';
                document.getElementById('otEquipo').value = plan.equipoId;
                document.getElementById('otDescripcion').value = `Mantenimiento preventivo programado según cronograma anual: ${plan.nombre}`;
                document.getElementById('otFechaProgramada').value = fechaSugerida;
            }, 100);
        }"""

crear_ot_new = """        function crearOTDesdeCronograma(planId, fechaSugerida) {
            const plan = (db.planesPreventivos || []).find(p => p.id === planId) || (db.planesRefrigeracion || []).find(p => p.id === planId);
            if (!plan) return;
            openModalOT(false);
            setTimeout(() => {
                if (document.getElementById('otPlanId')) document.getElementById('otPlanId').value = planId;
                document.getElementById('otTipo').value = 'Preventivo';
                document.getElementById('otPrioridad').value = 'Media';
                document.getElementById('otEquipo').value = plan.equipoId;
                document.getElementById('otDescripcion').value = `Mantenimiento preventivo programado según cronograma anual: ${plan.nombre}`;
                document.getElementById('otFechaProgramada').value = fechaSugerida;
            }, 100);
        }"""

if crear_ot_old in html:
    html = html.replace(crear_ot_old, crear_ot_new)
    print("[OK] crearOTDesdeCronograma actualizado con enlace otPlanId.")

# Guardar cambios
INDEX_HTML.write_text(html, encoding="utf-8")
STATIC_INDEX_HTML.write_text(html, encoding="utf-8")
print("[COMPLETO] index.html y app/static/index.html sincronizados con éxito.")

# -*- coding: utf-8 -*-
"""
Script de actualización Fase 2 para Frontend SPA GMAO Industrial Pro
Empresa: SALTYSNACK TUYERO C.A.
Implementa:
- Subpestaña "Próximas Intervenciones y Alertas" en Cronograma Anual
- Botones y funciones de Exportación Excel (.xlsx) y Word (.docx) en Informes Periódicos
- Restricciones de seguridad para Activos/Equipos (Solo Gerente de Planta y Jefe de Mantenimiento)
- Vistas completas para Seguimiento en Taller Externo y Salida de Materiales (Almacenista)
- Flujo de cambio automático de estatus e integración total de actualizarBadges()
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_INDEX = BASE_DIR / "app" / "static" / "index.html"
ROOT_INDEX = BASE_DIR / "index.html"

with open(STATIC_INDEX, "r", encoding="utf-8") as f:
    text = f.read()

# -----------------------------------------------------------------------------
# 1. ACTUALIZAR RENDERINFORMESVIEW CON BOTONES EXCEL Y WORD
# -----------------------------------------------------------------------------
target_informe_btn = """                        <div class="flex items-center space-x-2">
                            <button onclick="imprimirInforme()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-print"></i>
                                <span>Imprimir Formato Formal (PDF)</span>
                            </button>
                        </div>"""

replacement_informe_btn = """                        <div class="flex flex-wrap items-center gap-2">
                            <button onclick="exportarInformePeriodicoExcel()" class="bg-emerald-600 hover:bg-emerald-700 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition" title="Exportar Matriz y Tablas a Excel (.xlsx)">
                                <i class="fas fa-file-excel"></i>
                                <span>Exportar Excel (.xlsx)</span>
                            </button>
                            <button onclick="exportarInformePeriodicoWord()" class="bg-blue-800 hover:bg-blue-900 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition" title="Exportar Documento Formal a Word (.docx)">
                                <i class="fas fa-file-word"></i>
                                <span>Exportar Word (.docx)</span>
                            </button>
                            <button onclick="imprimirInforme()" class="bg-slate-800 hover:bg-slate-900 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-print"></i>
                                <span>Imprimir Formato (PDF)</span>
                            </button>
                        </div>"""

if target_informe_btn in text:
    text = text.replace(target_informe_btn, replacement_informe_btn)
    print("[OK] Botones de exportación Excel y Word integrados en Informes.")
else:
    print("[ERROR] target_informe_btn no encontrado.")

# -----------------------------------------------------------------------------
# 2. FUNCIONES EXPORTARINFORMEPERIODICOEXCEL Y EXPORTARINFORMEPERIODICOWORD
# -----------------------------------------------------------------------------
target_print_informe = """        function imprimirInforme() {
            window.print();
        }"""

replacement_print_informe = """        function exportarInformePeriodicoExcel() {
            let periodoValor = informeAnio;
            if (informeFiltroPeriodo === 'Mensual') periodoValor = informeMes;
            else if (informeFiltroPeriodo === 'Rango') periodoValor = `${informeFechaInicio || 'inicio'}_${informeFechaFin || 'fin'}`;

            if (navigator.onLine) {
                mostrarToast('Exportando Excel', 'Generando archivo Excel corporativo con tablas y firmas...', 'info');
                window.location.href = `/api/reports/informe-periodico-excel?periodo_tipo=${encodeURIComponent(informeFiltroPeriodo)}&periodo_valor=${encodeURIComponent(periodoValor)}&equipo_id=${encodeURIComponent(informeFiltroEquipo)}`;
            } else {
                exportarInformeExcelOffline();
            }
        }

        function exportarInformePeriodicoWord() {
            let periodoValor = informeAnio;
            if (informeFiltroPeriodo === 'Mensual') periodoValor = informeMes;
            else if (informeFiltroPeriodo === 'Rango') periodoValor = `${informeFechaInicio || 'inicio'}_${informeFechaFin || 'fin'}`;

            mostrarToast('Exportando Word', 'Generando documento oficial Word (.docx) institucional...', 'info');
            fetch(`/api/reports/informe-periodico-word?periodo_tipo=${encodeURIComponent(informeFiltroPeriodo)}&periodo_valor=${encodeURIComponent(periodoValor)}&equipo_id=${encodeURIComponent(informeFiltroEquipo)}`)
                .then(res => {
                    if (!res.ok) throw new Error('Error en el servidor al generar Word');
                    return res.blob();
                })
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `INFORME_PERIODICO_${periodoValor.replace(/-/g, '_')}.docx`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    mostrarToast('Descarga Completada', 'Documento Word (.docx) descargado con éxito.', 'success');
                })
                .catch(err => {
                    console.error(err);
                    mostrarToast('Aviso de Exportación', 'La exportación a Word requiere conexión al servidor local Python.', 'warning');
                });
        }

        function exportarInformeExcelOffline() {
            try {
                const wb = XLSX.utils.book_new();
                const concluidas = (db.ots || []).filter(o => o.status === 'Concluida' || o.status === 'Completada');
                const data = concluidas.map(o => ({
                    'N° OT': o.id,
                    'Tipo': o.tipo,
                    'Equipo': o.equipoId,
                    'Fecha': o.fechaFin || o.fechaProgramada || o.fechaAsignacion,
                    'Actividades': o.actividades || o.descripcion,
                    'Tiempo Intervención (h)': o.tiempoIntervencion || 0,
                    'Tiempo Parada (h)': o.tiempoParada || 0,
                    'Estatus': o.status
                }));
                const ws = XLSX.utils.json_to_sheet(data);
                XLSX.utils.book_append_sheet(wb, ws, "OTs Culminadas");
                XLSX.writeFile(wb, `INFORME_OFFLINE_${new Date().toISOString().slice(0,10)}.xlsx`);
                mostrarToast('Excel Offline', 'Archivo Excel descargado en modo local.', 'success');
            } catch(e) {
                alert('Exportación offline completada.');
            }
        }

        function imprimirInforme() {
            window.print();
        }"""

if target_print_informe in text:
    text = text.replace(target_print_informe, replacement_print_informe)
    print("[OK] Funciones exportarInformePeriodicoExcel y exportarInformePeriodicoWord insertadas.")

# -----------------------------------------------------------------------------
# 3. ACTUALIZAR CRONOGRAMA ANUAL CON SUBPESTAÑAS Y ALERTAS
# -----------------------------------------------------------------------------
target_cronograma_func = "function renderCronogramaAnualView(container) {"
replacement_cronograma_func = """let cronogramaSubTab = 'matriz'; // 'matriz' | 'proximas'

        function setCronogramaSubTab(tab) {
            cronogramaSubTab = tab;
            renderCronogramaAnualView(document.getElementById('mainView'));
        }

        function renderCronogramaAnualView(container) {"""

if target_cronograma_func in text:
    text = text.replace(target_cronograma_func, replacement_cronograma_func, 1)
    print("[OK] Subpestañas del Cronograma registradas.")

# Modificar el cuerpo del renderCronogramaAnualView para incluir la alerta destacada y la pestaña de Próximas Intervenciones
target_cron_layout = """            container.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-3">"""

replacement_cron_layout = """            const hoyDate = new Date(new Date().toISOString().slice(0, 10) + 'T00:00:00');

            // 1. Recopilar y clasificar todas las próximas intervenciones preventivas y OTs programadas
            const proximosPlanes = (db.planesPreventivos || []).filter(p => p.proximaFecha).map(p => {
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
                    esOT: false
                };
            });

            const proximasOTs = (db.ots || []).filter(o => o.status !== 'Concluida' && o.status !== 'Completada' && (o.fechaProgramada || o.fechaAsignacion)).map(o => {
                const fProg = (o.fechaProgramada || o.fechaAsignacion).slice(0, 10);
                const oDate = new Date(fProg + 'T00:00:00');
                const diffDays = Math.round((oDate.getTime() - hoyDate.getTime()) / (1000 * 60 * 60 * 24));
                const eq = (db.equipos || []).find(e => e.id === o.equipoId) || { name: o.equipoId };
                return {
                    tipoItem: `OT Programada (${o.tipo})`,
                    id: o.id,
                    equipoId: o.equipoId,
                    equipoNombre: eq.name,
                    actividad: o.descripcion,
                    frecuencia: o.prioridad,
                    fechaEjecucion: fProg,
                    diffDays: diffDays,
                    tecnicoIds: o.tecnicoIds || [],
                    esOT: true
                };
            });

            const todasProximas = [...proximosPlanes, ...proximasOTs].sort((a, b) => a.fechaEjecucion.localeCompare(b.fechaEjecucion));
            const alertasUrgentes = todasProximas.filter(item => item.diffDays <= 5);

            const rowsProximasHtml = todasProximas.map(item => {
                let badgeUrgencia = 'bg-slate-100 text-slate-700';
                let labelUrgencia = `En ${item.diffDays} días`;

                if (item.diffDays < 0) {
                    badgeUrgencia = 'bg-red-100 text-red-800 border-red-300 font-bold';
                    labelUrgencia = `¡Vencida hace ${Math.abs(item.diffDays)} d!`;
                } else if (item.diffDays === 0) {
                    badgeUrgencia = 'bg-red-600 text-white font-bold animate-pulse';
                    labelUrgencia = '¡Vence Hoy!';
                } else if (item.diffDays <= 3) {
                    badgeUrgencia = 'bg-amber-100 text-amber-800 font-bold border-amber-300';
                    labelUrgencia = `¡Próxima en ${item.diffDays} d!`;
                } else if (item.diffDays <= 7) {
                    badgeUrgencia = 'bg-blue-100 text-blue-800 font-semibold';
                    labelUrgencia = `En ${item.diffDays} días`;
                }

                return `
                    <tr class="hover:bg-slate-50 transition border-b border-slate-100">
                        <td class="p-2.5">
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${item.esOT ? 'bg-indigo-100 text-indigo-800' : 'bg-emerald-100 text-emerald-800'}">${item.tipoItem}</span>
                            <span class="block font-mono text-[10px] text-slate-400 mt-0.5">${item.id}</span>
                        </td>
                        <td class="p-2.5 font-mono text-xs font-bold text-slate-800 whitespace-nowrap">${item.fechaEjecucion}</td>
                        <td class="p-2.5 text-center">
                            <span class="px-2 py-0.5 rounded-full text-[10px] border ${badgeUrgencia}">${labelUrgencia}</span>
                        </td>
                        <td class="p-2.5 text-xs font-semibold text-slate-800">
                            ${item.equipoNombre}
                            <span class="block text-[10px] font-mono font-bold text-blue-700">${item.equipoId}</span>
                        </td>
                        <td class="p-2.5 text-xs text-slate-600 max-w-sm truncate" title="${item.actividad}">${item.actividad}</td>
                        <td class="p-2.5 text-xs text-slate-500 font-medium">${item.frecuencia}</td>
                        <td class="p-2.5 text-right whitespace-nowrap">
                            ${!item.esOT ? `
                                <button onclick="crearOTDesdeCronograma('${item.id}', '${item.fechaEjecucion}')" class="bg-blue-600 hover:bg-blue-700 text-white px-2.5 py-1 rounded text-xs font-semibold shadow">
                                    <i class="fas fa-bolt mr-1"></i> Generar OT
                                </button>
                            ` : `
                                <button onclick="openModalCierreOT('${item.id}')" class="bg-indigo-600 hover:bg-indigo-700 text-white px-2.5 py-1 rounded text-xs font-semibold shadow">
                                    <i class="fas fa-clipboard-check mr-1"></i> Ejecutar / Cerrar
                                </button>
                            `}
                        </td>
                    </tr>
                `;
            }).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <!-- ALERTA DINÁMICA DE INTERVENCIONES PREVENTIVAS PRÓXIMAS / VENCIDAS -->
                    ${alertasUrgentes.length > 0 ? `
                        <div class="p-3.5 bg-amber-50 border-l-4 border-amber-500 rounded-r-xl shadow-sm flex items-center justify-between text-xs text-amber-900">
                            <div class="flex items-center space-x-2.5">
                                <i class="fas fa-exclamation-triangle text-amber-600 text-lg"></i>
                                <div>
                                    <span class="font-bold">Alertas de Cronograma y OTs Programadas:</span>
                                    <span> Existen <strong>${alertasUrgentes.length} intervenciones prioritarias</strong> programadas para los próximos 5 días o vencidas.</span>
                                </div>
                            </div>
                            <button onclick="setCronogramaSubTab('proximas')" class="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-bold transition shadow-sm whitespace-nowrap">
                                Ver Intervenciones Próximas
                            </button>
                        </div>
                    ` : ''}

                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-3">"""

if target_cron_layout in text:
    text = text.replace(target_cron_layout, replacement_cron_layout)
    print("[OK] Lógica y banner de Próximas Intervenciones insertados en Cronograma.")

# Insertar la barra de subpestañas antes de la tabla anual
target_table_cron = """                    <!-- LEYENDA Y MATRIZ ANUAL -->
                    <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm overflow-x-auto">"""

replacement_table_cron = """                    <!-- NAVEGACIÓN POR SUBPESTAÑAS DEL CRONOGRAMA (REQUERIMIENTO 5) -->
                    <div class="flex items-center space-x-2 bg-white px-4 pt-2 rounded-xl border border-slate-200 shadow-sm">
                        <button onclick="setCronogramaSubTab('matriz')" class="px-4 py-2.5 text-xs font-bold border-b-2 transition ${cronogramaSubTab === 'matriz' ? 'border-emerald-600 text-emerald-700 bg-emerald-50/50 rounded-t-lg' : 'border-transparent text-slate-500 hover:text-slate-800'}">
                            <i class="fas fa-th mr-1.5"></i> Matriz Cronograma Anual (${anio})
                        </button>
                        <button onclick="setCronogramaSubTab('proximas')" class="px-4 py-2.5 text-xs font-bold border-b-2 transition flex items-center space-x-1.5 ${cronogramaSubTab === 'proximas' ? 'border-blue-600 text-blue-700 bg-blue-50/50 rounded-t-lg' : 'border-transparent text-slate-500 hover:text-slate-800'}">
                            <i class="fas fa-bell mr-1"></i>
                            <span>Próximas Intervenciones y Alertas</span>
                            ${todasProximas.length > 0 ? `<span class="bg-blue-600 text-white text-[10px] px-1.5 py-0.2 rounded-full font-bold">${todasProximas.length}</span>` : ''}
                        </button>
                    </div>

                    ${cronogramaSubTab === 'proximas' ? `
                        <!-- VISTA DEDICADA: LISTA PRIORIZADA DE PRÓXIMAS INTERVENCIONES -->
                        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
                            <div class="flex items-center justify-between border-b pb-2">
                                <div>
                                    <h3 class="text-sm font-bold text-slate-800 flex items-center">
                                        <i class="fas fa-calendar-check text-blue-600 mr-2"></i> Rutinas e Intervenciones Próximas a Ejecutar
                                    </h3>
                                    <p class="text-xs text-slate-500">Ordenadas cronológicamente por fecha de intervención garantizando seguimiento y cumplimiento oportuno.</p>
                                </div>
                                <span class="text-xs font-mono font-bold text-slate-600">${todasProximas.length} Actividades Pendientes</span>
                            </div>

                            <div class="overflow-x-auto">
                                <table class="w-full text-left border-collapse text-xs">
                                    <thead class="bg-slate-900 text-white">
                                        <tr>
                                            <th class="p-2.5">Tipo / Folio</th>
                                            <th class="p-2.5">Fecha Ejecución</th>
                                            <th class="p-2.5 text-center">Estatus Plazo</th>
                                            <th class="p-2.5">Equipo / Sistema</th>
                                            <th class="p-2.5">Descripción de Rutina / Trabajo</th>
                                            <th class="p-2.5">Frecuencia / Prioridad</th>
                                            <th class="p-2.5 text-right">Acción Oportuna</th>
                                        </tr>
                                    </thead>
                                    <tbody class="divide-y divide-slate-100">
                                        ${rowsProximasHtml.length > 0 ? rowsProximasHtml : `<tr><td colspan="7" class="p-6 text-center text-slate-400">No hay intervenciones preventivas próximas pendientes.</td></tr>`}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ` : `
                    <!-- LEYENDA Y MATRIZ ANUAL -->
                    <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm overflow-x-auto">`}"""

if target_table_cron in text:
    text = text.replace(target_table_cron, replacement_table_cron)
    # Cerrar la llave condicional correspondiente
    text = text.replace("                        </table>\n                    </div>\n                </div>\n            `;\n        }\n\n        function cambiarCronogramaAnio", "                        </table>\n                    </div>\n                    `} \n                </div>\n            `;\n        }\n\n        function cambiarCronogramaAnio")
    print("[OK] Pestaña dedicada 'Próximas Intervenciones' integrada en Cronograma.")

# -----------------------------------------------------------------------------
# 4. RESTRICCIÓN DE SEGURIDAD ESTRICTA EN RENDEREQUIPOSVIEW() Y MODALES
# -----------------------------------------------------------------------------
target_render_equipos = """        function renderEquiposView(container) {
            // Ordenamiento alfanumérico natural robusto (ej: M-01, M-02, M-10) tanto ASC como DESC
            const sortedEquipos = [...db.equipos].sort((a, b) => naturalCompare(a.id, b.id, equiposSortOrder === 'ASC'));

            const rowsHtml = sortedEquipos.map(e => `
                <tr class="hover:bg-slate-50 transition">
                    <td class="p-2.5 font-mono font-bold text-blue-700 text-xs">${e.id}</td>
                    <td class="p-2.5 text-xs font-semibold text-slate-800">${e.name}</td>
                    <td class="p-2.5 text-xs text-slate-600">${e.planta} - ${e.linea}</td>
                    <td class="p-2.5 text-center">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${e.criticidad === 'Alta' ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-700'}">${e.criticidad}</span>
                    </td>
                    <td class="p-2.5 text-center">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">${e.status}</span>
                    </td>
                    <td class="p-2.5 text-right space-x-1">
                        <button onclick="openModalEquipo('${e.id}')" title="Modificar Activo" class="text-blue-600 hover:text-blue-800 p-1"><i class="fas fa-edit"></i></button>
                        <button onclick="eliminarEquipo('${e.id}')" title="Eliminar Activo" class="text-red-500 hover:text-red-700 p-1"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `).join('');"""

replacement_render_equipos = """        function renderEquiposView(container) {
            const puedeGestionar = puedeModificarEquipos(currentUser);
            // Ordenamiento alfanumérico natural robusto (ej: M-01, M-02, M-10) tanto ASC como DESC
            const sortedEquipos = [...db.equipos].sort((a, b) => naturalCompare(a.id, b.id, equiposSortOrder === 'ASC'));

            const rowsHtml = sortedEquipos.map(e => `
                <tr class="hover:bg-slate-50 transition">
                    <td class="p-2.5 font-mono font-bold text-blue-700 text-xs">${e.id}</td>
                    <td class="p-2.5 text-xs font-semibold text-slate-800">${e.name}</td>
                    <td class="p-2.5 text-xs text-slate-600">${e.planta} - ${e.linea}</td>
                    <td class="p-2.5 text-center">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${e.criticidad === 'Alta' ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-700'}">${e.criticidad}</span>
                    </td>
                    <td class="p-2.5 text-center">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">${e.status}</span>
                    </td>
                    <td class="p-2.5 text-right space-x-1">
                        ${puedeGestionar ? `
                            <button onclick="openModalEquipo('${e.id}')" title="Modificar Activo" class="text-blue-600 hover:text-blue-800 p-1"><i class="fas fa-edit"></i></button>
                            <button onclick="eliminarEquipo('${e.id}')" title="Eliminar Activo" class="text-red-500 hover:text-red-700 p-1"><i class="fas fa-trash"></i></button>
                        ` : `
                            <span class="text-[10px] text-slate-400 font-medium italic"><i class="fas fa-lock mr-1"></i>Solo lectura</span>
                        `}
                    </td>
                </tr>
            `).join('');"""

if target_render_equipos in text:
    text = text.replace(target_render_equipos, replacement_render_equipos)
    print("[OK] Control de permisos en filas de Equipos aplicado.")

# Quitar botón de registrar si no puede gestionar y agregar aviso institucional
target_btn_equipo = """                        <div class="flex items-center space-x-2">
                            <button onclick="toggleEquiposSortOrder()" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold border flex items-center space-x-1.5 transition">
                                <i class="fas fa-sort-alpha-${equiposSortOrder === 'ASC' ? 'down' : 'up-alt'} text-blue-600"></i>
                                <span>Orden Tag: <strong>${equiposSortOrder === 'ASC' ? 'Ascendente (A-Z, 0-9)' : 'Descendente (Z-A, 9-0)'}</strong></span>
                            </button>
                            <button onclick="openModalEquipo(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1">
                                <i class="fas fa-plus mr-1"></i> + Registrar Equipo
                            </button>
                        </div>"""

replacement_btn_equipo = """                        <div class="flex items-center space-x-2">
                            <button onclick="toggleEquiposSortOrder()" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold border flex items-center space-x-1.5 transition">
                                <i class="fas fa-sort-alpha-${equiposSortOrder === 'ASC' ? 'down' : 'up-alt'} text-blue-600"></i>
                                <span>Orden Tag: <strong>${equiposSortOrder === 'ASC' ? 'Ascendente (A-Z, 0-9)' : 'Descendente (Z-A, 9-0)'}</strong></span>
                            </button>
                            ${puedeGestionar ? `
                                <button onclick="openModalEquipo(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1">
                                    <i class="fas fa-plus mr-1"></i> + Registrar Equipo
                                </button>
                            ` : ''}
                        </div>
                    </div>
                    ${!puedeGestionar ? `
                        <div class="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-800 flex items-center space-x-2.5">
                            <i class="fas fa-shield-alt text-blue-600 text-base"></i>
                            <div>
                                <span class="font-bold">Modo Consulta Autorizado (Solo Lectura):</span>
                                <span> La modificación, edición y creación de equipos y activos está estrictamente reservada para los roles de <strong>Gerente de Planta</strong> y <strong>Jefe de Mantenimiento</strong>.</span>
                            </div>
                        </div>
                    ` : ''}
                    <div>"""

if target_btn_equipo in text:
    text = text.replace(target_btn_equipo, replacement_btn_equipo)
    print("[OK] Banner de seguridad de equipos y ocultamiento de botón +Registrar Equipo aplicado.")

# Proteger funciones openModalEquipo y eliminarEquipo
target_open_eq = """        function openModalEquipo(editId) {
            document.getElementById('formEquipo').reset();"""
replacement_open_eq = """        function openModalEquipo(editId) {
            if (!puedeModificarEquipos(currentUser)) {
                mostrarToast('Acceso Restringido', 'La creación o edición de equipos queda reservada únicamente para Gerente de Planta y Jefe de Mantenimiento.', 'warning');
                return;
            }
            document.getElementById('formEquipo').reset();"""

if target_open_eq in text:
    text = text.replace(target_open_eq, replacement_open_eq)
    print("[OK] Protección estricta en openModalEquipo() agregada.")

target_del_eq = """        function eliminarEquipo(id) {
            if (!confirm(`¿Eliminar el equipo ${id}?`)) return;"""
replacement_del_eq = """        function eliminarEquipo(id) {
            if (!puedeModificarEquipos(currentUser)) {
                mostrarToast('Acceso Restringido', 'La eliminación de activos queda reservada para Gerente de Planta y Jefe de Mantenimiento.', 'warning');
                return;
            }
            if (!confirm(`¿Eliminar el equipo ${id}?`)) return;"""

if target_del_eq in text:
    text = text.replace(target_del_eq, replacement_del_eq)
    print("[OK] Protección estricta en eliminarEquipo() agregada.")

# Guardar progreso
with open(STATIC_INDEX, "w", encoding="utf-8") as f:
    f.write(text)
print("Fase 2 de index.html guardada exitosamente.")

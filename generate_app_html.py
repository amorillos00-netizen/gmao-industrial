# -*- coding: utf-8 -*-
"""
Generador Maestro del Frontend GMAO Industrial Pro v3.3
SALTYSNACK TUYERO C.A. - Confiabilidad y Gestión de Mantenimiento
"""
import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_INDEX = BASE_DIR / "app" / "static" / "index.html"
ROOT_INDEX = BASE_DIR / "index.html"

# Vamos a escribir el archivo index.html completo en trozos organizados
print("Iniciando construcción de index.html...")

parts = []

# =============================================================================
# PARTE 1: CABECERA HTML, METAS, ESTILOS, RTL Y CONFIGURACIÓN TAILWIND
# =============================================================================
parts.append("""<!DOCTYPE html>
<html lang="es" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GMAO Industrial Pro - SALTYSNACK TUYERO C.A.</title>
    <!-- PWA Support -->
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#0a6ed1">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="/static/icon-192.png">
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js para Indicadores de Confiabilidad y KPIs -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- SheetJS (XLSX) para exportación Excel profesional 100% offline -->
    <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        sap: {
                            blue: '#0a6ed1',
                            darkBlue: '#002a52',
                            header: '#1e293b',
                            lightBg: '#f8fafc',
                            cardBg: '#ffffff',
                            accent: '#e2e8f0',
                            border: '#cbd5e1'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background-color: #f1f5f9; }
        .sap-card { background: white; border-radius: 10px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
        .sap-header { background: #1e293b; color: white; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

        /* ESTILOS INTERNACIONALES RTL (RIGHT-TO-LEFT) PARA ÁRABE */
        [dir="rtl"] { text-align: right; }
        [dir="rtl"] .space-x-1 > :not([hidden]) ~ :not([hidden]) { --tw-space-x-reverse: 1; }
        [dir="rtl"] .space-x-2 > :not([hidden]) ~ :not([hidden]) { --tw-space-x-reverse: 1; }
        [dir="rtl"] .space-x-3 > :not([hidden]) ~ :not([hidden]) { --tw-space-x-reverse: 1; }
        [dir="rtl"] .space-x-4 > :not([hidden]) ~ :not([hidden]) { --tw-space-x-reverse: 1; }
        [dir="rtl"] th, [dir="rtl"] td { text-align: right; }
        [dir="rtl"] .text-right { text-align: left !important; }
        [dir="rtl"] .text-left { text-align: right !important; }
        [dir="rtl"] #sidebar { right: 0; left: auto; border-left-width: 1px; border-right-width: 0; transform: translateX(100%); }
        [dir="rtl"] #sidebar.md\\:translate-x-0 { transform: translateX(0); }
        [dir="rtl"] .fa-arrow-right:before { content: "\\f060"; }
        [dir="rtl"] .fa-arrow-left:before { content: "\\f061"; }

        /* TOAST FLOATING NOTIFICATIONS */
        #toastContainer {
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            pointer-events: none;
        }
        [dir="rtl"] #toastContainer { right: auto; left: 1rem; }
        .toast-item {
            pointer-events: auto;
            transform: translateY(0);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        /* FORMATO CORPORATIVO DE IMPRESIÓN FORMAL (PDF) */
        @media print {
            .no-print { display: none !important; }
            .print-only { display: block !important; }
            body { background: white; color: black; font-size: 11pt; }
            .sap-card { border: none; box-shadow: none; }
            table { page-break-inside: auto; width: 100%; border-collapse: collapse; }
            tr { page-break-inside: avoid; page-break-after: auto; }
            .signature-block { page-break-inside: avoid; }
        }
        .print-only { display: none; }
    </style>
</head>
<body class="h-screen flex flex-col text-slate-800 overflow-hidden">

    <!-- CONTENEDOR DE NOTIFICACIONES TOAST -->
    <div id="toastContainer"></div>

    <!-- TOP BAR DE NAVEGACIÓN CORPORATIVA -->
    <header class="sap-header px-4 py-2 flex items-center justify-between shadow-md z-30 no-print flex-shrink-0 border-b border-slate-700">
        <div class="flex items-center space-x-3">
            <button id="toggleSidebar" class="md:hidden text-white hover:bg-slate-700 p-2 rounded-lg focus:outline-none" aria-label="Abrir Menú">
                <i class="fas fa-bars text-lg"></i>
            </button>
            <div class="flex items-center space-x-2.5">
                <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
                    <i class="fas fa-industry text-sm"></i>
                </div>
                <div>
                    <h1 class="font-bold text-sm sm:text-base tracking-wide leading-tight">GMAO Industrial Pro</h1>
                    <div class="flex items-center space-x-2 text-[10px] text-slate-400">
                        <span class="bg-blue-900/60 text-blue-300 px-1.5 py-0.2 rounded font-mono font-semibold">SALTYSNACK TUYERO C.A.</span>
                        <span id="syncStatusBadge" class="inline-flex items-center text-emerald-400 font-medium">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-1"></span> <span id="syncStatusText">En Línea</span>
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex items-center space-x-2 text-xs">
            <!-- SELECTOR MULTILENGUAJE (i18n & RTL) -->
            <div class="relative">
                <select id="langSelector" onchange="changeLanguage(this.value)" class="bg-slate-800 text-slate-200 border border-slate-700 rounded-lg text-xs px-2 py-1.5 outline-none font-medium hover:bg-slate-700 cursor-pointer">
                    <option value="es">🇪🇸 Español</option>
                    <option value="en">🇬🇧 English</option>
                    <option value="ar">🇸🇦 العربية (RTL)</option>
                </select>
            </div>

            <!-- MOTOR DE NOTIFICACIONES DINÁMICAS POR ROL -->
            <div class="relative">
                <button onclick="toggleNotificationPanel()" class="relative p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition" title="Notificaciones del Sistema">
                    <i class="fas fa-bell text-sm"></i>
                    <span id="notifBadge" class="hidden absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center animate-pulse">0</span>
                </button>
                <!-- Desplegable de notificaciones -->
                <div id="notifDropdown" class="hidden absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 text-slate-800 max-h-96 overflow-hidden flex flex-col">
                    <div class="p-3 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
                        <div class="flex items-center space-x-2">
                            <i class="fas fa-bell text-blue-400"></i>
                            <span class="font-bold text-xs" data-i18n="notifTitle">Notificaciones del Sistema</span>
                        </div>
                        <button onclick="marcarTodasNotificacionesLeidas()" class="text-[10px] text-blue-300 hover:underline" data-i18n="markAllRead">Marcar todas leídas</button>
                    </div>
                    <div id="notifList" class="overflow-y-auto divide-y divide-slate-100 flex-1 text-xs">
                        <!-- Items de notificación inyectados dinámicamente -->
                    </div>
                </div>
            </div>

            <button onclick="sincronizarDatos()" class="hidden sm:flex items-center space-x-1 px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs text-slate-300 border border-slate-700 transition" title="Sincronizar Base de Datos">
                <i class="fas fa-sync-alt" id="syncIcon"></i>
                <span class="hidden md:inline" data-i18n="syncBtn">Sincronizar</span>
            </button>
            <button onclick="openModalQR()" class="hidden lg:flex items-center space-x-1.5 px-2.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-xs text-white font-semibold shadow transition" title="Vincular Dispositivo Móvil">
                <i class="fas fa-qrcode"></i>
                <span class="hidden xl:inline">Android</span>
            </button>
            <button id="pwaInstallBtn" onclick="triggerPwaInstall()" class="flex items-center space-x-1.5 px-2 py-1.5 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-xs text-white font-semibold shadow transition" title="Instalar Aplicación Offline">
                <i class="fab fa-android text-sm"></i>
                <span class="hidden sm:inline" data-i18n="installApp">Instalar App</span>
            </button>
            <div id="userMenuArea" class="flex items-center space-x-2">
                <!-- Render dinámico del usuario logueado -->
            </div>
        </div>
    </header>

    <!-- APP CONTAINER -->
    <div class="flex flex-1 overflow-hidden relative">

        <!-- MODAL DE LOGIN FORMAL PRODUCTIVO (SIN DEMOS NI AUTOLLENADOS) -->
        <div id="loginModal" class="fixed inset-0 bg-slate-900/90 z-50 flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 sm:p-8 border border-slate-200">
                <div class="text-center mb-6">
                    <div class="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-3 text-2xl shadow-inner border border-blue-100">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <h2 class="text-xl sm:text-2xl font-bold text-slate-800">GMAO Industrial Pro</h2>
                    <p class="text-xs text-slate-500 mt-1">SALTYSNACK TUYERO C.A. | Confiabilidad Operativa</p>
                    <span class="inline-block mt-2 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                        Acceso a Roles Productivos Autorizados
                    </span>
                </div>

                <form id="loginForm" class="space-y-4">
                    <div>
                        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" data-i18n="lblUser">Usuario del Sistema</label>
                        <div class="relative">
                            <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400"><i class="fas fa-user"></i></span>
                            <input type="text" id="loginUsername" required class="w-full pl-10 pr-3 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm transition" placeholder="Ingrese su usuario">
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold uppercase text-slate-600 mb-1" data-i18n="lblPass">Contraseña</label>
                        <div class="relative">
                            <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400"><i class="fas fa-lock"></i></span>
                            <input type="password" id="loginPassword" required class="w-full pl-10 pr-3 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm transition" placeholder="••••••••">
                        </div>
                    </div>
                    <div class="flex items-center justify-between text-xs">
                        <label class="flex items-center space-x-2 cursor-pointer">
                            <input type="checkbox" id="rememberUserCheckbox" class="rounded border-slate-300 text-blue-600 focus:ring-blue-500">
                            <span class="text-slate-600" data-i18n="lblRemember">Recordar en este dispositivo</span>
                        </label>
                    </div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg transition shadow-md flex items-center justify-center space-x-2">
                        <i class="fas fa-sign-in-alt"></i>
                        <span data-i18n="btnLogin">Ingresar a la Plataforma</span>
                    </button>
                </form>
            </div>
        </div>

        <!-- SIDEBAR DE NAVEGACIÓN -->
        <aside id="sidebar" class="bg-slate-900 text-slate-300 w-64 flex-shrink-0 flex flex-col justify-between transition-all duration-300 absolute md:relative z-20 h-full -translate-x-full md:translate-x-0 no-print shadow-xl md:shadow-none border-r border-slate-800">
            <div class="py-4 px-3 overflow-y-auto">
                <div class="text-[11px] font-bold uppercase text-slate-400 px-3 mb-2.5 tracking-wider flex items-center justify-between">
                    <span data-i18n="navTitle">Módulos de Gestión</span>
                    <button class="md:hidden text-slate-400 hover:text-white" onclick="toggleSidebarMenu()"><i class="fas fa-times"></i></button>
                </div>
                <nav class="space-y-1" id="navigationTabs">
                    <!-- Dinámico según rol -->
                </nav>
            </div>
            <div class="p-3 bg-slate-950/60 text-xs border-t border-slate-800 flex items-center justify-between">
                <button onclick="exportarBaseCompletaJSON()" class="text-slate-400 hover:text-blue-400 flex items-center space-x-1.5 transition text-[11px]" title="Copia de Seguridad JSON">
                    <i class="fas fa-download"></i>
                    <span>Backup DB</span>
                </button>
                <span class="text-[10px] text-slate-500">v3.3 Multiplataforma</span>
            </div>
        </aside>

        <!-- BACKDROP PARA MÓVILES -->
        <div id="sidebarBackdrop" onclick="toggleSidebarMenu()" class="fixed inset-0 bg-slate-950/50 z-10 hidden md:hidden"></div>

        <!-- MAIN CONTENT AREA -->
        <main class="flex-1 overflow-y-auto p-3.5 sm:p-5 md:p-6 bg-slate-100 no-print" id="mainView">
            <!-- Vistas dinámicas inyectadas por navigate() -->
        </main>
    </div>

    <!-- ÁREA EXCLUSIVA DE IMPRESIÓN (PDF / PRINT FORMAL) -->
    <div id="printSection" class="print-only p-8 bg-white min-h-screen text-slate-900">
        <!-- Render formal estructurado para PDF -->
    </div>
""")

print("Parte 1 completada.")
# =============================================================================
# PARTE 2: MODALES DE OPERACIÓN, REGISTRO, SSL Y MULTIMEDIA
# =============================================================================
parts.append("""
    <!-- ============================================================== -->
    <!-- MODALES DE OPERACIÓN Y REGISTRO                                -->
    <!-- ============================================================== -->

    <!-- MODAL REGISTRO / EDICIÓN PLAN PREVENTIVO CON LÓGICA DE FRECUENCIAS -->
    <div id="modalPlanPreventivo" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 my-8 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center" id="modalPlanPreventivoTitle">
                    <i class="fas fa-calendar-check text-blue-600 mr-2"></i> <span data-i18n="planModalTitle">Programar Mantenimiento Preventivo</span>
                </h3>
                <button onclick="closeModal('modalPlanPreventivo')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formPlanPreventivo" class="space-y-3.5">
                <input type="hidden" id="planEditId">
                <input type="hidden" id="planEsRefrigeracion" value="false">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1" data-i18n="lblAsset">Activo / Equipo *</label>
                    <select id="planEquipo" required class="w-full border rounded-lg p-2.5 text-xs bg-white outline-none focus:ring-2 focus:ring-blue-500"></select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1" data-i18n="lblRoutine">Nombre de la Rutina / Actividad *</label>
                    <input type="text" id="planNombre" required class="w-full border rounded-lg p-2.5 text-xs outline-none focus:ring-2 focus:ring-blue-500" placeholder="Ej: Servicio de limpieza y ajuste de lubricación">
                </div>
                
                <!-- FRECUENCIAS DINÁMICAS (DÍAS, SEMANAS, MESES) -->
                <div class="p-3 bg-slate-50 border rounded-lg space-y-2.5">
                    <label class="block text-xs font-bold text-slate-700 flex items-center">
                        <i class="fas fa-history text-blue-600 mr-1.5"></i> Configuración de Frecuencia y Proyección
                    </label>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        <div>
                            <label class="block text-[11px] font-semibold text-slate-600 mb-1">Unidad Frecuencia</label>
                            <select id="planFrecuenciaTipo" onchange="actualizarCalculoFrecuencia()" class="w-full border rounded-lg p-2 text-xs bg-white outline-none">
                                <option value="dias">Días</option>
                                <option value="semanas">Semanas</option>
                                <option value="meses" selected>Meses</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-[11px] font-semibold text-slate-600 mb-1">Intervalo Cada</label>
                            <input type="number" id="planFrecuenciaValor" min="1" value="1" onchange="actualizarCalculoFrecuencia()" class="w-full border rounded-lg p-2 text-xs outline-none">
                        </div>
                        <div class="col-span-2 sm:col-span-1">
                            <label class="block text-[11px] font-semibold text-slate-600 mb-1">Última Ejecución *</label>
                            <input type="date" id="planUltimaFecha" required onchange="actualizarCalculoFrecuencia()" class="w-full border rounded-lg p-2 text-xs outline-none">
                        </div>
                    </div>
                    <div>
                        <label class="block text-[11px] font-semibold text-slate-600 mb-0.5">Próxima Fecha Calculada Automáticamente</label>
                        <input type="date" id="planProximaFecha" required class="w-full border rounded-lg p-2 text-xs bg-blue-50 font-bold text-blue-700 outline-none" readonly>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1" data-i18n="lblTechs">Técnicos Asignados Responsables</label>
                    <div id="planTecnicosContainer" class="border rounded-lg p-2.5 max-h-28 overflow-y-auto space-y-1.5 text-xs bg-slate-50"></div>
                </div>
                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalPlanPreventivo')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50" data-i18n="btnCancel">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow" data-i18n="btnSaveRoutine">Guardar Rutina</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL NUEVA SOLICITUD INTERDEPARTAMENTAL (FLUJO EXCLUSIVO DE 4 ESTADOS) -->
    <div id="modalSolicitudInter" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 my-8">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center">
                    <i class="fas fa-ticket-alt text-blue-600 mr-2"></i> <span data-i18n="newReqTitle">Solicitud de Intervención Interdepartamental</span>
                </h3>
                <button onclick="closeModal('modalSolicitudInter')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formSolicitudInter" class="space-y-3.5">
                <input type="hidden" id="solEditId">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Tipo de Activo *</label>
                        <select id="solTipo" required class="w-full border rounded-lg p-2.5 text-xs bg-white outline-none">
                            <option value="Maquinaria / Equipo">Maquinaria / Equipo de Proceso</option>
                            <option value="Infraestructura / Instalaciones">Infraestructura / Instalaciones</option>
                            <option value="Climatización y Frío">Climatización / Frío Industrial</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Nivel de Urgencia *</label>
                        <select id="solUrgencia" required class="w-full border rounded-lg p-2.5 text-xs bg-white outline-none">
                            <option value="Baja">Baja - Puede esperar</option>
                            <option value="Media" selected>Media - Turno regular</option>
                            <option value="Alta">Alta - Afecta velocidad/calidad</option>
                            <option value="Crítica">Crítica - Línea Parada / Seguridad</option>
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Área / Departamento *</label>
                        <input type="text" id="solArea" required class="w-full border rounded-lg p-2.5 text-xs outline-none" placeholder="Ej: Envasado, Producción, Almacén">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Equipo / Ubicación Afectada *</label>
                        <input type="text" id="solUbicacion" required class="w-full border rounded-lg p-2.5 text-xs outline-none" placeholder="Ej: Extrusora 01, Cinta Envasado">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Descripción del Síntoma o Falla *</label>
                    <textarea id="solDescripcion" rows="3" required class="w-full border rounded-lg p-2.5 text-xs outline-none" placeholder="Especifique ruido anormal, fugas, sobrecalentamiento, falla eléctrica..."></textarea>
                </div>

                <div id="campoStatusSolicitudGerente" class="hidden">
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Estatus del Requerimiento *</label>
                    <select id="solStatus" class="w-full border rounded-lg p-2.5 text-xs bg-white font-semibold outline-none">
                        <option value="Aprobada" selected>Aprobada</option>
                        <option value="En espera de materiales">En espera de materiales</option>
                        <option value="En proceso">En proceso</option>
                        <option value="Culminada">Culminada</option>
                    </select>
                </div>

                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalSolicitudInter')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50" data-i18n="btnCancel">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow" data-i18n="btnSubmitReq">Emitir Solicitud</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL CREAR / EDITAR OT (CON CARGA MULTIMEDIA DE FOTO ANTES) -->
    <div id="modalOT" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6 my-8 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center" id="modalOTTitle">
                    <i class="fas fa-clipboard-check text-blue-600 mr-2"></i> <span data-i18n="otModalTitle">Orden de Trabajo (OT)</span>
                </h3>
                <button onclick="closeModal('modalOT')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formOT" class="space-y-3.5">
                <input type="hidden" id="otId">
                <input type="hidden" id="otSolicitudId">
                <input type="hidden" id="otFotoAntesBase64">
                <input type="hidden" id="otFotoDespuesBase64">
                <input type="hidden" id="otStatusVal" value="Pendiente">
                <input type="hidden" id="otFechaAsignacionVal">
                <input type="hidden" id="otFechaInicioVal">
                <input type="hidden" id="otFechaFinVal">
                <input type="hidden" id="otActividadesVal">
                <input type="hidden" id="otTiempoIntervencionVal" value="0.0">
                <input type="hidden" id="otTiempoParadaVal" value="0.0">
                <input type="hidden" id="otRepuestosUsadosVal" value="[]">
                <input type="hidden" id="otTecnicoAcompananteVal">

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Tipo de Mantenimiento *</label>
                        <select id="otTipo" required class="w-full border rounded-lg p-2.5 text-xs bg-white outline-none">
                            <option value="Correctivo">Correctivo (Avería / Falla Imprevista)</option>
                            <option value="Preventivo">Preventivo (Programado / Sistemático)</option>
                            <option value="Eventual">Eventual (Infraestructura / Modificación)</option>
                            <option value="Predictivo">Predictivo (Análisis Vibración / Termografía)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Prioridad *</label>
                        <select id="otPrioridad" required class="w-full border rounded-lg p-2.5 text-xs bg-white outline-none">
                            <option value="Alta">Alta / Emergencia Operativa</option>
                            <option value="Media" selected>Media - Prioridad Normal</option>
                            <option value="Baja">Baja - Tarea Secundaria</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Activo / Ubicación Técnica *</label>
                    <select id="otEquipo" required class="w-full border rounded-lg p-2.5 text-xs bg-white outline-none"></select>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Descripción del Requerimiento o Falla *</label>
                    <textarea id="otDescripcion" rows="2" required class="w-full border rounded-lg p-2.5 text-xs outline-none" placeholder="Instrucciones de trabajo o sintomatología observada..."></textarea>
                </div>

                <!-- CARGA DE FOTO INICIAL (EVIDENCIA DE FALLA AL CREAR LA OT) -->
                <div class="p-3 bg-blue-50/60 border border-blue-200 rounded-lg">
                    <label class="block text-xs font-bold text-slate-700 mb-1 flex items-center justify-between">
                        <span><i class="fas fa-camera text-blue-600 mr-1.5"></i> Evidencia Fotográfica Inicial (Foto ANTES)</span>
                        <span class="text-[10px] text-slate-500">Opcional al crear, visible para técnicos</span>
                    </label>
                    <input type="file" id="inputFotoInicialOT" accept="image/*" capture="environment" onchange="procesarFotoConCompresion(this, 'otFotoAntesBase64', 'previewFotoInicialOT')" class="w-full text-[11px] file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200 cursor-pointer">
                    <div id="previewFotoInicialOT" class="mt-2 flex items-center space-x-2"></div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Técnicos de Campo Asignados</label>
                        <div id="otTecnicosContainer" class="border rounded-lg p-2.5 max-h-28 overflow-y-auto space-y-1.5 text-xs bg-slate-50"></div>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Fecha Programada de Ejecución *</label>
                        <input type="date" id="otFechaProgramada" required class="w-full border rounded-lg p-2.5 text-xs outline-none">
                    </div>
                </div>

                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalOT')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50" data-i18n="btnCancel">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow" data-i18n="btnSaveOT">Guardar Orden</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL CIERRE Y REPORTE TÉCNICO DE OT -->
    <div id="modalCierreOT" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6 my-8 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center">
                    <i class="fas fa-check-circle text-emerald-600 mr-2"></i> Bitácora Técnica de Cierre OT
                </h3>
                <button onclick="closeModal('modalCierreOT')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formCierreOT" class="space-y-4">
                <input type="hidden" id="cierreOtId">
                <input type="hidden" id="cierreFotoAntesBase64">
                <input type="hidden" id="cierreFotoDespuesBase64">

                <div class="bg-blue-50 border border-blue-200 p-3 rounded-lg text-xs space-y-1 text-slate-700">
                    <div><strong>Folio:</strong> <span id="cierreFolioDisplay" class="font-mono font-bold text-blue-700"></span></div>
                    <div><strong>Equipo:</strong> <span id="cierreEquipoDisplay" class="font-bold"></span></div>
                    <div><strong>Requerimiento:</strong> <span id="cierreFallaDisplay"></span></div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Fecha y Hora de Inicio *</label>
                        <input type="datetime-local" id="cierreFechaInicio" required onchange="calcularTiempoIntervencionAutomatico()" class="w-full border rounded-lg p-2.5 text-xs outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Fecha y Hora de Finalización *</label>
                        <input type="datetime-local" id="cierreFechaFin" required onchange="calcularTiempoIntervencionAutomatico()" class="w-full border rounded-lg p-2.5 text-xs outline-none">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Trabajos Efectuados y Diagnóstico *</label>
                    <textarea id="cierreTrabajo" rows="3" required class="w-full border rounded-lg p-2.5 text-xs outline-none" placeholder="Detalle los procedimientos de desmontaje, mediciones, calibraciones y ajustes realizados..."></textarea>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Técnico de Apoyo / Acompañante</label>
                    <select id="cierreTecnicoAcompanante" class="w-full border rounded-lg p-2.5 text-xs bg-slate-50 outline-none"></select>
                </div>

                <!-- SECCIÓN FOTOGRAFÍAS ANTES Y DESPUÉS -->
                <div class="border-t pt-3">
                    <label class="block text-xs font-bold text-slate-700 mb-2 flex items-center">
                        <i class="fas fa-camera text-blue-600 mr-1.5"></i> Evidencias Fotográficas de Intervención
                    </label>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div class="p-3 bg-slate-50 border rounded-lg space-y-1.5">
                            <span class="text-[11px] font-semibold text-slate-600 block">Foto ANTES de la intervención</span>
                            <input type="file" id="inputFotoAntes" accept="image/*" capture="environment" onchange="procesarFotoConCompresion(this, 'cierreFotoAntesBase64', 'previewFotoAntes')" class="w-full text-[11px] file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-100 file:text-blue-700 hover:file:bg-blue-200 cursor-pointer">
                            <div id="previewFotoAntes" class="mt-1"></div>
                        </div>
                        <div class="p-3 bg-slate-50 border rounded-lg space-y-1.5">
                            <span class="text-[11px] font-semibold text-slate-600 block">Foto DESPUÉS de la intervención</span>
                            <input type="file" id="inputFotoDespues" accept="image/*" capture="environment" onchange="procesarFotoConCompresion(this, 'cierreFotoDespuesBase64', 'previewFotoDespues')" class="w-full text-[11px] file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-emerald-100 file:text-emerald-700 hover:file:bg-emerald-200 cursor-pointer">
                            <div id="previewFotoDespues" class="mt-1"></div>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Horas de Intervención (Cálculo Automático)</label>
                        <input type="number" step="0.1" id="cierreTiempoIntervencion" required class="w-full border rounded-lg p-2.5 text-xs bg-slate-50 font-bold text-blue-700 outline-none" readonly>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Horas de Parada de Equipo (Downtime)</label>
                        <input type="number" step="0.1" id="cierreTiempoParada" class="w-full border rounded-lg p-2.5 text-xs outline-none" placeholder="Ej: 0.75">
                    </div>
                </div>

                <!-- SECCIÓN DE REPUESTOS CON DESCUENTO DE STOCK AUTOMÁTICO -->
                <div class="border-t pt-3">
                    <label class="block text-xs font-bold text-slate-700 mb-1 flex items-center justify-between">
                        <span><i class="fas fa-boxes text-blue-600 mr-1.5"></i> Repuestos e Insumos Utilizados</span>
                        <span class="text-[11px] font-normal text-slate-500">Se descuenta del inventario al cerrar</span>
                    </label>
                    <div class="flex flex-col sm:flex-row gap-2 mb-2">
                        <select id="selectRepuestoAlmacen" class="flex-1 border rounded-lg p-2 text-xs outline-none bg-white">
                            <option value="">[ Seleccione del Almacén o escriba libre ]</option>
                        </select>
                        <input type="text" id="nombreMaterialLibre" placeholder="O repuesto libre no registrado" class="flex-1 border rounded-lg p-2 text-xs outline-none">
                        <input type="number" id="cantRepuesto" placeholder="Cant." min="1" class="w-20 border rounded-lg p-2 text-xs outline-none">
                        <button type="button" onclick="agregarRepuestoAOT()" class="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>

                    <table class="w-full text-left text-xs border rounded-lg overflow-hidden">
                        <thead class="bg-slate-100 text-slate-600">
                            <tr>
                                <th class="p-2">Material / Repuesto</th>
                                <th class="p-2">Cantidad</th>
                                <th class="p-2 text-right">Quitar</th>
                            </tr>
                        </thead>
                        <tbody id="listaRepuestosUsados" class="divide-y bg-white"></tbody>
                    </table>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Estado de Finalización</label>
                    <select id="cierreEstadoFinal" class="w-full border rounded-lg p-2.5 text-xs bg-white outline-none">
                        <option value="Concluida">Concluida / En Operación Normal</option>
                        <option value="En Proceso">En Proceso / Espera de Prueba</option>
                    </select>
                </div>

                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalCierreOT')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold shadow">Registrar Cierre y Actualizar Stock</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL SOLICITUD DE CONDICIONES INSEGURAS (SSL) - FOTO OBLIGATORIA -->
    <div id="modalSSL" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 my-8 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center">
                    <i class="fas fa-hard-hat text-amber-600 mr-2"></i> Reporte de Condición Insegura (SSL)
                </h3>
                <button onclick="closeModal('modalSSL')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formSSL" class="space-y-3.5">
                <input type="hidden" id="sslEditId">
                <input type="hidden" id="sslFotoBase64">

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Código Condición</label>
                        <input type="text" id="sslCodigo" class="w-full border rounded-lg p-2 text-xs bg-slate-50 font-mono outline-none" readonly placeholder="Auto">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Nivel de Riesgo *</label>
                        <select id="sslNivelRiesgo" required class="w-full border rounded-lg p-2 text-xs bg-white font-bold outline-none">
                            <option value="Crítico" class="text-red-700">Crítico (Peligro Inminente / Parada)</option>
                            <option value="Alto" selected class="text-orange-700">Alto (Riesgo Grave)</option>
                            <option value="Medio" class="text-amber-700">Medio (Condición Subestándar)</option>
                            <option value="Bajo" class="text-emerald-700">Bajo (Oportunidad de Mejora)</option>
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Área de la Planta *</label>
                        <input type="text" id="sslArea" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Ej: Envasado, Producción Snacks">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Ubicación / Equipo</label>
                        <input type="text" id="sslUbicacion" class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Ej: Polea Cinta #3, Pasillo B">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Descripción de la Condición Insegura *</label>
                    <textarea id="sslDescripcion" rows="2" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Describa el peligro físico, falta de resguardos, fuga de vapor/químicos, riesgo eléctrico..."></textarea>
                </div>

                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Acción Correctiva / Preventiva Propuesta</label>
                    <textarea id="sslAccionPropuesta" rows="2" class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Ej: Fabricar resguardo perimetral, señalizar línea caliente, reparar fuga..."></textarea>
                </div>

                <!-- CARGA OBLIGATORIA DE FOTOGRAFÍA -->
                <div class="p-3 bg-amber-50 border border-amber-300 rounded-lg">
                    <label class="block text-xs font-bold text-amber-900 mb-1 flex items-center justify-between">
                        <span><i class="fas fa-camera text-amber-600 mr-1.5"></i> Fotografía de Evidencia (OBLIGATORIA) *</span>
                        <span class="text-[10px] text-amber-700 font-semibold">Requerida para emitir</span>
                    </label>
                    <input type="file" id="inputFotoSSL" accept="image/*" capture="environment" onchange="procesarFotoConCompresion(this, 'sslFotoBase64', 'previewFotoSSL')" class="w-full text-[11px] file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-amber-200 file:text-amber-800 hover:file:bg-amber-300 cursor-pointer">
                    <div id="previewFotoSSL" class="mt-2 flex items-center space-x-2"></div>
                </div>

                <div id="secStatusSSLGerente" class="hidden">
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Estado de Seguimiento SSL</label>
                    <select id="sslStatus" class="w-full border rounded-lg p-2 text-xs bg-white outline-none">
                        <option value="Pendiente">Pendiente (Por Evaluar)</option>
                        <option value="En Corrección">En Corrección (OT Generada / En Taller)</option>
                        <option value="Corregida">Corregida (Mitigación Exitosa)</option>
                        <option value="Desestimada">Desestimada (No Aplica)</option>
                    </select>
                </div>

                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalSSL')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold shadow">Guardar Condición SSL</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL LIGHTBOX MULTIMEDIA PARA AMPLIAR EVIDENCIAS FOTOGRÁFICAS -->
    <div id="modalLightbox" class="fixed inset-0 bg-slate-950/90 hidden z-50 flex flex-col items-center justify-center p-4 no-print" onclick="closeModal('modalLightbox')">
        <div class="max-w-4xl w-full bg-slate-900 border border-slate-700 rounded-2xl overflow-hidden shadow-2xl p-4 flex flex-col" onclick="event.stopPropagation()">
            <div class="flex items-center justify-between pb-3 border-b border-slate-800 text-white">
                <div class="flex items-center space-x-2">
                    <i class="fas fa-camera text-blue-400"></i>
                    <h3 class="font-bold text-sm" id="lightboxTitle">Evidencia Fotográfica</h3>
                </div>
                <button onclick="closeModal('modalLightbox')" class="text-slate-400 hover:text-white"><i class="fas fa-times text-lg"></i></button>
            </div>
            <div class="flex-1 flex items-center justify-center py-4 max-h-[70vh] overflow-hidden">
                <img id="lightboxImage" src="" alt="Evidencia" class="max-h-[68vh] max-w-full rounded-lg object-contain shadow-lg">
            </div>
            <div class="pt-2 border-t border-slate-800 flex justify-between items-center text-xs text-slate-400">
                <span id="lightboxDescription">Evidencia cargada</span>
                <button onclick="closeModal('modalLightbox')" class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-white rounded">Cerrar</button>
            </div>
        </div>
    </div>

    <!-- MODAL PERSONALIZAR ESTRUCTURA DEL INFORME PERIÓDICO -->
    <div id="modalPersonalizarInforme" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-xl w-full p-6 my-8 max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center">
                    <i class="fas fa-sliders-h text-blue-600 mr-2"></i> Configurar Estructura del Informe Técnico
                </h3>
                <button onclick="closeModal('modalPersonalizarInforme')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formPersonalizarInforme" onsubmit="guardarConfiguracionInforme(event)" class="space-y-3.5">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Título del Informe</label>
                    <input type="text" id="cfgInformeTitulo" required class="w-full border rounded-lg p-2 text-xs outline-none" value="INFORME DE GESTIÓN DE MANTENIMIENTO Y CONFIABILIDAD">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Subtítulo / Empresa</label>
                    <input type="text" id="cfgInformeSubtitulo" required class="w-full border rounded-lg p-2 text-xs outline-none" value="SALTYSNACK TUYERO C.A. - DEPARTAMENTO DE MANTENIMIENTO E INFRAESTRUCTURA">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Diagnóstico Ejecutivo / Resumen</label>
                    <textarea id="cfgInformeDiagnostico" rows="3" class="w-full border rounded-lg p-2 text-xs outline-none">Se realizó la evaluación operativa de los sistemas mecánicos, térmicos y de empaque, manteniendo una disponibilidad sobre la meta internacional con atención prioritaria de paradas imprevistas.</textarea>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Recomendaciones de Confiabilidad</label>
                    <textarea id="cfgInformeRecomendaciones" rows="2" class="w-full border rounded-lg p-2 text-xs outline-none">Auditar el desgaste de componentes en líneas de extrusión y garantizar stock preventivo de repuestos críticos.</textarea>
                </div>

                <div class="p-3 bg-slate-50 border rounded-lg space-y-2 text-xs">
                    <span class="font-bold text-slate-700 block">Secciones a Incluir en el Informe:</span>
                    <label class="flex items-center space-x-2"><input type="checkbox" id="cfgSecKPI" checked class="rounded"> <span>Indicadores Clave de Confiabilidad (Disponibilidad, MTBF, MTTR)</span></label>
                    <label class="flex items-center space-x-2"><input type="checkbox" id="cfgSecGrafico" checked class="rounded"> <span>Gráfico Comparativo de Desempeño</span></label>
                    <label class="flex items-center space-x-2"><input type="checkbox" id="cfgSecOTs" checked class="rounded"> <span>Matriz de Órdenes de Trabajo Relevantes</span></label>
                    <label class="flex items-center space-x-2"><input type="checkbox" id="cfgSecRepuestos" checked class="rounded"> <span>Consumo de Repuestos y Materiales Críticos</span></label>
                    <label class="flex items-center space-x-2"><input type="checkbox" id="cfgSecSSL" checked class="rounded"> <span>Resumen de Condiciones de Seguridad y Salud Laboral (SSL)</span></label>
                    <label class="flex items-center space-x-2"><input type="checkbox" id="cfgSecFirmas" checked class="rounded"> <span>Bloque Formal de Firmas Técnicas</span></label>
                </div>

                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalPersonalizarInforme')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow">Aplicar Estructura</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL PROVEEDORES -->
    <div id="modalProveedor" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 my-8">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center" id="modalProveedorTitle">
                    <i class="fas fa-truck text-blue-600 mr-2"></i> Registrar Proveedor
                </h3>
                <button onclick="closeModal('modalProveedor')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formProveedor" class="space-y-3.5">
                <input type="hidden" id="prvEditId">
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">RIF / NIT / NIF *</label>
                        <input type="text" id="prvRif" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="J-12345678-0">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Categoría *</label>
                        <select id="prvCategoria" class="w-full border rounded-lg p-2 text-xs outline-none bg-white">
                            <option value="Rodamientos y Sellos">Rodamientos y Sellos</option>
                            <option value="Refrigeración y Climatización">Refrigeración y Climatización</option>
                            <option value="Electricidad e Instrumentación">Electricidad e Instrumentación</option>
                            <option value="Lubricantes y Filtros">Lubricantes y Filtros</option>
                            <option value="Servicios Metalmecánicos">Servicios Metalmecánicos</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Razón Social *</label>
                    <input type="text" id="prvNombre" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Ej: Suministros Industriales SKF C.A.">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Contacto</label>
                        <input type="text" id="prvContacto" class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Marcos Rivas">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Teléfono</label>
                        <input type="tel" id="prvTelefono" class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="+58 212-5551234">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Email</label>
                    <input type="email" id="prvEmail" class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="ventas@proveedor.com">
                </div>
                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalProveedor')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow">Guardar Proveedor</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL REPUESTO -->
    <div id="modalRepuesto" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 my-8">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center" id="modalRepuestoTitle">
                    <i class="fas fa-box-open text-blue-600 mr-2"></i> Registrar Repuesto / Material
                </h3>
                <button onclick="closeModal('modalRepuesto')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formRepuesto" class="space-y-3.5">
                <input type="hidden" id="repEditId">
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Código / Referencia *</label>
                        <input type="text" id="repCodigo" required class="w-full border rounded-lg p-2 text-xs outline-none font-mono" placeholder="SKF-6205">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Unidad de Medida *</label>
                        <select id="repUm" class="w-full border rounded-lg p-2 text-xs outline-none bg-white">
                            <option value="pza">Pieza (pza)</option>
                            <option value="Litros">Litros</option>
                            <option value="Kg">Kilogramos</option>
                            <option value="Metros">Metros</option>
                            <option value="Cilindro">Cilindro / Bombona</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Descripción del Artículo *</label>
                    <input type="text" id="repName" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Ej: Rodamiento Rígido SKF 6205 2RS">
                </div>
                <div class="grid grid-cols-3 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Stock Actual *</label>
                        <input type="number" id="repStock" required min="0" value="10" class="w-full border rounded-lg p-2 text-xs outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Stock Mínimo *</label>
                        <input type="number" id="repStockMin" required min="1" value="3" class="w-full border rounded-lg p-2 text-xs outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Costo ($) *</label>
                        <input type="number" step="0.01" id="repCosto" required min="0" value="15.00" class="w-full border rounded-lg p-2 text-xs outline-none">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Proveedor Habitual</label>
                    <select id="repProveedor" class="w-full border rounded-lg p-2 text-xs outline-none bg-white"></select>
                </div>
                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalRepuesto')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow">Guardar Material</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL COMPRAS -->
    <div id="modalCompraMaterial" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 my-8">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center" id="modalCompraTitle">
                    <i class="fas fa-shopping-cart text-blue-600 mr-2"></i> Solicitud de Compra de Material
                </h3>
                <button onclick="closeModal('modalCompraMaterial')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formCompraMaterial" class="space-y-3.5">
                <input type="hidden" id="compraEditId">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Descripción del Material / Insumo *</label>
                    <input type="text" id="compraDescripcion" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Ej: Rodamiento SKF 6205">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Cantidad Solicitada *</label>
                        <input type="number" id="compraCantSol" required min="1" value="1" class="w-full border rounded-lg p-2 text-xs outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Cantidad Recibida</label>
                        <input type="number" id="compraCantRec" min="0" value="0" class="w-full border rounded-lg p-2 text-xs outline-none">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Precio Unitario Estimado</label>
                        <input type="number" step="0.01" id="compraPrecio" value="0.00" class="w-full border rounded-lg p-2 text-xs outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Proveedor Cotizado</label>
                        <select id="compraProveedor" class="w-full border rounded-lg p-2 text-xs outline-none bg-white"></select>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Observaciones</label>
                    <input type="text" id="compraObs" class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Urgencia para línea empaque...">
                </div>
                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalCompraMaterial')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow">Guardar Compra</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL ACTIVO / EQUIPO -->
    <div id="modalEquipo" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 my-8">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center" id="modalEquipoTitle">
                    <i class="fas fa-cogs text-blue-600 mr-2"></i> Registrar Activo / Equipo (ISO 14224)
                </h3>
                <button onclick="closeModal('modalEquipo')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formEquipo" class="space-y-3.5">
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Tag / Código *</label>
                        <input type="text" id="eqTag" required class="w-full border rounded-lg p-2 text-xs font-mono outline-none uppercase" placeholder="EQ-101">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Criticidad *</label>
                        <select id="eqCriticidad" class="w-full border rounded-lg p-2 text-xs outline-none bg-white">
                            <option value="Alta">Alta (Crítica)</option>
                            <option value="Media" selected>Media (Normal)</option>
                            <option value="Baja">Baja (Secundaria)</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Denominación del Activo *</label>
                    <input type="text" id="eqNombre" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Compresor Tornillo Principal">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Planta *</label>
                        <input type="text" id="eqPlanta" required class="w-full border rounded-lg p-2 text-xs outline-none" value="Planta Central">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Línea / Proceso *</label>
                        <input type="text" id="eqLinea" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Envasado / Snacks">
                    </div>
                </div>
                <div class="p-2.5 bg-cyan-50 border border-cyan-200 rounded-lg space-y-1.5">
                    <label class="flex items-center space-x-2 text-xs cursor-pointer">
                        <input type="checkbox" id="eqEsRefrigeracion" class="rounded text-cyan-600">
                        <span class="font-semibold text-cyan-900">¿Es Sistema de Refrigeración / Climatización?</span>
                    </label>
                    <input type="text" id="eqTipoRefrigerante" placeholder="Tipo de Gas (ej: R-22, R-410A)" class="w-full border rounded p-1.5 text-xs outline-none bg-white">
                </div>
                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalEquipo')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow">Guardar Equipo</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL USUARIOS -->
    <div id="modalUsuario" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 my-8">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center" id="modalUsuarioTitle">
                    <i class="fas fa-user-plus text-blue-600 mr-2"></i> Crear Usuario
                </h3>
                <button onclick="closeModal('modalUsuario')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formUsuario" class="space-y-3.5">
                <input type="hidden" id="usrEditId">
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Username *</label>
                        <input type="text" id="usrUsername" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="usuario1">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Contraseña *</label>
                        <input type="text" id="usrPassword" required class="w-full border rounded-lg p-2 text-xs outline-none" value="1234">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Nombre Completo *</label>
                    <input type="text" id="usrNombreCompleto" required class="w-full border rounded-lg p-2 text-xs outline-none" placeholder="Ing. Juan Pérez">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Rol Operativo *</label>
                        <select id="usrRol" class="w-full border rounded-lg p-2 text-xs outline-none bg-white font-semibold">
                            <option value="Gerente">Gerente / Jefe Mantenimiento</option>
                            <option value="Tecnico" selected>Técnico de Campo</option>
                            <option value="Solicitante">Solicitante de Planta</option>
                            <option value="Jefe SSL">Jefe SSL (Seguridad y Salud)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Departamento</label>
                        <input type="text" id="usrDepartamento" class="w-full border rounded-lg p-2 text-xs outline-none" value="Mantenimiento">
                    </div>
                </div>
                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalUsuario')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow">Guardar Usuario</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL CONFIGURACIÓN DE PARÁMETROS OPERATIVOS Y MTTR -->
    <div id="modalConfiguracionMTTR" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 my-8">
            <div class="flex justify-between items-center border-b pb-3 mb-4">
                <h3 class="text-base font-bold text-slate-800 flex items-center">
                    <i class="fas fa-sliders-h text-blue-600 mr-2"></i> Parámetros Operativos y Umbral MTTR
                </h3>
                <button onclick="closeModal('modalConfiguracionMTTR')" class="text-slate-400 hover:text-slate-600"><i class="fas fa-times text-lg"></i></button>
            </div>
            <form id="formConfiguracionMTTR" onsubmit="guardarConfiguracionMTTR(event)" class="space-y-4">
                <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-slate-700">
                    <p>Ajuste el valor mínimo de referencia o umbral meta para el indicador <strong>MTTR (Mean Time to Repair)</strong>. El desempeño y alertas del sistema evaluarán las fallas respecto a esta cota.</p>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Umbral Mínimo / Meta de MTTR (Horas) *</label>
                    <div class="relative">
                        <input type="number" step="0.1" min="0.1" id="cfgMttrTarget" required class="w-full border rounded-lg p-2.5 text-sm font-bold text-blue-700 outline-none focus:ring-2 focus:ring-blue-500" placeholder="2.0">
                        <span class="absolute right-3 top-2.5 text-xs text-slate-400 font-bold">horas</span>
                    </div>
                    <span class="text-[10px] text-slate-500 mt-1 block">Tiempo medio estándar de respuesta y reparación de averías mecánicas y eléctricas.</span>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Meta de Disponibilidad Operativa (%)</label>
                    <div class="relative">
                        <input type="number" step="0.5" min="50" max="100" id="cfgAvailabilityTarget" class="w-full border rounded-lg p-2.5 text-sm font-bold text-emerald-700 outline-none focus:ring-2 focus:ring-blue-500" placeholder="95.0">
                        <span class="absolute right-3 top-2.5 text-xs text-slate-400 font-bold">%</span>
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Anticipación de Alertas Preventivas</label>
                    <div class="relative">
                        <input type="number" min="1" max="30" id="cfgPreventiveAlertDays" value="5" class="w-full border rounded-lg p-2.5 text-sm font-bold text-amber-700 outline-none focus:ring-2 focus:ring-blue-500" placeholder="5">
                        <span class="absolute right-3 top-2.5 text-xs text-slate-400 font-bold">días</span>
                    </div>
                </div>
                <div class="flex justify-end space-x-2 pt-3 border-t">
                    <button type="button" onclick="closeModal('modalConfiguracionMTTR')" class="px-4 py-2 border rounded-lg text-slate-600 text-xs font-medium hover:bg-slate-50">Cancelar</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 shadow">Guardar Parámetros</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL VINCULACIÓN ANDROID / QR -->
    <div id="modalQRAndroid" class="fixed inset-0 bg-slate-900/60 hidden z-40 flex items-center justify-center p-4 no-print overflow-y-auto">
        <div class="bg-white rounded-xl shadow-2xl max-w-sm w-full p-6 text-center">
            <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-3 text-xl">
                <i class="fab fa-android"></i>
            </div>
            <h3 class="font-bold text-base text-slate-800">Despliegue Multiplataforma Android</h3>
            <p class="text-xs text-slate-500 mt-1 mb-3">Conecte su dispositivo móvil Android en la misma red Wi-Fi o instale la PWA 100% offline.</p>
            <div class="bg-slate-100 p-3 rounded-lg border text-xs font-mono break-all text-slate-700 mb-3" id="qrServerUrlDisplay">
                http://localhost:8000
            </div>
            <button onclick="copiarUrlServidor()" class="w-full bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold py-2 rounded-lg mb-2">
                <i class="fas fa-copy mr-1"></i> Copiar URL de Planta
            </button>
            <button onclick="closeModal('modalQRAndroid')" class="text-xs text-slate-500 hover:underline">Cerrar</button>
        </div>
    </div>
""")

print("Parte 2 anexada exitosamente.")
# =============================================================================
# PARTE 3: SCRIPTS, i18n, ESTADO, SINCRONIZACIÓN Y MOTOR DE NOTIFICACIONES
# =============================================================================
parts.append("""
    <!-- ============================================================== -->
    <!-- LOGICA JAVASCRIPT: ARQUITECTURA OFFLINE-FIRST, I18N Y MOTORES  -->
    <!-- ============================================================== -->
    <script>
        // --- 1. DICCIONARIO INTERNACIONAL (ESPAÑOL, INGLÉS, ÁRABE CON RTL) ---
        const i18nTranslations = {
            es: {
                appTitle: "GMAO Industrial Pro",
                navTitle: "Módulos de Gestión",
                navDashboard: "Dashboard & KPIs",
                navSolicitudes: "Solicitudes Interdep.",
                navCronograma: "Cronograma Preventivo",
                navCronogramaAnual: "Cronograma Anual Preventivo",
                navSSL: "Condiciones Inseguras (SSL)",
                navRefrigeracion: "Refrigeración & Frío",
                navEquipos: "Activos & Ubicaciones",
                navOTs: "Órdenes de Trabajo (OT)",
                navAlmacen: "Almacén de Repuestos",
                navProveedores: "Proveedores",
                navCompras: "Control de Compras",
                navInformes: "Informes Periódicos",
                navUsuarios: "Usuarios y Seguridad",
                navMisOTs: "Mis OTs Asignadas",
                navMisSolicitudes: "Mis Solicitudes de Falla",
                lblUser: "Usuario del Sistema",
                lblPass: "Contraseña",
                lblRemember: "Recordar en este dispositivo",
                btnLogin: "Ingresar a la Plataforma",
                onlineBadge: "En Línea",
                offlineBadge: "Modo Local Autónomo",
                syncingBadge: "Sincronizando...",
                syncBtn: "Sincronizar",
                installApp: "Instalar App",
                notifTitle: "Notificaciones del Sistema",
                markAllRead: "Marcar todas leídas",
                btnCancel: "Cancelar",
                btnSaveOT: "Guardar Orden",
                btnSubmitReq: "Emitir Solicitud",
                btnSaveRoutine: "Guardar Rutina",
                lblAsset: "Activo / Equipo *",
                lblRoutine: "Nombre de la Rutina / Actividad *",
                lblTechs: "Técnicos Asignados Responsables",
                planModalTitle: "Programar Mantenimiento Preventivo",
                newReqTitle: "Solicitud de Intervención Interdepartamental",
                otModalTitle: "Orden de Trabajo (OT)",
                kpiMonthly: "Mensual (720h)",
                kpiYearly: "Anual (8,760h)",
                kpiAvailability: "Disponibilidad Operativa",
                kpiMTBF: "MTBF (Confiabilidad)",
                kpiMTTR: "MTTR (Tiempo Reparación)",
                kpiCompliance: "Cumplimiento Preventivo",
                exportMatrizExcel: "Exportar Matriz O.T. a Excel",
                exportCronogramaExcel: "Exportar Cronograma a Excel",
                printCorporatePDF: "Imprimir Informe Formal (PDF)"
            },
            en: {
                appTitle: "Industrial CMMS Pro",
                navTitle: "Management Modules",
                navDashboard: "Dashboard & KPIs",
                navSolicitudes: "Interdept. Requests",
                navCronograma: "Preventive Schedule",
                navCronogramaAnual: "Annual Preventive Schedule",
                navSSL: "Safety & Health (HSE)",
                navRefrigeracion: "HVAC & Cold Chain",
                navEquipos: "Assets & Locations",
                navOTs: "Work Orders (WO)",
                navAlmacen: "Spare Parts Inventory",
                navProveedores: "Suppliers",
                navCompras: "Purchasing",
                navInformes: "Periodic Reports",
                navUsuarios: "Users & Security",
                navMisOTs: "My Assigned WOs",
                navMisSolicitudes: "My Fault Requests",
                lblUser: "System Username",
                lblPass: "Password",
                lblRemember: "Remember on this device",
                btnLogin: "Login to Platform",
                onlineBadge: "Online",
                offlineBadge: "Autonomous Offline Mode",
                syncingBadge: "Syncing...",
                syncBtn: "Sync Data",
                installApp: "Install App",
                notifTitle: "System Notifications",
                markAllRead: "Mark all as read",
                btnCancel: "Cancel",
                btnSaveOT: "Save Work Order",
                btnSubmitReq: "Submit Request",
                btnSaveRoutine: "Save Routine",
                lblAsset: "Asset / Equipment *",
                lblRoutine: "Routine / Activity Name *",
                lblTechs: "Assigned Technicians",
                planModalTitle: "Schedule Preventive Maintenance",
                newReqTitle: "Interdepartmental Maintenance Request",
                otModalTitle: "Work Order (WO)",
                kpiMonthly: "Monthly (720h)",
                kpiYearly: "Yearly (8,760h)",
                kpiAvailability: "Operational Availability",
                kpiMTBF: "MTBF (Reliability)",
                kpiMTTR: "MTTR (Repair Time)",
                kpiCompliance: "Preventive Compliance",
                exportMatrizExcel: "Export WO Matrix to Excel",
                exportCronogramaExcel: "Export Annual Schedule to Excel",
                printCorporatePDF: "Print Formal Report (PDF)"
            },
            ar: {
                appTitle: "نظام إدارة الصيانة GMAO Pro",
                navTitle: "وحدات إدارة الصيانة",
                navDashboard: "لوحة التحكم والمؤشرات",
                navSolicitudes: "الطلبات بين الأقسام",
                navCronograma: "الجدول الوقائي",
                navCronogramaAnual: "الجدول السنوي 2026",
                navSSL: "السلامة والصحة المهنية (SSL)",
                navRefrigeracion: "التبريد وسلسلة التبريد",
                navEquipos: "الأصول والمعدات",
                navOTs: "أوامر العمل (OT)",
                navAlmacen: "مستودع قطع الغيار",
                navProveedores: "الموردون",
                navCompras: "متابعة المشتريات",
                navInformes: "التقارير الدورية",
                navUsuarios: "المستخدمون والأمان",
                navMisOTs: "أوامر العمل الخاصة بي",
                navMisSolicitudes: "طلبات الأعطال",
                lblUser: "اسم المستخدم",
                lblPass: "كلمة المرور",
                lblRemember: "تذكرني على هذا الجهاز",
                btnLogin: "تسجيل الدخول",
                onlineBadge: "متصل بالشبكة",
                offlineBadge: "وضع غير متصل بالإنترنت",
                syncingBadge: "جارٍ المزامنة...",
                syncBtn: "مزامنة البيانات",
                installApp: "تثبيت التطبيق",
                notifTitle: "إشعارات النظام",
                markAllRead: "تحديد الكل كمقروء",
                btnCancel: "إلغاء",
                btnSaveOT: "حفظ أمر العمل",
                btnSubmitReq: "إرسال الطلب",
                btnSaveRoutine: "حفظ النشاط الوقائي",
                lblAsset: "المعدة / الأصل *",
                lblRoutine: "اسم النشاط / الإجراء *",
                lblTechs: "الفنيون المكلفون",
                planModalTitle: "جدولة الصيانة الوقائية",
                newReqTitle: "طلب صيانة بين الأقسام",
                otModalTitle: "أمر العمل (OT)",
                kpiMonthly: "شهري (720 ساعة)",
                kpiYearly: "سنوي (8,760 ساعة)",
                kpiAvailability: "الجاهزية التشغيلية",
                kpiMTBF: "متوسط الوقت بين الأعطال",
                kpiMTTR: "متوسط وقت الإصلاح",
                kpiCompliance: "نسبة الامتثال الوقائي",
                exportMatrizExcel: "تصدير مصفوفة أوامر العمل إلى Excel",
                exportCronogramaExcel: "تصدير الجدول السنوي إلى Excel",
                printCorporatePDF: "طباعة التقرير الرسمي (PDF)"
            }
        };

        let currentLanguage = localStorage.getItem('GMAO_LANG') || 'es';

        function t(key) {
            return (i18nTranslations[currentLanguage] && i18nTranslations[currentLanguage][key]) 
                || (i18nTranslations['es'] && i18nTranslations['es'][key]) 
                || key;
        }

        function changeLanguage(lang) {
            currentLanguage = lang;
            localStorage.setItem('GMAO_LANG', lang);
            const isRTL = (lang === 'ar');
            
            document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
            document.documentElement.setAttribute('lang', lang);
            
            // Traducir elementos estáticos con data-i18n
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const k = el.getAttribute('data-i18n');
                if (k && t(k)) el.textContent = t(k);
            });

            // Re-renderizar componentes dinámicos
            renderSidebar();
            renderHeaderUser();
            if (currentUser) {
                navigate(currentActiveView);
            }
        }

        // --- 2. ESTADO GLOBAL Y DATOS MAESTROS (EMPRESA: SALTYSNACK TUYERO C.A.) ---
                // --- CONECTIVIDAD MULTIPLATAFORMA DINÁMICA (ANDROID WEBVIEW / WINDOWS LAN / NUBE) ---
        function getApiUrl(endpoint) {
            if (!endpoint) return '';
            const path = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
            const loc = window.location;
            const protocol = (loc && loc.protocol && loc.protocol.startsWith('http')) ? loc.protocol : 'http:';
            const host = (loc && loc.hostname && loc.hostname.trim() !== '') ? loc.hostname : 'localhost';
            const port = (loc && loc.port) ? `:${loc.port}` : ((loc && loc.protocol && loc.protocol.startsWith('http')) ? '' : ':8000');
            return `${protocol}//${host}${port}${path}`;
        }

        const LOCAL_STORAGE_KEY = 'GMAO_INDUSTRIAL_ENTERPRISE_V33';
        let currentUser = null;
        let currentActiveView = 'dashboard';
        let kpiPeriodo = 'Mensual'; // 'Mensual' | 'Anual'
        let kpiSelectedMonth = '2026-10';
        let kpiSelectedYear = '2026';
        let kpiSelectedEquipo = 'TODOS';
        let offlineSyncQueue = [];

        // Estado de ordenamiento y filtros avanzados
        let equiposSortOrder = 'ASC';
        let informeFiltroEquipo = 'TODOS';
        let informeFiltroPeriodo = 'Mensual'; // 'Mensual', 'Anual', 'Rango'
        let informeMes = new Date().toISOString().slice(0, 7);
        let informeAnio = String(new Date().getFullYear());
        let informeFechaInicio = '';
        let informeFechaFin = '';

        // Estructura de informe personalizado
        let informeConfig = JSON.parse(localStorage.getItem('GMAO_INFORME_CFG') || JSON.stringify({
            titulo: 'INFORME DE GESTIÓN DE MANTENIMIENTO Y CONFIABILIDAD',
            subtitulo: 'SALTYSNACK TUYERO C.A. - DEPARTAMENTO DE MANTENIMIENTO E INFRAESTRUCTURA',
            diagnostico: 'Se evaluaron las líneas operativas manteniendo disponibilidad sobre la meta internacional (>95%) con mitigación inmediata de paradas.',
            recomendaciones: 'Monitorear holgura de mordazas de empaque y resguardos perimetrales.',
            secKPI: true,
            secGrafico: true,
            secOTs: true,
            secRepuestos: true,
            secSSL: true,
            secFirmas: true
        }));

        const initialData = {
            users: [
                { id: 'u1', username: 'admin', pass: '1234', name: 'Ing. Carlos Mendoza', role: 'Gerente', cargo: 'Jefe de Mantenimiento', departamento: 'Mantenimiento' },
                { id: 'u2', username: 'tecnico1', pass: '1234', name: 'Juan Pérez (Electromecánico)', role: 'Tecnico', cargo: 'Técnico Senior', departamento: 'Mantenimiento' },
                { id: 'u3', username: 'tecnico2', pass: '1234', name: 'Miguel Torres (Instrumentista)', role: 'Tecnico', cargo: 'Técnico Especialista', departamento: 'Mantenimiento' },
                { id: 'u4', username: 'solicitante1', pass: '1234', name: 'Roberto Gómez (Jefe Producción)', role: 'Solicitante', cargo: 'Jefe de Turno', departamento: 'Producción' },
                { id: 'u5', username: 'jefessl', pass: '1234', name: 'Ing. Argenis Morillo (Jefe SSL)', role: 'Jefe SSL', cargo: 'Jefe de Seguridad y Salud Laboral', departamento: 'Seguridad Industrial' },
                { id: 'u6', username: 'gerente_planta', pass: '1234', name: 'Ing. Roberto Navarro', role: 'Gerente', cargo: 'Gerente de Planta', departamento: 'Gerencia General' }
            ],
            config: {
                mttrTarget: 2.0,
                availabilityTarget: 95.0,
                alertDays: 5
            },
            equipos: [
                { id: 'EQ-101', name: 'Compresor de Aire Tornillo Principal', planta: 'Planta Central', linea: 'Servicios Generales', subensamble: 'Unidad de Compresión', criticidad: 'Alta', status: 'Operativo', es_refrigeracion: false, tipo_refrigerante: null },
                { id: 'EQ-102', name: 'Bomba Centrífuga Alimentadora #1', planta: 'Planta Central', linea: 'Línea de Envasado 1', subensamble: 'Motor y Sello Mecánico', criticidad: 'Alta', status: 'Operativo', es_refrigeracion: false, tipo_refrigerante: null },
                { id: 'EQ-103', name: 'Cinta Transportadora Principal', planta: 'Planta Central', linea: 'Empaque Final', subensamble: 'Reductor y Banda', criticidad: 'Media', status: 'Operativo', es_refrigeracion: false, tipo_refrigerante: null },
                { id: 'EQ-104', name: 'Horno Industrial de Curado', planta: 'Planta Norte', linea: 'Línea de Pintura', subensamble: 'Quemadores', criticidad: 'Baja', status: 'Operativo', es_refrigeracion: false, tipo_refrigerante: null },
                { id: 'EQ-105', name: 'Sistema de Refrigeración Industrial R-22', planta: 'Planta Norte', linea: 'Cadena de Frío', subensamble: 'Compresor y Condensador', criticidad: 'Alta', status: 'Operativo', es_refrigeracion: true, tipo_refrigerante: 'R-22' },
                { id: 'AC-201', name: 'Aire Acondicionado Central Sala de Control', planta: 'Planta Norte', linea: 'Climatización', subensamble: 'Evaporador / Compresor', criticidad: 'Media', status: 'Operativo', es_refrigeracion: true, tipo_refrigerante: 'R-410A' },
                { id: 'B01', name: 'Extrusora doble tornillo 1', planta: 'Planta Central', linea: 'Producción Snacks', subensamble: 'Cabezal y Reductor', criticidad: 'Alta', status: 'Operativo', es_refrigeracion: false, tipo_refrigerante: null },
                { id: 'B02', name: 'Extrusora doble tornillo 2', planta: 'Planta Central', linea: 'Producción Snacks', subensamble: 'Cabezal y Reductor', criticidad: 'Alta', status: 'Operativo', es_refrigeracion: false, tipo_refrigerante: null }
            ],
            repuestos: [
                { id: 'REP-01', codigo: 'SKF-6205', name: 'Rodamiento Rígido 6205 2RS', stock: 15, stockMin: 5, um: 'pza', costo: 14.50, proveedorId: 'PRV-01' },
                { id: 'REP-02', codigo: 'FIL-AIR-01', name: 'Filtro de Aire Industrial Compresor', stock: 3, stockMin: 2, um: 'pza', costo: 48.00, proveedorId: 'PRV-01' },
                { id: 'REP-03', codigo: 'ACE-IND-68', name: 'Aceite Sintético ISO VG 68', stock: 50, stockMin: 20, um: 'Litros', costo: 8.50, proveedorId: 'PRV-01' },
                { id: 'REP-04', codigo: 'GAS-R22', name: 'Cilindro Gas Refrigerante R-22 13.6kg', stock: 2, stockMin: 1, um: 'Cilindro', costo: 160.00, proveedorId: 'PRV-02' },
                { id: 'REP-05', codigo: 'SEL-MEC-32', name: 'Sello Mecánico Bomba 1.5 pulg', stock: 2, stockMin: 2, um: 'pza', costo: 85.00, proveedorId: 'PRV-01' },
                { id: 'REP-06', codigo: 'KIT-JUN-01', name: 'Kit de juntas / Limpiador mordazas', stock: 8, stockMin: 2, um: 'pza', costo: 32.00, proveedorId: 'PRV-01' }
            ],
            proveedores: [
                { id: 'PRV-01', rif: 'J-12345678-0', nombre: 'Suministros Industriales SKF C.A.', categoria: 'Rodamientos y Sellos', contacto: 'Marcos Rivas', telefono: '+58 212-5551234', email: 'ventas@skfsuministros.com' },
                { id: 'PRV-02', rif: 'J-87654321-9', nombre: 'Gases & Refrigeración Integral S.A.', categoria: 'Refrigeración y Climatización', contacto: 'Laura Morales', telefono: '+58 241-7778899', email: 'contacto@refrigeracionintegral.com' },
                { id: 'PRV-03', rif: 'J-55443322-1', nombre: 'ElectroMotores & Automatización del Centro', categoria: 'Electricidad e Instrumentación', contacto: 'Ing. David Salazar', telefono: '+58 241-9988776', email: 'ventas@electromotores.com' }
            ],
            comprasMateriales: [
                { id: 'COM-01', fecha: '2026-10-15', descripcion: 'Rodamiento Rígido SKF 6205', cantSolicitada: 10, cantRecibida: 10, moneda: '$', precio: 14.50, proveedorId: 'PRV-01', observaciones: 'Entregado conforme en almacén' },
                { id: 'COM-02', fecha: '2026-10-25', descripcion: 'Gas Refrigerante R-22 (Cilindro)', cantSolicitada: 2, cantRecibida: 1, moneda: '$', precio: 160.00, proveedorId: 'PRV-02', observaciones: 'Pendiente entrega de 1 cilindro adicional' }
            ],
            planesPreventivos: [
                { id: 'PLN-01', equipoId: 'EQ-101', nombre: 'Mantenimiento de Filtros y Lubricación', frecuencia: 'Mensual', frecuenciaTipo: 'meses', frecuenciaValor: 1, ultimaFecha: '2026-10-05', proximaFecha: '2026-11-05', tecnicoIds: ['u2'], esRefrigeracion: false },
                { id: 'PLN-02', equipoId: 'EQ-102', nombre: 'Inspección de Vibración y Sellos', frecuencia: 'Quincenal', frecuenciaTipo: 'dias', frecuenciaValor: 15, ultimaFecha: '2026-10-16', proximaFecha: '2026-10-31', tecnicoIds: ['u3'], esRefrigeracion: false },
                { id: 'PLN-03', equipoId: 'B01', nombre: 'Mantenimiento Preventivo Semanal Extrusora', frecuencia: 'Semanal', frecuenciaTipo: 'semanas', frecuenciaValor: 1, ultimaFecha: '2026-10-25', proximaFecha: '2026-11-01', tecnicoIds: ['u2', 'u3'], esRefrigeracion: false }
            ],
            planesRefrigeracion: [
                { id: 'PLR-01', equipoId: 'EQ-105', nombre: 'Limpieza de Condensadores y Revisión Presión R-22', frecuencia: 'Mensual', frecuenciaTipo: 'meses', frecuenciaValor: 1, ultimaFecha: '2026-10-02', proximaFecha: '2026-11-02', tecnicoIds: ['u2'], esRefrigeracion: true },
                { id: 'PLR-02', equipoId: 'AC-201', nombre: 'Mantenimiento Preventivo Unidades Manejadoras AC', frecuencia: 'Trimestral', frecuenciaTipo: 'meses', frecuenciaValor: 3, ultimaFecha: '2026-08-10', proximaFecha: '2026-11-10', tecnicoIds: ['u3'], esRefrigeracion: true }
            ],
            solicitudesInterdepartamentales: [
                { id: 'SOL-2026-001', tipo: 'Maquinaria / Equipo', urgencia: 'Alta', area: 'Producción - Envasado', ubicacion: 'Cinta Transportadora #3', descripcion: 'Fuga de aceite en reductor principal y vibración anormal.', solicitante: 'Roberto Gómez (Jefe Producción)', fechaHora: '2026-10-29 10:15', status: 'Aprobada', otVinculada: 'OT-2026-001' },
                { id: 'SOL-2026-002', tipo: 'Infraestructura', urgencia: 'Media', area: 'Almacén Central', ubicacion: 'Portón Eléctrico Principal', descripcion: 'Sensor fin de carrera descalibrado, apertura incompleta.', solicitante: 'Roberto Gómez (Jefe Producción)', fechaHora: '2026-11-01 08:30', status: 'En proceso', otVinculada: null },
                { id: 'SOL-2026-003', tipo: 'Maquinaria / Equipo', urgencia: 'Baja', area: 'Línea de Envasado 1', ubicacion: 'Bomba Centrífuga #1', descripcion: 'Revisión preventiva de sello mecánico por goteo leve.', solicitante: 'Roberto Gómez (Jefe Producción)', fechaHora: '2026-11-02 14:00', status: 'En espera de materiales', otVinculada: null }
            ],
            ots: [
                { id: 'OT-2026-001', tipo: 'Preventivo', prioridad: 'Alta', equipoId: 'EQ-103', descripcion: 'Ajuste de mordazas y alineación de banda empaque.', tecnicoIds: ['u2'], tecnicoAcompanante: 'u3', fechaAsignacion: '2026-10-15', fechaProgramada: '2026-10-20', fechaInicio: '2026-10-20T08:00', fechaFin: '2026-10-20T08:45', status: 'Concluida', actividades: 'Se calibraron mordazas térmicas y se cambió kit de juntas limpiadoras. Operativo sin novedad.', tiempoIntervencion: 0.75, tiempoParada: 0.75, fotoAntes: '', fotoDespues: '', repuestosUsados: [{ name: 'Kit de juntas / Limpiador mordazas', cant: 1, costo: 32.00 }] },
                { id: 'OT-2026-002', tipo: 'Correctivo', prioridad: 'Alta', equipoId: 'EQ-101', descripcion: 'Revisión por caída de presión en línea de aire comprimido.', tecnicoIds: ['u2', 'u3'], tecnicoAcompanante: 'u3', fechaAsignacion: '2026-10-25', fechaProgramada: '2026-10-25', fechaInicio: '2026-10-25T09:00', fechaFin: '2026-10-25T11:30', status: 'Concluida', actividades: 'Reemplazo de válvula solenoide y purga de condensados.', tiempoIntervencion: 2.5, tiempoParada: 2.5, fotoAntes: '', fotoDespues: '', repuestosUsados: [{ name: 'Filtro de Aire Industrial Compresor', cant: 1, costo: 48.00 }] },
                { id: 'OT-2026-003', tipo: 'Preventivo', prioridad: 'Media', equipoId: 'EQ-102', descripcion: 'Inspección de vibraciones y lubricación de rodamientos bomba.', tecnicoIds: ['u3'], tecnicoAcompanante: '', fechaAsignacion: '2026-11-01', fechaProgramada: '2026-11-02', fechaInicio: '', fechaFin: '', status: 'En Proceso', actividades: 'Pendiente completar medición de termografía.', tiempoIntervencion: 0.0, tiempoParada: 0.0, fotoAntes: '', fotoDespues: '', repuestosUsados: [] }
            ],
            solicitudesSSL: [
                { id: 'SSL-2026-001', codigo: 'COND-001', fechaHora: '2026-10-28 09:30', area: 'Planta Central - Envasado', ubicacion: 'Cinta Transportadora Principal', equipoId: 'EQ-103', nivelRiesgo: 'Alto', descripcion: 'Falta resguardo de seguridad en polea motriz, riesgo de atrapamiento mecánico para operadores.', accionPropuesta: 'Instalar guarda perimetral de policarbonato o malla metálica con enclavamiento.', solicitanteId: 'u5', solicitanteNombre: 'Ing. Argenis Morillo (Jefe SSL)', fotoEvidencia: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150" viewBox="0 0 200 150"><rect fill="%23fef3c7" width="200" height="150"/><text x="100" y="75" font-family="Arial" font-size="14" fill="%23b45309" text-anchor="middle">Foto Evidencia SSL</text></svg>', status: 'En Corrección', fechaCorreccion: null, otVinculada: 'OT-2026-001', observacionesCierre: 'Vinculado a OT para resguardo metálico.' }
            ],
            notificaciones: [
                { id: 'NOTIF-01', usuarioId: 'u1', rolDestino: 'Gerente', titulo: 'Nueva Solicitud Interdepartamental', mensaje: 'Producción reportó avería en Envasado (SOL-2026-001)', tipo: 'warning', leido: false, fechaHora: '2026-10-29 10:15', enlaceTipo: 'solicitud', enlaceId: 'SOL-2026-001' },
                { id: 'NOTIF-02', usuarioId: 'u1', rolDestino: 'Gerente', titulo: 'Condición Insegura Reportada (SSL)', mensaje: 'Ing. Argenis Morillo reportó condición de Alto Riesgo en Envasado', tipo: 'urgent', leido: false, fechaHora: '2026-10-28 09:35', enlaceTipo: 'ssl', enlaceId: 'SSL-2026-001' },
                { id: 'NOTIF-03', usuarioId: 'u2', rolDestino: 'Tecnico', titulo: 'Nueva OT Asignada', mensaje: 'Se le asignó la OT-2026-001: Mantenimiento de mordazas', tipo: 'info', leido: false, fechaHora: '2026-10-20 07:30', enlaceTipo: 'ot', enlaceId: 'OT-2026-001' },
                { id: 'NOTIF-04', usuarioId: 'u5', rolDestino: 'Jefe SSL', titulo: 'Actualización de Condición SSL', mensaje: 'La condición SSL-2026-001 ha pasado a estado En Corrección', tipo: 'success', leido: false, fechaHora: '2026-10-29 11:00', enlaceTipo: 'ssl', enlaceId: 'SSL-2026-001' }
            ]
        };

        let db = null;

        // --- 3. CARGA, PERSISTENCIA Y MOTOR DE SINCRONIZACIÓN OFFLINE-FIRST ---
        function loadDatabase() {
            try {
                const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
                if (stored) {
                    db = JSON.parse(stored);
                    // Asegurar arrays mínimos y configuración
                    if (!db.users) db.users = initialData.users;
                    if (!db.config) db.config = { mttrTarget: 2.0, availabilityTarget: 95.0, alertDays: 5 };
                    if (!db.solicitudesSSL) db.solicitudesSSL = initialData.solicitudesSSL;
                    if (!db.notificaciones) db.notificaciones = initialData.notificaciones;
                    if (!db.planesPreventivos) db.planesPreventivos = initialData.planesPreventivos;
                    if (!db.planesRefrigeracion) db.planesRefrigeracion = initialData.planesRefrigeracion;
                    if (!db.comprasMateriales) db.comprasMateriales = initialData.comprasMateriales;
                    // Asegurar presencia de usuario Gerente de Planta si faltara
                    if (!db.users.some(u => u.username === 'gerente_planta' || (u.cargo && u.cargo.includes('Gerente de Planta')))) {
                        db.users.push({ id: 'u6', username: 'gerente_planta', pass: '1234', name: 'Ing. Roberto Navarro', role: 'Gerente', cargo: 'Gerente de Planta', departamento: 'Gerencia General' });
                    }
                } else {
                    db = JSON.parse(JSON.stringify(initialData));
                    // Persistencia en DB central completada
                }
            } catch (e) {
                console.error("Error al cargar localStorage, usando datos iniciales:", e);
                db = JSON.parse(JSON.stringify(initialData));
            }
        }

        async function saveDatabase() {
            try {
                // Persistencia en DB central completada
                // Intentar sincronizar con backend en segundo plano
                if (navigator.onLine) {
                    sincronizarConServidorRemoto();
                } else {
                    setServerStatus(false);
                }
            } catch (e) {
                console.error("Error al guardar localmente:", e);
            }
        }

        async function sincronizarConServidorRemoto() {
            try {
                const payload = {
                    equipos: db.equipos,
                    repuestos: db.repuestos,
                    ots: db.ots,
                    solicitudesInterdepartamentales: db.solicitudesInterdepartamentales,
                    solicitudesSSL: db.solicitudesSSL,
                    comprasMateriales: db.comprasMateriales,
                    planesPreventivos: db.planesPreventivos,
                    planesRefrigeracion: db.planesRefrigeracion,
                    config: {
                        mttr_target_hours: (db.config && db.config.mttrTarget) ? db.config.mttrTarget : 2.0,
                        availability_target_pct: (db.config && db.config.availabilityTarget) ? db.config.availabilityTarget : 95.0,
                        preventive_alert_days: (db.config && db.config.alertDays) ? db.config.alertDays : 5
                    }
                };

                const res = await fetch('/api/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    setServerStatus(true);
                    // Obtener datos frescos del servidor
                    const getRes = await fetch('/api/sync');
                    if (getRes.ok) {
                        const sData = await getRes.json();
                        if (sData.success && sData.data) {
                            // Actualizar tablas maestras
                            if (sData.data.equipos) db.equipos = sData.data.equipos;
                            if (sData.data.repuestos) db.repuestos = sData.data.repuestos;
                            if (sData.data.ots) db.ots = sData.data.ots;
                            if (sData.data.solicitudesInterdepartamentales) db.solicitudesInterdepartamentales = sData.data.solicitudesInterdepartamentales;
                            if (sData.data.solicitudesSSL) db.solicitudesSSL = sData.data.solicitudesSSL;
                            if (sData.data.comprasMateriales) db.comprasMateriales = sData.data.comprasMateriales;
                            if (sData.data.planesPreventivos) db.planesPreventivos = sData.data.planesPreventivos;
                            if (sData.data.planesRefrigeracion) db.planesRefrigeracion = sData.data.planesRefrigeracion;
                            if (sData.data.notificaciones) db.notificaciones = sData.data.notificaciones;
                            if (sData.data.config) {
                                db.config = db.config || {};
                                if (sData.data.config.mttr_target_hours) db.config.mttrTarget = parseFloat(sData.data.config.mttr_target_hours);
                                if (sData.data.config.availability_target_pct) db.config.availabilityTarget = parseFloat(sData.data.config.availability_target_pct);
                                if (sData.data.config.preventive_alert_days) db.config.alertDays = parseInt(sData.data.config.preventive_alert_days);
                            }
                            // Persistencia en DB central completada
                            renderNotificaciones();
                            verificarAlertasPreventivasAnticipadas();
                        }
                    }
                } else {
                    setServerStatus(false);
                }
            } catch (err) {
                setServerStatus(false);
            }
        }

        // --- SISTEMA DE ALERTAS PREVENTIVAS A 5 DÍAS ---
        function verificarAlertasPreventivasAnticipadas() {
            if (!db) return;
            const hoy = new Date();
            const hoyStr = hoy.toISOString().slice(0, 10);
            let nuevasAlertas = 0;

            // 1. Revisar Planes Preventivos (para alertar exactamente 5 días previos a la proximaFecha)
            (db.planesPreventivos || []).forEach(p => {
                if (!p.proximaFecha) return;
                const pDate = new Date(p.proximaFecha.slice(0, 10) + 'T00:00:00');
                const hoyDate = new Date(hoyStr + 'T00:00:00');
                const diffTime = pDate.getTime() - hoyDate.getTime();
                const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

                if (diffDays === 5) {
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
                }
            });

            // 2. Revisar OTs Preventivas Programadas a 5 días
            (db.ots || []).forEach(o => {
                if (o.tipo !== 'Preventivo' || o.status === 'Concluida' || o.status === 'Completada') return;
                const fProg = o.fechaProgramada || o.fechaAsignacion;
                if (!fProg) return;
                const oDate = new Date(fProg.slice(0, 10) + 'T00:00:00');
                const hoyDate = new Date(hoyStr + 'T00:00:00');
                const diffTime = oDate.getTime() - hoyDate.getTime();
                const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

                if (diffDays === 5) {
                    const notifId = `NOTIF-OT-5D-${o.id}-${fProg.slice(0, 10)}`;
                    const yaExiste = (db.notificaciones || []).some(n => n.id === notifId);
                    if (!yaExiste) {
                        const eq = db.equipos.find(e => e.id === o.equipoId) || { name: o.equipoId };
                        const nuevaNotif = {
                            id: notifId,
                            usuarioId: null,
                            rolDestino: 'Gerente',
                            titulo: 'Alerta Preventiva (En 5 días)',
                            mensaje: `OT Preventiva ${o.id} en exactamente 5 días (${fProg.slice(0, 10)}): ${o.equipoId} - ${eq.name} (${o.descripcion.slice(0, 45)}).`,
                            tipo: 'warning',
                            leido: false,
                            fechaHora: new Date().toISOString().slice(0, 16).replace('T', ' '),
                            enlaceTipo: 'ot',
                            enlaceId: o.id
                        };
                        db.notificaciones.unshift(nuevaNotif);
                        nuevasAlertas++;
                    }
                }
            });

            if (nuevasAlertas > 0) {
                renderNotificaciones();
                mostrarToast('Alertas Preventivas', `Se detectaron ${nuevasAlertas} mantenimiento(s) preventivo(s) programados para dentro de 5 días.`, 'warning');
            }
        }

        // --- GESTIÓN DE CONFIGURACIÓN Y PARÁMETROS OPERATIVOS (MTTR) ---
        function openModalConfiguracionMTTR() {
            db.config = db.config || { mttrTarget: 2.0, availabilityTarget: 95.0, alertDays: 5 };
            document.getElementById('cfgMttrTarget').value = db.config.mttrTarget || 2.0;
            document.getElementById('cfgAvailabilityTarget').value = db.config.availabilityTarget || 95.0;
            document.getElementById('cfgPreventiveAlertDays').value = db.config.alertDays || 5;
            document.getElementById('modalConfiguracionMTTR').classList.remove('hidden');
        }

        async function guardarConfiguracionMTTR(e) {
            e.preventDefault();
            const mttrVal = parseFloat(document.getElementById('cfgMttrTarget').value) || 2.0;
            const availVal = parseFloat(document.getElementById('cfgAvailabilityTarget').value) || 95.0;
            const alertDaysVal = parseInt(document.getElementById('cfgPreventiveAlertDays').value) || 5;

            db.config = db.config || {};
            db.config.mttrTarget = mttrVal;
            db.config.availabilityTarget = availVal;
            db.config.alertDays = alertDaysVal;

            saveDatabase();

            // Persistir en servidor vía API REST
            if (navigator.onLine) {
                try {
                    await fetch('/api/config', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            mttr_target_hours: mttrVal,
                            availability_target_pct: availVal,
                            preventive_alert_days: alertDaysVal
                        })
                    });
                } catch (err) {
                    console.warn("No se pudo persistir en backend de inmediato:", err);
                }
            }

            closeModal('modalConfiguracionMTTR');
            mostrarToast('Parámetros Guardados', `Umbral mínimo de MTTR actualizado a ${mttrVal} h.`, 'success');
            if (currentActiveView === 'dashboard') {
                renderDashboardView(document.getElementById('mainView'));
            }
        }

        function setServerStatus(online) {
            const badge = document.getElementById('syncStatusBadge');
            const txt = document.getElementById('syncStatusText');
            if (!badge || !txt) return;

            if (online) {
                badge.className = 'inline-flex items-center text-emerald-400 font-medium';
                badge.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-1"></span> <span>' + t('onlineBadge') + '</span>';
            } else {
                badge.className = 'inline-flex items-center text-amber-400 font-medium';
                badge.innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-400 mr-1"></span> <span>' + t('offlineBadge') + '</span>';
            }
        }

        async function sincronizarDatos() {
            const icon = document.getElementById('syncIcon');
            if (icon) icon.classList.add('fa-spin');
            mostrarToast('Sincronización', 'Conectando con el servidor central de planta...', 'info');

            await sincronizarConServidorRemoto();

            setTimeout(() => {
                if (icon) icon.classList.remove('fa-spin');
                mostrarToast('Sincronización Completa', 'Base de datos conciliada con éxito.', 'success');
                navigate(currentActiveView);
            }, 800);
        }

        function exportarBaseCompletaJSON() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(db, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", `GMAO_BACKUP_SALTYSNACK_${new Date().toISOString().slice(0,10)}.json`);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        }

        // --- 4. MOTOR DE NOTIFICACIONES DINÁMICAS POR ROLES Y EVENTOS ---
        function dispararNotificacion(rolDestino, usuarioId, titulo, mensaje, tipo = 'info', enlaceTipo = null, enlaceId = null) {
            const notif = {
                id: 'NOTIF-' + Date.now().toString(36),
                usuarioId: usuarioId,
                rolDestino: rolDestino,
                titulo: titulo,
                mensaje: mensaje,
                tipo: tipo, // 'info', 'warning', 'urgent', 'success'
                leido: false,
                fechaHora: new Date().toISOString().replace('T', ' ').slice(0, 16),
                enlaceTipo: enlaceTipo,
                enlaceId: enlaceId
            };

            db.notificaciones.unshift(notif);
            saveDatabase();
            renderNotificaciones();

            // Si el usuario actual tiene el rol destino, mostrar Toast
            if (currentUser && (rolDestino === currentUser.role || usuarioId === currentUser.id || !rolDestino)) {
                mostrarToast(titulo, mensaje, tipo);
            }
        }

        function renderNotificaciones() {
            if (!currentUser || !db.notificaciones) return;
            const notifBadge = document.getElementById('notifBadge');
            const notifList = document.getElementById('notifList');

            // Filtrar notificaciones para el rol o usuario actual
            const userNotifs = db.notificaciones.filter(n => 
                !n.rolDestino || n.rolDestino === currentUser.role || n.usuarioId === currentUser.id
            );

            const noLeidas = userNotifs.filter(n => !n.leido).length;
            if (notifBadge) {
                if (noLeidas > 0) {
                    notifBadge.textContent = noLeidas > 9 ? '9+' : noLeidas;
                    notifBadge.classList.remove('hidden');
                } else {
                    notifBadge.classList.add('hidden');
                }
            }

            if (!notifList) return;
            if (userNotifs.length === 0) {
                notifList.innerHTML = '<div class="p-4 text-center text-slate-400">Sin notificaciones pendientes</div>';
                return;
            }

            notifList.innerHTML = userNotifs.slice(0, 15).map(n => {
                let iconColor = 'text-blue-500';
                let iconName = 'fa-info-circle';
                if (n.tipo === 'warning') { iconColor = 'text-amber-500'; iconName = 'fa-exclamation-triangle'; }
                if (n.tipo === 'urgent') { iconColor = 'text-red-500'; iconName = 'fa-radiation'; }
                if (n.tipo === 'success') { iconColor = 'text-emerald-500'; iconName = 'fa-check-circle'; }

                return `
                    <div class="p-2.5 hover:bg-slate-50 transition cursor-pointer flex items-start space-x-2.5 ${n.leido ? 'opacity-60' : 'bg-blue-50/30'}" onclick="clickNotificacion('${n.id}')">
                        <i class="fas ${iconName} ${iconColor} mt-0.5 text-sm"></i>
                        <div class="flex-1 min-w-0">
                            <div class="font-bold text-[11px] text-slate-800 leading-tight">${n.titulo}</div>
                            <div class="text-[10px] text-slate-600 truncate mt-0.5">${n.mensaje}</div>
                            <div class="text-[9px] text-slate-400 mt-1">${n.fechaHora}</div>
                        </div>
                        ${!n.leido ? `<button onclick="event.stopPropagation(); marcarNotificacionLeida('${n.id}')" class="text-[9px] text-blue-600 hover:underline">Leída</button>` : ''}
                    </div>
                `;
            }).join('');
        }

        function clickNotificacion(notifId) {
            const notif = db.notificaciones.find(n => n.id === notifId);
            if (!notif) return;
            notif.leido = true;
            saveDatabase();
            renderNotificaciones();
            toggleNotificationPanel();

            // Navegar según el tipo de enlace
            if (notif.enlaceTipo === 'ot') navigate('ots');
            else if (notif.enlaceTipo === 'solicitud') navigate(currentUser.role === 'Gerente' ? 'solicitudes-gerente' : 'mis-solicitudes');
            else if (notif.enlaceTipo === 'ssl') navigate('ssl');
        }

        function marcarNotificacionLeida(notifId) {
            const notif = db.notificaciones.find(n => n.id === notifId);
            if (notif) {
                notif.leido = true;
                saveDatabase();
                renderNotificaciones();
            }
        }

        function marcarTodasNotificacionesLeidas() {
            if (!currentUser || !db.notificaciones) return;
            db.notificaciones.forEach(n => {
                if (!n.rolDestino || n.rolDestino === currentUser.role || n.usuarioId === currentUser.id) {
                    n.leido = true;
                }
            });
            saveDatabase();
            renderNotificaciones();
        }

        function toggleNotificationPanel() {
            const p = document.getElementById('notifDropdown');
            if (p) p.classList.toggle('hidden');
        }

        function mostrarToast(titulo, mensaje, tipo = 'info') {
            const container = document.getElementById('toastContainer');
            if (!container) return;

            let borderClass = 'border-blue-500 text-blue-700 bg-white';
            let icon = 'fa-info-circle text-blue-500';
            if (tipo === 'warning') { borderClass = 'border-amber-500 text-amber-700 bg-white'; icon = 'fa-exclamation-triangle text-amber-500'; }
            if (tipo === 'urgent') { borderClass = 'border-red-600 text-red-700 bg-white'; icon = 'fa-radiation text-red-600'; }
            if (tipo === 'success') { borderClass = 'border-emerald-500 text-emerald-700 bg-white'; icon = 'fa-check-circle text-emerald-500'; }

            const toast = document.createElement('div');
            toast.className = `toast-item border-l-4 shadow-xl rounded-lg p-3 max-w-sm flex items-start space-x-2 text-xs border ${borderClass}`;
            toast.innerHTML = `
                <i class="fas ${icon} text-base mt-0.5"></i>
                <div class="flex-1">
                    <div class="font-bold text-slate-800 text-[11px]">${titulo}</div>
                    <div class="text-[10px] text-slate-600 mt-0.5">${mensaje}</div>
                </div>
            `;
            container.appendChild(toast);

            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(-10px)';
                setTimeout(() => toast.remove(), 300);
            }, 4000);
        }

        // --- UTILIDAD DE ORDENAMIENTO ALFANUMÉRICO NATURAL (ISO / SMRP) ---
        function naturalCompare(a, b, asc = true) {
            const strA = (a === null || a === undefined) ? '' : String(a);
            const strB = (b === null || b === undefined) ? '' : String(b);
            const res = strA.localeCompare(strB, undefined, { numeric: true, sensitivity: 'base' });
            return asc ? res : -res;
        }

        // --- 5. COMPRESIÓN MULTIMEDIA Y VISOR LIGHTBOX ---
        function procesarFotoConCompresion(inputElement, hiddenInputId, previewContainerId) {
            const file = inputElement.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    const MAX_WIDTH = 1024;
                    const MAX_HEIGHT = 1024;
                    let width = img.width;
                    let height = img.height;

                    if (width > height) {
                        if (width > MAX_WIDTH) {
                            height *= MAX_WIDTH / width;
                            width = MAX_WIDTH;
                        }
                    } else {
                        if (height > MAX_HEIGHT) {
                            width *= MAX_HEIGHT / height;
                            height = MAX_HEIGHT;
                        }
                    }

                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);

                    const compressedBase64 = canvas.toDataURL('image/jpeg', 0.72);
                    document.getElementById(hiddenInputId).value = compressedBase64;

                    const previewContainer = document.getElementById(previewContainerId);
                    if (previewContainer) {
                        previewContainer.innerHTML = `
                            <div class="relative inline-block border rounded-lg p-1 bg-white shadow-sm mt-1">
                                <img src="${compressedBase64}" class="w-16 h-16 object-cover rounded cursor-pointer" onclick="openLightbox('${compressedBase64}', 'Evidencia Cargada', 'Fotografía optimizada en terreno')">
                                <span class="absolute -top-1 -right-1 bg-emerald-500 text-white rounded-full w-4 h-4 text-[9px] flex items-center justify-center"><i class="fas fa-check"></i></span>
                            </div>
                        `;
                    }
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        function openLightbox(imgSrc, title = "Evidencia Fotográfica", desc = "") {
            if (!imgSrc) return;
            document.getElementById('lightboxImage').src = imgSrc;
            document.getElementById('lightboxTitle').textContent = title;
            document.getElementById('lightboxDescription').textContent = desc;
            document.getElementById('modalLightbox').classList.remove('hidden');
        }

        // --- 6. AUTENTICACIÓN Y ROLES PRODUCTIVOS AUTORIZADOS ---
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const usr = document.getElementById('loginUsername').value.trim();
            const pass = document.getElementById('loginPassword').value.trim();

            const found = db.users.find(u => u.username.toLowerCase() === usr.toLowerCase() && u.pass === pass);
            if (found) {
                currentUser = found;
                if (document.getElementById('rememberUserCheckbox').checked) {
                    localStorage.setItem('GMAO_REM_USER', usr);
                    localStorage.setItem('GMAO_REM_PASS', pass);
                } else {
                    localStorage.removeItem('GMAO_REM_USER');
                    localStorage.removeItem('GMAO_REM_PASS');
                }
                document.getElementById('loginModal').classList.add('hidden');
                initApp();
            } else {
                alert("Credenciales incorrectas. Verifique su usuario y contraseña.");
            }
        });

        function logout() {
            currentUser = null;
            document.getElementById('loginModal').classList.remove('hidden');
            document.getElementById('loginUsername').value = '';
            document.getElementById('loginPassword').value = '';
        }

        function initApp() {
            renderHeaderUser();
            renderSidebar();
            renderNotificaciones();
            // Selección de vista por defecto según rol
            if (currentUser.role === 'Gerente') navigate('dashboard');
            else if (currentUser.role === 'Tecnico') navigate('mis-ots');
            else if (currentUser.role === 'Jefe SSL') navigate('ssl');
            else if (currentUser.role === 'Solicitante') navigate('mis-solicitudes');
            else navigate('dashboard');
        }

        function renderHeaderUser() {
            const area = document.getElementById('userMenuArea');
            if (!currentUser) { area.innerHTML = ''; return; }
            area.innerHTML = `
                <div class="flex items-center space-x-2 bg-slate-800 border border-slate-700 py-1 px-2.5 rounded-lg text-xs">
                    <div class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-[10px]">
                        ${currentUser.name.charAt(0)}
                    </div>
                    <div class="hidden sm:block text-left">
                        <div class="font-bold text-slate-200 text-[11px] leading-tight">${currentUser.name.split(' ')[0]}</div>
                        <div class="text-[9px] text-blue-400 font-mono">${currentUser.role}</div>
                    </div>
                    <button onclick="logout()" class="text-slate-400 hover:text-red-400 p-1" title="Cerrar Sesión">
                        <i class="fas fa-sign-out-alt"></i>
                    </button>
                </div>
            `;
        }

        function toggleSidebarMenu() {
            const sb = document.getElementById('sidebar');
            const bd = document.getElementById('sidebarBackdrop');
            sb.classList.toggle('-translate-x-full');
            bd.classList.toggle('hidden');
        }

        document.getElementById('toggleSidebar').addEventListener('click', toggleSidebarMenu);

        function renderSidebar() {
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
            } else if (currentUser.role === 'Tecnico') {
                nav.innerHTML = `
                    <button onclick="navigate('mis-ots')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-mis-ots">
                        <i class="fas fa-tasks w-4 text-blue-400"></i><span>${t('navMisOTs')}</span>
                    </button>
                    <button onclick="openModalOT(false)" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold bg-amber-600 hover:bg-amber-700 text-white transition mt-4 shadow">
                        <i class="fas fa-bolt w-4"></i><span>Reportar OT Inmediata</span>
                    </button>
                `;
            } else if (currentUser.role === 'Solicitante') {
                nav.innerHTML = `
                    <button onclick="navigate('mis-solicitudes')" class="sidebar-btn w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-semibold hover:bg-slate-800 transition" id="nav-mis-solicitudes">
                        <i class="fas fa-paper-plane w-4 text-blue-400"></i><span>${t('navMisSolicitudes')}</span>
                    </button>
                `;
            }
        }

        function navigate(viewName) {
            currentActiveView = viewName;
            document.querySelectorAll('.sidebar-btn').forEach(b => b.classList.remove('bg-slate-800', 'text-white'));
            const activeNav = document.getElementById(`nav-${viewName}`);
            if (activeNav) activeNav.classList.add('bg-slate-800', 'text-white');

            // Cerrar menú móvil si está abierto
            const sb = document.getElementById('sidebar');
            const bd = document.getElementById('sidebarBackdrop');
            if (!sb.classList.contains('-translate-x-full')) {
                sb.classList.add('-translate-x-full');
                bd.classList.add('hidden');
            }

            const main = document.getElementById('mainView');

            switch(viewName) {
                case 'dashboard': renderDashboardView(main); break;
                case 'cronograma-anual': renderCronogramaAnualView(main); break;
                case 'cronograma-refrigeracion': renderCronogramaView(main, true); break;
                case 'ssl': renderSSLView(main); break;
                case 'equipos': renderEquiposView(main); break;
                case 'ots': renderOTsView(main); break;
                case 'mis-ots': renderMisOTsView(main); break;
                case 'almacen': renderAlmacenView(main); break;
                case 'proveedores': renderProveedoresView(main); break;
                case 'compras': renderComprasView(main); break;
                case 'informes': renderInformesView(main); break;
                case 'usuarios': renderUsuariosView(main); break;
                case 'solicitudes-gerente': renderSolicitudesGerenteView(main); break;
                case 'mis-solicitudes': renderMisSolicitudesView(main); break;
                default: renderDashboardView(main);
            }
        }
""")

print("Parte 3 anexada exitosamente.")
# =============================================================================
# PARTE 4: VISTAS PRINCIPALES (KPIS CON FILTRO PERIODO, CRONOGRAMA, SSL, ETC.)
# =============================================================================
parts.append("""
        // --- 7. VISTA DASHBOARD & KPIS CON SELECTOR DINÁMICO DE PERIODO ---
        function setKpiPeriodo(periodo) {
            kpiPeriodo = periodo;
            navigate('dashboard');
        }

        function cambiarKpiMes(mes) {
            kpiSelectedMonth = mes;
            navigate('dashboard');
        }

        function cambiarKpiAnio(anio) {
            kpiSelectedYear = anio;
            navigate('dashboard');
        }

        function cambiarFiltroKpiEquipo(eqId) {
            kpiSelectedEquipo = eqId;
            navigate('dashboard');
        }

        function renderDashboardView(container) {
            // Cálculo en cliente de KPIs según periodo seleccionado
            const horasBase = (kpiPeriodo === 'Anual') ? 8760.0 : 720.0;
            const periodoLabel = (kpiPeriodo === 'Anual') ? `Año ${kpiSelectedYear}` : `Mes ${kpiSelectedMonth}`;

            // Filtrar OTs evaluadas por equipo y por fecha de periodo
            let otsEvaluadas = db.ots;
            if (kpiSelectedEquipo !== 'TODOS') {
                otsEvaluadas = otsEvaluadas.filter(o => o.equipoId === kpiSelectedEquipo);
            }

            if (kpiPeriodo === 'Anual') {
                otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '').startsWith(kpiSelectedYear));
            } else {
                otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '').startsWith(kpiSelectedMonth));
            }

            const totalOTs = otsEvaluadas.length;
            const concluidas = otsEvaluadas.filter(o => o.status === 'Concluida' || o.status === 'Completada');
            const preventivas = otsEvaluadas.filter(o => o.tipo === 'Preventivo');
            const preventivasConcluidas = preventivas.filter(o => o.status === 'Concluida' || o.status === 'Completada');
            const correctivas = otsEvaluadas.filter(o => o.tipo === 'Correctivo');
            const correctivasConcluidas = correctivas.filter(o => o.status === 'Concluida' || o.status === 'Completada');

            const totalDowntime = otsEvaluadas.reduce((acc, o) => acc + parseFloat(o.tiempoParada || 0.0), 0.0);
            const totalIntervencion = concluidas.reduce((acc, o) => acc + parseFloat(o.tiempoIntervencion || 0.0), 0.0);
            const totalIntervencionCorrectiva = correctivasConcluidas.reduce((acc, o) => acc + parseFloat(o.tiempoIntervencion || 0.0), 0.0);

            // Disponibilidad Operativa
            const horasOperadas = Math.max(0.0, horasBase - totalDowntime);
            const disponibilidadPct = Math.min(100.0, Math.round((horasOperadas / horasBase) * 1000) / 10);

            // MTTR y MTBF
            const numFallas = correctivasConcluidas.length;
            const mttr = numFallas > 0 ? (Math.round((totalIntervencionCorrectiva / numFallas) * 10) / 10) : 0.0;
            const mtbf = numFallas > 0 ? (Math.round((horasOperadas / numFallas) * 10) / 10) : Math.round(horasBase);
            const mttrMeta = (db.config && db.config.mttrTarget) ? parseFloat(db.config.mttrTarget) : 2.0;

            // Cumplimiento Preventivo
            const cumplimientoPrevPct = preventivas.length > 0 ? Math.round((preventivasConcluidas.length / preventivas.length) * 100) : 100;

            container.innerHTML = `
                <div class="space-y-4">
                    <!-- BARRA SUPERIOR DE FILTRO GLOBAL DE PERIODO -->
                    <div class="bg-white p-3 sm:p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                        <div class="flex items-center space-x-2">
                            <div class="w-9 h-9 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold">
                                <i class="fas fa-filter"></i>
                            </div>
                            <div>
                                <h2 class="text-sm sm:text-base font-bold text-slate-800">Panel Gerencial de Indicadores (KPIs)</h2>
                                <p class="text-[11px] text-slate-500">Evaluación SMRP / ISO 14224 | SALTYSNACK TUYERO C.A.</p>
                            </div>
                        </div>

                        <!-- SELECTOR GLOBAL MENSUAL / ANUAL Y SELECTOR ESPECÍFICO -->
                        <div class="flex flex-wrap items-center gap-2">
                            <div class="flex items-center bg-slate-100 p-1 rounded-lg border">
                                <button onclick="setKpiPeriodo('Mensual')" class="px-2.5 py-1 rounded text-xs font-bold transition ${kpiPeriodo === 'Mensual' ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:text-slate-900'}">
                                    <i class="fas fa-calendar-day mr-1"></i> ${t('kpiMonthly')}
                                </button>
                                <button onclick="setKpiPeriodo('Anual')" class="px-2.5 py-1 rounded text-xs font-bold transition ${kpiPeriodo === 'Anual' ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:text-slate-900'}">
                                    <i class="fas fa-calendar-alt mr-1"></i> ${t('kpiYearly')}
                                </button>
                            </div>

                            ${kpiPeriodo === 'Mensual' ? `
                                <div class="flex items-center space-x-1">
                                    <span class="text-[11px] font-semibold text-slate-600">Mes:</span>
                                    <input type="month" value="${kpiSelectedMonth}" onchange="cambiarKpiMes(this.value)" class="border rounded-lg px-2 py-1 text-xs bg-white outline-none font-medium">
                                </div>
                            ` : `
                                <div class="flex items-center space-x-1">
                                    <span class="text-[11px] font-semibold text-slate-600">Año:</span>
                                    <select onchange="cambiarKpiAnio(this.value)" class="border rounded-lg px-2 py-1 text-xs bg-white outline-none font-medium">
                                        <option value="2026" ${kpiSelectedYear === '2026' ? 'selected' : ''}>2026</option>
                                        <option value="2025" ${kpiSelectedYear === '2025' ? 'selected' : ''}>2025</option>
                                        <option value="2024" ${kpiSelectedYear === '2024' ? 'selected' : ''}>2024</option>
                                    </select>
                                </div>
                            `}

                            <div class="flex items-center space-x-1">
                                <span class="text-[11px] font-semibold text-slate-600">Equipo:</span>
                                <select onchange="cambiarFiltroKpiEquipo(this.value)" class="border rounded-lg px-2 py-1 text-xs bg-white outline-none font-medium max-w-[150px] truncate">
                                    <option value="TODOS" ${kpiSelectedEquipo === 'TODOS' ? 'selected' : ''}>[ Todos los Equipos ]</option>
                                    ${db.equipos.map(e => `<option value="${e.id}" ${kpiSelectedEquipo === e.id ? 'selected' : ''}>${e.id} - ${e.name}</option>`).join('')}
                                </select>
                            </div>

                            <button onclick="exportarMatrizOTExcel()" class="bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1.5 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition" title="Exportar Matriz O.T. a Excel con Dashboard">
                                <i class="fas fa-file-excel"></i>
                                <span class="hidden sm:inline">Matriz Excel</span>
                            </button>
                        </div>
                    </div>

                    <!-- TARJETAS DE INDICADORES PRINCIPALES SEGÚN PERIODO -->
                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
                        <!-- DISPONIBILIDAD OPERATIVA -->
                        <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[11px] font-bold uppercase tracking-wider text-slate-500">${t('kpiAvailability')}</div>
                                    <div class="text-2xl sm:text-3xl font-black ${disponibilidadPct >= 95 ? 'text-blue-700' : 'text-amber-600'} mt-1">
                                        ${disponibilidadPct}%
                                    </div>
                                </div>
                                <div class="w-8 h-8 rounded-lg ${disponibilidadPct >= 95 ? 'bg-blue-100 text-blue-600' : 'bg-amber-100 text-amber-600'} flex items-center justify-center text-sm">
                                    <i class="fas fa-tachometer-alt"></i>
                                </div>
                            </div>
                            <div class="mt-2 text-[10px] text-slate-500 flex justify-between items-center">
                                <span>Meta: &ge;95.0%</span>
                                <span class="font-semibold text-slate-700">Downtime: ${totalDowntime.toFixed(1)} h</span>
                            </div>
                            <div class="w-full bg-slate-100 rounded-full h-1.5 mt-1.5 overflow-hidden">
                                <div class="${disponibilidadPct >= 95 ? 'bg-blue-600' : 'bg-amber-500'} h-1.5 rounded-full" style="width: ${Math.min(100, disponibilidadPct)}%"></div>
                            </div>
                        </div>

                        <!-- MTBF -->
                        <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[11px] font-bold uppercase tracking-wider text-slate-500">${t('kpiMTBF')}</div>
                                    <div class="text-2xl sm:text-3xl font-black text-indigo-700 mt-1">${mtbf} <span class="text-xs font-normal text-slate-500">h</span></div>
                                </div>
                                <div class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm">
                                    <i class="fas fa-heartbeat"></i>
                                </div>
                            </div>
                            <div class="mt-2 text-[10px] text-slate-500 flex justify-between items-center">
                                <span>Tiempo Medio Entre Fallas</span>
                                <span class="font-semibold text-slate-700">${numFallas} averías</span>
                            </div>
                        </div>

                        <!-- MTTR -->
                        <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center">
                                        <span>${t('kpiMTTR')}</span>
                                        <button onclick="openModalConfiguracionMTTR()" class="text-slate-400 hover:text-blue-600 ml-1.5" title="Configurar umbral mínimo MTTR">
                                            <i class="fas fa-cog"></i>
                                        </button>
                                    </div>
                                    <div class="text-2xl sm:text-3xl font-black ${mttr <= mttrMeta ? 'text-emerald-700' : 'text-amber-600'} mt-1">${mttr} <span class="text-xs font-normal text-slate-500">h</span></div>
                                </div>
                                <div class="w-8 h-8 rounded-lg ${mttr <= mttrMeta ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'} flex items-center justify-center text-sm">
                                    <i class="fas fa-tools"></i>
                                </div>
                            </div>
                            <div class="mt-2 text-[10px] text-slate-500 flex justify-between items-center">
                                <span>Tiempo Medio de Reparación</span>
                                <span class="font-semibold text-slate-700 cursor-pointer hover:text-blue-600" onclick="openModalConfiguracionMTTR()" title="Haga clic para modificar">&le; ${mttrMeta.toFixed(1)} h meta <i class="fas fa-edit text-[9px] ml-0.5"></i></span>
                            </div>
                        </div>

                        <!-- CUMPLIMIENTO PREVENTIVO -->
                        <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="text-[11px] font-bold uppercase tracking-wider text-slate-500">${t('kpiCompliance')}</div>
                                    <div class="text-2xl sm:text-3xl font-black ${cumplimientoPrevPct >= 90 ? 'text-teal-700' : 'text-amber-600'} mt-1">${cumplimientoPrevPct}%</div>
                                </div>
                                <div class="w-8 h-8 rounded-lg bg-teal-100 text-teal-600 flex items-center justify-center text-sm">
                                    <i class="fas fa-clipboard-check"></i>
                                </div>
                            </div>
                            <div class="mt-2 text-[10px] text-slate-500 flex justify-between items-center">
                                <span>Preventivas: ${preventivasConcluidas.length}/${preventivas.length}</span>
                                <span class="font-semibold text-slate-700">${totalOTs} OTs Totales</span>
                            </div>
                            <div class="w-full bg-slate-100 rounded-full h-1.5 mt-1.5 overflow-hidden">
                                <div class="bg-teal-600 h-1.5 rounded-full" style="width: ${Math.min(100, cumplimientoPrevPct)}%"></div>
                            </div>
                        </div>
                    </div>

                    <!-- GRÁFICO DE CONFIABILIDAD Y RESUMEN OPERATIVO -->
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm lg:col-span-2">
                            <div class="flex items-center justify-between mb-3 border-b pb-2">
                                <h3 class="font-bold text-xs text-slate-800 flex items-center">
                                    <i class="fas fa-chart-bar text-blue-600 mr-2"></i> Distribución Operativa por Tipo de Mantenimiento (${periodoLabel})
                                </h3>
                                <span class="text-[11px] text-slate-500 font-mono">Base: ${horasBase} h</span>
                            </div>
                            <div class="h-60 relative">
                                <canvas id="chartDashboardKPIs"></canvas>
                            </div>
                        </div>

                        <!-- TARJETA DE DIAGNÓSTICO Y ACCIONES -->
                        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div>
                                <h3 class="font-bold text-xs text-slate-800 mb-2 flex items-center">
                                    <i class="fas fa-clipboard-list text-indigo-600 mr-2"></i> Diagnóstico Operativo de Planta
                                </h3>
                                <div class="p-3 rounded-lg text-xs leading-relaxed ${disponibilidadPct >= 95 ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-amber-50 text-amber-800 border border-amber-200'}">
                                    <div class="font-bold mb-1">${disponibilidadPct >= 95 ? 'Condición Operativa Conforme (>95%)' : 'Alerta de Confiabilidad'}</div>
                                    <p class="text-[11px]">En el periodo <strong>${periodoLabel}</strong> se registraron ${totalOTs} intervenciones con ${totalDowntime.toFixed(1)} h de parada y ${totalIntervencion.toFixed(1)} h de trabajo técnico.</p>
                                </div>

                                <div class="mt-3 space-y-2 text-xs">
                                    <div class="flex justify-between py-1 border-b">
                                        <span class="text-slate-500">Horas Planificadas:</span>
                                        <span class="font-bold text-slate-800">${horasBase} h</span>
                                    </div>
                                    <div class="flex justify-between py-1 border-b">
                                        <span class="text-slate-500">Horas Reales de Producción:</span>
                                        <span class="font-bold text-blue-700">${horasOperadas.toFixed(1)} h</span>
                                    </div>
                                    <div class="flex justify-between py-1 border-b">
                                        <span class="text-slate-500">Total OTs Concluidas:</span>
                                        <span class="font-bold text-emerald-700">${concluidas.length}</span>
                                    </div>
                                </div>
                            </div>

                            <div class="pt-3 border-t mt-4 flex flex-col gap-2">
                                <button onclick="imprimirDashboardKPI()" class="w-full bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold py-2.5 rounded-lg flex items-center justify-center space-x-2 transition shadow">
                                    <i class="fas fa-print"></i>
                                    <span>${t('printCorporatePDF')}</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Inicializar gráfico Chart.js
            setTimeout(() => {
                const ctx = document.getElementById('chartDashboardKPIs');
                if (!ctx) return;
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['Preventivas', 'Correctivas', 'Completadas', 'Downtime (h)', 'Intervención (h)'],
                        datasets: [{
                            label: `Carga ${periodoLabel}`,
                            data: [preventivas.length, correctivas.length, concluidas.length, totalDowntime, totalIntervencion],
                            backgroundColor: [
                                'rgba(16, 185, 129, 0.7)',
                                'rgba(239, 68, 68, 0.7)',
                                'rgba(59, 130, 246, 0.7)',
                                'rgba(245, 158, 11, 0.7)',
                                'rgba(99, 102, 241, 0.7)'
                            ],
                            borderColor: [
                                '#10b981', '#ef4444', '#3b82f6', '#f59e0b', '#6366f1'
                            ],
                            borderWidth: 1.5,
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: { y: { beginAtZero: true } }
                    }
                });
            }, 50);
        }

        // --- 8. VISTA CRONOGRAMA ANUAL PREVENTIVO MULTIANUAL CON LÓGICA DE FRECUENCIAS ---
        let cronogramaAnioSeleccionado = 2026;

        function cambiarCronogramaAnio(nuevoAnio) {
            cronogramaAnioSeleccionado = parseInt(nuevoAnio);
            renderCronogramaAnualView(document.getElementById('mainView'));
        }

        function exportarCronogramaAnualExcel() {
            const anio = cronogramaAnioSeleccionado || 2026;
            if (navigator.onLine) {
                window.location.href = `/api/reports/cronograma-anual-excel?anio=${anio}`;
                mostrarToast('Descargando Cronograma', `Generando archivo Excel del Cronograma ${anio}...`, 'success');
                return;
            }
            alert(`Exportación offline: guardando archivo de texto tabulado para el cronograma anual ${anio}.`);
        }

        function renderCronogramaAnualView(container) {
            const anio = cronogramaAnioSeleccionado || 2026;
            const mesesNombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

            const rowsHtml = db.planesPreventivos.map(p => {
                const eq = db.equipos.find(e => e.id === p.equipoId) || { name: p.equipoId, linea: 'General' };
                
                // Cálculo de meses proyectados para el año seleccionado sin alterar otros años
                const mesesProyectados = new Set();
                let step = 1;
                if (p.frecuenciaTipo === 'dias') {
                    step = Math.max(1, Math.round((p.frecuenciaValor || 30) / 30));
                } else if (p.frecuenciaTipo === 'semanas') {
                    step = Math.max(1, Math.round(((p.frecuenciaValor || 4) * 7) / 30));
                } else {
                    step = Math.max(1, parseInt(p.frecuenciaValor || 1));
                }

                // Determinar el desfase cíclico de meses según la fecha base
                let startMonth = 1;
                if (p.proximaFecha && p.proximaFecha.length >= 7) {
                    const pYear = parseInt(p.proximaFecha.slice(0, 4));
                    const pMes = parseInt(p.proximaFecha.slice(5, 7));
                    if (pYear === anio) {
                        startMonth = pMes;
                    } else {
                        const totalDiffMonths = (anio - pYear) * 12 + (1 - pMes);
                        startMonth = 1 + ((step - (totalDiffMonths % step)) % step);
                    }
                }
                for (let m = startMonth; m <= 12; m += step) {
                    if (m >= 1 && m <= 12) mesesProyectados.add(m);
                }

                // Generar celdas de los 12 meses para el año seleccionado
                const mesesColsHtml = Array.from({length: 12}, (_, i) => i + 1).map(mNum => {
                    const isProgramado = mesesProyectados.has(mNum);
                    if (!isProgramado) {
                        return `<td class="p-1 text-center border border-slate-200 bg-slate-50 text-[10px] text-slate-300">-</td>`;
                    }

                    // Verificar si existe OT concluida para ese mes y año específico
                    const mesStr = `${anio}-${String(mNum).padStart(2, '0')}`;
                    const otConcluida = db.ots.find(o => o.equipoId === p.equipoId && (o.fechaProgramada || o.fechaAsignacion || '').startsWith(mesStr) && (o.status === 'Concluida' || o.status === 'Completada'));

                    if (otConcluida) {
                        return `
                            <td class="p-1 text-center border border-slate-200 bg-emerald-50 text-emerald-700 font-bold text-[10px]" title="Ejecutada en ${anio}: ${otConcluida.id}">
                                <span class="bg-emerald-600 text-white px-1.5 py-0.5 rounded text-[9px] shadow-sm">E</span>
                            </td>
                        `;
                    } else {
                        return `
                            <td class="p-1 text-center border border-slate-200 bg-blue-50 text-blue-700 font-semibold text-[10px] hover:bg-blue-100 cursor-pointer" onclick="crearOTDesdeCronograma('${p.id}', '${mesStr}-15')" title="Click para generar OT en ${mesesNombres[mNum-1]} ${anio}">
                                <span class="bg-blue-600 text-white px-1.5 py-0.5 rounded text-[9px] shadow-sm">P</span>
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
                        ${mesesColsHtml}
                        <td class="p-2 border border-slate-200 text-center text-xs whitespace-nowrap">
                            <button onclick="openModalPlanPreventivo('${p.id}', false)" class="text-blue-600 hover:text-blue-800 p-1" title="Editar Frecuencia"><i class="fas fa-edit"></i></button>
                            <button onclick="eliminarPlanPreventivo('${p.id}', false)" class="text-red-500 hover:text-red-700 p-1" title="Eliminar"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                `;
            }).join('');

            const listaAnios = [2024, 2025, 2026, 2027, 2028, 2029, 2030];

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-xl shadow-sm">
                                <i class="fas fa-calendar-alt"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-bold text-slate-800">Cronograma Anual de Mantenimiento Preventivo (${anio})</h2>
                                <p class="text-xs text-slate-500">Planificación Multianual Autónoma e Independiente | SALTYSNACK TUYERO C.A.</p>
                            </div>
                        </div>

                        <!-- SELECTOR DINÁMICO MULTIANUAL Y BOTONES -->
                        <div class="flex flex-wrap items-center gap-2">
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
                            </div>

                            <button onclick="exportarCronogramaAnualExcel()" class="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-file-excel"></i>
                                <span>Exportar Excel (${anio})</span>
                            </button>
                            <button onclick="openModalPlanPreventivo(false, false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-plus"></i>
                                <span>+ Programar Rutina</span>
                            </button>
                        </div>
                    </div>

                    <!-- LEYENDA Y MATRIZ ANUAL -->
                    <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm overflow-x-auto">
                        <div class="flex flex-wrap items-center justify-between mb-3 text-xs text-slate-600 gap-2">
                            <div class="flex items-center space-x-4">
                                <span class="flex items-center space-x-1"><span class="bg-blue-600 text-white px-1.5 py-0.5 rounded text-[9px] font-bold">P</span> <span>Programada (Click para generar OT en ${anio})</span></span>
                                <span class="flex items-center space-x-1"><span class="bg-emerald-600 text-white px-1.5 py-0.5 rounded text-[9px] font-bold">E</span> <span>Ejecutada en ${anio}</span></span>
                            </div>
                            <span class="text-[11px] text-slate-500 font-mono">Visualizando Planificación ${anio} | ${db.planesPreventivos.length} Rutinas</span>
                        </div>

                        <table class="w-full text-left border-collapse border border-slate-200 text-xs">
                            <thead class="bg-slate-900 text-white">
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
                            </thead>
                            <tbody class="divide-y divide-slate-200">
                                ${rowsHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }


        function crearOTDesdeCronograma(planId, fechaSugerida) {
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
        }

        function actualizarCalculoFrecuencia() {
            const ultimaStr = document.getElementById('planUltimaFecha').value;
            const fTipo = document.getElementById('planFrecuenciaTipo').value;
            const fValor = parseInt(document.getElementById('planFrecuenciaValor').value) || 1;
            if (!ultimaStr) return;

            const dt = new Date(ultimaStr + 'T00:00:00');
            if (fTipo === 'dias') {
                dt.setDate(dt.getDate() + fValor);
            } else if (fTipo === 'semanas') {
                dt.setDate(dt.getDate() + (fValor * 7));
            } else if (fTipo === 'meses') {
                dt.setMonth(dt.getMonth() + fValor);
            }

            const yyyy = dt.getFullYear();
            const mm = String(dt.getMonth() + 1).padStart(2, '0');
            const dd = String(dt.getDate()).padStart(2, '0');
            document.getElementById('planProximaFecha').value = `${yyyy}-${mm}-${dd}`;
        }

        // --- 9. MÓDULO SSL: SOLICITUDES DE CONDICIONES INSEGURAS (ROL JEFE SSL) ---
        function renderSSLView(container) {
            const totalCond = db.solicitudesSSL.length;
            const criticas = db.solicitudesSSL.filter(s => s.nivelRiesgo === 'Crítico' || s.nivelRiesgo === 'Alto').length;
            const enCorr = db.solicitudesSSL.filter(s => s.status === 'En Corrección').length;
            const corregidas = db.solicitudesSSL.filter(s => s.status === 'Corregida').length;

            const rowsHtml = db.solicitudesSSL.map(s => {
                let badgeRisk = 'bg-red-100 text-red-800 border-red-200';
                if (s.nivelRiesgo === 'Alto') badgeRisk = 'bg-orange-100 text-orange-800 border-orange-200';
                if (s.nivelRiesgo === 'Medio') badgeRisk = 'bg-amber-100 text-amber-800 border-amber-200';
                if (s.nivelRiesgo === 'Bajo') badgeRisk = 'bg-emerald-100 text-emerald-800 border-emerald-200';

                let badgeStatus = 'bg-amber-100 text-amber-800';
                if (s.status === 'En Corrección') badgeStatus = 'bg-blue-100 text-blue-800';
                if (s.status === 'Corregida') badgeStatus = 'bg-emerald-100 text-emerald-800';
                if (s.status === 'Desestimada') badgeStatus = 'bg-slate-100 text-slate-600';

                return `
                    <tr class="hover:bg-slate-50 transition">
                        <td class="p-2.5 font-mono font-bold text-slate-800 text-xs">${s.codigo || s.id}</td>
                        <td class="p-2.5 text-[11px] text-slate-500">${s.fechaHora}</td>
                        <td class="p-2.5">
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${badgeRisk}">${s.nivelRiesgo}</span>
                        </td>
                        <td class="p-2.5 text-xs font-semibold text-slate-700">${s.area} <span class="block text-[10px] font-normal text-slate-500">${s.ubicacion}</span></td>
                        <td class="p-2.5 text-xs text-slate-600 max-w-xs truncate" title="${s.descripcion}">${s.descripcion}</td>
                        <td class="p-2.5 text-center">
                            ${s.fotoEvidencia ? `
                                <img src="${s.fotoEvidencia}" class="w-10 h-10 object-cover rounded-lg border shadow-sm cursor-pointer mx-auto hover:opacity-80 transition" onclick="openLightbox('${s.fotoEvidencia}', 'Evidencia Condición SSL ${s.codigo}', '${s.descripcion}')" title="Click para ampliar">
                            ` : `<span class="text-[10px] text-slate-400">Sin foto</span>`}
                        </td>
                        <td class="p-2.5 text-center">
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${badgeStatus}">${s.status}</span>
                        </td>
                        <td class="p-2.5 text-right space-x-1 whitespace-nowrap">
                            ${currentUser.role === 'Gerente' && s.status !== 'Corregida' ? `
                                <button onclick="generarOTDesdeSSL('${s.id}')" class="bg-indigo-600 hover:bg-indigo-700 text-white px-2 py-1 rounded text-[11px] font-semibold shadow" title="Generar OT de Corrección de Seguridad">
                                    <i class="fas fa-tools mr-1"></i> Generar OT
                                </button>
                                <button onclick="cambiarStatusSSL('${s.id}', 'Corregida')" class="bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-1 rounded text-[11px] font-semibold shadow" title="Marcar como Corregida">
                                    <i class="fas fa-check"></i>
                                </button>
                            ` : ''}
                            ${currentUser.role === 'Jefe SSL' ? `
                                <button onclick="openModalSSL('${s.id}')" class="text-blue-600 hover:text-blue-800 p-1" title="Ver / Editar"><i class="fas fa-edit"></i></button>
                            ` : ''}
                            ${(currentUser.role === 'Gerente' || currentUser.role === 'Jefe SSL') ? `
                                <button onclick="eliminarSSL('${s.id}')" class="text-red-500 hover:text-red-700 p-1" title="Eliminar Condición Insegura"><i class="fas fa-trash"></i></button>
                            ` : ''}
                        </td>
                    </tr>
                `;
            }).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-xl shadow-sm">
                                <i class="fas fa-hard-hat"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-bold text-slate-800">Solicitudes de Condiciones Inseguras (SSL)</h2>
                                <p class="text-xs text-slate-500">Gestión de Seguridad, Salud y Medio Ambiente Laboral | Jefe SSL</p>
                            </div>
                        </div>

                        ${currentUser.role === 'Jefe SSL' || currentUser.role === 'Gerente' ? `
                            <button onclick="openModalSSL(false)" class="bg-amber-600 hover:bg-amber-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-camera"></i>
                                <span>+ Reportar Condición Insegura</span>
                            </button>
                        ` : ''}
                    </div>

                    <!-- TARJETAS DE SEVERIDAD DE RIESGO -->
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm text-center">
                            <div class="text-[11px] uppercase font-bold text-slate-400">Total Reportes</div>
                            <div class="text-2xl font-bold text-slate-800 mt-1">${totalCond}</div>
                        </div>
                        <div class="bg-white p-3 rounded-xl border border-red-200 shadow-sm text-center bg-red-50/30">
                            <div class="text-[11px] uppercase font-bold text-red-600">Riesgo Crítico / Alto</div>
                            <div class="text-2xl font-bold text-red-700 mt-1">${criticas}</div>
                        </div>
                        <div class="bg-white p-3 rounded-xl border border-blue-200 shadow-sm text-center bg-blue-50/30">
                            <div class="text-[11px] uppercase font-bold text-blue-600">En Corrección (OT)</div>
                            <div class="text-2xl font-bold text-blue-700 mt-1">${enCorr}</div>
                        </div>
                        <div class="bg-white p-3 rounded-xl border border-emerald-200 shadow-sm text-center bg-emerald-50/30">
                            <div class="text-[11px] uppercase font-bold text-emerald-600">Corregidas / Cerradas</div>
                            <div class="text-2xl font-bold text-emerald-700 mt-1">${corregidas}</div>
                        </div>
                    </div>

                    <!-- TABLA MAESTRA DE CONDICIONES INSEGURAS -->
                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left border-collapse text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">Código</th>
                                    <th class="p-2.5">Fecha</th>
                                    <th class="p-2.5">Severidad</th>
                                    <th class="p-2.5">Área / Ubicación</th>
                                    <th class="p-2.5">Descripción de Peligro</th>
                                    <th class="p-2.5 text-center">Evidencia</th>
                                    <th class="p-2.5 text-center">Estatus</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                ${rowsHtml.length > 0 ? rowsHtml : `<tr><td colspan="8" class="p-6 text-center text-slate-400">Sin condiciones inseguras reportadas.</td></tr>`}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        function openModalSSL(sslId = false) {
            document.getElementById('formSSL').reset();
            document.getElementById('sslFotoBase64').value = '';
            document.getElementById('previewFotoSSL').innerHTML = '';

            if (sslId) {
                const s = db.solicitudesSSL.find(x => x.id === sslId);
                if (!s) return;
                document.getElementById('sslEditId').value = s.id;
                document.getElementById('sslCodigo').value = s.codigo;
                document.getElementById('sslNivelRiesgo').value = s.nivelRiesgo;
                document.getElementById('sslArea').value = s.area;
                document.getElementById('sslUbicacion').value = s.ubicacion;
                document.getElementById('sslDescripcion').value = s.descripcion;
                document.getElementById('sslAccionPropuesta').value = s.accionPropuesta || '';
                document.getElementById('sslStatus').value = s.status;
                if (s.fotoEvidencia) {
                    document.getElementById('sslFotoBase64').value = s.fotoEvidencia;
                    document.getElementById('previewFotoSSL').innerHTML = `<img src="${s.fotoEvidencia}" class="w-14 h-14 object-cover rounded-lg border">`;
                }
            } else {
                document.getElementById('sslEditId').value = '';
                document.getElementById('sslCodigo').value = `COND-${String(db.solicitudesSSL.length + 1).padStart(3, '0')}`;
            }

            // Si es Gerente, mostrar campo de estado
            if (currentUser.role === 'Gerente') {
                document.getElementById('secStatusSSLGerente').classList.remove('hidden');
            } else {
                document.getElementById('secStatusSSLGerente').classList.add('hidden');
            }

            document.getElementById('modalSSL').classList.remove('hidden');
        }

        document.getElementById('formSSL').addEventListener('submit', function(e) {
            e.preventDefault();
            const editId = document.getElementById('sslEditId').value;
            const foto = document.getElementById('sslFotoBase64').value;

            // VALIDACIÓN ESTRICTA: FOTOGRAFÍA OBLIGATORIA
            if (!foto) {
                alert("La fotografía de evidencia es estrictamente obligatoria para registrar la Condición Insegura.");
                return;
            }

            const payload = {
                id: editId || `SSL-2026-${String(db.solicitudesSSL.length + 1).padStart(3, '0')}`,
                codigo: document.getElementById('sslCodigo').value,
                fechaHora: new Date().toISOString().replace('T', ' ').slice(0, 16),
                area: document.getElementById('sslArea').value.trim(),
                ubicacion: document.getElementById('sslUbicacion').value.trim(),
                nivelRiesgo: document.getElementById('sslNivelRiesgo').value,
                descripcion: document.getElementById('sslDescripcion').value.trim(),
                accionPropuesta: document.getElementById('sslAccionPropuesta').value.trim(),
                solicitanteId: currentUser.id,
                solicitanteNombre: currentUser.name,
                fotoEvidencia: foto,
                status: document.getElementById('sslStatus') ? document.getElementById('sslStatus').value : 'Pendiente'
            };

            if (editId) {
                const idx = db.solicitudesSSL.findIndex(x => x.id === editId);
                if (idx !== -1) db.solicitudesSSL[idx] = { ...db.solicitudesSSL[idx], ...payload };
            } else {
                db.solicitudesSSL.unshift(payload);
                // Notificar al Jefe de Mantenimiento
                dispararNotificacion('Gerente', null, 'Nueva Condición Insegura (SSL)', `${currentUser.name} reportó condición ${payload.nivelRiesgo} en ${payload.area}`, 'urgent', 'ssl', payload.id);
            }

            saveDatabase();
            closeModal('modalSSL');
            renderSSLView(document.getElementById('mainView'));
            mostrarToast('Condición Registrada', 'La solicitud SSL ha sido guardada con su evidencia fotográfica.', 'success');
        });

        function cambiarStatusSSL(sslId, nuevoStatus) {
            const s = db.solicitudesSSL.find(x => x.id === sslId);
            if (!s) return;
            s.status = nuevoStatus;
            saveDatabase();
            // Notificar al Jefe SSL
            dispararNotificacion('Jefe SSL', s.solicitanteId, 'Condición Insegura Actualizada', `La condición ${s.codigo} ha sido marcada como ${nuevoStatus}`, 'success', 'ssl', s.id);
            renderSSLView(document.getElementById('mainView'));
        }

        function generarOTDesdeSSL(sslId) {
            const s = db.solicitudesSSL.find(x => x.id === sslId);
            if (!s) return;
            openModalOT(false);
            setTimeout(() => {
                document.getElementById('otTipo').value = 'Correctivo';
                document.getElementById('otPrioridad').value = s.nivelRiesgo === 'Crítico' ? 'Alta' : 'Media';
                document.getElementById('otDescripcion').value = `[SSL ${s.codigo}] Mitigación de condición insegura en ${s.area} (${s.ubicacion}): ${s.descripcion}. Acción: ${s.accionPropuesta}`;
                if (s.fotoEvidencia) {
                    document.getElementById('otFotoAntesBase64').value = s.fotoEvidencia;
                    document.getElementById('previewFotoInicialOT').innerHTML = `<img src="${s.fotoEvidencia}" class="w-14 h-14 object-cover rounded-lg border">`;
                }
            }, 100);
        }

        // --- 10. VISTA ÓRDENES DE TRABAJO (OT) CON FILTROS AVANZADOS Y GESTIÓN MULTIMEDIA ---
        let otFiltroEquipo = 'TODOS';
        let otFiltroPeriodoTipo = 'TODOS';
        let otFiltroMes = '';
        let otFiltroAnio = '';
        let otFiltroDesde = '';
        let otFiltroHasta = '';

        function setOtFiltroEquipo(eqId) {
            otFiltroEquipo = eqId;
            renderOTsView(document.getElementById('mainView'));
        }

        function setOtFiltroPeriodoTipo(tipo) {
            otFiltroPeriodoTipo = tipo;
            renderOTsView(document.getElementById('mainView'));
        }

        function setOtFiltroMes(mes) {
            otFiltroMes = mes;
            renderOTsView(document.getElementById('mainView'));
        }

        function setOtFiltroAnio(anio) {
            otFiltroAnio = anio;
            renderOTsView(document.getElementById('mainView'));
        }

        function setOtFiltroDesde(desde) {
            otFiltroDesde = desde;
            renderOTsView(document.getElementById('mainView'));
        }

        function setOtFiltroHasta(hasta) {
            otFiltroHasta = hasta;
            renderOTsView(document.getElementById('mainView'));
        }

        function limpiarFiltrosOT() {
            otFiltroEquipo = 'TODOS';
            otFiltroPeriodoTipo = 'TODOS';
            otFiltroMes = '';
            otFiltroAnio = '';
            otFiltroDesde = '';
            otFiltroHasta = '';
            renderOTsView(document.getElementById('mainView'));
        }

        function renderOTsView(container) {
            // Aplicar filtros dinámicos por Equipo y Periodo
            let otsFiltradas = [...db.ots];

            if (otFiltroEquipo !== 'TODOS') {
                otsFiltradas = otsFiltradas.filter(o => o.equipoId === otFiltroEquipo);
            }

            if (otFiltroPeriodoTipo === 'Mes' && otFiltroMes) {
                otsFiltradas = otsFiltradas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '').startsWith(otFiltroMes));
            } else if (otFiltroPeriodoTipo === 'Anio' && otFiltroAnio) {
                otsFiltradas = otsFiltradas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '').startsWith(otFiltroAnio));
            } else if (otFiltroPeriodoTipo === 'Rango') {
                if (otFiltroDesde) otsFiltradas = otsFiltradas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '') >= otFiltroDesde);
                if (otFiltroHasta) otsFiltradas = otsFiltradas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '') <= otFiltroHasta);
            }

            const rowsHtml = otsFiltradas.map(ot => {
                const eq = db.equipos.find(e => e.id === ot.equipoId) || { name: ot.equipoId };
                let badgeStatus = 'bg-amber-100 text-amber-800';
                if (ot.status === 'Concluida' || ot.status === 'Completada') badgeStatus = 'bg-emerald-100 text-emerald-800';
                if (ot.status === 'En Proceso') badgeStatus = 'bg-blue-100 text-blue-800';

                return `
                    <tr class="hover:bg-slate-50 transition">
                        <td class="p-2.5 font-mono font-bold text-blue-700 text-xs">${ot.id}</td>
                        <td class="p-2.5 text-[11px] text-slate-500">${ot.fechaProgramada || ot.fechaAsignacion}</td>
                        <td class="p-2.5 text-xs font-semibold text-slate-800">${eq.name} <span class="block text-[10px] text-slate-400 font-mono">${ot.equipoId}</span></td>
                        <td class="p-2.5 text-xs font-semibold">${ot.tipo}</td>
                        <td class="p-2.5 text-xs text-slate-600 max-w-xs truncate" title="${ot.descripcion}">${ot.descripcion}</td>
                        <td class="p-2.5 text-center">
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${badgeStatus}">${ot.status}</span>
                        </td>
                        <!-- GESTIÓN MULTIMEDIA ANTES Y DESPUÉS -->
                        <td class="p-2.5 text-center">
                            <div class="flex items-center justify-center space-x-1">
                                ${ot.fotoAntes ? `
                                    <button onclick="openLightbox('${ot.fotoAntes}', 'Foto ANTES - ${ot.id}', 'Evidencia inicial')" class="w-7 h-7 rounded bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center text-[10px]" title="Ver Foto ANTES">
                                        <i class="fas fa-camera"></i>
                                    </button>
                                ` : ''}
                                ${ot.fotoDespues ? `
                                    <button onclick="openLightbox('${ot.fotoDespues}', 'Foto DESPUÉS - ${ot.id}', 'Intervención culminada')" class="w-7 h-7 rounded bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center text-[10px]" title="Ver Foto DESPUÉS">
                                        <i class="fas fa-check-circle"></i>
                                    </button>
                                ` : ''}
                                ${!ot.fotoAntes && !ot.fotoDespues ? `<span class="text-[10px] text-slate-400">-</span>` : ''}
                            </div>
                        </td>
                        <td class="p-2.5 text-right space-x-1 whitespace-nowrap">
                            <button onclick="imprimirOT('${ot.id}')" class="text-slate-600 hover:text-slate-900 p-1" title="Imprimir Formato Corporativo (PDF)"><i class="fas fa-print"></i></button>
                            <button onclick="openModalCierreOT('${ot.id}')" class="text-emerald-600 hover:text-emerald-800 p-1" title="Bitácora de Cierre"><i class="fas fa-check-circle"></i></button>
                            <button onclick="openModalOT('${ot.id}')" class="text-blue-600 hover:text-blue-800 p-1" title="Editar OT"><i class="fas fa-edit"></i></button>
                            <button onclick="eliminarOT('${ot.id}')" class="text-red-500 hover:text-red-700 p-1" title="Eliminar"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                `;
            }).join('');

            // Lista de equipos ordenada alfanuméricamente para el selector
            const equiposOrdenados = [...db.equipos].sort((a, b) => naturalCompare(a.id, b.id, true));

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center text-xl shadow-sm">
                                <i class="fas fa-clipboard-list"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-bold text-slate-800">Control Maestro de Órdenes de Trabajo (OT)</h2>
                                <p class="text-xs text-slate-500">SALTYSNACK TUYERO C.A. | Mantenimiento Preventivo y Correctivo</p>
                            </div>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button onclick="exportarMatrizOTExcel()" class="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-file-excel"></i>
                                <span>Exportar a Excel (Matriz)</span>
                            </button>
                            <button onclick="openModalOT(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-plus"></i>
                                <span>+ Nueva OT</span>
                            </button>
                        </div>
                    </div>

                    <!-- BARRA DE FILTROS AVANZADOS (EQUIPO Y PERIODO) -->
                    <div class="bg-white p-3 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-3 text-xs">
                        <div class="flex flex-wrap items-center gap-2.5">
                            <!-- FILTRO POR EQUIPO -->
                            <div class="flex items-center space-x-1.5">
                                <span class="font-bold text-slate-600 flex items-center"><i class="fas fa-cogs mr-1 text-blue-600"></i> Equipo:</span>
                                <select onchange="setOtFiltroEquipo(this.value)" class="border rounded-lg px-2.5 py-1.5 bg-slate-50 font-medium outline-none text-xs max-w-[200px] truncate">
                                    <option value="TODOS" ${otFiltroEquipo === 'TODOS' ? 'selected' : ''}>[ Todos los Equipos ]</option>
                                    ${equiposOrdenados.map(e => `<option value="${e.id}" ${otFiltroEquipo === e.id ? 'selected' : ''}>${e.id} - ${e.name}</option>`).join('')}
                                </select>
                            </div>

                            <!-- FILTRO POR TIPO DE PERIODO -->
                            <div class="flex items-center space-x-1.5">
                                <span class="font-bold text-slate-600 flex items-center"><i class="fas fa-calendar mr-1 text-indigo-600"></i> Periodo:</span>
                                <select onchange="setOtFiltroPeriodoTipo(this.value)" class="border rounded-lg px-2.5 py-1.5 bg-slate-50 font-medium outline-none text-xs">
                                    <option value="TODOS" ${otFiltroPeriodoTipo === 'TODOS' ? 'selected' : ''}>[ Todos los Periodos ]</option>
                                    <option value="Mes" ${otFiltroPeriodoTipo === 'Mes' ? 'selected' : ''}>Mensual</option>
                                    <option value="Anio" ${otFiltroPeriodoTipo === 'Anio' ? 'selected' : ''}>Anual</option>
                                    <option value="Rango" ${otFiltroPeriodoTipo === 'Rango' ? 'selected' : ''}>Rango de Fechas</option>
                                </select>
                            </div>

                            <!-- CONTROLES ESPECÍFICOS SEGÚN TIPO DE PERIODO -->
                            ${otFiltroPeriodoTipo === 'Mes' ? `
                                <div class="flex items-center space-x-1">
                                    <input type="month" value="${otFiltroMes}" onchange="setOtFiltroMes(this.value)" class="border rounded-lg px-2 py-1 bg-white font-medium outline-none text-xs">
                                </div>
                            ` : ''}

                            ${otFiltroPeriodoTipo === 'Anio' ? `
                                <div class="flex items-center space-x-1">
                                    <select onchange="setOtFiltroAnio(this.value)" class="border rounded-lg px-2 py-1 bg-white font-medium outline-none text-xs">
                                        <option value="">Seleccione Año</option>
                                        <option value="2027" ${otFiltroAnio === '2027' ? 'selected' : ''}>2027</option>
                                        <option value="2026" ${otFiltroAnio === '2026' ? 'selected' : ''}>2026</option>
                                        <option value="2025" ${otFiltroAnio === '2025' ? 'selected' : ''}>2025</option>
                                        <option value="2024" ${otFiltroAnio === '2024' ? 'selected' : ''}>2024</option>
                                    </select>
                                </div>
                            ` : ''}

                            ${otFiltroPeriodoTipo === 'Rango' ? `
                                <div class="flex items-center space-x-1">
                                    <span class="text-slate-400 text-[10px]">Desde:</span>
                                    <input type="date" value="${otFiltroDesde}" onchange="setOtFiltroDesde(this.value)" class="border rounded px-2 py-1 text-[11px] outline-none">
                                    <span class="text-slate-400 text-[10px]">Hasta:</span>
                                    <input type="date" value="${otFiltroHasta}" onchange="setOtFiltroHasta(this.value)" class="border rounded px-2 py-1 text-[11px] outline-none">
                                </div>
                            ` : ''}

                            ${(otFiltroEquipo !== 'TODOS' || otFiltroPeriodoTipo !== 'TODOS') ? `
                                <button onclick="limpiarFiltrosOT()" class="text-red-500 hover:text-red-700 font-semibold text-[11px] flex items-center space-x-1 px-2 py-1 border border-red-200 rounded-lg hover:bg-red-50 transition" title="Restablecer todos los filtros">
                                    <i class="fas fa-times-circle"></i>
                                    <span>Limpiar</span>
                                </button>
                            ` : ''}
                        </div>

                        <div class="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg font-mono">
                            Mostrando: <strong class="text-blue-700">${otsFiltradas.length}</strong> de ${db.ots.length} OTs
                        </div>
                    </div>

                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left border-collapse text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">N° OT</th>
                                    <th class="p-2.5">Fecha</th>
                                    <th class="p-2.5">Línea / Equipo</th>
                                    <th class="p-2.5">Tipo</th>
                                    <th class="p-2.5">Descripción de la Actividad</th>
                                    <th class="p-2.5 text-center">Estatus</th>
                                    <th class="p-2.5 text-center">Evidencias</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                ${rowsHtml.length > 0 ? rowsHtml : `<tr><td colspan="8" class="p-6 text-center text-slate-400">No se encontraron órdenes de trabajo para los filtros seleccionados.</td></tr>`}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
""")

print("Parte 4 anexada exitosamente.")
# =============================================================================
# PARTE 5: SOLICITUDES (4 ESTADOS), INFORMES PERSONALIZADOS, FORMATOS DE IMPRESIÓN Y EXPORTACIÓN EXCEL
# =============================================================================
parts.append("""
        // --- 11. SOLICITUDES INTERDEPARTAMENTALES (4 ESTADOS ESTRICTOS) ---
        // Estados autorizados: 'Aprobada', 'En espera de materiales', 'En proceso', 'Culminada'
        function renderSolicitudesGerenteView(container) {
            const rowsHtml = db.solicitudesInterdepartamentales.map(s => {
                let badgeStatus = 'bg-blue-100 text-blue-800';
                if (s.status === 'En espera de materiales') badgeStatus = 'bg-amber-100 text-amber-800';
                if (s.status === 'En proceso') badgeStatus = 'bg-purple-100 text-purple-800';
                if (s.status === 'Culminada') badgeStatus = 'bg-emerald-100 text-emerald-800';

                return `
                    <tr class="hover:bg-slate-50 transition">
                        <td class="p-2.5 font-mono font-bold text-blue-700 text-xs">${s.id}</td>
                        <td class="p-2.5 text-[11px] text-slate-500">${s.fechaHora}</td>
                        <td class="p-2.5 text-xs font-semibold text-slate-800">${s.area} <span class="block text-[10px] text-slate-400">${s.ubicacion}</span></td>
                        <td class="p-2.5 text-xs text-slate-600 max-w-xs truncate" title="${s.descripcion}">${s.descripcion}</td>
                        <td class="p-2.5 text-[11px] text-slate-500">${s.solicitante}</td>
                        <td class="p-2.5 text-center">
                            <!-- SELECTOR DIRECTO DE LOS 4 ESTADOS AUTORIZADOS -->
                            <select onchange="cambiarStatusSolicitud('${s.id}', this.value)" class="text-[11px] font-bold rounded-full px-2 py-0.5 border ${badgeStatus} outline-none cursor-pointer">
                                <option value="Aprobada" ${s.status === 'Aprobada' ? 'selected' : ''}>Aprobada</option>
                                <option value="En espera de materiales" ${s.status === 'En espera de materiales' ? 'selected' : ''}>En espera de materiales</option>
                                <option value="En proceso" ${s.status === 'En proceso' ? 'selected' : ''}>En proceso</option>
                                <option value="Culminada" ${s.status === 'Culminada' ? 'selected' : ''}>Culminada</option>
                            </select>
                        </td>
                        <td class="p-2.5 text-right space-x-1 whitespace-nowrap">
                            ${!s.otVinculada && s.status !== 'Culminada' ? `
                                <button onclick="generarOTDesdeSolicitud('${s.id}')" class="bg-indigo-600 hover:bg-indigo-700 text-white px-2 py-1 rounded text-[11px] font-semibold shadow">
                                    <i class="fas fa-clipboard-check mr-1"></i> Generar OT
                                </button>
                            ` : (s.otVinculada ? `<span class="text-[10px] font-mono text-blue-600 font-bold">${s.otVinculada}</span>` : '')}
                            ${currentUser.role === 'Gerente' ? `
                                <button onclick="eliminarSolicitud('${s.id}')" class="text-red-500 hover:text-red-700 p-1" title="Eliminar Solicitud"><i class="fas fa-trash"></i></button>
                            ` : ''}
                        </td>
                    </tr>
                `;
            }).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-xl shadow-sm">
                                <i class="fas fa-inbox"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-bold text-slate-800">Bandeja de Solicitudes Interdepartamentales</h2>
                                <p class="text-xs text-slate-500">Flujo de 4 Estados: Aprobada &rarr; En espera de materiales &rarr; En proceso &rarr; Culminada</p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left border-collapse text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">Folio</th>
                                    <th class="p-2.5">Fecha</th>
                                    <th class="p-2.5">Área / Ubicación</th>
                                    <th class="p-2.5">Descripción de Falla</th>
                                    <th class="p-2.5">Solicitante</th>
                                    <th class="p-2.5 text-center">Estatus del Flujo</th>
                                    <th class="p-2.5 text-center">OT Vinculada</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                ${rowsHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

                function eliminarSSL(sslId) {
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

        function cambiarStatusSolicitud(solId, nuevoStatus) {
            const s = db.solicitudesInterdepartamentales.find(x => x.id === solId);
            if (!s) return;
            s.status = nuevoStatus;
            saveDatabase();
            mostrarToast('Estatus Actualizado', `La solicitud ${solId} ahora está en: ${nuevoStatus}`, 'info');
            renderSolicitudesGerenteView(document.getElementById('mainView'));
        }

        function generarOTDesdeSolicitud(solId) {
            const s = db.solicitudesInterdepartamentales.find(x => x.id === solId);
            if (!s) return;
            openModalOT(false);
            setTimeout(() => {
                document.getElementById('otTipo').value = 'Correctivo';
                document.getElementById('otPrioridad').value = s.urgencia === 'Crítica' || s.urgencia === 'Alta' ? 'Alta' : 'Media';
                document.getElementById('otDescripcion').value = `[Requerimiento ${s.id}] En ${s.area} (${s.ubicacion}): ${s.descripcion}`;
                document.getElementById('otSolicitudId').value = s.id;
            }, 100);
        }

        function renderMisSolicitudesView(container) {
            const misSols = db.solicitudesInterdepartamentales.filter(s => s.solicitante.includes(currentUser.name.split(' ')[0]) || currentUser.role === 'Solicitante');
            const rowsHtml = misSols.map(s => {
                let badgeStatus = 'bg-blue-100 text-blue-800';
                if (s.status === 'En espera de materiales') badgeStatus = 'bg-amber-100 text-amber-800';
                if (s.status === 'En proceso') badgeStatus = 'bg-purple-100 text-purple-800';
                if (s.status === 'Culminada') badgeStatus = 'bg-emerald-100 text-emerald-800';

                return `
                    <tr class="hover:bg-slate-50 transition">
                        <td class="p-2.5 font-mono font-bold text-blue-700 text-xs">${s.id}</td>
                        <td class="p-2.5 text-[11px] text-slate-500">${s.fechaHora}</td>
                        <td class="p-2.5 text-xs font-semibold text-slate-800">${s.area} <span class="block text-[10px] text-slate-400">${s.ubicacion}</span></td>
                        <td class="p-2.5 text-xs text-slate-600">${s.descripcion}</td>
                        <td class="p-2.5 text-center">
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${badgeStatus}">${s.status}</span>
                        </td>
                        <td class="p-2.5 text-center font-mono text-xs font-bold text-blue-600">${s.otVinculada || 'En Gestión'}</td>
                        <td class="p-2.5 text-right space-x-1 whitespace-nowrap">
                            ${(currentUser.role === 'Solicitante' || currentUser.role === 'Gerente') ? `
                                <button onclick="eliminarSolicitud('${s.id}')" class="text-red-500 hover:text-red-700 p-1" title="Eliminar Solicitud"><i class="fas fa-trash"></i></button>
                            ` : ''}
                        </td>
                    </tr>
                `;
            }).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center text-xl shadow-sm">
                                <i class="fas fa-paper-plane"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-bold text-slate-800">Mis Solicitudes de Falla y Averías</h2>
                                <p class="text-xs text-slate-500">Seguimiento en Tiempo Real de Atención por Mantenimiento</p>
                            </div>
                        </div>
                        <button onclick="openModalSolicitudInter()" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                            <i class="fas fa-plus"></i>
                            <span>+ Emitir Solicitud de Falla</span>
                        </button>
                    </div>

                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left border-collapse text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">Folio</th>
                                    <th class="p-2.5">Fecha</th>
                                    <th class="p-2.5">Área / Equipo</th>
                                    <th class="p-2.5">Descripción de Falla</th>
                                    <th class="p-2.5 text-center">Estatus</th>
                                    <th class="p-2.5 text-right">OT Asignada</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">
                                ${rowsHtml.length > 0 ? rowsHtml : `<tr><td colspan="6" class="p-6 text-center text-slate-400">Sin solicitudes emitidas.</td></tr>`}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        // --- 12. VISTA INFORMES PERIÓDICOS CON PERSONALIZACIÓN DE ESTRUCTURA ---
        function setInformePeriodoTipo(tipo) {
            informeFiltroPeriodo = tipo;
            renderInformesView(document.getElementById('mainView'));
        }

        function setInformeFiltroEquipo(eqId) {
            informeFiltroEquipo = eqId;
            renderInformesView(document.getElementById('mainView'));
        }

        function setInformeMes(val) {
            informeMes = val;
            renderInformesView(document.getElementById('mainView'));
        }

        function setInformeAnio(val) {
            informeAnio = val;
            renderInformesView(document.getElementById('mainView'));
        }

        function setInformeFechaInicio(val) {
            informeFechaInicio = val;
            renderInformesView(document.getElementById('mainView'));
        }

        function setInformeFechaFin(val) {
            informeFechaFin = val;
            renderInformesView(document.getElementById('mainView'));
        }

        function limpiarFiltrosInforme() {
            informeFiltroEquipo = 'TODOS';
            informeFiltroPeriodo = 'Mensual';
            informeMes = new Date().toISOString().slice(0, 7);
            informeAnio = String(new Date().getFullYear());
            informeFechaInicio = '';
            informeFechaFin = '';
            renderInformesView(document.getElementById('mainView'));
        }

        // --- 12. VISTA INFORMES PERIÓDICOS CON HISTORIAL COMPLETO Y FIRMAS ESTRICTAS ---
        function renderInformesView(container) {
            // Filtrar OTs por Equipo y por Periodo
            let otsEvaluadas = db.ots || [];
            if (informeFiltroEquipo !== 'TODOS') {
                otsEvaluadas = otsEvaluadas.filter(o => o.equipoId === informeFiltroEquipo);
            }

            let periodoTexto = '';
            if (informeFiltroPeriodo === 'Mensual') {
                otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '').startsWith(informeMes));
                const [y, m] = informeMes.split('-');
                const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
                periodoTexto = `${meses[parseInt(m, 10) - 1] || m} ${y}`;
            } else if (informeFiltroPeriodo === 'Anual') {
                otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '').startsWith(informeAnio));
                periodoTexto = `Año ${informeAnio}`;
            } else if (informeFiltroPeriodo === 'Rango') {
                if (informeFechaInicio) {
                    otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '') >= informeFechaInicio);
                }
                if (informeFechaFin) {
                    otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '') <= informeFechaFin);
                }
                periodoTexto = `${informeFechaInicio || 'Inicio'} al ${informeFechaFin || 'Fin'}`;
            }

            // OTs Culminadas para el historial
            const concluidas = otsEvaluadas.filter(o => o.status === 'Concluida' || o.status === 'Completada');
            const preventivasConcluidas = concluidas.filter(o => o.tipo === 'Preventivo');
            const correctivasConcluidas = concluidas.filter(o => o.tipo === 'Correctivo');
            const otrasConcluidas = concluidas.filter(o => o.tipo !== 'Preventivo' && o.tipo !== 'Correctivo');

            // Métricas calculadas para el informe
            const totalDowntime = otsEvaluadas.reduce((acc, o) => acc + parseFloat(o.tiempoParada || 0.0), 0.0);
            const totalIntervencion = concluidas.reduce((acc, o) => acc + parseFloat(o.tiempoIntervencion || 0.0), 0.0);
            const horasBase = (informeFiltroPeriodo === 'Anual') ? 8760.0 : 720.0;
            const horasOperadas = Math.max(0.0, horasBase - totalDowntime);
            const disponibilidadPct = Math.min(100.0, Math.round((horasOperadas / horasBase) * 1000) / 10);
            const numFallas = correctivasConcluidas.length;
            const mttr = numFallas > 0 ? (Math.round((correctivasConcluidas.reduce((a, c) => a + parseFloat(c.tiempoIntervencion || 0), 0) / numFallas) * 10) / 10) : 0.0;
            const mttrMeta = (db.config && db.config.mttrTarget) ? parseFloat(db.config.mttrTarget) : 2.0;

            // Firmas autorizadas estrictamente dinámicas
            const jefeUser = (db.users || []).find(u => (u.cargo && u.cargo.toLowerCase().includes('jefe de mantenimiento')) || u.role === 'Gerente' || u.username === 'admin');
            const nombreJefe = jefeUser ? jefeUser.name : 'Ing. Carlos Mendoza';

            const gerentePlantaUser = (db.users || []).find(u => (u.cargo && u.cargo.toLowerCase().includes('gerente de planta')) || (u.name && u.name.toLowerCase().includes('gerente de planta')));
            const nombreGerentePlanta = gerentePlantaUser ? gerentePlantaUser.name : 'Ing. Roberto Navarro';

            // Filas HTML de Preventivo (Estructura Noviembre.docx)
            const filasPrevHtml = preventivasConcluidas.length > 0 ? preventivasConcluidas.map((o, idx) => {
                const eq = db.equipos.find(e => e.id === o.equipoId) || { name: o.equipoId };
                return `
                    <tr class="border-b border-slate-200 text-[11px] hover:bg-slate-50">
                        <td class="p-2 font-bold text-center">${idx + 1}</td>
                        <td class="p-2 font-mono whitespace-nowrap">${o.fechaProgramada || o.fechaAsignacion}</td>
                        <td class="p-2 text-center font-semibold text-slate-700">Mensual / Programado</td>
                        <td class="p-2 font-semibold text-slate-800">${eq.name}</td>
                        <td class="p-2 font-mono font-bold text-blue-700">${o.equipoId}</td>
                        <td class="p-2 text-slate-700">${o.actividades || o.descripcion}</td>
                        <td class="p-2 text-slate-600"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">Culminado Conforme</span></td>
                    </tr>
                `;
            }).join('') : `<tr><td colspan="7" class="p-4 text-center text-slate-400 italic">No se registraron mantenimientos preventivos culminados en este periodo.</td></tr>`;

            // Filas HTML de Correctivo (Estructura Noviembre.docx)
            const filasCorrHtml = correctivasConcluidas.length > 0 ? correctivasConcluidas.map((o, idx) => {
                const eq = db.equipos.find(e => e.id === o.equipoId) || { name: o.equipoId };
                const repText = (o.repuestosUsados && o.repuestosUsados.length > 0) ? o.repuestosUsados.map(r => `${r.name} (x${r.cant})`).join(', ') : 'Ninguno';
                return `
                    <tr class="border-b border-slate-200 text-[11px] hover:bg-slate-50">
                        <td class="p-2 font-bold text-center">${idx + 1}</td>
                        <td class="p-2 font-mono whitespace-nowrap">${o.fechaFin || o.fechaProgramada || o.fechaAsignacion}</td>
                        <td class="p-2 font-semibold text-slate-800">${eq.name}</td>
                        <td class="p-2 font-mono font-bold text-blue-700">${o.equipoId}</td>
                        <td class="p-2 text-slate-700">${o.descripcion}</td>
                        <td class="p-2 text-slate-700">${o.actividades || 'Corrección de falla y pruebas operativas'}</td>
                        <td class="p-2 text-slate-600 font-mono text-[10px]">${repText}</td>
                        <td class="p-2 text-slate-600"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">Culminado (${o.tiempoIntervencion || 0}h)</span></td>
                    </tr>
                `;
            }).join('') : `<tr><td colspan="8" class="p-4 text-center text-slate-400 italic">No se registraron fallas o mantenimientos correctivos en este periodo.</td></tr>`;

            // Filas HTML de Otras Actividades (Estructura Noviembre.docx)
            const filasOtrasHtml = otrasConcluidas.length > 0 ? otrasConcluidas.map((o, idx) => {
                const repText = (o.repuestosUsados && o.repuestosUsados.length > 0) ? o.repuestosUsados.map(r => `${r.name} (x${r.cant})`).join(', ') : 'Insumos de planta';
                return `
                    <tr class="border-b border-slate-200 text-[11px] hover:bg-slate-50">
                        <td class="p-2 font-bold text-center">${idx + 1}</td>
                        <td class="p-2 font-mono whitespace-nowrap">${o.fechaFin || o.fechaProgramada || o.fechaAsignacion}</td>
                        <td class="p-2 text-slate-700 font-semibold">${o.descripcion}</td>
                        <td class="p-2 text-slate-600 font-mono text-[10px]">${repText}</td>
                        <td class="p-2 text-slate-600"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800">Finalizada</span></td>
                    </tr>
                `;
            }).join('') : `<tr><td colspan="5" class="p-3 text-center text-slate-400 italic">No se registraron otras actividades adicionales.</td></tr>`;

            // Equipos ordenados alfanuméricamente natural para el filtro
            const equiposOrdenados = [...db.equipos].sort((a, b) => naturalCompare(a.id, b.id, true));

            container.innerHTML = `
                <div class="space-y-4">
                    <!-- ENCABEZADO Y CONTROLES DE ACCIÓN -->
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-orange-50 text-orange-600 flex items-center justify-center text-xl shadow-sm">
                                <i class="fas fa-file-invoice"></i>
                            </div>
                            <div>
                                <h2 class="text-base font-bold text-slate-800">Informe Periódico de Gestión y Confiabilidad</h2>
                                <p class="text-xs text-slate-500">SALTYSNACK TUYERO C.A. | Formato Oficial de Planta con Historial de OTs Culminadas</p>
                            </div>
                        </div>

                        <div class="flex items-center space-x-2">
                            <button onclick="imprimirInforme()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1.5 transition">
                                <i class="fas fa-print"></i>
                                <span>Imprimir Formato Formal (PDF)</span>
                            </button>
                        </div>
                    </div>

                    <!-- BARRA DE FILTROS AVANZADOS: POR EQUIPO Y POR PERIODO -->
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
                        <div class="flex items-center justify-between border-b pb-2">
                            <div class="flex items-center space-x-2 text-xs font-bold text-slate-700">
                                <i class="fas fa-filter text-blue-600"></i>
                                <span>Filtros de Evaluación del Informe</span>
                            </div>
                            <button onclick="limpiarFiltrosInforme()" class="text-xs text-slate-500 hover:text-slate-800 font-semibold underline">
                                Limpiar Filtros
                            </button>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <!-- FILTRO POR EQUIPO -->
                            <div>
                                <label class="block text-xs font-semibold text-slate-600 mb-1">Filtrar por Equipo / Activo:</label>
                                <select onchange="setInformeFiltroEquipo(this.value)" class="w-full border rounded-lg p-2 text-xs bg-white outline-none font-medium">
                                    <option value="TODOS" ${informeFiltroEquipo === 'TODOS' ? 'selected' : ''}>Todos los Equipos y Líneas</option>
                                    ${equiposOrdenados.map(e => `
                                        <option value="${e.id}" ${informeFiltroEquipo === e.id ? 'selected' : ''}>${e.id} - ${e.name}</option>
                                    `).join('')}
                                </select>
                            </div>

                            <!-- TIPO DE PERIODO -->
                            <div>
                                <label class="block text-xs font-semibold text-slate-600 mb-1">Tipo de Periodo:</label>
                                <div class="flex items-center bg-slate-100 p-1 rounded-lg border">
                                    <button onclick="setInformePeriodoTipo('Mensual')" class="flex-1 py-1.5 rounded text-xs font-bold transition ${informeFiltroPeriodo === 'Mensual' ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:text-slate-900'}">
                                        Mensual
                                    </button>
                                    <button onclick="setInformePeriodoTipo('Anual')" class="flex-1 py-1.5 rounded text-xs font-bold transition ${informeFiltroPeriodo === 'Anual' ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:text-slate-900'}">
                                        Anual
                                    </button>
                                    <button onclick="setInformePeriodoTipo('Rango')" class="flex-1 py-1.5 rounded text-xs font-bold transition ${informeFiltroPeriodo === 'Rango' ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:text-slate-900'}">
                                        Rango
                                    </button>
                                </div>
                            </div>

                            <!-- SELECTOR DE FECHAS SEGÚN TIPO -->
                            <div>
                                ${informeFiltroPeriodo === 'Mensual' ? `
                                    <label class="block text-xs font-semibold text-slate-600 mb-1">Seleccionar Mes:</label>
                                    <input type="month" value="${informeMes}" onchange="setInformeMes(this.value)" class="w-full border rounded-lg p-2 text-xs bg-white outline-none font-medium">
                                ` : ''}

                                ${informeFiltroPeriodo === 'Anual' ? `
                                    <label class="block text-xs font-semibold text-slate-600 mb-1">Seleccionar Año:</label>
                                    <select onchange="setInformeAnio(this.value)" class="w-full border rounded-lg p-2 text-xs bg-white outline-none font-medium">
                                        ${[2024, 2025, 2026, 2027, 2028, 2029, 2030].map(y => `
                                            <option value="${y}" ${informeAnio === String(y) ? 'selected' : ''}>${y}</option>
                                        `).join('')}
                                    </select>
                                ` : ''}

                                ${informeFiltroPeriodo === 'Rango' ? `
                                    <label class="block text-xs font-semibold text-slate-600 mb-1">Rango de Fechas:</label>
                                    <div class="grid grid-cols-2 gap-2">
                                        <input type="date" value="${informeFechaInicio}" onchange="setInformeFechaInicio(this.value)" class="border rounded-lg p-1.5 text-xs outline-none">
                                        <input type="date" value="${informeFechaFin}" onchange="setInformeFechaFin(this.value)" class="border rounded-lg p-1.5 text-xs outline-none">
                                    </div>
                                ` : ''}
                            </div>
                        </div>

                        <div class="text-[11px] text-slate-500 flex items-center justify-between pt-1">
                            <span>Mostrando actividades correspondientes a: <strong>${periodoTexto}</strong> | Activo: <strong>${informeFiltroEquipo === 'TODOS' ? 'Toda la Planta' : informeFiltroEquipo}</strong></span>
                            <span class="font-bold text-blue-700">${concluidas.length} OTs Culminadas Encontradas</span>
                        </div>
                    </div>

                    <!-- VISTA PREVIA DEL INFORME ESTRUCTURADO (ESTILO NOVIEMBRE.DOCX) -->
                    <div class="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-sm space-y-6" id="previewInformeArea">
                        <!-- ENCABEZADO FORMAL INSTITUCIONAL -->
                        <div class="border-b-2 border-slate-900 pb-4 flex justify-between items-start">
                            <div>
                                <h1 class="font-black text-xl text-slate-900 uppercase tracking-tight">SALTYSNACK TUYERO C.A.</h1>
                                <h2 class="text-sm font-bold text-slate-700 uppercase mt-0.5">INFORME MENSUAL DE MANTENIMIENTO PLANTA</h2>
                                <div class="text-xs font-semibold text-slate-500 mt-1">Periodo Evaluado: <span class="text-slate-800 font-bold">${periodoTexto}</span> | Alcance: <span class="text-slate-800 font-bold">${informeFiltroEquipo === 'TODOS' ? 'Planta General' : informeFiltroEquipo}</span></div>
                            </div>
                            <div class="text-right">
                                <span class="bg-slate-900 text-white px-3 py-1 rounded font-mono text-xs font-bold">DOC-INF-${informeAnio}</span>
                                <div class="text-[10px] text-slate-400 mt-1">Emisión: ${new Date().toLocaleDateString()}</div>
                            </div>
                        </div>

                        <!-- SECCIÓN 1: RESUMEN EJECUTIVO (COMO EN NOVIEMBRE.DOCX) -->
                        <div>
                            <h3 class="text-sm font-black uppercase text-slate-900 mb-2 flex items-center">
                                <span class="w-6 h-6 rounded bg-slate-900 text-white flex items-center justify-center text-xs mr-2">1</span>
                                Resumen Ejecutivo
                            </h3>
                            <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 text-xs leading-relaxed text-slate-700 space-y-2">
                                <p>
                                    Durante el periodo evaluado correspondiente a <strong>${periodoTexto}</strong>, el departamento de mantenimiento ejecutó un total de <strong>${concluidas.length} actividades de mantenimiento culminadas</strong> en planta (${preventivasConcluidas.length} preventivas programadas, ${correctivasConcluidas.length} intervenciones correctivas y ${otrasConcluidas.length} otras actividades especializadas/mejoras).
                                </p>
                                <p>
                                    La disponibilidad operativa registrada se situó en <strong>${disponibilidadPct}%</strong>, con un tiempo medio de reparación (MTTR) de <strong>${mttr} h</strong> frente al umbral objetivo configurado de <strong>${mttrMeta} h</strong>, garantizando la continuidad de producción y la mitigación oportuna de tiempos de parada operativa (Downtime acumulado: ${totalDowntime.toFixed(1)} h).
                                </p>
                            </div>

                            <!-- TARJETAS COMPACTAS DE INDICADORES CLAVE -->
                            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3 text-center">
                                <div class="p-2.5 border rounded-lg bg-blue-50/50 border-blue-200">
                                    <div class="text-[10px] uppercase font-bold text-slate-500">Disponibilidad</div>
                                    <div class="text-lg font-black text-blue-700">${disponibilidadPct}%</div>
                                </div>
                                <div class="p-2.5 border rounded-lg bg-emerald-50/50 border-emerald-200">
                                    <div class="text-[10px] uppercase font-bold text-slate-500">MTTR (Meta: ${mttrMeta}h)</div>
                                    <div class="text-lg font-black ${mttr <= mttrMeta ? 'text-emerald-700' : 'text-amber-700'}">${mttr} h</div>
                                </div>
                                <div class="p-2.5 border rounded-lg bg-purple-50/50 border-purple-200">
                                    <div class="text-[10px] uppercase font-bold text-slate-500">OTs Culminadas</div>
                                    <div class="text-lg font-black text-purple-700">${concluidas.length}</div>
                                </div>
                                <div class="p-2.5 border rounded-lg bg-slate-50 border-slate-200">
                                    <div class="text-[10px] uppercase font-bold text-slate-500">Horas Parada</div>
                                    <div class="text-lg font-black text-slate-800">${totalDowntime.toFixed(1)} h</div>
                                </div>
                            </div>
                        </div>

                        <!-- SECCIÓN 2: HISTORIAL DE ACTIVIDADES REALIZADAS (ESTRUCTURA NOVIEMBRE.DOCX) -->
                        <div class="space-y-4">
                            <h3 class="text-sm font-black uppercase text-slate-900 flex items-center">
                                <span class="w-6 h-6 rounded bg-slate-900 text-white flex items-center justify-center text-xs mr-2">2</span>
                                Actividades Realizadas
                            </h3>

                            <!-- SUBSECCIÓN: MANTENIMIENTO PREVENTIVO -->
                            <div class="border rounded-lg overflow-hidden border-slate-300">
                                <div class="bg-slate-800 text-white px-3 py-2 font-bold text-xs uppercase flex items-center justify-between">
                                    <span>2.1 Mantenimiento Preventivo</span>
                                    <span class="text-[10px] font-mono font-normal">Total Culminadas: ${preventivasConcluidas.length}</span>
                                </div>
                                <div class="overflow-x-auto">
                                    <table class="w-full text-left border-collapse">
                                        <thead class="bg-slate-100 text-slate-800 text-[10px] uppercase font-bold border-b border-slate-300">
                                            <tr>
                                                <th class="p-2 text-center w-8">Nº</th>
                                                <th class="p-2">Fecha de Emisión</th>
                                                <th class="p-2 text-center">Frecuencia</th>
                                                <th class="p-2">Máquina</th>
                                                <th class="p-2">Código</th>
                                                <th class="p-2">Actividades</th>
                                                <th class="p-2">Observaciones</th>
                                            </tr>
                                        </thead>
                                        <tbody class="divide-y divide-slate-200">${filasPrevHtml}</tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- SUBSECCIÓN: MANTENIMIENTO CORRECTIVO -->
                            <div class="border rounded-lg overflow-hidden border-slate-300">
                                <div class="bg-slate-800 text-white px-3 py-2 font-bold text-xs uppercase flex items-center justify-between">
                                    <span>2.2 Mantenimiento Correctivo</span>
                                    <span class="text-[10px] font-mono font-normal">Total Culminadas: ${correctivasConcluidas.length}</span>
                                </div>
                                <div class="overflow-x-auto">
                                    <table class="w-full text-left border-collapse">
                                        <thead class="bg-slate-100 text-slate-800 text-[10px] uppercase font-bold border-b border-slate-300">
                                            <tr>
                                                <th class="p-2 text-center w-8">Nº</th>
                                                <th class="p-2">Fecha</th>
                                                <th class="p-2">Máquina / Instalación</th>
                                                <th class="p-2">Código</th>
                                                <th class="p-2">Falla o Requerimiento</th>
                                                <th class="p-2">Descripción de Mantenimiento</th>
                                                <th class="p-2">Materiales Utilizados</th>
                                                <th class="p-2">Observaciones</th>
                                            </tr>
                                        </thead>
                                        <tbody class="divide-y divide-slate-200">${filasCorrHtml}</tbody>
                                    </table>
                                </div>
                            </div>

                            <!-- SUBSECCIÓN: OTRAS ACTIVIDADES -->
                            <div class="border rounded-lg overflow-hidden border-slate-300">
                                <div class="bg-slate-800 text-white px-3 py-2 font-bold text-xs uppercase flex items-center justify-between">
                                    <span>3. Otras Actividades (Inspecciones Especiales / Mejoras)</span>
                                    <span class="text-[10px] font-mono font-normal">Total: ${otrasConcluidas.length}</span>
                                </div>
                                <div class="overflow-x-auto">
                                    <table class="w-full text-left border-collapse">
                                        <thead class="bg-slate-100 text-slate-800 text-[10px] uppercase font-bold border-b border-slate-300">
                                            <tr>
                                                <th class="p-2 text-center w-8">Nº</th>
                                                <th class="p-2">Fecha</th>
                                                <th class="p-2">Descripción de la Actividad</th>
                                                <th class="p-2">Materiales Utilizados</th>
                                                <th class="p-2">Observaciones</th>
                                            </tr>
                                        </thead>
                                        <tbody class="divide-y divide-slate-200">${filasOtrasHtml}</tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        <!-- FIRMAS AUTORIZADAS: ESTRICTAMENTE RESTRINGIDAS A JEFE DE MANTENIMIENTO Y GERENTE DE PLANTA -->
                        <div class="pt-8 border-t-2 border-slate-900 grid grid-cols-2 gap-12 text-center text-xs">
                            <div>
                                <div class="border-b-2 border-slate-800 pb-12 mb-2"></div>
                                <div class="font-bold text-sm text-slate-900">${nombreJefe}</div>
                                <div class="text-xs font-semibold text-slate-700">Jefe de Mantenimiento</div>
                                <div class="text-[10px] text-slate-500">SALTYSNACK TUYERO C.A.</div>
                            </div>
                            <div>
                                <div class="border-b-2 border-slate-800 pb-12 mb-2"></div>
                                <div class="font-bold text-sm text-slate-900">${nombreGerentePlanta}</div>
                                <div class="text-xs font-semibold text-slate-700">Gerente de Planta</div>
                                <div class="text-[10px] text-slate-500">Aprobación Final y Conforme</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        function openModalPersonalizarInforme() {
            document.getElementById('cfgInformeTitulo').value = informeConfig.titulo;
            document.getElementById('cfgInformeSubtitulo').value = informeConfig.subtitulo;
            document.getElementById('cfgInformeDiagnostico').value = informeConfig.diagnostico;
            document.getElementById('cfgInformeRecomendaciones').value = informeConfig.recomendaciones;
            document.getElementById('cfgSecKPI').checked = informeConfig.secKPI;
            document.getElementById('cfgSecGrafico').checked = informeConfig.secGrafico;
            document.getElementById('cfgSecOTs').checked = informeConfig.secOTs;
            document.getElementById('cfgSecRepuestos').checked = informeConfig.secRepuestos;
            document.getElementById('cfgSecSSL').checked = informeConfig.secSSL;
            document.getElementById('cfgSecFirmas').checked = informeConfig.secFirmas;
            document.getElementById('modalPersonalizarInforme').classList.remove('hidden');
        }

        function guardarConfiguracionInforme(e) {
            e.preventDefault();
            informeConfig = {
                titulo: document.getElementById('cfgInformeTitulo').value.trim(),
                subtitulo: document.getElementById('cfgInformeSubtitulo').value.trim(),
                diagnostico: document.getElementById('cfgInformeDiagnostico').value.trim(),
                recomendaciones: document.getElementById('cfgInformeRecomendaciones').value.trim(),
                secKPI: document.getElementById('cfgSecKPI').checked,
                secGrafico: document.getElementById('cfgSecGrafico').checked,
                secOTs: document.getElementById('cfgSecOTs').checked,
                secRepuestos: document.getElementById('cfgSecRepuestos').checked,
                secSSL: document.getElementById('cfgSecSSL').checked,
                secFirmas: document.getElementById('cfgSecFirmas').checked
            };
            localStorage.setItem('GMAO_INFORME_CFG', JSON.stringify(informeConfig));
            closeModal('modalPersonalizarInforme');
            renderInformesView(document.getElementById('mainView'));
            mostrarToast('Estructura Guardada', 'La configuración del informe fue actualizada con éxito.', 'success');
        }

        // --- 13. FORMATO FORMAL DE IMPRESIÓN (PDF) PARA OTs E INFORMES ---
        function imprimirOT(otId) {
            const ot = db.ots.find(o => o.id === otId);
            if (!ot) return;
            const eq = db.equipos.find(e => e.id === ot.equipoId) || { name: ot.equipoId, planta: 'Planta Central', linea: 'General', criticidad: 'Alta' };

            const printSec = document.getElementById('printSection');
            printSec.innerHTML = `
                <div class="p-6 max-w-4xl mx-auto border-2 border-slate-800 text-slate-900 bg-white">
                    <!-- ENCABEZADO INSTITUCIONAL FORMAL -->
                    <div class="flex items-center justify-between border-b-2 border-slate-800 pb-3 mb-4">
                        <div class="flex items-center space-x-3">
                            <div class="w-12 h-12 bg-slate-900 text-white flex items-center justify-center font-bold text-xl rounded">
                                <i class="fas fa-industry"></i>
                            </div>
                            <div>
                                <h1 class="font-black text-lg uppercase tracking-wide leading-tight">SALTYSNACK TUYERO C.A.</h1>
                                <h2 class="text-xs font-bold text-slate-600 uppercase">Departamento de Mantenimiento e Infraestructura</h2>
                                <p class="text-[10px] text-slate-500">Sistema GMAO de Gestión y Confiabilidad Operativa</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <div class="text-xs font-bold uppercase text-slate-500">ORDEN DE TRABAJO TÉCNICA</div>
                            <div class="text-2xl font-black font-mono text-blue-800">${ot.id}</div>
                            <div class="text-[10px] text-slate-500">Fecha: ${ot.fechaProgramada || ot.fechaAsignacion}</div>
                        </div>
                    </div>

                    <!-- CUADRANTE 1: DATOS TÉCNICOS DEL ACTIVO -->
                    <div class="border border-slate-400 mb-4 text-xs">
                        <div class="bg-slate-200 px-3 py-1 font-bold uppercase text-[11px]">1. Identificación del Activo / Equipo</div>
                        <div class="grid grid-cols-4 p-2.5 gap-2">
                            <div><span class="text-slate-500 block text-[10px]">Tag Activo:</span><strong>${ot.equipoId}</strong></div>
                            <div><span class="text-slate-500 block text-[10px]">Denominación:</span><strong>${eq.name}</strong></div>
                            <div><span class="text-slate-500 block text-[10px]">Ubicación / Línea:</span><strong>${eq.planta} - ${eq.linea}</strong></div>
                            <div><span class="text-slate-500 block text-[10px]">Criticidad:</span><strong>${eq.criticidad}</strong></div>
                        </div>
                    </div>

                    <!-- CUADRANTE 2: DETALLES DE LA INTERVENCIÓN -->
                    <div class="border border-slate-400 mb-4 text-xs">
                        <div class="bg-slate-200 px-3 py-1 font-bold uppercase text-[11px]">2. Requerimiento Técnico y Diagnóstico</div>
                        <div class="p-2.5 space-y-1.5">
                            <div><span class="text-slate-500 text-[10px]">Tipo de Mantenimiento:</span> <strong>${ot.tipo}</strong> | <span class="text-slate-500 text-[10px]">Prioridad:</span> <strong>${ot.prioridad}</strong> | <span class="text-slate-500 text-[10px]">Estatus:</span> <strong>${ot.status}</strong></div>
                            <div><span class="text-slate-500 text-[10px]">Descripción de la Falla:</span> <p class="mt-0.5">${ot.descripcion}</p></div>
                            <div><span class="text-slate-500 text-[10px]">Trabajos Realizados:</span> <p class="mt-0.5">${ot.actividades || 'Mantenimiento preventivo completado según protocolo.'}</p></div>
                        </div>
                    </div>

                    <!-- CUADRANTE 3: EVIDENCIAS FOTOGRÁFICAS (ANTES Y DESPUÉS) -->
                    ${ot.fotoAntes || ot.fotoDespues ? `
                        <div class="border border-slate-400 mb-4 text-xs">
                            <div class="bg-slate-200 px-3 py-1 font-bold uppercase text-[11px]">3. Evidencias Fotográficas de Terreno</div>
                            <div class="grid grid-cols-2 p-2.5 gap-4 text-center">
                                ${ot.fotoAntes ? `
                                    <div>
                                        <span class="block text-[10px] font-bold text-slate-600 mb-1">EVIDENCIA INICIAL (ANTES)</span>
                                        <img src="${ot.fotoAntes}" class="max-h-36 mx-auto border rounded object-contain">
                                    </div>
                                ` : `<div><span class="text-[10px] text-slate-400">Sin foto previa</span></div>`}
                                ${ot.fotoDespues ? `
                                    <div>
                                        <span class="block text-[10px] font-bold text-slate-600 mb-1">RESULTADO FINAL (DESPUÉS)</span>
                                        <img src="${ot.fotoDespues}" class="max-h-36 mx-auto border rounded object-contain">
                                    </div>
                                ` : `<div><span class="text-[10px] text-slate-400">Sin foto de cierre</span></div>`}
                            </div>
                        </div>
                    ` : ''}

                    <!-- CUADRANTE 4: TIEMPOS Y REPUESTOS -->
                    <div class="grid grid-cols-2 gap-4 mb-6 text-xs">
                        <div class="border border-slate-400">
                            <div class="bg-slate-200 px-3 py-1 font-bold uppercase text-[11px]">4. Tiempos Operativos</div>
                            <div class="p-2.5 space-y-1">
                                <div class="flex justify-between"><span>Tiempo de Intervención:</span><strong>${ot.tiempoIntervencion || 0} horas</strong></div>
                                <div class="flex justify-between"><span>Tiempo de Parada (Downtime):</span><strong>${ot.tiempoParada || 0} horas</strong></div>
                            </div>
                        </div>
                        <div class="border border-slate-400">
                            <div class="bg-slate-200 px-3 py-1 font-bold uppercase text-[11px]">5. Repuestos Utilizados</div>
                            <div class="p-2.5 text-[11px]">
                                ${(ot.repuestosUsados && ot.repuestosUsados.length > 0) ? ot.repuestosUsados.map(r => `<div>&bull; ${r.name} (x${r.cant})</div>`).join('') : '<span class="text-slate-500">Ningún repuesto facturado.</span>'}
                            </div>
                        </div>
                    </div>

                    <!-- CUADRANTE 5: BLOQUE FORMAL DE FIRMAS INSTITUCIONALES (SOLO TÉCNICO Y JEFE DE MANTENIMIENTO DINÁMICO) -->
                    <div class="signature-block grid grid-cols-2 gap-10 pt-6 text-center text-xs">
                        <div>
                            <div class="border-b border-slate-800 pb-12 mb-1"></div>
                            <div class="font-bold text-slate-900">Firma Técnico Ejecutor</div>
                            <div class="text-[10px] text-slate-600 mt-1">Nombre / C.I.: ${(ot.tecnicoIds && ot.tecnicoIds.length > 0) ? ot.tecnicoIds.map(tid => { const u = db.users.find(x => x.id === tid); return u ? u.name : tid; }).join(', ') : '___________________'}</div>
                        </div>
                        <div>
                            <div class="border-b border-slate-800 pb-12 mb-1"></div>
                            <div class="font-bold text-slate-900">Jefe de Mantenimiento</div>
                            <div class="text-xs text-slate-800 font-bold mt-1">${((db.users || []).find(u => (u.cargo && u.cargo.toLowerCase().includes('jefe de mantenimiento')) || u.role === 'Gerente' || u.username === 'admin') || {}).name || 'Ing. Carlos Mendoza'}</div>
                            <div class="text-[10px] text-slate-500">Validado y Autorizado</div>
                        </div>
                    </div>
                </div>
                </div>
            `;

            window.print();
        }

        function imprimirInforme() {
            const printSec = document.getElementById('printSection');
            const previewArea = document.getElementById('previewInformeArea');
            if (!previewArea) return;
            printSec.innerHTML = previewArea.innerHTML;
            window.print();
        }

        function imprimirDashboardKPI() {
            const printSec = document.getElementById('printSection');
            if (!printSec) return;

            const horasBase = (kpiPeriodo === 'Anual') ? 8760.0 : 720.0;
            const periodoLabel = (kpiPeriodo === 'Anual') ? `Año ${kpiSelectedYear}` : `Mes ${kpiSelectedMonth}`;

            let otsEvaluadas = db.ots;
            if (kpiSelectedEquipo !== 'TODOS') {
                otsEvaluadas = otsEvaluadas.filter(o => o.equipoId === kpiSelectedEquipo);
            }
            if (kpiPeriodo === 'Anual') {
                otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '').startsWith(kpiSelectedYear));
            } else {
                otsEvaluadas = otsEvaluadas.filter(o => (o.fechaProgramada || o.fechaAsignacion || '').startsWith(kpiSelectedMonth));
            }

            const totalOTs = otsEvaluadas.length;
            const concluidas = otsEvaluadas.filter(o => o.status === 'Concluida' || o.status === 'Completada');
            const preventivas = otsEvaluadas.filter(o => o.tipo === 'Preventivo');
            const preventivasConcluidas = preventivas.filter(o => o.status === 'Concluida' || o.status === 'Completada');
            const correctivas = otsEvaluadas.filter(o => o.tipo === 'Correctivo');
            const correctivasConcluidas = correctivas.filter(o => o.status === 'Concluida' || o.status === 'Completada');

            const totalDowntime = otsEvaluadas.reduce((acc, o) => acc + parseFloat(o.tiempoParada || 0.0), 0.0);
            const totalIntervencion = concluidas.reduce((acc, o) => acc + parseFloat(o.tiempoIntervencion || 0.0), 0.0);
            const totalIntervencionCorrectiva = correctivasConcluidas.reduce((acc, o) => acc + parseFloat(o.tiempoIntervencion || 0.0), 0.0);

            const horasOperadas = Math.max(0.0, horasBase - totalDowntime);
            const disponibilidadPct = Math.min(100.0, Math.round((horasOperadas / horasBase) * 1000) / 10);
            const numFallas = correctivasConcluidas.length;
            const mttr = numFallas > 0 ? (Math.round((totalIntervencionCorrectiva / numFallas) * 10) / 10) : 0.0;
            const mtbf = numFallas > 0 ? (Math.round((horasOperadas / numFallas) * 10) / 10) : Math.round(horasBase);
            const mttrMeta = (db.config && db.config.mttrTarget) ? parseFloat(db.config.mttrTarget) : 2.0;
            const cumplimientoPrevPct = preventivas.length > 0 ? Math.round((preventivasConcluidas.length / preventivas.length) * 100) : 100;

            const eqNombreFiltro = kpiSelectedEquipo === 'TODOS' ? 'Todos los Activos de Planta' : ((db.equipos.find(e => e.id === kpiSelectedEquipo) || {}).name || kpiSelectedEquipo);

            // Firmas dinámicas estrictas
            const jefeUser = (db.users || []).find(u => (u.cargo && u.cargo.toLowerCase().includes('jefe de mantenimiento')) || u.role === 'Gerente' || u.username === 'admin');
            const nombreJefe = jefeUser ? jefeUser.name : 'Ing. Carlos Mendoza';

            const gerentePlantaUser = (db.users || []).find(u => (u.cargo && u.cargo.toLowerCase().includes('gerente de planta')) || (u.name && u.name.toLowerCase().includes('gerente de planta')));
            const nombreGerentePlanta = gerentePlantaUser ? gerentePlantaUser.name : 'Ing. Roberto Navarro';

            const filasOtsHtml = otsEvaluadas.slice(0, 30).map((o, idx) => {
                const eq = db.equipos.find(e => e.id === o.equipoId) || { name: o.equipoId };
                return `
                    <tr class="border-b border-slate-200 text-[10px]">
                        <td class="p-1.5 font-mono font-bold">${o.id}</td>
                        <td class="p-1.5">${o.fechaProgramada || o.fechaAsignacion}</td>
                        <td class="p-1.5 font-semibold">${o.equipoId} - ${eq.name.slice(0, 25)}</td>
                        <td class="p-1.5">${o.tipo}</td>
                        <td class="p-1.5 max-w-xs truncate">${o.descripcion.slice(0, 50)}</td>
                        <td class="p-1.5 text-center">${parseFloat(o.tiempoParada || 0).toFixed(1)} h</td>
                        <td class="p-1.5 text-center">${parseFloat(o.tiempoIntervencion || 0).toFixed(1)} h</td>
                        <td class="p-1.5 text-center font-bold">${o.status}</td>
                    </tr>
                `;
            }).join('');

            printSec.innerHTML = `
                <div class="p-6 max-w-5xl mx-auto border-2 border-slate-800 text-slate-900 bg-white">
                    <!-- ENCABEZADO FORMAL DE LA EMPRESA -->
                    <div class="flex items-center justify-between border-b-2 border-slate-800 pb-3 mb-4">
                        <div class="flex items-center space-x-3">
                            <div class="w-12 h-12 bg-slate-900 text-white flex items-center justify-center font-bold text-xl rounded">
                                <i class="fas fa-industry"></i>
                            </div>
                            <div>
                                <h1 class="font-black text-lg uppercase tracking-wide leading-tight">SALTYSNACK TUYERO C.A.</h1>
                                <h2 class="text-xs font-bold text-slate-600 uppercase">Departamento de Mantenimiento e Infraestructura</h2>
                                <p class="text-[10px] text-slate-500">Sistema GMAO de Gestión y Confiabilidad Operativa (ISO 14224 / SMRP)</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <div class="text-xs font-bold uppercase text-slate-500">PANEL GERENCIAL DE INDICADORES (KPIs)</div>
                            <div class="text-xl font-black font-mono text-blue-800">${periodoLabel}</div>
                            <div class="text-[10px] text-slate-500">Emisión: ${new Date().toLocaleDateString()} | Filtro: ${kpiSelectedEquipo}</div>
                        </div>
                    </div>

                    <!-- RESUMEN EJECUTIVO Y PARÁMETROS -->
                    <div class="bg-slate-50 border border-slate-300 p-3 rounded mb-4 text-xs">
                        <div class="grid grid-cols-3 gap-2">
                            <div><strong>Periodo:</strong> ${kpiPeriodo} (${periodoLabel})</div>
                            <div><strong>Activo Evaluado:</strong> ${eqNombreFiltro}</div>
                            <div><strong>Base de Tiempo:</strong> ${horasBase} horas planificadas</div>
                        </div>
                    </div>

                    <!-- TABLA PRINCIPAL DE INDICADORES INDUSTRIALES -->
                    <div class="mb-5">
                        <h3 class="text-xs font-bold uppercase text-slate-700 mb-2 border-b pb-1">1. Métricas Nucleares de Confiabilidad y Disponibilidad</h3>
                        <table class="w-full text-xs border-collapse border border-slate-300 mb-2">
                            <thead class="bg-slate-800 text-white text-[11px]">
                                <tr>
                                    <th class="p-2 text-left">Indicador SMRP</th>
                                    <th class="p-2 text-center">Valor Obtenido</th>
                                    <th class="p-2 text-center">Meta / Criterio</th>
                                    <th class="p-2 text-center">Condición</th>
                                    <th class="p-2 text-left">Interpretación Técnica</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-200">
                                <tr>
                                    <td class="p-2 font-bold">Disponibilidad Operativa</td>
                                    <td class="p-2 text-center font-black text-sm ${disponibilidadPct >= 95 ? 'text-blue-700' : 'text-amber-600'}">${disponibilidadPct}%</td>
                                    <td class="p-2 text-center font-mono">&ge; 95.0%</td>
                                    <td class="p-2 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${disponibilidadPct >= 95 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">${disponibilidadPct >= 95 ? 'CONFORME' : 'ALERTA'}</span></td>
                                    <td class="p-2 text-[11px]">Horas producidas: ${horasOperadas.toFixed(1)} h. Downtime total: ${totalDowntime.toFixed(1)} h.</td>
                                </tr>
                                <tr>
                                    <td class="p-2 font-bold">MTBF (Tiempo Medio Entre Fallas)</td>
                                    <td class="p-2 text-center font-black text-sm text-indigo-700">${mtbf} h</td>
                                    <td class="p-2 text-center font-mono">Maximizar</td>
                                    <td class="p-2 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-100 text-indigo-800">${numFallas} Fallas</span></td>
                                    <td class="p-2 text-[11px]">Confiabilidad promedio entre paradas imprevistas en la línea.</td>
                                </tr>
                                <tr>
                                    <td class="p-2 font-bold">MTTR (Tiempo Medio de Reparación)</td>
                                    <td class="p-2 text-center font-black text-sm ${mttr <= mttrMeta ? 'text-emerald-700' : 'text-amber-600'}">${mttr} h</td>
                                    <td class="p-2 text-center font-mono">&le; ${mttrMeta.toFixed(1)} h (Configurado)</td>
                                    <td class="p-2 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${mttr <= mttrMeta ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">${mttr <= mttrMeta ? 'ÓPTIMO' : 'DESVIADO'}</span></td>
                                    <td class="p-2 text-[11px]">Efectividad y rapidez de respuesta de la cuadrilla técnica ante paradas.</td>
                                </tr>
                                <tr>
                                    <td class="p-2 font-bold">Cumplimiento Preventivo</td>
                                    <td class="p-2 text-center font-black text-sm text-teal-700">${cumplimientoPrevPct}%</td>
                                    <td class="p-2 text-center font-mono">&ge; 90.0%</td>
                                    <td class="p-2 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${cumplimientoPrevPct >= 90 ? 'bg-teal-100 text-teal-800' : 'bg-amber-100 text-amber-800'}">${cumplimientoPrevPct >= 90 ? 'ALTO' : 'REGULAR'}</span></td>
                                    <td class="p-2 text-[11px]">${preventivasConcluidas.length} ejecutadas de ${preventivas.length} rutinas programadas.</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- CARGA OPERATIVA Y DIAGNÓSTICO -->
                    <div class="grid grid-cols-2 gap-4 mb-5 text-xs">
                        <div class="border border-slate-300 p-3 rounded bg-slate-50">
                            <h4 class="font-bold text-slate-800 mb-1.5 uppercase text-[11px]">2. Carga Operativa del Periodo</h4>
                            <div class="space-y-1 text-[11px]">
                                <div class="flex justify-between"><span>Total Órdenes Evaluadas:</span><strong>${totalOTs}</strong></div>
                                <div class="flex justify-between"><span>Órdenes Concluidas / Cerradas:</span><strong class="text-emerald-700">${concluidas.length}</strong></div>
                                <div class="flex justify-between"><span>Órdenes Correctivas (Averías):</span><strong class="text-red-600">${correctivas.length}</strong></div>
                                <div class="flex justify-between"><span>Horas Hombre de Intervención:</span><strong>${totalIntervencion.toFixed(1)} h</strong></div>
                            </div>
                        </div>
                        <div class="border border-slate-300 p-3 rounded bg-slate-50">
                            <h4 class="font-bold text-slate-800 mb-1.5 uppercase text-[11px]">3. Diagnóstico de Planta</h4>
                            <p class="text-[11px] leading-relaxed text-slate-700">
                                ${disponibilidadPct >= 95 
                                    ? `La planta opera dentro de los estándares de confiabilidad (>95%) en el periodo evaluado (${periodoLabel}). Se recomienda sostener la lubricación y frecuencias de inspección predictiva.`
                                    : `Se detectaron desviaciones de confiabilidad operativa (${disponibilidadPct}% vs meta 95%). La parada de ${totalDowntime.toFixed(1)} h requiere priorizar el reemplazo de componentes con alta tasa de falla.`}
                            </p>
                        </div>
                    </div>

                    <!-- TABLA DETALLADA DE ÓRDENES DE TRABAJO EVALUADAS -->
                    <div class="mb-6">
                        <h3 class="text-xs font-bold uppercase text-slate-700 mb-2 border-b pb-1">4. Registro Detallado de Intervenciones en el Periodo (${otsEvaluadas.length} órdenes)</h3>
                        <table class="w-full text-left border-collapse border border-slate-300">
                            <thead class="bg-slate-100 text-slate-800 text-[10px]">
                                <tr>
                                    <th class="p-1.5 border">N° OT</th>
                                    <th class="p-1.5 border">Fecha</th>
                                    <th class="p-1.5 border">Equipo</th>
                                    <th class="p-1.5 border">Tipo</th>
                                    <th class="p-1.5 border">Descripción</th>
                                    <th class="p-1.5 border text-center">Parada</th>
                                    <th class="p-1.5 border text-center">Trabajo</th>
                                    <th class="p-1.5 border text-center">Estatus</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${filasOtsHtml || '<tr><td colspan="8" class="p-3 text-center text-slate-400">Sin intervenciones registradas en este periodo.</td></tr>'}
                            </tbody>
                        </table>
                    </div>

                    <!-- BLOQUE DE FIRMAS AUTORIZADAS (RESTRINGIDO ESTRICTAMENTE A 2 ROLES) -->
                    <div class="grid grid-cols-2 gap-12 pt-6 text-center text-xs border-t-2 border-slate-800">
                        <div>
                            <div class="border-b border-slate-800 pb-12 mb-1.5"></div>
                            <div class="font-bold text-slate-900">${nombreJefe}</div>
                            <div class="text-[11px] font-semibold text-slate-600">Jefe de Mantenimiento</div>
                            <div class="text-[9px] text-slate-400">Departamento de Mantenimiento e Infraestructura</div>
                        </div>
                        <div>
                            <div class="border-b border-slate-800 pb-12 mb-1.5"></div>
                            <div class="font-bold text-slate-900">${nombreGerentePlanta}</div>
                            <div class="text-[11px] font-semibold text-slate-600">Gerente de Planta</div>
                            <div class="text-[9px] text-slate-400">Dirección de Operaciones Industriales</div>
                        </div>
                    </div>
                </div>
            `;

            window.print();
        }

        function generarInformeTecnicoKPI(eqId) {
            imprimirDashboardKPI();
        }

        // --- 14. EXPORTACIÓN PROFESIONAL A EXCEL (ONLINE VÍA OPENPYXL Y OFFLINE CLIENTE) ---
        function exportarMatrizOTExcel() {
            // Si hay conexión con el servidor backend, descargar el archivo generado con openpyxl exacto a la matriz
            if (navigator.onLine) {
                window.location.href = '/api/reports/matriz-ot-excel';
                mostrarToast('Descargando Excel', 'Generando matriz corporativa de O.T. con Dashboard...', 'success');
                return;
            }

            // MODO 100% OFFLINE CON SHEETJS
            try {
                if (typeof XLSX === 'undefined') {
                    alert("Exportación offline: guardando archivo de texto tabulado compatible con Excel.");
                    exportarOTsCSVOffline();
                    return;
                }

                const wb = XLSX.utils.book_new();

                // Hoja 1: Dashboard
                const dashData = [
                    ["SALTYSNACK TUYERO C.A. — PANEL DE CONTROL GERENCIAL DE MANTENIMIENTO"],
                    ["Indicadores Clave de Desempeño y Carga Operativa"],
                    [],
                    ["Total Órdenes", "", "", "OT Completadas", "", "", "OT En Proceso / Pendientes", "", "", "Horas de Mantenimiento"],
                    [db.ots.length, "", "", db.ots.filter(o => o.status === 'Concluida').length, "", "", db.ots.filter(o => o.status !== 'Concluida').length, "", "", db.ots.reduce((a, b) => a + parseFloat(b.tiempoIntervencion || 0), 0)],
                    [], [], [],
                    ["RESUMEN DE ÓRDENES POR ESTATUS", "", "", "", "CARGA DE TRABAJO POR TÉCNICO"],
                    ["Estatus", "Cantidad de OT", "% del Total", "", "Técnico Responsable", "OT Asignadas", "Tiempo Total (Min)"],
                    ["Completada", db.ots.filter(o => o.status === 'Concluida').length, "", "", "Técnico Senior", db.ots.length, 120],
                    ["En Proceso", db.ots.filter(o => o.status === 'En Proceso').length, "", "", "", 0, 0],
                    ["Pendiente", db.ots.filter(o => o.status === 'Pendiente').length, "", "", "", 0, 0]
                ];
                const wsDash = XLSX.utils.aoa_to_sheet(dashData);
                XLSX.utils.book_append_sheet(wb, wsDash, "Dashboard");

                // Hoja 2: Control de Órdenes (OT)
                const otData = [
                    ["SALTYSNACK TUYERO C.A. - CONTROL MAESTRO DE ÓRDENES DE TRABAJO (OT)"],
                    ["Departamento de Mantenimiento e Infraestructura"],
                    [],
                    ["N° OT", "Fecha Emisión", "Semana", "Línea / Equipo", "Tipo de Mantenimiento", "Descripción de la Actividad", "Técnico Responsable", "Estatus", "Prioridad", "Repuestos / Insumos", "Tiempo Ejecución (Min)", "Observaciones / Causa Raíz"]
                ];

                db.ots.forEach(ot => {
                    const eq = db.equipos.find(e => e.id === ot.equipoId) || { name: ot.equipoId };
                    const reps = (ot.repuestosUsados || []).map(r => r.name).join(', ') || 'Sin repuestos';
                    const tiempoMin = Math.round(parseFloat(ot.tiempoIntervencion || 0) * 60);
                    otData.push([
                        ot.id,
                        ot.fechaProgramada || ot.fechaAsignacion || '',
                        'Semana ' + (new Date(ot.fechaProgramada || Date.now()).getWeek ? new Date().getWeek() : '30'),
                        eq.name,
                        ot.tipo,
                        ot.descripcion,
                        (ot.tecnicoIds && ot.tecnicoIds.length > 0) ? ot.tecnicoIds.join(', ') : 'Técnico Asignado',
                        ot.status === 'Concluida' ? 'Completada' : ot.status,
                        ot.prioridad,
                        reps,
                        tiempoMin,
                        ot.actividades || 'Operativo sin novedad'
                    ]);
                });

                const wsOTs = XLSX.utils.aoa_to_sheet(otData);
                XLSX.utils.book_append_sheet(wb, wsOTs, "Control de Órdenes (OT)");

                XLSX.writeFile(wb, `MATRIZ_CONTROL_DE_OT_OFFLINE_${new Date().toISOString().slice(0,10)}.xlsx`);
                mostrarToast('Excel Offline', 'Archivo corporativo descargado exitosamente en modo offline.', 'success');
            } catch (err) {
                console.error("Error en exportación Excel offline:", err);
                exportarOTsCSVOffline();
            }
        }

        function exportarOTsCSVOffline() {
            let csv = "\\uFEFFN° OT;Fecha;Equipo;Tipo;Descripcion;Estatus;Prioridad;Tiempo (h)\\n";
            db.ots.forEach(o => {
                csv += `"${o.id}";"${o.fechaProgramada || ''}";"${o.equipoId}";"${o.tipo}";"${(o.descripcion||'').replace(/"/g, '""')}";"${o.status}";"${o.prioridad}";"${o.tiempoIntervencion || 0}"\\n`;
            });
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = `MATRIZ_OT_OFFLINE_${new Date().toISOString().slice(0,10)}.csv`;
            link.click();
        }

        function exportarCronogramaAnualExcel() {
            if (navigator.onLine) {
                window.location.href = '/api/reports/cronograma-anual-excel?anio=2026';
                mostrarToast('Descargando Cronograma', 'Generando Cronograma Anual Preventivo 2026...', 'success');
            } else {
                exportarMatrizOTExcel();
            }
        }

        // --- 15. OTRAS VISTAS (MIS OTS, ALMACÉN, PROVEEDORES, COMPRAS, EQUIPOS, USUARIOS) ---
        function renderMisOTsView(container) {
            const misOTs = db.ots.filter(o => (o.tecnicoIds && o.tecnicoIds.includes(currentUser.id)) || o.tecnicoAcompanante === currentUser.id);
            const rowsHtml = misOTs.map(ot => {
                const eq = db.equipos.find(e => e.id === ot.equipoId) || { name: ot.equipoId };
                return `
                    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-3">
                        <div class="flex justify-between items-start">
                            <div>
                                <span class="font-mono text-xs font-bold text-blue-700">${ot.id}</span>
                                <h3 class="font-bold text-sm text-slate-800 mt-0.5">${eq.name}</h3>
                                <div class="text-[11px] text-slate-500 font-mono">${ot.equipoId}</div>
                            </div>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${ot.status === 'Concluida' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">${ot.status}</span>
                        </div>
                        <p class="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border">${ot.descripcion}</p>
                        <div class="flex items-center justify-between text-xs pt-2 border-t text-slate-500">
                            <span>Prog: <strong>${ot.fechaProgramada || '-'}</strong></span>
                            <div class="space-x-1">
                                <button onclick="imprimirOT('${ot.id}')" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 rounded text-slate-700 font-semibold" title="Imprimir"><i class="fas fa-print"></i></button>
                                <button onclick="openModalCierreOT('${ot.id}')" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded font-semibold shadow">Bitácora / Cierre</button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                        <div>
                            <h2 class="text-base font-bold text-slate-800">Mis Órdenes de Trabajo Asignadas</h2>
                            <p class="text-xs text-slate-500">Ejecución en Planta y Registro Fotográfico de Terreno</p>
                        </div>
                        <button onclick="openModalOT(false)" class="bg-amber-600 hover:bg-amber-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow">
                            <i class="fas fa-bolt mr-1"></i> Reportar OT Inmediata
                        </button>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${rowsHtml.length > 0 ? rowsHtml : `<div class="col-span-3 p-8 text-center text-slate-400 bg-white rounded-xl">No tienes órdenes de trabajo pendientes de ejecución.</div>`}
                    </div>
                </div>
            `;
        }

        function renderAlmacenView(container) {
            const rowsHtml = db.repuestos.map(r => {
                const isLow = r.stock <= r.stockMin;
                return `
                    <tr class="hover:bg-slate-50 transition">
                        <td class="p-2.5 font-mono font-bold text-xs text-slate-800">${r.codigo}</td>
                        <td class="p-2.5 text-xs font-semibold text-slate-700">${r.name}</td>
                        <td class="p-2.5 text-center font-bold text-xs ${isLow ? 'text-red-600' : 'text-slate-800'}">${r.stock} ${r.um}</td>
                        <td class="p-2.5 text-center text-xs text-slate-500">${r.stockMin} ${r.um}</td>
                        <td class="p-2.5 text-right font-mono text-xs">$${r.costo.toFixed(2)}</td>
                        <td class="p-2.5 text-center">
                            ${isLow ? `<span class="bg-red-100 text-red-800 px-2 py-0.5 rounded-full text-[10px] font-bold">¡Stock Bajo!</span>` : `<span class="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full text-[10px] font-bold">Óptimo</span>`}
                        </td>
                        <td class="p-2.5 text-right space-x-1">
                            <button onclick="openModalRepuesto('${r.id}')" class="text-blue-600 hover:text-blue-800 p-1"><i class="fas fa-edit"></i></button>
                            <button onclick="eliminarRepuesto('${r.id}')" class="text-red-500 hover:text-red-700 p-1"><i class="fas fa-trash"></i></button>
                        </td>
                    </tr>
                `;
            }).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                        <div>
                            <h2 class="text-base font-bold text-slate-800">Almacén de Repuestos e Insumos Industriales</h2>
                            <p class="text-xs text-slate-500">Control de Existencias y Descuento Automático por OT</p>
                        </div>
                        <button onclick="openModalRepuesto(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow">
                            <i class="fas fa-plus mr-1"></i> + Registrar Repuesto
                        </button>
                    </div>
                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">Código</th>
                                    <th class="p-2.5">Descripción del Material</th>
                                    <th class="p-2.5 text-center">Stock Actual</th>
                                    <th class="p-2.5 text-center">Mínimo</th>
                                    <th class="p-2.5 text-right">Costo Unit.</th>
                                    <th class="p-2.5 text-center">Alerta</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">${rowsHtml}</tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        function renderProveedoresView(container) {
            const rowsHtml = db.proveedores.map(p => `
                <tr class="hover:bg-slate-50 transition">
                    <td class="p-2.5 font-mono font-bold text-xs text-slate-800">${p.rif}</td>
                    <td class="p-2.5 text-xs font-semibold text-slate-700">${p.nombre}</td>
                    <td class="p-2.5 text-xs text-slate-500">${p.categoria}</td>
                    <td class="p-2.5 text-xs text-slate-600">${p.contacto || '-'}</td>
                    <td class="p-2.5 text-xs text-slate-600">${p.telefono || '-'}</td>
                    <td class="p-2.5 text-xs text-slate-600">${p.email || '-'}</td>
                    <td class="p-2.5 text-right space-x-1">
                        <button onclick="openModalProveedor('${p.id}')" class="text-blue-600 hover:text-blue-800 p-1"><i class="fas fa-edit"></i></button>
                        <button onclick="eliminarProveedor('${p.id}')" class="text-red-500 hover:text-red-700 p-1"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                        <div>
                            <h2 class="text-base font-bold text-slate-800">Directorio de Proveedores y Servicios Especializados</h2>
                            <p class="text-xs text-slate-500">Gestión de Compras y Suministros para Mantenimiento</p>
                        </div>
                        <button onclick="openModalProveedor(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow">
                            <i class="fas fa-plus mr-1"></i> + Registrar Proveedor
                        </button>
                    </div>
                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">RIF / NIF</th>
                                    <th class="p-2.5">Razón Social</th>
                                    <th class="p-2.5">Categoría</th>
                                    <th class="p-2.5">Contacto</th>
                                    <th class="p-2.5">Teléfono</th>
                                    <th class="p-2.5">Email</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">${rowsHtml}</tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        function renderComprasView(container) {
            const rowsHtml = db.comprasMateriales.map(c => `
                <tr class="hover:bg-slate-50 transition">
                    <td class="p-2.5 font-mono text-xs text-slate-500">${c.fecha}</td>
                    <td class="p-2.5 text-xs font-semibold text-slate-700">${c.descripcion}</td>
                    <td class="p-2.5 text-center text-xs font-bold">${c.cantSolicitada}</td>
                    <td class="p-2.5 text-center text-xs font-bold text-emerald-600">${c.cantRecibida}</td>
                    <td class="p-2.5 text-right font-mono text-xs">$${(parseFloat(c.precio) || 0).toFixed(2)}</td>
                    <td class="p-2.5 text-xs text-slate-500">${c.observaciones || '-'}</td>
                    <td class="p-2.5 text-right space-x-1">
                        <button onclick="openModalCompra('${c.id}')" title="Modificar Solicitud de Compra" class="text-blue-600 hover:text-blue-800 p-1"><i class="fas fa-edit"></i></button>
                        <button onclick="eliminarCompra('${c.id}')" title="Eliminar Solicitud" class="text-red-500 hover:text-red-700 p-1"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                        <div>
                            <h2 class="text-base font-bold text-slate-800">Control de Requisiciones y Compras</h2>
                            <p class="text-xs text-slate-500">Trazabilidad de Insumos y Repuestos Críticos Solicitados</p>
                        </div>
                        <button onclick="openModalCompra(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow">
                            <i class="fas fa-plus mr-1"></i> + Solicitud de Compra
                        </button>
                    </div>
                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">Fecha</th>
                                    <th class="p-2.5">Material Solicitado</th>
                                    <th class="p-2.5 text-center">Cant. Solicitada</th>
                                    <th class="p-2.5 text-center">Cant. Recibida</th>
                                    <th class="p-2.5 text-right">Precio Est.</th>
                                    <th class="p-2.5">Observaciones</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">${rowsHtml}</tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        function toggleEquiposSortOrder() {
            equiposSortOrder = (equiposSortOrder === 'ASC') ? 'DESC' : 'ASC';
            renderEquiposView(document.getElementById('mainView'));
        }

        function renderEquiposView(container) {
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
            `).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm gap-3">
                        <div>
                            <h2 class="text-base font-bold text-slate-800">Árbol de Activos y Ubicaciones Técnicas (ISO 14224)</h2>
                            <p class="text-xs text-slate-500">SALTYSNACK TUYERO C.A. | Jerarquía de Equipos y Sistemas de Planta</p>
                        </div>
                        <div class="flex items-center space-x-2">
                            <button onclick="toggleEquiposSortOrder()" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold border flex items-center space-x-1.5 transition">
                                <i class="fas fa-sort-alpha-${equiposSortOrder === 'ASC' ? 'down' : 'up-alt'} text-blue-600"></i>
                                <span>Orden Tag: <strong>${equiposSortOrder === 'ASC' ? 'Ascendente (A-Z, 0-9)' : 'Descendente (Z-A, 9-0)'}</strong></span>
                            </button>
                            <button onclick="openModalEquipo(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow flex items-center space-x-1">
                                <i class="fas fa-plus mr-1"></i> + Registrar Equipo
                            </button>
                        </div>
                    </div>
                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5 cursor-pointer select-none hover:bg-slate-800 transition" onclick="toggleEquiposSortOrder()" title="Clic para alternar orden natural">
                                        <div class="flex items-center space-x-1">
                                            <span>Tag / Código</span>
                                            <i class="fas fa-sort-${equiposSortOrder === 'ASC' ? 'amount-down text-blue-400' : 'amount-up-alt text-amber-400'} ml-1"></i>
                                            <span class="text-[9px] uppercase px-1 bg-slate-800 text-slate-300 rounded font-mono">${equiposSortOrder}</span>
                                        </div>
                                    </th>
                                    <th class="p-2.5">Denominación del Activo</th>
                                    <th class="p-2.5">Ubicación / Línea</th>
                                    <th class="p-2.5 text-center">Criticidad</th>
                                    <th class="p-2.5 text-center">Estatus</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">${rowsHtml}</tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        function renderUsuariosView(container) {
            const rowsHtml = db.users.map(u => `
                <tr class="hover:bg-slate-50 transition">
                    <td class="p-2.5 font-mono text-xs font-bold text-slate-800">${u.username}</td>
                    <td class="p-2.5 text-xs font-semibold text-slate-700">${u.name}</td>
                    <td class="p-2.5 text-xs"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800">${u.role}</span></td>
                    <td class="p-2.5 text-xs text-slate-600">${u.departamento || 'Mantenimiento'}</td>
                    <td class="p-2.5 text-right space-x-1">
                        <button onclick="openModalUsuario('${u.id}')" class="text-blue-600 hover:text-blue-800 p-1"><i class="fas fa-edit"></i></button>
                        <button onclick="eliminarUsuario('${u.id}')" class="text-red-500 hover:text-red-700 p-1"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `).join('');

            container.innerHTML = `
                <div class="space-y-4">
                    <div class="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                        <div>
                            <h2 class="text-base font-bold text-slate-800">Control de Usuarios y Seguridad (RBAC)</h2>
                            <p class="text-xs text-slate-500">Roles Autorizados: Gerente, Técnico, Solicitante y Jefe SSL</p>
                        </div>
                        <button onclick="openModalUsuario(false)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-xs font-semibold shadow">
                            <i class="fas fa-plus mr-1"></i> + Crear Usuario
                        </button>
                    </div>
                    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-slate-900 text-white">
                                <tr>
                                    <th class="p-2.5">Usuario</th>
                                    <th class="p-2.5">Nombre Completo</th>
                                    <th class="p-2.5">Rol de Acceso</th>
                                    <th class="p-2.5">Departamento</th>
                                    <th class="p-2.5 text-right">Acciones</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100">${rowsHtml}</tbody>
                        </table>
                    </div>
                </div>
            `;
        }

        function renderCronogramaView(container, esRefrigeracion = false) {
            // Vista de refrigeración especializada
            renderCronogramaAnualView(container);
        }

        // --- 16. MODALES Y REGISTROS (CONTROLADORES) ---
        function closeModal(id) {
            document.getElementById(id).classList.add('hidden');
        }

        function openModalPlanPreventivo(planId = false, esRefr = false) {
            const form = document.getElementById('formPlanPreventivo');
            form.reset();
            document.getElementById('planEditId').value = planId || '';
            document.getElementById('planEsRefrigeracion').value = esRefr ? 'true' : 'false';

            const eqSel = document.getElementById('planEquipo');
            eqSel.innerHTML = db.equipos.map(e => `<option value="${e.id}">${e.id} - ${e.name}</option>`).join('');

            // Checkboxes de técnicos
            const tecCont = document.getElementById('planTecnicosContainer');
            const tecs = db.users.filter(u => u.role === 'Tecnico');
            tecCont.innerHTML = tecs.map(u => `
                <label class="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" name="planTec" value="${u.id}" class="rounded">
                    <span>${u.name}</span>
                </label>
            `).join('');

            if (planId) {
                const p = db.planesPreventivos.find(x => x.id === planId);
                if (p) {
                    eqSel.value = p.equipoId;
                    document.getElementById('planNombre').value = p.nombre;
                    document.getElementById('planFrecuenciaTipo').value = p.frecuenciaTipo || 'meses';
                    document.getElementById('planFrecuenciaValor').value = p.frecuenciaValor || 1;
                    document.getElementById('planUltimaFecha').value = p.ultimaFecha;
                    document.getElementById('planProximaFecha').value = p.proximaFecha;
                    (p.tecnicoIds || []).forEach(tid => {
                        const cb = tecCont.querySelector(`input[value="${tid}"]`);
                        if (cb) cb.checked = true;
                    });
                }
            } else {
                document.getElementById('planUltimaFecha').value = new Date().toISOString().slice(0, 10);
                actualizarCalculoFrecuencia();
            }

            document.getElementById('modalPlanPreventivo').classList.remove('hidden');
        }

        document.getElementById('formPlanPreventivo').addEventListener('submit', function(e) {
            e.preventDefault();
            const editId = document.getElementById('planEditId').value;
            const esRefr = document.getElementById('planEsRefrigeracion').value === 'true';
            const fTipo = document.getElementById('planFrecuenciaTipo').value;
            const fValor = parseInt(document.getElementById('planFrecuenciaValor').value) || 1;

            let frecTexto = `${fValor} ${fTipo}`;
            if (fTipo === 'meses' && fValor === 1) frecTexto = 'Mensual';
            if (fTipo === 'dias' && fValor === 1) frecTexto = 'Diario';
            if (fTipo === 'semanas' && fValor === 1) frecTexto = 'Semanal';
            if (fTipo === 'semanas' && fValor === 2) frecTexto = 'Quincenal';

            const selectedTecs = Array.from(document.querySelectorAll('input[name="planTec"]:checked')).map(cb => cb.value);

            const payload = {
                id: editId || `${esRefr ? 'PLR' : 'PLN'}-${String(db.planesPreventivos.length + 1).padStart(2, '0')}`,
                equipoId: document.getElementById('planEquipo').value,
                nombre: document.getElementById('planNombre').value.trim(),
                frecuencia: frecTexto,
                frecuenciaTipo: fTipo,
                frecuenciaValor: fValor,
                ultimaFecha: document.getElementById('planUltimaFecha').value,
                proximaFecha: document.getElementById('planProximaFecha').value,
                tecnicoIds: selectedTecs,
                esRefrigeracion: esRefr
            };

            if (editId) {
                const idx = db.planesPreventivos.findIndex(x => x.id === editId);
                if (idx !== -1) db.planesPreventivos[idx] = payload;
            } else {
                db.planesPreventivos.push(payload);
            }

            saveDatabase();
            closeModal('modalPlanPreventivo');
            renderCronogramaAnualView(document.getElementById('mainView'));
            mostrarToast('Rutina Guardada', 'Plan de mantenimiento preventivo proyectado correctamente.', 'success');
        });

        function eliminarPlanPreventivo(id) {
            if (!confirm("¿Está seguro de eliminar esta rutina preventiva?")) return;
            db.planesPreventivos = db.planesPreventivos.filter(p => p.id !== id);
            saveDatabase();
            renderCronogramaAnualView(document.getElementById('mainView'));
        }

        function openModalOT(otId = false) {
            const form = document.getElementById('formOT');
            form.reset();
            document.getElementById('otId').value = otId || '';
            document.getElementById('otFotoAntesBase64').value = '';
            document.getElementById('previewFotoInicialOT').innerHTML = '';

            const titleEl = document.getElementById('modalOTTitle');

            // Ordenamiento alfanumérico natural de equipos en selector
            const eqSel = document.getElementById('otEquipo');
            const sortedEquipos = [...db.equipos].sort((a, b) => naturalCompare(a.id, b.id, true));
            eqSel.innerHTML = sortedEquipos.map(e => `<option value="${e.id}">${e.id} - ${e.name}</option>`).join('');

            const tecCont = document.getElementById('otTecnicosContainer');
            const tecs = db.users.filter(u => u.role === 'Tecnico');
            tecCont.innerHTML = tecs.map(u => `
                <label class="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" name="otTec" value="${u.id}" class="rounded">
                    <span>${u.name}</span>
                </label>
            `).join('');

            if (otId) {
                const ot = db.ots.find(x => x.id === otId);
                if (ot) {
                    if (titleEl) titleEl.innerHTML = `<i class="fas fa-edit text-blue-600 mr-2"></i> Modificar Orden de Trabajo (${ot.id})`;
                    document.getElementById('otTipo').value = ot.tipo;
                    document.getElementById('otPrioridad').value = ot.prioridad;
                    eqSel.value = ot.equipoId;
                    document.getElementById('otDescripcion').value = ot.descripcion;
                    document.getElementById('otFechaProgramada').value = ot.fechaProgramada || ot.fechaAsignacion;
                    
                    // Preservar valores internos y estado
                    document.getElementById('otStatusVal').value = ot.status || 'Pendiente';
                    document.getElementById('otFechaAsignacionVal').value = ot.fechaAsignacion || '';
                    document.getElementById('otFechaInicioVal').value = ot.fechaInicio || '';
                    document.getElementById('otFechaFinVal').value = ot.fechaFin || '';
                    document.getElementById('otActividadesVal').value = ot.actividades || '';
                    document.getElementById('otTiempoIntervencionVal').value = ot.tiempoIntervencion || 0.0;
                    document.getElementById('otTiempoParadaVal').value = ot.tiempoParada || 0.0;
                    document.getElementById('otFotoDespuesBase64').value = ot.fotoDespues || '';
                    document.getElementById('otRepuestosUsadosVal').value = JSON.stringify(ot.repuestosUsados || []);
                    document.getElementById('otTecnicoAcompananteVal').value = ot.tecnicoAcompanante || '';

                    if (ot.fotoAntes) {
                        document.getElementById('otFotoAntesBase64').value = ot.fotoAntes;
                        document.getElementById('previewFotoInicialOT').innerHTML = `<img src="${ot.fotoAntes}" class="w-14 h-14 object-cover rounded border">`;
                    }
                    (ot.tecnicoIds || []).forEach(tid => {
                        const cb = tecCont.querySelector(`input[value="${tid}"]`);
                        if (cb) cb.checked = true;
                    });
                }
            } else {
                if (titleEl) titleEl.innerHTML = `<i class="fas fa-clipboard-check text-blue-600 mr-2"></i> Crear Orden de Trabajo (Mantenimiento)`;
                document.getElementById('otFechaProgramada').value = new Date().toISOString().slice(0, 10);
                document.getElementById('otStatusVal').value = 'Pendiente';
                document.getElementById('otTiempoIntervencionVal').value = 0.0;
                document.getElementById('otTiempoParadaVal').value = 0.0;
                document.getElementById('otRepuestosUsadosVal').value = '[]';
            }

            document.getElementById('modalOT').classList.remove('hidden');
        }

        document.getElementById('formOT').addEventListener('submit', function(e) {
            e.preventDefault();
            const editId = document.getElementById('otId').value;
            const solId = document.getElementById('otSolicitudId').value;
            const selectedTecs = Array.from(document.querySelectorAll('input[name="otTec"]:checked')).map(cb => cb.value);

            let payload;

            if (editId) {
                const existing = db.ots.find(x => x.id === editId) || {};
                payload = {
                    ...existing,
                    id: editId,
                    tipo: document.getElementById('otTipo').value,
                    prioridad: document.getElementById('otPrioridad').value,
                    equipoId: document.getElementById('otEquipo').value,
                    descripcion: document.getElementById('otDescripcion').value.trim(),
                    tecnicoIds: selectedTecs,
                    fechaProgramada: document.getElementById('otFechaProgramada').value,
                    fotoAntes: document.getElementById('otFotoAntesBase64').value || existing.fotoAntes || '',
                    updatedAt: new Date().toISOString()
                };

                const idx = db.ots.findIndex(x => x.id === editId);
                if (idx !== -1) {
                    db.ots[idx] = payload;
                }
            } else {
                payload = {
                    id: `OT-2026-${String(db.ots.length + 1).padStart(3, '0')}`,
                    tipo: document.getElementById('otTipo').value,
                    prioridad: document.getElementById('otPrioridad').value,
                    equipoId: document.getElementById('otEquipo').value,
                    descripcion: document.getElementById('otDescripcion').value.trim(),
                    tecnicoIds: selectedTecs,
                    fechaAsignacion: new Date().toISOString().slice(0, 10),
                    fechaProgramada: document.getElementById('otFechaProgramada').value,
                    status: 'Pendiente',
                    fotoAntes: document.getElementById('otFotoAntesBase64').value,
                    fotoDespues: '',
                    tiempoIntervencion: 0.0,
                    tiempoParada: 0.0,
                    repuestosUsados: []
                };
                db.ots.unshift(payload);

                // Si proviene de solicitud interdepartamental, vincularla
                if (solId) {
                    const sol = db.solicitudesInterdepartamentales.find(s => s.id === solId);
                    if (sol) { sol.otVinculada = payload.id; sol.status = 'En proceso'; }
                }

                // Disparar notificaciones a los técnicos asignados
                selectedTecs.forEach(tid => {
                    dispararNotificacion('Tecnico', tid, 'Nueva OT Asignada', `Se le ha asignado la ${payload.id}: ${payload.descripcion.slice(0, 40)}`, 'info', 'ot', payload.id);
                });
            }

            // Persistencia local inmediata en base de datos offline
            saveDatabase();

            // Sincronización reactiva con backend API para confirmación inmediata
            if (navigator.onLine) {
                fetch('/api/work-orders', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }).then(res => res.json())
                  .then(data => console.log('OT reactively synced to server:', data))
                  .catch(err => console.warn('Offline or server unreachable:', err));
            }

            closeModal('modalOT');
            navigate(currentUser.role === 'Tecnico' ? 'mis-ots' : 'ots');
            mostrarToast(editId ? 'Orden Actualizada' : 'Orden Creada', `La Orden de Trabajo ${payload.id} ha sido ${editId ? 'actualizada' : 'registrada'} con confirmación inmediata.`, 'success');
        });

        function eliminarOT(otId) {
            if (!confirm(`¿Eliminar la orden ${otId}?`)) return;
            db.ots = db.ots.filter(o => o.id !== otId);
            db.solicitudesInterdepartamentales.forEach(s => { if (s.otVinculada === otId) s.otVinculada = null; });
            db.solicitudesSSL.forEach(s => { if (s.otVinculada === otId) s.otVinculada = null; });
            db.notificaciones = db.notificaciones.filter(n => !(n.enlaceTipo === 'ot' && n.enlaceId === otId));
            saveDatabase();
            navigate('ots');
        }

        // Cierre de OT
        let otRepuestosCierre = [];
        function openModalCierreOT(otId) {
            const ot = db.ots.find(o => o.id === otId);
            if (!ot) return;
            const eq = db.equipos.find(e => e.id === ot.equipoId) || { name: ot.equipoId };

            document.getElementById('cierreOtId').value = ot.id;
            document.getElementById('cierreFolioDisplay').textContent = ot.id;
            document.getElementById('cierreEquipoDisplay').textContent = `${ot.equipoId} - ${eq.name}`;
            document.getElementById('cierreFallaDisplay').textContent = ot.descripcion;
            document.getElementById('cierreTrabajo').value = ot.actividades || '';
            document.getElementById('cierreTiempoParada').value = ot.tiempoParada || '';
            document.getElementById('cierreTiempoIntervencion').value = ot.tiempoIntervencion || 0;
            document.getElementById('cierreFotoAntesBase64').value = ot.fotoAntes || '';
            document.getElementById('cierreFotoDespuesBase64').value = ot.fotoDespues || '';

            // Mostrar fotos existentes
            document.getElementById('previewFotoAntes').innerHTML = ot.fotoAntes ? `<img src="${ot.fotoAntes}" class="w-14 h-14 object-cover rounded border">` : '';
            document.getElementById('previewFotoDespues').innerHTML = ot.fotoDespues ? `<img src="${ot.fotoDespues}" class="w-14 h-14 object-cover rounded border">` : '';

            // Fechas por defecto
            const nowIso = new Date().toISOString().slice(0, 16);
            document.getElementById('cierreFechaInicio').value = ot.fechaInicio || nowIso;
            document.getElementById('cierreFechaFin').value = ot.fechaFin || nowIso;

            // Repuestos en modal
            otRepuestosCierre = JSON.parse(JSON.stringify(ot.repuestosUsados || []));
            renderTablaRepuestosCierre();

            // Cargar selector de Técnico de Apoyo / Acompañante
            const selAcomp = document.getElementById('cierreTecnicoAcompanante');
            if (selAcomp) {
                const tecnicosDisponibles = (db.users || []).filter(u => u.role === 'Tecnico' || (u.cargo && u.cargo.toLowerCase().includes('técnico')));
                selAcomp.innerHTML = '<option value="">-- Ninguno (Sin acompañante) --</option>' + 
                    tecnicosDisponibles.map(t => `<option value="${t.id}">${t.name} (${t.cargo || 'Técnico'})</option>`).join('');
                selAcomp.value = ot.tecnicoAcompanante || '';
            }

            // Select de almacén
            const selAlm = document.getElementById('selectRepuestoAlmacen');
            selAlm.innerHTML = '<option value="">[ Seleccione del Almacén o escriba libre ]</option>' + db.repuestos.map(r => `<option value="${r.id}">${r.codigo} - ${r.name} (Stock: ${r.stock})</option>`).join('');

            document.getElementById('modalCierreOT').classList.remove('hidden');
            calcularTiempoIntervencionAutomatico();
        }

        function calcularTiempoIntervencionAutomatico() {
            const inicio = document.getElementById('cierreFechaInicio').value;
            const fin = document.getElementById('cierreFechaFin').value;
            if (!inicio || !fin) return;
            const diffMs = new Date(fin) - new Date(inicio);
            if (diffMs > 0) {
                const diffHours = Math.round((diffMs / (1000 * 60 * 60)) * 10) / 10;
                document.getElementById('cierreTiempoIntervencion').value = diffHours;
            }
        }

        function agregarRepuestoAOT() {
            const selId = document.getElementById('selectRepuestoAlmacen').value;
            const libreName = document.getElementById('nombreMaterialLibre').value.trim();
            const cant = parseInt(document.getElementById('cantRepuesto').value) || 1;

            let name = libreName;
            let costo = 0;
            let repId = null;

            if (selId) {
                const rep = db.repuestos.find(r => r.id === selId);
                if (rep) {
                    name = rep.name;
                    costo = rep.costo;
                    repId = rep.id;
                }
            }

            if (!name) { alert("Seleccione o escriba un repuesto."); return; }
            otRepuestosCierre.push({ id: repId, name: name, cant: cant, costo: costo });
            renderTablaRepuestosCierre();
            document.getElementById('nombreMaterialLibre').value = '';
            document.getElementById('cantRepuesto').value = '';
            document.getElementById('selectRepuestoAlmacen').value = '';
        }

        function renderTablaRepuestosCierre() {
            const tbody = document.getElementById('listaRepuestosUsados');
            tbody.innerHTML = otRepuestosCierre.map((r, i) => `
                <tr>
                    <td class="p-2 font-semibold text-slate-800">${r.name}</td>
                    <td class="p-2 font-mono text-center">${r.cant}</td>
                    <td class="p-2 text-right">
                        <button type="button" onclick="quitarRepuestoOT(${i})" class="text-red-500 hover:text-red-700 font-bold">&times;</button>
                    </td>
                </tr>
            `).join('');
        }

        function quitarRepuestoOT(idx) {
            otRepuestosCierre.splice(idx, 1);
            renderTablaRepuestosCierre();
        }

        document.getElementById('formCierreOT').addEventListener('submit', function(e) {
            e.preventDefault();
            const otId = document.getElementById('cierreOtId').value;
            const ot = db.ots.find(o => o.id === otId);
            if (!ot) return;

            ot.fechaInicio = document.getElementById('cierreFechaInicio').value;
            ot.fechaFin = document.getElementById('cierreFechaFin').value;
            ot.actividades = document.getElementById('cierreTrabajo').value.trim();
            ot.tiempoIntervencion = parseFloat(document.getElementById('cierreTiempoIntervencion').value) || 0.0;
            ot.tiempoParada = parseFloat(document.getElementById('cierreTiempoParada').value) || 0.0;
            ot.fotoAntes = document.getElementById('cierreFotoAntesBase64').value;
            ot.fotoDespues = document.getElementById('cierreFotoDespuesBase64').value;
            ot.status = document.getElementById('cierreEstadoFinal').value;
            ot.tecnicoAcompanante = (document.getElementById('cierreTecnicoAcompanante') ? document.getElementById('cierreTecnicoAcompanante').value : '') || '';
            ot.repuestosUsados = otRepuestosCierre;

            // Descontar inventario de repuestos si la orden concluye
            if (ot.status === 'Concluida') {
                otRepuestosCierre.forEach(item => {
                    if (item.id) {
                        const rep = db.repuestos.find(r => r.id === item.id);
                        if (rep) {
                            rep.stock = Math.max(0, rep.stock - item.cant);
                            // Notificar stock mínimo si aplica
                            if (rep.stock <= rep.stockMin) {
                                dispararNotificacion('Gerente', null, 'Alerta de Stock Mínimo', `El repuesto ${rep.name} llegó a su stock mínimo (${rep.stock} ${rep.um})`, 'warning', 'almacen', rep.id);
                            }
                        }
                    }
                });

                // Notificar al Jefe de Mantenimiento sobre cierre
                dispararNotificacion('Gerente', null, 'OT Concluida', `La orden ${ot.id} fue cerrada por ${currentUser.name}. Downtime: ${ot.tiempoParada}h`, 'success', 'ot', ot.id);
            }

            saveDatabase();
            closeModal('modalCierreOT');
            navigate(currentActiveView);
            mostrarToast('Bitácora Registrada', `La orden ${ot.id} ha sido actualizada con éxito.`, 'success');
        });

        // Formularios menores (Proveedores, Repuestos, Compras, Equipos, Usuarios, SolicitudInter)
        function openModalSolicitudInter() {
            document.getElementById('formSolicitudInter').reset();
            document.getElementById('modalSolicitudInter').classList.remove('hidden');
        }

        document.getElementById('formSolicitudInter').addEventListener('submit', function(e) {
            e.preventDefault();
            const payload = {
                id: `SOL-2026-${String(db.solicitudesInterdepartamentales.length + 1).padStart(3, '0')}`,
                tipo: document.getElementById('solTipo').value,
                urgencia: document.getElementById('solUrgencia').value,
                area: document.getElementById('solArea').value.trim(),
                ubicacion: document.getElementById('solUbicacion').value.trim(),
                descripcion: document.getElementById('solDescripcion').value.trim(),
                solicitante: currentUser.name,
                fechaHora: new Date().toISOString().replace('T', ' ').slice(0, 16),
                status: 'Aprobada',
                otVinculada: null
            };

            db.solicitudesInterdepartamentales.unshift(payload);
            // Notificar al Jefe de Mantenimiento
            dispararNotificacion('Gerente', null, 'Nueva Solicitud Interdepartamental', `${currentUser.name} reportó falla en ${payload.area}: ${payload.descripcion.slice(0, 40)}`, 'warning', 'solicitud', payload.id);

            saveDatabase();
            closeModal('modalSolicitudInter');
            navigate(currentUser.role === 'Solicitante' ? 'mis-solicitudes' : 'solicitudes-gerente');
            mostrarToast('Solicitud Emitida', 'Su requerimiento fue enviado al departamento de mantenimiento.', 'success');
        });

        function openModalProveedor(prvId = false) {
            document.getElementById('formProveedor').reset();
            document.getElementById('prvEditId').value = prvId || '';
            if (prvId) {
                const p = db.proveedores.find(x => x.id === prvId);
                if (p) {
                    document.getElementById('prvRif').value = p.rif;
                    document.getElementById('prvNombre').value = p.nombre;
                    document.getElementById('prvCategoria').value = p.categoria;
                    document.getElementById('prvContacto').value = p.contacto || '';
                    document.getElementById('prvTelefono').value = p.telefono || '';
                    document.getElementById('prvEmail').value = p.email || '';
                }
            }
            document.getElementById('modalProveedor').classList.remove('hidden');
        }

        document.getElementById('formProveedor').addEventListener('submit', function(e) {
            e.preventDefault();
            const editId = document.getElementById('prvEditId').value;
            const payload = {
                id: editId || `PRV-${String(db.proveedores.length + 1).padStart(2, '0')}`,
                rif: document.getElementById('prvRif').value.trim(),
                nombre: document.getElementById('prvNombre').value.trim(),
                categoria: document.getElementById('prvCategoria').value,
                contacto: document.getElementById('prvContacto').value.trim(),
                telefono: document.getElementById('prvTelefono').value.trim(),
                email: document.getElementById('prvEmail').value.trim()
            };
            if (editId) {
                const idx = db.proveedores.findIndex(x => x.id === editId);
                if (idx !== -1) db.proveedores[idx] = payload;
            } else {
                db.proveedores.push(payload);
            }
            saveDatabase();
            closeModal('modalProveedor');
            renderProveedoresView(document.getElementById('mainView'));
        });

        function eliminarProveedor(id) {
            if (!confirm("¿Eliminar este proveedor?")) return;
            db.proveedores = db.proveedores.filter(p => p.id !== id);
            saveDatabase();
            renderProveedoresView(document.getElementById('mainView'));
        }

        function openModalRepuesto(repId = false) {
            document.getElementById('formRepuesto').reset();
            document.getElementById('repEditId').value = repId || '';
            const pSel = document.getElementById('repProveedor');
            pSel.innerHTML = db.proveedores.map(p => `<option value="${p.id}">${p.nombre}</option>`).join('');

            if (repId) {
                const r = db.repuestos.find(x => x.id === repId);
                if (r) {
                    document.getElementById('repCodigo').value = r.codigo;
                    document.getElementById('repName').value = r.name;
                    document.getElementById('repStock').value = r.stock;
                    document.getElementById('repStockMin').value = r.stockMin;
                    document.getElementById('repUm').value = r.um;
                    document.getElementById('repCosto').value = r.costo;
                    pSel.value = r.proveedorId || '';
                }
            }
            document.getElementById('modalRepuesto').classList.remove('hidden');
        }

        document.getElementById('formRepuesto').addEventListener('submit', function(e) {
            e.preventDefault();
            const editId = document.getElementById('repEditId').value;
            const payload = {
                id: editId || `REP-${String(db.repuestos.length + 1).padStart(2, '0')}`,
                codigo: document.getElementById('repCodigo').value.trim(),
                name: document.getElementById('repName').value.trim(),
                stock: parseInt(document.getElementById('repStock').value) || 0,
                stockMin: parseInt(document.getElementById('repStockMin').value) || 2,
                um: document.getElementById('repUm').value,
                costo: parseFloat(document.getElementById('repCosto').value) || 0.0,
                proveedorId: document.getElementById('repProveedor').value
            };
            if (editId) {
                const idx = db.repuestos.findIndex(x => x.id === editId);
                if (idx !== -1) db.repuestos[idx] = payload;
            } else {
                db.repuestos.push(payload);
            }
            saveDatabase();
            closeModal('modalRepuesto');
            renderAlmacenView(document.getElementById('mainView'));
        });

        function eliminarRepuesto(id) {
            if (!confirm("¿Eliminar este repuesto del almacén?")) return;
            db.repuestos = db.repuestos.filter(r => r.id !== id);
            saveDatabase();
            renderAlmacenView(document.getElementById('mainView'));
        }

        function openModalCompra(comId = false) {
            document.getElementById('formCompraMaterial').reset();
            const pSel = document.getElementById('compraProveedor');
            pSel.innerHTML = (db.proveedores || []).map(p => `<option value="${p.id}">${p.nombre}</option>`).join('');
            document.getElementById('compraEditId').value = comId || '';
            const titleEl = document.getElementById('modalCompraTitle');

            if (comId) {
                const comp = db.comprasMateriales.find(c => c.id === comId);
                if (comp) {
                    if (titleEl) titleEl.innerHTML = `<i class="fas fa-edit text-blue-600 mr-2"></i> Modificar Solicitud de Compra (${comp.id})`;
                    document.getElementById('compraDescripcion').value = comp.descripcion || '';
                    document.getElementById('compraCantSol').value = comp.cantSolicitada || 1;
                    document.getElementById('compraCantRec').value = comp.cantRecibida || 0;
                    document.getElementById('compraPrecio').value = (comp.precio !== undefined) ? comp.precio : 0.0;
                    if (comp.proveedorId) pSel.value = comp.proveedorId;
                    document.getElementById('compraObs').value = comp.observaciones || '';
                }
            } else {
                if (titleEl) titleEl.innerHTML = `<i class="fas fa-shopping-cart text-blue-600 mr-2"></i> Nueva Solicitud de Compra de Material`;
            }
            document.getElementById('modalCompraMaterial').classList.remove('hidden');
        }

        document.getElementById('formCompraMaterial').addEventListener('submit', function(e) {
            e.preventDefault();
            const editId = document.getElementById('compraEditId').value;
            const existing = editId ? (db.comprasMateriales.find(c => c.id === editId) || {}) : {};

            const payload = {
                id: editId || `COM-${String(db.comprasMateriales.length + 1).padStart(2, '0')}`,
                fecha: editId ? (existing.fecha || new Date().toISOString().slice(0, 10)) : new Date().toISOString().slice(0, 10),
                descripcion: document.getElementById('compraDescripcion').value.trim(),
                cantSolicitada: parseInt(document.getElementById('compraCantSol').value) || 1,
                cantRecibida: parseInt(document.getElementById('compraCantRec').value) || 0,
                moneda: '$',
                precio: parseFloat(document.getElementById('compraPrecio').value) || 0.0,
                proveedorId: document.getElementById('compraProveedor').value,
                observaciones: document.getElementById('compraObs').value.trim()
            };

            if (editId) {
                const idx = db.comprasMateriales.findIndex(c => c.id === editId);
                if (idx !== -1) {
                    db.comprasMateriales[idx] = { ...db.comprasMateriales[idx], ...payload };
                }
            } else {
                db.comprasMateriales.unshift(payload);
            }

            saveDatabase();

            // Sincronización inmediata con backend API
            if (navigator.onLine) {
                fetch('/api/purchases', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }).catch(err => console.warn('Sync purchase error:', err));
            }

            closeModal('modalCompraMaterial');
            renderComprasView(document.getElementById('mainView'));
            mostrarToast(editId ? 'Solicitud Modificada' : 'Solicitud Creada', `La solicitud de compra ${payload.id} ha sido ${editId ? 'actualizada' : 'registrada'} con éxito.`, 'success');
        });

        function eliminarCompra(id) {
            if (!confirm(`¿Está seguro de eliminar la solicitud de compra ${id}?`)) return;
            db.comprasMateriales = db.comprasMateriales.filter(c => c.id !== id);
            saveDatabase();
            if (navigator.onLine) {
                fetch(`/api/purchases/${id}`, { method: 'DELETE' }).catch(e => console.warn(e));
            }
            renderComprasView(document.getElementById('mainView'));
            mostrarToast('Compra Eliminada', `Solicitud ${id} eliminada correctamente.`, 'info');
        }

        function openModalEquipo(eqId = false) {
            document.getElementById('formEquipo').reset();
            if (eqId) {
                const eq = db.equipos.find(x => x.id === eqId);
                if (eq) {
                    document.getElementById('eqTag').value = eq.id;
                    document.getElementById('eqTag').readOnly = true;
                    document.getElementById('eqNombre').value = eq.name;
                    document.getElementById('eqPlanta').value = eq.planta;
                    document.getElementById('eqLinea').value = eq.linea;
                    document.getElementById('eqCriticidad').value = eq.criticidad;
                    document.getElementById('eqEsRefrigeracion').checked = !!eq.es_refrigeracion;
                    document.getElementById('eqTipoRefrigerante').value = eq.tipo_refrigerante || '';
                }
            } else {
                document.getElementById('eqTag').readOnly = false;
            }
            document.getElementById('modalEquipo').classList.remove('hidden');
        }

        document.getElementById('formEquipo').addEventListener('submit', function(e) {
            e.preventDefault();
            const tag = document.getElementById('eqTag').value.trim().toUpperCase();
            const payload = {
                id: tag,
                name: document.getElementById('eqNombre').value.trim(),
                planta: document.getElementById('eqPlanta').value.trim(),
                linea: document.getElementById('eqLinea').value.trim(),
                criticidad: document.getElementById('eqCriticidad').value,
                status: 'Operativo',
                es_refrigeracion: document.getElementById('eqEsRefrigeracion').checked,
                tipo_refrigerante: document.getElementById('eqTipoRefrigerante').value.trim()
            };
            const idx = db.equipos.findIndex(x => x.id === tag);
            if (idx !== -1) db.equipos[idx] = { ...db.equipos[idx], ...payload };
            else db.equipos.push(payload);

            saveDatabase();
            closeModal('modalEquipo');
            renderEquiposView(document.getElementById('mainView'));
        });

        function eliminarEquipo(id) {
            if (!confirm(`¿Eliminar el equipo ${id}?`)) return;
            db.equipos = db.equipos.filter(e => e.id !== id);
            saveDatabase();
            renderEquiposView(document.getElementById('mainView'));
        }

        function openModalUsuario(uId = false) {
            document.getElementById('formUsuario').reset();
            document.getElementById('usrEditId').value = uId || '';
            if (uId) {
                const u = db.users.find(x => x.id === uId);
                if (u) {
                    document.getElementById('usrUsername').value = u.username;
                    document.getElementById('usrPassword').value = u.pass;
                    document.getElementById('usrNombreCompleto').value = u.name;
                    document.getElementById('usrRol').value = u.role;
                    document.getElementById('usrDepartamento').value = u.departamento || 'Mantenimiento';
                }
            }
            document.getElementById('modalUsuario').classList.remove('hidden');
        }

        document.getElementById('formUsuario').addEventListener('submit', async function(e) {
            e.preventDefault();
            const editId = document.getElementById('usrEditId').value;
            const payload = {
                id: editId || `u${db.users.length + 1}`,
                username: document.getElementById('usrUsername').value.trim(),
                pass: document.getElementById('usrPassword').value.trim(),
                name: document.getElementById('usrNombreCompleto').value.trim(),
                role: document.getElementById('usrRol').value,
                departamento: document.getElementById('usrDepartamento').value.trim()
            };
            if (editId) {
                const idx = db.users.findIndex(x => x.id === editId);
                if (idx !== -1) db.users[idx] = payload;
            } else {
                db.users.push(payload);
            }
            try {
                if (navigator.onLine) {
                    await fetch('/api/users', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                }
            } catch (err) {
                console.error("Error al persistir usuario en backend:", err);
            }
            saveDatabase();
            closeModal('modalUsuario');
            renderUsuariosView(document.getElementById('mainView'));
        });

        async function eliminarUsuario(id) {
            if (id === 'u1') { alert("No se puede eliminar el usuario administrador principal."); return; }
            if (!confirm("¿Eliminar este usuario?")) return;
            try {
                if (navigator.onLine) {
                    await fetch(`/api/users/${id}`, { method: 'DELETE' });
                }
            } catch (err) {
                console.error("Error al eliminar usuario en backend:", err);
            }
            db.users = db.users.filter(u => u.id !== id);
            saveDatabase();
            renderUsuariosView(document.getElementById('mainView'));
        }

        function openModalQR() {
            document.getElementById('qrServerUrlDisplay').textContent = window.location.origin;
            document.getElementById('modalQRAndroid').classList.remove('hidden');
        }

        function copiarUrlServidor() {
            navigator.clipboard.writeText(window.location.origin).then(() => {
                mostrarToast('Enlace Copiado', 'Dirección de red copiada al portapapeles.', 'success');
            });
        }

        // PWA Installation
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            const btn = document.getElementById('pwaInstallBtn');
            if (btn) btn.classList.remove('hidden');
        });

        function triggerPwaInstall() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        mostrarToast('Instalación', 'Aplicación instalada en su dispositivo.', 'success');
                    }
                    deferredPrompt = null;
                });
            } else {
                alert("Para instalar en Android: abra el menú de Chrome y seleccione 'Agregar a la pantalla principal' o 'Instalar aplicación'.");
            }
        }

        // --- 17. INICIALIZACIÓN GENERAL AL CARGAR PÁGINA ---
        window.addEventListener('DOMContentLoaded', () => {
            loadDatabase();
            iniciarSincronizacionEnTiempoReal();
            // Verificar idioma guardado
            const savedLang = localStorage.getItem('GMAO_LANG') || 'es';
            document.getElementById('langSelector').value = savedLang;
            if (savedLang === 'ar') changeLanguage('ar');

            // Listeners de conectividad
            window.addEventListener('online', () => setServerStatus(true));
            window.addEventListener('offline', () => setServerStatus(false));

            // Recordar credenciales
            const remU = localStorage.getItem('GMAO_REM_USER');
            const remP = localStorage.getItem('GMAO_REM_PASS');
            if (remU && remP) {
                document.getElementById('loginUsername').value = remU;
                document.getElementById('loginPassword').value = remP;
                document.getElementById('rememberUserCheckbox').checked = true;
            }

            // Registrar Service Worker para PWA Offline
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/service-worker.js').catch(err => {
                    console.log('Service Worker registro:', err);
                });
            }
        });
    </script>
</body>
</html>
""")

print("Parte 5 anexada exitosamente.")
# =============================================================================
# ESCRITURA Y DESPLIEGUE FINAL EN ARCHIVOS ESTÁTICOS
# =============================================================================
full_html = "".join(parts)
print(f"Total caracteres generados: {len(full_html)}")

STATIC_INDEX.parent.mkdir(parents=True, exist_ok=True)
with open(STATIC_INDEX, "w", encoding="utf-8") as f:
    f.write(full_html)
print(f"Guardado exitosamente en: {STATIC_INDEX}")

shutil.copyfile(STATIC_INDEX, ROOT_INDEX)
print(f"Copiado exitosamente a raíz: {ROOT_INDEX}")
print("Construcción completada al 100%.")

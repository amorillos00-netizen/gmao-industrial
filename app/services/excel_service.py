"""
Servicio de Generación y Exportación Profesional a Excel (ISO 55000 / GMAO)
Basado en la estructura corporativa de 'MATRIZ CONTROL DE O.T.xlsx'
y 'Cronograma_Anual_Mantenimiento_Preventivo'.
Empresa: SALTYSNACK TUYERO C.A.
"""
import io
import json
import base64
from PIL import Image as PILImage
from openpyxl.drawing.image import Image as ExcelImage
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def hex_to_fill(hex_str: str) -> PatternFill:
    """Retorna un PatternFill a partir de un hex como '1E3A8A'."""
    clean = hex_str.replace("#", "")
    return PatternFill(start_color=clean, end_color=clean, fill_type="solid")

def create_thin_border() -> Border:
    thin = Side(border_style="thin", color="CBD5E1")
    return Border(left=thin, right=thin, top=thin, bottom=thin)

def generate_matriz_control_ot_excel(ots: list, users: list = None, equipos: list = None) -> bytes:
    """
    Genera el archivo Excel corporativo 'MATRIZ CONTROL DE O.T.xlsx' con 2 hojas:
    1. Dashboard: Tarjetas KPI, resumen por estatus con fórmulas y carga por técnico.
    2. Control de Órdenes (OT): Matriz maestra con todas las órdenes de trabajo.
    """
    wb = openpyxl.Workbook()
    # Eliminar hoja por defecto si existe
    ws_dashboard = wb.active
    ws_dashboard.title = "Dashboard"
    ws_ots = wb.create_sheet(title="Control de Órdenes (OT)")

    user_map = {}
    if users:
        for u in users:
            user_map[u.get("id")] = u.get("name") or u.get("nombre_completo") or u.get("username")

    equip_map = {}
    if equipos:
        for e in equipos:
            equip_map[e.get("id")] = f"{e.get('name')} ({e.get('linea', 'General')})"

    border_thin = create_thin_border()
    font_title = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, italic=True, color="475569")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_data = Font(name="Calibri", size=10)

    fill_navy = hex_to_fill("0A6ED1")      # Azul corporativo SAP/Industrial
    fill_dark_navy = hex_to_fill("002A52") # Azul oscuro encabezados
    fill_slate = hex_to_fill("334155")     # Gris pizarra
    fill_card = hex_to_fill("F8FAFC")      # Fondo tarjetas
    fill_zebra = hex_to_fill("F1F5F9")     # Cebra filas

    # =========================================================================
    # HOJA 2: CONTROL DE ÓRDENES (OT) - SE LLENA PRIMERO PARA QUE EL DASHBOARD PUEDA REFERENCIARLA
    # =========================================================================
    ws_ots.views.sheetView[0].showGridLines = True
    
    # Encabezado institucional
    ws_ots.merge_cells("A1:L1")
    ws_ots["A1"] = "SALTYSNACK TUYERO C.A. - CONTROL MAESTRO DE ÓRDENES DE TRABAJO (OT)"
    ws_ots["A1"].font = font_title
    ws_ots["A1"].fill = fill_dark_navy
    ws_ots["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws_ots.row_dimensions[1].height = 30

    ws_ots.merge_cells("A2:L2")
    ws_ots["A2"] = "Departamento de Mantenimiento e Infraestructura | Ing. Carlos Mendoza / Ing. Argenis Morillo"
    ws_ots["A2"].font = font_sub
    ws_ots["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws_ots.row_dimensions[2].height = 18

    # Cabeceras de tabla
    headers_ot = [
        "N° OT", "Fecha Emisión", "Semana", "Línea / Equipo", "Tipo de Mantenimiento",
        "Descripción de la Actividad", "Técnico Responsable", "Estatus", "Prioridad",
        "Repuestos / Insumos", "Tiempo Ejecución (Min)", "Observaciones / Causa Raíz"
    ]
    ws_ots.row_dimensions[4].height = 24
    for col_idx, h in enumerate(headers_ot, 1):
        cell = ws_ots.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_navy
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border_thin

    # Llenado de filas de OTs
    row_num = 5
    for ot in ots:
        fecha_emision = ot.get("fechaProgramada") or ot.get("fecha_programada") or ot.get("fechaAsignacion") or ot.get("fecha_asignacion") or ""
        semana_str = ""
        if fecha_emision and len(fecha_emision) >= 10:
            try:
                dt = datetime.strptime(fecha_emision[:10], "%Y-%m-%d")
                semana_str = f"Semana {dt.isocalendar()[1]}"
            except Exception:
                semana_str = ""

        # Nombres de técnicos
        tec_ids = ot.get("tecnicoIds") or []
        if isinstance(tec_ids, str):
            try:
                tec_ids = json.loads(tec_ids)
            except Exception:
                tec_ids = [tec_ids]
        tec_names = [user_map.get(tid, tid) for tid in tec_ids if tid]
        tec_str = ", ".join(tec_names) if tec_names else "No Asignado"

        # Nombre de equipo
        eq_id = ot.get("equipoId") or ot.get("equipo_id") or ""
        eq_str = equip_map.get(eq_id, eq_id)

        # Repuestos
        rep_list = ot.get("repuestosUsados") or []
        if isinstance(rep_list, str):
            try:
                rep_list = json.loads(rep_list)
            except Exception:
                rep_list = []
        rep_str = ", ".join([f"{r.get('name')} (x{r.get('cant')})" for r in rep_list]) if rep_list else "Sin Repuestos"

        # Tiempo en minutos
        tiempo_horas = float(ot.get("tiempoIntervencion") or ot.get("tiempo_intervencion") or 0.0)
        tiempo_minutos = round(tiempo_horas * 60)

        # Estatus unificado
        estatus = ot.get("status") or "Pendiente"
        if estatus in ("Concluida", "Completada"):
            estatus = "Completada"
        elif estatus == "En Proceso":
            estatus = "En Proceso"
        else:
            estatus = "Pendiente"

        data_row = [
            ot.get("id", ""),
            fecha_emision[:10] if fecha_emision else "",
            semana_str,
            eq_str,
            ot.get("tipo", "Correctivo"),
            ot.get("descripcion", ""),
            tec_str,
            estatus,
            ot.get("prioridad", "Media"),
            rep_str,
            tiempo_minutos,
            ot.get("actividades", "") or "Operativo sin novedad"
        ]

        ws_ots.row_dimensions[row_num].height = 20
        is_zebra = (row_num % 2 == 0)
        for col_idx, val in enumerate(data_row, 1):
            cell = ws_ots.cell(row=row_num, column=col_idx, value=val)
            cell.font = font_data
            cell.border = border_thin
            if is_zebra:
                cell.fill = fill_zebra
            # Alineaciones específicas
            if col_idx in (1, 2, 3, 5, 8, 9):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif col_idx == 11:
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        row_num += 1

    last_ot_row = max(5, row_num - 1)

    # Autoajuste de anchos de columnas
    ot_col_widths = {1: 14, 2: 14, 3: 13, 4: 28, 5: 18, 6: 35, 7: 24, 8: 15, 9: 12, 10: 25, 11: 18, 12: 30}
    for col_idx, w in ot_col_widths.items():
        ws_ots.column_dimensions[get_column_letter(col_idx)].width = w

    # =========================================================================
    # HOJA 1: DASHBOARD GERENCIAL
    # =========================================================================
    ws_dashboard.views.sheetView[0].showGridLines = True

    # Encabezado institucional Dashboard
    ws_dashboard.merge_cells("A1:J1")
    ws_dashboard["A1"] = "SALTYSNACK TUYERO C.A. — PANEL DE CONTROL GERENCIAL DE MANTENIMIENTO"
    ws_dashboard["A1"].font = font_title
    ws_dashboard["A1"].fill = fill_dark_navy
    ws_dashboard["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws_dashboard.row_dimensions[1].height = 32

    ws_dashboard.merge_cells("A2:J2")
    ws_dashboard["A2"] = "Indicadores Clave de Desempeño y Carga Operativa (Ing. Carlos Mendoza / Ing. Argenis Morillo)"
    ws_dashboard["A2"].font = font_sub
    ws_dashboard["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws_dashboard.row_dimensions[2].height = 18

    # Tarjetas KPI (Fila 4 y 5)
    kpis_config = [
        ("A4:B4", "A5:B5", "Total Órdenes", f"=COUNTA('Control de Órdenes (OT)'!A5:A{last_ot_row})"),
        ("D4:E4", "D5:E5", "OT Completadas", f"=COUNTIF('Control de Órdenes (OT)'!H5:H{last_ot_row}, \"Completada\")"),
        ("G4:H4", "G5:H5", "OT En Proceso / Pendientes", f"=COUNTIF('Control de Órdenes (OT)'!H5:H{last_ot_row}, \"En Proceso\") + COUNTIF('Control de Órdenes (OT)'!H5:H{last_ot_row}, \"Pendiente\")"),
        ("J4:K4", "J5:K5", "Horas de Mantenimiento", f"=ROUND(SUM('Control de Órdenes (OT)'!K5:K{last_ot_row})/60, 2)")
    ]

    for title_range, val_range, title, formula in kpis_config:
        ws_dashboard.merge_cells(title_range)
        ws_dashboard.merge_cells(val_range)
        t_cell = ws_dashboard[title_range.split(":")[0]]
        t_cell.value = title
        t_cell.font = font_header
        t_cell.fill = fill_navy
        t_cell.alignment = Alignment(horizontal="center", vertical="center")
        
        v_cell = ws_dashboard[val_range.split(":")[0]]
        v_cell.value = formula
        v_cell.font = Font(name="Calibri", size=18, bold=True, color="0A6ED1")
        v_cell.fill = fill_card
        v_cell.alignment = Alignment(horizontal="center", vertical="center")
        
        for r in ws_dashboard[title_range]:
            for c in r: c.border = border_thin
        for r in ws_dashboard[val_range]:
            for c in r: c.border = border_thin

    ws_dashboard.row_dimensions[4].height = 20
    ws_dashboard.row_dimensions[5].height = 36

    # TABLA 1: RESUMEN DE ÓRDENES POR ESTATUS (Fila 9)
    ws_dashboard.merge_cells("A9:C9")
    ws_dashboard["A9"] = "RESUMEN DE ÓRDENES POR ESTATUS"
    ws_dashboard["A9"].font = font_header
    ws_dashboard["A9"].fill = fill_slate
    ws_dashboard["A9"].alignment = Alignment(horizontal="center", vertical="center")

    headers_estatus = ["Estatus", "Cantidad de OT", "% del Total"]
    for col_idx, h in enumerate(headers_estatus, 1):
        cell = ws_dashboard.cell(row=10, column=col_idx, value=h)
        cell.font = font_bold
        cell.fill = fill_zebra
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_thin

    status_rows = [
        (11, "Completada", f'=COUNTIF(\'Control de Órdenes (OT)\'!H$5:H${last_ot_row}, "Completada")'),
        (12, "En Proceso", f'=COUNTIF(\'Control de Órdenes (OT)\'!H$5:H${last_ot_row}, "En Proceso")'),
        (13, "Pendiente", f'=COUNTIF(\'Control de Órdenes (OT)\'!H$5:H${last_ot_row}, "Pendiente")')
    ]

    for r_idx, s_name, s_formula in status_rows:
        c1 = ws_dashboard.cell(row=r_idx, column=1, value=s_name)
        c2 = ws_dashboard.cell(row=r_idx, column=2, value=s_formula)
        c3 = ws_dashboard.cell(row=r_idx, column=3, value=f'=IF(B$14>0, B{r_idx}/B$14, 0)')
        c1.font = font_data; c1.border = border_thin
        c2.font = font_data; c2.border = border_thin; c2.alignment = Alignment(horizontal="center")
        c3.font = font_data; c3.border = border_thin; c3.number_format = "0.0%"; c3.alignment = Alignment(horizontal="center")

    # Fila Total General Estatus
    ws_dashboard.cell(row=14, column=1, value="Total General").font = font_bold
    ws_dashboard.cell(row=14, column=2, value="=SUM(B11:B13)").font = font_bold
    ws_dashboard.cell(row=14, column=3, value="=SUM(C11:C13)").font = font_bold
    ws_dashboard.cell(row=14, column=3).number_format = "0.0%"
    for c in range(1, 4):
        ws_dashboard.cell(row=14, column=c).border = border_thin
        ws_dashboard.cell(row=14, column=c).fill = fill_zebra
        if c > 1: ws_dashboard.cell(row=14, column=c).alignment = Alignment(horizontal="center")

    # TABLA 2: CARGA DE TRABAJO POR TÉCNICO (Fila 9, Columna E:G)
    ws_dashboard.merge_cells("E9:G9")
    ws_dashboard["E9"] = "CARGA DE TRABAJO POR TÉCNICO"
    ws_dashboard["E9"].font = font_header
    ws_dashboard["E9"].fill = fill_slate
    ws_dashboard["E9"].alignment = Alignment(horizontal="center", vertical="center")

    headers_tec = ["Técnico Responsable", "OT Asignadas", "Tiempo Total (Min)"]
    for i, h in enumerate(headers_tec, 5):
        cell = ws_dashboard.cell(row=10, column=i, value=h)
        cell.font = font_bold
        cell.fill = fill_zebra
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_thin

    tecnicos_list = [u for u in (users or []) if u.get("role") in ("Tecnico", "ROL-TEC") or "tecnico" in u.get("username", "").lower()]
    if not tecnicos_list:
        tecnicos_list = [{"id": "u2", "name": "Juan Pérez (Electromecánico)"}, {"id": "u3", "name": "Miguel Torres (Instrumentista)"}]

    t_row = 11
    for tec in tecnicos_list:
        t_name = tec.get("name") or tec.get("nombre_completo") or tec.get("username")
        c1 = ws_dashboard.cell(row=t_row, column=5, value=t_name)
        c2 = ws_dashboard.cell(row=t_row, column=6, value=f'=COUNTIF(\'Control de Órdenes (OT)\'!G$5:G${last_ot_row}, "*{t_name}*")')
        c3 = ws_dashboard.cell(row=t_row, column=7, value=f'=SUMIF(\'Control de Órdenes (OT)\'!G$5:G${last_ot_row}, "*{t_name}*", \'Control de Órdenes (OT)\'!K$5:K${last_ot_row})')
        c1.font = font_data; c1.border = border_thin
        c2.font = font_data; c2.border = border_thin; c2.alignment = Alignment(horizontal="center")
        c3.font = font_data; c3.border = border_thin; c3.alignment = Alignment(horizontal="right")
        t_row += 1

    # Fila Total General Técnicos
    ws_dashboard.cell(row=t_row, column=5, value="Total General").font = font_bold
    ws_dashboard.cell(row=t_row, column=6, value=f"=SUM(F11:F{t_row-1})").font = font_bold
    ws_dashboard.cell(row=t_row, column=7, value=f"=SUM(G11:G{t_row-1})").font = font_bold
    for c in range(5, 8):
        ws_dashboard.cell(row=t_row, column=c).border = border_thin
        ws_dashboard.cell(row=t_row, column=c).fill = fill_zebra
        if c == 6: ws_dashboard.cell(row=t_row, column=c).alignment = Alignment(horizontal="center")
        if c == 7: ws_dashboard.cell(row=t_row, column=c).alignment = Alignment(horizontal="right")

    # Ajuste de anchos del Dashboard
    dash_col_widths = {1: 18, 2: 16, 3: 14, 4: 4, 5: 32, 6: 15, 7: 18, 8: 4, 9: 4, 10: 16, 11: 16}
    for col_idx, w in dash_col_widths.items():
        ws_dashboard.column_dimensions[get_column_letter(col_idx)].width = w

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def generate_cronograma_anual_excel(planes: list, equipos: list = None, anio: int = 2026) -> bytes:
    """
    Genera el archivo Excel corporativo 'Cronograma_Anual_Mantenimiento_Preventivo.xlsx'
    con proyección anual dinámica de 12 meses (Enero a Diciembre).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Cronograma Anual {anio}"
    ws.views.sheetView[0].showGridLines = True

    equip_map = {e.get("id"): e for e in (equipos or [])}

    border_thin = create_thin_border()
    font_title = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, italic=True, color="475569")
    font_header = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=9, bold=True)
    font_data = Font(name="Calibri", size=9)

    fill_dark = hex_to_fill("002A52")
    fill_blue = hex_to_fill("0A6ED1")
    fill_zebra = hex_to_fill("F8FAFC")
    fill_prog = hex_to_fill("DBEAFE") # Azul suave celda programada

    # Título principal
    ws.merge_cells("A1:S1")
    ws["A1"] = f"SALTYSNACK TUYERO C.A. - CRONOGRAMA ANUAL DE MANTENIMIENTO PREVENTIVO {anio}"
    ws["A1"].font = font_title
    ws["A1"].fill = fill_dark
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:S2")
    ws["A2"] = "DEPARTAMENTO DE MANTENIMIENTO E INFRAESTRUCTURA | PLAN MAESTRO DE CONFIABILIDAD OPERATIVA"
    ws["A2"].font = font_sub
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 18

    # Cabeceras fijas + 12 meses
    meses_nombres = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    headers = ["CÓDIGO ACTIVO", "EQUIPO / SISTEMA", "UBICACIÓN / LÍNEA", "ACTIVIDAD PREVENTIVA", "FRECUENCIA", "ÚLTIMA EJECUCIÓN", "PRÓXIMA FECHA"] + meses_nombres

    ws.row_dimensions[4].height = 22
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_blue
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border_thin

    # Llenado de cada plan
    row_num = 5
    for p in planes:
        eq_id = p.get("equipoId") or p.get("equipo_id") or ""
        eq_info = equip_map.get(eq_id, {})
        eq_nombre = eq_info.get("name") or eq_info.get("nombre") or eq_id
        eq_ubicacion = f"{eq_info.get('planta', 'Planta Central')} - {eq_info.get('linea', 'General')}"
        
        frecuencia = p.get("frecuencia", "Mensual")
        ultima = p.get("ultimaFecha") or p.get("ultima_fecha") or ""
        proxima = p.get("proximaFecha") or p.get("proxima_fecha") or ""

        # Determinar en qué meses cae la proyección
        meses_activos = set()
        if proxima and len(proxima) >= 7:
            try:
                prox_dt = datetime.strptime(proxima[:10], "%Y-%m-%d")
                mes_prox = prox_dt.month
                # Proyección según frecuencia
                frec_lower = frecuencia.lower()
                step = 1
                if "diario" in frec_lower or "semanal" in frec_lower or "quincenal" in frec_lower or "mensual" in frec_lower:
                    step = 1
                elif "bimestral" in frec_lower:
                    step = 2
                elif "trimestral" in frec_lower:
                    step = 3
                elif "semestral" in frec_lower:
                    step = 6
                elif "anual" in frec_lower:
                    step = 12

                curr_m = mes_prox
                while curr_m <= 12:
                    meses_activos.add(curr_m)
                    curr_m += step
            except Exception:
                pass

        base_data = [
            eq_id,
            eq_nombre,
            eq_ubicacion,
            p.get("nombre", ""),
            frecuencia,
            ultima[:10] if ultima else "",
            proxima[:10] if proxima else ""
        ]

        ws.row_dimensions[row_num].height = 18
        is_zebra = (row_num % 2 == 0)

        # Celdas de datos base
        for col_idx, val in enumerate(base_data, 1):
            cell = ws.cell(row=row_num, column=col_idx, value=val)
            cell.font = font_data
            cell.border = border_thin
            if is_zebra: cell.fill = fill_zebra
            if col_idx in (1, 5, 6, 7):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        # Celdas de meses (Col 8 a 19)
        for m_idx in range(1, 13):
            col_target = 7 + m_idx
            cell = ws.cell(row=row_num, column=col_target)
            cell.border = border_thin
            if m_idx in meses_activos:
                cell.value = "P"
                cell.font = Font(name="Calibri", size=9, bold=True, color="0A6ED1")
                cell.fill = fill_prog
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.value = ""
                if is_zebra: cell.fill = fill_zebra

        row_num += 1

    # Anchos de columnas
    col_widths = {1: 14, 2: 28, 3: 26, 4: 32, 5: 14, 6: 15, 7: 15}
    for m in range(8, 20):
        col_widths[m] = 6
    for col_idx, w in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = w

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()


def generate_informe_periodico_excel(
    ots: list,
    equipos: list = None,
    periodo_tipo: str = "Mensual",
    periodo_valor: str = "2026-10",
    equipo_filtro: str = "TODOS",
    nombre_jefe: str = "Ing. Carlos Mendoza",
    cargo_jefe: str = "Jefe de Mantenimiento",
    nombre_gerente: str = "Ing. Roberto Navarro",
    cargo_gerente: str = "Gerente de Planta",
    mttr_target: float = 2.0
) -> bytes:
    """
    Genera el archivo Excel corporativo del Informe Periódico de Mantenimiento y Confiabilidad
    con formato ejecutivo, tablas estructuradas de Preventivo, Correctivo y firmas dinámicas.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Informe Periódico"

    eq_map = {e.get("id"): e for e in (equipos or [])}

    # Filtrar OTs por Equipo
    ots_eval = ots or []
    if equipo_filtro and equipo_filtro != "TODOS":
        ots_eval = [o for o in ots_eval if o.get("equipoId") == equipo_filtro or o.get("equipo_id") == equipo_filtro]

    # Texto legible de periodo
    meses_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    periodo_texto = periodo_valor
    if periodo_tipo == "Mensual" and "-" in periodo_valor:
        parts = periodo_valor.split("-")
        y, m = parts[0], parts[1]
        m_idx = int(m) - 1
        m_nombre = meses_es[m_idx] if 0 <= m_idx < 12 else m
        periodo_texto = f"{m_nombre} {y}"
        ots_eval = [o for o in ots_eval if (o.get("fechaProgramada") or o.get("fecha_programada") or o.get("fechaAsignacion") or o.get("fecha_asignacion") or "").startswith(periodo_valor)]
    elif periodo_tipo == "Anual":
        periodo_texto = f"Año {periodo_valor}"
        ots_eval = [o for o in ots_eval if (o.get("fechaProgramada") or o.get("fecha_programada") or o.get("fechaAsignacion") or o.get("fecha_asignacion") or "").startswith(str(periodo_valor))]
    elif periodo_tipo == "Rango" or "_al_" in str(periodo_valor):
        parts = str(periodo_valor).split("_al_") if "_al_" in str(periodo_valor) else [str(periodo_valor), ""]
        f_ini = parts[0]
        f_fin = parts[1] if len(parts) > 1 else ""
        periodo_texto = f"{f_ini} al {f_fin}" if f_fin else f_ini
        if f_ini and f_fin:
            ots_eval = [o for o in ots_eval if f_ini <= (o.get("fechaProgramada") or o.get("fecha_programada") or o.get("fechaAsignacion") or o.get("fecha_asignacion") or "")[:10] <= f_fin]
        elif f_ini:
            ots_eval = [o for o in ots_eval if (o.get("fechaProgramada") or o.get("fecha_programada") or o.get("fechaAsignacion") or o.get("fecha_asignacion") or "")[:10] >= f_ini]

    concluidas = [o for o in ots_eval if o.get("status") in ("Concluida", "Completada")]
    preventivas = [o for o in concluidas if o.get("tipo") == "Preventivo"]
    correctivas = [o for o in concluidas if o.get("tipo") == "Correctivo"]
    otras = [o for o in concluidas if o.get("tipo") not in ("Preventivo", "Correctivo")]

    # Métricas
    horas_base = 8760.0 if periodo_tipo == "Anual" else 720.0
    total_downtime = sum(float(o.get("tiempoParada") or o.get("tiempo_parada") or 0.0) for o in ots_eval)
    horas_operadas = max(0.0, horas_base - total_downtime)
    disponibilidad_pct = min(100.0, round((horas_operadas / horas_base) * 1000) / 10)
    num_fallas = len(correctivas)
    mttr = round((sum(float(c.get("tiempoIntervencion") or c.get("tiempo_intervencion") or 0.0) for c in correctivas) / num_fallas) * 10) / 10 if num_fallas > 0 else 0.0

    # Estilos
    font_title = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, bold=True, color="E2E8F0")
    font_sec = Font(name="Calibri", size=11, bold=True, color="0F172A")
    font_tbl_hdr = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
    font_data = Font(name="Calibri", size=9, color="1E293B")
    font_bold = Font(name="Calibri", size=9, bold=True, color="1E293B")
    font_italic = Font(name="Calibri", size=9, italic=True, color="64748B")

    fill_navy = hex_to_fill("1E3A8A")
    fill_hdr = hex_to_fill("0F172A")
    fill_zebra = hex_to_fill("F8FAFC")
    fill_kpi_card = hex_to_fill("EFF6FF")
    fill_kpi_border = hex_to_fill("DBEAFE")
    border_thin = create_thin_border()

    # 1. ENCABEZADO CORPORATIVO
    ws.merge_cells("A1:G1")
    c1 = ws["A1"]
    c1.value = "SALTYSNACK TUYERO C.A. - DEPARTAMENTO DE MANTENIMIENTO E INFRAESTRUCTURA"
    c1.font = font_title
    c1.fill = fill_navy
    c1.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    ws.merge_cells("A2:G2")
    c2 = ws["A2"]
    c2.value = f"INFORME DE GESTIÓN Y CONFIABILIDAD | Periodo: {periodo_texto.upper()} | Alcance: {equipo_filtro}"
    c2.font = font_sub
    c2.fill = hex_to_fill("1E293B")
    c2.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 22

    # Metadata bar
    ws["A3"].value = f"Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws["A3"].font = font_italic
    ws["G3"].value = f"DOC-INF-{datetime.now().year}"
    ws["G3"].font = Font(name="Calibri", size=9, bold=True, color="475569")
    ws["G3"].alignment = Alignment(horizontal="right")

    # 2. RESUMEN EJECUTIVO Y TARJETAS KPI
    ws["A5"].value = "1. RESUMEN EJECUTIVO Y MÉTRICAS DE CONFIABILIDAD (SMRP / ISO 55000)"
    ws["A5"].font = font_sec

    # Tarjetas KPI (Fila 6 a 7)
    kpi_cols = [
        ("Disponibilidad Operativa", f"{disponibilidad_pct}%", "B", "C"),
        ("MTTR (Tiempo Medio Reparación)", f"{mttr} h (Meta: {mttr_target}h)", "D", "E"),
        ("OTs Culminadas en Periodo", str(len(concluidas)), "F", "F"),
        ("Horas Parada (Downtime)", f"{total_downtime:.1f} h", "G", "G")
    ]
    # Dibujar tarjetas
    card_labels = ["Disponibilidad Operativa", f"MTTR (Meta: {mttr_target}h)", "OTs Culminadas", "Horas Parada Total"]
    card_vals = [f"{disponibilidad_pct}%", f"{mttr} h", str(len(concluidas)), f"{total_downtime:.1f} h"]
    cols_pos = ["A", "C", "E", "G"]
    
    # Asignar en columnas
    ws["A6"].value = "Disponibilidad:"
    ws["A6"].font = Font(name="Calibri", size=9, bold=True, color="475569")
    ws["B6"].value = f"{disponibilidad_pct}%"
    ws["B6"].font = Font(name="Calibri", size=11, bold=True, color="0A6ED1")

    ws["C6"].value = f"MTTR (Meta {mttr_target}h):"
    ws["C6"].font = Font(name="Calibri", size=9, bold=True, color="475569")
    ws["D6"].value = f"{mttr} h"
    ws["D6"].font = Font(name="Calibri", size=11, bold=True, color="059669")

    ws["E6"].value = "OTs Culminadas:"
    ws["E6"].font = Font(name="Calibri", size=9, bold=True, color="475569")
    ws["E6"].alignment = Alignment(horizontal="right")
    ws["F6"].value = len(concluidas)
    ws["F6"].font = Font(name="Calibri", size=11, bold=True, color="1E293B")

    ws["F6"].alignment = Alignment(horizontal="center")
    ws["G6"].value = f"Downtime: {total_downtime:.1f} h"
    ws["G6"].font = Font(name="Calibri", size=9, bold=True, color="7C3AED")
    ws["G6"].alignment = Alignment(horizontal="right")

    # 3. MANTENIMIENTO PREVENTIVO
    row = 9
    ws.cell(row=row, column=1, value=f"2.1 Mantenimiento Preventivo ({len(preventivas)} Rutinas Culminadas)").font = font_sec
    row += 1

    headers_prev = ["Nº", "Fecha Emisión", "Frecuencia", "Máquina / Equipo", "Código Tag", "Actividades Ejecutadas", "Observaciones"]
    for c_i, h in enumerate(headers_prev, 1):
        cell = ws.cell(row=row, column=c_i, value=h)
        cell.font = font_tbl_hdr
        cell.fill = fill_hdr
        cell.alignment = Alignment(horizontal="center" if c_i in (1, 2, 3, 5) else "left", vertical="center")
        cell.border = border_thin
    ws.row_dimensions[row].height = 20
    row += 1

    if preventivas:
        for idx, ot in enumerate(preventivas, 1):
            eq_id = ot.get("equipoId") or ot.get("equipo_id", "")
            eq_info = eq_map.get(eq_id, {})
            eq_name = eq_info.get("name") or eq_info.get("nombre") or eq_id
            f_prog = ot.get("fechaProgramada") or ot.get("fecha_programada") or ot.get("fechaAsignacion") or "-"
            act = ot.get("actividades") or ot.get("descripcion") or "-"

            vals = [idx, f_prog, "Programado", eq_name, eq_id, act, "Culminado Conforme"]
            for c_i, v in enumerate(vals, 1):
                cell = ws.cell(row=row, column=c_i, value=v)
                cell.font = font_data
                cell.border = border_thin
                cell.alignment = Alignment(horizontal="center" if c_i in (1, 2, 3, 5) else "left", vertical="center")
                if idx % 2 == 0: cell.fill = fill_zebra
            row += 1
    else:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
        c = ws.cell(row=row, column=1, value="No se registraron mantenimientos preventivos culminados en este periodo.")
        c.font = font_italic
        c.alignment = Alignment(horizontal="center", vertical="center")
        for col_idx in range(1, 8): ws.cell(row=row, column=col_idx).border = border_thin
        row += 1

    # 4. MANTENIMIENTO CORRECTIVO
    row += 1
    ws.cell(row=row, column=1, value=f"2.2 Mantenimiento Correctivo ({len(correctivas)} Fallas Atendidas)").font = font_sec
    row += 1

    headers_corr = ["Nº", "Fecha", "Máquina / Instalación", "Código Tag", "Falla o Requerimiento", "Descripción de Mantenimiento", "Materiales y Observación"]
    for c_i, h in enumerate(headers_corr, 1):
        cell = ws.cell(row=row, column=c_i, value=h)
        cell.font = font_tbl_hdr
        cell.fill = fill_hdr
        cell.alignment = Alignment(horizontal="center" if c_i in (1, 2, 4) else "left", vertical="center")
        cell.border = border_thin
    ws.row_dimensions[row].height = 20
    row += 1

    if correctivas:
        for idx, ot in enumerate(correctivas, 1):
            eq_id = ot.get("equipoId") or ot.get("equipo_id", "")
            eq_info = eq_map.get(eq_id, {})
            eq_name = eq_info.get("name") or eq_info.get("nombre") or eq_id
            f_act = ot.get("fechaFin") or ot.get("fecha_fin") or ot.get("fechaProgramada") or ot.get("fechaAsignacion") or "-"
            falla = ot.get("descripcion") or "-"
            desc_m = ot.get("actividades") or "Corrección de falla y prueba operativa"
            reps = ot.get("repuestosUsados") or ot.get("repuestos_usados") or []
            rep_text = ", ".join(f"{r.get('name') or r.get('nombre')} (x{r.get('cant', 1)})" for r in reps) if reps else "Ninguno"
            t_int = ot.get("tiempoIntervencion") or ot.get("tiempo_intervencion") or 0.0

            vals = [idx, f_act, eq_name, eq_id, falla, desc_m, f"{rep_text} | Culminado ({t_int}h)"]
            for c_i, v in enumerate(vals, 1):
                cell = ws.cell(row=row, column=c_i, value=v)
                cell.font = font_data
                cell.border = border_thin
                cell.alignment = Alignment(horizontal="center" if c_i in (1, 2, 4) else "left", vertical="center")
                if idx % 2 == 0: cell.fill = fill_zebra
            row += 1
    else:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
        c = ws.cell(row=row, column=1, value="No se registraron fallas o mantenimientos correctivos en este periodo.")
        c.font = font_italic
        c.alignment = Alignment(horizontal="center", vertical="center")
        for col_idx in range(1, 8): ws.cell(row=row, column=col_idx).border = border_thin
        row += 1

    # 5. OTRAS ACTIVIDADES (si existen)
    if otras:
        row += 1
        ws.cell(row=row, column=1, value=f"3. Otras Actividades Especiales y Mejoras ({len(otras)} Realizadas)").font = font_sec
        row += 1

        headers_otras = ["Nº", "Fecha", "Descripción de la Actividad", "Materiales Utilizados", "Observaciones", "", ""]
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=4)
        ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=7)
        ws.cell(row=row, column=1, value="Nº").font = font_tbl_hdr
        ws.cell(row=row, column=1).fill = fill_hdr
        ws.cell(row=row, column=1).border = border_thin
        ws.cell(row=row, column=2, value="Fecha").font = font_tbl_hdr
        ws.cell(row=row, column=2).fill = fill_hdr
        ws.cell(row=row, column=2).border = border_thin
        ws.cell(row=row, column=3, value="Descripción de la Actividad").font = font_tbl_hdr
        ws.cell(row=row, column=3).fill = fill_hdr
        ws.cell(row=row, column=3).border = border_thin
        ws.cell(row=row, column=5, value="Materiales y Observación").font = font_tbl_hdr
        ws.cell(row=row, column=5).fill = fill_hdr
        ws.cell(row=row, column=5).border = border_thin
        row += 1

        for idx, ot in enumerate(otras, 1):
            f_act = ot.get("fechaFin") or ot.get("fecha_fin") or ot.get("fechaProgramada") or ot.get("fechaAsignacion") or "-"
            act = ot.get("actividades") or ot.get("descripcion") or "-"
            reps = ot.get("repuestosUsados") or ot.get("repuestos_usados") or []
            rep_text = ", ".join(f"{r.get('name') or r.get('nombre')} (x{r.get('cant', 1)})" for r in reps) if reps else "Insumos menores"

            ws.cell(row=row, column=1, value=idx).font = font_data
            ws.cell(row=row, column=1).alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=1).border = border_thin
            ws.cell(row=row, column=2, value=f_act).font = font_data
            ws.cell(row=row, column=2).alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=2).border = border_thin
            ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=4)
            ws.cell(row=row, column=3, value=act).font = font_data
            ws.cell(row=row, column=3).border = border_thin
            ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=7)
            ws.cell(row=row, column=5, value=f"{rep_text} | Finalizada Conforme").font = font_data
            ws.cell(row=row, column=5).border = border_thin
            row += 1

    # 6. FIRMAS AUTORIZADAS DINÁMICAS
    row += 3
    # Línea de firma
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
    ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=6)
    c_line1 = ws.cell(row=row, column=2, value="_________________________________________")
    c_line1.alignment = Alignment(horizontal="center")
    c_line2 = ws.cell(row=row, column=5, value="_________________________________________")
    c_line2.alignment = Alignment(horizontal="center")
    row += 1

    # Nombres
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
    ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=6)
    c_n1 = ws.cell(row=row, column=2, value=nombre_jefe)
    c_n1.font = Font(name="Calibri", size=10, bold=True, color="0F172A")
    c_n1.alignment = Alignment(horizontal="center")
    c_n2 = ws.cell(row=row, column=5, value=nombre_gerente)
    c_n2.font = Font(name="Calibri", size=10, bold=True, color="0F172A")
    c_n2.alignment = Alignment(horizontal="center")
    row += 1

    # Cargos
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
    ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=6)
    c_c1 = ws.cell(row=row, column=2, value=f"{cargo_jefe} - SALTYSNACK TUYERO C.A.")
    c_c1.font = Font(name="Calibri", size=9, color="475569")
    c_c1.alignment = Alignment(horizontal="center")
    c_c2 = ws.cell(row=row, column=5, value=f"{cargo_gerente} - Aprobación Final y Conforme")
    c_c2.font = Font(name="Calibri", size=9, color="475569")
    c_c2.alignment = Alignment(horizontal="center")

    # Anchos de columnas ajustados
    col_widths = {1: 8, 2: 15, 3: 20, 4: 26, 5: 16, 6: 32, 7: 28}
    for c_idx, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c_idx)].width = w

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()



def generate_informe_ssl_excel(ssl_requests: list, users: list = None, equipos: list = None) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Condiciones Inseguras (SSL)"
    ws.views.sheetView[0].showGridLines = True

    border_thin = create_thin_border()
    font_company = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Calibri", size=10, bold=True, color="E2E8F0")
    font_kpi_lbl = Font(name="Calibri", size=9, bold=True, color="475569")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_data = Font(name="Calibri", size=10)
    font_muted = Font(name="Calibri", size=9, italic=True, color="64748B")

    fill_dark_navy = hex_to_fill("002A52")
    fill_navy = hex_to_fill("0A6ED1")
    fill_kpi_bg = hex_to_fill("F8FAFC")
    fill_zebra = hex_to_fill("F8FAFC")

    equip_map = {}
    if equipos:
        for e in equipos:
            equip_map[e.get("id")] = e.get("name") or e.get("id")

    user_map = {}
    if users:
        for u in users:
            user_map[u.get("id")] = u.get("name") or u.get("nombre_completo") or u.get("username")

    # 1. Cabecera institucional
    ws.merge_cells("A1:N1")
    ws["A1"] = "SALTYSNACK TUYERO C.A. - DEPARTAMENTO DE SEGURIDAD Y SALUD LABORAL (SSL / SIAHO)"
    ws["A1"].font = font_company
    ws["A1"].fill = fill_dark_navy
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:N2")
    ws["A2"] = "INFORME OFICIAL Y MATRIZ DE CONDICIONES INSEGURAS CON EVIDENCIAS FOTOGRAFICAS (LOPCYMAT)"
    ws["A2"].font = font_subtitle
    ws["A2"].fill = fill_navy
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    ws.merge_cells("A3:N3")
    ws["A3"] = f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Sistema GMAO Industrial Pro v3.3"
    ws["A3"].font = font_muted
    ws["A3"].alignment = Alignment(horizontal="right", vertical="center")
    ws.row_dimensions[3].height = 18

    # 2. Resumen ejecutivo de KPIs
    total_reg = len(ssl_requests)
    criticas_altas = sum(1 for s in ssl_requests if s.get("nivelRiesgo") in ("Crítico", "Alto", "Critico"))
    en_correccion = sum(1 for s in ssl_requests if s.get("status") == "En Corrección")
    corregidas = sum(1 for s in ssl_requests if s.get("status") == "Corregida")
    desestimadas = sum(1 for s in ssl_requests if s.get("status") == "Desestimada")

    kpis = [
        ("A5:B5", "A6:B6", "TOTAL REPORTES", total_reg, "0A6ED1"),
        ("D5:E5", "D6:E6", "RIESGO CRÍTICO / ALTO", criticas_altas, "DC2626"),
        ("G5:H5", "G6:H6", "EN CORRECCIÓN", en_correccion, "D97706"),
        ("J5:K5", "J6:K6", "CORREGIDAS / MITIGADAS", corregidas, "059669"),
        ("M5:N5", "M6:N6", "DESESTIMADAS", desestimadas, "64748B")
    ]

    for lbl_rng, val_rng, lbl, val, color_hex in kpis:
        ws.merge_cells(lbl_rng)
        cell_lbl = ws[lbl_rng.split(":")[0]]
        cell_lbl.value = lbl
        cell_lbl.font = font_kpi_lbl
        cell_lbl.fill = fill_kpi_bg
        cell_lbl.alignment = Alignment(horizontal="center", vertical="center")
        cell_lbl.border = border_thin

        ws.merge_cells(val_rng)
        cell_val = ws[val_rng.split(":")[0]]
        cell_val.value = val
        cell_val.font = Font(name="Calibri", size=16, bold=True, color=color_hex)
        cell_val.fill = fill_kpi_bg
        cell_val.alignment = Alignment(horizontal="center", vertical="center")
        cell_val.border = border_thin

    ws.row_dimensions[5].height = 18
    ws.row_dimensions[6].height = 24

    # 3. Encabezados de tabla
    headers = [
        ("N°", 6),
        ("Código", 13),
        ("Folio", 14),
        ("Fecha / Hora", 16),
        ("Nivel Riesgo", 14),
        ("Área de Planta", 20),
        ("Ubicación Técnica", 22),
        ("Equipo / Activo", 24),
        ("Reportado Por", 22),
        ("Descripción del Riesgo", 36),
        ("Acción Propuesta", 32),
        ("Estado Actual", 16),
        ("OT Vinculada", 14),
        ("Evidencia Fotográfica", 24)
    ]

    start_row = 8
    ws.row_dimensions[start_row].height = 25
    for col_idx, (h_text, width) in enumerate(headers, start=1):
        c = ws.cell(row=start_row, column=col_idx, value=h_text)
        c.font = font_header
        c.fill = fill_dark_navy
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border_thin
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    current_row = start_row + 1

    for idx, s in enumerate(ssl_requests, start=1):
        codigo = s.get("codigo") or f"COND-{idx:03d}"
        folio = s.get("id", "")
        fecha = s.get("fechaHora", "")
        riesgo = s.get("nivelRiesgo", "Medio")
        area = s.get("area", "")
        ubicacion = s.get("ubicacion", "")
        eq_id = s.get("equipoId", "")
        eq_nombre = equip_map.get(eq_id, eq_id) if eq_id else "Área General"
        solic_nombre = s.get("solicitanteNombre") or user_map.get(s.get("solicitanteId"), "Jefe SSL")
        descripcion = s.get("descripcion", "")
        accion = s.get("accionPropuesta", "")
        status = s.get("status", "Pendiente")
        ot = s.get("otVinculada") or "-"
        foto_b64 = s.get("fotoEvidencia", "")

        is_zebra = (idx % 2 == 0)
        row_fill = fill_zebra if is_zebra else PatternFill(fill_type=None)

        riesgo_fill = None
        if riesgo in ("Crítico", "Critico"): riesgo_fill = hex_to_fill("FEE2E2")
        elif riesgo == "Alto": riesgo_fill = hex_to_fill("FFEDD5")
        elif riesgo == "Medio": riesgo_fill = hex_to_fill("FEF3C7")
        elif riesgo == "Bajo": riesgo_fill = hex_to_fill("D1FAE5")

        status_fill = None
        if status == "Corregida": status_fill = hex_to_fill("D1FAE5")
        elif status == "En Corrección": status_fill = hex_to_fill("DBEAFE")
        elif status == "Pendiente": status_fill = hex_to_fill("FEF3C7")
        elif status == "Desestimada": status_fill = hex_to_fill("F1F5F9")

        row_vals = [
            (idx, Alignment(horizontal="center", vertical="center"), None),
            (codigo, Alignment(horizontal="center", vertical="center"), None),
            (folio, Alignment(horizontal="center", vertical="center"), None),
            (fecha, Alignment(horizontal="center", vertical="center"), None),
            (riesgo, Alignment(horizontal="center", vertical="center"), riesgo_fill),
            (area, Alignment(horizontal="left", vertical="center"), None),
            (ubicacion, Alignment(horizontal="left", vertical="center"), None),
            (f"{eq_id} - {eq_nombre}" if eq_id else "General", Alignment(horizontal="left", vertical="center"), None),
            (solic_nombre, Alignment(horizontal="left", vertical="center"), None),
            (descripcion, Alignment(horizontal="left", vertical="center", wrap_text=True), None),
            (accion, Alignment(horizontal="left", vertical="center", wrap_text=True), None),
            (status, Alignment(horizontal="center", vertical="center"), status_fill),
            (ot, Alignment(horizontal="center", vertical="center"), None),
        ]

        has_photo = bool(foto_b64 and ("base64," in foto_b64 or len(foto_b64) > 100))
        ws.row_dimensions[current_row].height = 65 if has_photo else 25

        for col_i, (val, align, custom_fill) in enumerate(row_vals, start=1):
            cell = ws.cell(row=current_row, column=col_i, value=val)
            cell.font = font_bold if col_i in (2, 5, 12) else font_data
            cell.alignment = align
            cell.border = border_thin
            cell.fill = custom_fill if custom_fill else row_fill

        # Evidencia Fotográfica (Columna 14 = N)
        photo_cell = ws.cell(row=current_row, column=14)
        photo_cell.border = border_thin
        photo_cell.fill = row_fill
        photo_cell.alignment = Alignment(horizontal="center", vertical="center")

        if has_photo:
            try:
                raw_b64 = foto_b64.split(",", 1)[1] if "," in foto_b64 else foto_b64
                img_data = base64.b64decode(raw_b64)
                pil_img = PILImage.open(io.BytesIO(img_data))
                if pil_img.mode not in ("RGB", "RGBA"):
                    pil_img = pil_img.convert("RGB")
                pil_img.thumbnail((120, 75))
                out_img = io.BytesIO()
                pil_img.save(out_img, format="PNG")
                out_img.seek(0)
                xl_img = ExcelImage(out_img)
                xl_img.width = pil_img.width
                xl_img.height = pil_img.height
                cell_coord = f"N{current_row}"
                ws.add_image(xl_img, cell_coord)
            except Exception as e:
                photo_cell.value = "Foto Registrada"
                photo_cell.font = font_muted
        else:
            photo_cell.value = "Sin Evidencia"
            photo_cell.font = font_muted

        current_row += 1

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()

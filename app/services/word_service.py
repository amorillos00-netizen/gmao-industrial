# -*- coding: utf-8 -*-
"""
Servicio de Generación y Exportación Profesional a Word (.docx)
Módulo: Informes Periódicos de Mantenimiento y Confiabilidad Industrial
Empresa: SALTYSNACK TUYERO C.A.
Estándares: ISO 14224 / ISO 55000 / SMRP
"""
import io
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_shading(cell, color_hex):
    """Aplica color de fondo hexadecimal a una celda de tabla."""
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Establece márgenes internos (padding) de una celda."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_informe_periodico_docx(
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
    Genera el informe técnico periódico institucional en formato .docx
    con estructura idéntica a 'Noviembre.docx', tablas formateadas y firmas autorizadas.
    """
    doc = Document()

    # Configuración de márgenes de página (Estándar Formal: 2 cm / 0.79 in)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Diccionario de equipos para resolución rápida
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
        # Filtrar OTs por mes
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

    # OTs Concluidas
    concluidas = [o for o in ots_eval if o.get("status") in ("Concluida", "Completada")]
    preventivas = [o for o in concluidas if o.get("tipo") == "Preventivo"]
    correctivas = [o for o in concluidas if o.get("tipo") == "Correctivo"]
    otras = [o for o in concluidas if o.get("tipo") not in ("Preventivo", "Correctivo")]

    # Métricas SMRP
    horas_base = 8760.0 if periodo_tipo == "Anual" else 720.0
    total_downtime = sum(float(o.get("tiempoParada") or o.get("tiempo_parada") or 0.0) for o in ots_eval)
    total_intervencion = sum(float(o.get("tiempoIntervencion") or o.get("tiempo_intervencion") or 0.0) for o in concluidas)
    horas_operadas = max(0.0, horas_base - total_downtime)
    disponibilidad_pct = min(100.0, round((horas_operadas / horas_base) * 1000) / 10)
    num_fallas = len(correctivas)
    mttr = round((sum(float(c.get("tiempoIntervencion") or c.get("tiempo_intervencion") or 0.0) for c in correctivas) / num_fallas) * 10) / 10 if num_fallas > 0 else 0.0

    # -------------------------------------------------------------
    # 1. ENCABEZADO CORPORATIVO
    # -------------------------------------------------------------
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False
    header_table.columns[0].width = Inches(5.0)
    header_table.columns[1].width = Inches(2.0)

    cell_left = header_table.cell(0, 0)
    p_comp = cell_left.paragraphs[0]
    p_comp.paragraph_format.space_before = Pt(0)
    p_comp.paragraph_format.space_after = Pt(2)
    run_comp = p_comp.add_run("SALTYSNACK TUYERO C.A.")
    run_comp.font.name = "Arial"
    run_comp.font.size = Pt(14)
    run_comp.font.bold = True
    run_comp.font.color.rgb = RGBColor(15, 23, 42) # Slate 900

    p_sub = cell_left.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(2)
    run_sub = p_sub.add_run("DEPARTAMENTO DE MANTENIMIENTO E INFRAESTRUCTURA")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(9)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    p_inf = cell_left.add_paragraph()
    p_inf.paragraph_format.space_after = Pt(0)
    run_inf = p_inf.add_run(f"INFORME DE GESTIÓN Y CONFIABILIDAD | {periodo_texto.upper()}")
    run_inf.font.name = "Arial"
    run_inf.font.size = Pt(10)
    run_inf.font.bold = True
    run_inf.font.color.rgb = RGBColor(10, 110, 209) # SAP Blue

    cell_right = header_table.cell(0, 1)
    p_doc = cell_right.paragraphs[0]
    p_doc.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_doc.paragraph_format.space_after = Pt(2)
    run_doc = p_doc.add_run(f"DOC-INF-{datetime.now().year}")
    run_doc.font.name = "Courier New"
    run_doc.font.size = Pt(10)
    run_doc.font.bold = True
    run_doc.font.color.rgb = RGBColor(30, 41, 59)

    p_date = cell_right.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_date.paragraph_format.space_after = Pt(0)
    run_date = p_date.add_run(f"Emisión: {datetime.now().strftime('%d/%m/%Y')}")
    run_date.font.name = "Arial"
    run_date.font.size = Pt(8.5)
    run_date.font.color.rgb = RGBColor(100, 116, 139)

    # Separador
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(4)
    p_div.paragraph_format.space_after = Pt(10)
    run_div = p_div.add_run("―" * 60)
    run_div.font.color.rgb = RGBColor(203, 213, 225)

    # -------------------------------------------------------------
    # 2. RESUMEN EJECUTIVO Y KPIS
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(6)
    h1.paragraph_format.space_after = Pt(4)
    run_h1 = h1.add_run("1. RESUMEN EJECUTIVO")
    run_h1.font.name = "Arial"
    run_h1.font.size = Pt(11)
    run_h1.font.bold = True
    run_h1.font.color.rgb = RGBColor(15, 23, 42)

    p_res = doc.add_paragraph()
    p_res.paragraph_format.space_after = Pt(8)
    p_res.paragraph_format.line_spacing = 1.15
    res_text = (
        f"Durante el periodo correspondiente a {periodo_texto}, el departamento de mantenimiento industrial "
        f"ejecutó y concluyó un total de {len(concluidas)} órdenes de trabajo (OT) en planta "
        f"({len(preventivas)} mantenimientos preventivos programados, {len(correctivas)} intervenciones correctivas "
        f"y {len(otras)} actividades especializadas/mejoras). La disponibilidad operativa de planta alcanzó "
        f"un {disponibilidad_pct}%, con un tiempo medio de reparación (MTTR) de {mttr} horas (frente a la meta corporativa "
        f"de {mttr_target} horas) y un tiempo total de parada acumulada de {total_downtime:.1f} horas."
    )
    run_res = p_res.add_run(res_text)
    run_res.font.name = "Arial"
    run_res.font.size = Pt(9.5)
    run_res.font.color.rgb = RGBColor(51, 65, 85)

    # Tabla compacta de KPIs
    kpi_table = doc.add_table(rows=2, cols=4)
    kpi_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    kpi_headers = ["Disponibilidad Operativa", f"MTTR (Meta: {mttr_target}h)", "OTs Culminadas", "Horas Parada Total"]
    kpi_values = [f"{disponibilidad_pct}%", f"{mttr} h", str(len(concluidas)), f"{total_downtime:.1f} h"]

    for i in range(4):
        c_h = kpi_table.cell(0, i)
        c_h.paragraphs[0].text = kpi_headers[i]
        c_h.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c_h.paragraphs[0].runs[0].font.name = "Arial"
        c_h.paragraphs[0].runs[0].font.size = Pt(8.5)
        c_h.paragraphs[0].runs[0].font.bold = True
        c_h.paragraphs[0].runs[0].font.color.rgb = RGBColor(71, 85, 105)
        set_cell_shading(c_h, "F1F5F9")
        set_cell_margins(c_h, 80, 80, 100, 100)

        c_v = kpi_table.cell(1, i)
        c_v.paragraphs[0].text = kpi_values[i]
        c_v.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c_v.paragraphs[0].runs[0].font.name = "Arial"
        c_v.paragraphs[0].runs[0].font.size = Pt(12)
        c_v.paragraphs[0].runs[0].font.bold = True
        c_v.paragraphs[0].runs[0].font.color.rgb = RGBColor(10, 110, 209) if i == 0 else (RGBColor(5, 150, 105) if i == 1 else RGBColor(15, 23, 42))
        set_cell_shading(c_v, "FFFFFF")
        set_cell_margins(c_v, 80, 80, 100, 100)

    # -------------------------------------------------------------
    # 3. HISTORIAL DE ACTIVIDADES REALIZADAS
    # -------------------------------------------------------------
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(4)
    run_h2 = h2.add_run("2. HISTORIAL DE ACTIVIDADES REALIZADAS")
    run_h2.font.name = "Arial"
    run_h2.font.size = Pt(11)
    run_h2.font.bold = True
    run_h2.font.color.rgb = RGBColor(15, 23, 42)

    # 2.1 Mantenimiento Preventivo
    h21 = doc.add_paragraph()
    h21.paragraph_format.space_before = Pt(6)
    h21.paragraph_format.space_after = Pt(4)
    run_h21 = h21.add_run(f"2.1 Mantenimiento Preventivo ({len(preventivas)} Rutinas Culminadas)")
    run_h21.font.name = "Arial"
    run_h21.font.size = Pt(10)
    run_h21.font.bold = True
    run_h21.font.color.rgb = RGBColor(30, 41, 59)

    cols_prev = ["Nº", "Fecha Emisión", "Frecuencia", "Máquina / Equipo", "Código", "Actividades Ejecutadas", "Observaciones"]
    table_prev = doc.add_table(rows=1, cols=len(cols_prev))
    table_prev.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table_prev.rows[0].cells
    for idx, cname in enumerate(cols_prev):
        hdr_cells[idx].text = cname
        p = hdr_cells[idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in (0, 1, 2, 4) else WD_ALIGN_PARAGRAPH.LEFT
        p.runs[0].font.name = "Arial"
        p.runs[0].font.size = Pt(8.5)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_shading(hdr_cells[idx], "1E293B")
        set_cell_margins(hdr_cells[idx], 80, 80, 100, 100)

    if preventivas:
        for idx, ot in enumerate(preventivas):
            row_cells = table_prev.add_row().cells
            eq_id = ot.get("equipoId") or ot.get("equipo_id", "")
            eq_info = eq_map.get(eq_id, {})
            eq_name = eq_info.get("name") or eq_info.get("nombre") or eq_id
            f_prog = ot.get("fechaProgramada") or ot.get("fecha_programada") or ot.get("fechaAsignacion") or "-"
            act = ot.get("actividades") or ot.get("descripcion") or "-"

            vals = [str(idx + 1), f_prog, "Programado", eq_name, eq_id, act, "Culminado Conforme"]
            for c_i, v in enumerate(vals):
                row_cells[c_i].text = v
                p = row_cells[c_i].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in (0, 1, 2, 4) else WD_ALIGN_PARAGRAPH.LEFT
                if p.runs:
                    p.runs[0].font.name = "Arial"
                    p.runs[0].font.size = Pt(8)
                    p.runs[0].font.color.rgb = RGBColor(30, 41, 59)
                if idx % 2 == 1:
                    set_cell_shading(row_cells[c_i], "F8FAFC")
                set_cell_margins(row_cells[c_i], 60, 60, 80, 80)
    else:
        empty_row = table_prev.add_row().cells
        empty_row[0].merge(empty_row[len(cols_prev) - 1])
        empty_row[0].text = "No se registraron mantenimientos preventivos culminados en este periodo."
        empty_row[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        empty_row[0].paragraphs[0].runs[0].font.name = "Arial"
        empty_row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        empty_row[0].paragraphs[0].runs[0].font.italic = True
        set_cell_margins(empty_row[0], 80, 80, 100, 100)

    # 2.2 Mantenimiento Correctivo
    h22 = doc.add_paragraph()
    h22.paragraph_format.space_before = Pt(12)
    h22.paragraph_format.space_after = Pt(4)
    run_h22 = h22.add_run(f"2.2 Mantenimiento Correctivo ({len(correctivas)} Fallas Atendidas)")
    run_h22.font.name = "Arial"
    run_h22.font.size = Pt(10)
    run_h22.font.bold = True
    run_h22.font.color.rgb = RGBColor(30, 41, 59)

    cols_corr = ["Nº", "Fecha", "Máquina / Instalación", "Código", "Falla o Requerimiento", "Descripción de Mantenimiento", "Materiales Utilizados", "Observaciones"]
    table_corr = doc.add_table(rows=1, cols=len(cols_corr))
    table_corr.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_corr = table_corr.rows[0].cells
    for idx, cname in enumerate(cols_corr):
        hdr_corr[idx].text = cname
        p = hdr_corr[idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in (0, 1, 3) else WD_ALIGN_PARAGRAPH.LEFT
        p.runs[0].font.name = "Arial"
        p.runs[0].font.size = Pt(8.5)
        p.runs[0].font.bold = True
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_shading(hdr_corr[idx], "1E293B")
        set_cell_margins(hdr_corr[idx], 80, 80, 100, 100)

    if correctivas:
        for idx, ot in enumerate(correctivas):
            row_cells = table_corr.add_row().cells
            eq_id = ot.get("equipoId") or ot.get("equipo_id", "")
            eq_info = eq_map.get(eq_id, {})
            eq_name = eq_info.get("name") or eq_info.get("nombre") or eq_id
            f_act = ot.get("fechaFin") or ot.get("fecha_fin") or ot.get("fechaProgramada") or ot.get("fechaAsignacion") or "-"
            falla = ot.get("descripcion") or "-"
            desc_m = ot.get("actividades") or "Corrección de falla y verificación operativa"
            reps = ot.get("repuestosUsados") or ot.get("repuestos_usados") or []
            rep_text = ", ".join(f"{r.get('name') or r.get('nombre')} (x{r.get('cant', 1)})" for r in reps) if reps else "Ninguno"
            t_int = ot.get("tiempoIntervencion") or ot.get("tiempo_intervencion") or 0.0

            vals = [str(idx + 1), f_act, eq_name, eq_id, falla, desc_m, rep_text, f"Culminado ({t_int}h)"]
            for c_i, v in enumerate(vals):
                row_cells[c_i].text = v
                p = row_cells[c_i].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in (0, 1, 3) else WD_ALIGN_PARAGRAPH.LEFT
                if p.runs:
                    p.runs[0].font.name = "Arial"
                    p.runs[0].font.size = Pt(8)
                    p.runs[0].font.color.rgb = RGBColor(30, 41, 59)
                if idx % 2 == 1:
                    set_cell_shading(row_cells[c_i], "F8FAFC")
                set_cell_margins(row_cells[c_i], 60, 60, 80, 80)
    else:
        empty_row = table_corr.add_row().cells
        empty_row[0].merge(empty_row[len(cols_corr) - 1])
        empty_row[0].text = "No se registraron fallas o mantenimientos correctivos en este periodo."
        empty_row[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        empty_row[0].paragraphs[0].runs[0].font.name = "Arial"
        empty_row[0].paragraphs[0].runs[0].font.size = Pt(8.5)
        empty_row[0].paragraphs[0].runs[0].font.italic = True
        set_cell_margins(empty_row[0], 80, 80, 100, 100)

    # 2.3 Otras Actividades
    if otras:
        h23 = doc.add_paragraph()
        h23.paragraph_format.space_before = Pt(12)
        h23.paragraph_format.space_after = Pt(4)
        run_h23 = h23.add_run(f"3. Otras Actividades Especiales y Mejoras ({len(otras)} Realizadas)")
        run_h23.font.name = "Arial"
        run_h23.font.size = Pt(10)
        run_h23.font.bold = True
        run_h23.font.color.rgb = RGBColor(30, 41, 59)

        cols_otras = ["Nº", "Fecha", "Descripción de la Actividad", "Materiales Utilizados", "Observaciones"]
        table_otras = doc.add_table(rows=1, cols=len(cols_otras))
        table_otras.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr_otras = table_otras.rows[0].cells
        for idx, cname in enumerate(cols_otras):
            hdr_otras[idx].text = cname
            p = hdr_otras[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in (0, 1) else WD_ALIGN_PARAGRAPH.LEFT
            p.runs[0].font.name = "Arial"
            p.runs[0].font.size = Pt(8.5)
            p.runs[0].font.bold = True
            p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
            set_cell_shading(hdr_otras[idx], "1E293B")
            set_cell_margins(hdr_otras[idx], 80, 80, 100, 100)

        for idx, ot in enumerate(otras):
            row_cells = table_otras.add_row().cells
            f_act = ot.get("fechaFin") or ot.get("fecha_fin") or ot.get("fechaProgramada") or ot.get("fechaAsignacion") or "-"
            act = ot.get("actividades") or ot.get("descripcion") or "-"
            reps = ot.get("repuestosUsados") or ot.get("repuestos_usados") or []
            rep_text = ", ".join(f"{r.get('name') or r.get('nombre')} (x{r.get('cant', 1)})" for r in reps) if reps else "Insumos menores"

            vals = [str(idx + 1), f_act, act, rep_text, "Culminada Conforme"]
            for c_i, v in enumerate(vals):
                row_cells[c_i].text = v
                p = row_cells[c_i].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_i in (0, 1) else WD_ALIGN_PARAGRAPH.LEFT
                if p.runs:
                    p.runs[0].font.name = "Arial"
                    p.runs[0].font.size = Pt(8)
                    p.runs[0].font.color.rgb = RGBColor(30, 41, 59)
                if idx % 2 == 1:
                    set_cell_shading(row_cells[c_i], "F8FAFC")
                set_cell_margins(row_cells[c_i], 60, 60, 80, 80)

    # -------------------------------------------------------------
    # 4. CAMPOS DE FIRMA DINÁMICOS
    # -------------------------------------------------------------
    doc.add_paragraph().paragraph_format.space_before = Pt(20)

    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.autofit = False
    sig_table.columns[0].width = Inches(3.5)
    sig_table.columns[1].width = Inches(3.5)

    # Celda Jefe de Mantenimiento
    c_sig_jefe = sig_table.cell(0, 0)
    p_line_jefe = c_sig_jefe.paragraphs[0]
    p_line_jefe.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line_jefe.paragraph_format.space_after = Pt(2)
    p_line_jefe.add_run("_________________________________________")

    p_jefe_name = c_sig_jefe.add_paragraph()
    p_jefe_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_jefe_name.paragraph_format.space_after = Pt(1)
    run_jn = p_jefe_name.add_run(nombre_jefe)
    run_jn.font.name = "Arial"
    run_jn.font.size = Pt(9.5)
    run_jn.font.bold = True
    run_jn.font.color.rgb = RGBColor(15, 23, 42)

    p_jefe_c = c_sig_jefe.add_paragraph()
    p_jefe_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_jefe_c.paragraph_format.space_after = Pt(0)
    run_jc = p_jefe_c.add_run(f"{cargo_jefe}\nSALTYSNACK TUYERO C.A.")
    run_jc.font.name = "Arial"
    run_jc.font.size = Pt(8.5)
    run_jc.font.color.rgb = RGBColor(71, 85, 105)

    # Celda Gerente de Planta
    c_sig_ger = sig_table.cell(0, 1)
    p_line_ger = c_sig_ger.paragraphs[0]
    p_line_ger.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line_ger.paragraph_format.space_after = Pt(2)
    p_line_ger.add_run("_________________________________________")

    p_ger_name = c_sig_ger.add_paragraph()
    p_ger_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ger_name.paragraph_format.space_after = Pt(1)
    run_gn = p_ger_name.add_run(nombre_gerente)
    run_gn.font.name = "Arial"
    run_gn.font.size = Pt(9.5)
    run_gn.font.bold = True
    run_gn.font.color.rgb = RGBColor(15, 23, 42)

    p_ger_c = c_sig_ger.add_paragraph()
    p_ger_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ger_c.paragraph_format.space_after = Pt(0)
    run_gc = p_ger_c.add_run(f"{cargo_gerente}\nAprobación Final y Conforme")
    run_gc.font.name = "Arial"
    run_gc.font.size = Pt(8.5)
    run_gc.font.color.rgb = RGBColor(71, 85, 105)

    # Guardar documento en buffer de bytes
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

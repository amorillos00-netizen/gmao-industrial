# -*- coding: utf-8 -*-
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_HTML = BASE_DIR / "index.html"
STATIC_INDEX_HTML = BASE_DIR / "app" / "static" / "index.html"

html = INDEX_HTML.read_text(encoding="utf-8")

# 1. En openModalOT:
open_modal_old = """            document.getElementById('otFotoAntesBase64').value = '';
            if (document.getElementById('otSslId')) document.getElementById('otSslId').value = '';
            if (document.getElementById('otSolicitudId')) document.getElementById('otSolicitudId').value = '';"""

open_modal_new = """            document.getElementById('otFotoAntesBase64').value = '';
            if (document.getElementById('otPlanId')) document.getElementById('otPlanId').value = '';
            if (document.getElementById('otSslId')) document.getElementById('otSslId').value = '';
            if (document.getElementById('otSolicitudId')) document.getElementById('otSolicitudId').value = '';"""

if open_modal_old in html and "document.getElementById('otPlanId').value = '';" not in html:
    html = html.replace(open_modal_old, open_modal_new)
    print("[OK] Reset de otPlanId en openModalOT")

open_modal_edit_old = """            if (otId) {
                const ot = db.ots.find(x => x.id === otId);
                if (!ot) return;
                titleEl.textContent = 'Editar Orden de Trabajo';"""

open_modal_edit_new = """            if (otId) {
                const ot = db.ots.find(x => x.id === otId);
                if (!ot) return;
                titleEl.textContent = 'Editar Orden de Trabajo';
                if (document.getElementById('otPlanId')) document.getElementById('otPlanId').value = ot.planId || '';"""

if open_modal_edit_old in html and "document.getElementById('otPlanId').value = ot.planId || '';" not in html:
    html = html.replace(open_modal_edit_old, open_modal_edit_new)
    print("[OK] Carga de otPlanId en edición de openModalOT")

# 2. En formOT submit:
form_submit_old = """            const editId = document.getElementById('otId').value;
            const solId = document.getElementById('otSolicitudId').value;
            const sslId = (document.getElementById('otSslId') ? document.getElementById('otSslId').value : '') || '';"""

form_submit_new = """            const editId = document.getElementById('otId').value;
            const planId = (document.getElementById('otPlanId') ? document.getElementById('otPlanId').value : '') || '';
            const solId = document.getElementById('otSolicitudId').value;
            const sslId = (document.getElementById('otSslId') ? document.getElementById('otSslId').value : '') || '';"""

if form_submit_old in html and "const planId = (document.getElementById('otPlanId')" not in html:
    html = html.replace(form_submit_old, form_submit_new)
    print("[OK] Lectura de planId en submit de formOT")

payload_edit_old = """                    fechaProgramada: document.getElementById('otFechaProgramada').value,
                    fotoAntes: document.getElementById('otFotoAntesBase64').value || existing.fotoAntes || '',
                    updatedAt: new Date().toISOString()"""

payload_edit_new = """                    fechaProgramada: document.getElementById('otFechaProgramada').value,
                    planId: planId || existing.planId || null,
                    fotoAntes: document.getElementById('otFotoAntesBase64').value || existing.fotoAntes || '',
                    updatedAt: new Date().toISOString()"""

if payload_edit_old in html and "planId: planId || existing.planId || null," not in html:
    html = html.replace(payload_edit_old, payload_edit_new)
    print("[OK] Persistencia de planId en edición de formOT")

payload_new_old = """                    repuestosUsados: [],
                    solicitudId: solId || null,
                    sslReportId: sslId || null"""

payload_new_new = """                    repuestosUsados: [],
                    planId: planId || null,
                    solicitudId: solId || null,
                    sslReportId: sslId || null"""

if payload_new_old in html and "planId: planId || null," not in html:
    html = html.replace(payload_new_old, payload_new_new)
    print("[OK] Persistencia de planId en nueva OT de formOT")

INDEX_HTML.write_text(html, encoding="utf-8")
STATIC_INDEX_HTML.write_text(html, encoding="utf-8")
print("[COMPLETO] Actualizaciones de enlace OT-Plan guardadas.")

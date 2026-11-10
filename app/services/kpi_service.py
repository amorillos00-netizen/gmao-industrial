"""
Servicio de Ingeniería de Confiabilidad y Cálculo de Indicadores (KPIs)
Estándares SMRP (Society for Maintenance & Reliability Professionals) e ISO 14224.
Soporte completo para filtrado dinámico por Periodo: Mensual vs Anual.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.config import DEFAULT_MONTHLY_HOURS, AVAILABILITY_TARGET_PCT

DEFAULT_YEARLY_HOURS = 8760.0

def calculate_reliability_kpis(
    ots: List[Dict[str, Any]], 
    equipo_filter: str = "TODOS",
    periodo_tipo: str = "Mensual",
    periodo_valor: Optional[str] = None,
    mttr_target_hours: float = 2.0
) -> Dict[str, Any]:
    """
    Calcula los indicadores nucleares de mantenimiento y confiabilidad industrial con filtrado dinámico por periodo.
    
    Fórmulas estándar:
    - Disponibilidad = ((Horas Operativas) / (Horas Planificadas del Periodo)) * 100
    - MTBF = Horas Operativas / Número de Fallas Correctivas Concluidas
    - MTTR = Total Horas Reparación / Número de Fallas Correctivas Concluidas
    - Cumplimiento Preventivo = (Preventivas Concluidas / Total Preventivas Programadas en el periodo) * 100
    """
    # 1. Filtrado por equipo
    if equipo_filter and equipo_filter != "TODOS":
        ots_evaluadas = [o for o in ots if o.get("equipoId") == equipo_filter or o.get("equipo_id") == equipo_filter]
    else:
        ots_evaluadas = list(ots)

    # 2. Filtrado dinámico por periodo (Mensual vs Anual)
    # periodo_tipo: 'Mensual' | 'Anual'
    # periodo_valor: '2026-10' (para mensual) o '2026' (para anual) o None (periodo actual/último)
    if periodo_tipo == "Anual":
        horas_base = DEFAULT_YEARLY_HOURS
        filtro_anio = periodo_valor if (periodo_valor and len(str(periodo_valor)) == 4) else None
        if filtro_anio:
            ots_evaluadas = [
                o for o in ots_evaluadas 
                if (o.get("fechaProgramada") or o.get("fecha_programada") or o.get("fechaAsignacion") or o.get("fecha_asignacion") or "").startswith(filtro_anio)
            ]
    else:
        # Modo Mensual por defecto
        horas_base = DEFAULT_MONTHLY_HOURS
        filtro_mes = periodo_valor if (periodo_valor and len(str(periodo_valor)) >= 7) else None
        if filtro_mes:
            ots_evaluadas = [
                o for o in ots_evaluadas 
                if (o.get("fechaProgramada") or o.get("fecha_programada") or o.get("fechaAsignacion") or o.get("fecha_asignacion") or "").startswith(filtro_mes[:7])
            ]

    total_ots = len(ots_evaluadas)
    concluidas = [o for o in ots_evaluadas if o.get("status") in ("Concluida", "Completada")]
    
    # Separación rigurosa por tipo de mantenimiento
    preventivas = [o for o in ots_evaluadas if o.get("tipo") == "Preventivo"]
    preventivas_concluidas = [o for o in preventivas if o.get("status") in ("Concluida", "Completada")]
    
    correctivas = [o for o in ots_evaluadas if o.get("tipo") == "Correctivo"]
    correctivas_concluidas = [o for o in correctivas if o.get("status") in ("Concluida", "Completada")]
    
    eventuales = [o for o in ots_evaluadas if o.get("tipo") in ("Eventual", "Mejora", "Predictivo")]

    # Tiempos de parada (Downtime) y de intervención (Horas Hombre)
    total_downtime = sum(float(o.get("tiempoParada") or o.get("tiempo_parada") or 0.0) for o in ots_evaluadas)
    total_intervencion_correctiva = sum(float(o.get("tiempoIntervencion") or o.get("tiempo_intervencion") or 0.0) for o in correctivas_concluidas)
    total_intervencion_general = sum(float(o.get("tiempoIntervencion") or o.get("tiempo_intervencion") or 0.0) for o in concluidas)

    # 1. Disponibilidad Operativa (%)
    horas_operadas = max(0.0, horas_base - total_downtime)
    disponibilidad_pct = round((horas_operadas / horas_base) * 100.0, 1)

    # 2. MTTR (Mean Time To Repair) y MTBF (Mean Time Between Failures)
    num_fallas = len(correctivas_concluidas)
    if num_fallas > 0:
        mttr_horas = round(total_intervencion_correctiva / num_fallas, 1)
        mtbf_horas = round(horas_operadas / num_fallas, 1)
    else:
        mttr_horas = 0.0
        mtbf_horas = round(horas_base, 1)

    # 3. Cumplimiento Preventivo (%)
    if len(preventivas) > 0:
        cumplimiento_preventivo_pct = round((len(preventivas_concluidas) / len(preventivas)) * 100.0, 1)
    else:
        cumplimiento_preventivo_pct = 100.0

    return {
        "periodo_tipo": periodo_tipo,
        "periodo_valor": periodo_valor,
        "horas_base": horas_base,
        "disponibilidad_pct": disponibilidad_pct,
        "disponibilidad_meta_pct": AVAILABILITY_TARGET_PCT,
        "mttr_horas": mttr_horas,
        "mttr_meta_horas": mttr_target_hours,
        "mtbf_horas": mtbf_horas,
        "cumplimiento_preventivo_pct": cumplimiento_preventivo_pct,
        "total_downtime_horas": round(total_downtime, 1),
        "total_intervencion_horas": round(total_intervencion_general, 1),
        "total_ots": total_ots,
        "total_concluidas": len(concluidas),
        "total_pendientes": total_ots - len(concluidas),
        "conteo_preventivas": len(preventivas),
        "conteo_preventivas_concluidas": len(preventivas_concluidas),
        "conteo_correctivas": len(correctivas),
        "conteo_correctivas_concluidas": len(correctivas_concluidas),
        "conteo_eventuales": len(eventuales),
        "diagnostico": (
            f"Condición operativa óptima en periodo {periodo_tipo.lower()} (>95%)."
            if disponibilidad_pct >= AVAILABILITY_TARGET_PCT
            else f"Alerta de confiabilidad en periodo {periodo_tipo.lower()}: Alta indisponibilidad detectada ({disponibilidad_pct}%)."
        )
    }

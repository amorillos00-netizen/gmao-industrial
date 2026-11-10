"""
Suite de Pruebas Unitarias para Cálculo de Confiabilidad y Fórmulas SMRP / ISO 14224.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.kpi_service import calculate_reliability_kpis

def test_kpi_calculation():
    # Caso de prueba: Planta con 2 paradas que suman 20 horas de downtime
    ots_mock = [
        {"id": "OT-01", "tipo": "Preventivo", "status": "Concluida", "tiempoParada": 0, "tiempoIntervencion": 3.0, "equipoId": "EQ-101"},
        {"id": "OT-02", "tipo": "Preventivo", "status": "Concluida", "tiempoParada": 0, "tiempoIntervencion": 2.0, "equipoId": "EQ-101"},
        {"id": "OT-03", "tipo": "Correctivo", "status": "Concluida", "tiempoParada": 12.0, "tiempoIntervencion": 4.0, "equipoId": "EQ-101"},
        {"id": "OT-04", "tipo": "Correctivo", "status": "Concluida", "tiempoParada": 8.0, "tiempoIntervencion": 6.0, "equipoId": "EQ-101"},
        {"id": "OT-05", "tipo": "Preventivo", "status": "Pendiente", "tiempoParada": 0, "tiempoIntervencion": 0.0, "equipoId": "EQ-101"},
    ]

    kpis = calculate_reliability_kpis(ots_mock, "TODOS")

    # Validaciones:
    # Downtime total = 12 + 8 = 20 horas
    assert kpis["total_downtime_horas"] == 20.0, f"Downtime esperado 20.0, obtenido {kpis['total_downtime_horas']}"
    
    # Horas operadas = 720 - 20 = 700 horas
    # Disponibilidad = (700 / 720) * 100 = 97.22% -> 97.2%
    assert kpis["disponibilidad_pct"] == 97.2, f"Disponibilidad esperada 97.2%, obtenida {kpis['disponibilidad_pct']}%"
    
    # MTTR = (4 + 6) / 2 fallas = 5.0 horas
    assert kpis["mttr_horas"] == 5.0, f"MTTR esperado 5.0, obtenido {kpis['mttr_horas']}"
    
    # MTBF = 700 / 2 fallas = 350.0 horas
    assert kpis["mtbf_horas"] == 350.0, f"MTBF esperado 350.0, obtenido {kpis['mtbf_horas']}"
    
    # Cumplimiento preventivo = 2 concluidas de 3 = 66.7%
    assert kpis["cumplimiento_preventivo_pct"] == 66.7, f"Cumplimiento esperado 66.7%, obtenido {kpis['cumplimiento_preventivo_pct']}%"

    print("[OK] Todas las pruebas de confiabilidad y formulas SMRP pasaron con exito.")

if __name__ == "__main__":
    test_kpi_calculation()

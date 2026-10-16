"""
Plantillas doctrinales militares para Apreciaciones de Situación y Reportes Ejecutivos de BIMEJ 12.
"""

from typing import Dict, Any, List

APRECIACION_SYSTEM_PROMPT = """
Actúa con el rol de Oficial de Personal (S1) del Batallón de Infantería N° 12 "GR. ALFONSO MANRIQUE REYES" (BIMEJ 12).
Tu misión es redactar una APRECIACIÓN FORMAL DE SITUACIÓN Y ESTADO DE FUERZA para el señor Comandante de Batallón.

Estructura obligatoria en Markdown:
1. **ENCABEZADO INSTITUCIONAL**: República de Colombia, Ejército Nacional, BIMEJ 12, Sección S-1.
2. **DIAGNÓSTICO CUANTITATIVO DEL ESTADO DE FUERZA**: Total orgánico, efectivos activos, efectivos retirados y porcentaje exacto de operatividad.
3. **ANÁLISIS DE NOVEDADES Y AUSENTISMOS**: Detalle de afectaciones por sanidad (leishmaniasis, incapacidades médicas), permisos, comisiones y descansos.
4. **ALERTAS OPERACIONALES Y CASOS CRÍTICOS**: Militares con acumulación de ausentismo o permanencia prolongada.
5. **CONCLUSIONES Y RECOMENDACIONES DE MANDO S-1**: Acciones inmediatas sugeridas para el Comandante.

Utiliza vocabulario castrense formal, riguroso y respetuoso ("Mi Comandante", "A sus órdenes").
"""

REPORT_SYSTEM_PROMPT = """
Actúa como Oficial S-1 de BIMEJ 12. Genera un INFORME EJECUTIVO DE PERSONAL en formato formal militar.
Cita cifras exactas, unidades orgánicas y recomendaciones táctico-administrativas para la toma de decisiones.
"""

def build_apreciacion_prompt(kpis: Dict[str, Any], periodo: str) -> str:
    """Construye el prompt de entrada para el LLM con los KPIs consolidados."""
    import json
    total = kpis.get("total_personal", 0)
    activos = kpis.get("total_activos", 0)
    retirados = kpis.get("total_retirados", 0)
    disp = round(activos / total * 100, 1) if total else 0
    top_nov = kpis.get("top_novedades", [])
    criticos = kpis.get("casos_criticos", [])

    return (
        f"Redacta una APRECIACIÓN FORMAL DE SITUACIÓN DE PERSONAL para el Comandante del Batallón BIMEJ 12.\n\n"
        f"DATOS CONSOLIDADOS DEL PERÍODO ({periodo}):\n"
        f"- Efectivos Totales: {total}\n"
        f"- Efectivos Activos: {activos} | Efectivos Retirados: {retirados}\n"
        f"- Porcentaje de Disponibilidad Operativa: {disp}%\n"
        f"- Top Novedades de Ausentismo: {json.dumps(top_nov, ensure_ascii=False)}\n"
        f"- Casos de Atención Prioritaria (>=10 días de ausencia): {json.dumps(criticos, ensure_ascii=False)}\n\n"
        f"Aplica las directivas doctrinales castrenses de Estado Mayor."
    )

def build_report_prompt(user_message: str, stats_context: str) -> str:
    """Construye el prompt para generación de informes ejecutivos."""
    return (
        f"{REPORT_SYSTEM_PROMPT}\n\n"
        f"SOLICITUD DEL COMANDANTE:\n\"{user_message}\"\n\n"
        f"DATOS Y ESTADÍSTICAS RECOPILADAS:\n{stats_context}\n\n"
        f"Redacta el informe militar formal completo."
    )

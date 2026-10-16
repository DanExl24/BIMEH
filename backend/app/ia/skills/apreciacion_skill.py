"""
Habilidad para redactar y consolidar la Apreciación de Situación de Personal S-1 para la Comandancia.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any

from app.ia.skills.base import BaseSkill, QueryContext, SkillResult
from app.ia.sql.executor import execute_safe_query
from app.ia.prompts.report_templates import APRECIACION_SYSTEM_PROMPT, build_apreciacion_prompt
from app.ia.providers import get_llm_provider

class ApreciacionSkill(BaseSkill):
    name = "apreciacion_skill"
    description = "Genera el informe formal de Apreciación de Situación de Personal y Estado de Fuerza para el Comandante."

    def can_handle(self, ctx: QueryContext) -> bool:
        msg = ctx.msg_norm
        triggers = [
            "apreciacion", "apreciacion militar", "apreciacion de situacion",
            "apreciacion de personal", "informe formal de mando", "boletin de situacion",
            "estado de fuerza formal", "informe de estado mayor"
        ]
        return any(t in msg for t in triggers)

    def execute(self, ctx: QueryContext) -> Optional[SkillResult]:
        db = ctx.db
        if not db:
            return None

        now = datetime.now()
        def run(sql: str) -> Dict[str, Any]:
            try:
                cols, rows = execute_safe_query(db, sql)
                return {"columns": cols, "rows": rows, "total": len(rows)}
            except Exception:
                return {"columns": [], "rows": [{}], "total": 0}

        total = run("SELECT COUNT(*) AS t FROM v_personal_resumen")["rows"][0].get("t", 0)
        activos = run("SELECT COUNT(*) AS t FROM v_personal_resumen WHERE estado='ACTIVO'")["rows"][0].get("t", 0)
        retirados = run("SELECT COUNT(*) AS t FROM v_personal_resumen WHERE estado='RETIRADO'")["rows"][0].get("t", 0)
        top_nov = run("SELECT novedad, total_dias_registrados FROM v_conteo_novedades ORDER BY total_dias_registrados DESC LIMIT 5")["rows"]
        criticos = run(f"SELECT cedula, nombre, COUNT(*) AS dias FROM v_novedades_detalle WHERE fecha_reporte LIKE '{now.year}-%' GROUP BY cedula, nombre HAVING COUNT(*)>=10 ORDER BY dias DESC LIMIT 10")["rows"]

        kpis = {
            "total_personal": total,
            "total_activos": activos,
            "total_retirados": retirados,
            "top_novedades": top_nov,
            "casos_criticos": criticos
        }
        periodo = now.strftime("%B %Y")
        prompt = build_apreciacion_prompt(kpis, periodo)

        llm, model_name = get_llm_provider()
        briefing = llm.generate_text(
            prompt=prompt,
            system_instruction=APRECIACION_SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=1024
        )

        return SkillResult(
            type="conversation",
            answer=briefing,
            report_info={
                "periodo": periodo,
                "kpis": kpis,
                "apreciacion": briefing,
                "fecha_generacion": now.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

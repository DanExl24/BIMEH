"""
Habilidad para consultar el estado de fuerza, efectivos orgánicos, activos, retirados y despliegue del batallón.
"""

import re
from typing import Optional
from app.ia.skills.base import BaseSkill, QueryContext, SkillResult

class EfectivosSkill(BaseSkill):
    name = "efectivos_skill"
    description = "Consulta la fuerza disponible, personal activo, retirado y distribución operativa de BIMEJ 12."

    def can_handle(self, ctx: QueryContext) -> bool:
        msg = ctx.msg_norm
        # Total personal activo
        if re.search(r"\b(cuantos?|total|efectivos?|cantidad)\b", msg) and \
           re.search(r"\b(activos?|disponibles?)\b", msg) and \
           not re.search(r"\b(novedad|novedades|retirado)\b", msg):
            return True

        # Total personal retirado
        if re.search(r"\b(cuantos?|total|cantidad)\b", msg) and \
           re.search(r"\b(retirados?|bajas?|dados? de baja)\b", msg):
            return True

        # Resumen general del batallón
        if re.search(r"\b(cuantos?\s+militares?|total\s+de\s+personal|fuerza\s+total|efectivo\s+total)\b", msg):
            return True

        # Personal en área de operaciones vs comando
        if re.search(r"\b(area\s+de\s+operaciones|cdo\s+unidad|comando\s+de\s+unidad|fuerza\s+disponible)\b", msg) and \
           re.search(r"\b(cuantos?|total|listado|personal|efectivos?)\b", msg):
            return True

        return False

    def execute(self, ctx: QueryContext) -> Optional[SkillResult]:
        msg = ctx.msg_norm

        # 1. Total personal activo
        if re.search(r"\b(cuantos?|total|efectivos?|cantidad)\b", msg) and \
           re.search(r"\b(activos?|disponibles?)\b", msg) and \
           not re.search(r"\b(novedad|novedades|retirado)\b", msg):
            return SkillResult(
                type="sql",
                sql="SELECT COUNT(*) AS total_activos FROM v_personal_resumen WHERE estado = 'ACTIVO'",
                description="Conteo total de personal activo en BIMEJ 12"
            )

        # 2. Total personal retirado
        if re.search(r"\b(cuantos?|total|cantidad)\b", msg) and \
           re.search(r"\b(retirados?|bajas?|dados? de baja)\b", msg):
            return SkillResult(
                type="sql",
                sql="SELECT COUNT(*) AS total_retirados FROM v_personal_resumen WHERE estado = 'RETIRADO'",
                description="Conteo total de personal retirado en BIMEJ 12"
            )

        # 3. Resumen general del batallón
        if re.search(r"\b(cuantos?\s+militares?|total\s+de\s+personal|fuerza\s+total|efectivo\s+total)\b", msg):
            return SkillResult(
                type="sql",
                sql="SELECT estado, COUNT(*) AS total FROM v_personal_resumen GROUP BY estado ORDER BY total DESC",
                description="Resumen total del personal del batallón por estado"
            )

        # 4. Despliegue área de operaciones vs comando
        if re.search(r"\b(area\s+de\s+operaciones|cdo\s+unidad|comando\s+de\s+unidad|fuerza\s+disponible)\b", msg):
            filtro_sub = "AREA OPERACIONES" if "area" in msg else "CDO UNIDAD"
            mes_filter = f"AND fecha_reporte LIKE '{ctx.anio}-{ctx.mes_num:02d}-%'" if ctx.mes_num else ""
            return SkillResult(
                type="sql",
                sql=f"SELECT cedula, nombre, fecha_reporte, novedad FROM v_novedades_detalle WHERE UPPER(novedad) LIKE '%{filtro_sub}%' {mes_filter} ORDER BY fecha_reporte DESC LIMIT 50",
                description=f"Personal desplegado en {filtro_sub}"
            )

        return None

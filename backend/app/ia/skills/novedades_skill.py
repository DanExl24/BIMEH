"""
Habilidad para consultar novedades, ausentismos, rankings, incapacidades y permisos del batallón.
"""

import re
from typing import Optional
from app.ia.skills.base import BaseSkill, QueryContext, SkillResult

class NovedadesSkill(BaseSkill):
    name = "novedades_skill"
    description = "Consulta novedades del día, ausentismos, rankings (más/menos frecuentes) y afectaciones de personal."

    def can_handle(self, ctx: QueryContext) -> bool:
        # Si la consulta va dirigida a un militar específico por cédula o contexto, lo maneja MilitarSkill
        if ctx.cedula_en_msg or ctx.active_militar:
            return False

        msg = ctx.msg_norm

        # Novedades de hoy
        hoy_triggers = ["hoy", "del dia de hoy", "reporte de hoy", "parte de hoy", "novedades de hoy", "quienes tienen novedad hoy"]
        if any(t in msg for t in hoy_triggers):
            return True

        # Ranking de novedades del batallón
        ranking_triggers = (
            r"\b(ranking|rankings|top\s*\d*|mas\s+frecuentes?|mas\s+comunes?|"
            r"mas\s+presentadas?|mas\s+registradas?|mas\s+repetidas?|"
            r"menos\s+frecuentes?|menos\s+comunes?|menos\s+registradas?|"
            r"novedades\s+frecuentes|que\s+novedades\s+hay\s+mas|"
            r"cuales\s+son\s+las\s+novedades|novedades\s+del\s+batallon|"
            r"principales\s+novedades|novedades\s+principales)\b"
        )
        if re.search(ranking_triggers, msg) or ctx.is_least:
            return True

        # Novedad por tipo (vacaciones, permisos, incapacidades, leishmaniasis)
        if ctx.novedad_type or ctx.subnovedad_oficial:
            return True

        # Novedades generales de un mes
        if ctx.mes_num and re.search(r"\b(novedades?|reportes?|ausencias?|afectaciones?)\b", msg):
            return True

        # Umbral de días
        if re.search(r"m[aá]s\s+de\s+(\d+)\s+d[ií]as?", msg):
            return True

        return False

    def execute(self, ctx: QueryContext) -> Optional[SkillResult]:
        msg = ctx.msg_norm
        anio = ctx.anio
        mes_num = ctx.mes_num

        # 1. Novedades de hoy
        hoy_triggers = ["hoy", "del dia de hoy", "reporte de hoy", "parte de hoy", "novedades de hoy", "quienes tienen novedad hoy"]
        if any(t in msg for t in hoy_triggers):
            return SkillResult(
                type="sql",
                sql="SELECT cedula, nombre, fecha_reporte, novedad, descripcion FROM v_novedades_detalle WHERE fecha_reporte = CURRENT_DATE ORDER BY nombre ASC LIMIT 50",
                description="Personal con novedad registrada hoy en BIMEJ 12"
            )

        # 2. Ranking de novedades del batallón
        ranking_triggers = (
            r"\b(ranking|rankings|top\s*\d*|mas\s+frecuentes?|mas\s+comunes?|"
            r"mas\s+presentadas?|mas\s+registradas?|mas\s+repetidas?|"
            r"menos\s+frecuentes?|menos\s+comunes?|menos\s+registradas?|"
            r"novedades\s+frecuentes|que\s+novedades\s+hay\s+mas|"
            r"cuales\s+son\s+las\s+novedades|novedades\s+del\s+batallon|"
            r"principales\s+novedades|novedades\s+principales)\b"
        )
        if re.search(ranking_triggers, msg) or ctx.is_least:
            order = "ASC" if ctx.is_least else "DESC"
            desc_tipo = "menos frecuentes" if ctx.is_least else "más frecuentes"
            if mes_num:
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT novedad, COUNT(*) AS total_dias_registrados, COUNT(DISTINCT cedula) AS total_personal_afectado "
                        f"FROM v_novedades_detalle WHERE fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                        f"GROUP BY novedad ORDER BY total_dias_registrados {order} LIMIT 10"
                    ),
                    description=f"Ranking de novedades {desc_tipo} en mes {mes_num}/{anio}"
                )
            return SkillResult(
                type="sql",
                sql=(
                    f"SELECT novedad, total_dias_registrados, total_personal_afectado "
                    f"FROM v_conteo_novedades ORDER BY total_dias_registrados {order} LIMIT 10"
                ),
                description=f"Ranking de novedades {desc_tipo} en BIMEJ 12"
            )

        # 3. Personal con más de N días de novedad
        min_days_match = re.search(r"m[aá]s\s+de\s+(\d+)\s+d[ií]as?", msg)
        min_days = int(min_days_match.group(1)) if min_days_match else None
        if min_days is not None:
            novedad_clause = f"AND UPPER(novedad) LIKE '%{ctx.novedad_type}%'" if ctx.novedad_type else ""
            mes_clause = f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%'" if mes_num else f"AND fecha_reporte LIKE '{anio}-%'"
            nov_desc = f" de {ctx.novedad_type}" if ctx.novedad_type else ""
            mes_desc = f" en mes {mes_num}/{anio}" if mes_num else f" en {anio}"
            return SkillResult(
                type="sql",
                sql=(
                    f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                    f"FROM v_novedades_detalle WHERE 1=1 {novedad_clause} {mes_clause} "
                    f"GROUP BY cedula, nombre, novedad HAVING COUNT(*) > {min_days} "
                    f"ORDER BY total_dias DESC LIMIT 50"
                ),
                description=f"Personal con más de {min_days} días{nov_desc}{mes_desc}"
            )

        # 4. Novedad por tipo + rango de días
        if ctx.novedad_type and ctx.day_range and mes_num:
            d1, d2 = ctx.day_range
            return SkillResult(
                type="sql",
                sql=(
                    f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                    f"FROM v_novedades_detalle WHERE UPPER(novedad) LIKE '%{ctx.novedad_type}%' "
                    f"AND fecha_reporte >= '{anio}-{mes_num:02d}-{d1:02d}' "
                    f"AND fecha_reporte <= '{anio}-{mes_num:02d}-{d2:02d}' "
                    f"ORDER BY fecha_reporte ASC, nombre ASC LIMIT 50"
                ),
                description=f"Personal con {ctx.novedad_type} del {d1} al {d2} de mes {mes_num}/{anio}"
            )

        # 5. Novedad por tipo + mes completo
        if ctx.novedad_type and mes_num:
            return SkillResult(
                type="sql",
                sql=(
                    f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                    f"FROM v_novedades_detalle WHERE UPPER(novedad) LIKE '%{ctx.novedad_type}%' "
                    f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                    f"ORDER BY fecha_reporte ASC, nombre ASC LIMIT 50"
                ),
                description=f"Personal con {ctx.novedad_type} en mes {mes_num}/{anio}"
            )

        # 6. Novedad por tipo general
        if ctx.novedad_type:
            return SkillResult(
                type="sql",
                sql=(
                    f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                    f"FROM v_novedades_detalle WHERE UPPER(novedad) LIKE '%{ctx.novedad_type}%' "
                    f"ORDER BY fecha_reporte DESC LIMIT 50"
                ),
                description=f"Personal con {ctx.novedad_type} en BIMEJ 12"
            )

        # 7. Novedades generales de un mes
        if mes_num:
            return SkillResult(
                type="sql",
                sql=(
                    f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                    f"FROM v_novedades_detalle WHERE fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                    f"ORDER BY fecha_reporte ASC LIMIT 50"
                ),
                description=f"Novedades del mes {mes_num}/{anio}"
            )

        return None

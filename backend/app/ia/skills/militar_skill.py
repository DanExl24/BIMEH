"""
Habilidad para consultar expedientes individuales, novedades y búsqueda de militares por cédula o nombre.
"""

import re
from typing import Optional
from app.ia.skills.base import BaseSkill, QueryContext, SkillResult
from app.ia.nlp.militar_matcher import _extract_name_tokens, _name_like_clause

def _build_novedad_sql_clause(novedad_type: str, col_name: str = "novedad") -> str:
    nt = novedad_type.upper().strip()
    if nt in ("INCAPACIDAD", "INCAPACIDADES", "I/R", "IR", "REPOSO", "EXCUSA", "EXCUSA MEDICA"):
        return f"({col_name} ILIKE '%INCAPACIDAD%' OR {col_name} = 'I/R' OR {col_name} ILIKE '%REPOSO%')"
    elif nt in ("VACACION", "VACACIONES", "DESCANSO"):
        return f"({col_name} ILIKE '%VACACION%' OR {col_name} ILIKE '%DESCANSO%')"
    return f"UPPER({col_name}) LIKE '%{nt}%'"

class MilitarSkill(BaseSkill):
    name = "militar_skill"
    description = "Consulta expedientes individuales, historiales de novedades y búsquedas por cédula o nombre propio."

    def can_handle(self, ctx: QueryContext) -> bool:
        # Cédula en el mensaje
        if ctx.cedula_en_msg:
            return True

        # Militar activo en contexto
        if ctx.active_militar and (ctx.active_militar.get("cedula") or ctx.active_militar.get("nombre")):
            return True

        # Nombre detectado en el mensaje: solo si va con novedad, con mes o con trigger explícito de búsqueda
        tokens = _extract_name_tokens(ctx.msg_norm)
        if tokens:
            if ctx.novedad_type or ctx.mes_num:
                return True
            buscar_triggers = [
                "quien es", "buscar a", "busca a", "informacion de",
                "datos de", "que sabes de", "mostrar personal", "buscar personal",
                "sabes quien es", "dime quien es", "expediente de", "reporte de", "historial de"
            ]
            if any(t in ctx.msg_norm for t in buscar_triggers):
                return True

        return False

    def execute(self, ctx: QueryContext) -> Optional[SkillResult]:
        msg = ctx.msg_norm
        anio = ctx.anio
        mes_num = ctx.mes_num
        ranking_triggers = (
            r"\b(frecuentes?|comunes?|mas\s+presente|mas\s+tiene|mas\s+registro|"
            r"mas\s+registrada?|ranking|mayor\s+cantidad|mas\s+repetida?|mas\s+dias|"
            r"principal\s+novedad|menos\s+frecuente|menos\s+registrada?|menor|"
            r"visible|mas\s+visible|mas\s+visibles?|notable|notables?|destacada?|"
            r"destacadas?|predominante|predominantes?|relevante|relevantes?|"
            r"principal|principales)\b"
        )
        nov_kw = r"\b(novedad|novedades|permiso|permisos|vacacion|vacaciones|incapacidad|incapacidades|excusa|excusas|historial|dias|sancion|sanciones|retiro)\b"

        # Resolución unificada de fechas (mes único o rango de fechas/meses)
        date_clause: Optional[str] = None
        desc_periodo: Optional[str] = None
        if ctx.is_range and ctx.date_range:
            f_ini, f_fin = ctx.date_range
            date_clause = f"fecha_reporte >= '{f_ini}' AND fecha_reporte <= '{f_fin}'"
            desc_periodo = ctx.range_label or f"{f_ini} al {f_fin}"
        elif mes_num:
            date_clause = f"fecha_reporte LIKE '{anio}-{mes_num:02d}-%'"
            desc_periodo = f"mes {mes_num}/{anio}"

        # ------------------------------------------------------------------
        # CASO 1: CEDULA EXPLICITA EN EL MENSAJE (Máxima prioridad)
        # ------------------------------------------------------------------
        if ctx.cedula_en_msg:
            cv = ctx.cedula_en_msg

            # 1a. Cédula + ranking (con o sin período)
            if re.search(ranking_triggers, msg) or ctx.is_least:
                order = "ASC" if ctx.is_least else "DESC"
                desc_tipo = "menos frecuente" if ctx.is_least else "más frecuente"
                if date_clause:
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                            f"FROM v_novedades_detalle WHERE cedula = {cv} "
                            f"AND {date_clause} "
                            f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 20"
                        ),
                        description=f"Novedad {desc_tipo} de cédula {cv} en {desc_periodo}"
                    )
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                        f"FROM v_novedades_detalle WHERE cedula = {cv} "
                        f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 20"
                    ),
                    description=f"Novedades {desc_tipo}s de cédula {cv}"
                )

            # 1b. Cédula + tipo de novedad específico (con o sin período)
            if ctx.novedad_type:
                if date_clause:
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                            f"FROM v_novedades_detalle WHERE cedula = {cv} "
                            f"AND {_build_novedad_sql_clause(ctx.novedad_type)} "
                            f"AND {date_clause} "
                            f"ORDER BY fecha_reporte ASC"
                        ),
                        description=f"Días de {ctx.novedad_type} de cédula {cv} en {desc_periodo}"
                    )
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE cedula = {cv} "
                        f"AND {_build_novedad_sql_clause(ctx.novedad_type)} "
                        f"ORDER BY fecha_reporte DESC LIMIT 100"
                    ),
                    description=f"Historial de {ctx.novedad_type} de cédula {cv}"
                )

            # 1c. Cédula + período (mes o rango de meses)
            if date_clause:
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE cedula = {cv} "
                        f"AND {date_clause} "
                        f"ORDER BY fecha_reporte ASC"
                    ),
                    description=f"Novedades de cédula {cv} en {desc_periodo}"
                )

            # 1d. Cédula + palabras de novedades
            if re.search(nov_kw, msg):
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE cedula = {cv} "
                        f"ORDER BY fecha_reporte DESC LIMIT 100"
                    ),
                    description=f"Historial de novedades de cédula {cv}"
                )

            # 1e. Búsqueda pura de perfil por cédula
            return SkillResult(
                type="sql",
                sql=f"SELECT cedula, nombre, estado, fecha_retiro, total_novedades_historicas FROM v_personal_resumen WHERE cedula = {cv} LIMIT 5",
                description=f"Búsqueda de personal por cédula {cv}"
            )

        # ------------------------------------------------------------------
        # CASO 2: MILITAR EN CONTEXTO ACTIVO
        # ------------------------------------------------------------------
        ced = str(ctx.active_militar.get("cedula", "")) if ctx.active_militar else ""
        nom = str(ctx.active_militar.get("nombre", "")) if ctx.active_militar else ""
        if ced:
            if date_clause:
                if re.search(ranking_triggers, msg) or ctx.is_least:
                    order = "ASC" if ctx.is_least else "DESC"
                    desc_tipo = "menos frecuente" if ctx.is_least else "más frecuente"
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                            f"FROM v_novedades_detalle WHERE cedula = {ced} "
                            f"AND {date_clause} "
                            f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 20"
                        ),
                        description=f"Novedad {desc_tipo} de {nom} en {desc_periodo}"
                    )
                if ctx.novedad_type:
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                            f"FROM v_novedades_detalle WHERE cedula = {ced} "
                            f"AND {_build_novedad_sql_clause(ctx.novedad_type)} "
                            f"AND {date_clause} "
                            f"ORDER BY fecha_reporte ASC"
                        ),
                        description=f"Días de {ctx.novedad_type} de {nom} en {desc_periodo}"
                    )
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE cedula = {ced} "
                        f"AND {date_clause} "
                        f"ORDER BY fecha_reporte ASC"
                    ),
                    description=f"Novedades de {nom} en {desc_periodo}"
                )

            # Consultas conversacionales de seguimiento
            followup_kw = [
                "historial", "sus novedades", "novedad", "novedades",
                "permisos", "vacaciones", "excusas", "incapacidades",
                "frecuentes", "cuantas", "cuantos", "dias", "ausencias",
                "reportes", "su novedad", "ultima novedad",
                "menos frecuente", "menos comun", "menos registrada", "menor", "menos", "minima",
                "sobre el", "de el", "dime mas", "mas info", "mas informacion",
                "mas datos", "cuentame", "que mas", "mas detalles", "informacion",
                "datos", "perfil", "estado", "como esta", "activo", "retirado",
                "presente", "presencia", "meses", "ha estado", "aparece", "registrado"
            ]
            if any(kw in msg for kw in followup_kw):
                if re.search(ranking_triggers, msg) or ctx.is_least:
                    order = "ASC" if ctx.is_least else "DESC"
                    desc_tipo = "menos frecuente" if ctx.is_least else "más frecuente"
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                            f"FROM v_novedades_detalle WHERE cedula = {ced} "
                            f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 20"
                        ),
                        description=f"Novedades {desc_tipo}s de {nom}"
                    )

                if re.search(r"\b(en\s+que\s+meses|cuales\s+meses|que\s+meses|meses\s+present)\b", msg):
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT EXTRACT(YEAR FROM fecha_reporte::date)::int AS anio, "
                            f"EXTRACT(MONTH FROM fecha_reporte::date)::int AS mes, "
                            f"COUNT(*) AS dias_presente FROM v_novedades_detalle "
                            f"WHERE cedula = {ced} GROUP BY anio, mes ORDER BY anio, mes"
                        ),
                        description=f"Meses con presencia registrada de {nom}"
                    )

                if re.search(r"\b(estado|activo|retirado|datos|informacion)\b", msg) and not re.search(r"\b(ha\s+estado|habia\s+estado|estuvo|ha\s+sido)\b", msg):
                    return SkillResult(
                        type="sql",
                        sql=f"SELECT cedula, nombre, estado, fecha_retiro, total_novedades_historicas FROM v_personal_resumen WHERE cedula = {ced}",
                        description=f"Estado general de {nom}"
                    )

                if re.search(r"\b(en\s+que\s+mes|cual\s+mes|mes\s+con\s+mas|mes\s+con\s+mayor|mes\s+pico)\b", msg) and ctx.novedad_type:
                    nov_cond = _build_novedad_sql_clause(ctx.novedad_type)
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT EXTRACT(MONTH FROM fecha_reporte::date)::int AS mes, "
                            f"COUNT(*) AS total_dias FROM v_novedades_detalle "
                            f"WHERE cedula = {ced} AND {nov_cond} "
                            f"GROUP BY mes ORDER BY total_dias DESC LIMIT 5"
                        ),
                        description=f"Meses con mayor registro de {ctx.novedad_type} de {nom}"
                    )

                if ctx.novedad_type:
                    nov_cond = _build_novedad_sql_clause(ctx.novedad_type)
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                            f"FROM v_novedades_detalle WHERE cedula = {ced} "
                            f"AND {nov_cond} "
                            f"ORDER BY fecha_reporte DESC LIMIT 100"
                        ),
                        description=f"Historial de {ctx.novedad_type} de {nom}"
                    )

                return SkillResult(
                    type="sql",
                    sql=f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion FROM v_novedades_detalle WHERE cedula = {ced} ORDER BY fecha_reporte DESC LIMIT 100",
                    description=f"Historial de novedades de {nom}"
                )

        # ------------------------------------------------------------------
        # CASO 3: NOMBRE DE MILITAR DETECTADO EN EL MENSAJE
        # ------------------------------------------------------------------
        name_tokens = _extract_name_tokens(msg)
        if name_tokens:
            like_clauses = " AND ".join(_name_like_clause(t) for t in name_tokens[:4])
            nom_label = " ".join(name_tokens)

            # Nombre + ranking
            if re.search(ranking_triggers, msg) or ctx.is_least:
                order = "ASC" if ctx.is_least else "DESC"
                desc_tipo = "menos frecuente" if ctx.is_least else "más frecuente"
                date_filter = f"AND {date_clause}" if date_clause else ""
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                        f"FROM v_novedades_detalle WHERE {like_clauses} {date_filter} "
                        f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 20"
                    ),
                    description=f"Novedad {desc_tipo} de {nom_label}" + (f" en {desc_periodo}" if desc_periodo else "")
                )

            # Nombre + novedad + período
            if ctx.novedad_type and date_clause:
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE {like_clauses} "
                        f"AND {_build_novedad_sql_clause(ctx.novedad_type)} "
                        f"AND {date_clause} "
                        f"ORDER BY fecha_reporte ASC"
                    ),
                    description=f"Días de {ctx.novedad_type} de {nom_label} en {desc_periodo}"
                )

            # Nombre + novedad
            if ctx.novedad_type:
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE {like_clauses} "
                        f"AND {_build_novedad_sql_clause(ctx.novedad_type)} "
                        f"ORDER BY fecha_reporte DESC LIMIT 100"
                    ),
                    description=f"Historial de {ctx.novedad_type} de {nom_label}"
                )

            # Nombre + período
            if date_clause:
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE {like_clauses} "
                        f"AND {date_clause} "
                        f"ORDER BY fecha_reporte ASC"
                    ),
                    description=f"Novedades de {nom_label} en {desc_periodo}"
                )

            # Búsqueda pura de personal por nombre (solo con trigger explícito)
            buscar_triggers = [
                "quien es", "buscar a", "busca a", "informacion de",
                "datos de", "que sabes de", "mostrar personal", "buscar personal",
                "sabes quien es", "dime quien es", "expediente de", "reporte de", "historial de"
            ]
            if any(t in msg for t in buscar_triggers):
                return SkillResult(
                    type="sql",
                    sql=f"SELECT cedula, nombre, estado, fecha_retiro, total_novedades_historicas FROM v_personal_resumen WHERE {like_clauses} LIMIT 10",
                    description=f"Búsqueda de personal: {nom_label}"
                )

        return None

"""
Habilidad para consultar expedientes individuales, novedades y búsqueda de militares por cédula o nombre.
"""

import re
from typing import Optional
from app.ia.skills.base import BaseSkill, QueryContext, SkillResult
from app.ia.nlp.militar_matcher import _extract_name_tokens, _name_like_clause

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
        ranking_triggers = r"\b(frecuentes?|comunes?|mas\s+presente|mas\s+tiene|mas\s+registro|mas\s+registrada?|ranking|mayor\s+cantidad|mas\s+repetida?|mas\s+dias|principal\s+novedad|menos\s+frecuente|menos\s+registrada?|menor)\b"
        nov_kw = r"\b(novedad|novedades|permiso|permisos|vacacion|vacaciones|incapacidad|incapacidades|excusa|excusas|historial|dias|sancion|sanciones|retiro)\b"

        # ------------------------------------------------------------------
        # CASO 1: CEDULA EXPLICITA EN EL MENSAJE (Máxima prioridad)
        # ------------------------------------------------------------------
        if ctx.cedula_en_msg:
            cv = ctx.cedula_en_msg

            # 1a. Cédula + ranking (con o sin mes)
            if re.search(ranking_triggers, msg) or ctx.is_least:
                order = "ASC" if ctx.is_least else "DESC"
                desc_tipo = "menos frecuente" if ctx.is_least else "más frecuente"
                if mes_num:
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                            f"FROM v_novedades_detalle WHERE cedula = {cv} "
                            f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                            f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 10"
                        ),
                        description=f"Novedad {desc_tipo} de cédula {cv} en mes {mes_num}/{anio}"
                    )
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                        f"FROM v_novedades_detalle WHERE cedula = {cv} "
                        f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 10"
                    ),
                    description=f"Novedades {desc_tipo}s de cédula {cv}"
                )

            # 1b. Cédula + tipo de novedad específico (con o sin mes)
            if ctx.novedad_type:
                if mes_num:
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                            f"FROM v_novedades_detalle WHERE cedula = {cv} "
                            f"AND UPPER(novedad) LIKE '%{ctx.novedad_type}%' "
                            f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                            f"ORDER BY fecha_reporte ASC LIMIT 50"
                        ),
                        description=f"Días de {ctx.novedad_type} de cédula {cv} en mes {mes_num}/{anio}"
                    )
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE cedula = {cv} "
                        f"AND UPPER(novedad) LIKE '%{ctx.novedad_type}%' "
                        f"ORDER BY fecha_reporte DESC LIMIT 50"
                    ),
                    description=f"Historial de {ctx.novedad_type} de cédula {cv}"
                )

            # 1c. Cédula + mes (novedades de ese mes)
            if mes_num:
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE cedula = {cv} "
                        f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                        f"ORDER BY fecha_reporte ASC LIMIT 50"
                    ),
                    description=f"Novedades de cédula {cv} en mes {mes_num}/{anio}"
                )

            # 1d. Cédula + palabras de novedades
            if re.search(nov_kw, msg):
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE cedula = {cv} "
                        f"ORDER BY fecha_reporte DESC LIMIT 30"
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
            if mes_num:
                if re.search(ranking_triggers, msg) or ctx.is_least:
                    order = "ASC" if ctx.is_least else "DESC"
                    desc_tipo = "menos frecuente" if ctx.is_least else "más frecuente"
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                            f"FROM v_novedades_detalle WHERE cedula = {ced} "
                            f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                            f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 10"
                        ),
                        description=f"Novedad {desc_tipo} de {nom} en mes {mes_num}/{anio}"
                    )
                if ctx.novedad_type:
                    return SkillResult(
                        type="sql",
                        sql=(
                            f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                            f"FROM v_novedades_detalle WHERE cedula = {ced} "
                            f"AND UPPER(novedad) LIKE '%{ctx.novedad_type}%' "
                            f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                            f"ORDER BY fecha_reporte ASC LIMIT 50"
                        ),
                        description=f"Días de {ctx.novedad_type} de {nom} en mes {mes_num}/{anio}"
                    )
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE cedula = {ced} "
                        f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                        f"ORDER BY fecha_reporte ASC LIMIT 50"
                    ),
                    description=f"Novedades de {nom} en mes {mes_num}/{anio}"
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
                            f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 10"
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

                return SkillResult(
                    type="sql",
                    sql=f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion FROM v_novedades_detalle WHERE cedula = {ced} ORDER BY fecha_reporte DESC LIMIT 30",
                    description=f"Historial de novedades de {nom}"
                )

        # ------------------------------------------------------------------
        # CASO 3: NOMBRE DE MILITAR DETECTADO EN EL MENSAJE
        # ------------------------------------------------------------------
        name_tokens = _extract_name_tokens(msg)
        if name_tokens:
            like_clauses = " AND ".join(_name_like_clause(t) for t in name_tokens[:4])
            nom_label = " ".join(name_tokens)

            # Nombre + novedad + mes
            if ctx.novedad_type and mes_num:
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE {like_clauses} "
                        f"AND UPPER(novedad) LIKE '%{ctx.novedad_type}%' "
                        f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                        f"ORDER BY fecha_reporte ASC LIMIT 50"
                    ),
                    description=f"Días de {ctx.novedad_type} de {nom_label} en mes {mes_num}/{anio}"
                )

            # Nombre + novedad
            if ctx.novedad_type:
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE {like_clauses} "
                        f"AND UPPER(novedad) LIKE '%{ctx.novedad_type}%' "
                        f"ORDER BY fecha_reporte DESC LIMIT 50"
                    ),
                    description=f"Historial de {ctx.novedad_type} de {nom_label}"
                )

            # Nombre + mes
            if mes_num:
                return SkillResult(
                    type="sql",
                    sql=(
                        f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                        f"FROM v_novedades_detalle WHERE {like_clauses} "
                        f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                        f"ORDER BY fecha_reporte ASC LIMIT 50"
                    ),
                    description=f"Novedades de {nom_label} en mes {mes_num}/{anio}"
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

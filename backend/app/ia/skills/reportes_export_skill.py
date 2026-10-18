"""
Habilidad para generar, configurar y despachar enlaces de descarga de reportes oficiales de BIMEJ 12.
Delega el ensamblado y ordenamiento de formatos al motor desacoplado ReportDeliveryEngine.
Soporta:
  1. Base de Datos Maestra de Personal (Excel / PDF / CSV)
  2. Catálogo Oficial de Subnovedades
  3. Expedientes Individuales de Militar (Heatmap, Historial, Ágil)
  4. Reportes Detallados Diarios
  5. Reportes de Unidad / Mensuales con opciones interactivas
"""

import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.ia.skills.base import BaseSkill, QueryContext, SkillResult
from app.ia.skills.report_delivery import ReportDeliveryEngine, ReportDeliveryRequest
from app.ia.nlp.normalizer import _norm
from app.ia.nlp.militar_matcher import (
    _extract_name_tokens, _name_like_clause,
    _find_best_militar_fuzzy, _inspect_soldier_novedades,
    _extract_subnovedad_oficial, _extract_novedad_type
)
from app.ia.nlp.date_extractor import (
    _extract_report_date, _extract_month_name, _extract_month_range,
    get_month_name_from_date, check_month_has_data
)
from app.ia.prompts.guardrails import _is_conversational_inquiry

logger = logging.getLogger(__name__)

class ReportesExportSkill(BaseSkill):
    name = "reportes_export_skill"
    description = "Genera y despacha opciones de descarga para reportes oficiales (Excel, PDF, CSV, Heatmap, Parte Ágil)."

    def can_handle(self, ctx: QueryContext) -> bool:
        msg = ctx.msg_norm

        # 0. Consultas conversacionales / explicativas sobre capacidades o funcionamiento
        # Deben responderse por IA con contexto conversacional, nunca interceptarse como archivo.
        if _is_conversational_inquiry(msg):
            return False

        meta_report_patterns = [
            r"\bque\s+(mas\s+|otros?\s+)?reportes\b",
            r"\bque\s+reportes\s+(puedes|sabes|hay|tienes|haces|generas|existen|manejas)\b",
            r"\bcuales\s+(son\s+los\s+)?(reportes|formatos)\b",
            r"\bcuales\s+reportes\s+(puedes|sabes|hay|tienes|haces|generas|existen|manejas)\b",
            r"\bque\s+tipo(s)?\s+de\s+reportes\b",
            r"\bcomo\s+(funcionan|descargo|genero)\s+(los\s+)?reportes\b",
            r"\bque\s+formatos\s+(de\s+reporte\s+)?(tienes|hay|manejas|existen|haces)\b",
            r"\bque\s+puedes\s+(exportar|descargar|generar)\b",
            r"\bexplicame\s+(los\s+)?reportes\b",
            r"\bcomo\s+puedo\s+(pedir|sacar|descargar)\s+(un\s+)?reporte\b"
        ]
        if any(re.search(pat, msg) for pat in meta_report_patterns):
            return False

        report_keywords = [
            "reporte", "reportes", "informe", "informes", "descargar", "descarga",
            "exportar", "exportacion", "exporte", "generar reporte", "generar informe",
            "excel", "xlsx", "pdf", "csv", "sabana", "matriz", "heatmap", "consolidado",
            "expediente", "hoja de vida", "parte agil", "parte diario", "parte oficial",
            "agil", "historial", "historial completo", "formato agil", "formato heatmap", "formato historial"
        ]
        return any(k in msg for k in report_keywords)

    def execute(self, ctx: QueryContext) -> Optional[SkillResult]:
        msg = ctx.msg_norm
        if _is_conversational_inquiry(msg):
            return None
        user_message = ctx.user_message
        active_militar = ctx.active_militar
        db = ctx.db
        history = ctx.history
        current_year = ctx.current_year

        # 1. Determinar preferencia de formato y modo visual
        formato = "pdf" if ("pdf" in msg and not ("excel" in msg or "xlsx" in msg)) else "excel"
        modo_matriz = "colores" if any(k in msg for k in ["color", "colores", "visual"]) else ("completo" if any(k in msg for k in ["completo", "nombre"]) else "letras")

        format_preference = None
        if any(k in msg for k in ["heatmap", "matriz", "sabana", "consolidado"]):
            format_preference = "heatmap"
        elif any(k in msg for k in ["agil", "parte agil"]):
            format_preference = "agil"
        elif any(k in msg for k in ["historial", "historial completo", "expediente general"]):
            format_preference = "historial"
        elif any(k in msg for k in ["parte diario", "reporte diario"]):
            format_preference = "dia"

        is_query_export = any(k in msg for k in [
            "esa consulta", "esta consulta", "dame esa", "dame esta", "dame eso", "dame este",
            "exportar esa", "exportar esta", "la consulta", "esta tabla", "esa tabla", "exportar tabla"
        ])

        # 2. Recuperación de contexto previo desde el historial (multiturno)
        history_month = None
        history_month_range = None
        history_range_label = None
        history_date = None
        history_subnov = None
        history_cedula = None
        if history:
            for h_entry in reversed(history):
                h_text = h_entry.get("text", "") or h_entry.get("content", "") or ""
                if not h_text:
                    continue
                h_norm = _norm(h_text)
                if not history_month_range:
                    history_month_range = _extract_month_range(h_norm)
                    if history_month_range:
                        m1, m2 = history_month_range
                        nombres = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
                        history_range_label = f"{nombres[m1-1]} - {nombres[m2-1]} {current_year}"
                if not history_month and not history_month_range:
                    history_month = _extract_month_name(h_norm)
                if not history_date:
                    history_date = _extract_report_date(h_norm, h_text)
                    if history_date and not history_month and not history_month_range:
                        history_month = get_month_name_from_date(history_date)
                if not history_subnov:
                    history_subnov = _extract_subnovedad_oficial(h_norm) or _extract_novedad_type(h_norm)
                if not history_cedula:
                    c_match = re.search(r"\b(\d{6,10})\b", h_text)
                    if c_match:
                        history_cedula = int(c_match.group(1))

        # 3. Casos directos: Base de Datos Maestra y Catálogo de Subnovedades
        if any(k in msg for k in ["base de datos", "personal db", "maestro de personal", "nomina", "censo de personal", "censo completo", "todos los militares", "censo maestro"]):
            req = ReportDeliveryRequest(target_type="personal_db", formato_solicitado=formato)
            return ReportDeliveryEngine.deliver(req)

        if any(k in msg for k in ["subnovedad", "subnovedades", "catalogo de novedades", "codigos de novedad", "tabla de codigos"]):
            req = ReportDeliveryRequest(target_type="subnovedades", formato_solicitado=formato)
            return ReportDeliveryEngine.deliver(req)

        # 4. Detección de militar / expediente individual
        cedula_match = re.search(r"\b(\d{6,10})\b", user_message)
        referencia_personal = any(k in msg for k in [
            "expediente", "hoja de vida", "de el", "del militar", "del soldado",
            "este personal", "este militar", "su reporte", "sus reportes", "su historial",
            "su consolidado", "su parte", "su novedad", "sus novedades",
            "esa consulta", "esta consulta", "dame esa", "dame esta", "dame eso", "dame este",
            "exportar esa", "exportar esta", "la consulta", "de esa", "de esta", "de ese",
            "del mismo", "de este", "su expediente", "sus datos", "esta tabla", "esa tabla",
            "exportar tabla", "descargar tabla"
        ])
        is_unidad_explicit = any(t in msg for t in [
            "unidad", "batallon", "bimej", "toda la unidad", "todo el batallon",
            "general", "todos los militares", "todos los efectivos", "censo", "de todos"
        ])

        cedula_val = None
        nom_mil = None
        if cedula_match:
            cedula_val = int(cedula_match.group(1))
            nom_mil = active_militar.get("nombre") if active_militar and str(active_militar.get("cedula")) == str(cedula_val) else None
        elif active_militar and active_militar.get("cedula") and not is_unidad_explicit:
            # Preservación de contexto militar: si hay un militar activo, el reporte le pertenece a él
            cedula_val = int(active_militar.get("cedula"))
            nom_mil = active_militar.get("nombre")
        elif referencia_personal and history_cedula and not is_unidad_explicit:
            cedula_val = history_cedula
            nom_mil = active_militar.get("nombre") if active_militar else None

        is_explicit_soldier_name_request = bool(re.search(
            r"\b(reporte|informe|expediente|hoja\s+de\s+vida|historial|datos|sabana)\s+(de|del|para|sobre)\s+([a-záéíóúñ]+)",
            msg
        )) or referencia_personal

        name_tokens = _extract_name_tokens(msg)
        if not cedula_val and db and name_tokens and is_explicit_soldier_name_request:
            like_clauses = " AND ".join(_name_like_clause(t) for t in name_tokens[:4])
            try:
                cur = db.cursor()
                cur.execute(f"SELECT cedula, nombre FROM v_personal_resumen WHERE {like_clauses} LIMIT 5")
                p_rows = cur.fetchall()
                if p_rows:
                    cedula_val = int(p_rows[0][0])
                    nom_mil = p_rows[0][1]
                else:
                    cur.execute("SELECT cedula, nombre FROM v_personal_resumen")
                    all_person = cur.fetchall()
                    best_cand = _find_best_militar_fuzzy(name_tokens, all_person)
                    if best_cand:
                        cedula_val = int(best_cand[0])
                        nom_mil = best_cand[1]
                    elif is_explicit_soldier_name_request and len(name_tokens) >= 1:
                        busqueda_txt = " ".join(t.upper() for t in name_tokens)
                        info = {
                            "tipo": "no_encontrado",
                            "formato_solicitado": formato,
                            "titulo": f"Personal no encontrado: {busqueda_txt}",
                            "descripcion": f"No se encontró ningún militar registrado con el nombre o apellido '{busqueda_txt}' en BIMEJ 12.",
                            "url_excel": None,
                            "url_pdf": None,
                            "parametros": {},
                            "mensaje": (
                                f"Mi Comandante, no se encontró en los registros de BIMEJ 12 a ningún militar con el nombre o apellido '**{busqueda_txt}**'.\n\n"
                                f"Por favor verifique los apellidos o proporcione el número de cédula (ej: *'reporte de cédula 12345678'*)."
                            )
                        }
                        return SkillResult(type="conversation", answer=info["mensaje"], report_info=info)
            except Exception as e:
                logger.warning(f"[ReportesExportSkill Search] Error: {e}")

        # Subnovedad
        subnov_val = ctx.subnovedad_oficial or ctx.novedad_type or history_subnov

        # Si se identificó a un militar concreto
        if cedula_val:
            nom_mil = nom_mil or (active_militar.get("nombre") if active_militar else f"C.C. {cedula_val}")

            m_range = ctx.month_range or history_month_range
            range_label = ctx.range_label or history_range_label
            m_nombre = _extract_month_name(msg)
            if not m_nombre and not m_range:
                m_nombre = history_month or ""

            # Si hay un rango multimes activo y el usuario no pidió un mes puntual individual en este turno:
            if m_range and (not m_nombre or "-" in m_nombre):
                nombres = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
                m_nombre = f"{nombres[m_range[0]-1]} - {nombres[m_range[1]-1]}"

            pide_top_novedad = bool(re.search(
                r"\b(novedad\s+m[aá]s\s+(presente|frecuente|comun|común|reiterada)|m[aá]s\s+(presente|frecuente)|mayor\s+novedad|principal\s+novedad)\b",
                msg
            ))
            inspection = _inspect_soldier_novedades(db, cedula_val, m_nombre, subnov_val)
            if pide_top_novedad and not subnov_val:
                if inspection.get("top_novedad_mes"):
                    subnov_val = inspection["top_novedad_mes"]
                elif inspection.get("tiene_novedades_mes") and inspection.get("novedades_mes"):
                    subnov_val = max(inspection["novedades_mes"].items(), key=lambda x: x[1])[0]

            req = ReportDeliveryRequest(
                target_type="militar",
                formato_solicitado=formato,
                format_preference=format_preference,
                visual_mode=modo_matriz,
                mes=m_nombre,
                range_label=range_label,
                is_query_export=is_query_export,
                cedula=cedula_val,
                nombre=nom_mil,
                subnovedad=subnov_val,
                inspection=inspection,
                active_militar={"cedula": str(cedula_val), "nombre": nom_mil},
                current_year=current_year,
                db=db
            )
            return ReportDeliveryEngine.deliver(req)

        # 5. Detección de Fecha Puntual (Reporte Diario)
        fecha_val = _extract_report_date(msg, user_message)
        is_daily_mention = bool(fecha_val or any(k in msg for k in ["parte diario", "reporte diario", "del dia", "reporte del dia", "dia"]))
        
        # Si pide un día puntual y NO pidió un formato mensual (heatmap, agil, historial)
        if is_daily_mention and format_preference not in ["heatmap", "agil", "historial"] and not any(k in msg for k in ["consolidado", "agil", "mes", "mensual"]):
            f_target = fecha_val or datetime.now().strftime("%Y-%m-%d")
            req = ReportDeliveryRequest(
                target_type="dia",
                fecha=f_target,
                formato_solicitado=formato
            )
            return ReportDeliveryEngine.deliver(req)

        # 6. Reportes de Unidad / Mensuales
        # Si se pidió heatmap/agil/historial y antes se habló de una fecha (ej: 'hoy' o '2026-10-16'),
        # deducir automáticamente el mes de esa fecha (ej: 'OCTUBRE') en lugar de caer a 'TODOS'.
        mes_val = _extract_month_name(msg)
        if not mes_val:
            if fecha_val:
                mes_val = get_month_name_from_date(fecha_val)
            elif history_month:
                mes_val = history_month
            elif history_date:
                mes_val = get_month_name_from_date(history_date)
            else:
                mes_val = "TODOS"

        req = ReportDeliveryRequest(
            target_type="unidad",
            formato_solicitado=formato,
            format_preference=format_preference,
            visual_mode=modo_matriz,
            mes=mes_val,
            subnovedad=subnov_val,
            current_year=current_year,
            db=db
        )
        return ReportDeliveryEngine.deliver(req)

"""
Habilidad para generar, configurar y despachar enlaces de descarga de reportes oficiales de BIMEJ 12.
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
from urllib.parse import quote_plus
from typing import Optional, Dict, Any, List

from app.ia.skills.base import BaseSkill, QueryContext, SkillResult
from app.ia.nlp.normalizer import _norm
from app.ia.nlp.militar_matcher import (
    _extract_name_tokens, _name_like_clause,
    _find_best_militar_fuzzy, _inspect_soldier_novedades,
    _extract_subnovedad_oficial, _extract_novedad_type
)
from app.ia.nlp.date_extractor import _extract_report_date, _extract_month_name, check_month_has_data
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

        # Recuperación de contexto previo desde el historial si el mensaje actual es de seguimiento
        history_month = None
        history_subnov = None
        if history:
            for h_entry in reversed(history):
                h_text = h_entry.get("text", "") or h_entry.get("content", "") or ""
                if not h_text:
                    continue
                h_norm = _norm(h_text)
                if not history_month:
                    history_month = _extract_month_name(h_norm)
                if not history_subnov:
                    history_subnov = _extract_subnovedad_oficial(h_norm) or _extract_novedad_type(h_norm)
                if history_month and history_subnov:
                    break

        # Formato solicitado
        formato = "pdf" if ("pdf" in msg and not ("excel" in msg or "xlsx" in msg)) else "excel"

        # 1. Base de Datos Maestra de Personal (personal_db)
        if any(k in msg for k in ["base de datos", "personal db", "maestro de personal", "nomina", "censo de personal", "censo completo", "todos los militares", "censo maestro"]):
            info = {
                "tipo": "personal_db",
                "formato_solicitado": formato,
                "titulo": "Base de Datos Maestra de Personal BIMEJ 12",
                "descripcion": "Censo maestro de efectivos orgánicos del batallón, incluyendo cédula, grado, apellidos, nombres y estado operacional.",
                "url_excel": "/api/exportar/excel?tipo=personal_db",
                "url_pdf": "/api/exportar/pdf?tipo=personal_db",
                "url_csv": "/api/exportar/csv?tipo=personal_db",
                "parametros": {"tipo": "personal_db"},
                "mensaje": (
                    "He generado los enlaces de descarga para la **Base de Datos Maestra de Personal** de BIMEJ 12.\n\n"
                    "Contiene el censo completo de efectivos, cédulas, nombres y estado operacional. "
                    "Puede descargarlo directamente en **Excel (.xlsx)** o **PDF (.pdf)** con los botones a continuación:"
                )
            }
            return SkillResult(type="report", report_info=info, answer=info["mensaje"])

        # 2. Catálogo Oficial de Subnovedades (subnovedades)
        if any(k in msg for k in ["subnovedad", "subnovedades", "catalogo de novedades", "codigos de novedad", "tabla de codigos"]):
            info = {
                "tipo": "subnovedades",
                "formato_solicitado": formato,
                "titulo": "Catálogo Oficial de Subnovedades y Códigos Operativos",
                "descripcion": "Diccionario oficial con la totalidad de códigos de novedades, descripciones y tipos de ausentismo configurados en el sistema.",
                "url_excel": "/api/exportar/excel?tipo=subnovedades",
                "url_pdf": "/api/exportar/pdf?tipo=subnovedades",
                "url_csv": "/api/exportar/csv?tipo=subnovedades",
                "parametros": {"tipo": "subnovedades"},
                "mensaje": (
                    "He preparado la descarga del **Catálogo Oficial de Subnovedades** de BIMEJ 12.\n\n"
                    "Disponible para descarga inmediata en formato **Excel** y **PDF**:"
                )
            }
            return SkillResult(type="report", report_info=info, answer=info["mensaje"])

        # 3. Expediente Individual de Militar / Reporte por Persona (personal)
        cedula_match = re.search(r"\b(\d{6,10})\b", user_message)
        is_personal_intent = bool(cedula_match) or any(k in msg for k in [
            "expediente", "hoja de vida", "de el", "del militar", "del soldado",
            "este personal", "este militar", "su reporte", "sus reportes", "su historial",
            "su consolidado", "su parte", "su novedad", "sus novedades"
        ])
        is_personal_followup = bool(
            active_militar and active_militar.get("cedula") and 
            any(k in msg for k in ["agil", "heatmap", "matriz", "historial", "excel", "pdf"]) and
            not any(t in msg for t in ["unidad", "batallon", "del mes", "en el mes", "general", "todos"])
        )

        cedula_val = None
        nom_mil = None
        if cedula_match:
            cedula_val = int(cedula_match.group(1))
            nom_mil = active_militar.get("nombre") if active_militar and str(active_militar.get("cedula")) == str(cedula_val) else None
        elif is_personal_intent and active_militar and active_militar.get("cedula"):
            cedula_val = int(active_militar.get("cedula"))
            nom_mil = active_militar.get("nombre")
        elif is_personal_followup and active_militar and active_militar.get("cedula"):
            cedula_val = int(active_militar.get("cedula"))
            nom_mil = active_militar.get("nombre")

        is_explicit_soldier_name_request = bool(re.search(
            r"\b(reporte|informe|expediente|hoja\s+de\s+vida|historial|datos|sabana)\s+(de|del|para|sobre)\s+([a-záéíóúñ]+)",
            msg
        )) or is_personal_intent

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

        # Si se identificó a un militar concreto
        if cedula_val:
            m_nombre = _extract_month_name(msg) or history_month or ""
            subnov_val = ctx.subnovedad_oficial or ctx.novedad_type or history_subnov
            nom_mil = nom_mil or (active_militar.get("nombre") if active_militar else f"C.C. {cedula_val}")

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

            mes_query = f"&mes={m_nombre}" if m_nombre else ""
            subnov_query = f"&subnovedad={subnov_val}" if subnov_val else ""
            periodo_txt = f" para {m_nombre}" if m_nombre else " (Historial Anual / Completo)"
            filtro_subnov_txt = f" [Filtro: {subnov_val}]" if subnov_val else ""
            detected_militar = {"cedula": str(cedula_val), "nombre": nom_mil}

            tiene_nov_mes = inspection.get("tiene_novedades_mes", True)
            sin_novedades = bool(m_nombre and m_nombre.upper() != "TODOS" and not tiene_nov_mes)

            meses_sugeridos = []
            candidatos_meses = inspection.get("meses_con_filtro", []) if (subnov_val and inspection.get("meses_con_filtro")) else inspection.get("meses_con_novedades", [])
            for m in candidatos_meses[:4]:
                sub_prompt = f" filtrando {subnov_val}" if (subnov_val and inspection.get("meses_con_filtro")) else ""
                meses_sugeridos.append({
                    "mes": m["mes"],
                    "cant_dias": m["total_dias"],
                    "resumen": m.get("resumen", f"{m['total_dias']} días"),
                    "prompt": f"dame el reporte de {nom_mil} en el mes de {m['mes']}{sub_prompt}"
                })

            badge_heatmap = "HEATMAP (100% DISP)" if sin_novedades else "HEATMAP"
            badge_expediente = "EXPEDIENTE (0 NOV)" if sin_novedades else "EXPEDIENTE"
            badge_agil = "ÁGIL (0 NOV)" if sin_novedades else "ÁGIL"

            desc_heatmap = f"Matriz día a día (D, N, R){periodo_txt}. {'Personal 100% disponible (D) en este período.' if sin_novedades else ''}"
            desc_personal = f"Relación nominal de novedades{filtro_subnov_txt}. {'Aparecerá sin registros al no tener ausentismos.' if sin_novedades else ''}"
            desc_agil = f"Resumen ejecutivo de ausentismos. {'Aparecerá vacío al estar 100% disponible.' if sin_novedades else ''}"

            modo_hm = "colores" if any(k in msg for k in ["color", "colores", "visual"]) else "letras"
            tit_hm = f"Matriz Heatmap Visual por Colores{filtro_subnov_txt}" if modo_hm == "colores" else f"Matriz Heatmap (Consolidado Día a Día){filtro_subnov_txt}"

            opciones = [
                {
                    "id": "heatmap",
                    "titulo": tit_hm,
                    "descripcion": desc_heatmap,
                    "badge": badge_heatmap,
                    "tipo_export": "consolidado_mensual",
                    "url_excel": f"/api/exportar/excel?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}",
                    "url_pdf": f"/api/exportar/pdf?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}"
                },
                {
                    "id": "personal",
                    "titulo": f"Historial Completo (Expediente Cronológico){filtro_subnov_txt}",
                    "descripcion": desc_personal,
                    "badge": badge_expediente,
                    "tipo_export": "personal",
                    "url_excel": f"/api/exportar/excel?tipo=personal&cedula={cedula_val}{mes_query}{subnov_query}",
                    "url_pdf": f"/api/exportar/pdf?tipo=personal&cedula={cedula_val}{mes_query}{subnov_query}"
                },
                {
                    "id": "agil",
                    "titulo": f"Exportación Ágil (Resumen de Novedades){filtro_subnov_txt}",
                    "descripcion": desc_agil,
                    "badge": badge_agil,
                    "tipo_export": "agil",
                    "url_excel": f"/api/exportar/excel?tipo=agil&cedula={cedula_val}{mes_query}{subnov_query}",
                    "url_pdf": f"/api/exportar/pdf?tipo=agil&cedula={cedula_val}{mes_query}{subnov_query}"
                }
            ]

            if sin_novedades:
                mensaje_novedad = (
                    f"He identificado al militar **{nom_mil}** (C.C. {cedula_val}).\n\n"
                    f"⚠️ **Aviso de Ausencia de Novedades:**\n"
                    f"He identificado que este personal **no cuenta con novedades para el mes de {m_nombre}** "
                    f"(se encuentra 100% disponible en la unidad, por lo que las tablas de ausentismos aparecerán vacías).\n\n"
                )
                if inspection.get("meses_con_novedades"):
                    meses_txt = "\n".join([f"• **{m['mes']}**: {m['total_dias']} días con novedad ({m['resumen']})" for m in inspection["meses_con_novedades"][:3]])
                    mensaje_novedad += f"💡 Registra novedades en los meses de:\n{meses_txt}\n\nPuede pulsar cualquiera de los accesos a continuación:"
            else:
                subnov_msg = f"\n• Subnovedad filtrada: **{subnov_val}**" if subnov_val else ""
                mensaje_novedad = (
                    f"He identificado al militar **{nom_mil}** (C.C. {cedula_val}).\n\n"
                    f"• Período: **{m_nombre or 'Todo el año / Historial completo'}**{subnov_msg}\n\n"
                    f"Para este integrante tiene a su disposición 3 formatos oficiales de reporte. "
                    f"Seleccione la modalidad que desea generar:"
                )

            info = {
                "tipo": "seleccion_reporte_personal",
                "formato_solicitado": formato,
                "titulo": f"Reportes Oficiales: {nom_mil}{filtro_subnov_txt}",
                "descripcion": f"Personal identificado: {nom_mil} (C.C. {cedula_val}){periodo_txt}{filtro_subnov_txt}.",
                "url_excel": f"/api/exportar/excel?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}",
                "url_pdf": f"/api/exportar/pdf?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}",
                "parametros": {"cedula": cedula_val, "mes": m_nombre or "TODOS", "subnovedad": subnov_val},
                "active_militar": detected_militar,
                "opciones": opciones,
                "sin_novedades": sin_novedades,
                "meses_sugeridos": meses_sugeridos,
                "mensaje": mensaje_novedad
            }
            return SkillResult(type="report", report_info=info, answer=mensaje_novedad, active_militar=detected_militar)

        # 4. Reporte Detallado Diario (dia)
        fecha_val = _extract_report_date(msg, user_message)
        if (fecha_val or any(k in msg for k in ["parte diario", "reporte diario", "del dia", "reporte del dia", "dia"])) and not any(k in msg for k in ["consolidado", "agil", "mes", "mensual"]):
            f_target = fecha_val or datetime.now().strftime("%Y-%m-%d")
            info = {
                "tipo": "dia",
                "formato_solicitado": formato,
                "titulo": f"Reporte Detallado de Personal - Día {f_target}",
                "descripcion": f"Relación nominal de todo el personal de la unidad militar con detalle de novedades para {f_target}.",
                "url_excel": f"/api/exportar/excel?tipo=dia&fecha={f_target}",
                "url_pdf": f"/api/exportar/pdf?tipo=dia&fecha={f_target}",
                "parametros": {"fecha": f_target},
                "mensaje": f"He preparado el **Reporte Detallado Diario** para el **{f_target}**."
            }
            return SkillResult(type="report", report_info=info, answer=info["mensaje"])

        # 5. Reportes Oficiales de Unidad / Mensuales
        mes_val = _extract_month_name(msg) or history_month or "TODOS"
        subnov_val = ctx.subnovedad_oficial or ctx.novedad_type or history_subnov

        if mes_val != "TODOS" and db and not check_month_has_data(mes_val, db):
            try:
                from app.database import get_available_date_range
                r_range = get_available_date_range(db)
                nov_txt = f" con novedad de {subnov_val}" if subnov_val else ""
                info = {
                    "tipo": "no_encontrado",
                    "mensaje": (
                        f"⚠️ **Aviso de Período No Disponible:**\n\n"
                        f"En la base de datos de BIMEJ 12 **no se registran reportes diarios para el mes de {mes_val}**.\n\n"
                        f"El sistema actualmente cuenta con reportes diarios cargados para el período de **{r_range['texto']}**.\n\n"
                        f"💡 Puede solicitar el reporte{nov_txt} para **{r_range['max_month']}** o para **TODO EL AÑO**."
                    )
                }
                return SkillResult(type="conversation", answer=info["mensaje"], report_info=info)
            except Exception:
                pass

        modo_matriz = "colores" if any(k in msg for k in ["color", "colores", "visual"]) else ("completo" if any(k in msg for k in ["completo", "nombre"]) else "letras")
        subnov_query = f"&subnovedad={quote_plus(subnov_val)}" if subnov_val else ""
        filtro_subnov_txt = f" (Filtro: {subnov_val})" if subnov_val else ""
        filtro_subnov_desc = f" con filtro aplicado a la novedad '{subnov_val}'" if subnov_val else ""
        titulo_mes = f"Año Completo {current_year}" if mes_val == "TODOS" else mes_val.upper()

        tit_hm = f"Matriz Heatmap Visual por Colores{filtro_subnov_txt}" if modo_matriz == "colores" else f"Matriz Heatmap (Consolidado Día a Día){filtro_subnov_txt}"

        opc_heatmap = {
            "id": "heatmap",
            "titulo": tit_hm,
            "descripcion": f"Matriz integral de la unidad con la operatividad día a día (D, N, R) de cada integrante{filtro_subnov_desc}.",
            "badge": "MATRIZ HEATMAP",
            "tipo_export": "consolidado_mensual",
            "url_excel": f"/api/exportar/excel?tipo=consolidado_mensual&mes={mes_val}&modo={modo_matriz}{subnov_query}",
            "url_pdf": f"/api/exportar/pdf?tipo=consolidado_mensual&mes={mes_val}&modo={modo_matriz}{subnov_query}"
        }

        opc_agil = {
            "id": "agil",
            "titulo": f"Parte Ágil de Novedades{filtro_subnov_txt}",
            "descripcion": f"Resumen ejecutivo nominal agrupado por rangos cronológicos de ausentismos para {titulo_mes}.",
            "badge": "PARTE ÁGIL",
            "tipo_export": "agil",
            "url_excel": f"/api/exportar/excel?tipo=agil&mes={mes_val}{subnov_query}",
            "url_pdf": f"/api/exportar/pdf?tipo=agil&mes={mes_val}{subnov_query}"
        }

        opc_historial = {
            "id": "historial",
            "titulo": f"Historial Completo de Novedades{filtro_subnov_txt}",
            "descripcion": f"Relación nominal detallada con fecha de reporte, inicio y término{filtro_subnov_desc}.",
            "badge": "HISTORIAL DETALLADO",
            "tipo_export": "historial_novedades",
            "url_excel": f"/api/exportar/excel?tipo=historial_novedades&mes={mes_val}{subnov_query}",
            "url_pdf": f"/api/exportar/pdf?tipo=historial_novedades&mes={mes_val}{subnov_query}"
        }

        if any(k in msg for k in ["agil", "parte agil"]):
            opciones = [opc_agil, opc_heatmap, opc_historial]
            primary_excel = opc_agil["url_excel"]
            primary_pdf = opc_agil["url_pdf"]
            mensaje = f"He preparado el **Parte Ágil de Novedades** para el período **{titulo_mes}**{filtro_subnov_txt}."
        elif any(k in msg for k in ["historial", "historial completo", "expediente general"]):
            opciones = [opc_historial, opc_heatmap, opc_agil]
            primary_excel = opc_historial["url_excel"]
            primary_pdf = opc_historial["url_pdf"]
            mensaje = f"He preparado el **Historial Completo de Novedades** para el período **{titulo_mes}**{filtro_subnov_txt}."
        else:
            opciones = [opc_heatmap, opc_agil, opc_historial]
            primary_excel = opc_heatmap["url_excel"]
            primary_pdf = opc_heatmap["url_pdf"]
            mensaje = (
                f"He preparado los reportes oficiales de la unidad para el período **{titulo_mes}**{filtro_subnov_txt}.\n\n"
                f"Para este período tiene a su disposición los **3 formatos oficiales de reporte** del sistema BIMEJ 12."
            )

        info = {
            "tipo": "seleccion_reporte_unidad",
            "formato_solicitado": formato,
            "titulo": f"Reportes Oficiales de la Unidad - {titulo_mes}{filtro_subnov_txt}",
            "descripcion": f"Consolidado de novedades y operatividad para la unidad militar en {titulo_mes}.",
            "url_excel": primary_excel,
            "url_pdf": primary_pdf,
            "parametros": {"mes": mes_val, "modo": modo_matriz, "subnovedad": subnov_val},
            "opciones": opciones,
            "mensaje": mensaje
        }
        return SkillResult(type="report", report_info=info, answer=mensaje)

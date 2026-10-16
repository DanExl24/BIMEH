"""
Motor General de Formatos de Entrega de Reportes (ReportDeliveryEngine).

Desacopla la lógica de negocio y de consulta de los formatos de entrega de archivos (Excel, PDF, CSV).
Estructura y prioriza dinámicamente las opciones oficiales de reporte:
  1. Matriz Heatmap (Consolidado Día a Día)
  2. Parte Ágil de Novedades
  3. Historial Detallado de Novedades
  4. Reporte Detallado Diario
  5. Censo Maestro de Personal
  6. Catálogo Oficial de Subnovedades
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import quote_plus

from app.ia.skills.base import SkillResult
from app.ia.nlp.date_extractor import check_month_has_data

@dataclass
class ReportDeliveryRequest:
    target_type: str  # "unidad" | "militar" | "dia" | "personal_db" | "subnovedades"
    formato_solicitado: str = "excel"  # "excel" | "pdf" | "csv"
    format_preference: Optional[str] = None  # "heatmap" | "agil" | "historial" | "dia"
    visual_mode: str = "letras"  # "letras" | "colores" | "completo"
    
    # Parámetros temporales
    mes: Optional[str] = None  # "ENERO" .. "DICIEMBRE", "TODOS"
    fecha: Optional[str] = None  # "YYYY-MM-DD"
    range_label: Optional[str] = None
    is_query_export: bool = False
    current_year: int = 2026
    
    # Parámetros de personal
    cedula: Optional[int] = None
    nombre: Optional[str] = None
    active_militar: Optional[Dict[str, Any]] = None
    
    # Filtro opcional
    subnovedad: Optional[str] = None
    
    # Inspección de novedades (soldado)
    inspection: Optional[Dict[str, Any]] = None
    
    # Conexión opcional a base de datos
    db: Any = None


class ReportDeliveryEngine:
    """
    Motor centralizado de formatos de entrega.
    Ensambla las tarjetas reactivas, URLs de descarga y textos descriptivos oficiales.
    """

    @classmethod
    def deliver(cls, req: ReportDeliveryRequest) -> SkillResult:
        if req.target_type == "personal_db":
            return cls._deliver_personal_db(req)
        elif req.target_type == "subnovedades":
            return cls._deliver_subnovedades(req)
        elif req.target_type == "dia":
            return cls._deliver_dia(req)
        elif req.target_type == "militar":
            return cls._deliver_militar(req)
        else:
            return cls._deliver_unidad(req)

    # -------------------------------------------------------------------------
    # 1. Base de Datos Maestra de Personal (personal_db)
    # -------------------------------------------------------------------------
    @classmethod
    def _deliver_personal_db(cls, req: ReportDeliveryRequest) -> SkillResult:
        info = {
            "tipo": "personal_db",
            "formato_solicitado": req.formato_solicitado,
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

    # -------------------------------------------------------------------------
    # 2. Catálogo Oficial de Subnovedades
    # -------------------------------------------------------------------------
    @classmethod
    def _deliver_subnovedades(cls, req: ReportDeliveryRequest) -> SkillResult:
        info = {
            "tipo": "subnovedades",
            "formato_solicitado": req.formato_solicitado,
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

    # -------------------------------------------------------------------------
    # 3. Reporte Detallado Diario
    # -------------------------------------------------------------------------
    @classmethod
    def _deliver_dia(cls, req: ReportDeliveryRequest) -> SkillResult:
        f_target = req.fecha or datetime.now().strftime("%Y-%m-%d")
        info = {
            "tipo": "dia",
            "formato_solicitado": req.formato_solicitado,
            "titulo": f"Reporte Detallado de Personal - Día {f_target}",
            "descripcion": f"Relación nominal de todo el personal de la unidad militar con detalle de novedades para {f_target}.",
            "url_excel": f"/api/exportar/excel?tipo=dia&fecha={f_target}",
            "url_pdf": f"/api/exportar/pdf?tipo=dia&fecha={f_target}",
            "parametros": {"fecha": f_target},
            "mensaje": (
                f"He preparado el **Reporte Detallado Diario** para el **{f_target}**.\n\n"
                f"Contiene la relación nominal de todo el personal con novedad y disponible en dicha jornada:"
            )
        }
        return SkillResult(type="report", report_info=info, answer=info["mensaje"])

    # -------------------------------------------------------------------------
    # 4. Expediente Individual de Militar (Personal)
    # -------------------------------------------------------------------------
    @classmethod
    def _deliver_militar(cls, req: ReportDeliveryRequest) -> SkillResult:
        cedula_val = req.cedula
        nom_mil = req.nombre or (req.active_militar.get("nombre") if req.active_militar else f"C.C. {cedula_val}")
        m_nombre = req.mes or ""
        subnov_val = req.subnovedad
        modo_hm = req.visual_mode
        pref = req.format_preference

        mes_query = f"&mes={m_nombre}" if m_nombre else ""
        subnov_query = f"&subnovedad={quote_plus(subnov_val)}" if subnov_val else ""
        filtro_subnov_txt = f" [Filtro: {subnov_val}]" if subnov_val else ""
        range_lbl = getattr(req, "range_label", None)
        if range_lbl:
            periodo_txt = f" para el período {range_lbl}"
        elif m_nombre:
            periodo_txt = f" para el mes de {m_nombre}"
        else:
            periodo_txt = " (historial completo)"

        # Opciones disponibles para militar
        desc_hm = f"Operatividad día a día (D, N, R) de {nom_mil}{periodo_txt} con codificación oficial."
        desc_personal = f"Bitácora histórica con fechas de inicio, término y descripciones de novedades para {nom_mil}."
        desc_agil = f"Extracto ejecutivo de ausentismos y novedades agrupadas por intervalos para {nom_mil}."

        badge_heatmap = "MATRIZ HEATMAP"
        badge_expediente = "EXPEDIENTE CRONOLÓGICO"
        badge_agil = "PARTE ÁGIL"

        opc_heatmap = {
            "id": "heatmap",
            "titulo": f"Matriz Heatmap Individual{filtro_subnov_txt}",
            "descripcion": desc_hm,
            "badge": badge_heatmap,
            "tipo_export": "consolidado_mensual",
            "url_excel": f"/api/exportar/excel?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}",
            "url_pdf": f"/api/exportar/pdf?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}"
        }

        opc_personal = {
            "id": "personal",
            "titulo": f"Historial Completo (Expediente Cronológico){filtro_subnov_txt}",
            "descripcion": desc_personal,
            "badge": badge_expediente,
            "tipo_export": "personal",
            "url_excel": f"/api/exportar/excel?tipo=personal&cedula={cedula_val}{mes_query}{subnov_query}",
            "url_pdf": f"/api/exportar/pdf?tipo=personal&cedula={cedula_val}{mes_query}{subnov_query}"
        }

        opc_agil = {
            "id": "agil",
            "titulo": f"Exportación Ágil (Resumen de Novedades){filtro_subnov_txt}",
            "descripcion": desc_agil,
            "badge": badge_agil,
            "tipo_export": "agil",
            "url_excel": f"/api/exportar/excel?tipo=agil&cedula={cedula_val}{mes_query}{subnov_query}",
            "url_pdf": f"/api/exportar/pdf?tipo=agil&cedula={cedula_val}{mes_query}{subnov_query}"
        }

        # Ordenamiento dinámico según preferencia
        if pref == "agil":
            opciones = [opc_agil, opc_heatmap, opc_personal]
        elif pref == "heatmap":
            opciones = [opc_heatmap, opc_personal, opc_agil]
        elif pref == "historial":
            opciones = [opc_personal, opc_heatmap, opc_agil]
        else:
            opciones = [opc_heatmap, opc_personal, opc_agil]

        inspection = req.inspection or {}
        sin_novedades = inspection.get("sin_novedades", False)
        meses_sugeridos = [m["mes"] for m in inspection.get("meses_con_novedades", [])]

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
            periodo_display = range_lbl or m_nombre or 'Todo el año / Historial completo'
            nota_consulta = ""
            if getattr(req, "is_query_export", False):
                nota_consulta = (
                    "\n\n💡 *Tip de exportación de consulta:* Para exportar directamente la tabla con los "
                    "registros resumidos de la consulta en pantalla (por ejemplo, el ranking o resumen), "
                    "puede pulsar el botón **'Ver a detalle'** en el mensaje anterior y hacer clic en **Excel (.xlsx)** o **PDF (.pdf)**."
                )
            mensaje_novedad = (
                f"He preparado los reportes oficiales para **{nom_mil}** (C.C. {cedula_val}).\n\n"
                f"• Período: **{periodo_display}**{subnov_msg}\n\n"
                f"Para este integrante tiene a su disposición los 3 formatos oficiales de reporte del BIMEJ 12. "
                f"Seleccione la modalidad que desea generar:{nota_consulta}"
            )

        detected_militar = {"cedula": cedula_val, "nombre": nom_mil}
        primary_excel = opciones[0]["url_excel"]
        primary_pdf = opciones[0]["url_pdf"]

        info = {
            "tipo": "seleccion_reporte_personal",
            "formato_solicitado": req.formato_solicitado,
            "titulo": f"Reportes Oficiales: {nom_mil}{filtro_subnov_txt}",
            "descripcion": f"Personal identificado: {nom_mil} (C.C. {cedula_val}){periodo_txt}{filtro_subnov_txt}.",
            "url_excel": primary_excel,
            "url_pdf": primary_pdf,
            "parametros": {"cedula": cedula_val, "mes": m_nombre or "TODOS", "subnovedad": subnov_val},
            "active_militar": detected_militar,
            "opciones": opciones,
            "sin_novedades": sin_novedades,
            "meses_sugeridos": meses_sugeridos,
            "mensaje": mensaje_novedad
        }
        return SkillResult(type="report", report_info=info, answer=mensaje_novedad, active_militar=detected_militar)

    # -------------------------------------------------------------------------
    # 5. Reportes Oficiales de Unidad / Mensuales
    # -------------------------------------------------------------------------
    @classmethod
    def _deliver_unidad(cls, req: ReportDeliveryRequest) -> SkillResult:
        mes_val = req.mes or "TODOS"
        subnov_val = req.subnovedad
        modo_matriz = req.visual_mode
        pref = req.format_preference

        # Validación de datos en el mes
        if mes_val != "TODOS" and req.db and not check_month_has_data(mes_val, req.db):
            try:
                from app.database import get_available_date_range
                r_range = get_available_date_range(req.db)
                nov_txt = f" con novedad de {subnov_val}" if subnov_val else ""
                info = {
                    "tipo": "no_encontrado",
                    "mensaje": (
                        f"⚠️ **Aviso de Período No Disponible:**\n\n"
                        f"En la base de datos de BIMEJ 12 **no se registran reportes diarios para el mes de {mes_val}**.\n\n"
                        f"El sistema actualmente cuenta con reportes diarios cargados para el período de **{r_range['texto']}** "
                        f"(los meses posteriores aún no han sido sincronizados en la base de datos).\n\n"
                        f"💡 Si lo desea, puede solicitar el reporte{nov_txt} para uno de los meses "
                        f"con información registrada (por ejemplo: **{r_range['max_month']}**), o para **TODO EL AÑO**."
                    )
                }
                return SkillResult(type="conversation", answer=info["mensaje"], report_info=info)
            except Exception:
                pass

        subnov_query = f"&subnovedad={quote_plus(subnov_val)}" if subnov_val else ""
        filtro_subnov_txt = f" (Filtro: {subnov_val})" if subnov_val else ""
        filtro_subnov_desc = f" con filtro aplicado a la novedad '{subnov_val}'" if subnov_val else ""
        titulo_mes = f"Año Completo {req.current_year}" if mes_val == "TODOS" else mes_val.upper()

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
            "descripcion": f"Resumen ejecutivo nominal agrupado por rangos cronológicos de ausentismos y novedades oficiales para {titulo_mes}.",
            "badge": "PARTE ÁGIL",
            "tipo_export": "agil",
            "url_excel": f"/api/exportar/excel?tipo=agil&mes={mes_val}{subnov_query}",
            "url_pdf": f"/api/exportar/pdf?tipo=agil&mes={mes_val}{subnov_query}"
        }

        opc_historial = {
            "id": "historial",
            "titulo": f"Historial Completo de Novedades{filtro_subnov_txt}",
            "descripcion": f"Relación nominal detallada con fecha de reporte, inicio, término y descripción oficial de novedades{filtro_subnov_desc}.",
            "badge": "HISTORIAL DETALLADO",
            "tipo_export": "historial_novedades",
            "url_excel": f"/api/exportar/excel?tipo=historial_novedades&mes={mes_val}{subnov_query}",
            "url_pdf": f"/api/exportar/pdf?tipo=historial_novedades&mes={mes_val}{subnov_query}"
        }

        if pref == "agil":
            opciones = [opc_agil, opc_heatmap, opc_historial]
            primary_excel = opc_agil["url_excel"]
            primary_pdf = opc_agil["url_pdf"]
            mensaje = (
                f"He preparado el **Parte Ágil de Novedades** para el período **{titulo_mes}**{filtro_subnov_txt}.\n\n"
                f"Agrupa los ausentismos por intervalos de fechas con sus justificaciones oficiales.\n"
                f"A continuación tiene disponible la descarga directa en Excel y PDF, junto a los otros 2 formatos oficiales de la unidad:"
            )
        elif pref == "historial":
            opciones = [opc_historial, opc_heatmap, opc_agil]
            primary_excel = opc_historial["url_excel"]
            primary_pdf = opc_historial["url_pdf"]
            mensaje = (
                f"He preparado el **Historial Completo de Novedades** para el período **{titulo_mes}**{filtro_subnov_txt}.\n\n"
                f"Contiene la relación detallada de novedades registradas con sus fechas de vigencia y observaciones.\n"
                f"A continuación puede descargarlo en Excel o PDF, o seleccionar cualquiera de los otros formatos disponibles:"
            )
        elif pref == "heatmap":
            opciones = [opc_heatmap, opc_agil, opc_historial]
            primary_excel = opc_heatmap["url_excel"]
            primary_pdf = opc_heatmap["url_pdf"]
            mensaje = (
                f"He preparado la **Matriz Heatmap (Consolidado Mensual)** para **{titulo_mes}**{filtro_subnov_txt}.\n\n"
                f"Refleja la operatividad día a día (D, N, R) de cada efectivo orgánico del batallón.\n"
                f"Puede descargarlo directamente con los botones inferiores o consultar los formatos Ágil e Historial Completo:"
            )
        else:
            opciones = [opc_heatmap, opc_agil, opc_historial]
            primary_excel = opc_heatmap["url_excel"]
            primary_pdf = opc_heatmap["url_pdf"]
            mensaje = (
                f"He preparado los reportes oficiales de la unidad para el período **{titulo_mes}**{filtro_subnov_txt}.\n\n"
                f"Para este período tiene a su disposición los **3 formatos oficiales de reporte** del sistema BIMEJ 12.\n"
                f"Puede descargar cualquiera de ellos directamente en **Excel (.xlsx)** o **PDF (.pdf)** con los botones a continuación:"
            )

        info = {
            "tipo": "seleccion_reporte_unidad",
            "formato_solicitado": req.formato_solicitado,
            "titulo": f"Reportes Oficiales de la Unidad - {titulo_mes}{filtro_subnov_txt}",
            "descripcion": f"Consolidado de novedades y operatividad para la unidad militar en {titulo_mes}{filtro_subnov_desc}.",
            "url_excel": primary_excel,
            "url_pdf": primary_pdf,
            "parametros": {"mes": mes_val, "modo": modo_matriz, "subnovedad": subnov_val},
            "opciones": opciones,
            "mensaje": mensaje
        }
        return SkillResult(type="report", report_info=info, answer=mensaje)

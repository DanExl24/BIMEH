"""
Módulo Fachada (Facade) para retrocompatibilidad con app.services.query_catalog.
Redirige todas las llamadas al nuevo paquete modular app.ia.
"""

from typing import Optional, Tuple, Dict, Any, List

from app.ia.nlp.normalizer import _norm
from app.ia.nlp.date_extractor import (
    MESES_ES,
    MESES_STR_MAP,
    _extract_month,
    _extract_month_name,
    _extract_year,
    _extract_day_range,
    _extract_report_date,
    check_month_has_data,
)
from app.ia.nlp.militar_matcher import (
    NOVEDADES_MAP,
    MAPA_SUBNOVEDADES_OFICIAL,
    _extract_subnovedad_oficial,
    _extract_novedad_type,
    _extract_name_tokens,
    _name_like_clause,
    _find_best_militar_fuzzy,
    _inspect_soldier_novedades,
    _is_least_frequent,
)
from app.ia.prompts.guardrails import _is_conversational_inquiry
from app.ia.skills import build_default_skill_registry, QueryContext
from app.ia.skills.reportes_export_skill import ReportesExportSkill

_registry = build_default_skill_registry()
_report_skill = ReportesExportSkill()

def match_catalog(
    user_message: str,
    active_militar: Optional[Dict[str, Any]] = None,
    current_year: Optional[int] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Fachada retrocompatible de match_catalog.
    Evalúa la consulta contra el SkillRegistry y retorna (sql, descripcion) si hay coincidencia.
    """
    if not user_message:
        return None, None

    ctx = QueryContext(
        user_message=user_message,
        active_militar=active_militar,
        current_year=current_year or 2026
    )
    result = _registry.dispatch(ctx)
    if result and result.type == "sql" and result.sql:
        return result.sql, result.description

    return None, None

def match_report_request(
    user_message: str,
    active_militar: Optional[Dict[str, Any]] = None,
    current_year: int = 2026,
    force_report_mode: bool = False,
    db: Optional[Any] = None,
    history: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Fachada retrocompatible de match_report_request.
    Delega en ReportesExportSkill para generar enlaces de descarga oficiales.
    """
    ctx = QueryContext(
        user_message=user_message,
        active_militar=active_militar,
        current_year=current_year,
        db=db,
        history=history
    )
    if _is_conversational_inquiry(ctx.msg_norm):
        return None
    if force_report_mode or _report_skill.can_handle(ctx):
        res = _report_skill.execute(ctx)
        if res and res.report_info:
            return res.report_info
    return None

__all__ = [
    "_norm",
    "MESES_ES",
    "MESES_STR_MAP",
    "NOVEDADES_MAP",
    "MAPA_SUBNOVEDADES_OFICIAL",
    "_extract_subnovedad_oficial",
    "_find_best_militar_fuzzy",
    "_extract_month",
    "_extract_year",
    "_extract_day_range",
    "_extract_novedad_type",
    "_extract_name_tokens",
    "_name_like_clause",
    "_is_least_frequent",
    "match_catalog",
    "_extract_month_name",
    "_extract_report_date",
    "_inspect_soldier_novedades",
    "_is_conversational_inquiry",
    "match_report_request",
    "check_month_has_data",
]

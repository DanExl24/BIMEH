"""
Módulo de Procesamiento de Lenguaje Natural (NLP) y Normalización en Español.
"""

from app.ia.nlp.normalizer import _norm
from app.ia.nlp.date_extractor import (
    MESES_ES,
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

__all__ = [
    "_norm",
    "MESES_ES",
    "_extract_month",
    "_extract_month_name",
    "_extract_year",
    "_extract_day_range",
    "_extract_report_date",
    "check_month_has_data",
    "NOVEDADES_MAP",
    "MAPA_SUBNOVEDADES_OFICIAL",
    "_extract_subnovedad_oficial",
    "_extract_novedad_type",
    "_extract_name_tokens",
    "_name_like_clause",
    "_find_best_militar_fuzzy",
    "_inspect_soldier_novedades",
    "_is_least_frequent",
]

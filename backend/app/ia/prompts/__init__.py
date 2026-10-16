"""
Repositorio centralizado de System Prompts, Guardrails y Plantillas Doctrinales de BIMEH.
"""

from app.ia.prompts.system_prompts import DATABASE_SCHEMA_CONTEXT, build_system_prompt
from app.ia.prompts.guardrails import (
    REFUSAL_PHRASES,
    REFUSAL_MESSAGE,
    is_query_in_domain,
    _is_refusal,
    _is_conversational_inquiry,
    get_fast_conversational_reply,
    _auto_synthesize,
)
from app.ia.prompts.report_templates import (
    APRECIACION_SYSTEM_PROMPT,
    REPORT_SYSTEM_PROMPT,
    build_apreciacion_prompt,
    build_report_prompt,
)

__all__ = [
    "DATABASE_SCHEMA_CONTEXT",
    "build_system_prompt",
    "REFUSAL_PHRASES",
    "REFUSAL_MESSAGE",
    "is_query_in_domain",
    "_is_refusal",
    "_is_conversational_inquiry",
    "get_fast_conversational_reply",
    "_auto_synthesize",
    "APRECIACION_SYSTEM_PROMPT",
    "REPORT_SYSTEM_PROMPT",
    "build_apreciacion_prompt",
    "build_report_prompt",
]

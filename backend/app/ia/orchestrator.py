"""
Orquestador central del subsistema de Inteligencia Artificial Militar de BIMEH.
Coordina:
  1. Confinamiento temático y guardrails de dominio.
  2. Respuestas conversacionales ultrarrápidas (<5ms).
  3. Despacho modular mediante SkillRegistry (Fast-Path determinista).
  4. Generación sintética de SQL mediante LLM Provider (Slow-Path).
  5. Ejecución segura en PostgreSQL y síntesis de respuestas castrenses.
"""

import re
import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from app.ia.config import get_current_config
from app.ia.nlp.normalizer import _norm
from app.ia.prompts.system_prompts import build_system_prompt
from app.ia.prompts.guardrails import (
    REFUSAL_MESSAGE,
    is_query_in_domain,
    get_fast_conversational_reply,
    _auto_synthesize,
    _is_refusal,
)
from app.ia.skills import build_default_skill_registry, QueryContext, SkillResult
from app.ia.providers import get_llm_provider
from app.ia.sql.validator import is_sql_safe, validate_sql
from app.ia.sql.executor import execute_safe_query

logger = logging.getLogger(__name__)

class IAOrchestrator:
    """Orquestador principal de analítica conversacional militar."""

    def __init__(self):
        self.skill_registry = build_default_skill_registry()

    def process_query(
        self,
        user_message: str,
        db: Any,
        history: Optional[List[Dict[str, Any]]] = None,
        active_militar: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        mode: str = "chat",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa una consulta en lenguaje natural con total conciencia de contexto.
        """
        now = datetime.now()
        force_report = (mode == "report")

        # Inyectar militar y periodo desde context si no vinieron explícitos
        if not active_militar and context and context.get("active_militar"):
            active_militar = context.get("active_militar")

        ctx_period = (context.get("active_period") or {}) if context else {}
        llm_provider, backend_name = get_llm_provider()
        active_model = model or get_current_config().get("gemini_model" if backend_name == "gemini" else "ollama_model")
        model_label = f"{backend_name} ({active_model})"

        # ------------------------------------------------------------------
        # PASO 1: GUARDRAILS DE CONFINAMIENTO TEMÁTICO MILITAR
        # ------------------------------------------------------------------
        if not is_query_in_domain(user_message):
            logger.info(f"[IAOrchestrator] Consulta fuera de dominio militar: '{user_message}'")
            return {
                "type": "conversation",
                "answer": REFUSAL_MESSAGE,
                "sql": None,
                "columns": [],
                "rows": [],
                "total_records": 0,
                "model": model_label,
                "active_militar": active_militar,
                "detected_entities": {"militar": active_militar, "period": ctx_period}
            }

        # ------------------------------------------------------------------
        # PASO 2: RESPUESTAS CONVERSACIONALES ULTRARRÁPIDAS (<5ms)
        # ------------------------------------------------------------------
        fast_reply_tuple = get_fast_conversational_reply(user_message)
        if fast_reply_tuple and not force_report:
            conv_tipo, fast_reply = fast_reply_tuple
            return {
                "type": "conversation",
                "answer": fast_reply,
                "sql": None,
                "columns": [],
                "rows": [],
                "total_records": 0,
                "model": f"{backend_name} (fast-reply)",
                "active_militar": active_militar,
                "detected_entities": {"militar": active_militar, "period": ctx_period}
            }

        # ------------------------------------------------------------------
        # PASO 3: FAST-PATH MEDIANTE SKILL REGISTRY
        # ------------------------------------------------------------------
        q_ctx = QueryContext(
            user_message=user_message,
            active_militar=active_militar,
            context=context,
            current_year=now.year,
            db=db,
            history=history
        )

        skill_result: Optional[SkillResult] = self.skill_registry.dispatch(q_ctx)

        if skill_result:
            # Caso 3a: El skill resolvió un reporte interactivo
            if skill_result.type == "report":
                updated_militar = skill_result.active_militar or active_militar
                return {
                    "type": "report",
                    "answer": skill_result.answer,
                    "report_info": skill_result.report_info,
                    "sql": None,
                    "columns": [],
                    "rows": [],
                    "total_records": 0,
                    "model": f"{model_label} (reporte)",
                    "active_militar": updated_militar,
                    "detected_entities": {"militar": updated_militar, "period": ctx_period}
                }

            # Caso 3b: El skill resolvió una conversación o mensaje explicativo
            if skill_result.type == "conversation":
                return {
                    "type": "conversation",
                    "answer": skill_result.answer,
                    "report_info": skill_result.report_info,
                    "sql": None,
                    "columns": [],
                    "rows": [],
                    "total_records": 0,
                    "model": model_label,
                    "active_militar": active_militar,
                    "detected_entities": {"militar": active_militar, "period": ctx_period}
                }

            # Caso 3c: El skill generó una sentencia SQL determinista
            if skill_result.type == "sql" and skill_result.sql:
                sql_to_run = skill_result.sql
                try:
                    cols, rows = execute_safe_query(db, sql_to_run)
                    query_result = {"columns": cols, "rows": rows, "total": len(rows)}
                    
                    # Síntesis del resultado
                    if query_result["total"] == 0 or query_result["total"] <= 5:
                        synthesis = _auto_synthesize(user_message, query_result, db=db)
                    else:
                        try:
                            synthesis = llm_provider.generate_text(
                                prompt=(
                                    f"Asistente Militar BIMEJ 12.\nUsuario: \"{user_message}\"\n"
                                    f"Resultados ({query_result['total']} registros): {json.dumps(query_result['rows'][:8], ensure_ascii=False)}\n"
                                    f"Redacta resumen militar claro en 2 oraciones."
                                ),
                                temperature=0.2,
                                max_tokens=150,
                                model=active_model
                            )
                            if _is_refusal(synthesis):
                                synthesis = _auto_synthesize(user_message, query_result, db=db)
                        except Exception:
                            synthesis = _auto_synthesize(user_message, query_result, db=db)

                    # Identificar si se consultó un militar específico
                    detected_m = active_militar
                    if query_result.get("rows"):
                        first = query_result["rows"][0]
                        cedulas_r = {str(r.get("cedula")) for r in query_result["rows"] if r.get("cedula")}
                        if "cedula" in first and len(cedulas_r) == 1:
                            detected_m = {
                                "cedula": str(first.get("cedula")),
                                "nombre": str(first.get("nombre") or (active_militar.get("nombre") if active_militar else "")).strip()
                            }

                    return {
                        "type": "data",
                        "answer": synthesis,
                        "sql": sql_to_run,
                        "columns": query_result["columns"],
                        "rows": query_result["rows"],
                        "total_records": query_result["total"],
                        "model": f"{model_label} (catálogo)",
                        "active_militar": detected_m,
                        "detected_entities": {"militar": detected_m, "period": ctx_period}
                    }
                except Exception as e:
                    logger.error(f"[IAOrchestrator] Error ejecutando SQL de catálogo: {e}")
                    return {
                        "type": "error",
                        "answer": f"Error ejecutando la consulta militar: {e}",
                        "sql": sql_to_run,
                        "columns": [],
                        "rows": [],
                        "total_records": 0,
                        "model": model_label,
                        "active_militar": active_militar,
                        "detected_entities": {"militar": active_militar, "period": ctx_period}
                    }

        # ------------------------------------------------------------------
        # PASO 4: SLOW-PATH (TEXT-TO-SQL MEDIANTE LLM PROVIDER)
        # ------------------------------------------------------------------
        logger.info(f"[IAOrchestrator] Consulta no cubierta en catálogo. Invocando Text-to-SQL con {model_label}...")
        system_instruction = build_system_prompt(context=context, active_militar=active_militar, current_year=now.year)
        
        prompt = (
            f"Consulta del Comandante: \"{user_message}\"\n\n"
            f"Instrucción: Genera ÚNICAMENTE la sentencia SQL válida para PostgreSQL que responde a la consulta.\n"
            f"No agregues texto explicativo ni bloques markdown. Solo la sentencia SQL pura."
        )

        try:
            raw_sql = llm_provider.generate_text(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.1,
                max_tokens=250,
                model=active_model
            )
            # Limpiar bloques markdown ```sql ... ```
            clean_sql = re.sub(r"^```(?:sql)?\s*", "", raw_sql.strip(), flags=re.IGNORECASE)
            clean_sql = re.sub(r"\s*```$", "", clean_sql).strip()

            is_safe, error_motivo = validate_sql(clean_sql)
            if not is_safe:
                logger.warning(f"[IAOrchestrator] SQL generado inseguro: '{clean_sql}' - Motivo: {error_motivo}")
                return {
                    "type": "error",
                    "answer": f"Por políticas de seguridad operacional, no se puede ejecutar la consulta generada: {error_motivo}",
                    "sql": clean_sql,
                    "columns": [],
                    "rows": [],
                    "total_records": 0,
                    "model": model_label,
                    "active_militar": active_militar,
                    "detected_entities": {"militar": active_militar, "period": ctx_period}
                }

            cols, rows = execute_safe_query(db, clean_sql)
            query_result = {"columns": cols, "rows": rows, "total": len(rows)}
            synthesis = _auto_synthesize(user_message, query_result, db=db)

            return {
                "type": "data",
                "answer": synthesis,
                "sql": clean_sql,
                "columns": query_result["columns"],
                "rows": query_result["rows"],
                "total_records": query_result["total"],
                "model": model_label,
                "active_militar": active_militar,
                "detected_entities": {"militar": active_militar, "period": ctx_period}
            }
        except Exception as e:
            logger.error(f"[IAOrchestrator] Error en Text-to-SQL: {e}")
            return {
                "type": "error",
                "answer": f"No se pudo completar la consulta con el motor de IA: {e}",
                "sql": None,
                "columns": [],
                "rows": [],
                "total_records": 0,
                "model": model_label,
                "active_militar": active_militar,
                "detected_entities": {"militar": active_militar, "period": ctx_period}
            }

_orchestrator_instance = None

def get_ia_orchestrator() -> IAOrchestrator:
    """Singleton del orquestador de IA."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = IAOrchestrator()
    return _orchestrator_instance

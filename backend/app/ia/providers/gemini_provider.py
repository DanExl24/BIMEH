"""
Proveedor de inferencia para Google Gemini API utilizando el SDK oficial google-genai.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from app.ia.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

AVAILABLE_GEMINI_MODELS: List[Dict[str, Any]] = [
    {
        "id": "gemini-3.5-flash-lite",
        "name": "Gemini 3.5 Flash Lite",
        "rpd": 500,
        "rpm": 15,
        "tpm": "250K",
        "category": "Flash Lite",
        "description": "Máxima cuota gratuita diaria (500 solicitudes/día). Ultrarrápido y ligero para consultas frecuentes.",
        "recommended": True,
        "badge": "500 req/día (Recomendado)",
    },
    {
        "id": "gemini-3.1-flash-lite",
        "name": "Gemini 3.1 Flash Lite",
        "rpd": 500,
        "rpm": 15,
        "tpm": "250K",
        "category": "Flash Lite",
        "description": "Alta cuota gratuita diaria (500 solicitudes/día). Muy veloz y estable para análisis militar.",
        "recommended": True,
        "badge": "500 req/día",
    },
    {
        "id": "gemini-3.8-flash",
        "name": "Gemini 3.8 Flash",
        "rpd": 20,
        "rpm": 5,
        "tpm": "250K",
        "category": "Flash",
        "description": "Mayor capacidad de razonamiento y síntesis avanzada. Cuota diaria reducida (20 solicitudes/día en Free Tier).",
        "recommended": False,
        "badge": "20 req/día",
    },
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "rpd": 20,
        "rpm": 5,
        "tpm": "250K",
        "category": "Flash",
        "description": "Modelo balanceado multimodal estándar. Cuota diaria reducida (20 solicitudes/día en Free Tier).",
        "recommended": False,
        "badge": "20 req/día",
    },
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "rpd": 50,
        "rpm": 2,
        "tpm": "32K",
        "category": "Pro",
        "description": "Razonamiento profundo para análisis complejos. Mayor latencia y límites estrictos de peticiones por minuto.",
        "recommended": False,
        "badge": "Avanzado / Pro",
    },
]

class GeminiProvider(BaseLLMProvider):
    """Adaptador para la API de Google Gemini en la nube."""

    def __init__(self):
        self._cached_live_models: List[str] = []
        self._last_live_fetch: float = 0.0

    def _get_client(self) -> genai.Client:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if not key:
            raise RuntimeError("GEMINI_API_KEY no está configurada en las variables de entorno.")
        return genai.Client(api_key=key)

    def get_live_models(self) -> List[str]:
        now = time.time()
        if self._cached_live_models and (now - self._last_live_fetch) < 300:
            return self._cached_live_models
        try:
            client = self._get_client()
            all_m = list(client.models.list())
            found = []
            for m in all_m:
                m_name = getattr(m, "name", "") or ""
                clean_name = m_name.replace("models/", "").strip()
                if "flash" in clean_name or "pro" in clean_name:
                    found.append(clean_name)
            if found:
                self._cached_live_models = found
                self._last_live_fetch = now
                return found
        except Exception as e:
            logger.warning(f"[GeminiProvider] No se pudo listar modelos desde API: {e}")
        return self._cached_live_models

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 512,
        model: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        client = self._get_client()
        config_kwargs: Dict[str, Any] = {
            "temperature": temperature,
            "max_output_tokens": max_tokens
        }
        if json_mode:
            config_kwargs["response_mime_type"] = "application/json"
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        primary_model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        live_models = self.get_live_models()

        # Priorizar modelos con alta cuota gratuita
        high_quota_priority = [
            primary_model,
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.7-flash",
            "gemini-3.8-flash",
        ]
        models_to_try = []
        for m in high_quota_priority:
            if m in live_models and m not in models_to_try:
                models_to_try.append(m)
                if len(models_to_try) >= 3:
                    break
        if not models_to_try:
            models_to_try = [primary_model]

        last_error_detail = None
        for idx, model_name in enumerate(models_to_try):
            max_attempts = 2 if idx == 0 else 1
            for attempt in range(max_attempts):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(**config_kwargs),
                    )
                    return response.text.strip() if response.text else ""
                except Exception as e:
                    err_str = str(e).upper()
                    last_error_detail = e
                    is_quota = "RESOURCE_EXHAUSTED" in err_str or "QUOTA" in err_str or "429" in err_str
                    is_transient = ("503" in err_str or "UNAVAILABLE" in err_str or "HIGH DEMAND" in err_str) and not is_quota
                    is_unsupported = "404" in err_str or "NOT_FOUND" in err_str or "MODALIT" in err_str or "NOT SUPPORTED" in err_str or "INVALID_ARGUMENT" in err_str

                    if is_quota:
                        logger.warning(f"[GeminiProvider] Cuota agotada en '{model_name}'. Probando fallback...")
                        break
                    elif is_transient:
                        if attempt < max_attempts - 1:
                            logger.warning(f"[GeminiProvider] Saturación temporal (503) en '{model_name}'. Reintentando...")
                            time.sleep(1.0)
                        else:
                            break
                    elif is_unsupported:
                        logger.warning(f"[GeminiProvider] Modelo '{model_name}' no soportado ({e}). Omitiendo.")
                        break
                    else:
                        if idx < len(models_to_try) - 1:
                            logger.warning(f"[GeminiProvider] Error con '{model_name}': {e}. Probando fallback...")
                            break
                        logger.error(f"[GeminiProvider] Error con '{model_name}': {e}")
                        raise RuntimeError(f"Error de Gemini: {e}")

        err_str = str(last_error_detail).upper()
        if "RESOURCE_EXHAUSTED" in err_str or "QUOTA" in err_str or "429" in err_str:
            raise RuntimeError(
                "La cuota de la API de Google Gemini ha sido alcanzada por hoy. "
                "Las consultas operacionales y tablas del catálogo militar continúan 100% operativas."
            )
        raise RuntimeError(
            f"El servicio de Gemini está experimentando alta demanda en Google Cloud. (Detalle: {last_error_detail})"
        )

    def get_status(self) -> Dict[str, Any]:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        configured_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        if not key:
            return {
                "backend": "gemini",
                "online": False,
                "model_configured": configured_model,
                "error": "GEMINI_API_KEY no configurada",
                "available_models": self.get_available_models(),
            }
        try:
            client = self._get_client()
            all_m = list(client.models.list())
            model_names = [getattr(m, "name", "").replace("models/", "") for m in all_m]
            return {
                "backend": "gemini",
                "online": True,
                "model_configured": configured_model,
                "models_available": model_names[:15],
                "available_models": self.get_available_models(),
            }
        except Exception as e:
            return {
                "backend": "gemini",
                "online": False,
                "model_configured": configured_model,
                "error": str(e),
                "available_models": self.get_available_models(),
            }

    def get_available_models(self) -> List[Dict[str, Any]]:
        current_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
        result = []
        for m in AVAILABLE_GEMINI_MODELS:
            entry = dict(m)
            entry["active"] = (m["id"] == current_model)
            result.append(entry)
        if not any(m["id"] == current_model for m in AVAILABLE_GEMINI_MODELS):
            result.insert(0, {
                "id": current_model,
                "name": current_model,
                "rpd": None,
                "rpm": None,
                "tpm": None,
                "category": "Custom",
                "description": f"Modelo configurado manualmente: {current_model}",
                "recommended": False,
                "badge": "Personalizado",
                "active": True
            })
        return result

"""
LLM Gateway: Capa de abstracción y factoría de proveedores de inferencia para BIMEH.
"""

import os
import logging
from typing import Tuple
from app.ia.providers.base import BaseLLMProvider
from app.ia.providers.gemini_provider import GeminiProvider
from app.ia.providers.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

_gemini_instance = None
_ollama_instance = None

def get_llm_provider(preferred_backend: str = None) -> Tuple[BaseLLMProvider, str]:
    """
    Retorna la instancia del proveedor de LLM activo según la configuración o parámetro.
    Aplica conmutación y fallback transparente si un proveedor no está disponible.
    """
    global _gemini_instance, _ollama_instance

    backend = (preferred_backend or os.getenv("AI_BACKEND", "gemini")).lower().strip()

    if backend == "gemini":
        has_key = bool(os.getenv("GEMINI_API_KEY", "").strip())
        if has_key:
            if _gemini_instance is None:
                _gemini_instance = GeminiProvider()
            return _gemini_instance, "gemini"
        else:
            logger.warning("[get_llm_provider] GEMINI_API_KEY no presente. Conmutando a Ollama local...")
            if _ollama_instance is None:
                _ollama_instance = OllamaProvider()
            return _ollama_instance, "ollama"

    elif backend == "ollama":
        if _ollama_instance is None:
            _ollama_instance = OllamaProvider()
        return _ollama_instance, "ollama"

    # Default a Gemini si es posible
    if _gemini_instance is None:
        _gemini_instance = GeminiProvider()
    return _gemini_instance, "gemini"

__all__ = ["BaseLLMProvider", "GeminiProvider", "OllamaProvider", "get_llm_provider"]

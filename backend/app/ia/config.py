"""
Configuración centralizada del subsistema de Inteligencia Artificial de BIMEH.
"""

import os
from typing import Dict, Any

AI_BACKEND = os.getenv("AI_BACKEND", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

SQL_TIMEOUT_SECONDS = int(os.getenv("IA_SQL_TIMEOUT", "5"))
SQL_MAX_ROWS = int(os.getenv("IA_SQL_MAX_ROWS", "100"))

def get_current_config() -> Dict[str, Any]:
    """Retorna la configuración activa en memoria."""
    return {
        "backend": os.getenv("AI_BACKEND", AI_BACKEND),
        "gemini_model": os.getenv("GEMINI_MODEL", GEMINI_MODEL),
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL),
        "ollama_model": os.getenv("OLLAMA_MODEL", OLLAMA_DEFAULT_MODEL),
        "has_gemini_key": bool(os.getenv("GEMINI_API_KEY", GEMINI_API_KEY).strip()),
        "sql_timeout": SQL_TIMEOUT_SECONDS,
        "sql_max_rows": SQL_MAX_ROWS,
    }

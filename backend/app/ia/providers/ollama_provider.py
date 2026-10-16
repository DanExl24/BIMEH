"""
Proveedor de inferencia para Ollama (IA Local en servidor o workstation).
"""

import os
import httpx
import logging
from typing import Dict, Any, List, Optional
from app.ia.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    """Adaptador para modelos ejecutados localmente mediante Ollama."""

    def __init__(self):
        self.timeout = 60.0

    @property
    def base_url(self) -> str:
        return os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")

    @property
    def default_model(self) -> str:
        return os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 512,
        model: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        active_model = model or self.default_model
        payload: Dict[str, Any] = {
            "model": active_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        if system_instruction:
            payload["system"] = system_instruction
        if json_mode:
            payload["format"] = "json"

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/api/generate", json=payload)
                res.raise_for_status()
                data = res.json()
                return data.get("response", "").strip()
        except httpx.ConnectError:
            raise RuntimeError(f"No se pudo conectar a Ollama en {self.base_url}. Asegúrese de que el servicio esté iniciado.")
        except httpx.TimeoutException:
            raise RuntimeError(f"Tiempo de espera agotado al consultar Ollama ({active_model}).")
        except Exception as e:
            raise RuntimeError(f"Error consultando Ollama: {e}")

    def get_status(self) -> Dict[str, Any]:
        configured_model = self.default_model
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m["name"] for m in res.json().get("models", [])]
                    return {
                        "backend": "ollama",
                        "online": True,
                        "model_configured": configured_model,
                        "models_available": models,
                        "available_models": self.get_available_models(),
                    }
        except Exception as e:
            logger.debug(f"[OllamaProvider] Error comprobando estado: {e}")

        return {
            "backend": "ollama",
            "online": False,
            "model_configured": configured_model,
            "error": f"Ollama no responde en {self.base_url}",
            "available_models": self.get_available_models(),
        }

    def get_available_models(self) -> List[Dict[str, Any]]:
        configured = self.default_model
        available = []
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    for m in res.json().get("models", []):
                        m_name = m.get("name", "")
                        available.append({
                            "id": m_name,
                            "name": m_name,
                            "rpd": "Ilimitado (Local)",
                            "rpm": "Ilimitado",
                            "tpm": "Local",
                            "category": "Ollama Local",
                            "description": "Modelo de inferencia local sin conexión a Internet.",
                            "recommended": (m_name == configured),
                            "badge": "Local",
                            "active": (m_name == configured)
                        })
        except Exception:
            pass

        if not available:
            available.append({
                "id": configured,
                "name": configured,
                "rpd": "Local",
                "rpm": "Local",
                "tpm": "Local",
                "category": "Ollama Local",
                "description": "Modelo configurado por defecto.",
                "recommended": True,
                "badge": "Local",
                "active": True
            })
        return available

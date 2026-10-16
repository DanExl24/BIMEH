"""
Clase base abstracta para los proveedores de inferencia de modelos de lenguaje (LLM Gateway).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseLLMProvider(ABC):
    """Interfaz estándar que deben implementar todos los motores de LLM (Gemini, Ollama, etc.)."""

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 512,
        model: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        """Genera una respuesta en texto o JSON a partir de un prompt y directivas de sistema."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Retorna el estado de conectividad, salud y disponibilidad del proveedor."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Retorna la lista de modelos homologados y disponibles para este proveedor."""
        pass

"""
Router de API para el Asistente de IA en BIMEH.
Soporta dos backends: Gemini (Google Cloud) u Ollama (local).
Se configura con la variable de entorno AI_BACKEND=gemini|ollama
"""

import os
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.services import ollama_service

import logging

logger = logging.getLogger(__name__)

def get_ai_backend():
    backend = os.getenv("AI_BACKEND", "gemini").lower().strip()
    if backend == "gemini":
        try:
            from app.services import gemini_service
            return gemini_service, "gemini"
        except ImportError as e:
            logger.warning("No se pudo cargar gemini_service: %s. Usando fallback a ollama.", e)
            return ollama_service, f"ollama (fallback: {e})"
    return ollama_service, "ollama"

router = APIRouter(prefix="/api/ia", tags=["IA"])


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pregunta o solicitud en lenguaje natural para la IA")
    history: Optional[List[Dict[str, Any]]] = Field(default=None, description="Historial previo de mensajes")
    active_militar: Optional[Dict[str, Any]] = Field(default=None, description="Militar en contexto activo (cedula, nombre)")


class ApreciacionRequest(BaseModel):
    mes: Optional[str] = Field("TODOS", description="Nombre del mes operacional o TODOS para consolidado")


class IAConfigRequest(BaseModel):
    base_url: Optional[str] = Field(None, description="URL de Ollama o Cloudflare Tunnel (ej. https://...trycloudflare.com)")
    model: Optional[str] = Field(None, description="Modelo de Ollama (ej. llama3.1:8b)")


@router.get("/status")
def get_ia_status():
    """Reporta el estado del backend de IA activo (Gemini o Ollama)."""
    service, backend_name = get_ai_backend()
    if backend_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        api_key_ok = bool(api_key)
        return {
            "backend": "gemini",
            "model_configured": os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            "online": api_key_ok,
            "api_key_configured": api_key_ok,
            "error": None if api_key_ok else "GEMINI_API_KEY no encontrada en variables de entorno",
        }
    status = ollama_service.check_ollama_status()
    if "fallback" in backend_name:
        status["backend"] = backend_name
        status["warning"] = "Se configuro Gemini pero no se pudo importar el SDK google-genai en el contenedor."
    return status


@router.post("/config")
def update_ia_config(req: IAConfigRequest):
    """Actualiza la URL o modelo de Ollama en tiempo de ejecución."""
    if req.base_url:
        os.environ["OLLAMA_BASE_URL"] = req.base_url.strip().rstrip("/")
    if req.model:
        os.environ["OLLAMA_MODEL"] = req.model.strip()
    return ollama_service.check_ollama_status()


@router.post("/chat")
def chat_with_ia(req: ChatMessageRequest, db = Depends(get_db)):
    """
    Recibe una solicitud en lenguaje natural del usuario.
    Usa el backend configurado (Gemini o Ollama) para generar SQL y sintetizar resultados.
    """
    service, backend_name = get_ai_backend()
    if backend_name == "ollama":
        status = ollama_service.check_ollama_status()
        if not status.get("online"):
            raise HTTPException(
                status_code=503,
                detail=(
                    "El servicio de Ollama no está en ejecución. "
                    f"Ejecute: ollama run {status.get('model_configured')}"
                )
            )
    elif backend_name == "gemini":
        if not os.getenv("GEMINI_API_KEY", "").strip():
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY no está configurada en el archivo .env o variables de entorno."
            )

    start_time = time.time()
    try:
        resultado = service.process_user_query(
            user_message=req.message,
            db=db,
            history=req.history,
            active_militar=req.active_militar
        )
        elapsed = round(time.time() - start_time, 1)
        return {
            "status": "success",
            "elapsed_seconds": elapsed,
            "backend": backend_name,
            **resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando consulta con IA ({backend_name}): {str(e)}"
        )


@router.post("/apreciacion")
def generar_apreciacion_comandancia(req: ApreciacionRequest, db = Depends(get_db)):
    """
    Genera el informe formal de Apreciación de Situación de Personal para la comandancia.
    """
    service, backend_name = get_ai_backend()
    if backend_name == "ollama":
        status = ollama_service.check_ollama_status()
        if not status.get("online"):
            raise HTTPException(
                status_code=503,
                detail="El servicio de Ollama no está en ejecución."
            )
    elif backend_name == "gemini":
        if not os.getenv("GEMINI_API_KEY", "").strip():
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY no está configurada en el archivo .env o variables de entorno."
            )

    start_time = time.time()
    try:
        # gemini_service usa generate_apreciacion; ollama_service usa generate_executive_briefing
        if hasattr(service, "generate_apreciacion"):
            resultado = service.generate_apreciacion(db)
        else:
            resultado = service.generate_executive_briefing(req.mes, db)
        elapsed = round(time.time() - start_time, 1)
        return {
            "status": "success",
            "elapsed_seconds": elapsed,
            "backend": backend_name,
            **resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando apreciación ({backend_name}): {str(e)}"
        )

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

# Seleccionar backend según variable de entorno
_backend = os.getenv("AI_BACKEND", "gemini").lower().strip()
if _backend == "gemini":
    try:
        from app.services import gemini_service as ai_service
        _backend_name = "gemini"
    except ImportError:
        ai_service = ollama_service  # type: ignore
        _backend_name = "ollama (fallback)"
else:
    ai_service = ollama_service  # type: ignore
    _backend_name = "ollama"

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
    if _backend_name == "gemini":
        api_key_ok = bool(os.getenv("GEMINI_API_KEY", ""))
        return {
            "backend": "gemini",
            "model_configured": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            "online": api_key_ok,
            "api_key_configured": api_key_ok,
        }
    return ollama_service.check_ollama_status()


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
    # Solo verificar estado de Ollama si el backend activo es Ollama
    if _backend_name == "ollama":
        status = ollama_service.check_ollama_status()
        if not status.get("online"):
            raise HTTPException(
                status_code=503,
                detail=(
                    "El servicio de Ollama no está en ejecución. "
                    f"Ejecute: ollama run {status.get('model_configured')}"
                )
            )

    start_time = time.time()
    try:
        resultado = ai_service.process_user_query(
            user_message=req.message,
            db=db,
            history=req.history,
            active_militar=req.active_militar
        )
        elapsed = round(time.time() - start_time, 1)
        return {
            "status": "success",
            "elapsed_seconds": elapsed,
            "backend": _backend_name,
            **resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando consulta con IA ({_backend_name}): {str(e)}"
        )


@router.post("/apreciacion")
def generar_apreciacion_comandancia(req: ApreciacionRequest, db = Depends(get_db)):
    """
    Genera el informe formal de Apreciación de Situación de Personal para la comandancia.
    """
    if _backend_name == "ollama":
        status = ollama_service.check_ollama_status()
        if not status.get("online"):
            raise HTTPException(
                status_code=503,
                detail="El servicio de Ollama no está en ejecución."
            )

    start_time = time.time()
    try:
        # gemini_service usa generate_apreciacion; ollama_service usa generate_executive_briefing
        if hasattr(ai_service, "generate_apreciacion"):
            resultado = ai_service.generate_apreciacion(db)
        else:
            resultado = ai_service.generate_executive_briefing(req.mes, db)
        elapsed = round(time.time() - start_time, 1)
        return {
            "status": "success",
            "elapsed_seconds": elapsed,
            "backend": _backend_name,
            **resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando apreciación ({_backend_name}): {str(e)}"
        )

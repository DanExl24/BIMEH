"""
Router de API para el Asistente de IA (Ollama) en BIMEH.
Provee endpoints de estado, chat conversacional con Text-to-SQL y generación
de apreciaciones de comandancia.
"""

import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.services import ollama_service

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
    """
    Verifica si el servidor de Ollama está online localmente y reporta
    el modelo configurado y los modelos instalados.
    """
    return ollama_service.check_ollama_status()


@router.post("/config")
def update_ia_config(req: IAConfigRequest):
    """
    Actualiza dinámicamente la URL base de Ollama (útil para Cloudflare Tunnel)
    o el modelo en tiempo de ejecución.
    """
    import os
    if req.base_url:
        os.environ["OLLAMA_BASE_URL"] = req.base_url.strip().rstrip("/")
    if req.model:
        os.environ["OLLAMA_MODEL"] = req.model.strip()
    return ollama_service.check_ollama_status()


@router.post("/chat")
def chat_with_ia(req: ChatMessageRequest, db = Depends(get_db)):
    """
    Recibe una solicitud en lenguaje natural del usuario.
    Analiza la intención, ejecuta la consulta SQL segura en PostgreSQL si aplica,
    y retorna la respuesta explicativa junto con los datos tabulares.
    """
    status = ollama_service.check_ollama_status()
    if not status.get("online"):
        raise HTTPException(
            status_code=503,
            detail=(
                "El servicio de Ollama no está en ejecución localmente. "
                f"Por favor inicie Ollama o ejecute 'ollama run {status.get('model_configured')}' en su terminal."
            )
        )

    start_time = time.time()
    try:
        resultado = ollama_service.process_user_query(
            user_message=req.message,
            db=db,
            history=req.history,
            active_militar=req.active_militar
        )
        elapsed = round(time.time() - start_time, 1)
        return {
            "status": "success",
            "elapsed_seconds": elapsed,
            **resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la consulta con IA: {str(e)}"
        )


@router.post("/apreciacion")
def generar_apreciacion_comandancia(req: ApreciacionRequest, db = Depends(get_db)):
    """
    Genera un informe formal militar de Apreciación de Situación de Personal
    para la comandancia del BIMEJ 12 a partir de las métricas consolidadas.
    """
    status = ollama_service.check_ollama_status()
    if not status.get("online"):
        raise HTTPException(
            status_code=503,
            detail=(
                "El servicio de Ollama no está en ejecución localmente. "
                f"Por favor inicie Ollama o ejecute 'ollama run {status.get('model_configured')}' en su terminal."
            )
        )

    start_time = time.time()
    try:
        resultado = ollama_service.generate_executive_briefing(req.mes, db)
        elapsed = round(time.time() - start_time, 1)
        return {
            "status": "success",
            "elapsed_seconds": elapsed,
            **resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando apreciación con IA: {str(e)}"
        )

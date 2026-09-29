"""
Router de API para el Asistente de IA (Ollama) en BIMEH.
Provee endpoints de estado, chat conversacional con Text-to-SQL y generación
de apreciaciones de comandancia.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from app.database import get_db
from app.services import ollama_service

router = APIRouter(prefix="/api/ia", tags=["IA"])


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pregunta o solicitud en lenguaje natural para la IA")


class ApreciacionRequest(BaseModel):
    mes: Optional[str] = Field("TODOS", description="Nombre del mes operacional o TODOS para consolidado")


@router.get("/status")
def get_ia_status():
    """
    Verifica si el servidor de Ollama está online localmente y reporta
    el modelo configurado y los modelos instalados.
    """
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

    try:
        resultado = ollama_service.process_user_query(req.message, db)
        return {
            "status": "success",
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

    try:
        resultado = ollama_service.generate_executive_briefing(req.mes, db)
        return {
            "status": "success",
            **resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando apreciación con IA: {str(e)}"
        )

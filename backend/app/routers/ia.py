"""
Router de API para el Asistente de IA en BIMEH.
Utiliza la arquitectura modular basada en IAOrchestrator, LLM Providers y SessionRepository.
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.database import get_db
from app.ia.orchestrator import get_ia_orchestrator
from app.ia.providers import get_llm_provider
from app.ia.repository import (
    listar_sesiones,
    crear_sesion,
    obtener_mensajes_sesion,
    eliminar_sesion,
    guardar_mensaje,
    actualizar_titulo_sesion,
    sesion_existe,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ia", tags=["IA"])

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Pregunta o solicitud en lenguaje natural para la IA")
    history: Optional[List[Dict[str, Any]]] = Field(default=None, description="Historial previo de mensajes")
    active_militar: Optional[Dict[str, Any]] = Field(default=None, description="Militar en contexto activo (cedula, nombre)")
    model: Optional[str] = Field(default=None, description="Modelo de Gemini u Ollama a utilizar para esta consulta")
    mode: Optional[str] = Field(default="chat", description="Modo de operacion: 'chat' o 'report'")
    session_id: Optional[int] = Field(default=None, description="ID de la sesión de chat para persistencia")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexto visual de pantalla y filtros activos")

class CreateSessionRequest(BaseModel):
    titulo: Optional[str] = Field(default="Nueva conversación", description="Título inicial de la sesión de chat")

class ApreciacionRequest(BaseModel):
    mes: Optional[str] = Field("TODOS", description="Nombre del mes operacional o TODOS para consolidado")
    model: Optional[str] = Field(default=None, description="Modelo de Gemini u Ollama a utilizar")

class IAConfigRequest(BaseModel):
    base_url: Optional[str] = Field(None, description="URL de Ollama o Cloudflare Tunnel (ej. https://...trycloudflare.com)")
    model: Optional[str] = Field(None, description="Modelo activo (ej. gemini-3.5-flash-lite o llama3.1)")

@router.get("/status")
def get_ia_status():
    """Reporta el estado del backend de IA activo (Gemini o Ollama) y los modelos disponibles."""
    llm, backend_name = get_llm_provider()
    return llm.get_status()

@router.get("/sesiones")
def list_chat_sessions(db = Depends(get_db)):
    """Lista las sesiones de chat persistentes ordenadas por última actualización."""
    return listar_sesiones(db)

@router.post("/sesiones")
def create_chat_session(req: Optional[CreateSessionRequest] = None, db = Depends(get_db)):
    """Crea una nueva sesión vacía de chat."""
    titulo = req.titulo if req and req.titulo else "Nueva conversación"
    return crear_sesion(db, titulo=titulo)

@router.get("/sesiones/{session_id}")
def get_chat_session(session_id: int, db = Depends(get_db)):
    """Recupera el historial de mensajes de una sesión existente."""
    session = obtener_mensajes_sesion(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión de chat no encontrada")
    return session

@router.delete("/sesiones/{session_id}")
def delete_chat_session(session_id: int, db = Depends(get_db)):
    """Elimina una sesión de chat y sus mensajes asociados."""
    eliminar_sesion(db, session_id)
    return {"status": "success", "message": f"Sesión {session_id} eliminada correctamente"}

@router.post("/config")
def update_ia_config(req: IAConfigRequest):
    """Actualiza la URL o modelo de IA en tiempo de ejecución (sin necesidad de reiniciar)."""
    if req.base_url:
        os.environ["OLLAMA_BASE_URL"] = req.base_url.strip().rstrip("/")
    if req.model:
        model_name = req.model.strip()
        os.environ["GEMINI_MODEL"] = model_name
        os.environ["OLLAMA_MODEL"] = model_name
        logger.info(f"[IA Config] Modelo activo actualizado a: {model_name}")
    return get_ia_status()

@router.post("/chat")
def chat_with_ia(req: ChatMessageRequest, db = Depends(get_db)):
    """
    Recibe una solicitud en lenguaje natural del usuario.
    Persiste la conversación en BD y utiliza context awareness para responder.
    """
    # 1. Resolver o crear la sesión de chat
    session_id = req.session_id
    if session_id and not sesion_existe(db, session_id):
        session_id = None

    if not session_id:
        nueva_ses = crear_sesion(db, titulo=req.message)
        session_id = nueva_ses["id"]
    else:
        # Autotitular si la sesión tenía título por defecto
        ses_data = obtener_mensajes_sesion(db, session_id)
        if ses_data and ses_data.get("titulo") in ("Nueva conversación", "Nueva consulta", ""):
            actualizar_titulo_sesion(db, session_id, req.message)

    # 2. Guardar mensaje del usuario
    guardar_mensaje(
        db=db,
        session_id=session_id,
        rol="user",
        contenido=req.message,
        metadatos={"context": req.context or {}}
    )

    # 3. Reconstruir historial si no vino del frontend
    history = req.history
    if not history:
        ses_data = obtener_mensajes_sesion(db, session_id)
        if ses_data and ses_data.get("mensajes"):
            # Excluir el último mensaje recién agregado
            prev_msgs = [m for m in ses_data["mensajes"][:-1]][-6:]
            history = [{"sender": m["rol"], "text": m["contenido"]} for m in prev_msgs]

    start_time = time.time()
    try:
        orchestrator = get_ia_orchestrator()
        resultado = orchestrator.process_query(
            user_message=req.message,
            db=db,
            history=history,
            active_militar=req.active_militar,
            model=req.model,
            mode=req.mode or "chat",
            context=req.context
        )
        elapsed = round(time.time() - start_time, 1)

        # 4. Guardar respuesta del asistente en BD
        bot_meta = {
            "elapsed_seconds": elapsed,
            "backend": resultado.get("model"),
            "model": resultado.get("model"),
            "sql": resultado.get("sql"),
            "type": resultado.get("type"),
            "detected_entities": resultado.get("detected_entities")
        }
        guardar_mensaje(
            db=db,
            session_id=session_id,
            rol="assistant",
            contenido=resultado.get("answer", ""),
            metadatos=bot_meta
        )

        return {
            "status": "success",
            "session_id": session_id,
            "elapsed_seconds": elapsed,
            "backend": resultado.get("model", "ia"),
            **resultado
        }
    except Exception as e:
        logger.error(f"[chat_with_ia] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando consulta con IA: {str(e)}"
        )

@router.post("/apreciacion")
def generar_apreciacion_comandancia(req: ApreciacionRequest, db = Depends(get_db)):
    """
    Genera el informe formal de Apreciación de Situación de Personal para la comandancia.
    """
    from app.ia.skills.apreciacion_skill import ApreciacionSkill
    from app.ia.skills.base import QueryContext

    start_time = time.time()
    try:
        skill = ApreciacionSkill()
        ctx = QueryContext(user_message=f"Apreciación de personal mes {req.mes}", db=db)
        res = skill.execute(ctx)
        elapsed = round(time.time() - start_time, 1)
        if res and res.report_info:
            return {
                "status": "success",
                "elapsed_seconds": elapsed,
                **res.report_info
            }
        return {
            "status": "success",
            "elapsed_seconds": elapsed,
            "apreciacion": res.answer if res else "No se pudo generar la apreciación."
        }
    except Exception as e:
        logger.error(f"[generar_apreciacion_comandancia] Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generando apreciación: {str(e)}"
        )

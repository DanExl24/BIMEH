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
    """Reporta el estado del backend de IA activo (Gemini o Ollama) y la lista de modelos disponibles con sus cuotas."""
    service, backend_name = get_ai_backend()
    if backend_name == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        api_key_ok = bool(api_key)
        current_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        models_info = getattr(service, "get_gemini_models_info", lambda: [])()
        return {
            "backend": "gemini",
            "model_configured": current_model,
            "online": api_key_ok,
            "api_key_configured": api_key_ok,
            "available_models": models_info,
            "error": None if api_key_ok else "GEMINI_API_KEY no encontrada en variables de entorno",
        }
    status = ollama_service.check_ollama_status()
    if "fallback" in backend_name:
        status["backend"] = backend_name
        status["warning"] = "Se configuro Gemini pero no se pudo importar el SDK google-genai en el contenedor."
    return status


@router.get("/sesiones")
def list_chat_sessions(db = Depends(get_db)):
    """Lista las sesiones de chat persistentes ordenadas por última actualización."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT s.id, s.titulo, s.creado_en, s.actualizado_en,
               COUNT(m.id) AS total_mensajes
        FROM IA_SESIONES s
        LEFT JOIN IA_MENSAJES m ON m.id_sesion = s.id
        GROUP BY s.id, s.titulo, s.creado_en, s.actualizado_en
        ORDER BY s.actualizado_en DESC
        LIMIT 50;
    """)
    rows = cursor.fetchall()
    return [
        {
            "id": r[0],
            "titulo": r[1],
            "creado_en": r[2].strftime("%Y-%m-%d %H:%M:%S") if r[2] else None,
            "actualizado_en": r[3].strftime("%Y-%m-%d %H:%M:%S") if r[3] else None,
            "total_mensajes": r[4]
        }
        for r in rows
    ]


@router.post("/sesiones")
def create_chat_session(req: Optional[CreateSessionRequest] = None, db = Depends(get_db)):
    """Crea una nueva sesión vacía de chat."""
    titulo = (req.titulo.strip() if req and req.titulo else "Nueva conversación")
    cursor = db.cursor()
    cursor.execute("INSERT INTO IA_SESIONES (titulo) VALUES (%s) RETURNING id, titulo, creado_en;", (titulo,))
    row = cursor.fetchone()
    try: db.commit()
    except: pass
    return {
        "id": row[0],
        "titulo": row[1],
        "creado_en": row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else None,
        "total_mensajes": 0
    }


@router.get("/sesiones/{session_id}")
def get_chat_session(session_id: int, db = Depends(get_db)):
    """Recupera el historial de mensajes de una sesión existente."""
    cursor = db.cursor()
    cursor.execute("SELECT id, titulo, creado_en FROM IA_SESIONES WHERE id = %s;", (session_id,))
    session = cursor.fetchone()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión de chat no encontrada")
    cursor.execute("""
        SELECT id, rol, contenido, metadatos, creado_en
        FROM IA_MENSAJES
        WHERE id_sesion = %s
        ORDER BY id ASC;
    """, (session_id,))
    mensajes = cursor.fetchall()
    return {
        "id": session[0],
        "titulo": session[1],
        "creado_en": session[2].strftime("%Y-%m-%d %H:%M:%S") if session[2] else None,
        "mensajes": [
            {
                "id": m[0],
                "rol": m[1],
                "contenido": m[2],
                "metadatos": m[3] if isinstance(m[3], dict) else json.loads(m[3] or "{}"),
                "creado_en": m[4].strftime("%Y-%m-%d %H:%M:%S") if m[4] else None
            }
            for m in mensajes
        ]
    }


@router.delete("/sesiones/{session_id}")
def delete_chat_session(session_id: int, db = Depends(get_db)):
    """Elimina una sesión de chat y sus mensajes asociados."""
    cursor = db.cursor()
    cursor.execute("DELETE FROM IA_SESIONES WHERE id = %s;", (session_id,))
    try: db.commit()
    except: pass
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

    cursor = db.cursor()

    # 1. Resolver o crear la sesión de chat
    session_id = req.session_id
    if session_id:
        cursor.execute("SELECT id, titulo FROM IA_SESIONES WHERE id = %s;", (session_id,))
        ses_row = cursor.fetchone()
        if not ses_row:
            session_id = None
    if not session_id:
        # Generar título inicial a partir de la primera pregunta del usuario
        primer_titulo = req.message.strip().replace("\n", " ")
        if len(primer_titulo) > 42:
            primer_titulo = primer_titulo[:40] + "..."
        cursor.execute("INSERT INTO IA_SESIONES (titulo) VALUES (%s) RETURNING id;", (primer_titulo,))
        session_id = cursor.fetchone()[0]
        try: db.commit()
        except: pass
    else:
        # Si la sesión tenía un título por defecto, actualizar con la pregunta
        cursor.execute("SELECT titulo FROM IA_SESIONES WHERE id = %s;", (session_id,))
        t_row = cursor.fetchone()
        if t_row and t_row[0] in ("Nueva conversación", "Nueva consulta", ""):
            primer_titulo = req.message.strip().replace("\n", " ")
            if len(primer_titulo) > 42:
                primer_titulo = primer_titulo[:40] + "..."
            cursor.execute("UPDATE IA_SESIONES SET titulo = %s WHERE id = %s;", (primer_titulo, session_id))
            try: db.commit()
            except: pass

    # 2. Guardar mensaje del usuario en la base de datos
    user_meta = {"context": req.context or {}}
    cursor.execute(
        "INSERT INTO IA_MENSAJES (id_sesion, rol, contenido, metadatos) VALUES (%s, %s, %s, %s);",
        (session_id, "user", req.message, json.dumps(user_meta, ensure_ascii=False))
    )
    try: db.commit()
    except: pass

    # 3. Reconstruir historial si no vino del frontend
    history = req.history
    if not history:
        cursor.execute("""
            SELECT rol, contenido
            FROM IA_MENSAJES
            WHERE id_sesion = %s AND id < (SELECT MAX(id) FROM IA_MENSAJES WHERE id_sesion = %s)
            ORDER BY id DESC
            LIMIT 6;
        """, (session_id, session_id))
        prev_msgs = cursor.fetchall()
        if prev_msgs:
            history = [{"sender": p[0], "text": p[1]} for p in reversed(prev_msgs)]

    start_time = time.time()
    try:
        query_kwargs = {
            "user_message": req.message,
            "db": db,
            "history": history,
            "active_militar": req.active_militar,
            "mode": req.mode or "chat",
            "context": req.context
        }
        if req.model:
            query_kwargs["model"] = req.model

        resultado = service.process_user_query(**query_kwargs)
        elapsed = round(time.time() - start_time, 1)

        # 4. Guardar respuesta del asistente en BD
        bot_meta = {
            "elapsed_seconds": elapsed,
            "backend": backend_name,
            "model": resultado.get("model"),
            "sql": resultado.get("sql"),
            "type": resultado.get("type"),
            "detected_entities": resultado.get("detected_entities")
        }
        cursor.execute(
            "INSERT INTO IA_MENSAJES (id_sesion, rol, contenido, metadatos) VALUES (%s, %s, %s, %s);",
            (session_id, "assistant", resultado.get("answer", ""), json.dumps(bot_meta, ensure_ascii=False))
        )
        cursor.execute("UPDATE IA_SESIONES SET actualizado_en = CURRENT_TIMESTAMP WHERE id = %s;", (session_id,))
        try: db.commit()
        except: pass

        return {
            "status": "success",
            "session_id": session_id,
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
            resultado = service.generate_apreciacion(db, model=req.model)
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

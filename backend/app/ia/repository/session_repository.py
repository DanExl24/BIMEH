"""
Repositorio para la persistencia relacional de sesiones e historial de mensajes de IA.
Maneja las tablas IA_SESIONES e IA_MENSAJES en PostgreSQL.
"""

import json
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

def listar_sesiones(db) -> List[Dict[str, Any]]:
    """Obtiene la lista de sesiones de chat ordenadas por última actualización."""
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT s.id, s.titulo, s.creado_en, s.actualizado_en,
                   COUNT(m.id) AS total_mensajes
            FROM IA_SESIONES s
            LEFT JOIN IA_MENSAJES m ON s.id = m.id_sesion
            GROUP BY s.id, s.titulo, s.creado_en, s.actualizado_en
            ORDER BY s.actualizado_en DESC, s.id DESC;
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
    finally:
        cursor.close()

def crear_sesion(db, titulo: Optional[str] = None) -> Dict[str, Any]:
    """Crea una nueva sesión vacía de chat y retorna sus datos."""
    tit = (titulo.strip() if titulo and titulo.strip() else "Nueva conversación")
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO IA_SESIONES (titulo) VALUES (%s) RETURNING id, titulo, creado_en;", (tit,))
        row = cursor.fetchone()
        try:
            db.commit()
        except Exception:
            pass
        return {
            "id": row[0],
            "titulo": row[1],
            "creado_en": row[2].strftime("%Y-%m-%d %H:%M:%S") if row[2] else None,
            "total_mensajes": 0
        }
    finally:
        cursor.close()

def sesion_existe(db, session_id: int) -> bool:
    """Verifica si una sesión existe en la base de datos."""
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id FROM IA_SESIONES WHERE id = %s;", (session_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()

def obtener_mensajes_sesion(db, session_id: int) -> Optional[Dict[str, Any]]:
    """Recupera la sesión con todo su historial de mensajes ordenados cronológicamente."""
    cursor = db.cursor()
    try:
        cursor.execute("SELECT id, titulo, creado_en FROM IA_SESIONES WHERE id = %s;", (session_id,))
        session = cursor.fetchone()
        if not session:
            return None

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
    finally:
        cursor.close()

def eliminar_sesion(db, session_id: int) -> bool:
    """Elimina en cascada una sesión y todos sus mensajes asociados."""
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM IA_SESIONES WHERE id = %s;", (session_id,))
        try:
            db.commit()
        except Exception:
            pass
        return True
    finally:
        cursor.close()

def guardar_mensaje(
    db,
    session_id: int,
    rol: str,
    contenido: str,
    metadatos: Optional[Dict[str, Any]] = None
) -> int:
    """Guarda un mensaje en la tabla IA_MENSAJES y actualiza la fecha de la sesión."""
    cursor = db.cursor()
    try:
        meta_json = json.dumps(metadatos or {}, ensure_ascii=False)
        cursor.execute(
            "INSERT INTO IA_MENSAJES (id_sesion, rol, contenido, metadatos) VALUES (%s, %s, %s, %s) RETURNING id;",
            (session_id, rol, contenido, meta_json)
        )
        msg_id = cursor.fetchone()[0]
        # Actualizar marca de tiempo de la sesión
        cursor.execute("UPDATE IA_SESIONES SET actualizado_en = CURRENT_TIMESTAMP WHERE id = %s;", (session_id,))
        try:
            db.commit()
        except Exception:
            pass
        return msg_id
    finally:
        cursor.close()

def actualizar_titulo_sesion(db, session_id: int, titulo: str) -> None:
    """Actualiza el título descriptivo de una sesión."""
    clean_tit = titulo.strip().replace("\n", " ")
    if len(clean_tit) > 42:
        clean_tit = clean_tit[:40] + "..."
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE IA_SESIONES SET titulo = %s WHERE id = %s;", (clean_tit, session_id))
        try:
            db.commit()
        except Exception:
            pass
    finally:
        cursor.close()

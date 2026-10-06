"""
Servicio de Integracion con Google Gemini para BIMEH.
Reemplaza a Ollama como motor de IA.

Configuracion en .env:
    GEMINI_API_KEY=<tu_api_key>
    GEMINI_MODEL=gemini-3.8-flash
    AI_BACKEND=gemini
"""

import os
import re
import time
import json
import logging
import unicodedata
from typing import Dict, Any, List, Optional
from datetime import datetime

from google import genai
from google.genai import types

from app.services.query_catalog import match_catalog

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

DATABASE_SCHEMA_CONTEXT = """
Eres el Asistente de Inteligencia de Personal Militar para el batallon BIMEJ 12.
Tienes acceso de SOLO LECTURA a la base de datos PostgreSQL de BIMEH.

VISTAS DISPONIBLES:
1. v_personal_resumen:
   Columnas: id, cedula, nombre, estado ('ACTIVO'/'RETIRADO'), fecha_retiro, total_novedades_historicas
   Nombres en formato: "APELLIDOS NOMBRES" (ej: "PENA MUNOZ JORGE ENRIQUE")
   Busqueda por nombre: WHERE UPPER(nombre) LIKE '%PENA%' AND UPPER(nombre) LIKE '%JORGE%'

2. v_novedades_detalle:
   Columnas: id_registro, cedula, nombre, estado, fecha_reporte, novedad, descripcion, fecha_inicio, fecha_final
   Filtrar por mes: EXTRACT(MONTH FROM fecha_reporte) = <numero>
   Filtrar por anio: EXTRACT(YEAR FROM fecha_reporte) = <numero>

3. v_conteo_novedades:
   Columnas: novedad, total_dias_registrados, total_personal_afectado

REGLAS CRITICAS:
- Solo genera SELECT. NUNCA INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
- Siempre LIMIT <= 50.
- Para filtrar mes: usa EXTRACT(), NUNCA UPPER(novedad) LIKE '%NOMBRE_MES%'.
- Cedula exacta: WHERE cedula = <numero> (sin CAST).
"""

BANNED_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRANT|REVOKE|EXEC|EXECUTE|SHUTDOWN)\b",
    re.IGNORECASE
)
REFUSAL_PHRASES = [
    "lo siento", "no puedo", "cannot", "i'm sorry", "i cannot",
    "no puedo proporcionar", "unable to",
]


def _get_client():
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_API_KEY no configurada en .env")
    return genai.Client(api_key=key)


_cached_live_models: List[str] = []
_last_live_fetch: float = 0.0


def get_live_gemini_models(client) -> List[str]:
    """Consulta la API de Google para descubrir qué modelos están realmente disponibles en la cuenta."""
    global _cached_live_models, _last_live_fetch
    now = time.time()
    if _cached_live_models and (now - _last_live_fetch < 1800):
        return _cached_live_models
    try:
        found = []
        excluded_keywords = ["tts", "audio", "realtime", "embed", "imagen", "robotics"]
        for m in client.models.list():
            actions = getattr(m, "supported_actions", []) or []
            if not actions or "generateContent" in actions:
                clean_name = m.name.replace("models/", "").strip()
                clean_lower = clean_name.lower()
                # Excluir modelos de voz, audio o que no generen texto
                if any(ex in clean_lower for ex in excluded_keywords):
                    continue
                if "gemini" in clean_lower:
                    found.append(clean_name)
        if found:
            _cached_live_models = found
            _last_live_fetch = now
            logger.info(f"[Gemini] Modelos de texto activos detectados: {found}")
            return found
    except Exception as e:
        logger.warning(f"[Gemini] No se pudo listar modelos desde API: {e}")
    return _cached_live_models


def query_gemini(prompt, system=None, temperature=0.1, max_tokens=512, json_mode=False):
    client = _get_client()
    config_kwargs = {"temperature": temperature, "max_output_tokens": max_tokens}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"
    if system:
        config_kwargs["system_instruction"] = system

    primary_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    live_models = get_live_gemini_models(client)

    # Armar lista ordenada de modelos compatibles para generación de texto
    models_to_try = [primary_model]
    for lm in live_models:
        if lm not in models_to_try and "flash" in lm.lower():
            models_to_try.append(lm)
    for lm in live_models:
        if lm not in models_to_try:
            models_to_try.append(lm)

    last_transient_error = None
    for idx, model_name in enumerate(models_to_try):
        # 3 intentos con backoff para el modelo principal
        max_attempts = 3 if idx == 0 else 1
        for attempt in range(max_attempts):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs),
                )
                return response.text.strip() if response.text else ""
            except Exception as e:
                err_str = str(e).upper()
                is_transient = "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str or "HIGH DEMAND" in err_str
                is_unsupported = "404" in err_str or "NOT_FOUND" in err_str or "MODALIT" in err_str or "NOT SUPPORTED" in err_str or "INVALID_ARGUMENT" in err_str

                if is_transient:
                    last_transient_error = e
                    backoff = 1.5 * (attempt + 1)
                    logger.warning(
                        f"[Gemini] Saturación temporal (503/429) en '{model_name}' (intento {attempt + 1}/{max_attempts}). "
                        f"Reintentando en {backoff:.1f}s..."
                    )
                    time.sleep(backoff)
                elif is_unsupported:
                    logger.warning(f"[Gemini] Modelo '{model_name}' no soporta texto o no está disponible ({e}). Omitiendo.")
                    break
                else:
                    if idx < len(models_to_try) - 1:
                        logger.warning(f"[Gemini] Error con '{model_name}': {e}. Probando siguiente modelo...")
                        break
                    logger.error(f"[Gemini] Error no recuperable con modelo '{model_name}': {e}")
                    raise RuntimeError(f"Error de Gemini: {e}")

    logger.error(f"[Gemini] Todos los reintentos fallaron: {last_transient_error}")
    raise RuntimeError(
        f"El servicio de Gemini está experimentando alta demanda momentánea en Google Cloud. "
        f"Por favor intente nuevamente en unos segundos. (Detalle: {last_transient_error})"
    )


def _norm(text):
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _is_refusal(text):
    t = text.lower().strip()
    return any(p in t for p in REFUSAL_PHRASES)


def _auto_synthesize(user_message, query_result):
    total = query_result["total"]
    rows = query_result["rows"]
    cols = query_result["columns"]
    if total == 1 and len(cols) == 1:
        val = list(rows[0].values())[0]
        return f"Segun BIMEJ 12: **{cols[0]}** = **{val}**."
    if "cedula" in cols and "nombre" in cols:
        nombres = list({r.get("nombre", "") for r in rows[:5] if r.get("nombre")})
        muestra = ", ".join(nombres[:3])
        resto = f" y {total - 3} mas" if total > 3 else ""
        return f"Se encontraron **{total} registros** en BIMEJ 12. Personal: {muestra}{resto}."
    if "novedad" in cols and "total_dias" in cols:
        top = rows[0]
        return (f"Novedad mas registrada: **{top.get('novedad','')}** con **{top.get('total_dias','')} dias**.")
    return f"Se encontraron **{total} registros** en BIMEJ 12."


def is_sql_safe(sql):
    return not BANNED_SQL.search(sql)


def execute_safe_query(db, sql):
    if not is_sql_safe(sql):
        raise ValueError(f"SQL no permitido: {sql}")
    cursor = db.cursor()
    cursor.execute(sql)
    columns = [d[0] for d in cursor.description] if cursor.description else []
    rows_raw = cursor.fetchall()
    rows = []
    for row in rows_raw:
        rd = {}
        for i, col in enumerate(columns):
            v = row[i]
            if hasattr(v, "isoformat"):
                v = v.isoformat()
            rd[col] = v
        rows.append(rd)
    return {"columns": columns, "rows": rows, "total": len(rows)}


def get_fast_conversational_reply(text):
    msg = _norm(text)
    saludos = ["hola", "buenos dias", "buenas tardes", "buenas noches", "buen dia"]
    if any(s in msg for s in saludos):
        hora = datetime.now().hour
        saludo = "Buenos dias" if hora < 12 else "Buenas tardes" if hora < 19 else "Buenas noches"
        return "saludo", f"{saludo}, mi Comandante. Soy el Asistente de Personal de BIMEJ 12. Como le puedo ayudar?"
    gracias = ["gracias", "muchas gracias", "perfecto", "excelente"]
    if any(g in msg for g in gracias):
        return "cortesia", "A sus ordenes, mi Comandante. Requiere alguna consulta adicional?"

    ayuda_keywords = [
        "que haces", "que puedes hacer", "quien eres", "para que sirves",
        "como funcionas", "como te llamas", "que sabes hacer", "ayuda", "comandos",
        "que consultas", "consultas sql", "que puedo consultar", "que puedo preguntar",
        "ejemplos", "ejemplos de consultas"
    ]
    if any(k in msg for k in ayuda_keywords):
        return "ayuda", (
            "A sus órdenes, mi Comandante. Soy el Asistente de Inteligencia de Personal de BIMEJ 12.\n\n"
            "Puedo responder consultas operacionales en lenguaje natural sobre:\n\n"
            "• **Efectivos:** Total de personal activo y retirado (ej: *'¿Cuántos efectivos activos hay?'*).\n"
            "• **Novedades:** Permisos, vacaciones, incapacidades médicas y excusas (ej: *'Personal con incapacidad este mes'*).\n"
            "• **Compañías:** Distribución de personal y fuerza disponible (ej: *'Personal activo por compañías'*).\n"
            "• **Historial individual:** Búsqueda por nombre o cédula (ej: *'Novedades de Gómez en julio'* o *'Historial de cédula 123456'*).\n"
            "• **Ranking:** Novedades más recurrentes (ej: *'¿Cuál es la novedad más frecuente en el batallón?'*).\n"
            "• **Apreciación militar:** Boletín de situación general (puede usar el botón 'Apreciación' superior)."
        )

    despedidas = ["adios", "chao", "hasta luego", "hasta pronto", "nos vemos"]
    if any(d in msg for d in despedidas):
        return "despedida", "Hasta luego, mi Comandante. Quedo a su disposición para futuras consultas."

    return None, None


def should_apply_militar_context(user_message, active_militar):
    if not active_militar:
        return False
    msg = user_message.lower()
    active_cedula = str(active_militar.get("cedula", ""))
    cedulas = re.findall(r"\b\d{6,10}\b", msg)
    if cedulas:
        return all(c == active_cedula for c in cedulas)
    global_triggers = ["todo el personal", "todo el batallon", "todos los militares", "en total"]
    if any(t in msg for t in global_triggers):
        return False
    followup_kw = [
        "su ", "sus ", "el mismo", "este personal", "novedad", "novedades",
        "historial", "permisos", "vacaciones", "incapacidad", "estado",
        "presente", "registrada", "frecuente", "meses",
    ]
    return any(k in msg for k in followup_kw)


def process_user_query(user_message, db, history=None, active_militar=None):
    model_label = f"gemini ({os.getenv('GEMINI_MODEL', 'gemini-3.8-flash')})"
    now = datetime.now()

    # 1. Respuestas rapidas sin IA
    conv_tipo, fast_reply = get_fast_conversational_reply(user_message)
    if conv_tipo:
        return {"type": "conversation", "answer": fast_reply, "sql": None,
                "columns": [], "rows": [], "total_records": 0,
                "model": model_label, "active_militar": active_militar}

    # 2. Fast-path catalogo
    is_followup_pre = should_apply_militar_context(user_message, active_militar)
    catalog_active = active_militar if is_followup_pre else None
    catalog_sql, catalog_desc = match_catalog(user_message, active_militar=catalog_active, current_year=now.year)

    if catalog_sql:
        logger.info(f"[Catalogo] Fast-path: {catalog_desc}")
        try:
            cat_result = execute_safe_query(db, catalog_sql)
        except Exception as e:
            try: db.rollback()
            except: pass
            logger.warning(f"[Catalogo] Fallo: {e}. Cayendo a Gemini.")
            cat_result = None

        if cat_result is not None:
            if cat_result["total"] == 0:
                synth = "Se consulto BIMEJ 12 pero **no se encontraron registros coincidentes**."
            else:
                try:
                    synth = query_gemini(
                        f"Eres el Asistente Militar de BIMEJ 12.\nUsuario: \"{user_message}\"\n"
                        f"Resultados ({cat_result['total']} registros): {json.dumps(cat_result['rows'][:8], ensure_ascii=False)}\n"
                        f"Redacta un resumen militar claro en maximo 2 oraciones.",
                        temperature=0.2, max_tokens=150
                    )
                    if _is_refusal(synth):
                        synth = _auto_synthesize(user_message, cat_result)
                except:
                    synth = _auto_synthesize(user_message, cat_result)

            detected_m = catalog_active
            if cat_result.get("rows"):
                first = cat_result["rows"][0]
                cedulas_r = {str(r.get("cedula")) for r in cat_result["rows"] if r.get("cedula")}
                if "cedula" in first and len(cedulas_r) == 1:
                    detected_m = {"cedula": str(first.get("cedula")),
                                  "nombre": str(first.get("nombre") or (active_militar.get("nombre") if active_militar else "")).strip()}
            return {"type": "data", "answer": synth, "sql": catalog_sql,
                    "columns": cat_result["columns"], "rows": cat_result["rows"],
                    "total_records": cat_result["total"],
                    "model": f"{model_label} (catalogo)", "active_militar": detected_m}

    # 3. Slow-path: Gemini genera SQL
    is_followup = should_apply_militar_context(user_message, active_militar)
    militar_ctx = ""
    if is_followup and active_militar:
        ced = active_militar.get("cedula")
        nom = active_militar.get("nombre", "")
        militar_ctx = f"\nMILITAR EN CONTEXTO: {nom} | cedula = {ced}. Filtra SIEMPRE por cedula = {ced}.\n"

    fecha_hoy = now.strftime("%Y-%m-%d")
    sql_prompt = (
        f"{DATABASE_SCHEMA_CONTEXT}\n{militar_ctx}\n"
        f"FECHA ACTUAL: {fecha_hoy}  ANo ACTUAL: {now.year}\n\n"
        f"PREGUNTA: {user_message}\n\n"
        f"Responde UNICAMENTE con JSON:\n"
        f'{{\"type\": \"sql\", \"sql\": \"<SELECT ...>\"}}\n'
        f"o si no requiere BD:\n"
        f'{{\"type\": \"conversation\", \"answer\": \"<respuesta>\"}}\n'
        f"CRITICO: Para filtrar por mes usa EXTRACT(MONTH FROM fecha_reporte)=<num>, NUNCA LIKE con nombre del mes."
    )

    raw = query_gemini(prompt=sql_prompt, temperature=0.05, max_tokens=400, json_mode=True)
    try:
        parsed = json.loads(raw)
    except:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        parsed = json.loads(m.group()) if m else {}

    if parsed.get("type") == "conversation":
        return {"type": "conversation", "answer": parsed.get("answer", raw),
                "sql": None, "columns": [], "rows": [], "total_records": 0,
                "model": model_label, "active_militar": active_militar}

    sql = parsed.get("sql", "").strip()
    if not sql or not is_sql_safe(sql):
        answer_text = parsed.get("answer") or "No pude generar una consulta segura para esa solicitud."
        return {"type": "conversation", "answer": answer_text,
                "sql": None, "columns": [], "rows": [], "total_records": 0,
                "model": model_label, "active_militar": active_militar}

    # Ejecutar con auto-correccion
    query_result = None
    validated_sql = sql
    last_error = None
    for attempt in range(3):
        try:
            query_result = execute_safe_query(db, validated_sql)
            break
        except Exception as e:
            last_error = str(e)
            try: db.rollback()
            except: pass
            if attempt < 2:
                try:
                    fixed = query_gemini(
                        f"SQL fallo con error: {last_error}\nSQL: {validated_sql}\nDevuelve SOLO el SQL corregido.",
                        temperature=0.0, max_tokens=300
                    )
                    fixed = re.sub(r"```\w*\n?", "", fixed).strip()
                    if fixed and is_sql_safe(fixed):
                        validated_sql = fixed
                except: pass

    if query_result is None:
        return {"type": "error", "answer": f"Error ejecutando consulta: {last_error}",
                "sql": validated_sql, "columns": [], "rows": [], "total_records": 0,
                "model": model_label, "active_militar": active_militar}

    # Sintesis
    if query_result["total"] == 0:
        synthesis = "Se consulto BIMEJ 12 pero **no se encontraron registros coincidentes**."
    else:
        try:
            synthesis = query_gemini(
                f"Asistente Militar BIMEJ 12.\nUsuario: \"{user_message}\"\n"
                f"Resultados ({query_result['total']} registros): {json.dumps(query_result['rows'][:8], ensure_ascii=False)}\n"
                f"Redacta resumen militar claro en 2-3 oraciones.",
                temperature=0.2, max_tokens=180
            )
            if _is_refusal(synthesis):
                synthesis = _auto_synthesize(user_message, query_result)
        except:
            synthesis = _auto_synthesize(user_message, query_result)

    detected_m = active_militar if is_followup else None
    if query_result.get("rows"):
        first = query_result["rows"][0]
        cedulas_r = {str(r.get("cedula")) for r in query_result["rows"] if r.get("cedula")}
        if "cedula" in first and len(cedulas_r) == 1:
            detected_m = {"cedula": str(first.get("cedula")),
                          "nombre": str(first.get("nombre") or (active_militar.get("nombre") if active_militar else "")).strip()}

    return {"type": "data", "answer": synthesis, "sql": validated_sql,
            "columns": query_result["columns"], "rows": query_result["rows"],
            "total_records": query_result["total"], "model": model_label,
            "active_militar": detected_m}


def generate_apreciacion(db):
    now = datetime.now()
    def run(sql):
        try: return execute_safe_query(db, sql)
        except: return {"rows": [{}], "total": 0, "columns": []}

    total = run("SELECT COUNT(*) AS t FROM v_personal_resumen")["rows"][0].get("t", 0)
    activos = run("SELECT COUNT(*) AS t FROM v_personal_resumen WHERE estado='ACTIVO'")["rows"][0].get("t", 0)
    retirados = run("SELECT COUNT(*) AS t FROM v_personal_resumen WHERE estado='RETIRADO'")["rows"][0].get("t", 0)
    top_nov = run("SELECT novedad, total_dias_registrados FROM v_conteo_novedades ORDER BY total_dias_registrados DESC LIMIT 5")["rows"]
    criticos = run(f"SELECT cedula, nombre, COUNT(*) AS dias FROM v_novedades_detalle WHERE EXTRACT(YEAR FROM fecha_reporte)={now.year} GROUP BY cedula, nombre HAVING COUNT(*)>=10 ORDER BY dias DESC LIMIT 10")["rows"]

    prompt = (
        f"Actua como el Oficial de Personal (S1) del Batallon BIMEJ 12.\n"
        f"Redacta una APRECIACION DE SITUACION Y ESTADO DE FUERZA para el Comandante.\n\n"
        f"DATOS ({now.strftime('%B %Y')}):\n"
        f"- Total: {total} | Activos: {activos} | Retirados: {retirados}\n"
        f"- Disponibilidad: {round(activos/total*100,1) if total else 0}%\n"
        f"- Top novedades: {json.dumps(top_nov, ensure_ascii=False)}\n"
        f"- Casos criticos (>=10 dias): {json.dumps(criticos, ensure_ascii=False)}\n\n"
        f"Estructura en Markdown: Encabezado, Diagnostico, Analisis Novedades, Alertas, Recomendacion S1.\n"
        f"Vocabulario castrence formal."
    )
    briefing = query_gemini(prompt=prompt, temperature=0.3, max_tokens=1024)
    return {"periodo": now.strftime("%B %Y"),
            "kpis": {"total_personal": total, "total_activos": activos, "total_retirados": retirados,
                     "top_novedades": top_nov, "casos_criticos": criticos},
            "apreciacion": briefing,
            "fecha_generacion": now.strftime("%Y-%m-%d %H:%M:%S")}

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
   NOTA CRITICA: fecha_reporte es tipo VARCHAR ('YYYY-MM-DD').
   Para filtrar por mes/año usa SIEMPRE:
     fecha_reporte LIKE '<YYYY>-<MM>-%'  (ej: fecha_reporte LIKE '2026-08-%' para agosto de 2026)
     o si usas EXTRACT, castea a fecha: EXTRACT(MONTH FROM fecha_reporte::date) = <num>

3. v_conteo_novedades:
   Columnas: novedad, total_dias_registrados, total_personal_afectado

REGLAS CRITICAS:
- Solo genera SELECT. NUNCA INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
- Siempre LIMIT <= 50.
- Para filtrar mes/año usa LIKE 'YYYY-MM-%' (ej: '2026-08-%') o fecha_reporte::date.
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

    # Armar lista con el modelo principal y hasta 2 alternativas
    models_to_try = [primary_model]
    for fallback in ["gemini-2.5-pro", "gemini-3.8-pro", "gemini-2.0-flash-001"]:
        if fallback in live_models and fallback not in models_to_try:
            models_to_try.append(fallback)
            if len(models_to_try) >= 3:
                break

    last_error_detail = None
    for idx, model_name in enumerate(models_to_try):
        max_attempts = 2 if idx == 0 else 1
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
                last_error_detail = e
                is_quota = "RESOURCE_EXHAUSTED" in err_str or "QUOTA" in err_str or "429" in err_str
                is_transient = ("503" in err_str or "UNAVAILABLE" in err_str or "HIGH DEMAND" in err_str) and not is_quota
                is_unsupported = "404" in err_str or "NOT_FOUND" in err_str or "MODALIT" in err_str or "NOT SUPPORTED" in err_str or "INVALID_ARGUMENT" in err_str

                if is_quota:
                    logger.warning(f"[Gemini] Cuota agotada en '{model_name}'. Probando siguiente modelo...")
                    break
                elif is_transient:
                    if attempt < max_attempts - 1:
                        logger.warning(f"[Gemini] Saturación temporal (503) en '{model_name}'. Reintentando en 1s...")
                        time.sleep(1.0)
                    else:
                        break
                elif is_unsupported:
                    logger.warning(f"[Gemini] Modelo '{model_name}' no soportado ({e}). Omitiendo.")
                    break
                else:
                    if idx < len(models_to_try) - 1:
                        logger.warning(f"[Gemini] Error con '{model_name}': {e}. Probando fallback...")
                        break
                    logger.error(f"[Gemini] Error no recuperable con '{model_name}': {e}")
                    raise RuntimeError(f"Error de Gemini: {e}")

    err_str = str(last_error_detail).upper()
    if "RESOURCE_EXHAUSTED" in err_str or "QUOTA" in err_str or "429" in err_str:
        raise RuntimeError(
            "La cuota gratuita diaria de la API de Google Gemini (20 consultas/día en Free Tier) ha sido alcanzada por hoy. "
            "Las consultas operacionales y tablas del catálogo militar continúan 100% operativas."
        )
    raise RuntimeError(
        f"El servicio de Gemini está experimentando alta demanda momentánea en Google Cloud. "
        f"Por favor intente nuevamente en unos segundos. (Detalle: {last_error_detail})"
    )


def _norm(text):
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _is_refusal(text):
    t = text.lower().strip()
    return any(p in t for p in REFUSAL_PHRASES)


def _auto_synthesize(user_message, query_result):
    total = query_result.get("total", 0)
    rows = query_result.get("rows", [])
    cols = query_result.get("columns", [])

    if total == 0:
        return "Se consultó la base de datos de BIMEJ 12 pero **no se encontraron registros coincidentes** para los criterios indicados."

    # Caso 1: Un solo valor escalar (ej: COUNT)
    if total == 1 and len(cols) == 1:
        col = cols[0]
        val = list(rows[0].values())[0]
        if "activo" in col.lower():
            return f"En el Batallón BIMEJ 12 se registran **{val} efectivos activos** en el personal."
        if "retirado" in col.lower():
            return f"En el Batallón BIMEJ 12 se registran **{val} efectivos retirados**."
        return f"Según los registros de BIMEJ 12: **{col}** = **{val}**."

    # Caso 2: Reporte de fechas con novedad (ej: días de permiso/vacaciones/etc.)
    if "fecha_reporte" in cols:
        fechas = [str(r.get("fecha_reporte", "")) for r in rows if r.get("fecha_reporte")]
        nombres = list({r.get("nombre", "") for r in rows if r.get("nombre")})
        nombre_str = f" para **{nombres[0]}**" if len(nombres) == 1 else ""
        novedades = list({r.get("novedad", "") for r in rows if r.get("novedad")})
        novedad_str = f" con novedad **{novedades[0]}**" if len(novedades) == 1 else ""

        if total <= 6:
            fechas_fmt = ", ".join(fechas)
            return f"Se registran **{total} días**{novedad_str}{nombre_str} en BIMEJ 12: **{fechas_fmt}**."
        else:
            return f"Se registran **{total} días**{novedad_str}{nombre_str} en BIMEJ 12 (desde **{fechas[0]}** hasta **{fechas[-1]}**)."

    # Caso 3: Ranking de novedades frecuentes
    if "novedad" in cols and ("total_dias" in cols or "total_dias_registrados" in cols):
        top = rows[0]
        nov_nombre = top.get("novedad", "")
        dias = top.get("total_dias") or top.get("total_dias_registrados", 0)
        return f"Novedad más registrada en BIMEJ 12: **{nov_nombre}** con un total de **{dias} días** acumulados."

    # Caso 4: Lista de personal
    if "cedula" in cols and "nombre" in cols:
        nombres = [r.get("nombre", "") for r in rows[:5] if r.get("nombre")]
        muestra = ", ".join(nombres[:3])
        resto = f" y {total - 3} más" if total > 3 else ""
        return f"Se encontraron **{total} registros** en BIMEJ 12. Personal: **{muestra}{resto}**."

    return f"Se encontraron **{total} registros** coincidentes en la base de datos de BIMEJ 12."


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

    aclaracion_triggers = [
        "por que", "porque", "por que no", "a que se debe",
        "por que motivo", "por que razon", "explicame", "explica"
    ]
    clean_msg = msg.strip("?¿! .")
    if clean_msg in aclaracion_triggers:
        return "aclaracion", (
            "Mi Comandante, cuando no se encuentran registros para una consulta específica, "
            "se debe a que en los partes oficiales de BIMEJ 12 la persona no presenta esa novedad en ese período "
            "(se encontraba disponible/en servicio ordinario, o la novedad corresponde a otro mes). "
            "Puede consultar su historial completo diciendo: *'Historial de novedades de [Nombre o Cédula]'*."
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
        f"CRITICO: fecha_reporte es VARCHAR ('YYYY-MM-DD'). Para filtrar por mes usa fecha_reporte LIKE '{now.year}-<MM>-%' o EXTRACT(MONTH FROM fecha_reporte::date)=<num>."
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
    if query_result["total"] == 0 or query_result["total"] <= 5:
        synthesis = _auto_synthesize(user_message, query_result)
    else:
        try:
            synthesis = query_gemini(
                f"Asistente Militar BIMEJ 12.\nUsuario: \"{user_message}\"\n"
                f"Resultados ({query_result['total']} registros): {json.dumps(query_result['rows'][:8], ensure_ascii=False)}\n"
                f"Redacta resumen militar claro en 2 oraciones.",
                temperature=0.2, max_tokens=150
            )
            if _is_refusal(synthesis):
                synthesis = _auto_synthesize(user_message, query_result)
        except Exception:
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
    criticos = run(f"SELECT cedula, nombre, COUNT(*) AS dias FROM v_novedades_detalle WHERE fecha_reporte LIKE '{now.year}-%' GROUP BY cedula, nombre HAVING COUNT(*)>=10 ORDER BY dias DESC LIMIT 10")["rows"]

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

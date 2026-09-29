"""
Servicio de Integración con Ollama (IA Local) para BIMEH.
Procesa consultas en lenguaje natural, genera sentencias SQL seguras (solo lectura)
y redacta apreciaciones operacionales de personal para la comandancia.
"""

import os
import re
import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

DATABASE_SCHEMA_CONTEXT = """
Eres el Asistente de Inteligencia de Personal Militar para el batallón BIMEJ 12.
Tienes acceso de SOLO LECTURA a la base de datos PostgreSQL de BIMEH.

TABLAS Y ESQUEMA REAL:
1. PERSONAL:
   - id (INTEGER PRIMARY KEY)
   - cedula (BIGINT, documento de identidad único)
   - nombre (VARCHAR, apellidos y nombres del integrante militar)
   - fecha_retiro (VARCHAR, NULL o vacío si el militar está ACTIVO; contiene fecha si está RETIRADO)
   * REGLA ESTRICTA: La tabla PERSONAL ÚNICAMENTE tiene id, cedula, nombre, fecha_retiro. NO contiene compania, cargo, rango ni motivo_retiro. NUNCA hagas SELECT p.compania ni SELECT p.cargo.

2. REPORTES:
   - id (INTEGER PRIMARY KEY)
   - fecha (VARCHAR formato 'YYYY-MM-DD', representa el día del reporte diario)
   - archivo (VARCHAR)

3. SUB_NOVEDADES:
   - id (INTEGER PRIMARY KEY)
   - nombre (VARCHAR, nombre de la novedad: ej. 'VACACIONES', 'PERMISO', 'INCAPACIDAD MEDICA', 'COMISION DEL SERVICIO', 'LICENCIA', 'HOSPITALIZADO', 'AISLAMIENTO', 'EXCUSA DE SERVICIO', 'SANCION DISCIPLINARIA', etc.)

4. REGISTRO_PERSONAL:
   - id (INTEGER PRIMARY KEY)
   - id_reporte (INTEGER REFERENCES REPORTES.id)
   - id_personal (INTEGER REFERENCES PERSONAL.id)
   - id_sub_novedad (INTEGER REFERENCES SUB_NOVEDADES.id)
   - descripcion (TEXT, detalles, diagnóstico o justificación de la novedad)
   - fecha_inicio (VARCHAR)
   - fecha_final (VARCHAR)

REGLAS CRÍTICAS DE SQL:
- Solo genera consultas SELECT. NUNCA generes INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
- Militar ACTIVO: (p.fecha_retiro IS NULL OR p.fecha_retiro = '').
- Militar RETIRADO: (p.fecha_retiro IS NOT NULL AND p.fecha_retiro != '').
- Para buscar por nombre: UPPER(p.nombre) LIKE '%TERMINO%' (si buscan nombres y apellidos ej: 'JORGE PEÑA', busca '%JORGE%PEÑA%').
- Para buscar por cédula: CAST(p.cedula AS TEXT) LIKE '%TERMINO%'.
- Para consultar información o estado de un militar específico (ej: 'jorge peña'):
  SELECT p.cedula, p.nombre, CASE WHEN (p.fecha_retiro IS NULL OR p.fecha_retiro = '') THEN 'ACTIVO' ELSE 'RETIRADO' END AS estado, p.fecha_retiro, COUNT(rp.id) as total_novedades_registradas
  FROM PERSONAL p
  LEFT JOIN REGISTRO_PERSONAL rp ON rp.id_personal = p.id
  WHERE UPPER(p.nombre) LIKE '%JORGE%PEÑA%'
  GROUP BY p.cedula, p.nombre, p.fecha_retiro;
- Para ver historial de novedades o ausencias de un militar:
  SELECT p.cedula, p.nombre, r.fecha, sn.nombre AS novedad, rp.descripcion, rp.fecha_inicio, rp.fecha_final
  FROM PERSONAL p
  JOIN REGISTRO_PERSONAL rp ON rp.id_personal = p.id
  JOIN REPORTES r ON r.id = rp.id_reporte
  LEFT JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad
  WHERE UPPER(p.nombre) LIKE '%JORGE%PEÑA%'
  ORDER BY r.fecha DESC LIMIT 20;
- Para contar días acumulados de una novedad: COUNT(rp.id) o COUNT(DISTINCT r.fecha).
- Para ordenar por mayor incidencia usa ORDER BY COUNT(rp.id) DESC.
- Si la consulta no tiene LIMIT, incluye siempre LIMIT 50 para evitar sobrecarga.
"""

BANNED_SQL_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRANT|REVOKE|EXEC|EXECUTE|SHUTDOWN)\b",
    re.IGNORECASE
)


def get_ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")


def get_configured_model() -> str:
    return os.getenv("OLLAMA_MODEL", OLLAMA_DEFAULT_MODEL)


def check_ollama_status() -> Dict[str, Any]:
    """Verifica si Ollama está levantado y qué modelos tiene disponibles."""
    base_url = get_ollama_base_url()
    url = f"{base_url}/api/tags"
    model_name = get_configured_model()
    try:
        with httpx.Client(timeout=4.0) as client:
            res = client.get(url)
            if res.status_code == 200:
                data = res.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Buscar coincidencia exacta o por prefijo (ej: llama3.1:8b o llama3.1:latest)
                model_found = any(
                    m == model_name or m.startswith(model_name.split(":")[0]) 
                    for m in models
                )
                return {
                    "online": True,
                    "base_url": base_url,
                    "model_configured": model_name,
                    "model_available": model_found,
                    "models_installed": models,
                    "error": None
                }
            else:
                return {
                    "online": False,
                    "base_url": base_url,
                    "model_configured": model_name,
                    "model_available": False,
                    "models_installed": [],
                    "error": f"Ollama respondió con código {res.status_code}"
                }
    except Exception as e:
        return {
            "online": False,
            "base_url": base_url,
            "model_configured": model_name,
            "model_available": False,
            "models_installed": [],
            "error": f"No se pudo conectar a Ollama en {base_url}. Asegúrese de que Ollama o el túnel estén activos."
        }


def extract_sql_from_text(text: str) -> Optional[str]:
    """Extrae código SQL de bloques markdown o texto plano."""
    match = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        query = match.group(1).strip()
    else:
        query = text.strip()

    # Si contiene un SELECT, recortar desde el SELECT
    select_idx = query.upper().find("SELECT")
    with_idx = query.upper().find("WITH")

    start_idx = -1
    if select_idx != -1 and with_idx != -1:
        start_idx = min(select_idx, with_idx)
    elif select_idx != -1:
        start_idx = select_idx
    elif with_idx != -1:
        start_idx = with_idx

    if start_idx != -1:
        query = query[start_idx:].strip()

    # Limpiar punto y coma final
    if query.endswith(";"):
        query = query[:-1].strip()

    return query if query else None


def validate_sql(sql: str) -> tuple[bool, str]:
    """Valida que la consulta sea estrictamente segura y de solo lectura."""
    if not sql:
        return False, "La consulta SQL generada está vacía."

    # Rechazar sentencias peligrosas
    banned_match = BANNED_SQL_KEYWORDS.search(sql)
    if banned_match:
        return False, f"Sentencia no permitida detectada: {banned_match.group(0)}. Solo se permiten consultas de lectura."

    upper_sql = sql.upper().strip()
    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
        return False, "La consulta debe iniciar estrictamente con SELECT o WITH."

    # Asegurar LIMIT razonable
    if "LIMIT" not in upper_sql:
        sql = f"{sql} LIMIT 50"

    return True, sql


def execute_safe_query(db, sql: str) -> Dict[str, Any]:
    """Ejecuta una consulta SQL validada contra PostgreSQL y retorna datos serializables."""
    cursor = db.cursor()
    cursor.execute(sql)
    
    columns = [col[0] for col in cursor.description] if cursor.description else []
    raw_rows = cursor.fetchall() if cursor.description else []

    formatted_rows = []
    for r in raw_rows:
        row_dict = {}
        for col_name, val in zip(columns, r):
            if isinstance(val, (datetime,)):
                row_dict[col_name] = val.strftime("%Y-%m-%d")
            else:
                row_dict[col_name] = val
        formatted_rows.append(row_dict)

    return {
        "columns": columns,
        "rows": formatted_rows,
        "total": len(formatted_rows),
        "sql": sql
    }


def query_ollama(
    prompt: str,
    system: Optional[str] = None,
    format: Optional[str] = None,
    temperature: float = 0.1,
    timeout: float = 90.0
) -> str:
    """Envía un prompt a Ollama y retorna la respuesta de texto."""
    model = get_configured_model()
    base_url = get_ollama_base_url()
    url = f"{base_url}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9
        }
    }
    if format:
        payload["format"] = format
    if system:
        payload["system"] = system

    try:
        with httpx.Client(timeout=timeout) as client:
            res = client.post(url, json=payload)
            if res.status_code == 200:
                return res.json().get("response", "").strip()
            else:
                raise RuntimeError(f"Error de Ollama ({res.status_code}): {res.text}")
    except httpx.ConnectError:
        raise RuntimeError(f"No fue posible conectarse a Ollama en {base_url}. Asegúrate de que Ollama o el túnel estén activos.")
    except httpx.ReadTimeout:
        raise RuntimeError("El modelo de Ollama tardó demasiado en responder (tiempo de espera agotado).")


def process_user_query(user_message: str, db) -> Dict[str, Any]:
    """
    Procesa un mensaje en lenguaje natural:
    1. Determina si requiere consulta de base de datos.
    2. Si requiere SQL, lo genera y valida.
    3. Ejecuta la consulta en PostgreSQL con auto-corrección (Self-Healing).
    4. Solicita a la IA que sintetice los resultados en lenguaje militar claro.
    """
    model = get_configured_model()

    system_intent = f"""
{DATABASE_SCHEMA_CONTEXT}

DIRECTIVAS Y REGLAS DE DECISIÓN OBLIGATORIAS:
Eres el motor Text-to-SQL de BIMEH. Tu misión principal es responder mediante consultas SQL PostgreSQL.

1. REGLA FUNDAMENTAL DE CONSULTA A BASE DE DATOS:
- SI la solicitud del usuario menciona nombres o apellidos de personas (ej: 'jorge peña', 'rodriguez', etc.), números de cédula, novedades (permisos, vacaciones, excusas, etc.), ausencias, fechas, conteos de personal, listas o preguntas sobre el estado militar:
  DEBES responder OBLIGATORIAMENTE con {{"tipo": "sql", "sql": "SELECT ...", "explicacion": "..."}}.
- NUNCA respondas que no tienes información de un militar ni pidas más detalles. TÚ NO CONOCES AL PERSONAL EN MEMORIA, tu deber es buscarlo en la base de datos usando SQL en la tabla PERSONAL.
- En la consulta SQL para buscar personas por nombre, usa siempre: `UPPER(p.nombre) LIKE '%PALABRA1%PALABRA2%'`.

2. REGLA DE CONVERSACIÓN SIMPLE:
- ÚNICAMENTE clasifica como {{"tipo": "conversacion", "respuesta": "..."}} si el usuario envía un saludo simple (ej: 'hola', 'buenos días', 'saludos') o un agradecimiento ('gracias', 'hasta luego') o pregunta 'qué puedes hacer'.

EJEMPLOS DE REFERENCIA (FEW-SHOT):
Usuario: "informacion sobre jorge peña muñoz"
Respuesta:
{{"tipo": "sql", "sql": "SELECT p.cedula, p.nombre, CASE WHEN (p.fecha_retiro IS NULL OR p.fecha_retiro = '') THEN 'ACTIVO' ELSE 'RETIRADO' END AS estado, p.fecha_retiro, COUNT(rp.id) AS total_novedades FROM PERSONAL p LEFT JOIN REGISTRO_PERSONAL rp ON rp.id_personal = p.id WHERE UPPER(p.nombre) LIKE '%JORGE%PEÑA%' GROUP BY p.cedula, p.nombre, p.fecha_retiro LIMIT 10", "explicacion": "Consultando registro y estado militar de Jorge Peña"}}

Usuario: "cuantos militares activos hay en total"
Respuesta:
{{"tipo": "sql", "sql": "SELECT COUNT(*) AS total_activos FROM PERSONAL WHERE fecha_retiro IS NULL OR fecha_retiro = ''", "explicacion": "Contando total de efectivos activos"}}

Usuario: "quienes estan en vacaciones"
Respuesta:
{{"tipo": "sql", "sql": "SELECT p.cedula, p.nombre, sn.nombre AS novedad, r.fecha, rp.descripcion FROM PERSONAL p JOIN REGISTRO_PERSONAL rp ON rp.id_personal = p.id JOIN REPORTES r ON r.id = rp.id_reporte JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad WHERE UPPER(sn.nombre) LIKE '%VACACIONES%' ORDER BY r.fecha DESC LIMIT 50", "explicacion": "Personal con novedad de vacaciones"}}

Usuario: "hola, que puedes hacer?"
Respuesta:
{{"tipo": "conversacion", "respuesta": "Un cordial saludo militar. Soy el Asistente de Inteligencia de BIMEJ 12. Puedo consultar en la base de datos el estado de cualquier militar, verificar novedades del día, contar efectivos activos y generar partes de fuerza disponible."}}

Devuelve ÚNICAMENTE un objeto JSON válido.
"""

    prompt = f"Solicitud del usuario: \"{user_message}\""
    raw_response = query_ollama(prompt=prompt, system=system_intent, format="json", temperature=0.0)

    # Intentar parsear JSON
    tipo = "conversacion"
    generated_sql = None
    direct_answer = ""

    try:
        clean_json = raw_response
        json_match = re.search(r"\{[\s\S]*\}", raw_response)
        if json_match:
            clean_json = json_match.group(0)
        
        parsed = json.loads(clean_json)
        tipo = parsed.get("tipo", "conversacion")
        generated_sql = parsed.get("sql")
        direct_answer = parsed.get("respuesta") or parsed.get("explicacion") or ""
    except Exception:
        extracted = extract_sql_from_text(raw_response)
        if extracted and "SELECT" in extracted.upper():
            tipo = "sql"
            generated_sql = extracted
        else:
            tipo = "conversacion"
            direct_answer = raw_response

    # Si es conversación simple, retornar directamente
    if tipo == "conversacion" or not generated_sql:
        return {
            "type": "conversation",
            "answer": direct_answer or raw_response,
            "sql": None,
            "columns": [],
            "rows": [],
            "total_records": 0,
            "model": model
        }

    # Si es SQL, validar y ejecutar con bucle de auto-corrección (Self-Healing SQL)
    max_retries = 2
    query_result = None
    last_sql_err = None
    validated_sql = generated_sql

    for intento in range(max_retries + 1):
        is_valid, validated_sql = validate_sql(generated_sql)
        if not is_valid:
            last_sql_err = validated_sql
            break

        try:
            query_result = execute_safe_query(db, validated_sql)
            break  # ¡Consulta ejecutada con éxito!
        except Exception as sql_err:
            last_sql_err = sql_err
            logger.warning(
                f"[Auto-Corrección IA] Intento {intento + 1}/{max_retries + 1} falló al ejecutar SQL: {sql_err}. "
                "Enviando feedback de error a Ollama para auto-reparación..."
            )
            if intento < max_retries:
                fix_prompt = f"""
La consulta SQL que generaste previamente falló al ejecutarse en PostgreSQL con el siguiente error:

CONSULTA FALLIDA:
{validated_sql}

ERROR DE POSTGRESQL:
{str(sql_err)}

ESQUEMA EXACTO Y REAL DE LA BASE DE DATOS (REVISA LOS NOMBRES DE TABLAS Y COLUMNAS):
{DATABASE_SCHEMA_CONTEXT}

SOLICITUD ORIGINAL DEL USUARIO:
"{user_message}"

INSTRUCCIÓN DE CORRECCIÓN:
Analiza el error reportado por PostgreSQL y ajusta la consulta SQL utilizando ÚNICAMENTE las columnas y tablas existentes.
Por ejemplo: La tabla PERSONAL sólo tiene: id, cedula, nombre, fecha_retiro (NO existe compania ni cargo).
Responde ÚNICAMENTE en formato JSON válido:
{{"tipo": "sql", "sql": "SELECT ...", "explicacion": "Explicación de cómo corregiste el error..."}}
"""
                try:
                    fix_response = query_ollama(prompt=fix_prompt, format="json", temperature=0.0)
                    json_match = re.search(r"\{[\s\S]*\}", fix_response)
                    if json_match:
                        parsed_fix = json.loads(json_match.group(0))
                        generated_sql = parsed_fix.get("sql") or generated_sql
                    else:
                        extracted = extract_sql_from_text(fix_response)
                        if extracted:
                            generated_sql = extracted
                        else:
                            break
                except Exception as fix_call_err:
                    logger.error(f"Error llamando a Ollama durante auto-corrección: {fix_call_err}")
                    break

    if not query_result:
        return {
            "type": "error",
            "answer": f"Error en la consulta a la base de datos tras reintentos automáticos de auto-corrección: {str(last_sql_err)}",
            "sql": validated_sql,
            "columns": [],
            "rows": [],
            "total_records": 0,
            "model": model
        }

    # Sintetizar los resultados con la IA (o reporte directo si 0 registros)
    if query_result["total"] == 0:
        synthesis = f"Se consultó la base de datos de BIMEJ 12 para su solicitud, pero **no se encontraron registros coincidentes**."
    else:
        synthesis_prompt = f"""
Eres el Asistente Militar de BIMEJ 12.
El usuario preguntó: "{user_message}"
Se ejecutó con éxito la consulta SQL en PostgreSQL:
{validated_sql}

Resultados obtenidos ({query_result['total']} registros encontrados):
{json.dumps(query_result['rows'][:15], ensure_ascii=False)}

Por favor, redacta una respuesta clara, concisa y formal (estilo parte militar para BIMEJ 12).
Resume los hallazgos principales, totales y casos más destacados si los hay.
No repitas toda la tabla registro por registro si son muchos, ya que se le mostrará la tabla completa al usuario en pantalla.
"""
        try:
            synthesis = query_ollama(prompt=synthesis_prompt, temperature=0.3)
        except Exception:
            synthesis = f"Se encontraron **{query_result['total']} registros** que coinciden con su consulta."

    return {
        "type": "data",
        "answer": synthesis,
        "sql": validated_sql,
        "columns": query_result["columns"],
        "rows": query_result["rows"],
        "total_records": query_result["total"],
        "model": model
    }


def generate_executive_briefing(mes: Optional[str], db) -> Dict[str, Any]:
    """
    Recopila métricas consolidadas de personal y novedades de BIMEH
    y genera una Apreciación de Situación de Personal para el comando.
    """
    cursor = db.cursor()

    # 1. Total de personal activo y retirado
    cursor.execute("""
        SELECT 
            COUNT(*) AS total,
            COUNT(CASE WHEN fecha_retiro IS NULL OR fecha_retiro = '' THEN 1 END) AS activos,
            COUNT(CASE WHEN fecha_retiro IS NOT NULL AND fecha_retiro != '' THEN 1 END) AS retirados
        FROM PERSONAL;
    """)
    p_row = cursor.fetchone()
    total_personal = p_row[0] or 0
    total_activos = p_row[1] or 0
    total_retirados = p_row[2] or 0

    # 2. Distribución de personal
    companias = []

    # 3. Top novedades del período
    mes_filter = ""
    params = []
    if mes and mes.upper() != "TODOS":
        from app.database import get_month_dates
        dates = get_month_dates(mes)
        if dates:
            placeholders = ",".join("%s" for _ in dates)
            mes_filter = f"WHERE r.fecha IN ({placeholders})"
            params.extend(dates)

    cursor.execute(f"""
        SELECT sn.nombre, COUNT(rp.id) AS dias_reportados, COUNT(DISTINCT rp.id_personal) AS personal_afectado
        FROM REGISTRO_PERSONAL rp
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        JOIN REPORTES r ON rp.id_reporte = r.id
        {mes_filter}
        GROUP BY sn.nombre
        ORDER BY dias_reportados DESC
        LIMIT 6;
    """, params)
    top_novedades = [
        {"novedad": r[0], "dias": r[1], "efectivos": r[2]}
        for r in cursor.fetchall()
    ]

    # 4. Personal con mayor afectación prolongada (más de 10 días)
    cursor.execute(f"""
        SELECT p.cedula, p.nombre, sn.nombre AS novedad, COUNT(rp.id) AS total_dias
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON rp.id_personal = p.id
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        JOIN REPORTES r ON rp.id_reporte = r.id
        {mes_filter}
        GROUP BY p.cedula, p.nombre, sn.nombre
        HAVING COUNT(rp.id) >= 10
        ORDER BY total_dias DESC
        LIMIT 5;
    """, params)
    casos_criticos = [
        {"cedula": r[0], "nombre": r[1], "novedad": r[2], "dias": r[3]}
        for r in cursor.fetchall()
    ]

    # Prompt para redactar la apreciación oficial
    periodo_str = f"Mes de {mes.upper()}" if mes and mes.upper() != "TODOS" else "Consolidado General 2026"
    
    prompt = f"""
Actúa como el Oficial de Personal (S1) del Batallón BIMEJ 12.
Redacta una "APRECIACIÓN DE SITUACIÓN Y ESTADO DE FUERZA DE PERSONAL" para el Señor Comandante del Batallón.

DATOS OPERACIONALES ({periodo_str}):
- Efectivo Total en Sistema: {total_personal}
- Efectivo Activo en la Unidad: {total_activos} (Disponibilidad base)
- Personal Retirado/Baja: {total_retirados}
- Distribución por Compañías: {json.dumps(companias, ensure_ascii=False)}
- Principales Novedades Registradas: {json.dumps(top_novedades, ensure_ascii=False)}
- Casos de Ausentismo Crítico (>=10 días): {json.dumps(casos_criticos, ensure_ascii=False)}

ESTRUCTURA REQUERIDA (en formato Markdown):
1. **Encabezado Institucional**: BIMEJ 12 - Jefatura de Personal.
2. **Diagnóstico General de Fuerza**: Porcentaje de disponibilidad y distribución.
3. **Análisis de Novedades de Mayor Impacto**: Novedades médicas, vacaciones, comisiones.
4. **Alertas de Gestión de Personal**: Casos que requieren atención o seguimiento del comando.
5. **Recomendación del S1**: Sugerencias concretas para mantener la capacidad operativa.

Utiliza vocabulario castrense formal, respetuoso, directo y preciso.
"""

    briefing_text = query_ollama(prompt=prompt)

    return {
        "periodo": periodo_str,
        "kpis": {
            "total_personal": total_personal,
            "total_activos": total_activos,
            "total_retirados": total_retirados,
            "companias": companias,
            "top_novedades": top_novedades,
            "casos_criticos": casos_criticos
        },
        "apreciacion": briefing_text,
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

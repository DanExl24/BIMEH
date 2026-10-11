"""
Catalogo de Consultas SQL Pre-definidas -- Asistente IA BIMEH
=============================================================
Mapea intenciones comunes del usuario directamente a SQL probado,
evitando la generacion via LLM (que tarda ~40-85s en hardware modesto).

Flujo:
  match_catalog(mensaje, active_militar) -> (sql, descripcion) | (None, None)

Si retorna (None, None) el sistema cae al camino lento (LLM genera el SQL).
"""

import re
import unicodedata
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List


# ---------------------------------------------------------------------------
# Utilidades de normalizacion
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    """Normaliza a minusculas sin tildes ni puntuacion para matching robusto."""
    nfkd = unicodedata.normalize("NFD", text.lower())
    sin_tildes = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w\s]", " ", sin_tildes).strip()


# ---------------------------------------------------------------------------
# Mapas de referencia
# ---------------------------------------------------------------------------

MESES_ES: Dict[str, int] = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}

NOVEDADES_MAP: Dict[str, str] = {
    "vacacion": "VACACIONES",
    "vacaciones": "VACACIONES",
    "permiso": "PERMISO",
    "permisos": "PERMISO",
    "incapacidad": "INCAPACIDAD",
    "incapacidades": "INCAPACIDAD",
    "incapacitado": "INCAPACIDAD",
    "excusa": "EXCUSA MEDICA",
    "excusa medica": "EXCUSA MEDICA",
    "comision": "COMISION",
    "licencia": "LICENCIA",
    "hospitalizacion": "HOSPITALIZACION",
    "hospitalizado": "HOSPITALIZACION",
    "curso": "CURSO",
    "baja": "BAJA",
    "desercion": "DESERCION",
    "desertor": "DESERCION",
    "alta": "ALTA MEDICA",
    "alta medica": "ALTA MEDICA",
    "franco": "FRANCO",
    "francos": "FRANCO",
    "detenido": "DETENIDO",
    "detencion": "DETENIDO",
    "prision": "PRISION",
    "preso": "PRISION",
}


# ---------------------------------------------------------------------------
# Extractores de variables desde el mensaje
# ---------------------------------------------------------------------------

def _extract_month(msg_norm: str) -> Optional[int]:
    for nombre, num in MESES_ES.items():
        if re.search(rf"\b{re.escape(nombre)}\b", msg_norm):
            return num
    return None


def _extract_year(msg_norm: str, default_year: int) -> int:
    match = re.search(r"\b(20\d{2})\b", msg_norm)
    return int(match.group(1)) if match else default_year


def _extract_day_range(msg_norm: str) -> Optional[Tuple[int, int]]:
    patterns = [
        r"del\s+(\d{1,2})\s+al\s+(\d{1,2})",
        r"entre\s+el\s+(\d{1,2})\s+y\s+el\s+(\d{1,2})",
        r"del\s+(\d{1,2})\s+y\s+el\s+(\d{1,2})",
        r"(\d{1,2})\s+al\s+(\d{1,2})",
    ]
    for p in patterns:
        m = re.search(p, msg_norm)
        if m:
            d1, d2 = int(m.group(1)), int(m.group(2))
            return (min(d1, d2), max(d1, d2))
    return None


def _extract_novedad_type(msg_norm: str) -> Optional[str]:
    for kw, novedad in NOVEDADES_MAP.items():
        if re.search(rf"\b{re.escape(kw)}\b", msg_norm):
            return novedad
    return None


def _extract_name_tokens(msg_norm: str) -> List[str]:
    stopwords = {
        # articulos, preposiciones y conjunciones
        "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
        "en", "con", "por", "para", "que", "se", "su", "sus", "es", "son",
        "hay", "y", "o", "a", "me", "te", "nos", "como", "sobre", "acerca",
        # pronombres / interrogativos
        "cuantos", "cuantas", "quien", "quienes", "cual", "cuales",
        "como", "donde", "cuando", "este", "esta", "estos", "estas", "ese", "esa", "aquel",
        # verbos y peticiones
        "sabes", "conoces", "tiene", "tienes", "sabe", "conoce", "tuvo", "habia",
        "puedes", "podrias", "quiero", "quieres", "puedo", "decir", "decime", "dime",
        "ver", "saber", "conocer", "buscar", "busca", "dame", "mostrar", "mostrame",
        "listar", "lista", "informacion", "datos", "historia", "historial",
        "estan", "esta", "estuvo", "estaban", "hubo", "mas", "menos", "menor", "minima", "minimo", "rara", "habitual",
        # conectores, transiciones y adverbios
        "ahora", "entonces", "luego", "despues", "antes", "tambien", "ademas", "solo", "solamente",
        "otro", "otra", "otros", "otras", "mismo", "misma", "mismos", "mismas",
        "siguiente", "proximo", "proxima", "pasado", "pasada", "anterior", "nuevo", "nueva",
        "actual", "actualmente", "respecto", "sobre", "acerca", "favor", "porfa", "aqui", "alli",
        # palabras de tiempo y conteo
        "todos", "todas", "todo", "toda", "dias", "dia", "fecha", "fechas", "mes", "meses",
        "ano", "anos", "anio", "anios", "hoy", "ayer", "semana", "tiempo",
        # palabras del dominio militar y novedades
        "novedad", "novedades", "reporte", "reportes", "ausencia", "ausencias",
        "permiso", "permisos", "vacaciones", "incapacidad", "incapacidades",
        "excusa", "excusas", "franco", "francos", "alta", "detenido", "prision",
        "medica", "medico", "medicas", "medicos", "total", "frecuente", "frecuentes", "comun", "comunes",
        "distribucion", "evolucion",
        # terminos analiticos y rankings (no son nombres de personas)
        "ranking", "rankings", "top", "tops", "recurrente", "recurrentes",
        "estadistica", "estadisticas", "conteo", "conteos", "grafica", "graficas", "tabla", "tablas",
        "causa", "causas", "motivo", "motivos", "afectacion", "afectaciones", "impacto",
        "principal", "principales", "mayor", "mayores", "menor", "menores",
        # rangos militares (no son nombres propios)
        "personal", "militar", "militares", "soldado", "soldados", "cabo", "sargento",
        "teniente", "mayor", "coronel", "capitan", "suboficial", "efectivo", "efectivos",
        "batallon", "bimej", "compania", "companias", "registro", "registros", "estado",
        "activo", "activos", "retirado", "retirados"
    }
    meses_set = set(MESES_ES.keys())
    words = [w for w in re.split(r"[^a-z0-9ñáéíóú]+", msg_norm) if w]
    return [w for w in words if len(w) >= 3 and w not in stopwords and w not in meses_set and not w.isdigit()]


def _name_like_clause(token: str) -> str:
    """
    Genera una condicion LIKE tolerante a N/Ñ variantes para PostgreSQL.
    Ej: 'PENA' -> "(UPPER(nombre) LIKE '%PENA%' OR UPPER(nombre) LIKE '%PEÑA%')"
    """
    t = token.upper()
    has_enie = "Ñ" in t
    t_norm = t.replace("Ñ", "N")
    common_enie = {"PENA", "MUNOZ", "NINO", "CASTANO", "IBANEZ", "ORDONEZ", "BRICENO", "NUNEZ", "MONTANA", "PATINO", "CORUNA"}
    if has_enie or t in common_enie:
        t_enie = t_norm.replace("N", "\u00d1")
        return f"(UPPER(nombre) LIKE '%{t_norm}%' OR UPPER(nombre) LIKE '%{t_enie}%')"
    return f"UPPER(nombre) LIKE '%{t}%'"


def _is_least_frequent(msg: str) -> bool:
    """
    Detecta si el mensaje pregunta por la novedad MENOS frecuente,
    menos registrada, menor cantidad de dias o mas rara.
    """
    least_triggers = (
        r"\b(menos\s+frecuentes?|menos\s+comunes?|menor\s+frecuencia|menos\s+presentes?|"
        r"menos\s+tiene|menos\s+registro|menos\s+registradas?|menor\s+cantidad|"
        r"menos\s+repetidas?|menos\s+dias|menos\s+veces|minima\s+frecuencia|"
        r"mas\s+raras?|menos\s+habitual(es)?|novedades?\s+menores?|novedades?\s+menos)\b"
    )
    if re.search(least_triggers, msg):
        return True
    has_min = bool(re.search(r"\b(menos|menor(es)?|minima?s?|rara?s?)\b", msg))
    has_target = bool(re.search(r"\b(frecuentes?|comunes?|novedades?|registradas?|dias?|presencia|repetidas?)\b", msg))
    return has_min and has_target


# ---------------------------------------------------------------------------
# Funcion principal de matching
# ---------------------------------------------------------------------------

def match_catalog(
    user_message: str,
    active_militar: Optional[Dict[str, Any]] = None,
    current_year: Optional[int] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Intenta hacer match del mensaje con una plantilla pre-definida.

    Retorna:
        (sql, descripcion)  -> si hay coincidencia (fast path)
        (None, None)        -> sin match -> el LLM genera el SQL (slow path)
    """
    if not user_message:
        return None, None

    year = current_year or datetime.now().year
    msg = _norm(user_message)
    ced = str(active_militar.get("cedula", "")) if active_militar else ""
    nom = str(active_militar.get("nombre", "")) if active_militar else ""

    # Extraer variables comunes desde el inicio
    novedad_type = _extract_novedad_type(msg)
    mes_num = _extract_month(msg)
    day_range = _extract_day_range(msg)
    anio = _extract_year(msg, year)

    # ------------------------------------------------------------------
    # 0. CEDULA EXPLICITA EN EL MENSAJE (maxima prioridad)
    # Cuando el usuario escribe una cedula directamente en el texto,
    # ignoramos el contexto activo y resolvemos desde el mensaje.
    # Ej: "busca a este personal 1006524181"
    #     "dame la novedad mas presente de 1012344279 en el mes de junio"
    #     "novedades de julio de cedula 1006524181"
    # ------------------------------------------------------------------
    cedula_en_msg = re.search(r"\b(\d{7,10})\b", user_message)
    if cedula_en_msg:
        cv = cedula_en_msg.group(1)

        # 0-ranking: Cédula + más o menos frecuente / ranking (+ opcional mes)
        ranking_triggers = r"\b(frecuentes?|comunes?|mas\s+presente|mas\s+tiene|mas\s+registro|mas\s+registrada?|ranking|mayor\s+cantidad|mas\s+repetida?|mas\s+dias|principal\s+novedad|menos\s+frecuente|menos\s+registrada?|menor)\b"
        if re.search(ranking_triggers, msg) or _is_least_frequent(msg):
            is_least = _is_least_frequent(msg)
            order = "ASC" if is_least else "DESC"
            desc_tipo = "menos frecuente" if is_least else "más frecuente"
            if mes_num:
                return (
                    f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                    f"FROM v_novedades_detalle "
                    f"WHERE cedula = {cv} "
                    f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                    f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 10",
                    f"Novedad {desc_tipo} de cédula {cv} en mes {mes_num}/{anio}"
                )
            return (
                f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                f"FROM v_novedades_detalle "
                f"WHERE cedula = {cv} "
                f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 10",
                f"Novedades {desc_tipo}s de cédula {cv}"
            )

        # 0-tipo: Cédula + tipo específico de novedad (permiso, vacación, etc.)
        if novedad_type:
            if mes_num:
                return (
                    f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                    f"FROM v_novedades_detalle "
                    f"WHERE cedula = {cv} "
                    f"AND UPPER(novedad) LIKE '%{novedad_type}%' "
                    f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                    f"ORDER BY fecha_reporte ASC LIMIT 50",
                    f"Días de {novedad_type} de cédula {cv} en mes {mes_num}/{anio}"
                )
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE cedula = {cv} "
                f"AND UPPER(novedad) LIKE '%{novedad_type}%' "
                f"ORDER BY fecha_reporte DESC LIMIT 50",
                f"Historial de {novedad_type} de cédula {cv}"
            )

        # 0a. Cédula + novedades + mes (o cualquier mención de mes con cédula que no sea solo buscar perfil)
        nov_kw = r"\b(novedad|novedades|historial|reporte|reportes|ausencias?|permisos?|vacaciones?|dias?)\b"
        if mes_num and (re.search(nov_kw, msg) or not re.search(r"\b(quien|datos|info|perfil)\b", msg)):
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE cedula = {cv} "
                f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                f"ORDER BY fecha_reporte ASC LIMIT 50",
                f"Novedades de cédula {cv} en mes {mes_num}/{anio}"
            )

        # 0b. Cédula + novedades (sin mes -> historial completo)
        if re.search(nov_kw, msg):
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE cedula = {cv} "
                f"ORDER BY fecha_reporte DESC LIMIT 30",
                f"Historial de novedades de cédula {cv}"
            )

        # 0c. Búsqueda pura de la persona por cédula
        return (
            f"SELECT cedula, nombre, estado, fecha_retiro, total_novedades_historicas "
            f"FROM v_personal_resumen WHERE cedula = {cv} LIMIT 5",
            f"Búsqueda de personal por cédula {cv}"
        )

    # ------------------------------------------------------------------
    # 1. TOTAL PERSONAL ACTIVO
    # ------------------------------------------------------------------
    if re.search(r"\b(cuantos?|total|efectivos?|cantidad)\b", msg) and \
       re.search(r"\b(activos?|disponibles?)\b", msg) and \
       not re.search(r"\b(novedad|novedades|retirado)\b", msg):
        return (
            "SELECT COUNT(*) AS total_activos FROM v_personal_resumen WHERE estado = 'ACTIVO'",
            "Conteo total de personal activo en BIMEJ 12"
        )

    # ------------------------------------------------------------------
    # 2. TOTAL PERSONAL RETIRADO
    # ------------------------------------------------------------------
    if re.search(r"\b(cuantos?|total|cantidad)\b", msg) and \
       re.search(r"\b(retirados?|bajas?|dados? de baja)\b", msg):
        return (
            "SELECT COUNT(*) AS total_retirados FROM v_personal_resumen WHERE estado = 'RETIRADO'",
            "Conteo total de personal retirado"
        )

    # ------------------------------------------------------------------
    # 3. RESUMEN GENERAL BATALLON
    # ------------------------------------------------------------------
    if re.search(r"\b(cuantos?\s+militares?|total\s+de\s+personal|fuerza\s+total|efectivo\s+total)\b", msg):
        return (
            "SELECT estado, COUNT(*) AS total FROM v_personal_resumen GROUP BY estado ORDER BY total DESC",
            "Resumen total del personal del batallon por estado"
        )

    # ------------------------------------------------------------------
    # 4. NOVEDADES DEL DIA DE HOY
    # ------------------------------------------------------------------
    hoy_triggers = ["hoy", "del dia de hoy", "reporte de hoy", "parte de hoy",
                    "novedades de hoy", "quienes tienen novedad hoy"]
    if any(t in msg for t in hoy_triggers):
        return (
            "SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
            "FROM v_novedades_detalle WHERE fecha_reporte = CURRENT_DATE "
            "ORDER BY nombre ASC LIMIT 50",
            "Personal con novedad registrada hoy"
        )

    # ------------------------------------------------------------------
    # 5. RANKING DE NOVEDADES DEL BATALLON (MAS O MENOS FRECUENTES, CON O SIN MES)
    # ------------------------------------------------------------------
    ranking_batallon_triggers = (
        r"\b(ranking|rankings|top\s*\d*|mas\s+frecuentes?|mas\s+comunes?|"
        r"mas\s+presentadas?|mas\s+registradas?|mas\s+repetidas?|"
        r"menos\s+frecuentes?|menos\s+comunes?|menos\s+registradas?|"
        r"novedades\s+frecuentes|que\s+novedades\s+hay\s+mas|"
        r"cuales\s+son\s+las\s+novedades|novedades\s+del\s+batallon|"
        r"principales\s+novedades|novedades\s+principales)\b"
    )
    if not ced and (re.search(ranking_batallon_triggers, msg) or _is_least_frequent(msg)):
        is_least = _is_least_frequent(msg)
        order = "ASC" if is_least else "DESC"
        desc_tipo = "menos frecuentes" if is_least else "más frecuentes"

        # 5a. Ranking con mes especifico (ej: "ranking en el mes de junio", "novedades mas frecuentes en agosto")
        if mes_num:
            return (
                f"SELECT novedad, COUNT(*) AS total_dias_registrados, COUNT(DISTINCT cedula) AS total_personal_afectado "
                f"FROM v_novedades_detalle "
                f"WHERE fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                f"GROUP BY novedad "
                f"ORDER BY total_dias_registrados {order} LIMIT 10",
                f"Ranking de novedades {desc_tipo} en mes {mes_num}/{anio}"
            )

        # 5b. Ranking historico general del batallon
        return (
            f"SELECT novedad, total_dias_registrados, total_personal_afectado "
            f"FROM v_conteo_novedades "
            f"ORDER BY total_dias_registrados {order} LIMIT 10",
            f"Ranking de novedades {desc_tipo} en BIMEJ 12"
        )

    # ------------------------------------------------------------------
    # Extraer variables comunes para los bloques siguientes
    # ------------------------------------------------------------------
    novedad_type = _extract_novedad_type(msg)
    mes_num = _extract_month(msg)
    day_range = _extract_day_range(msg)
    anio = _extract_year(msg, year)

    # Extraer umbral de dias: "mas de 10 dias", "mas de 5 dias", etc.
    min_days_match = re.search(r"m[aá]s\s+de\s+(\d+)\s+d[ií]as?", msg)
    min_days = int(min_days_match.group(1)) if min_days_match else None

    # ------------------------------------------------------------------
    # 5.5 CONSULTAS POR NOMBRE DE MILITAR (detectado en el mensaje)
    # Ejemplos:
    #   "dame todos los dias que tuvo JORGE ENRIQUE PEÑA MUÑOZ como novedad PERMISO, en el mes de agosto"
    #   "novedades de Jorge Peña en agosto"
    #   "permisos de Peña Muñoz"
    #   "historial de Jorge Peña"
    # ------------------------------------------------------------------
    name_tokens = _extract_name_tokens(msg)
    if name_tokens and not ced:
        like_clauses = " AND ".join(_name_like_clause(t) for t in name_tokens[:4])
        nom_label = " ".join(name_tokens)

        # 5.5a. Nombre + tipo de novedad + mes (ej: Peña + Permiso + Agosto)
        if novedad_type and mes_num:
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE {like_clauses} "
                f"AND UPPER(novedad) LIKE '%{novedad_type}%' "
                f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                f"ORDER BY fecha_reporte ASC LIMIT 50",
                f"Dias de {novedad_type} de {nom_label} en mes {mes_num}/{anio}"
            )

        # 5.5b. Nombre + tipo de novedad (sin mes)
        if novedad_type:
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE {like_clauses} "
                f"AND UPPER(novedad) LIKE '%{novedad_type}%' "
                f"ORDER BY fecha_reporte DESC LIMIT 50",
                f"Historial de {novedad_type} de {nom_label}"
            )

        # 5.5c. Nombre + mes (sin tipo especifico de novedad)
        if mes_num:
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE {like_clauses} "
                f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                f"ORDER BY fecha_reporte ASC LIMIT 50",
                f"Novedades de {nom_label} en mes {mes_num}/{anio}"
            )

        # 5.5d. Nombre + historial / novedades explicitas
        if re.search(r"\b(novedad|novedades|historial|reporte|reportes|ausencias?|dias?|permisos?|vacaciones?)\b", msg):
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE {like_clauses} "
                f"ORDER BY fecha_reporte DESC LIMIT 30",
                f"Historial de novedades de {nom_label}"
            )

        # 5.5e. Busqueda de datos / perfil de la persona
        if re.search(r"\b(quien|buscar|busca|datos|info|informacion|estado|activo|retirado)\b", msg):
            return (
                f"SELECT cedula, nombre, estado, fecha_retiro, total_novedades_historicas "
                f"FROM v_personal_resumen "
                f"WHERE {like_clauses} LIMIT 5",
                f"Datos de personal: {nom_label}"
            )

    # ------------------------------------------------------------------
    # 6-EXTRA. PERSONAL CON MAS DE N DIAS DE [NOVEDAD]
    # "listar personal con mas de 10 dias de incapacidad"
    # ------------------------------------------------------------------
    if min_days is not None and novedad_type:
        return (
            f"SELECT cedula, nombre, COUNT(*) AS total_dias "
            f"FROM v_novedades_detalle "
            f"WHERE UPPER(novedad) LIKE '%{novedad_type}%' "
            f"GROUP BY cedula, nombre "
            f"HAVING COUNT(*) > {min_days} "
            f"ORDER BY total_dias DESC LIMIT 50",
            f"Personal con mas de {min_days} dias de {novedad_type}"
        )

    # Si hay umbral de dias pero sin tipo de novedad: agrupar todas las novedades
    if min_days is not None:
        return (
            f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
            f"FROM v_novedades_detalle "
            f"GROUP BY cedula, nombre, novedad "
            f"HAVING COUNT(*) > {min_days} "
            f"ORDER BY total_dias DESC LIMIT 50",
            f"Personal con mas de {min_days} dias de cualquier novedad"
        )

    # ------------------------------------------------------------------
    # 6. PERSONAL CON TIPO DE NOVEDAD + FILTROS DE FECHA (BATALLON)
    # ------------------------------------------------------------------
    if novedad_type:

        if mes_num and day_range:
            d1, d2 = day_range
            fi = f"{anio}-{mes_num:02d}-{d1:02d}"
            ff = f"{anio}-{mes_num:02d}-{d2:02d}"
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE UPPER(novedad) LIKE '%{novedad_type}%' "
                f"AND fecha_reporte BETWEEN '{fi}' AND '{ff}' "
                f"ORDER BY fecha_reporte DESC LIMIT 50",
                f"Personal con {novedad_type} entre {fi} y {ff}"
            )
        if mes_num:
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE UPPER(novedad) LIKE '%{novedad_type}%' "
                f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                f"ORDER BY fecha_reporte DESC LIMIT 50",
                f"Personal con {novedad_type} en mes {mes_num}/{anio}"
            )
        if day_range:
            d1, d2 = day_range
            mes_actual = datetime.now().month
            fi = f"{anio}-{mes_actual:02d}-{d1:02d}"
            ff = f"{anio}-{mes_actual:02d}-{d2:02d}"
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE UPPER(novedad) LIKE '%{novedad_type}%' "
                f"AND fecha_reporte BETWEEN '{fi}' AND '{ff}' "
                f"ORDER BY fecha_reporte DESC LIMIT 50",
                f"Personal con {novedad_type} entre {fi} y {ff}"
            )
        # Solo tipo novedad sin fecha
        if re.search(r"\b(quien|quienes|personal|lista|mostrar|hay|tienen|estan)\b", msg):
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE UPPER(novedad) LIKE '%{novedad_type}%' "
                f"ORDER BY fecha_reporte DESC LIMIT 50",
                f"Personal con novedad de tipo {novedad_type}"
            )

    # ------------------------------------------------------------------
    # 7. NOVEDADES POR RANGO DE FECHAS (sin tipo especifico)
    # ------------------------------------------------------------------
    if mes_num and day_range:
        d1, d2 = day_range
        fi = f"{anio}-{mes_num:02d}-{d1:02d}"
        ff = f"{anio}-{mes_num:02d}-{d2:02d}"
        if ced:
            return (
                f"SELECT fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE cedula = {ced} "
                f"AND fecha_reporte BETWEEN '{fi}' AND '{ff}' "
                f"ORDER BY fecha_reporte ASC LIMIT 50",
                f"Novedades de {nom} entre {fi} y {ff}"
            )
        return (
            f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
            f"FROM v_novedades_detalle "
            f"WHERE fecha_reporte BETWEEN '{fi}' AND '{ff}' "
            f"ORDER BY fecha_reporte ASC LIMIT 50",
            f"Novedades entre {fi} y {ff}"
        )

    if not ced and mes_num and re.search(r"\b(novedad|novedades|reporte|parte|ausencias?|permisos?)\b", msg):
        return (
            f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
            f"FROM v_novedades_detalle "
            f"WHERE fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
            f"ORDER BY fecha_reporte ASC LIMIT 50",
            f"Novedades del mes {mes_num}/{anio}"
        )

    # ------------------------------------------------------------------
    # 8. CONSULTAS SOBRE MILITAR EN CONTEXTO ACTIVO
    # ------------------------------------------------------------------
    if ced:
        ranking_triggers = r"\b(frecuentes?|comunes?|mas\s+presente|mas\s+tiene|mas\s+registro|mas\s+registrada?|ranking|mayor\s+cantidad|mas\s+repetida?|mas\s+dias|principal\s+novedad|menos\s+frecuente|menos\s+registrada?|menor)\b"

        # 8a. Si hay un mes mencionado ("ahora en el mes de julio", "y en julio", "en junio la novedad mas presente")
        if mes_num:
            # Ranking de novedades más o menos frecuentes en ese mes
            if re.search(ranking_triggers, msg) or _is_least_frequent(msg):
                is_least = _is_least_frequent(msg)
                order = "ASC" if is_least else "DESC"
                desc_tipo = "menos frecuente" if is_least else "más frecuente"
                return (
                    f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                    f"FROM v_novedades_detalle "
                    f"WHERE cedula = {ced} "
                    f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                    f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 10",
                    f"Novedad {desc_tipo} de {nom} en mes {mes_num}/{anio}"
                )
            # Novedad específica en ese mes
            if novedad_type:
                return (
                    f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                    f"FROM v_novedades_detalle "
                    f"WHERE cedula = {ced} "
                    f"AND UPPER(novedad) LIKE '%{novedad_type}%' "
                    f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                    f"ORDER BY fecha_reporte ASC LIMIT 50",
                    f"Dias de {novedad_type} de {nom} en mes {mes_num}/{anio}"
                )
            # Historial completo de novedades en ese mes
            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE cedula = {ced} "
                f"AND fecha_reporte LIKE '{anio}-{mes_num:02d}-%' "
                f"ORDER BY fecha_reporte ASC LIMIT 50",
                f"Novedades de {nom} en mes {mes_num}/{anio}"
            )

        followup_kw = [
            # novedades
            "historial", "sus novedades", "novedad", "novedades",
            "permisos", "vacaciones", "excusas", "incapacidades",
            "frecuentes", "cuantas", "cuantos", "dias", "ausencias",
            "reportes", "su novedad", "ultima novedad",
            "menos frecuente", "menos comun", "menos registrada", "menor", "menos", "minima",
            # peticiones conversacionales
            "sobre el", "de el", "dime mas", "mas info", "mas informacion",
            "mas datos", "cuentame", "que mas", "mas detalles", "informacion",
            "datos", "perfil",
            # estado personal
            "estado", "como esta", "activo", "retirado",
            # presencia (nuevo)
            "presente", "presencia", "meses", "ha estado",
            "aparece", "registrado", "aparecio", "aparecido",
        ]
        if any(kw in msg for kw in followup_kw):
            # Patron ampliado: "mas frecuente", "menos frecuente", "ranking", etc.
            if re.search(ranking_triggers, msg) or _is_least_frequent(msg):
                is_least = _is_least_frequent(msg)
                order = "ASC" if is_least else "DESC"
                desc_tipo = "menos frecuente" if is_least else "más frecuente"
                return (
                    f"SELECT cedula, nombre, novedad, COUNT(*) AS total_dias "
                    f"FROM v_novedades_detalle "
                    f"WHERE cedula = {ced} "
                    f"GROUP BY cedula, nombre, novedad ORDER BY total_dias {order} LIMIT 10",
                    f"Novedades {desc_tipo}s de {nom}"
                )

            # Consulta "en que meses esta presente / ha tenido novedades"
            if re.search(r"\b(en\s+que\s+meses|cuales\s+meses|que\s+meses|meses\s+present)\b", msg):
                return (
                    f"SELECT EXTRACT(YEAR FROM fecha_reporte::date)::int AS anio, "
                    f"EXTRACT(MONTH FROM fecha_reporte::date)::int AS mes, "
                    f"COUNT(*) AS dias_presente "
                    f"FROM v_novedades_detalle "
                    f"WHERE cedula = {ced} "
                    f"GROUP BY anio, mes ORDER BY anio, mes",
                    f"Meses con presencia registrada de {nom}"
                )

            # Datos del perfil (solo si no hay mes y pregunta por estado/datos)
            # Evitar que "ha estado presente" dispare esto
            if re.search(r"\b(estado|activo|retirado|datos|informacion)\b", msg) and \
               not re.search(r"\b(ha\s+estado|habia\s+estado|estuvo|ha\s+sido)\b", msg):
                return (
                    f"SELECT cedula, nombre, estado, fecha_retiro, total_novedades_historicas "
                    f"FROM v_personal_resumen WHERE cedula = {ced}",
                    f"Estado general de {nom}"
                )

            return (
                f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE cedula = {ced} "
                f"ORDER BY fecha_reporte DESC LIMIT 30",
                f"Historial de novedades de {nom}"
            )


    # ------------------------------------------------------------------
    # 9. BUSQUEDA DE PERSONAL POR NOMBRE/APELLIDO
    # ------------------------------------------------------------------
    buscar_triggers = [
        "quien es", "buscar a", "busca a", "informacion de",
        "datos de", "que sabes de", "mostrar personal", "buscar personal",
        "sabes quien es", "dime quien es",
    ]
    for trigger in buscar_triggers:
        if trigger in msg:
            remainder = msg.replace(trigger, "").strip()
            tokens = _extract_name_tokens(remainder)
            if tokens:
                like_clauses = " AND ".join(
                    _name_like_clause(t) for t in tokens[:4]
                )
                return (
                    f"SELECT cedula, nombre, estado, fecha_retiro, total_novedades_historicas "
                    f"FROM v_personal_resumen WHERE {like_clauses} LIMIT 10",
                    f"Busqueda de personal: {' '.join(tokens)}"
                )

    # ------------------------------------------------------------------
    # 10. BUSQUEDA POR CEDULA EXPLICITA
    # ------------------------------------------------------------------
    cedula_match = re.search(r"\b(\d{6,10})\b", user_message)
    if cedula_match:
        cedula_val = cedula_match.group(1)
        return (
            f"SELECT cedula, nombre, estado, fecha_retiro, total_novedades_historicas "
            f"FROM v_personal_resumen WHERE CAST(cedula AS TEXT) LIKE '%{cedula_val}%' LIMIT 5",
            f"Busqueda de personal por cedula {cedula_val}"
        )

    return None, None


# ---------------------------------------------------------------------------
# MODO REPORTES: Generacion interactiva de Excel y PDF desde el Asistente
# ---------------------------------------------------------------------------

MESES_STR_MAP: Dict[str, str] = {
    "enero": "ENERO", "febrero": "FEBRERO", "marzo": "MARZO", "abril": "ABRIL",
    "mayo": "MAYO", "junio": "JUNIO", "julio": "JULIO", "agosto": "AGOSTO",
    "septiembre": "SEPTIEMBRE", "octubre": "OCTUBRE", "noviembre": "NOVIEMBRE", "diciembre": "DICIEMBRE",
    "ene": "ENERO", "feb": "FEBRERO", "mar": "MARZO", "abr": "ABRIL",
    "jun": "JUNIO", "jul": "JULIO", "ago": "AGOSTO", "sep": "SEPTIEMBRE",
    "oct": "OCTUBRE", "nov": "NOVIEMBRE", "dic": "DICIEMBRE"
}

def _extract_month_name(msg_norm: str) -> Optional[str]:
    if re.search(r"\b(todos|todo el ano|anual|ano completo|anualidad|todos los meses)\b", msg_norm):
        return "TODOS"
    for k, v in MESES_STR_MAP.items():
        if re.search(rf"\b{re.escape(k)}\b", msg_norm):
            return v
    return None

def _extract_report_date(msg_norm: str, user_msg: str) -> Optional[str]:
    # YYYY-MM-DD
    iso = re.search(r"\b(20\d{2}-\d{1,2}-\d{1,2})\b", user_msg)
    if iso:
        parts = iso.group(1).split("-")
        return f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"
    
    # DD/MM/YYYY or DD-MM-YYYY
    dmy = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b", user_msg)
    if dmy:
        d, m, y = int(dmy.group(1)), int(dmy.group(2)), int(dmy.group(3))
        return f"{y:04d}-{m:02d}-{d:02d}"

    # hoy / del dia
    if re.search(r"\b(hoy|el dia de hoy|del dia)\b", msg_norm):
        return datetime.now().strftime("%Y-%m-%d")
    
    # DD de [mes]
    for k, m_name in MESES_STR_MAP.items():
        m_match = re.search(rf"\b(\d{1,2})\s+de\s+{re.escape(k)}\b", msg_norm)
        if m_match:
            d_val = int(m_match.group(1))
            m_num = MESES_ES.get(k, 1)
            year_val = datetime.now().year
            return f"{year_val}-{m_num:02d}-{d_val:02d}"
            
    return None

def match_report_request(
    user_message: str,
    active_militar: Optional[Dict[str, Any]] = None,
    current_year: int = 2026,
    force_report_mode: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Identifica solicitudes de generacion y descarga de reportes oficiales (Excel / PDF / CSV).
    Soporta:
      1. Base de Datos Maestra de Personal (personal_db)
      2. Catalogo Oficial de Subnovedades (subnovedades)
      3. Expediente Individual de Militar (personal)
      4. Reporte Detallado Diario (dia)
      5. Parte Agil de Novedades (mes con modo=agil)
      6. Consolidado Mensual (consolidado_mensual)
    """
    msg = _norm(user_message)
    
    report_keywords = [
        "reporte", "reportes", "informe", "informes", "descargar", "descarga",
        "exportar", "exportacion", "exporte", "generar reporte", "generar informe",
        "excel", "xlsx", "pdf", "csv", "sabana", "matriz", "heatmap", "consolidado",
        "expediente", "hoja de vida", "parte agil", "parte diario", "parte oficial"
    ]
    
    is_report_intent = force_report_mode or any(k in msg for k in report_keywords)
    if not is_report_intent:
        return None
        
    # Formato solicitado
    if "pdf" in msg and not ("excel" in msg or "xlsx" in msg):
        formato = "pdf"
    else:
        formato = "excel"
        
    # 1. Base de Datos Maestra de Personal (personal_db)
    if any(k in msg for k in ["base de datos", "personal db", "maestro de personal", "nomina", "censo de personal", "censo completo", "todos los militares", "censo maestro"]):
        return {
            "tipo": "personal_db",
            "formato_solicitado": formato,
            "titulo": "Base de Datos Maestra de Personal BIMEJ 12",
            "descripcion": "Censo maestro de efectivos orgánicos del batallón, incluyendo cédula, grado, apellidos, nombres y estado operacional.",
            "url_excel": "/api/exportar/excel?tipo=personal_db",
            "url_pdf": "/api/exportar/pdf?tipo=personal_db",
            "url_csv": "/api/exportar/csv?tipo=personal_db",
            "parametros": {"tipo": "personal_db"},
            "mensaje": (
                "He generado los enlaces de descarga para la **Base de Datos Maestra de Personal** de BIMEJ 12.\n\n"
                "Contiene el censo completo de efectivos, cédulas, nombres y estado operacional. "
                "Puede descargarlo directamente en **Excel (.xlsx)** o **PDF (.pdf)** con los botones a continuación:"
            )
        }

    # 2. Catálogo Oficial de Subnovedades (subnovedades)
    if any(k in msg for k in ["subnovedad", "subnovedades", "catalogo de novedades", "codigos de novedad", "tabla de codigos"]):
        return {
            "tipo": "subnovedades",
            "formato_solicitado": formato,
            "titulo": "Catálogo Oficial de Subnovedades y Códigos Operativos",
            "descripcion": "Diccionario oficial con la totalidad de códigos de novedades, descripciones y tipos de ausentismo configurados en el sistema.",
            "url_excel": "/api/exportar/excel?tipo=subnovedades",
            "url_pdf": "/api/exportar/pdf?tipo=subnovedades",
            "url_csv": "/api/exportar/csv?tipo=subnovedades",
            "parametros": {"tipo": "subnovedades"},
            "mensaje": (
                "He preparado la descarga del **Catálogo Oficial de Subnovedades** de BIMEJ 12.\n\n"
                "Disponible para descarga inmediata en formato **Excel** y **PDF**:"
            )
        }

    # 3. Expediente Individual de Militar (personal)
    cedula_match = re.search(r"\b(\d{6,10})\b", user_message)
    cedula_val = int(cedula_match.group(1)) if cedula_match else (int(active_militar.get("cedula")) if active_militar and active_militar.get("cedula") else None)
    
    es_expediente = any(k in msg for k in ["expediente", "hoja de vida", "individual", "militar"]) or (active_militar is not None and any(k in msg for k in ["reporte", "informe", "descargar", "excel", "pdf"]))
    if es_expediente and cedula_val:
        m_nombre = _extract_month_name(msg) or ""
        nom_mil = active_militar.get("nombre", f"C.C. {cedula_val}") if active_militar else f"C.C. {cedula_val}"
        mes_query = f"&mes={m_nombre}" if m_nombre else ""
        periodo_txt = f" ({m_nombre})" if m_nombre else " (Historial Completo)"
        return {
            "tipo": "personal",
            "formato_solicitado": formato,
            "titulo": f"Expediente Individual - {nom_mil}{periodo_txt}",
            "descripcion": f"Historial detallado de novedades, fechas de inicio y fin, observaciones y récord operativo para el militar con C.C. {cedula_val}.",
            "url_excel": f"/api/exportar/excel?tipo=personal&cedula={cedula_val}{mes_query}",
            "url_pdf": f"/api/exportar/pdf?tipo=personal&cedula={cedula_val}{mes_query}",
            "parametros": {"cedula": cedula_val, "mes": m_nombre or "TODOS"},
            "mensaje": (
                f"He generado el **Expediente Individual de Novedades** para **{nom_mil}**{periodo_txt}.\n\n"
                f"Haga clic en el botón para descargar el reporte oficial en su formato preferido:"
            )
        }

    # 4. Reporte Detallado Diario (dia)
    fecha_val = _extract_report_date(msg, user_message)
    if (fecha_val or any(k in msg for k in ["parte diario", "reporte diario", "del dia", "reporte del dia", "dia"])) and not any(k in msg for k in ["consolidado", "agil", "mes", "mensual"]):
        f_target = fecha_val or datetime.now().strftime("%Y-%m-%d")
        return {
            "tipo": "dia",
            "formato_solicitado": formato,
            "titulo": f"Reporte Detallado de Personal - Día {f_target}",
            "descripcion": f"Relación nominal de todo el personal de la unidad militar con detalle de novedades, ausencias y efectivos disponibles para la fecha {f_target}.",
            "url_excel": f"/api/exportar/excel?tipo=dia&fecha={f_target}",
            "url_pdf": f"/api/exportar/pdf?tipo=dia&fecha={f_target}",
            "parametros": {"fecha": f_target},
            "mensaje": (
                f"He preparado el **Reporte Detallado Diario** para el **{f_target}**.\n\n"
                f"Contiene la relación nominal de todo el personal con novedad y disponible en dicha jornada:"
            )
        }

    # 5. Parte Ágil de Novedades (mes, modo=agil)
    if any(k in msg for k in ["agil", "parte agil", "resumen de novedades", "resumen mensual", "novedades del mes"]):
        mes_val = _extract_month_name(msg) or "TODOS"
        titulo_mes = f"Año {current_year}" if mes_val == "TODOS" else mes_val
        return {
            "tipo": "mes",
            "formato_solicitado": formato,
            "titulo": f"Parte Ágil de Novedades - {titulo_mes}",
            "descripcion": f"Resumen ejecutivo condensado por rangos de días con comentarios descriptivos para {titulo_mes}.",
            "url_excel": f"/api/exportar/excel?tipo=mes&mes={mes_val}&modo=agil",
            "url_pdf": f"/api/exportar/pdf?tipo=mes&mes={mes_val}&modo=agil",
            "parametros": {"mes": mes_val, "modo": "agil"},
            "mensaje": (
                f"He preparado el **Parte Ágil de Novedades** para el período **{titulo_mes}**.\n\n"
                f"Agrupa las novedades por intervalos de días con sus descripciones oficiales:"
            )
        }

    # 6. Consolidado Mensual (consolidado_mensual) - Matriz Heatmap
    mes_val = _extract_month_name(msg) or "TODOS"
    modo_matriz = "completo" if any(k in msg for k in ["completo", "nombre", "subnovedad"]) else "letras"
    titulo_mes = f"Año Completo {current_year}" if mes_val == "TODOS" else mes_val
    return {
        "tipo": "consolidado_mensual",
        "formato_solicitado": formato,
        "titulo": f"Consolidado Mensual - {titulo_mes}",
        "descripcion": f"Matriz integral de toda la unidad que refleja la operatividad día a día de cada integrante con codificación oficial.",
        "url_excel": f"/api/exportar/excel?tipo=consolidado_mensual&mes={mes_val}&modo={modo_matriz}",
        "url_pdf": f"/api/exportar/pdf?tipo=consolidado_mensual&mes={mes_val}&modo={modo_matriz}",
        "parametros": {"mes": mes_val, "modo": modo_matriz},
        "mensaje": (
            f"He preparado el **Consolidado Mensual (Matriz Heatmap)** para **{titulo_mes}**.\n\n"
            f"Seleccione su formato de preferencia para iniciar la descarga oficial:"
        )
    }


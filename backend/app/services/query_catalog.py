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
import difflib
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List
from urllib.parse import quote_plus


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


def check_month_has_data(month_name_or_num: Any, db=None) -> bool:
    """
    Verifica si un mes cuenta con reportes registrados en la base de datos de BIMEJ 12.
    Acepta nombre del mes ('SEPTIEMBRE') o número (1..12).
    """
    try:
        from app.database import get_month_dates
        if isinstance(month_name_or_num, int):
            meses_nombres = {
                1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
                5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
                9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
            }
            m_nom = meses_nombres.get(month_name_or_num, "")
        else:
            m_nom = str(month_name_or_num).strip().upper()
        if not m_nom or m_nom == "TODOS":
            return True
        dates = get_month_dates(m_nom)
        return len(dates) > 0
    except Exception:
        if isinstance(month_name_or_num, int):
            return month_name_or_num in {1, 2, 3, 4, 5, 6, 7}
        m_str = str(month_name_or_num).strip().upper()
        return m_str in {"ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "TODOS"}

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


MAPA_SUBNOVEDADES_OFICIAL: List[Tuple[str, str]] = [
    (r"\b(incapacidad(es)?(\s+medica?s?)?|incapacitad[oa]s?|excusa(\s+medica)?)\b", "INCAPACIDAD"),
    (r"\b(vacacion(es)?|descanso)\b", "VACACIONES"),
    (r"\b(permiso(s)?)\b", "PERMISO"),
    (r"\b(comision(\s+de\s+servicio(s)?)?)\b", "COMISION DE SERVICIO"),
    (r"\b(hospital(izad[oa]s?)?|clinica)\b", "HOSPITALIZADOS"),
    (r"\b(curso\s+de\s+ley)\b", "CURSO DE LEY"),
    (r"\b(curso(s)?)\b", "CURSOS"),
    (r"\b(le[is]{1,2}hmania[sz]is)\b", "TRATAMIENTO LESIHMANIASIS"),
    (r"\b(desertor(es)?|desercion)\b", "DESERTOR"),
    (r"\b(detenid[oa]s?|penitenciario|carcel)\b", "DETENIDO CENTRO PENITENCIARIO"),
    (r"\b(retiro\s+asistido)\b", "RETIRO ASISTIDO"),
    (r"\b(retiro\s+en\s+tramite)\b", "RETIRO EN TRAMITE"),
    (r"\b(retardad[oa]s?|retardo)\b", "RETARDADO"),
    (r"\b(reentrenamiento|reentreanamiento)\b", "REENTREANAMIENTO"),
    (r"\b(area(\s+de)?\s+operaciones|operacion(es)?)\b", "AREA OPERACIONES"),
    (r"\b(cdo(\s+unidad)?|comando)\b", "CDO UNIDAD"),
    (r"\b(ciclo\s+code)\b", "CICLO CODE"),
    (r"\b(comite\s+incorporacion)\b", "COMITE INCORPORACION"),
    (r"\b(pendiente\s+presentacion)\b", "PENDIENTE PRESENTACION"),
]

def _extract_subnovedad_oficial(msg_norm: str) -> Optional[str]:
    """Identifica si el usuario pide filtrar por una subnovedad específica."""
    for pat, canon in MAPA_SUBNOVEDADES_OFICIAL:
        if re.search(pat, msg_norm):
            return canon
    return None

def _find_best_militar_fuzzy(user_tokens: List[str], candidates: List[Tuple[Any, str]]) -> Optional[Tuple[Any, str]]:
    """Tolerancia a erratas de digitación en nombres de militares (ej: 'iglesis' -> 'IGLESIAS')."""
    best_candidate = None
    best_score = 0.0
    for ced, nom in candidates:
        name_words = nom.upper().split()
        score = 0.0
        matched_tokens = 0
        for ut in user_tokens:
            ut_upper = ut.upper()
            if any(ut_upper in nw for nw in name_words):
                score += 1.0
                matched_tokens += 1
            else:
                close = difflib.get_close_matches(ut_upper, name_words, n=1, cutoff=0.72)
                if close:
                    score += 0.85
                    matched_tokens += 1
        is_strong_match = (matched_tokens == len(user_tokens)) or (len(user_tokens) > 2 and matched_tokens >= 2 and score >= 1.7)
        if is_strong_match and score > best_score:
            best_score = score
            best_candidate = (ced, nom)
    return best_candidate


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
        "pero", "sino", "aunque", "porque", "pues", "mientras", "cuando", "donde",
        "ahora", "entonces", "luego", "despues", "antes", "tambien", "ademas", "solo", "solamente",
        "otro", "otra", "otros", "otras", "mismo", "misma", "mismos", "mismas",
        "siguiente", "proximo", "proxima", "pasado", "pasada", "anterior", "nuevo", "nueva",
        "actual", "actualmente", "respecto", "sobre", "acerca", "favor", "porfa", "aqui", "alli",
        "filtrar", "filtrando", "filtro", "filtros",
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
        # rangos militares y sinonimos de personas (no son nombres propios)
        "personal", "personales", "persona", "personas", "integrante", "integrantes", "miembro", "miembros",
        "militar", "militares", "soldado", "soldados", "cabo", "cabos", "sargento", "sargentos",
        "teniente", "tenientes", "subteniente", "subtenientes", "mayor", "mayores", "coronel", "coroneles",
        "capitan", "capitanes", "general", "generales", "suboficial", "suboficiales", "oficial", "oficiales",
        "efectivo", "efectivos", "elemento", "elementos", "cuadro", "cuadros", "tropa", "tropas",
        "dragoneante", "dragoneantes", "agente", "agentes", "slp", "slb", "slr",
        "batallon", "bimej", "compania", "companias", "peloton", "pelotones", "seccion", "secciones",
        "listado", "listados", "listame", "relacion", "relaciones", "censo", "censos", "nomina", "nominas",
        "registro", "registros", "estado",
        "activo", "activos", "retirado", "retirados",
        # terminos de reportes y formatos (no son nombres de personas)
        "consolidado", "consolidados", "mensual", "mensuales", "diario", "diarios",
        "expediente", "expedientes", "hoja", "vida", "sabana", "matriz", "heatmap",
        "agil", "agiles", "descargar", "descarga", "exportar", "exportacion", "exporte",
        "excel", "xlsx", "pdf", "csv", "archivo", "documento", "informe", "informes"
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
        if re.search(r"\b(quien|quienes|personal|personales|lista|listar|listado|mostrar|hay|tienen|estan)\b", msg):
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

def _inspect_soldier_novedades(
    db: Optional[Any],
    cedula: int,
    mes_solicitado: Optional[str] = None,
    subnovedad_filtro: Optional[str] = None
) -> Dict[str, Any]:
    default_res = {
        "tiene_novedades_mes": True,
        "dias_novedad_mes": 0,
        "dias_filtro_mes": 0,
        "novedades_mes": {},
        "top_novedad_mes": None,
        "meses_con_novedades": [],
        "meses_con_filtro": [],
        "top_global_nov": {}
    }
    if not db:
        return default_res

    try:
        cur = db.cursor()
        disponibles = ['CDO UNIDAD', 'AREA OPERACIONES']
        pl_disp = ','.join('%s' for _ in disponibles)

        meses_nombres = {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL',
            5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
            9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
        }

        q = f"""
            SELECT EXTRACT(MONTH FROM to_date(r.fecha, 'YYYY-MM-DD'))::int as mes_num,
                   sn.nombre as novedad,
                   COUNT(*) as cant_dias
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN REPORTES r ON rp.id_reporte = r.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            WHERE p.cedula = %s AND sn.nombre NOT IN ({pl_disp})
            GROUP BY mes_num, sn.nombre
            ORDER BY mes_num ASC, cant_dias DESC
        """
        cur.execute(q, [cedula, *disponibles])
        rows = cur.fetchall()

        meses_dict = {}
        top_global_nov = {}
        for r in rows:
            m_num = int(r[0])
            m_nom = meses_nombres.get(m_num, f"MES {m_num}")
            nov = r[1]
            cant = int(r[2])
            if m_nom not in meses_dict:
                meses_dict[m_nom] = {"mes": m_nom, "mes_num": m_num, "total_dias": 0, "novedades": {}}
            meses_dict[m_nom]["total_dias"] += cant
            meses_dict[m_nom]["novedades"][nov] = meses_dict[m_nom]["novedades"].get(nov, 0) + cant
            top_global_nov[nov] = top_global_nov.get(nov, 0) + cant

        meses_con_novedades = []
        for m_nom, m_info in sorted(meses_dict.items(), key=lambda x: x[1]["mes_num"]):
            resumen_parts = [f"{nov} ({c})" for nov, c in sorted(m_info["novedades"].items(), key=lambda x: x[1], reverse=True)]
            meses_con_novedades.append({
                "mes": m_nom,
                "mes_num": m_info["mes_num"],
                "total_dias": m_info["total_dias"],
                "resumen": ", ".join(resumen_parts),
                "novedades": m_info["novedades"]
            })

        tiene_novedades_mes = True
        dias_novedad_mes = 0
        dias_filtro_mes = 0
        novedades_mes = {}
        top_novedad_mes = None

        if mes_solicitado and mes_solicitado.upper() != "TODOS":
            m_req = mes_solicitado.upper()
            if m_req in meses_dict:
                m_info = meses_dict[m_req]
                dias_novedad_mes = m_info["total_dias"]
                novedades_mes = m_info["novedades"]
                if novedades_mes:
                    top_novedad_mes = max(novedades_mes.items(), key=lambda x: x[1])[0]
                if subnovedad_filtro:
                    dias_filtro_mes = sum(c for nov, c in novedades_mes.items() if subnovedad_filtro.upper() in nov.upper())
                    tiene_novedades_mes = (dias_filtro_mes > 0)
                else:
                    tiene_novedades_mes = (dias_novedad_mes > 0)
            else:
                tiene_novedades_mes = False
                dias_novedad_mes = 0
                dias_filtro_mes = 0

        meses_con_filtro = []
        if subnovedad_filtro:
            for m_info in meses_con_novedades:
                matched_days = sum(c for nov, c in m_info["novedades"].items() if subnovedad_filtro.upper() in nov.upper())
                if matched_days > 0:
                    meses_con_filtro.append({
                        "mes": m_info["mes"],
                        "mes_num": m_info["mes_num"],
                        "total_dias": matched_days,
                        "subnovedad": subnovedad_filtro
                    })

        return {
            "tiene_novedades_mes": tiene_novedades_mes,
            "dias_novedad_mes": dias_novedad_mes,
            "dias_filtro_mes": dias_filtro_mes,
            "novedades_mes": novedades_mes,
            "top_novedad_mes": top_novedad_mes,
            "meses_con_novedades": meses_con_novedades,
            "meses_con_filtro": meses_con_filtro,
            "top_global_nov": top_global_nov
        }
    except Exception as e:
        logger.warning(f"[_inspect_soldier_novedades] Error: {e}")
        return default_res


def match_report_request(
    user_message: str,
    active_militar: Optional[Dict[str, Any]] = None,
    current_year: int = 2026,
    force_report_mode: bool = False,
    db: Optional[Any] = None
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

    # 3. Expediente Individual de Militar / Reporte por Persona (personal)
    cedula_match = re.search(r"\b(\d{6,10})\b", user_message)
    cedula_val = int(cedula_match.group(1)) if cedula_match else (int(active_militar.get("cedula")) if active_militar and active_militar.get("cedula") else None)
    nom_mil = active_militar.get("nombre") if active_militar else None

    # Búsqueda por nombre en base de datos si no hay cédula pero hay nombres/apellidos
    name_tokens = _extract_name_tokens(msg)
    if not cedula_val and db and name_tokens:
        like_clauses = " AND ".join(_name_like_clause(t) for t in name_tokens[:4])
        try:
            cur = db.cursor()
            cur.execute(f"SELECT cedula, nombre FROM v_personal_resumen WHERE {like_clauses} LIMIT 5")
            p_rows = cur.fetchall()
            if p_rows:
                cedula_val = int(p_rows[0][0])
                nom_mil = p_rows[0][1]
            else:
                # Fallback a fuzzy matching para tolerar erratas (ej: 'santiago iglesis' -> 'MENDEZ IGLESIAS DANIEL SANTIAGO')
                cur.execute("SELECT cedula, nombre FROM v_personal_resumen")
                all_person = cur.fetchall()
                best_cand = _find_best_militar_fuzzy(name_tokens, all_person)
                if best_cand:
                    cedula_val = int(best_cand[0])
                    nom_mil = best_cand[1]
                elif any(k in msg for k in ["persona", "militar", "soldado", "expediente", "hoja de vida", "del persona", "de la persona"]):
                    busqueda_txt = " ".join(t.upper() for t in name_tokens)
                    return {
                        "tipo": "no_encontrado",
                        "formato_solicitado": formato,
                        "titulo": f"Personal no encontrado: {busqueda_txt}",
                        "descripcion": f"No se encontró ningún militar registrado con el nombre o apellido '{busqueda_txt}' en la base de datos de BIMEJ 12.",
                        "url_excel": None,
                        "url_pdf": None,
                        "parametros": {},
                        "mensaje": (
                            f"Mi Comandante, no se encontró en los registros de BIMEJ 12 a ningún militar con el nombre o apellido '**{busqueda_txt}**'.\n\n"
                            f"Por favor verifique los apellidos o proporcione el número de cédula (ej: *'reporte de cédula 12345678'*)."
                        )
                    }
        except Exception as e:
            logger.warning(f"[Reporte Personal DB Search] Error: {e}")

    # Si se identificó a un militar concreto
    if cedula_val:
        m_nombre = _extract_month_name(msg) or ""
        subnov_val = _extract_subnovedad_oficial(msg)
        nom_mil = nom_mil or (active_militar.get("nombre") if active_militar else f"C.C. {cedula_val}")

        # Detección de solicitud de novedad más presente / frecuente
        pide_top_novedad = bool(re.search(
            r"\b(novedad\s+m[aá]s\s+(presente|frecuente|comun|común|reiterada)|m[aá]s\s+(presente|frecuente)|mayor\s+novedad|principal\s+novedad)\b",
            msg
        ))

        # Inspección proactiva en base de datos para validar si tiene novedades en el período
        inspection = _inspect_soldier_novedades(db, cedula_val, m_nombre, subnov_val)

        if pide_top_novedad and not subnov_val:
            if inspection.get("top_novedad_mes"):
                subnov_val = inspection["top_novedad_mes"]
            elif inspection.get("tiene_novedades_mes") and inspection.get("novedades_mes"):
                subnov_val = max(inspection["novedades_mes"].items(), key=lambda x: x[1])[0]

        mes_query = f"&mes={m_nombre}" if m_nombre else ""
        subnov_query = f"&subnovedad={subnov_val}" if subnov_val else ""
        
        periodo_txt = f" para {m_nombre}" if m_nombre else " (Historial Anual / Completo)"
        filtro_subnov_txt = f" [Filtro: {subnov_val}]" if subnov_val else ""
        detected_militar = {"cedula": str(cedula_val), "nombre": nom_mil}

        tiene_nov_mes = inspection.get("tiene_novedades_mes", True)
        sin_novedades = bool(m_nombre and m_nombre.upper() != "TODOS" and not tiene_nov_mes)

        # Generar sugerencias de meses alternativos que SÍ tienen novedad
        meses_sugeridos = []
        candidatos_meses = inspection.get("meses_con_filtro", []) if (subnov_val and inspection.get("meses_con_filtro")) else inspection.get("meses_con_novedades", [])
        for m in candidatos_meses[:4]:
            sub_prompt = f" filtrando {subnov_val}" if (subnov_val and inspection.get("meses_con_filtro")) else ""
            meses_sugeridos.append({
                "mes": m["mes"],
                "cant_dias": m["total_dias"],
                "resumen": m.get("resumen", f"{m['total_dias']} días"),
                "prompt": f"dame el reporte de {nom_mil} en el mes de {m['mes']}{sub_prompt}"
            })

        badge_heatmap = "HEATMAP (100% DISP)" if sin_novedades else "HEATMAP"
        badge_expediente = "EXPEDIENTE (0 NOV)" if sin_novedades else "EXPEDIENTE"
        badge_agil = "ÁGIL (0 NOV)" if sin_novedades else "ÁGIL"

        desc_heatmap = f"Matriz día a día (D, N, R){periodo_txt}. {'Personal 100% disponible (D) en este período.' if sin_novedades else ''}"
        desc_personal = f"Relación nominal de novedades{filtro_subnov_txt}. {'Aparecerá sin registros al no tener ausentismos.' if sin_novedades else ''}"
        desc_agil = f"Resumen ejecutivo de ausentismos. {'Aparecerá vacío al estar 100% disponible.' if sin_novedades else ''}"

        modo_hm = "colores" if any(k in msg for k in ["color", "colores", "visual"]) else "letras"
        tit_hm = f"Matriz Heatmap Visual por Colores{filtro_subnov_txt}" if modo_hm == "colores" else f"Matriz Heatmap (Consolidado Día a Día){filtro_subnov_txt}"

        opciones = [
            {
                "id": "heatmap",
                "titulo": tit_hm,
                "descripcion": desc_heatmap,
                "badge": badge_heatmap,
                "tipo_export": "consolidado_mensual",
                "url_excel": f"/api/exportar/excel?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}",
                "url_pdf": f"/api/exportar/pdf?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}"
            },
            {
                "id": "personal",
                "titulo": f"Historial Completo (Expediente Cronológico){filtro_subnov_txt}",
                "descripcion": desc_personal,
                "badge": badge_expediente,
                "tipo_export": "personal",
                "url_excel": f"/api/exportar/excel?tipo=personal&cedula={cedula_val}{mes_query}{subnov_query}",
                "url_pdf": f"/api/exportar/pdf?tipo=personal&cedula={cedula_val}{mes_query}{subnov_query}"
            },
            {
                "id": "agil",
                "titulo": f"Exportación Ágil (Resumen de Novedades){filtro_subnov_txt}",
                "descripcion": desc_agil,
                "badge": badge_agil,
                "tipo_export": "agil",
                "url_excel": f"/api/exportar/excel?tipo=agil&cedula={cedula_val}{mes_query}{subnov_query}",
                "url_pdf": f"/api/exportar/pdf?tipo=agil&cedula={cedula_val}{mes_query}{subnov_query}"
            }
        ]

        # Construcción del mensaje militar
        if sin_novedades:
            if subnov_val:
                mensaje_novedad = (
                    f"He identificado al militar **{nom_mil}** (C.C. {cedula_val}).\n\n"
                    f"⚠️ **Aviso de Ausencia de Novedades:**\n"
                    f"He identificado que este personal **no cuenta con registros de {subnov_val} en el mes de {m_nombre}** "
                    f"(en dicho período se encuentra 100% disponible / sin ausentismos bajo este concepto, por lo que las tablas de novedades aparecerán vacías).\n\n"
                )
                if inspection.get("meses_con_filtro"):
                    meses_txt = "\n".join([f"• **{m['mes']}**: {m['total_dias']} días de {subnov_val}" for m in inspection["meses_con_filtro"]])
                    mensaje_novedad += (
                        f"💡 Sin embargo, **SÍ registra {subnov_val}** en los siguientes meses:\n{meses_txt}\n\n"
                        f"Si quieres, puedo generar su reporte para un mes que **SÍ tenga esta novedad**, "
                        f"o puedes pulsar cualquiera de los accesos sugeridos a continuación:"
                    )
                elif inspection.get("meses_con_novedades"):
                    meses_txt = "\n".join([f"• **{m['mes']}**: {m['total_dias']} días con novedad ({m['resumen']})" for m in inspection["meses_con_novedades"][:3]])
                    mensaje_novedad += (
                        f"💡 Tampoco registra {subnov_val} en el resto del año. Sus novedades reales registradas en la unidad corresponden a:\n{meses_txt}\n\n"
                        f"Si quieres, puedo generar su reporte para un mes que **SÍ tenga novedad**, o seleccionar uno de los meses sugeridos:"
                    )
                else:
                    mensaje_novedad += "💡 Este integrante no registra novedades de ausentismo en ningún período registrado (100% disponible)."
            else:
                top_txt = ""
                if pide_top_novedad and inspection.get("top_global_nov"):
                    top_items = [f"**{k}** ({v} días)" for k, v in sorted(inspection["top_global_nov"].items(), key=lambda x: x[1], reverse=True)[:2]]
                    top_txt = f"\n• Solicitó filtrar por su novedad más presente, pero en {m_nombre} estuvo 100% disponible. A nivel histórico general, sus novedades más frecuentes son: {', '.join(top_items)}.\n"

                mensaje_novedad = (
                    f"He identificado al militar **{nom_mil}** (C.C. {cedula_val}).\n\n"
                    f"⚠️ **Aviso:** He identificado que este personal **no cuenta con novedades para el mes de {m_nombre}** "
                    f"(se encuentra 100% disponible en la unidad, por lo que la sección de ausentismos aparecerá vacía).{top_txt}\n\n"
                )
                if inspection.get("meses_con_novedades"):
                    meses_txt = "\n".join([f"• **{m['mes']}**: {m['total_dias']} días con novedad ({m['resumen']})" for m in inspection["meses_con_novedades"][:3]])
                    mensaje_novedad += (
                        f"💡 Si quieres, puedo generar su reporte para un mes que **SÍ tenga novedad**. Actualmente registra novedades en los meses de:\n{meses_txt}\n\n"
                        f"Puede pulsar uno de los meses sugeridos a continuación o descargar el reporte de {m_nombre} con estado disponible:"
                    )
                else:
                    mensaje_novedad += "💡 Este integrante no registra ninguna novedad de ausentismo en todo el historial (se encuentra 100% disponible)."
        else:
            subnov_msg = f"\n• Subnovedad filtrada: **{subnov_val}**" if subnov_val else ""
            resumen_nov_txt = ""
            if inspection.get("dias_novedad_mes", 0) > 0:
                resumen_parts = [f"{nov} ({c})" for nov, c in sorted(inspection["novedades_mes"].items(), key=lambda x: x[1], reverse=True)]
                resumen_nov_txt = f"\n• Novedades en {m_nombre}: **{inspection['dias_novedad_mes']} días** ({', '.join(resumen_parts)})"

            mensaje_novedad = (
                f"He identificado al militar **{nom_mil}** (C.C. {cedula_val}).\n\n"
                f"• Período: **{m_nombre or 'Todo el año / Historial completo'}**{subnov_msg}{resumen_nov_txt}\n\n"
                f"Para este integrante tiene a su disposición 3 formatos oficiales de reporte.\n"
                f"Por favor seleccione qué tipo de reporte desea generar a continuación:"
            )

        return {
            "tipo": "seleccion_reporte_personal",
            "formato_solicitado": formato,
            "titulo": f"Reportes Oficiales: {nom_mil}{filtro_subnov_txt}",
            "descripcion": f"Personal identificado: {nom_mil} (C.C. {cedula_val}){periodo_txt}{filtro_subnov_txt}. Seleccione la modalidad de reporte que desea generar:",
            "url_excel": f"/api/exportar/excel?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}",
            "url_pdf": f"/api/exportar/pdf?tipo=consolidado_mensual&cedula={cedula_val}{mes_query}{subnov_query}&modo={modo_hm}",
            "parametros": {"cedula": cedula_val, "mes": m_nombre or "TODOS", "subnovedad": subnov_val},
            "active_militar": detected_militar,
            "opciones": opciones,
            "sin_novedades": sin_novedades,
            "meses_sugeridos": meses_sugeridos,
            "mensaje": mensaje_novedad
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
        subnov_val = _extract_novedad_type(msg)
        if mes_val != "TODOS" and not check_month_has_data(mes_val, db):
            from app.database import get_available_date_range
            r_range = get_available_date_range(db)
            return {
                "tipo": "no_encontrado",
                "mensaje": (
                    f"⚠️ **Aviso de Período No Disponible:**\n\n"
                    f"En la base de datos de BIMEJ 12 **no se registran reportes diarios para el mes de {mes_val}**.\n\n"
                    f"El sistema actualmente cuenta con reportes cargados para el período de **{r_range['texto']}**.\n\n"
                    f"💡 Si lo desea, puede solicitar el **Parte Ágil** para un mes con datos disponibles "
                    f"(por ejemplo: **{r_range['max_month']}**), o bien para **TODO EL AÑO**."
                )
            }
        subnov_query = f"&subnovedad={quote_plus(subnov_val)}" if subnov_val else ""
        filtro_subnov_txt = f" (Filtro: {subnov_val})" if subnov_val else ""
        titulo_mes = f"Año {current_year}" if mes_val == "TODOS" else mes_val
        return {
            "tipo": "mes",
            "formato_solicitado": formato,
            "titulo": f"Parte Ágil de Novedades - {titulo_mes}{filtro_subnov_txt}",
            "descripcion": f"Resumen ejecutivo condensado por rangos de días con comentarios descriptivos para {titulo_mes}.",
            "url_excel": f"/api/exportar/excel?tipo=mes&mes={mes_val}&modo=agil{subnov_query}",
            "url_pdf": f"/api/exportar/pdf?tipo=mes&mes={mes_val}&modo=agil{subnov_query}",
            "parametros": {"mes": mes_val, "modo": "agil", "subnovedad": subnov_val},
            "mensaje": (
                f"He preparado el **Parte Ágil de Novedades** para el período **{titulo_mes}**{filtro_subnov_txt}.\n\n"
                f"Agrupa las novedades por intervalos de días con sus descripciones oficiales:"
            )
        }

    # 6. Consolidado Mensual (consolidado_mensual) - Matriz Heatmap
    mes_val = _extract_month_name(msg) or "TODOS"
    subnov_val = _extract_novedad_type(msg)

    if mes_val != "TODOS" and not check_month_has_data(mes_val, db):
        from app.database import get_available_date_range
        r_range = get_available_date_range(db)
        nov_txt = f" con novedad de {subnov_val}" if subnov_val else ""
        return {
            "tipo": "no_encontrado",
            "mensaje": (
                f"⚠️ **Aviso de Período No Disponible:**\n\n"
                f"En la base de datos de BIMEJ 12 **no se registran reportes diarios para el mes de {mes_val}**.\n\n"
                f"El sistema actualmente cuenta con reportes diarios cargados para el período de **{r_range['texto']}** "
                f"(los meses posteriores aún no han sido sincronizados en la base de datos).\n\n"
                f"💡 Si lo desea, puedo generar el **Consolidado Mensual (Matriz Heatmap)**{nov_txt} para uno de los meses "
                f"con información registrada (por ejemplo: **{r_range['max_month']}**), o para **TODO EL AÑO**."
            )
        }

    if any(k in msg for k in ["color", "colores", "visual"]):
        modo_matriz = "colores"
    elif any(k in msg for k in ["completo", "nombre", "subnovedad"]):
        modo_matriz = "completo"
    else:
        modo_matriz = "letras"

    subnov_query = f"&subnovedad={quote_plus(subnov_val)}" if subnov_val else ""
    filtro_subnov_txt = f" (Filtro: {subnov_val})" if subnov_val else ""
    filtro_subnov_desc = f" con filtro aplicado a la novedad '{subnov_val}'" if subnov_val else ""
    titulo_mes = f"Año Completo {current_year}" if mes_val == "TODOS" else mes_val
    return {
        "tipo": "consolidado_mensual",
        "formato_solicitado": formato,
        "titulo": f"Consolidado Mensual - {titulo_mes}{filtro_subnov_txt}",
        "descripcion": f"Matriz integral de toda la unidad que refleja la operatividad día a día de cada integrante con codificación oficial{filtro_subnov_desc}.",
        "url_excel": f"/api/exportar/excel?tipo=consolidado_mensual&mes={mes_val}&modo={modo_matriz}{subnov_query}",
        "url_pdf": f"/api/exportar/pdf?tipo=consolidado_mensual&mes={mes_val}&modo={modo_matriz}{subnov_query}",
        "parametros": {"mes": mes_val, "modo": modo_matriz, "subnovedad": subnov_val},
        "mensaje": (
            f"He preparado el **Consolidado Mensual (Matriz Heatmap)** para **{titulo_mes}**{filtro_subnov_txt}.\n\n"
            f"Seleccione su formato de preferencia para iniciar la descarga oficial:"
        )
    }


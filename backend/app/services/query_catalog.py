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
        # articulos y preposiciones
        "el", "la", "los", "las", "un", "una", "de", "del", "al",
        "en", "con", "por", "que", "se", "su", "sus", "es", "son",
        "hay", "y", "o", "a", "me", "te", "nos",
        # pronombres / interrogativos
        "cuantos", "cuantas", "quien", "quienes", "cual", "cuales",
        "como", "donde", "cuando", "este", "esta", "ese", "esa",
        # verbos comunes que confunden con nombres
        "sabes", "conoces", "tiene", "tienes", "sabe", "conoce",
        "puedes", "podrias", "quiero", "quieres", "puedo",
        "decir", "decime", "dime", "ver", "saber", "conocer",
        "buscar", "busca", "dame", "mostrar", "listar", "lista",
        "informacion", "datos", "historia", "historial",
        "novedades", "novedad",
        # rangos militares (no son nombres propios)
        "personal", "militar", "soldado", "cabo", "sargento", "teniente",
        "mayor", "coronel", "capitan", "suboficial", "efectivo",
        # otros
        "estado", "activo", "retirado", "bimej", "batallon",
        "para", "del", "sobre", "acerca",
    }
    words = msg_norm.split()
    return [w for w in words if len(w) >= 3 and w not in stopwords and not w.isdigit()]


def _name_like_clause(token: str) -> str:
    """
    Genera una condicion LIKE tolerante a N/N variantes para PostgreSQL.
    Ej: 'MUNOZ' -> "(UPPER(nombre) LIKE '%MUNOZ%' OR UPPER(nombre) LIKE '%MUNOZ%')"
    Como PostgreSQL mantiene la N en UPPER(), generamos ambas variantes:
      MUNOZ  <-> MUNOZ (N en el token, puede estar como N en DB)
      MUNOZ  <-> MUNOZ (N en DB puede haberse normalizado sin tilde)
    La clave es generar el LIKE con N y con N, ya que la DB puede tener ambos.
    """
    t = token.upper()
    # Generar variante con N->N y N->N para maxima cobertura
    t_with_n = t.replace("N", "N")  # identidad (token ya normalizado sin tildes)
    # Variante con N (puede estar en la DB como caracter con tilde)
    t_with_enie = t.replace("N", "\u00d1")  # N -> N (unicode N)
    if t_with_enie != t:
        return f"(UPPER(nombre) LIKE '%{t}%' OR UPPER(nombre) LIKE '%{t_with_enie}%')"
    # Si el token ya tiene N, generar variante sin ella
    t_without_enie = t.replace("\u00d1", "N")
    if t_without_enie != t:
        return f"(UPPER(nombre) LIKE '%{t}%' OR UPPER(nombre) LIKE '%{t_without_enie}%')"
    return f"UPPER(nombre) LIKE '%{t}%'"


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
    # 5. NOVEDADES MAS FRECUENTES DEL BATALLON
    # ------------------------------------------------------------------
    frecuentes_triggers = [
        "mas frecuentes", "mas comunes", "mas presentadas", "mas registradas",
        "ranking de novedades", "novedades frecuentes", "que novedades hay mas",
        "cuales son las novedades", "novedades del batallon"
    ]
    if any(t in msg for t in frecuentes_triggers) and not ced:
        return (
            "SELECT novedad, total_dias_registrados, total_personal_afectado "
            "FROM v_conteo_novedades ORDER BY total_dias_registrados DESC LIMIT 10",
            "Ranking de novedades mas frecuentes en BIMEJ 12"
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
    # 6. PERSONAL CON TIPO DE NOVEDAD + FILTROS DE FECHA
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
                f"AND EXTRACT(MONTH FROM fecha_reporte) = {mes_num} "
                f"AND EXTRACT(YEAR FROM fecha_reporte) = {anio} "
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

    if mes_num and re.search(r"\b(novedades?|reporte|parte|ausencias?|permisos?)\b", msg):
        if ced:
            return (
                f"SELECT fecha_reporte, novedad, descripcion "
                f"FROM v_novedades_detalle "
                f"WHERE cedula = {ced} "
                f"AND EXTRACT(MONTH FROM fecha_reporte) = {mes_num} "
                f"AND EXTRACT(YEAR FROM fecha_reporte) = {anio} "
                f"ORDER BY fecha_reporte ASC LIMIT 50",
                f"Novedades de {nom} en mes {mes_num}/{anio}"
            )
        return (
            f"SELECT cedula, nombre, fecha_reporte, novedad, descripcion "
            f"FROM v_novedades_detalle "
            f"WHERE EXTRACT(MONTH FROM fecha_reporte) = {mes_num} "
            f"AND EXTRACT(YEAR FROM fecha_reporte) = {anio} "
            f"ORDER BY fecha_reporte DESC LIMIT 50",
            f"Novedades del mes {mes_num}/{anio}"
        )

    # ------------------------------------------------------------------
    # 8. CONSULTAS SOBRE MILITAR EN CONTEXTO ACTIVO
    # ------------------------------------------------------------------
    if ced:
        followup_kw = [
            "historial", "sus novedades", "novedad", "novedades",
            "permisos", "vacaciones", "excusas", "incapacidades",
            "estado", "como esta", "activo", "retirado", "frecuentes",
            "cuantas", "cuantos", "dias", "ausencias", "reportes",
            "su novedad", "ultima novedad",
        ]
        if any(kw in msg for kw in followup_kw):
            # Patron ampliado: "mas frecuente", "mas registro", "mas tiene", "mas registrada", "ranking"
            es_frecuentes = re.search(
                r"\b(frecuentes?|comunes?|mas\s+tiene|mas\s+registro|mas\s+registrada?|ranking|mayor\s+cantidad)\b",
                msg
            )
            if es_frecuentes:
                # Con filtro de mes: "novedad con mas registro en julio"
                if mes_num:
                    return (
                        f"SELECT novedad, COUNT(*) AS total_dias "
                        f"FROM v_novedades_detalle "
                        f"WHERE cedula = {ced} "
                        f"AND EXTRACT(MONTH FROM fecha_reporte) = {mes_num} "
                        f"AND EXTRACT(YEAR FROM fecha_reporte) = {anio} "
                        f"GROUP BY novedad ORDER BY total_dias DESC LIMIT 10",
                        f"Novedades mas frecuentes de {nom} en mes {mes_num}/{anio}"
                    )
                # Sin filtro de mes: historial completo
                return (
                    f"SELECT novedad, COUNT(*) AS total_dias "
                    f"FROM v_novedades_detalle "
                    f"WHERE cedula = {ced} "
                    f"GROUP BY novedad ORDER BY total_dias DESC LIMIT 10",
                    f"Novedades mas frecuentes de {nom}"
                )
            if re.search(r"\b(estado|activo|retirado|datos|informacion)\b", msg):
                return (
                    f"SELECT cedula, nombre, estado, fecha_retiro, total_novedades_historicas "
                    f"FROM v_personal_resumen WHERE cedula = {ced}",
                    f"Estado general de {nom}"
                )
            # Historial con filtro de mes si se menciona
            if mes_num:
                return (
                    f"SELECT fecha_reporte, novedad, descripcion "
                    f"FROM v_novedades_detalle "
                    f"WHERE cedula = {ced} "
                    f"AND EXTRACT(MONTH FROM fecha_reporte) = {mes_num} "
                    f"AND EXTRACT(YEAR FROM fecha_reporte) = {anio} "
                    f"ORDER BY fecha_reporte ASC LIMIT 50",
                    f"Novedades de {nom} en mes {mes_num}/{anio}"
                )
            return (
                f"SELECT fecha_reporte, novedad, descripcion "
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

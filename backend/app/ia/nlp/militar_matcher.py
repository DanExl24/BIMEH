"""
Extracción y matching de entidades militares, cédulas, nombres y novedades.
"""

import re
import difflib
import logging
from typing import Optional, Tuple, Dict, Any, List

logger = logging.getLogger(__name__)

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
    "i/r": "INCAPACIDAD",
    "ir": "INCAPACIDAD",
    "reposo": "INCAPACIDAD",
}

MAPA_SUBNOVEDADES_OFICIAL: List[Tuple[str, str]] = [
    (r"\b(incapacidad(es)?(\s+medica?s?)?|incapacitad[oa]s?|excusa(\s+medica)?|i/?r|reposo)\b", "INCAPACIDAD"),
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

def _extract_cedula(msg: str) -> Optional[str]:
    """Extrae cédula explícita de 7 a 10 dígitos."""
    match = re.search(r"\b(\d{7,10})\b", msg)
    return match.group(1) if match else None

def _extract_subnovedad_oficial(msg_norm: str) -> Optional[str]:
    """Identifica si el usuario pide filtrar por una subnovedad específica."""
    for pat, canon in MAPA_SUBNOVEDADES_OFICIAL:
        if re.search(pat, msg_norm):
            return canon
    return None

def _extract_novedad_type(msg_norm: str) -> Optional[str]:
    """Extrae la categoría general de novedad militar."""
    for kw, novedad in NOVEDADES_MAP.items():
        if re.search(rf"\b{re.escape(kw)}\b", msg_norm):
            return novedad
    return None

def _extract_name_tokens(msg_norm: str) -> List[str]:
    """Extrae tokens significativos de nombres propios ignorando palabras comunes de mando."""
    stopwords = {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
        "en", "con", "por", "para", "que", "se", "su", "sus", "es", "son",
        "hay", "y", "o", "a", "me", "te", "nos", "como", "sobre", "acerca",
        "cuantos", "cuantas", "quien", "quienes", "cual", "cuales",
        "como", "donde", "cuando", "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquel", "aquella",
        "sabes", "conoces", "tiene", "tienes", "sabe", "conoce", "tuvo", "habia",
        "puedes", "podrias", "quiero", "quieres", "puedo", "decir", "decime", "dime",
        "ver", "veo", "ves", "ve", "vemos", "verlo", "verla",
        "saber", "conocer", "buscar", "busca", "dame", "mostrar", "mostrame", "mostrarlo", "mostrarla",
        "listar", "lista", "informacion", "datos", "historia", "historial",
        "hacer", "haces", "hace", "hacen", "hacerlo", "hacerla", "hacerlos", "hacerlas", "hice", "hizo", "hicieron",
        "poder", "puede", "pueden", "podria", "podrian", "pude", "pudo",
        "tener", "tienen", "tenemos", "tendra", "tuviera",
        "generar", "generas", "genera", "generan", "generarlo", "generarla",
        "descargar", "descargas", "descarga", "descargarlo", "descargarla",
        "exportar", "exportas", "exporta", "exportarlo", "exportarla",
        "filtrar", "filtras", "filtra", "filtran", "filtrando", "filtrarlo", "filtrarla", "filtro", "filtros",
        "sacar", "sacas", "saca", "sacarlo", "sacarla",
        "consultar", "consultas", "consulta", "consultarlo", "consultarla",
        "explicar", "explicas", "explica", "explicame",
        "dar", "darme", "darle", "darles",
        "estan", "esta", "estuvo", "estaban", "hubo", "mas", "menos", "menor", "minima", "minimo", "rara", "habitual",
        "especifico", "especifica", "especificos", "especificas",
        "particular", "particulares", "alguien", "nadie", "alguno", "alguna", "algunos", "algunas",
        "determinado", "determinada", "determinados", "determinadas",
        "cierto", "cierta", "ciertos", "ciertas", "cualquier", "cualquiera", "cualesquiera",
        "uno", "una", "unos", "unas", "otro", "otra", "otros", "otras",
        "cada", "mismo", "misma", "mismos", "mismas",
        "opcion", "opciones", "posible", "posibilidad", "posibilidades",
        "forma", "formas", "manera", "maneras", "modo", "modos",
        "caso", "casos", "ejemplo", "ejemplos", "pregunta", "preguntas", "duda", "dudas",
        "sistema", "asistente", "tema", "proyecto", "ecosistema", "modulo", "modulos",
        "formato", "formatos", "tipo", "tipos",
        "pero", "sino", "aunque", "porque", "pues", "mientras", "cuando", "donde",
        "ahora", "entonces", "luego", "despues", "antes", "tambien", "ademas", "solo", "solamente",
        "siguiente", "proximo", "proxima", "pasado", "pasada", "anterior", "nuevo", "nueva",
        "actual", "actualmente", "respecto", "sobre", "acerca", "favor", "porfa", "aqui", "alli",
        "todos", "todas", "todo", "toda", "dias", "dia", "fecha", "fechas", "mes", "meses",
        "ano", "anos", "anio", "anios", "hoy", "ayer", "semana", "tiempo",
        "novedad", "novedades", "reporte", "reportes", "ausencia", "ausencias",
        "permiso", "permisos", "vacaciones", "incapacidad", "incapacidades",
        "excusa", "excusas", "franco", "francos", "alta", "detenido", "prision",
        "medica", "medico", "medicas", "medicos", "total", "frecuente", "frecuentes", "comun", "comunes",
        "distribucion", "evolucion",
        "ranking", "rankings", "top", "tops", "recurrente", "recurrentes",
        "estadistica", "estadisticas", "conteo", "conteos", "grafica", "graficas", "tabla", "tablas",
        "causa", "causas", "motivo", "motivos", "afectacion", "afectaciones", "impacto",
        "principal", "principales", "mayor", "mayores", "menor", "menores",
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
        "consolidado", "consolidados", "mensual", "mensuales", "diario", "diarios",
        "expediente", "expedientes", "hoja", "vida", "sabana", "matriz", "heatmap",
        "agil", "agiles", "descargar", "descarga", "exportar", "exportacion", "exporte",
        "excel", "xlsx", "pdf", "csv", "archivo", "documento", "informe", "informes"
    }
    meses_set = {"enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre", "ene", "feb", "mar", "abr", "jun", "jul", "ago", "sep", "oct", "nov", "dic"}
    words = [w for w in re.split(r"[^a-z0-9ñáéíóú]+", msg_norm) if w]
    return [w for w in words if len(w) >= 3 and w not in stopwords and w not in meses_set and not w.isdigit()]

def _name_like_clause(token: str) -> str:
    """
    Genera una condición LIKE insensible a mayúsculas, tildes y N/Ñ mediante unaccent().
    Ej: 'peña' o 'pena' -> "unaccent(nombre) ILIKE unaccent('%pena%')"
    """
    t = token.strip()
    return f"unaccent(nombre) ILIKE unaccent('%{t}%')"

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

def _is_least_frequent(msg: str) -> bool:
    """Detecta si el mensaje pregunta por la novedad MENOS frecuente, menor o más rara."""
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

def _inspect_soldier_novedades(
    db: Optional[Any],
    cedula: int,
    mes_solicitado: Optional[str] = None,
    subnovedad_filtro: Optional[str] = None
) -> Dict[str, Any]:
    """Inspecciona y consolida las novedades registradas de un militar por mes y subnovedad."""
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

        def _match_nov(subnov_query: str, nov_name: str) -> bool:
            sq = subnov_query.upper().strip()
            nv = nov_name.upper().strip()
            if sq == nv or sq in nv or nv in sq:
                return True
            # Equivalencia oficial entre INCAPACIDAD e I/R (Incapacidad / Reposo)
            if sq in ("INCAPACIDAD", "INCAPACIDADES", "I/R", "REPOSO", "EXCUSA", "EXCUSA MEDICA"):
                if nv in ("INCAPACIDAD", "I/R") or "INCAPACIDAD" in nv or nv == "I/R":
                    return True
            return False

        if mes_solicitado and mes_solicitado.upper() not in ("TODOS", "ANUAL", "ALL"):
            m_req = mes_solicitado.upper()
            # Detección de rango de meses (ej: "MARZO - SEPTIEMBRE", "MARZO A SEPTIEMBRE")
            r_words = re.findall(r"\b[A-Z]+\b", m_req)
            lookup_meses = {
                'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4,
                'MAYO': 5, 'JUNIO': 6, 'JULIO': 7, 'AGOSTO': 8,
                'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12
            }
            range_nums = [lookup_meses[w] for w in r_words if w in lookup_meses]
            if len(range_nums) >= 2:
                target_range_nums = set(range(min(range_nums[0], range_nums[-1]), max(range_nums[0], range_nums[-1]) + 1))
                target_m_infos = [info for info in meses_dict.values() if info["mes_num"] in target_range_nums]
                dias_novedad_mes = sum(info["total_dias"] for info in target_m_infos)
                combined_novs = {}
                for info in target_m_infos:
                    for nov, c in info["novedades"].items():
                        combined_novs[nov] = combined_novs.get(nov, 0) + c
                novedades_mes = combined_novs
                if novedades_mes:
                    top_novedad_mes = max(novedades_mes.items(), key=lambda x: x[1])[0]
                if subnovedad_filtro:
                    dias_filtro_mes = sum(c for nov, c in novedades_mes.items() if _match_nov(subnovedad_filtro, nov))
                    tiene_novedades_mes = (dias_filtro_mes > 0)
                else:
                    tiene_novedades_mes = (dias_novedad_mes > 0)
            elif m_req in meses_dict:
                m_info = meses_dict[m_req]
                dias_novedad_mes = m_info["total_dias"]
                novedades_mes = m_info["novedades"]
                if novedades_mes:
                    top_novedad_mes = max(novedades_mes.items(), key=lambda x: x[1])[0]
                if subnovedad_filtro:
                    dias_filtro_mes = sum(c for nov, c in novedades_mes.items() if _match_nov(subnovedad_filtro, nov))
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
                matched_days = sum(c for nov, c in m_info["novedades"].items() if _match_nov(subnovedad_filtro, nov))
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


def _detect_month_superlative_intent(msg_norm: str) -> Optional[str]:
    """
    Detecta si el usuario está solicitando identificar un mes superlativo
    (el mes con mayor/máxima novedad, más frecuente, pico, o menor/mínima novedad).
    Retorna 'max', 'min' o None.
    """
    m = msg_norm.lower()

    # Patrones para máximo / mayor
    max_patterns = [
        r"\b(el\s+)?mes\b.*(mayor|m[aá]s|pico|m[aá]xima?o?|m[aá]s\s+(frecuente|presente|reiterad[ao]|comun|común|alto))\b",
        r"\b(mayor|m[aá]s|pico|m[aá]xima?o?|m[aá]s\s+(frecuente|presente|reiterad[ao]|comun|común|alto))\b.*(el\s+)?mes\b",
        r"\b(en\s+qu[eé]\s+mes|cu[aá]l\s+mes)\b.*(mayor|m[aá]s|pico|m[aá]xima?o?)\b",
        r"\b(mes\s+para\s+exportar|mes\s+donde\s+tenga)\b.*(mayor|m[aá]s|pico|m[aá]xima?o?)\b",
    ]
    for pat in max_patterns:
        if re.search(pat, m):
            return "max"

    # Patrones para mínimo / menor
    min_patterns = [
        r"\b(el\s+)?mes\b.*(menor|menos|m[ií]nima?o?|menos\s+(frecuente|presente|reiterad[ao]|comun|común|bajo))\b",
        r"\b(menor|menos|m[ií]nima?o?|menos\s+(frecuente|presente|reiterad[ao]|comun|común|bajo))\b.*(el\s+)?mes\b",
        r"\b(en\s+qu[eé]\s+mes|cu[aá]l\s+mes)\b.*(menor|menos|m[ií]nima?o?)\b",
        r"\b(mes\s+para\s+exportar|mes\s+donde\s+tenga)\b.*(menor|menos|m[ií]nima?o?)\b",
    ]
    for pat in min_patterns:
        if re.search(pat, m):
            return "min"

    return None


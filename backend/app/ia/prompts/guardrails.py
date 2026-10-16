"""
Guardrails de confinamiento militar, detección de intención fuera de dominio,
respuestas conversacionales rápidas y autosíntesis de resultados para BIMEH.
"""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from app.ia.nlp.normalizer import _norm
from app.ia.nlp.date_extractor import _extract_month, _extract_month_range, MESES_ES, check_month_has_data
from app.ia.nlp.militar_matcher import _extract_novedad_type

REFUSAL_PHRASES: List[str] = [
    "lo siento", "no puedo", "cannot", "i'm sorry", "i cannot",
    "no puedo proporcionar", "unable to",
]

REFUSAL_MESSAGE: str = (
    "Mi Comandante, como Asistente de BIMEJ 12 en la plataforma BIMEH, mi función operativa "
    "está restringida exclusivamente a la administración de personal, novedades y reportes de este batallón. "
    "No estoy autorizado para atender consultas ajenas al ecosistema de nuestra unidad militar. "
    "¿Desea consultar algún dato o reporte sobre los efectivos de BIMEJ 12?"
)

def _is_refusal(text: str) -> bool:
    """Verifica si el texto generado por un LLM es una denegación genérica."""
    t = text.lower().strip()
    return any(p in t for p in REFUSAL_PHRASES)

def is_query_in_domain(message: str) -> bool:
    """
    Verifica si la consulta está dentro del dominio del Batallón BIMEJ 12 / sistema BIMEH.
    Rechaza consultas evidentes sobre cocina, deportes, tareas escolares, etc.
    """
    msg = _norm(message)
    out_of_domain_keywords = [
        "receta", "cocinar", "futbol", "champions", "pelicula", "cancion",
        "horoscopo", "poema", "chiste", "codigo python", "javascript", "react",
        "formula 1", "nba", "bitcoin", "criptomoneda", "clima manana", "chistes"
    ]
    if any(k in msg for k in out_of_domain_keywords):
        return False
    return True

def _is_conversational_inquiry(msg_norm: str) -> bool:
    """
    Detecta si el mensaje es una consulta conversacional sobre capacidades o dudas,
    que debe ser respondida con texto y NO interceptada como descarga directa de archivo.
    """
    inquiry_patterns = [
        r"^(puedes|podrias|es posible|se puede|hay forma|tienes opcion|se podria|seria posible)\b",
        r"\b(puedes|podrias|se puede|es posible|hay forma|tienes opcion)\s+(hacerlo|sacarlo|filtrarlo|generarlo|consultarlo|verlo|hacer|sacar|filtrar|generar|consultar|ver)\b",
        r"\b(por|para)\s+(un|una|algun|alguna|cierto|determinado)?\s*(personal|militar|soldado|persona)\s+(en\s+)?(especifico|especifica|particular)\b",
        r"\b(como\s+funciona|como\s+se\s+hace|como\s+puedo|para\s+que\s+sirve|que\s+significa)\b",
        r"\b(que\s+diferencia\s+hay|cual\s+es\s+la\s+diferencia)\b",
        r"\b(puedes\s+explicar|me\s+explicas|explicame)\b",
        r"\b(que\s+opciones|que\s+formatos)\b",
    ]
    return any(re.search(pat, msg_norm) for pat in inquiry_patterns)

def get_fast_conversational_reply(text: str) -> Optional[Tuple[str, str]]:
    """
    Provee respuestas inmediatas (<5ms) para saludos, cortesías y preguntas sobre capacidades,
    ahorrando tiempo de inferencia y llamadas al LLM.
    """
    msg = _norm(text)
    saludos = ["hola", "buenos dias", "buenas tardes", "buenas noches", "buen dia"]
    if any(s in msg for s in saludos):
        hora = datetime.now().hour
        saludo = "Buenos días" if hora < 12 else "Buenas tardes" if hora < 19 else "Buenas noches"
        return "saludo", f"{saludo}, mi Comandante. Soy el Asistente de Personal de BIMEJ 12. ¿Cómo le puedo colaborar hoy?"

    gracias = ["gracias", "muchas gracias", "perfecto", "excelente", "muy bien"]
    if any(g in msg for g in gracias):
        return "cortesia", "A sus órdenes, mi Comandante. ¿Requiere alguna consulta o reporte adicional sobre la unidad?"

    reportes_info_keywords = [
        "que mas reportes", "que otros reportes", "que reportes puedes", "que reportes sabes",
        "que reportes hay", "que reportes tienes", "cuales reportes", "que tipo de reportes",
        "formatos de reporte", "como funcionan los reportes", "que reportes existen"
    ]
    if any(k in msg for k in reportes_info_keywords):
        return "ayuda_reportes", (
            "A sus órdenes, mi Comandante. En **BIMEJ 12** puedo generar y exportar reportes oficiales directamente en formatos **Excel (.xlsx)** y **PDF (.pdf)** con las siguientes modalidades:\n\n"
            "• **1. Consolidados Mensuales (Matriz Heatmap):**\n"
            "  Matriz operativa integral día a día que refleja el estado de cada efectivo (Disponible, Novedad, Retirado), disponible con codificación oficial de letras o vista visual por colores.\n\n"
            "• **2. Parte Ágil de Novedades:**\n"
            "  Resumen ejecutivo nominal agrupado cronológicamente por intervalos de fechas y novedades de ausentismo con justificaciones oficiales.\n\n"
            "• **3. Historial Completo de Novedades:**\n"
            "  Relación nominal detallada con fecha de reporte, inicio, término y descripción de la novedad registrada en la unidad.\n\n"
            "• **4. Reportes Detallados Diarios:**\n"
            "  Nómina completa de efectivos y ausentismos para una fecha específica (ej: *'Reporte del día de hoy'*).\n\n"
            "• **5. Expedientes Individuales de Militar:**\n"
            "  Historial cronológico de cualquier integrante orgánico por cédula o nombre (ej: *'Expediente de cédula 123456'* o *'Reporte de Gómez'*).\n\n"
            "• **6. Base de Datos Maestra y Catálogos:**\n"
            "  Censo de personal completo del batallón y catálogo oficial de subnovedades y códigos operacionales.\n\n"
            "💡 *Puede solicitarlos directamente en el chat (ej: 'Consolidado de junio en Excel' o 'Parte ágil de novedades de mayo') o seleccionando cualquiera de los botones interactivos.*"
        )

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
        return "despedida", "A sus órdenes, mi Comandante. Quedo atento a cualquier nuevo requerimiento para BIMEJ 12."

    return None

def _auto_synthesize(user_message: str, query_result: Dict[str, Any], db=None) -> str:
    """
    Sintetiza automáticamente los resultados de una consulta SQL en una respuesta militar
    cuando no se utiliza el LLM para redacción o en contingencia de cuotas.
    """
    total = query_result.get("total", 0)
    rows = query_result.get("rows", [])
    cols = query_result.get("columns", [])

    if total == 0:
        mes_solicitado = _extract_month(_norm(user_message))
        if mes_solicitado and not check_month_has_data(mes_solicitado, db):
            try:
                from app.database import get_available_date_range
                r_range = get_available_date_range(db)
                nombre_mes = [k for k, v in MESES_ES.items() if v == mes_solicitado and len(k) > 3]
                m_label = nombre_mes[0].capitalize() if nombre_mes else f"mes {mes_solicitado}"
                return (
                    f"Se consultó la base de datos de BIMEJ 12 pero **no se encontraron registros para {m_label}**, "
                    f"debido a que el sistema actualmente cuenta con reportes diarios cargados de **{r_range['texto']}** "
                    f"(no se registran partes diarios cargados para {m_label.lower()}).\n\n"
                    f"💡 Para consultar novedades de personal, puede solicitar un mes con registros disponibles como **{r_range['max_month'].lower()}**, "
                    f"o cargar/sincronizar los partes correspondientes desde el módulo de **Sincronizar Datos**."
                )
            except Exception:
                pass
        nov_type = _extract_novedad_type(_norm(user_message))
        if mes_solicitado and nov_type:
            nombre_mes = [k for k, v in MESES_ES.items() if v == mes_solicitado and len(k) > 3]
            m_label = nombre_mes[0].capitalize() if nombre_mes else f"mes {mes_solicitado}"
            return (
                f"Se consultó la base de datos de BIMEJ 12 para el mes de **{m_label}**, pero **no se registraron efectivos con novedad de {nov_type.lower()}** "
                f"en dicho período (el personal se encontraba disponible o con otras novedades registradas)."
            )
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

    # Caso 2: Reporte de fechas con novedad
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

    # Caso 3: Ranking de novedades frecuentes o menos frecuentes
    if "novedad" in cols and ("total_dias" in cols or "total_dias_registrados" in cols):
        is_least = any(w in _norm(user_message) for w in ["menos", "menor", "minima", "rara", "escas"])
        dias_col = "total_dias" if "total_dias" in cols else "total_dias_registrados"
        first_dias = rows[0].get(dias_col, 0)
        last_dias = rows[-1].get(dias_col, 0)

        meses_nombres = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        norm_msg = _norm(user_message)
        m_range = _extract_month_range(norm_msg)
        if m_range:
            m1, m2 = m_range
            nom1 = meses_nombres[m1 - 1]
            nom2 = meses_nombres[m2 - 1]
            mes_str = f" en el rango de {nom1} a {nom2}"
        else:
            mes_mencionado = next((m for m in meses_nombres if m in norm_msg), None)
            mes_str = f" durante el mes de {mes_mencionado}" if mes_mencionado else ""

        if is_least:
            target = rows[0] if first_dias <= last_dias else rows[-1]
            nov_nombre = target.get("novedad", "")
            dias = target.get(dias_col, 0)
            pers = target.get("total_personal_afectado")
            pers_str = f" ({pers} efectivos)" if pers else ""
            nombre_militar = target.get("nombre")
            if nombre_militar:
                return f"Novedad menos registrada para **{nombre_militar}**{mes_str}: **{nov_nombre}** con un total de **{dias} días**."
            return f"Novedad menos registrada en BIMEJ 12{mes_str}: **{nov_nombre}** con un total de **{dias} días** acumulados{pers_str}."
        else:
            target = rows[0] if first_dias >= last_dias else rows[-1]
            nov_nombre = target.get("novedad", "")
            dias = target.get(dias_col, 0)
            pers = target.get("total_personal_afectado")
            pers_str = f" ({pers} efectivos)" if pers else ""
            nombre_militar = target.get("nombre")
            if nombre_militar:
                return f"Novedad más registrada para **{nombre_militar}**{mes_str}: **{nov_nombre}** con un total de **{dias} días**."
            return f"Novedad más registrada en BIMEJ 12{mes_str}: **{nov_nombre}** con un total de **{dias} días** acumulados{pers_str}."

    # Caso 4: Lista de personal
    if "cedula" in cols and "nombre" in cols:
        nombres = [r.get("nombre", "") for r in rows[:5] if r.get("nombre")]
        muestra = ", ".join(nombres[:3])
        resto = f" y {total - 3} más" if total > 3 else ""
        return f"Se encontraron **{total} registros** en BIMEJ 12. Personal: **{muestra}{resto}**."

    return f"Se encontraron **{total} registros** coincidentes en la base de datos de BIMEJ 12."

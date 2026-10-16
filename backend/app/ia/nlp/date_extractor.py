"""
Extracción y validación de componentes de fecha y tiempo en lenguaje natural.
"""

import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

MESES_ES: Dict[str, int] = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}

MESES_STR_MAP: Dict[str, str] = {
    "enero": "ENERO", "febrero": "FEBRERO", "marzo": "MARZO", "abril": "ABRIL",
    "mayo": "MAYO", "junio": "JUNIO", "julio": "JULIO", "agosto": "AGOSTO",
    "septiembre": "SEPTIEMBRE", "octubre": "OCTUBRE", "noviembre": "NOVIEMBRE", "diciembre": "DICIEMBRE",
    "ene": "ENERO", "feb": "FEBRERO", "mar": "MARZO", "abr": "ABRIL",
    "jun": "JUNIO", "jul": "JULIO", "ago": "AGOSTO", "sep": "SEPTIEMBRE",
    "oct": "OCTUBRE", "nov": "NOVIEMBRE", "dic": "DICIEMBRE"
}

def _last_day_of_month(year: int, month: int) -> int:
    """Retorna el último día calendario para un mes y año dados."""
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if month in (4, 6, 9, 11):
        return 30
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return 29
    return 28

def _extract_month_range(msg_norm: str) -> Optional[Tuple[int, int]]:
    """
    Extrae un rango de meses (inicio, fin) en base a lenguaje natural.
    Ejemplos:
      - 'en el rango de marzo a octubre' -> (3, 10)
      - 'entre marzo y octubre' -> (3, 10)
      - 'de marzo a octubre' -> (3, 10)
      - 'desde marzo hasta octubre' -> (3, 10)
      - 'marzo a octubre' -> (3, 10)
    """
    patterns = [
        r"\b(?:en\s+el\s+)?(?:rango|periodo|lapso|intervalo)\s+(?:de|entre|del?)?\s+([a-z]+)\s+(?:a|al|hasta|y)\s+(?:el\s+)?([a-z]+)\b",
        r"\b(?:entre|desde|del?)\s+(?:mes\s+de\s+|de\s+)?([a-z]+)\s+(?:a|al|hasta|y)\s+(?:mes\s+de\s+|el\s+)?([a-z]+)\b",
        r"\b([a-z]+)\s*(?:a|al|hasta|-)\s*([a-z]+)\b",
    ]
    for pat in patterns:
        for m in re.finditer(pat, msg_norm):
            w1, w2 = m.group(1).strip(), m.group(2).strip()
            if w1 in MESES_ES and w2 in MESES_ES:
                m1, m2 = MESES_ES[w1], MESES_ES[w2]
                if m1 != m2:
                    return (min(m1, m2), max(m1, m2))
    return None

def _extract_month(msg_norm: str) -> Optional[int]:
    """Extrae el número de mes (1..12) a partir de texto normalizado o expresiones relativas."""
    # 0. Si es un rango de meses, el primer mes es el inicio
    m_range = _extract_month_range(msg_norm)
    if m_range:
        return m_range[0]

    # 1. Triggers relativos directos
    if re.search(r"\b(este mes|en este mes|mes actual|presente mes|mes en curso|del mes)\b", msg_norm):
        return datetime.now().month
    if re.search(r"\b(mes pasado|el mes pasado|mes anterior|el mes anterior)\b", msg_norm):
        m = datetime.now().month - 1
        return 12 if m == 0 else m

    # 2. Búsqueda explícita de nombres de mes
    for nombre, num in MESES_ES.items():
        if re.search(rf"\b{re.escape(nombre)}\b", msg_norm):
            return num
    return None

def _extract_month_name(msg_norm: str) -> Optional[str]:
    """Extrae el nombre oficial del mes en mayúsculas, rango de meses o 'TODOS'."""
    m_range = _extract_month_range(msg_norm)
    if m_range:
        nombres = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        return f"{nombres[m_range[0]-1]} - {nombres[m_range[1]-1]}"

    if re.search(r"\b(todos|todo el ano|anual|ano completo|anualidad|todos los meses)\b", msg_norm):
        return "TODOS"
    if re.search(r"\b(este mes|en este mes|mes actual|presente mes|mes en curso|del mes)\b", msg_norm):
        now_m = datetime.now().month
        nombres = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        return nombres[now_m - 1]
    if re.search(r"\b(mes pasado|el mes pasado|mes anterior|el mes anterior)\b", msg_norm):
        m = datetime.now().month - 1
        idx = 11 if m == 0 else (m - 1)
        nombres = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
        return nombres[idx]
    for k, v in MESES_STR_MAP.items():
        if re.search(rf"\b{re.escape(k)}\b", msg_norm):
            return v
    return None

def _extract_year(msg_norm: str, default_year: int) -> int:
    """Extrae el año explícito de 4 dígitos (20XX) o retorna el valor por defecto."""
    match = re.search(r"\b(20\d{2})\b", msg_norm)
    return int(match.group(1)) if match else default_year

def _extract_day_range(msg_norm: str) -> Optional[Tuple[int, int]]:
    """Extrae rangos de días tipo 'del 1 al 15', 'entre el 5 y el 20', etc."""
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

def _extract_date_range(msg_norm: str, user_msg: str = "", default_year: int = 2026) -> Optional[Tuple[str, str]]:
    """
    Extrae un rango de fechas absoluto (fecha_inicio, fecha_fin) en formato 'YYYY-MM-DD'.
    Maneja:
      1. Rango explícito de fechas ISO: '2026-03-01 al 2026-10-31'
      2. Rango entre días de diferentes meses: 'del 5 de marzo al 20 de octubre'
      3. Rango de meses completos: 'de marzo a octubre' -> '2026-03-01' a '2026-10-31'
      4. Rango de días en el mismo mes: 'del 1 al 15 de marzo' -> '2026-03-01' a '2026-03-15'
      5. Mes individual completo: 'en marzo' -> '2026-03-01' a '2026-03-31'
    """
    anio = _extract_year(msg_norm, default_year)

    # 1. Rango de fechas ISO YYYY-MM-DD
    iso_range = re.search(r"\b(20\d{2}-\d{1,2}-\d{1,2})\s+(?:al?|hasta|-)\s+(20\d{2}-\d{1,2}-\d{1,2})\b", user_msg)
    if iso_range:
        f1, f2 = iso_range.group(1), iso_range.group(2)
        return (f1, f2)

    # 2. Días entre diferentes meses (ej: del 5 de marzo al 20 de octubre)
    diff_months_day_range = re.search(
        r"\b(?:del?|desde)\s+(\d{1,2})\s+de\s+([a-z]+)\s+(?:al?|hasta)\s+(?:el\s+)?(\d{1,2})\s+de\s+([a-z]+)\b",
        msg_norm
    )
    if diff_months_day_range:
        d1, m1_str, d2, m2_str = (
            int(diff_months_day_range.group(1)),
            diff_months_day_range.group(2),
            int(diff_months_day_range.group(3)),
            diff_months_day_range.group(4)
        )
        if m1_str in MESES_ES and m2_str in MESES_ES:
            m1, m2 = MESES_ES[m1_str], MESES_ES[m2_str]
            return (f"{anio}-{m1:02d}-{d1:02d}", f"{anio}-{m2:02d}-{d2:02d}")

    # 3. Rango de meses completos (ej: rango de marzo a octubre, entre marzo y octubre)
    m_range = _extract_month_range(msg_norm)
    if m_range:
        m1, m2 = m_range
        last_d = _last_day_of_month(anio, m2)
        return (f"{anio}-{m1:02d}-01", f"{anio}-{m2:02d}-{last_d:02d}")

    # 4. Rango de días dentro del mismo mes (ej: del 1 al 15 de marzo)
    d_range = _extract_day_range(msg_norm)
    single_month = None
    for nombre, num in MESES_ES.items():
        if re.search(rf"\b{re.escape(nombre)}\b", msg_norm):
            single_month = num
            break
    if single_month is None:
        if re.search(r"\b(este mes|mes actual)\b", msg_norm):
            single_month = datetime.now().month

    if d_range and single_month:
        d1, d2 = d_range
        return (f"{anio}-{single_month:02d}-{d1:02d}", f"{anio}-{single_month:02d}-{d2:02d}")

    # 5. Mes individual completo
    if single_month:
        last_d = _last_day_of_month(anio, single_month)
        return (f"{anio}-{single_month:02d}-01", f"{anio}-{single_month:02d}-{last_d:02d}")

    return None

def _extract_report_date(msg_norm: str, user_msg: str) -> Optional[str]:
    """Extrae una fecha puntual para reportes diarios en formato YYYY-MM-DD."""
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

def get_month_name_from_date(date_str: str) -> Optional[str]:
    """Retorna el nombre oficial del mes en mayúsculas a partir de una fecha YYYY-MM-DD."""
    NUM_TO_MES = {
        1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
        5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
        9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
    }
    try:
        if not date_str:
            return None
        parts = date_str.split("-")
        if len(parts) >= 2:
            m_num = int(parts[1])
            return NUM_TO_MES.get(m_num)
    except Exception:
        pass
    return None

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

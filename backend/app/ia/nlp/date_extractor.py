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

def _extract_month(msg_norm: str) -> Optional[int]:
    """Extrae el número de mes (1..12) a partir de texto normalizado."""
    for nombre, num in MESES_ES.items():
        if re.search(rf"\b{re.escape(nombre)}\b", msg_norm):
            return num
    return None

def _extract_month_name(msg_norm: str) -> Optional[str]:
    """Extrae el nombre oficial del mes en mayúsculas o 'TODOS'."""
    if re.search(r"\b(todos|todo el ano|anual|ano completo|anualidad|todos los meses)\b", msg_norm):
        return "TODOS"
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

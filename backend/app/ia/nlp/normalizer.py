"""
Normalización de texto en español para procesamiento de lenguaje natural.
"""

import re
import unicodedata

def _norm(text: str) -> str:
    """
    Normaliza a minúsculas sin tildes ni puntuación innecesaria para matching robusto.
    Preserva caracteres alfanuméricos y espacios simples.
    """
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFD", text.lower())
    sin_tildes = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w\s]", " ", sin_tildes).strip()

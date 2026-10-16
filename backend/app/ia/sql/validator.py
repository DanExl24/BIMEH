"""
Validación de seguridad para sentencias SQL generadas por LLM o catálogo.
Garantiza que únicamente se ejecuten consultas SELECT de solo lectura.
"""

import re
from typing import Tuple

BANNED_SQL = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|REPLACE|GRANT|REVOKE|EXEC|EXECUTE|SHUTDOWN|COPY|VACUUM)\b",
    re.IGNORECASE
)

def is_sql_safe(sql: str) -> bool:
    """Verifica si la sentencia SQL no contiene comandos destructivos ni de modificación."""
    if not sql or not sql.strip():
        return False
    # Verificar keywords prohibidas
    if BANNED_SQL.search(sql):
        return False
    # Verificar que empiece con SELECT o WITH
    clean_sql = sql.strip().upper()
    return clean_sql.startswith("SELECT") or clean_sql.startswith("WITH")

def validate_sql(sql: str) -> Tuple[bool, str]:
    """
    Valida rigurosamente la sentencia SQL.
    Retorna (es_valido, motivo_error).
    """
    if not sql or not sql.strip():
        return False, "Sentencia SQL vacía."
    
    clean_sql = sql.strip()
    match = BANNED_SQL.search(clean_sql)
    if match:
        return False, f"Comando no permitido detectado: '{match.group(0).upper()}'."
    
    upper_sql = clean_sql.upper()
    if not (upper_sql.startswith("SELECT") or upper_sql.startswith("WITH")):
        return False, "La consulta debe iniciar con SELECT o WITH."
    
    return True, ""

"""
Ejecutor seguro de consultas SQL para el subsistema de IA de BIMEH.
"""

import logging
from typing import Tuple, List, Dict, Any
from app.ia.sql.validator import is_sql_safe

logger = logging.getLogger(__name__)

def execute_safe_query(db, sql: str, max_rows: int = 1000) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Ejecuta una consulta SQL validada en modo solo lectura sobre la base de datos PostgreSQL.
    
    Retorna:
        (columnas, filas_como_diccionarios)
    
    Lanza:
        ValueError: Si la sentencia SQL contiene cláusulas prohibidas.
        Exception: Si ocurre un error durante la ejecución en PostgreSQL.
    """
    if not is_sql_safe(sql):
        logger.warning(f"[execute_safe_query] Intento de ejecutar SQL no permitido: {sql}")
        raise ValueError(f"SQL no permitido por políticas de seguridad: {sql}")
    
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        columns = [d[0] for d in cursor.description] if cursor.description else []
        rows_raw = cursor.fetchall()
        
        rows: List[Dict[str, Any]] = []
        for row in rows_raw[:max_rows]:
            rd: Dict[str, Any] = {}
            for i, col in enumerate(columns):
                v = row[i]
                if hasattr(v, "isoformat"):
                    v = v.isoformat()
                elif hasattr(v, "__str__") and type(v).__name__ in ("Decimal", "UUID"):
                    v = str(v)
                rd[col] = v
            rows.append(rd)
            
        return columns, rows
    finally:
        cursor.close()

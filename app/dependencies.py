from datetime import datetime
from typing import List, Optional

DISPONIBLE_STATUSES = ["CDO UNIDAD", "AREA OPERACIONES"]

def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")

def get_report_ids_for_filter(db, mes: Optional[str] = None, dia: Optional[str] = None, fecha: Optional[str] = None) -> List[tuple]:
    cursor = db.cursor()
    
    if fecha:
        cursor.execute("SELECT id, fecha FROM REPORTES WHERE fecha = ?;", (fecha,))
        return cursor.fetchall()
        
    query = "SELECT id, fecha FROM REPORTES"
    where_clauses = []
    params = []
    
    month_order = {
        "ENERO": "01", "FEBRERO": "02", "MARZO": "03", "ABRIL": "04",
        "MAYO": "05", "JUNIO": "06", "JULIO": "07", "AGOSTO": "08",
        "SEPTIEMBRE": "09", "OCTUBRE": "10", "NOVIEMBRE": 11, "DICIEMBRE": "12"
    }
    
    if mes and mes.upper() in month_order:
        month_num = month_order[mes.upper()]
        where_clauses.append("strftime('%m', fecha) = ?")
        params.append(month_num)
        
    if dia:
        day_str = dia.zfill(2)
        where_clauses.append("strftime('%d', fecha) = ?")
        params.append(day_str)
        
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
        
    query += " ORDER BY fecha ASC;"
    
    cursor.execute(query, params)
    return cursor.fetchall()

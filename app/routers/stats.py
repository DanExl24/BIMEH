from fastapi import APIRouter, Depends, Query
from typing import List

from app.database import get_db, get_month_dates
from app.dependencies import DISPONIBLE_STATUSES

router = APIRouter(prefix="/api/stats", tags=["Estadísticas"])

@router.get("/ranking")
def get_stats_rankings(db = Depends(get_db)):
    cursor = db.cursor()
    
    # Most frequent subnovedades globally
    cursor.execute("""
        SELECT sn.nombre, COUNT(*) as total_dias
        FROM REGISTRO_PERSONAL rp
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        GROUP BY sn.nombre
        ORDER BY total_dias DESC;
    """)
    global_rank = [{"subnovedad": r[0], "dias_acumulados": r[1]} for r in cursor.fetchall()]
    
    # People with most novelty days
    placeholders = ",".join("?" for _ in DISPONIBLE_STATUSES)
    cursor.execute(f"""
        SELECT p.cedula, p.nombre, COUNT(*) as dias_novedad
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON rp.id_personal = p.id
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        WHERE sn.nombre NOT IN ({placeholders})
        GROUP BY p.id, p.cedula, p.nombre
        ORDER BY dias_novedad DESC
        LIMIT 15;
    """, DISPONIBLE_STATUSES)
    most_novelties_people = [{"cedula": r[0], "nombre": r[1], "dias_novedad": r[2]} for r in cursor.fetchall()]
    
    return {
        "global_rank": global_rank,
        "most_novelties_people": most_novelties_people
    }

@router.get("/heatmap")
def get_stats_heatmap(mes: str = Query(...), db = Depends(get_db)):
    dates = get_month_dates(mes)
    if not dates:
        return {"fechas": [], "data": []}
        
    cursor = db.cursor()
    
    # Get all reports in this month and map them to their index
    cursor.execute(f"SELECT id, fecha FROM REPORTES WHERE fecha IN ({','.join('?' for _ in dates)}) ORDER BY fecha ASC;", dates)
    reports = cursor.fetchall()
    report_ids = [r[0] for r in reports]
    report_id_to_date = {r[0]: r[1] for r in reports}
    
    # Find all personnel that have at least one record in these reports
    cursor.execute(f"""
        SELECT DISTINCT p.id, p.cedula, p.nombre, p.fecha_retiro
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON rp.id_personal = p.id
        WHERE rp.id_reporte IN ({','.join('?' for _ in report_ids)})
        ORDER BY p.nombre ASC;
    """, report_ids)
    personnel = cursor.fetchall()
    
    # Fetch all records for these people on these reports
    cursor.execute(f"""
        SELECT rp.id_personal, rp.id_reporte, sn.nombre
        FROM REGISTRO_PERSONAL rp
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        WHERE rp.id_reporte IN ({','.join('?' for _ in report_ids)});
    """, report_ids)
    
    records = cursor.fetchall()
    # Create lookup map: (person_id, date) -> subnovedad_name
    record_map = {}
    for r in records:
        pid, rid, sub_name = r[0], r[1], r[2]
        date_str = report_id_to_date.get(rid)
        if date_str:
            record_map[(pid, date_str)] = sub_name
            
    heatmap_data = []
    for p in personnel:
        pid, cedula, nombre, f_retiro = p[0], p[1], p[2], p[3]
        estados = []
        for d in dates:
            is_retired = False
            if f_retiro and d >= f_retiro:
                is_retired = True
                
            if is_retired:
                est = "RETIRADO"
            else:
                est = record_map.get((pid, d))
                if est is None:
                    est = "N/A"
            estados.append(est)
            
        heatmap_data.append({
            "cedula": cedula,
            "nombre": nombre,
            "estados": estados
        })
        
    return {
        "fechas": dates,
        "data": heatmap_data
    }

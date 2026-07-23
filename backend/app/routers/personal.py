from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional

from app.database import get_db, get_month_dates
from app.dependencies import DISPONIBLE_STATUSES

router = APIRouter(prefix="/api", tags=["Personal"])

@router.get("/personal/buscar")
def buscar_personal(q: str = Query(..., min_length=2), db = Depends(get_db)):
    cursor = db.cursor()
    
    # Try search by digit (cedula) or by name pattern
    search_pattern = f"%{q.upper()}%"
    cursor.execute("""
        SELECT cedula, nombre, CASE WHEN fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END as estado, fecha_retiro 
        FROM PERSONAL 
        WHERE CAST(cedula AS TEXT) LIKE ? OR nombre LIKE ?
        LIMIT 50;
    """, (search_pattern, search_pattern))
    
    rows = cursor.fetchall()
    return [{
        "cedula": row[0],
        "nombre": row[1],
        "estado": row[2],
        "fecha_retiro": row[3]
    } for row in rows]

@router.get("/personal/{cedula}")
def get_personal_detalle(cedula: int, db = Depends(get_db)):
    cursor = db.cursor()
    
    # Find personnel
    cursor.execute("SELECT id, nombre, CASE WHEN fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END as estado, fecha_retiro FROM PERSONAL WHERE cedula = ?;", (cedula,))
    p_row = cursor.fetchone()
    if not p_row:
        raise HTTPException(status_code=404, detail="Personal no encontrado.")
        
    p_id, nombre, estado, fecha_retiro = p_row[0], p_row[1], p_row[2], p_row[3]
    
    # Get all reports the user is in
    cursor.execute("""
        SELECT r.fecha, sn.nombre 
        FROM REGISTRO_PERSONAL rp
        JOIN REPORTES r ON rp.id_reporte = r.id
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        WHERE rp.id_personal = ?
        ORDER BY r.fecha ASC;
    """, (p_id,))
    
    records = cursor.fetchall()
    total_dias = len(records)
    
    if total_dias == 0:
        return {
            "cedula": cedula,
            "nombre": nombre,
            "estado": estado,
            "fecha_retiro": fecha_retiro,
            "primer_registro_fecha": None,
            "ultimo_registro_fecha": None,
            "total_dias": 0,
            "tiempo_disponible_pct": 0,
            "tiempo_novedades_pct": 0,
            "total_novedades": 0,
            "promedio_duracion_novedades": 0.0,
            "ultima_novedad": None
        }
        
    primer_registro_fecha = records[0][0]
    ultimo_registro_fecha = records[-1][0]
    
    disponibles_dias = sum(1 for r in records if r[1] in DISPONIBLE_STATUSES)
    tiempo_disponible_pct = round((disponibles_dias / total_dias * 100), 1)
    tiempo_novedades_pct = round((100.0 - tiempo_disponible_pct), 1)
    total_novedades = total_dias - disponibles_dias
    
    # Calculate average novelty length
    # An event is a run of consecutive reports in a non-available status
    novelty_runs = []
    current_run = 0
    
    for r in records:
        is_available = r[1] in DISPONIBLE_STATUSES
        if not is_available:
            current_run += 1
        else:
            if current_run > 0:
                novelty_runs.append(current_run)
                current_run = 0
                
    if current_run > 0:
        novelty_runs.append(current_run)
        
    promedio_duracion_novedades = round(sum(novelty_runs) / len(novelty_runs), 1) if novelty_runs else 0.0
    
    ultima_novedad = records[-1][1] if records else None
    
    return {
        "cedula": cedula,
        "nombre": nombre,
        "estado": estado,
        "fecha_retiro": fecha_retiro,
        "primer_registro_fecha": primer_registro_fecha,
        "ultimo_registro_fecha": ultimo_registro_fecha,
        "total_dias": total_dias,
        "tiempo_disponible_pct": tiempo_disponible_pct,
        "tiempo_novedades_pct": tiempo_novedades_pct,
        "total_novedades": total_novedades,
        "promedio_duracion_novedades": promedio_duracion_novedades,
        "ultima_novedad": ultima_novedad
    }

@router.get("/personal/{cedula}/historial")
def get_personal_historial(cedula: int, db = Depends(get_db)):
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM PERSONAL WHERE cedula = ?;", (cedula,))
    p_row = cursor.fetchone()
    if not p_row:
        raise HTTPException(status_code=404, detail="Personal no encontrado.")
    p_id = p_row[0]
    
    cursor.execute("""
        SELECT r.fecha, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final
        FROM REGISTRO_PERSONAL rp
        JOIN REPORTES r ON rp.id_reporte = r.id
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        WHERE rp.id_personal = ?
        ORDER BY r.fecha ASC;
    """, (p_id,))
    
    rows = cursor.fetchall()
    return [{
        "fecha": row[0],
        "subnovedad": row[1],
        "descripcion": row[2],
        "desde": row[3],
        "hasta": row[4]
    } for row in rows]

@router.get("/personal/{cedula}/acumulado")
def get_personal_acumulado(cedula: int, db = Depends(get_db)):
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM PERSONAL WHERE cedula = ?;", (cedula,))
    p_row = cursor.fetchone()
    if not p_row:
        raise HTTPException(status_code=404, detail="Personal no encontrado.")
    p_id = p_row[0]
    
    cursor.execute("""
        SELECT sn.nombre, COUNT(*) as dias
        FROM REGISTRO_PERSONAL rp
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        WHERE rp.id_personal = ?
        GROUP BY sn.nombre
        ORDER BY dias DESC;
    """, (p_id,))
    
    rows = cursor.fetchall()
    return [{"subnovedad": row[0], "dias": row[1]} for row in rows]

@router.get("/reportes/dia")
def get_reporte_dia(fecha: str = Query(...), db = Depends(get_db)):
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM REPORTES WHERE fecha = ?;", (fecha,))
    r_row = cursor.fetchone()
    if not r_row:
        return []
    r_id = r_row[0]
    
    cursor.execute("""
        SELECT p.cedula, p.nombre, sn.nombre as subnovedad, rp.descripcion, rp.fecha_inicio, rp.fecha_final
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON rp.id_personal = p.id
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        WHERE rp.id_reporte = ?
        ORDER BY p.nombre ASC;
    """, (r_id,))
    
    rows = cursor.fetchall()
    return [{
        "cedula": row[0],
        "nombre": row[1],
        "subnovedad": row[2],
        "descripcion": row[3],
        "desde": row[4],
        "hasta": row[5]
    } for row in rows]

@router.get("/reportes/calendario")
def get_calendario(mes: str = Query(...), db = Depends(get_db)):
    dates = get_month_dates(mes)
    if not dates:
        return []
        
    cursor = db.cursor()
    
    placeholders = ",".join("?" for _ in DISPONIBLE_STATUSES)
    cursor.execute(f"SELECT id FROM SUB_NOVEDADES WHERE nombre IN ({placeholders});", DISPONIBLE_STATUSES)
    avail_ids = [row[0] for row in cursor.fetchall()]
    
    avail_placeholders = ",".join("?" for _ in avail_ids)
    
    cal_data = []
    
    for d in dates:
        cursor.execute("SELECT id FROM REPORTES WHERE fecha = ?;", (d,))
        r_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = ?;", (r_id,))
        total = cursor.fetchone()[0]
        
        if total > 0 and avail_ids:
            cursor.execute(f"SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = ? AND id_sub_novedad IN ({avail_placeholders});", (r_id, *avail_ids))
            disponibles = cursor.fetchone()[0]
        else:
            disponibles = 0
            
        novedades = total - disponibles
        pct = round((disponibles / total * 100), 1) if total > 0 else 0.0
        
        cal_data.append({
            "fecha": d,
            "disponibilidad": pct,
            "total_personal": total,
            "disponibles": disponibles,
            "novedades": novedades
        })
        
    return cal_data

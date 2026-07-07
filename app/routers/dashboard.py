from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.dependencies import DISPONIBLE_STATUSES, get_report_ids_for_filter
from app.models import KPIData

router = APIRouter(prefix="/api", tags=["Dashboard"])

@router.get("/fechas")
def get_available_dates(db = Depends(get_db)):
    """Returns all dates that have reports, sorted chronologically."""
    cursor = db.cursor()
    cursor.execute("SELECT fecha FROM REPORTES ORDER BY fecha ASC;")
    dates = [row[0] for row in cursor.fetchall()]
    return dates

@router.get("/dashboard/kpis", response_model=KPIData)
def get_kpis(
    fecha: Optional[str] = Query(None, description="Fecha en formato YYYY-MM-DD"),
    mes: Optional[str] = Query(None, description="Nombre del mes (ENERO, FEBRERO...)"),
    dia: Optional[str] = Query(None, description="Día del mes (01, 02...)"),
    db = Depends(get_db)
):
    cursor = db.cursor()
    
    # If no parameters provided, default to the latest report date in DB
    if fecha is None and mes is None and dia is None:
        cursor.execute("SELECT fecha FROM REPORTES ORDER BY fecha DESC LIMIT 1;")
        latest_row = cursor.fetchone()
        if not latest_row:
            raise HTTPException(status_code=404, detail="No hay reportes cargados en el sistema.")
        fecha = latest_row[0]
        
    reports = get_report_ids_for_filter(db, mes, dia, fecha)
    if not reports:
        raise HTTPException(status_code=404, detail="No se encontraron reportes para el filtro seleccionado.")
        
    placeholders = ",".join("?" for _ in DISPONIBLE_STATUSES)
    cursor.execute(f"SELECT id FROM SUB_NOVEDADES WHERE nombre IN ({placeholders});", DISPONIBLE_STATUSES)
    available_ids = [row[0] for row in cursor.fetchall()]
    
    total_reports = len(reports)
    report_ids = [r[0] for r in reports]
    rep_placeholders = ",".join("?" for _ in report_ids)
    
    # Sum total personal
    cursor.execute(f"SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte IN ({rep_placeholders});", report_ids)
    sum_total_personal = cursor.fetchone()[0]
    
    # Sum disponibles
    sum_disponibles = 0
    if available_ids:
        av_placeholders = ",".join("?" for _ in available_ids)
        cursor.execute(f"""
            SELECT COUNT(*) FROM REGISTRO_PERSONAL 
            WHERE id_reporte IN ({rep_placeholders}) 
            AND id_sub_novedad IN ({av_placeholders});
        """, (*report_ids, *available_ids))
        sum_disponibles = cursor.fetchone()[0]
        
    # Averages
    avg_total_personal = int(round(sum_total_personal / total_reports)) if total_reports > 0 else 0
    avg_disponibles = int(round(sum_disponibles / total_reports)) if total_reports > 0 else 0
    avg_novedades = avg_total_personal - avg_disponibles
    avg_disponibilidad = round((avg_disponibles / avg_total_personal * 100), 1) if avg_total_personal > 0 else 0.0
    
    # Changes vs yesterday summed
    total_cambios = 0
    for r_id, r_fecha in reports:
        cursor.execute("SELECT id FROM REPORTES WHERE fecha < ? ORDER BY fecha DESC LIMIT 1;", (r_fecha,))
        prev_row = cursor.fetchone()
        if prev_row:
            prev_report_id = prev_row[0]
            
            cursor.execute("SELECT id_personal, id_sub_novedad FROM REGISTRO_PERSONAL WHERE id_reporte = ?;", (r_id,))
            today_statuses = {row[0]: row[1] for row in cursor.fetchall()}
            
            cursor.execute("SELECT id_personal, id_sub_novedad FROM REGISTRO_PERSONAL WHERE id_reporte = ?;", (prev_report_id,))
            yesterday_statuses = {row[0]: row[1] for row in cursor.fetchall()}
            
            all_person_ids = set(today_statuses.keys()).union(yesterday_statuses.keys())
            for pid in all_person_ids:
                if today_statuses.get(pid) != yesterday_statuses.get(pid):
                    total_cambios += 1
                    
    # Generate custom fecha label
    if fecha:
        fecha_label = fecha
    elif mes and dia:
        fecha_label = f"{mes} - Día {dia}"
    elif mes:
        fecha_label = f"Mes: {mes}"
    elif dia:
        fecha_label = f"Día {dia} (Anual)"
    else:
        fecha_label = "Anual (Todo el año)"
        
    return KPIData(
        fecha=fecha_label,
        total_personal=avg_total_personal,
        disponibles=avg_disponibles,
        novedades=avg_novedades,
        disponibilidad=avg_disponibilidad,
        cambios_vs_ayer=total_cambios
    )

@router.get("/dashboard/evolucion")
def get_evolucion(
    mes: Optional[str] = Query(None, description="Nombre del mes (ENERO, FEBRERO...)"),
    dia: Optional[str] = Query(None, description="Día del mes (01, 02...)"),
    db = Depends(get_db)
):
    cursor = db.cursor()
    
    reports = get_report_ids_for_filter(db, mes, dia, None)
    
    placeholders = ",".join("?" for _ in DISPONIBLE_STATUSES)
    cursor.execute(f"SELECT id FROM SUB_NOVEDADES WHERE nombre IN ({placeholders});", DISPONIBLE_STATUSES)
    available_ids = [row[0] for row in cursor.fetchall()]
    
    evolution_data = []
    
    for r in reports:
        report_id, date_str = r[0], r[1]
        
        cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = ?;", (report_id,))
        total = cursor.fetchone()[0]
        
        if available_ids:
            av_placeholders = ",".join("?" for _ in available_ids)
            cursor.execute(f"SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = ? AND id_sub_novedad IN ({av_placeholders});", (report_id, *available_ids))
            disponibles = cursor.fetchone()[0]
        else:
            disponibles = 0
            
        novedades = total - disponibles
        disponibilidad = round((disponibles / total * 100), 1) if total > 0 else 0.0
        
        evolution_data.append({
            "fecha": date_str,
            "total_personal": total,
            "disponibles": disponibles,
            "novedades": novedades,
            "disponibilidad": disponibilidad
        })
        
    return evolution_data

@router.get("/dashboard/novedades-frecuentes")
def get_novedades_frecuentes(
    fecha: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    dia: Optional[str] = Query(None),
    db = Depends(get_db)
):
    cursor = db.cursor()
    
    if fecha is None and mes is None and dia is None:
        cursor.execute("SELECT fecha FROM REPORTES ORDER BY fecha DESC LIMIT 1;")
        latest_row = cursor.fetchone()
        if latest_row:
            fecha = latest_row[0]
            
    reports = get_report_ids_for_filter(db, mes, dia, fecha)
    if not reports:
        return []
        
    report_ids = [r[0] for r in reports]
    rep_placeholders = ",".join("?" for _ in report_ids)
    
    ex_placeholders = ",".join("?" for _ in DISPONIBLE_STATUSES)
    
    cursor.execute(f"""
        SELECT sn.nombre, COUNT(*) as cantidad 
        FROM REGISTRO_PERSONAL rp 
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        WHERE rp.id_reporte IN ({rep_placeholders})
        AND sn.nombre NOT IN ({ex_placeholders})
        GROUP BY sn.nombre 
        ORDER BY cantidad DESC;
    """, (*report_ids, *DISPONIBLE_STATUSES))
    
    rows = cursor.fetchall()
    return [{"novedad": row[0], "cantidad": row[1]} for row in rows]

@router.get("/dashboard/distribucion")
def get_distribucion(
    fecha: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    dia: Optional[str] = Query(None),
    db = Depends(get_db)
):
    cursor = db.cursor()
    
    if fecha is None and mes is None and dia is None:
        cursor.execute("SELECT fecha FROM REPORTES ORDER BY fecha DESC LIMIT 1;")
        latest_row = cursor.fetchone()
        if latest_row:
            fecha = latest_row[0]
            
    reports = get_report_ids_for_filter(db, mes, dia, fecha)
    if not reports:
        return []
        
    report_ids = [r[0] for r in reports]
    rep_placeholders = ",".join("?" for _ in report_ids)
    
    cursor.execute(f"""
        SELECT sn.nombre, COUNT(*) as cantidad
        FROM REGISTRO_PERSONAL rp
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        WHERE rp.id_reporte IN ({rep_placeholders})
        GROUP BY sn.nombre
        ORDER BY cantidad DESC;
    """, report_ids)
    
    rows = cursor.fetchall()
    total = sum(row[1] for row in rows)
    num_days = len(reports)
    
    dist = []
    for row in rows:
        nombre = row[0]
        cantidad_total = row[1]
        cantidad_avg = int(round(cantidad_total / num_days)) if num_days > 0 else 0
        pct = round((cantidad_total / total * 100), 1) if total > 0 else 0.0
        
        categoria = "DISPONIBLE" if nombre in DISPONIBLE_STATUSES else "NOVEDAD"
        
        dist.append({
            "subnovedad": nombre,
            "cantidad": cantidad_avg,
            "porcentaje": pct,
            "categoria": categoria
        })
        
    return dist

@router.get("/dashboard/cambios")
def get_cambios(
    fecha: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    dia: Optional[str] = Query(None),
    db = Depends(get_db)
):
    cursor = db.cursor()
    
    if fecha is None and mes is None and dia is None:
        cursor.execute("SELECT fecha FROM REPORTES ORDER BY fecha DESC LIMIT 1;")
        latest_row = cursor.fetchone()
        if latest_row:
            fecha = latest_row[0]
            
    reports = get_report_ids_for_filter(db, mes, dia, fecha)
    if not reports:
        return {"entraron_novedades": [], "volvieron_disponibles": [], "otros_cambios": []}
        
    entraron_novedades = []
    volvieron_disponibles = []
    otros_cambios = []
    
    seen_changes = set()
    
    for r_id, r_fecha in reports:
        cursor.execute("SELECT id FROM REPORTES WHERE fecha < ? ORDER BY fecha DESC LIMIT 1;", (r_fecha,))
        prev_row = cursor.fetchone()
        if not prev_row:
            continue
        prev_report_id = prev_row[0]
        
        cursor.execute("""
            SELECT rp.id_personal, p.cedula, p.nombre, sn.nombre
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            WHERE rp.id_reporte = ?;
        """, (r_id,))
        today_map = {row[0]: {"cedula": row[1], "nombre": row[2], "subnovedad": row[3]} for row in cursor.fetchall()}
        
        cursor.execute("""
            SELECT rp.id_personal, p.cedula, p.nombre, sn.nombre
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            WHERE rp.id_reporte = ?;
        """, (prev_report_id,))
        prev_map = {row[0]: {"cedula": row[1], "nombre": row[2], "subnovedad": row[3]} for row in cursor.fetchall()}
        
        all_pids = set(today_map.keys()).union(prev_map.keys())
        
        for pid in all_pids:
            today_data = today_map.get(pid)
            prev_data = prev_map.get(pid)
            
            if today_data and prev_data:
                t_nov = today_data["subnovedad"]
                p_nov = prev_data["subnovedad"]
                
                if t_nov != p_nov:
                    change_key = (today_data["cedula"], p_nov, t_nov)
                    if change_key in seen_changes:
                        continue
                    seen_changes.add(change_key)
                    
                    change_item = {
                        "cedula": today_data["cedula"],
                        "nombre": today_data["nombre"],
                        "novedad_anterior": p_nov,
                        "novedad_nueva": t_nov,
                        "fecha": r_fecha
                    }
                    
                    p_disp = p_nov in DISPONIBLE_STATUSES
                    t_disp = t_nov in DISPONIBLE_STATUSES
                    
                    if p_disp and not t_disp:
                        entraron_novedades.append(change_item)
                    elif not p_disp and t_disp:
                        volvieron_disponibles.append(change_item)
                    else:
                        otros_cambios.append(change_item)
            elif today_data and not prev_data:
                t_nov = today_data["subnovedad"]
                change_key = (today_data["cedula"], "NO PRESENTADO", t_nov)
                if change_key in seen_changes:
                    continue
                seen_changes.add(change_key)
                
                change_item = {
                    "cedula": today_data["cedula"],
                    "nombre": today_data["nombre"],
                    "novedad_anterior": "NO PRESENTADO",
                    "novedad_nueva": t_nov,
                    "fecha": r_fecha
                }
                if t_nov in DISPONIBLE_STATUSES:
                    volvieron_disponibles.append(change_item)
                else:
                    entraron_novedades.append(change_item)
            elif prev_data and not today_data:
                p_nov = prev_data["subnovedad"]
                change_key = (prev_data["cedula"], p_nov, "RETIRADO / NO PRESENTADO")
                if change_key in seen_changes:
                    continue
                seen_changes.add(change_key)
                
                change_item = {
                    "cedula": prev_data["cedula"],
                    "nombre": prev_data["nombre"],
                    "novedad_anterior": p_nov,
                    "novedad_nueva": "RETIRADO / NO PRESENTADO",
                    "fecha": r_fecha
                }
                if p_nov in DISPONIBLE_STATUSES:
                    entraron_novedades.append(change_item)
                else:
                    otros_cambios.append(change_item)
                    
    return {
        "entraron_novedades": entraron_novedades[:150],
        "volvieron_disponibles": volvieron_disponibles[:150],
        "otros_cambios": otros_cambios[:150]
    }

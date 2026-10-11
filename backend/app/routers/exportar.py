from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
import io
import csv
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, landscape

from app.database import get_db, get_month_dates
from app.dependencies import DISPONIBLE_STATUSES

def format_agil_month_ranges(records: List[tuple], highlight_html: bool = False) -> str:
    """
    records: list of tuples (day_int, subnovedad_str, [desc]) sorted by day_int
    Returns string with line breaks for each novelty range:
    - HTML/PDF (<br/>): '<font color="#DC2626"><b>10-15</b></font> (VACACIONES)<br/><font color="#DC2626"><b>22</b></font> (PERMISO)'
    - Excel/Plain (\n): '10-15 (VACACIONES)\n22 (PERMISO)'
    """
    if not records:
        return "-"
    
    ranges = []
    curr_start = records[0][0]
    curr_end = records[0][0]
    curr_nov = records[0][1]
    
    def make_label(start: int, end: int, nov: str) -> str:
        day_str = f"{start:02d}" if start == end else f"{start:02d}-{end:02d}"
        if highlight_html:
            return f'<font color="#DC2626"><b>{day_str}</b></font> ({nov})'
        else:
            return f'{day_str} ({nov})'

    for rec in records[1:]:
        day = rec[0]
        nov = rec[1]
        if day == curr_end + 1 and nov == curr_nov:
            curr_end = day
        else:
            ranges.append(make_label(curr_start, curr_end, curr_nov))
            curr_start = day
            curr_end = day
            curr_nov = nov
            
    ranges.append(make_label(curr_start, curr_end, curr_nov))
        
    sep = "<br/>" if highlight_html else "\n"
    return sep.join(ranges)



router = APIRouter(prefix="/api/exportar", tags=["Exportaciones"])


@router.get("/csv")
def exportar_csv(
    tipo: str = Query(..., description="dia, mes, personal, personal_db, subnovedades, consolidado_mensual"),
    fecha: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    cedula: Optional[int] = Query(None),
    subnovedad: Optional[str] = Query(None),
    modo: Optional[str] = Query("letras"),
    db = Depends(get_db)
):
    print(f"\n[CSV REQUEST RECEIVED] tipo={tipo} | fecha={fecha} | mes={mes} | cedula={cedula} | subnovedad={subnovedad} | modo={modo}")
    output = io.StringIO()
    writer = csv.writer(output)
    
    cursor = db.cursor()
    
    if tipo == "dia":
        writer.writerow(["CEDULA", "APELLIDOS Y NOMBRES", "SUBNOVEDAD", "DESCRIPCION", "DESDE", "HASTA", "FECHA REPORTE"])
        query = """
            SELECT p.cedula, p.nombre, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final, r.fecha
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            JOIN REPORTES r ON rp.id_reporte = r.id
        """
        params = []
        where_clauses = []
        if fecha:
            where_clauses.append("r.fecha = %s")
            params.append(fecha)
        elif mes and mes.upper() != "TODOS":
            dates = get_month_dates(mes)
            if dates:
                placeholders = ",".join("%s" for _ in dates)
                where_clauses.append(f"r.fecha IN ({placeholders})")
                params.extend(dates)
            else:
                where_clauses.append("1=0")
                
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY r.fecha ASC, p.nombre ASC;"
        cursor.execute(query, params)
        for row in cursor.fetchall():
            writer.writerow(list(row))
            
        if fecha:
            filename = f"reporte_detallado_dia_{fecha}.csv"
        elif mes and mes.upper() != "TODOS":
            filename = f"reporte_detallado_mes_{mes}.csv"
        else:
            filename = "reporte_detallado_anual.csv"
        
    elif tipo == "mes" and mes:
        writer.writerow(["FECHA", "TOTAL PERSONAL", "DISPONIBLES", "NOVEDADES", "DISPONIBILIDAD %"])
        dates = get_month_dates(mes)
        for d in dates:
            cursor.execute("SELECT id FROM REPORTES WHERE fecha = %s;", (d,))
            r_row = cursor.fetchone()
            if not r_row:
                continue
            r_id = r_row[0]
            
            cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = %s;", (r_id,))
            total = cursor.fetchone()[0]
            
            placeholders = ",".join("%s" for _ in DISPONIBLE_STATUSES)
            cursor.execute(f"""
                SELECT COUNT(*) FROM REGISTRO_PERSONAL 
                WHERE id_reporte = %s AND id_sub_novedad IN (
                    SELECT id FROM SUB_NOVEDADES WHERE nombre IN ({placeholders})
                );
            """, (r_id, *DISPONIBLE_STATUSES))
            disp = cursor.fetchone()[0]
            nov = total - disp
            pct = round((disp / total * 100), 1) if total > 0 else 0.0
            writer.writerow([d, total, disp, nov, pct])
        filename = f"reporte_mensual_{mes}.csv"
        
    elif tipo == "personal" and cedula:
        writer.writerow(["FECHA", "SUBNOVEDAD", "DESCRIPCION", "DESDE", "HASTA"])
        cursor.execute("SELECT id, nombre FROM PERSONAL WHERE cedula = %s;", (cedula,))
        p_row = cursor.fetchone()
        if p_row:
            query = """
                SELECT r.fecha, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final
                FROM REGISTRO_PERSONAL rp
                JOIN REPORTES r ON rp.id_reporte = r.id
                JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                WHERE rp.id_personal = %s
            """
            params = [p_row[0]]
            if mes and mes.upper() != "TODOS":
                dates = get_month_dates(mes)
                if dates:
                    placeholders = ",".join("%s" for _ in dates)
                    query += f" AND r.fecha IN ({placeholders})"
                    params.extend(dates)
                else:
                    query += " AND 1=0"
            if subnovedad:
                query += " AND UPPER(sn.nombre) LIKE UPPER(%s)"
                params.append(f"%{subnovedad}%")
            query += " ORDER BY r.fecha ASC;"
            cursor.execute(query, tuple(params))
            for row in cursor.fetchall():
                writer.writerow(list(row))
        filename = f"historial_cedula_{cedula}.csv"
        
    elif tipo == "personal_db":
        writer.writerow(["CEDULA", "APELLIDOS Y NOMBRES", "ESTADO", "FECHA RETIRO"])
        cursor.execute("""
            SELECT cedula, nombre, CASE WHEN fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END as estado, fecha_retiro
            FROM PERSONAL
            ORDER BY nombre ASC;
        """)
        for row in cursor.fetchall():
            writer.writerow(list(row))
        filename = "base_datos_personal.csv"
        
    elif tipo == "subnovedades":
        writer.writerow(["ID", "NOMBRE NOVEDAD"])
        cursor.execute("SELECT id, nombre FROM SUB_NOVEDADES ORDER BY nombre ASC;")
        for row in cursor.fetchall():
            writer.writerow(list(row))
        filename = "catalogo_subnovedades.csv"
        
    elif tipo == "consolidado_mensual":
        is_all_months = not mes or mes.upper() == "TODOS" or mes == ""
        use_letras = (modo in ("letras", "colores"))
        
        if fecha:
            cursor.execute("SELECT id, fecha FROM REPORTES WHERE fecha = %s;", (fecha,))
            reports_db = cursor.fetchall()
        elif is_all_months:
            cursor.execute("SELECT id, fecha FROM REPORTES ORDER BY fecha ASC;")
            reports_db = cursor.fetchall()
        else:
            dates = get_month_dates(mes)
            if not dates:
                raise HTTPException(status_code=400, detail="No hay reportes para el mes especificado.")
            placeholders = ",".join("%s" for _ in dates)
            cursor.execute(f"SELECT id, fecha FROM REPORTES WHERE fecha IN ({placeholders}) ORDER BY fecha ASC;", dates)
            reports_db = cursor.fetchall()
            
        report_ids = [r[0] for r in reports_db]
        report_dates = [r[1] for r in reports_db]
        
        if report_ids:
            rep_placeholders = ",".join("%s" for _ in report_ids)
            query = f"""
                SELECT p.cedula, p.nombre, p.fecha_retiro, r.fecha as report_fecha, rp.id_reporte, sn.nombre as subnovedad
                FROM REGISTRO_PERSONAL rp
                JOIN PERSONAL p ON rp.id_personal = p.id
                JOIN REPORTES r ON rp.id_reporte = r.id
                JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                WHERE rp.id_reporte IN ({rep_placeholders})
            """
            params = list(report_ids)
            if cedula:
                query += " AND p.cedula = %s"
                params.append(cedula)
            if subnovedad:
                query += " AND sn.nombre = %s"
                params.append(subnovedad)
            query += " ORDER BY p.nombre ASC;"
            
            cursor.execute(query, params)
            
            person_map = {}
            for row in cursor.fetchall():
                key = (row[0], row[1], row[2])
                if key not in person_map:
                    person_map[key] = {}
                person_map[key][row[4]] = row[5]
                
            if cedula and is_all_months:
                person_rows = list(person_map.items())
                p_name = person_rows[0][0][1] if person_rows else ""
                f_ret = person_rows[0][0][2] if person_rows else None
                rep_dict = person_rows[0][1] if person_rows else {}

                writer.writerow([f"BIMEJ12 - MATRIZ HEATMAP ANUAL - CC {cedula} ({p_name})"])
                writer.writerow(["MES"] + [f"D{d}" for d in range(1, 32)])

                month_names_dict = {
                    '01': ('ENERO', 31), '02': ('FEBRERO', 29), '03': ('MARZO', 31),
                    '04': ('ABRIL', 30), '05': ('MAYO', 31), '06': ('JUNIO', 30),
                    '07': ('JULIO', 31), '08': ('AGOSTO', 31), '09': ('SEPTIEMBRE', 30),
                    '10': ('OCTUBRE', 31), '11': ('NOVIEMBRE', 30), '12': ('DICIEMBRE', 31)
                }
                date_to_rid = {r[1]: r[0] for r in reports_db}
                rep_year = reports_db[0][1].split('-')[0] if reports_db else str(datetime.now().year)
                active_m_nums = sorted(list(set(r[1].split('-')[1] for r in reports_db)))

                for m_num in active_m_nums:
                    m_name, max_days = month_names_dict.get(m_num, (f"MES {m_num}", 31))
                    row_data = [m_name]
                    for d in range(1, 32):
                        if d > max_days:
                            row_data.append("")
                            continue
                        dt_str = f"{rep_year}-{m_num}-{d:02d}"
                        if f_ret and dt_str >= f_ret:
                            row_data.append("R" if use_letras else "RETIRADO")
                        elif dt_str not in date_to_rid:
                            row_data.append("-")
                        else:
                            rid = date_to_rid[dt_str]
                            raw_nov = rep_dict.get(rid, "N/A")
                            if use_letras:
                                row_data.append("D" if raw_nov in DISPONIBLE_STATUSES else ("-" if raw_nov == "N/A" else "N"))
                            else:
                                row_data.append(raw_nov)
                    writer.writerow(row_data)
                filename = f"matriz_heatmap_anual_{cedula}.csv"
            else:
                if fecha:
                    headers = ["CEDULA", "INTEGRANTE", f"FECHA ({fecha})"]
                elif is_all_months:
                    headers = ["CEDULA", "INTEGRANTE"] + [f"{d.split('-')[2]}/{d.split('-')[1]}" for d in report_dates]
                else:
                    headers = ["CEDULA", "INTEGRANTE"] + [f"Día {d.split('-')[2]}" for d in report_dates]
                writer.writerow(headers)

                for (cedula_val, nombre_val, f_retiro), reports_dict in sorted(person_map.items(), key=lambda x: x[0][1]):
                    row_data = [cedula_val, nombre_val]
                    for r_id, r_fecha in reports_db:
                        is_retired = False
                        if f_retiro and r_fecha >= f_retiro:
                            is_retired = True
                            
                        if is_retired:
                            row_data.append("R" if use_letras else "RETIRADO")
                        else:
                            raw_nov = reports_dict.get(r_id, "N/A")
                            if use_letras:
                                if raw_nov in DISPONIBLE_STATUSES:
                                    cell_str = "D"
                                elif raw_nov == "N/A":
                                    cell_str = "-"
                                else:
                                    cell_str = "N"
                            else:
                                cell_str = raw_nov
                            row_data.append(cell_str)
                    writer.writerow(row_data)
                filename = f"consolidado_personal_{fecha if fecha else (mes if mes else 'TODOS')}.csv"
        
    else:
        raise HTTPException(status_code=400, detail="Parámetros inválidos para la exportación.")
        
    response = StreamingResponse(io.BytesIO(output.getvalue().encode("utf-8-sig")), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

@router.get("/excel")
def exportar_excel(
    tipo: str = Query(...),
    fecha: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    cedula: Optional[int] = Query(None),
    subnovedad: Optional[str] = Query(None),
    modo: Optional[str] = Query("letras"),
    db = Depends(get_db)
):
    print(f"\n[EXCEL REQUEST RECEIVED] tipo={tipo} | fecha={fecha} | mes={mes} | cedula={cedula} | subnovedad={subnovedad} | modo={modo}")
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Styles
    title_font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)
    normal_font = Font(name="Calibri", size=11)
    
    title_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid") # Dark gray
    header_fill = PatternFill(start_color="374151", end_color="374151", fill_type="solid") # Lighter dark gray
    
    thin_border = Border(
        left=Side(style='thin', color='D1D5DB'),
        right=Side(style='thin', color='D1D5DB'),
        top=Side(style='thin', color='D1D5DB'),
        bottom=Side(style='thin', color='D1D5DB')
    )
    
    cursor = db.cursor()
    
    if tipo == "dia":
        ws.title = "Reporte Detallado"
        
        ws.merge_cells("A1:G1")
        if fecha:
            title_text = f"BIMEJ12 — REPORTE DETALLADO DE PERSONAL — DÍA {fecha}"
        elif mes and mes.upper() != "TODOS":
            title_text = f"BIMEJ12 — REPORTE DETALLADO DE PERSONAL — MES DE {mes.upper()}"
        else:
            title_text = "BIMEJ12 — REPORTE DETALLADO DE PERSONAL — ANUAL COMPLETO"
            
        ws["A1"] = title_text
        ws["A1"].font = title_font
        ws["A1"].fill = title_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 40
        
        headers = ["CÉDULA", "APELLIDOS Y NOMBRES", "SUBNOVEDAD", "DESCRIPCIÓN", "DESDE", "HASTA", "FECHA REPORTE"]
        ws.append([])
        ws.append(headers)
        ws.row_dimensions[3].height = 25
        
        for col_idx in range(1, 8):
            cell = ws.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            
        query = """
            SELECT p.cedula, p.nombre, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final, r.fecha
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            JOIN REPORTES r ON rp.id_reporte = r.id
        """
        params = []
        where_clauses = []
        if fecha:
            where_clauses.append("r.fecha = %s")
            params.append(fecha)
        elif mes and mes.upper() != "TODOS":
            dates = get_month_dates(mes)
            if dates:
                placeholders = ",".join("%s" for _ in dates)
                where_clauses.append(f"r.fecha IN ({placeholders})")
                params.extend(dates)
            else:
                where_clauses.append("1=0")
                
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY r.fecha ASC, p.nombre ASC;"
        cursor.execute(query, params)
        for row in cursor.fetchall():
            ws.append(list(row))
            
        for r_idx in range(4, ws.max_row + 1):
            ws.row_dimensions[r_idx].height = 20
            for c_idx in range(1, 8):
                cell = ws.cell(row=r_idx, column=c_idx)
                cell.font = normal_font
                cell.border = thin_border
                if c_idx == 1:
                    cell.alignment = Alignment(horizontal="left")
                elif c_idx in (5, 6, 7):
                    cell.alignment = Alignment(horizontal="center")
                    
        filename = f"reporte_detallado_{fecha if fecha else (mes if mes else 'anual')}.xlsx"
        
    elif tipo == "mes" and mes:
        ws.title = f"Resumen {mes}"
        ws.merge_cells("A1:E1")
        ws["A1"] = f"BIMEJ12 — RESUMEN MENSUAL — {mes.upper()}"
        ws["A1"].font = title_font
        ws["A1"].fill = title_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 40
        
        headers = ["FECHA", "TOTAL PERSONAL", "DISPONIBLES", "NOVEDADES", "DISPONIBILIDAD %"]
        ws.append([])
        ws.append(headers)
        ws.row_dimensions[3].height = 25
        
        for col_idx in range(1, 6):
            cell = ws.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            
        dates = get_month_dates(mes)
        for d in dates:
            cursor.execute("SELECT id FROM REPORTES WHERE fecha = %s;", (d,))
            r_row = cursor.fetchone()
            if not r_row:
                continue
            r_id = r_row[0]
            
            cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = %s;", (r_id,))
            total = cursor.fetchone()[0]
            
            placeholders = ",".join("%s" for _ in DISPONIBLE_STATUSES)
            cursor.execute(f"""
                SELECT COUNT(*) FROM REGISTRO_PERSONAL 
                WHERE id_reporte = %s AND id_sub_novedad IN (
                    SELECT id FROM SUB_NOVEDADES WHERE nombre IN ({placeholders})
                );
            """, (r_id, *DISPONIBLE_STATUSES))
            disp = cursor.fetchone()[0]
            nov = total - disp
            pct = round((disp / total * 100), 1) if total > 0 else 0.0
            ws.append([d, total, disp, nov, pct])
            
        for r_idx in range(4, ws.max_row + 1):
            ws.row_dimensions[r_idx].height = 20
            for c_idx in range(1, 6):
                cell = ws.cell(row=r_idx, column=c_idx)
                cell.font = normal_font
                cell.border = thin_border
                if c_idx == 1:
                    cell.alignment = Alignment(horizontal="center")
                else:
                    cell.alignment = Alignment(horizontal="right")
                    
        filename = f"reporte_mensual_{mes}.xlsx"
        
    elif tipo == "personal" and cedula:
        cursor.execute("SELECT id, nombre, CASE WHEN fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END as estado FROM PERSONAL WHERE cedula = %s;", (cedula,))
        p_row = cursor.fetchone()
        nombre = p_row[1] if p_row else "Desconocido"
        estado = p_row[2] if p_row else "Desconocido"
        
        ws.title = "Historial"
        ws.merge_cells("A1:E1")
        ws["A1"] = f"HISTORIAL INDIVIDUAL: {nombre} ({cedula}) - {estado}"
        ws["A1"].font = title_font
        ws["A1"].fill = title_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 40
        
        headers = ["FECHA", "SUBNOVEDAD", "DESCRIPCIÓN", "DESDE", "HASTA"]
        ws.append([])
        ws.append(headers)
        ws.row_dimensions[3].height = 25
        
        for col_idx in range(1, 6):
            cell = ws.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            
        if p_row:
            query = """
                SELECT r.fecha, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final
                FROM REGISTRO_PERSONAL rp
                JOIN REPORTES r ON rp.id_reporte = r.id
                JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                WHERE rp.id_personal = %s
            """
            params = [p_row[0]]
            if mes and mes.upper() != "TODOS":
                dates = get_month_dates(mes)
                if dates:
                    placeholders = ",".join("%s" for _ in dates)
                    query += f" AND r.fecha IN ({placeholders})"
                    params.extend(dates)
                else:
                    query += " AND 1=0"
            if subnovedad:
                query += " AND UPPER(sn.nombre) LIKE UPPER(%s)"
                params.append(f"%{subnovedad}%")
            query += " ORDER BY r.fecha ASC;"
            cursor.execute(query, tuple(params))
            for row in cursor.fetchall():
                ws.append(list(row))
                
        for r_idx in range(4, ws.max_row + 1):
            ws.row_dimensions[r_idx].height = 20
            for c_idx in range(1, 6):
                cell = ws.cell(row=r_idx, column=c_idx)
                cell.font = normal_font
                cell.border = thin_border
                if c_idx == 1:
                    cell.alignment = Alignment(horizontal="center")
                elif c_idx in (4, 5):
                    cell.alignment = Alignment(horizontal="center")
                    
        filename = f"historial_personal_{cedula}.xlsx"
        
    elif tipo == "personal_db":
        ws.title = "Base Personal"
        ws.merge_cells("A1:D1")
        ws["A1"] = "BIMEJ12 — BASE DE DATOS DE PERSONAL"
        ws["A1"].font = title_font
        ws["A1"].fill = title_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 40
        
        headers = ["CÉDULA", "APELLIDOS Y NOMBRES", "ESTADO", "FECHA RETIRO"]
        ws.append([])
        ws.append(headers)
        ws.row_dimensions[3].height = 25
        
        for col_idx in range(1, 5):
            cell = ws.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            
        cursor.execute("""
            SELECT cedula, nombre, CASE WHEN fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END as estado, fecha_retiro
            FROM PERSONAL
            ORDER BY nombre ASC;
        """)
        for row in cursor.fetchall():
            ws.append(list(row))
            
        for r_idx in range(4, ws.max_row + 1):
            ws.row_dimensions[r_idx].height = 20
            for c_idx in range(1, 5):
                cell = ws.cell(row=r_idx, column=c_idx)
                cell.font = normal_font
                cell.border = thin_border
                if c_idx == 3:
                    cell.alignment = Alignment(horizontal="center")
                    if cell.value == "ACTIVO":
                        cell.font = Font(name="Calibri", size=11, color="10B981", bold=True)
                    else:
                        cell.font = Font(name="Calibri", size=11, color="EF4444", bold=True)
                elif c_idx == 4:
                    cell.alignment = Alignment(horizontal="center")
        filename = "base_datos_personal.xlsx"
        
    elif tipo == "subnovedades":
        ws.title = "Catálogo Novedades"
        ws.merge_cells("A1:B1")
        ws["A1"] = "BIMEJ12 — CATÁLOGO DE SUBNOVEDADES"
        ws["A1"].font = title_font
        ws["A1"].fill = title_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 40
        
        headers = ["ID", "NOMBRE NOVEDAD"]
        ws.append([])
        ws.append(headers)
        ws.row_dimensions[3].height = 25
        
        for col_idx in range(1, 3):
            cell = ws.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            
        cursor.execute("SELECT id, nombre FROM SUB_NOVEDADES ORDER BY nombre ASC;")
        for row in cursor.fetchall():
            ws.append(list(row))
            
        for r_idx in range(4, ws.max_row + 1):
            ws.row_dimensions[r_idx].height = 20
            for c_idx in range(1, 3):
                cell = ws.cell(row=r_idx, column=c_idx)
                cell.font = normal_font
                cell.border = thin_border
                if c_idx == 1:
                    cell.alignment = Alignment(horizontal="center")
        filename = "catalogo_subnovedades.xlsx"
        
    elif tipo == "consolidado_mensual":
        is_all_months = not mes or mes.upper() == "TODOS" or mes == ""
        is_colores = (modo == "colores")
        use_letras = (modo in ("letras", "colores"))
        
        if fecha:
            cursor.execute("SELECT id, fecha FROM REPORTES WHERE fecha = %s;", (fecha,))
            reports_db = cursor.fetchall()
        elif is_all_months:
            cursor.execute("SELECT fecha FROM REPORTES ORDER BY fecha ASC;")
            dates = [row[0] for row in cursor.fetchall()]
            if not dates:
                raise HTTPException(status_code=400, detail="No hay reportes registrados en el sistema.")
            placeholders = ",".join("%s" for _ in dates)
            cursor.execute(f"SELECT id, fecha FROM REPORTES WHERE fecha IN ({placeholders}) ORDER BY fecha ASC;", dates)
            reports_db = cursor.fetchall()
        else:
            dates = get_month_dates(mes)
            if not dates:
                raise HTTPException(status_code=400, detail="No hay reportes para el mes especificado.")
            placeholders = ",".join("%s" for _ in dates)
            cursor.execute(f"SELECT id, fecha FROM REPORTES WHERE fecha IN ({placeholders}) ORDER BY fecha ASC;", dates)
            reports_db = cursor.fetchall()
            
        report_ids = [r[0] for r in reports_db]
        report_dates = [r[1] for r in reports_db]

        if cedula and is_all_months:
            # Matriz Anual Individual (Mes x D01..D31)
            p_name = ""
            p_ret = None
            rep_dict = {}
            if report_ids:
                rep_placeholders = ",".join("%s" for _ in report_ids)
                query = f"""
                    SELECT p.cedula, p.nombre, p.fecha_retiro, r.fecha as report_fecha, rp.id_reporte, sn.nombre as subnovedad
                    FROM REGISTRO_PERSONAL rp
                    JOIN PERSONAL p ON rp.id_personal = p.id
                    JOIN REPORTES r ON rp.id_reporte = r.id
                    JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                    WHERE rp.id_reporte IN ({rep_placeholders}) AND p.cedula = %s
                """
                params = list(report_ids) + [cedula]
                if subnovedad:
                    query += " AND UPPER(sn.nombre) LIKE UPPER(%s)"
                    params.append(f"%{subnovedad}%")
                query += " ORDER BY r.fecha ASC;"
                cursor.execute(query, params)
                for row in cursor.fetchall():
                    p_name = row[1]
                    p_ret = row[2]
                    rep_dict[row[4]] = row[5]

            ws.title = "Matriz Heatmap Anual"
            ws.merge_cells("A1:AF1")
            ws["A1"] = f"BIMEJ12 — MATRIZ HEATMAP ANUAL COMPLETA — CC {cedula} ({p_name})"
            ws["A1"].font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
            ws["A1"].fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
            ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 36

            ws.merge_cells("A2:AF2")
            if is_colores:
                ws["A2"] = "LEYENDA:   [ D ] VERDE = DISPONIBLE   |   [ N ] ÁMBAR = NOVEDAD   |   [ R ] ROJO = RETIRADO   |   [ - ] OSCURO = SIN REGISTRO"
                ws["A2"].font = Font(name="Calibri", size=8.5, bold=True, color="38BDF8")
            else:
                ws["A2"] = "LEYENDA:   [ D ] DISPONIBLE   |   [ N ] NOVEDAD   |   [ R ] RETIRADO   |   [ - ] SIN REGISTRO"
                ws["A2"].font = Font(name="Calibri", size=8.5, bold=True, color="94A3B8")
            ws["A2"].fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
            ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[2].height = 20

            headers = ["MES"] + [f"D{d}" for d in range(1, 32)]
            ws.append([])
            ws.append(headers)
            ws.row_dimensions[4].height = 22

            ws.column_dimensions["A"].width = 16
            for d in range(1, 32):
                c_let = get_column_letter(d + 1)
                ws.column_dimensions[c_let].width = 4.8

            for c_idx in range(1, 33):
                c = ws.cell(row=4, column=c_idx)
                c.font = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
                c.fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.border = thin_border

            month_names_dict = {
                '01': ('ENERO', 31), '02': ('FEBRERO', 29), '03': ('MARZO', 31),
                '04': ('ABRIL', 30), '05': ('MAYO', 31), '06': ('JUNIO', 30),
                '07': ('JULIO', 31), '08': ('AGOSTO', 31), '09': ('SEPTIEMBRE', 30),
                '10': ('OCTUBRE', 31), '11': ('NOVIEMBRE', 30), '12': ('DICIEMBRE', 31)
            }
            date_to_rid = {r[1]: r[0] for r in reports_db}
            rep_year = reports_db[0][1].split('-')[0] if reports_db else str(datetime.now().year)
            active_m_nums = sorted(list(set(r[1].split('-')[1] for r in reports_db))) if reports_db else [f"{m:02d}" for m in range(1, 13)]

            cur_row = 5
            for m_num in active_m_nums:
                m_name, max_days = month_names_dict.get(m_num, (f"MES {m_num}", 31))
                ws.cell(row=cur_row, column=1, value=m_name)
                c_mes = ws.cell(row=cur_row, column=1)
                c_mes.font = Font(name="Calibri", size=9.5, bold=True, color="F1F5F9")
                c_mes.fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
                c_mes.alignment = Alignment(horizontal="left", vertical="center", indent=1)
                c_mes.border = thin_border
                ws.row_dimensions[cur_row].height = 22

                for d in range(1, 32):
                    c = ws.cell(row=cur_row, column=d + 1)
                    c.border = thin_border
                    c.alignment = Alignment(horizontal="center", vertical="center")

                    if d > max_days:
                        c.value = ""
                        c.fill = PatternFill(start_color="0B1329", end_color="0B1329", fill_type="solid")
                        continue

                    dt_str = f"{rep_year}-{m_num}-{d:02d}"
                    is_ret = (p_ret and dt_str >= p_ret)
                    if is_ret:
                        val = "R" if use_letras else "RETIRADO"
                    elif dt_str not in date_to_rid:
                        val = "-"
                    else:
                        rid = date_to_rid[dt_str]
                        nov = rep_dict.get(rid, "N/A")
                        if use_letras:
                            val = "D" if nov in DISPONIBLE_STATUSES else ("-" if nov == "N/A" else "N")
                        else:
                            val = nov
                    
                    c.value = val

                    if is_colores:
                        if val in ("D",) or val in DISPONIBLE_STATUSES:
                            c.fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
                            c.font = Font(name="Calibri", size=9.5, bold=True, color="FFFFFF")
                        elif val in ("N",) or (val not in ("-", "N/A", "R", "RETIRADO") and val not in DISPONIBLE_STATUSES):
                            c.fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid")
                            c.font = Font(name="Calibri", size=9.5, bold=True, color="FFFFFF")
                        elif val in ("R", "RETIRADO"):
                            c.fill = PatternFill(start_color="EF4444", end_color="EF4444", fill_type="solid")
                            c.font = Font(name="Calibri", size=9.5, bold=True, color="FFFFFF")
                        else:
                            c.fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
                            c.font = Font(name="Calibri", size=9.5, bold=False, color="64748B")
                    else:
                        if val in ("D",) or val in DISPONIBLE_STATUSES:
                            c.fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
                            c.font = Font(name="Calibri", size=9, bold=True, color="065F46")
                        elif val in ("-", "N/A"):
                            c.fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
                            c.font = Font(name="Calibri", size=9, bold=False, color="6B7280")
                        elif val in ("R", "RETIRADO"):
                            c.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
                            c.font = Font(name="Calibri", size=9, bold=True, color="DC2626")
                        else:
                            c.fill = PatternFill(start_color="FFE4E6", end_color="FFE4E6", fill_type="solid")
                            c.font = Font(name="Calibri", size=9, bold=True, color="991B1B")

                cur_row += 1

            filename = f"matriz_heatmap_anual_{cedula}.xlsx"

        else:
            ws.title = "Consolidado Completo" if is_all_months else f"Consolidado {mes if mes else ''}"
            
            num_cols = 2 + len(report_dates)
            col_letter = get_column_letter(num_cols)
            
            ws.merge_cells(f"A1:{col_letter}1")
            if cedula:
                title_text = f"BIMEJ12 — HISTORIAL DE PERSONAL (CC {cedula})"
            else:
                title_text = "BIMEJ12 — CONSOLIDADO DIARIO DE PERSONAL"
                
            if fecha:
                title_text += f" — DÍA {fecha}"
            elif not is_all_months:
                title_text += f" — {mes.upper()}"
            else:
                title_text += " — TODOS LOS MESES"
                
            ws["A1"] = title_text
            ws["A1"].font = title_font
            ws["A1"].fill = title_fill
            ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 40
            
            if fecha:
                headers = ["CÉDULA", "INTEGRANTE", f"FECHA ({fecha})"]
            elif is_all_months:
                headers = ["CÉDULA", "INTEGRANTE"] + [f"{d.split('-')[2]}/{d.split('-')[1]}" for d in report_dates]
            else:
                headers = ["CÉDULA", "INTEGRANTE"] + [f"Día {d.split('-')[2]}" for d in report_dates]
                
            ws.append([])
            ws.append(headers)
            ws.row_dimensions[3].height = 25
            
            for col_idx in range(1, num_cols + 1):
                cell = ws.cell(row=3, column=col_idx)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border
                
            if report_ids:
                rep_placeholders = ",".join("%s" for _ in report_ids)
                query = f"""
                    SELECT p.cedula, p.nombre, p.fecha_retiro, r.fecha as report_fecha, rp.id_reporte, sn.nombre as subnovedad
                    FROM REGISTRO_PERSONAL rp
                    JOIN PERSONAL p ON rp.id_personal = p.id
                    JOIN REPORTES r ON rp.id_reporte = r.id
                    JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                    WHERE rp.id_reporte IN ({rep_placeholders})
                """
                params = list(report_ids)
                if cedula:
                    query += " AND p.cedula = %s"
                    params.append(cedula)
                if subnovedad:
                    query += " AND UPPER(sn.nombre) LIKE UPPER(%s)"
                    params.append(f"%{subnovedad}%")
                query += " ORDER BY p.nombre ASC;"
                
                cursor.execute(query, params)
                
                person_map = {}
                for row in cursor.fetchall():
                    key = (row[0], row[1], row[2])
                    if key not in person_map:
                        person_map[key] = {}
                    person_map[key][row[4]] = row[5]
                    
                for (cedula_val, nombre_val, f_retiro), reports_dict in sorted(person_map.items(), key=lambda x: x[0][1]):
                    row_data = [cedula_val, nombre_val]
                    for r_id, r_fecha in reports_db:
                        is_retired = False
                        if f_retiro and r_fecha >= f_retiro:
                            is_retired = True
                            
                        if is_retired:
                            cell_str = "R" if use_letras else "RETIRADO"
                        else:
                            raw_nov = reports_dict.get(r_id, "N/A")
                            if use_letras:
                                if raw_nov in DISPONIBLE_STATUSES:
                                    cell_str = "D"
                                elif raw_nov == "N/A":
                                    cell_str = "-"
                                else:
                                    cell_str = "N"
                            else:
                                cell_str = raw_nov
                        row_data.append(cell_str)
                    ws.append(row_data)
                    
            for r_idx in range(4, ws.max_row + 1):
                ws.row_dimensions[r_idx].height = 24 if not use_letras else 20
                for c_idx in range(1, num_cols + 1):
                    cell = ws.cell(row=r_idx, column=c_idx)
                    cell.font = normal_font
                    cell.border = thin_border
                    if c_idx >= 3:
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                        val = str(cell.value)
                        if is_colores:
                            if val in DISPONIBLE_STATUSES or val == "D":
                                cell.fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
                                cell.font = Font(name="Calibri", size=9, color="FFFFFF", bold=True)
                            elif val in ("N/A", "-"):
                                cell.fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
                                cell.font = Font(name="Calibri", size=9, color="64748B")
                            elif val in ("RETIRADO", "R"):
                                cell.fill = PatternFill(start_color="EF4444", end_color="EF4444", fill_type="solid")
                                cell.font = Font(name="Calibri", size=9, color="FFFFFF", bold=True)
                            else:
                                cell.fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid")
                                cell.font = Font(name="Calibri", size=9, color="FFFFFF", bold=True)
                        else:
                            if val in DISPONIBLE_STATUSES or val == "D":
                                cell.fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
                                cell.font = Font(name="Calibri", size=9, color="065F46", bold=True)
                            elif val in ("N/A", "-"):
                                cell.fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
                                cell.font = Font(name="Calibri", size=9, color="6B7280")
                            elif val in ("RETIRADO", "R"):
                                cell.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
                                cell.font = Font(name="Calibri", size=9, color="DC2626", bold=True)
                            else:
                                cell.fill = PatternFill(start_color="FFE4E6", end_color="FFE4E6", fill_type="solid")
                                cell.font = Font(name="Calibri", size=8 if not use_letras else 9, color="991B1B", bold=True)

            if use_letras or is_colores:
                for c_idx in range(3, num_cols + 1):
                    ws.column_dimensions[get_column_letter(c_idx)].width = 4.8
                            
            filename = f"consolidado_personal_{fecha if fecha else (mes if mes else 'TODOS')}.xlsx"


        
    elif tipo == "historial_novedades":
        ws.title = "Historial Novedades"
        ws.merge_cells("A1:G1")
        ws["A1"] = "BIMEJ12 — HISTORIAL COMPLETO DE NOVEDADES"
        ws["A1"].font = title_font
        ws["A1"].fill = title_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 40
        
        headers = ["CÉDULA", "APELLIDOS Y NOMBRES", "SUBNOVEDAD", "DESCRIPCIÓN", "DESDE", "HASTA", "FECHA REPORTE"]
        ws.append([])
        ws.append(headers)
        ws.row_dimensions[3].height = 25
        
        for col_idx in range(1, 8):
            cell = ws.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            
        cursor.execute("""
            SELECT p.cedula, p.nombre, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final, r.fecha
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            JOIN REPORTES r ON rp.id_reporte = r.id
            ORDER BY r.fecha ASC, p.nombre ASC;
        """)
        for row in cursor.fetchall():
            ws.append(list(row))
            
        for r_idx in range(4, ws.max_row + 1):
            ws.row_dimensions[r_idx].height = 20
            for c_idx in range(1, 8):
                cell = ws.cell(row=r_idx, column=c_idx)
                cell.font = normal_font
                cell.border = thin_border
                if c_idx == 1:
                    cell.alignment = Alignment(horizontal="left")
                elif c_idx in (5, 6, 7):
                    cell.alignment = Alignment(horizontal="center")
        filename = "historial_completo_novedades.xlsx"
        
    elif tipo == "agil":
        is_all_months = not mes or mes.upper() == "TODOS" or mes == ""
        
        ws.title = "Exportación Ágil"
        ws.merge_cells("A1:G1")
        
        if fecha:
            title_text = f"BIMEJ12 — EXPORTACIÓN ÁGIL DE NOVEDADES — FECHA: {fecha}"
        elif not is_all_months:
            title_text = f"BIMEJ12 — EXPORTACIÓN ÁGIL DE NOVEDADES — MES DE {mes.upper()}"
        else:
            title_text = "BIMEJ12 — EXPORTACIÓN ÁGIL ANUAL DE NOVEDADES (TODOS LOS MESES)"
            
        if cedula:
            title_text += f" (CC {cedula})"
            
        ws["A1"] = title_text
        ws["A1"].font = title_font
        ws["A1"].fill = title_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 40

        ws.merge_cells("A2:G2")
        ws["A2"] = f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Consolidado Exclusivo de Novedades (Excluye Disponibilidad)"
        ws["A2"].font = Font(name="Calibri", size=9, italic=True, color="64748B")
        ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 20

        placeholders_disp = ",".join("%s" for _ in DISPONIBLE_STATUSES)
        query = f"""
            SELECT p.cedula, p.nombre, r.fecha, sn.nombre as subnovedad, rp.descripcion
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN REPORTES r ON rp.id_reporte = r.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            WHERE sn.nombre NOT IN ({placeholders_disp})
        """
        params = list(DISPONIBLE_STATUSES)
        
        if cedula:
            query += " AND p.cedula = %s"
            params.append(cedula)
        if subnovedad:
            query += " AND UPPER(sn.nombre) LIKE UPPER(%s)"
            params.append(f"%{subnovedad}%")
        if fecha:
            query += " AND r.fecha = %s"
            params.append(fecha)
        elif not is_all_months:
            dates = get_month_dates(mes)
            if dates:
                pl = ",".join("%s" for _ in dates)
                query += f" AND r.fecha IN ({pl})"
                params.extend(dates)
                
        query += " ORDER BY p.nombre ASC, r.fecha ASC;"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        if fecha:
            headers = ["CÉDULA", "INTEGRANTE", "NOVEDAD", "DESCRIPCIÓN", "FECHA"]
            ws.append([])
            ws.append(headers)
            ws.row_dimensions[4].height = 25
            for col_idx in range(1, 6):
                cell = ws.cell(row=4, column=col_idx)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border
            for row in rows:
                ws.append([row[0], row[1], row[3], row[4] or "-", row[2]])
            for r_idx in range(5, ws.max_row + 1):
                ws.row_dimensions[r_idx].height = 20
                for c_idx in range(1, 6):
                    cell = ws.cell(row=r_idx, column=c_idx)
                    cell.font = normal_font
                    cell.border = thin_border
                    if c_idx in (1, 5):
                        cell.alignment = Alignment(horizontal="center")
            filename = f"exportacion_agil_{fecha}.xlsx"

        elif not is_all_months:
            headers = ["CÉDULA", "INTEGRANTE", f"RESUMEN DE NOVEDADES - {mes.upper()}"]
            ws.append([])
            ws.append(headers)
            ws.row_dimensions[4].height = 25
            for col_idx in range(1, 4):
                cell = ws.cell(row=4, column=col_idx)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border
                
            from collections import defaultdict
            person_novs = defaultdict(list)
            for r in rows:
                c_num, p_name, r_date, subnov, desc = r
                day_num = int(r_date.split('-')[2])
                person_novs[(c_num, p_name)].append((day_num, subnov, desc))
                
            for (c_num, p_name), recs in sorted(person_novs.items(), key=lambda x: x[0][1]):
                summary_str = format_agil_month_ranges(recs)
                ws.append([c_num, p_name, summary_str])
                current_r = ws.max_row
                
                obs = [f"• Día {d:02d} ({sn}): {desc.strip()}" for d, sn, desc in recs if desc and str(desc).strip()]
                if obs:
                    ws.cell(row=current_r, column=3).comment = Comment("DESCRIPCIÓN DE NOVEDADES:\n" + "\n".join(obs), "BIMEJ12")
                
            for r_idx in range(5, ws.max_row + 1):
                cell_val = ws.cell(row=r_idx, column=3).value or ""
                num_lines = str(cell_val).count('\n') + 1
                ws.row_dimensions[r_idx].height = max(22, num_lines * 18)
                for c_idx in range(1, 4):
                    cell = ws.cell(row=r_idx, column=c_idx)
                    cell.font = normal_font
                    cell.border = thin_border
                    if c_idx == 1:
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                    elif c_idx == 2:
                        cell.alignment = Alignment(horizontal="left", vertical="center")
                    elif c_idx == 3:
                        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            filename = f"exportacion_agil_{mes}.xlsx"

        else:
            active_m_codes = set(r[2].split('-')[1] for r in rows)
            if not active_m_codes:
                cursor.execute("SELECT DISTINCT to_char(to_date(fecha, 'YYYY-MM-DD'), 'MM') FROM REPORTES;")
                active_m_codes = set(row[0] for row in cursor.fetchall())
                
            all_month_tuples = [
                ('01', 'ENERO'), ('02', 'FEBRERO'), ('03', 'MARZO'), ('04', 'ABRIL'),
                ('05', 'MAYO'), ('06', 'JUNIO'), ('07', 'JULIO'), ('08', 'AGOSTO'),
                ('09', 'SEPTIEMBRE'), ('10', 'OCTUBRE'), ('11', 'NOVIEMBRE'), ('12', 'DICIEMBRE')
            ]
            month_names_dict = [m for m in all_month_tuples if m[0] in active_m_codes]
            headers = ["CÉDULA", "INTEGRANTE"] + [m_name for _, m_name in month_names_dict]
            ws.append([])
            ws.append(headers)
            ws.row_dimensions[4].height = 25

            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=4, column=col_idx)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = thin_border
                
            from collections import defaultdict
            person_months = defaultdict(lambda: defaultdict(list))
            for r in rows:
                c_num, p_name, r_date, subnov, desc = r
                m_code = r_date.split('-')[1]
                day_num = int(r_date.split('-')[2])
                person_months[(c_num, p_name)][m_code].append((day_num, subnov, desc))
                
            for (c_num, p_name), m_dict in sorted(person_months.items(), key=lambda x: x[0][1]):
                row_data = [c_num, p_name]
                month_comments = {}
                for idx, (m_code, _) in enumerate(month_names_dict):
                    recs = m_dict.get(m_code, [])
                    row_data.append(format_agil_month_ranges(recs))
                    
                    obs = [f"• Día {d:02d} ({sn}): {desc.strip()}" for d, sn, desc in recs if desc and str(desc).strip()]
                    if obs:
                        col_number = 3 + idx
                        month_comments[col_number] = "DESCRIPCIÓN DE NOVEDADES:\n" + "\n".join(obs)
                        
                ws.append(row_data)
                current_r = ws.max_row
                for col_num, comment_txt in month_comments.items():
                    ws.cell(row=current_r, column=col_num).comment = Comment(comment_txt, "BIMEJ12")

            for r_idx in range(5, ws.max_row + 1):
                max_lines = 1
                for c_idx in range(3, len(headers) + 1):
                    val = str(ws.cell(row=r_idx, column=c_idx).value or "")
                    max_lines = max(max_lines, val.count('\n') + 1)
                ws.row_dimensions[r_idx].height = max(22, max_lines * 18)
                
                for c_idx in range(1, len(headers) + 1):
                    cell = ws.cell(row=r_idx, column=c_idx)
                    cell.font = normal_font
                    cell.border = thin_border
                    if c_idx == 1:
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                    elif c_idx == 2:
                        cell.alignment = Alignment(horizontal="left", vertical="center")
                    else:
                        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            filename = f"exportacion_agil_anual_{cedula if cedula else 'todos'}.xlsx"


        
    else:
        raise HTTPException(status_code=400, detail="Parámetros inválidos")
        
    # Auto-adjust column widths
    if tipo == "consolidado_mensual":
        if not (cedula and (not mes or mes.upper() == "TODOS" or mes == "")):
            ws.column_dimensions['A'].width = 12
            ws.column_dimensions['B'].width = 28
            for col_idx in range(3, num_cols + 1):
                col_letter = get_column_letter(col_idx)
                ws.column_dimensions[col_letter].width = 8
    else:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row == 1:
                    continue
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        
    out_file = io.BytesIO()
    wb.save(out_file)
    out_file.seek(0)
    
    response = StreamingResponse(out_file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

@router.get("/pdf")
def exportar_pdf(
    tipo: str = Query(...),
    fecha: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    cedula: Optional[int] = Query(None),
    subnovedad: Optional[str] = Query(None),
    modo: Optional[str] = Query("letras"),
    db = Depends(get_db)
):
    print(f"\n==========================================")
    print(f"[PDF REQUEST RECEIVED] tipo={tipo} | fecha={fecha} | mes={mes} | cedula={cedula} | subnovedad={subnovedad} | modo={modo}")
    print(f"==========================================")

    pdf_buffer = io.BytesIO()
    uid = id(pdf_buffer)
    
    # Select document layout based on export type
    doc_layout = landscape(letter) if tipo in ("dia", "mes", "consolidado_mensual") else letter
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=doc_layout,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles (Unique name per request to avoid ReportLab duplicate style KeyError)
    title_style = ParagraphStyle(
        f'DocTitle_{uid}',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        f'DocSubtitle_{uid}',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#475569'),
        alignment=1, # Center
        spaceAfter=20
    )
    
    th_style = ParagraphStyle(
        f'TableHeader_{uid}',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white,
        alignment=1 # Center
    )
    
    td_style = ParagraphStyle(
        f'TableCell_{uid}',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#1E293B'),
        alignment=0 # Left
    )
    
    story = []
    cursor = db.cursor()
    
    if tipo == "dia":
        if fecha:
            story.append(Paragraph(f"BIMEJ12 — REPORTE DETALLADO DE PERSONAL — DÍA {fecha}", title_style))
            story.append(Paragraph(f"Fecha del Reporte: {fecha} | Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        elif mes and mes.upper() != "TODOS":
            story.append(Paragraph(f"BIMEJ12 — REPORTE DETALLADO DE PERSONAL — MES DE {mes.upper()}", title_style))
            story.append(Paragraph(f"Mes: {mes.upper()} | Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        else:
            story.append(Paragraph(f"BIMEJ12 — REPORTE DETALLADO DE PERSONAL — ANUAL COMPLETO", title_style))
            story.append(Paragraph(f"Historial General Completo | Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
            
        headers = [
            Paragraph("CÉDULA", th_style),
            Paragraph("APELLIDOS Y NOMBRES", th_style),
            Paragraph("SUBNOVEDAD", th_style),
            Paragraph("DESCRIPCIÓN", th_style),
            Paragraph("DESDE", th_style),
            Paragraph("HASTA", th_style),
            Paragraph("FECHA", th_style)
        ]
        
        data = [headers]
        
        query = """
            SELECT p.cedula, p.nombre, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final, r.fecha
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            JOIN REPORTES r ON rp.id_reporte = r.id
        """
        params = []
        where_clauses = []
        if fecha:
            where_clauses.append("r.fecha = %s")
            params.append(fecha)
        elif mes and mes.upper() != "TODOS":
            dates = get_month_dates(mes)
            if dates:
                placeholders = ",".join("%s" for _ in dates)
                where_clauses.append(f"r.fecha IN ({placeholders})")
                params.extend(dates)
            else:
                where_clauses.append("1=0")
                
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY r.fecha ASC, p.nombre ASC;"
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            data.append([
                Paragraph(str(row[0]), td_style),
                Paragraph(row[1], td_style),
                Paragraph(row[2], td_style),
                Paragraph(row[3] or "", td_style),
                Paragraph(row[4] or "-", td_style),
                Paragraph(row[5] or "-", td_style),
                Paragraph(row[6], td_style)
            ])
            
        col_widths = [65, 160, 105, 175, 70, 70, 75]
        
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(t)
        filename = f"reporte_detallado_{fecha if fecha else (mes if mes else 'anual')}.pdf"
        
    elif tipo == "mes" and mes:
        story.append(Paragraph(f"BIMEJ12 — RESUMEN MENSUAL DE DISPONIBILIDAD", title_style))
        story.append(Paragraph(f"Mes: {mes.upper()} | Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        
        headers = [
            Paragraph("FECHA", th_style),
            Paragraph("TOTAL PERSONAL", th_style),
            Paragraph("DISPONIBLES", th_style),
            Paragraph("EN NOVEDADES", th_style),
            Paragraph("DISPONIBILIDAD %", th_style)
        ]
        
        data = [headers]
        
        dates = get_month_dates(mes)
        for d in dates:
            cursor.execute("SELECT id FROM REPORTES WHERE fecha = %s;", (d,))
            r_row = cursor.fetchone()
            if not r_row:
                continue
            r_id = r_row[0]
            
            cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = %s;", (r_id,))
            total = cursor.fetchone()[0]
            
            placeholders = ",".join("%s" for _ in DISPONIBLE_STATUSES)
            cursor.execute(f"""
                SELECT COUNT(*) FROM REGISTRO_PERSONAL 
                WHERE id_reporte = %s AND id_sub_novedad IN (
                    SELECT id FROM SUB_NOVEDADES WHERE nombre IN ({placeholders})
                );
            """, (r_id, *DISPONIBLE_STATUSES))
            disp = cursor.fetchone()[0]
            nov = total - disp
            pct = round((disp / total * 100), 1) if total > 0 else 0.0
            
            data.append([
                Paragraph(d, td_style),
                Paragraph(str(total), td_style),
                Paragraph(str(disp), td_style),
                Paragraph(str(nov), td_style),
                Paragraph(f"{pct}%", td_style)
            ])
            
        col_widths = [144, 144, 144, 144, 144] # 720 total
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(t)
        filename = f"reporte_mensual_{mes}.pdf"

    elif tipo == "personal" and cedula:
        cursor.execute("SELECT id, nombre, CASE WHEN fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END as estado, fecha_retiro FROM PERSONAL WHERE cedula = %s;", (cedula,))
        p_row = cursor.fetchone()
        if not p_row:
            raise HTTPException(status_code=404, detail="Personal no encontrado")
            
        p_id, nombre, estado, fecha_retiro = p_row[0], p_row[1], p_row[2], p_row[3]
        
        story.append(Paragraph(f"HISTORIAL DE PERSONAL INDIVIDUAL", title_style))
        story.append(Paragraph(f"Integrante: {nombre} | Cédula: {cedula} | Estado: {estado} " + (f"| Fecha Retiro: {fecha_retiro}" if fecha_retiro else ""), subtitle_style))
        
        cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_personal = %s;", (p_id,))
        total_dias = cursor.fetchone()[0]
        
        placeholders = ",".join("%s" for _ in DISPONIBLE_STATUSES)
        cursor.execute(f"""
            SELECT COUNT(*) FROM REGISTRO_PERSONAL 
            WHERE id_personal = %s AND id_sub_novedad IN (
                SELECT id FROM SUB_NOVEDADES WHERE nombre IN ({placeholders})
            );
        """, (p_id, *DISPONIBLE_STATUSES))
        disp_dias = cursor.fetchone()[0]
        nov_dias = total_dias - disp_dias
        disp_pct = round((disp_dias / total_dias * 100), 1) if total_dias > 0 else 0.0
        
        stats_data = [
            [Paragraph("<b>Total Días Registrados:</b>", td_style), Paragraph(str(total_dias), td_style),
             Paragraph("<b>Días Disponibles:</b>", td_style), Paragraph(f"{disp_dias} ({disp_pct}%)", td_style)],
            [Paragraph("<b>Días en Novedades:</b>", td_style), Paragraph(f"{nov_dias} ({round(100.0 - disp_pct, 1)}%)", td_style),
             Paragraph("<b>Estado Actual:</b>", td_style), Paragraph(estado, td_style)]
        ]
        stats_table = Table(stats_data, colWidths=[135, 135, 135, 135])
        stats_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 15))
        
        headers = [
            Paragraph("FECHA", th_style),
            Paragraph("SUBNOVEDAD", th_style),
            Paragraph("DESCRIPCIÓN", th_style),
            Paragraph("DESDE", th_style),
            Paragraph("HASTA", th_style)
        ]
        
        data = [headers]
        
        query = """
            SELECT r.fecha, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final
            FROM REGISTRO_PERSONAL rp
            JOIN REPORTES r ON rp.id_reporte = r.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            WHERE rp.id_personal = %s
        """
        params = [p_id]
        if mes and mes.upper() != "TODOS":
            dates = get_month_dates(mes)
            if dates:
                placeholders = ",".join("%s" for _ in dates)
                query += f" AND r.fecha IN ({placeholders})"
                params.extend(dates)
            else:
                query += " AND 1=0"
        if subnovedad:
            query += " AND UPPER(sn.nombre) LIKE UPPER(%s)"
            params.append(f"%{subnovedad}%")
        query += " ORDER BY r.fecha ASC;"
        cursor.execute(query, tuple(params))
        
        for row in cursor.fetchall():
            data.append([
                Paragraph(row[0], td_style),
                Paragraph(row[1], td_style),
                Paragraph(row[2] or "", td_style),
                Paragraph(row[3] or "-", td_style),
                Paragraph(row[4] or "-", td_style)
            ])
            
        col_widths = [75, 110, 195, 80, 80]
        
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(t)
        filename = f"historial_personal_{cedula}.pdf"
        
    elif tipo == "personal_db":
        doc_layout = letter
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=doc_layout,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        story.append(Paragraph("BIMEJ12 — BASE DE DATOS GENERAL DE PERSONAL", title_style))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        
        headers = [
            Paragraph("CÉDULA", th_style),
            Paragraph("APELLIDOS Y NOMBRES", th_style),
            Paragraph("ESTADO", th_style),
            Paragraph("FECHA RETIRO", th_style)
        ]
        data = [headers]
        
        cursor.execute("""
            SELECT cedula, nombre, CASE WHEN fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END as estado, fecha_retiro
            FROM PERSONAL
            ORDER BY nombre ASC;
        """)
        
        active_style = ParagraphStyle('ActCell', parent=td_style, textColor=colors.HexColor('#10B981'), fontName='Helvetica-Bold')
        ret_style = ParagraphStyle('RetCell', parent=td_style, textColor=colors.HexColor('#EF4444'), fontName='Helvetica-Bold')
        
        for row in cursor.fetchall():
            est_text = row[2]
            est_p = Paragraph(est_text, active_style) if est_text == "ACTIVO" else Paragraph(est_text, ret_style)
            data.append([
                Paragraph(str(row[0]), td_style),
                Paragraph(row[1], td_style),
                est_p,
                Paragraph(row[3] or "-", td_style)
            ])
            
        col_widths = [90, 230, 110, 110]
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(t)
        filename = "base_datos_personal.pdf"

    elif tipo == "subnovedades":
        doc_layout = letter
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=doc_layout,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        story.append(Paragraph("BIMEJ12 — CATÁLOGO DE SUBNOVEDADES", title_style))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        
        headers = [
            Paragraph("ID", th_style),
            Paragraph("NOMBRE DE LA SUBNOVEDAD", th_style)
        ]
        data = [headers]
        
        cursor.execute("SELECT id, nombre FROM SUB_NOVEDADES ORDER BY nombre ASC;")
        for row in cursor.fetchall():
            data.append([
                Paragraph(str(row[0]), td_style),
                Paragraph(row[1], td_style)
            ])
            
        col_widths = [100, 404]
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(t)
        filename = "catalogo_subnovedades.pdf"
        
    elif tipo == "consolidado_mensual":
        is_all_months = not mes or mes.upper() == "TODOS" or mes == ""
        is_colores = (modo == "colores")
        use_letras = (modo in ("letras", "colores"))
        
        doc_layout = landscape(letter)
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=doc_layout,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        if fecha:
            pdf_title = f"BIMEJ12 — CONSOLIDADO DIARIO DE PERSONAL — DÍA {fecha}"
            story.append(Paragraph(pdf_title, title_style))
            story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
            cursor.execute("SELECT id, fecha FROM REPORTES WHERE fecha = %s;", (fecha,))
            reports_db = cursor.fetchall()
        elif is_all_months:
            cursor.execute("SELECT id, fecha FROM REPORTES ORDER BY fecha ASC;")
            reports_db = cursor.fetchall()
            if not cedula:
                pdf_title = "BIMEJ12 — CONSOLIDADO DIARIO DE PERSONAL — TODOS LOS MESES"
                story.append(Paragraph(pdf_title, title_style))
                if is_colores:
                    story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | <font color='#10B981'><b>■ [D] Verde = Disponible</b></font> &nbsp;|&nbsp; <font color='#F59E0B'><b>■ [N] Ámbar = Novedad</b></font> &nbsp;|&nbsp; <font color='#EF4444'><b>■ [R] Rojo = Retirado</b></font> &nbsp;|&nbsp; <font color='#64748B'><b>■ [-] Oscuro = Sin Registro</b></font>", subtitle_style))
                else:
                    story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | D = Disponible, N = Novedad, R = Retirado, - = Sin Registro", subtitle_style))
        else:
            pdf_title = f"BIMEJ12 — CONSOLIDADO DIARIO DE PERSONAL — {mes.upper()}"
            story.append(Paragraph(pdf_title, title_style))
            if is_colores:
                legend_txt = "<font color='#10B981'><b>■ [D] Verde = Disponible</b></font> &nbsp;|&nbsp; <font color='#F59E0B'><b>■ [N] Ámbar = Novedad</b></font> &nbsp;|&nbsp; <font color='#EF4444'><b>■ [R] Rojo = Retirado</b></font> &nbsp;|&nbsp; <font color='#64748B'><b>■ [-] Oscuro = Sin Registro</b></font>"
            else:
                legend_txt = "D = Disponible, N = Novedad, R = Retirado, - = Sin Registro" if use_letras else "Detalle Completo de Novedades"
            story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | {legend_txt}", subtitle_style))
            
            dates = get_month_dates(mes)
            if not dates:
                raise HTTPException(status_code=400, detail="No hay reportes para el mes especificado.")
            placeholders = ",".join("%s" for _ in dates)
            cursor.execute(f"SELECT id, fecha FROM REPORTES WHERE fecha IN ({placeholders}) ORDER BY fecha ASC;", dates)
            reports_db = cursor.fetchall()

        report_ids = [r[0] for r in reports_db]
        
        # Styles for cells (Unique names per request)
        p_disp_style = ParagraphStyle(f'PDispG_{uid}', parent=td_style, fontSize=5 if not use_letras else 4.5, leading=6, textColor=colors.HexColor('#065F46'), fontName='Helvetica-Bold', alignment=1)
        p_nov_style = ParagraphStyle(f'PNovG_{uid}', parent=td_style, fontSize=5 if not use_letras else 4.5, leading=6, textColor=colors.HexColor('#92400E'), fontName='Helvetica-Bold', alignment=1)
        p_na_style = ParagraphStyle(f'PNAG_{uid}', parent=td_style, fontSize=5, leading=6, textColor=colors.HexColor('#9CA3AF'), alignment=1)
        p_ret_style = ParagraphStyle(f'PRetG_{uid}', parent=td_style, fontSize=4.5, leading=6, textColor=colors.HexColor('#7F1D1D'), fontName='Helvetica-Bold', alignment=1)

        p_white_bold = ParagraphStyle(f'PWhiteB_{uid}', parent=td_style, fontSize=6 if is_all_months and cedula else 4.5, leading=7, textColor=colors.white, fontName='Helvetica-Bold', alignment=1)
        p_slate_muted = ParagraphStyle(f'PSlateM_{uid}', parent=td_style, fontSize=6 if is_all_months and cedula else 4.5, leading=7, textColor=colors.HexColor('#94A3B8'), alignment=1)
        p_month_style = ParagraphStyle(f'PMonthB_{uid}', parent=td_style, fontSize=6.5, leading=8, textColor=colors.white, fontName='Helvetica-Bold', alignment=0)
        month_title_style = ParagraphStyle(f'MonthTitle_{uid}', parent=subtitle_style, fontSize=11, leading=14, textColor=colors.HexColor('#06B6D4'), fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=5)

        if report_ids:
            rep_placeholders = ",".join("%s" for _ in report_ids)
            query = f"""
                SELECT p.cedula, p.nombre, p.fecha_retiro, r.fecha as report_fecha, rp.id_reporte, sn.nombre as subnovedad
                FROM REGISTRO_PERSONAL rp
                JOIN PERSONAL p ON rp.id_personal = p.id
                JOIN REPORTES r ON rp.id_reporte = r.id
                JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                WHERE rp.id_reporte IN ({rep_placeholders})
            """
            params = list(report_ids)
            if cedula:
                query += " AND p.cedula = %s"
                params.append(cedula)
            if subnovedad:
                query += " AND UPPER(sn.nombre) LIKE UPPER(%s)"
                params.append(f"%{subnovedad}%")
            query += " ORDER BY p.nombre ASC;"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            person_map = {}
            for row in rows:
                key = (row[0], row[1], row[2])
                if key not in person_map:
                    person_map[key] = {}
                person_map[key][row[4]] = row[5]

            month_names_dict = {
                '01': ('ENERO', 31), '02': ('FEBRERO', 29), '03': ('MARZO', 31), '04': ('ABRIL', 30),
                '05': ('MAYO', 31), '06': ('JUNIO', 30), '07': ('JULIO', 31), '08': ('AGOSTO', 31),
                '09': ('SEPTIEMBRE', 30), '10': ('OCTUBRE', 31), '11': ('NOVIEMBRE', 30), '12': ('DICIEMBRE', 31)
            }

            if cedula and is_all_months:
                # PDF: Matriz Heatmap Anual para Personal Individual (Mes x D01..D31)
                person_rows = list(person_map.items())
                p_name = person_rows[0][0][1] if person_rows else ""
                f_ret = person_rows[0][0][2] if person_rows else None
                rep_dict = person_rows[0][1] if person_rows else {}
                rep_year = reports_db[0][1].split('-')[0] if reports_db else str(datetime.now().year)

                story.append(Paragraph("BIMEJ12 — MATRIZ HEATMAP ANUAL COMPLETA", title_style))
                story.append(Paragraph(f"<b>Cédula:</b> {cedula} &nbsp;|&nbsp; <b>Integrante:</b> {p_name} &nbsp;|&nbsp; <b>Año:</b> {rep_year} &nbsp;|&nbsp; Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
                if is_colores:
                    story.append(Paragraph("<font color='#10B981'><b>■ [D] Verde = Disponible</b></font> &nbsp;&nbsp;|&nbsp;&nbsp; <font color='#F59E0B'><b>■ [N] Ámbar = Novedad</b></font> &nbsp;&nbsp;|&nbsp;&nbsp; <font color='#EF4444'><b>■ [R] Rojo = Retirado</b></font> &nbsp;&nbsp;|&nbsp;&nbsp; <font color='#64748B'><b>■ [-] Oscuro = Sin Registro</b></font>", subtitle_style))
                else:
                    story.append(Paragraph("D = Disponible, N = Novedad, R = Retirado, - = Sin Registro", subtitle_style))
                story.append(Spacer(1, 10))

                headers = [Paragraph("MES", th_style)] + [Paragraph(f"D{d}", th_style) for d in range(1, 32)]
                data = [headers]
                table_styles = [
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
                    ('BACKGROUND', (0,1), (0,-1), colors.HexColor('#0F172A')),
                    ('ALIGN', (0,0), (0,-1), 'LEFT'),
                    ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#334155')),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ('LEFTPADDING', (0,0), (-1,-1), 1),
                    ('RIGHTPADDING', (0,0), (-1,-1), 1),
                ]

                date_to_rid = {r[1]: r[0] for r in reports_db}
                active_m_nums = sorted(list(set(r[1].split('-')[1] for r in reports_db))) if reports_db else [f"{m:02d}" for m in range(1, 13)]

                r_idx = 1
                for m_num in active_m_nums:
                    m_name, max_days = month_names_dict.get(m_num, (f"MES {m_num}", 31))
                    row_data = [Paragraph(m_name, p_month_style)]
                    for d in range(1, 32):
                        c_idx = d
                        if d > max_days:
                            row_data.append(Paragraph("", td_style))
                            table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#0B1329')))
                            continue

                        dt_str = f"{rep_year}-{m_num}-{d:02d}"
                        is_ret = (f_ret and dt_str >= f_ret)
                        if is_ret:
                            val = "R" if use_letras else "RETIRADO"
                        elif dt_str not in date_to_rid:
                            val = "-"
                        else:
                            rid = date_to_rid[dt_str]
                            nov = rep_dict.get(rid, "N/A")
                            if use_letras:
                                val = "D" if nov in DISPONIBLE_STATUSES else ("-" if nov == "N/A" else "N")
                            else:
                                val = nov

                        if is_colores:
                            if val in ("D",) or val in DISPONIBLE_STATUSES:
                                row_data.append(Paragraph("D", p_white_bold))
                                table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#10B981')))
                            elif val in ("N",) or (val not in ("-", "N/A", "R", "RETIRADO") and val not in DISPONIBLE_STATUSES):
                                row_data.append(Paragraph("N", p_white_bold))
                                table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#F59E0B')))
                            elif val in ("R", "RETIRADO"):
                                row_data.append(Paragraph("R", p_white_bold))
                                table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#EF4444')))
                            else:
                                row_data.append(Paragraph("-", p_slate_muted))
                                table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#1E293B')))
                        else:
                            if val in ("D",) or val in DISPONIBLE_STATUSES:
                                row_data.append(Paragraph("D", p_disp_style))
                                table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#D1FAE5')))
                            elif val in ("N",) or (val not in ("-", "N/A", "R", "RETIRADO") and val not in DISPONIBLE_STATUSES):
                                row_data.append(Paragraph("N", p_nov_style))
                                table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#FFE4E6')))
                            elif val in ("R", "RETIRADO"):
                                row_data.append(Paragraph("R", p_ret_style))
                                table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#FEE2E2')))
                            else:
                                row_data.append(Paragraph("-", p_na_style))
                                table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#F3F4F6')))

                    data.append(row_data)
                    r_idx += 1

                col_widths = [60] + [21 for _ in range(31)]
                t = Table(data, colWidths=col_widths, repeatRows=1)
                t.setStyle(TableStyle(table_styles))
                story.append(t)
                story.append(Spacer(1, 10))
                filename = f"matriz_heatmap_anual_{cedula}.pdf"

            else:
                from collections import defaultdict
                months_grouped = defaultdict(list)
                for r in reports_db:
                    m_num = r[1].split('-')[1]
                    months_grouped[m_num].append(r)

                for m_num, m_reports in sorted(months_grouped.items()):
                    m_name = month_names_dict.get(m_num, (f"MES {m_num}", 31))[0]
                    if is_all_months and not fecha:
                        story.append(Paragraph(f"MES DE {m_name}", month_title_style))
                    
                    m_dates = [r[1] for r in m_reports]
                    headers = [
                        Paragraph("CÉDULA", th_style),
                        Paragraph("INTEGRANTE", th_style)
                    ] + [Paragraph(d.split('-')[2], th_style) for d in m_dates]
                    
                    data = [headers]
                    table_styles = [
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A' if is_colores else '#1E293B')),
                        ('ALIGN', (0,0), (1,-1), 'LEFT'),
                        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#334155' if is_colores else '#CBD5E1')),
                        ('TOPPADDING', (0,0), (-1,-1), 1.5 if not use_letras else 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5 if not use_letras else 2),
                        ('LEFTPADDING', (0,0), (-1,-1), 1),
                        ('RIGHTPADDING', (0,0), (-1,-1), 1),
                    ]
                    if not is_colores:
                        table_styles.append(('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]))

                    r_idx = 1
                    for (c_num, name, f_retiro), reports_dict in sorted(person_map.items(), key=lambda x: x[0][1]):
                        row_data = [
                            Paragraph(str(c_num), td_style),
                            Paragraph(name, td_style)
                        ]
                        for d_idx, (r_id, r_fecha) in enumerate(m_reports):
                            c_idx = 2 + d_idx
                            is_retired = False
                            if f_retiro and r_fecha >= f_retiro:
                                is_retired = True
                                
                            if is_retired:
                                if is_colores:
                                    row_data.append(Paragraph("R", p_white_bold))
                                    table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#EF4444')))
                                else:
                                    row_data.append(Paragraph("R" if use_letras else "RETIRADO", p_ret_style))
                            else:
                                raw_nov = reports_dict.get(r_id, "N/A")
                                if use_letras:
                                    if raw_nov in DISPONIBLE_STATUSES:
                                        if is_colores:
                                            row_data.append(Paragraph("D", p_white_bold))
                                            table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#10B981')))
                                        else:
                                            row_data.append(Paragraph("D", p_disp_style))
                                    elif raw_nov == "N/A":
                                        if is_colores:
                                            row_data.append(Paragraph("-", p_slate_muted))
                                            table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#1E293B')))
                                        else:
                                            row_data.append(Paragraph("-", p_na_style))
                                    else:
                                        if is_colores:
                                            row_data.append(Paragraph("N", p_white_bold))
                                            table_styles.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor('#F59E0B')))
                                        else:
                                            row_data.append(Paragraph("N", p_nov_style))
                                else:
                                    if raw_nov in DISPONIBLE_STATUSES:
                                        row_data.append(Paragraph(raw_nov, p_disp_style))
                                    elif raw_nov == "N/A":
                                        row_data.append(Paragraph("-", p_na_style))
                                    else:
                                        row_data.append(Paragraph(raw_nov, p_nov_style))
                        data.append(row_data)
                        r_idx += 1
                        
                    num_days_col = len(m_dates)
                    cedula_width = 45
                    min_name_width = 110
                    avail_days_width = 720 - cedula_width - min_name_width
                    day_col_width = min(max(int(avail_days_width / max(num_days_col, 1)), 12), 120)
                    total_days_width = day_col_width * num_days_col
                    name_width = 720 - cedula_width - total_days_width
                    col_widths = [cedula_width, name_width] + [day_col_width for _ in m_dates]
                    
                    t = Table(data, colWidths=col_widths, repeatRows=1)
                    t.setStyle(TableStyle(table_styles))
                    story.append(t)
                    story.append(Spacer(1, 10))
                    
                filename = f"consolidado_personal_{fecha if fecha else (mes if mes else 'TODOS')}.pdf"



        
    elif tipo == "historial_novedades":
        story.append(Paragraph("BIMEJ12 — HISTORIAL COMPLETO DE NOVEDADES", title_style))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        
        headers = [
            Paragraph("CÉDULA", th_style),
            Paragraph("APELLIDOS Y NOMBRES", th_style),
            Paragraph("SUBNOVEDAD", th_style),
            Paragraph("DESCRIPCIÓN", th_style),
            Paragraph("DESDE", th_style),
            Paragraph("HASTA", th_style),
            Paragraph("REPORTE", th_style)
        ]
        
        data = [headers]
        
        cursor.execute("""
            SELECT p.cedula, p.nombre, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final, r.fecha
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            JOIN REPORTES r ON rp.id_reporte = r.id
            ORDER BY r.fecha ASC, p.nombre ASC;
        """)
        
        for row in cursor.fetchall():
            data.append([
                Paragraph(str(row[0]), td_style),
                Paragraph(row[1], td_style),
                Paragraph(row[2], td_style),
                Paragraph(row[3] or "", td_style),
                Paragraph(row[4] or "-", td_style),
                Paragraph(row[5] or "-", td_style),
                Paragraph(row[6], td_style)
            ])
            
        col_widths = [70, 150, 100, 160, 80, 80, 80]
        
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        filename = "historial_completo_novedades.pdf"
        
    elif tipo == "agil":
        is_all_months = not mes or mes.upper() == "TODOS" or mes == ""
        
        doc_layout = landscape(letter)
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=doc_layout,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        pdf_title = "BIMEJ12 — EXPORTACIÓN ÁGIL DE NOVEDADES"
        if fecha:
            pdf_title += f" — FECHA: {fecha}"
        elif not is_all_months:
            pdf_title += f" — MES DE {mes.upper()}"
        else:
            pdf_title += " — TODOS LOS MESES (ANUAL)"
            
        if cedula:
            pdf_title += f" (CC {cedula})"
            
        story.append(Paragraph(pdf_title, title_style))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Consolidado Exclusivo de Novedades (Excluye Disponibilidad)", subtitle_style))
        story.append(Spacer(1, 10))

        placeholders_disp = ",".join("%s" for _ in DISPONIBLE_STATUSES)
        query = f"""
            SELECT p.cedula, p.nombre, r.fecha, sn.nombre as subnovedad, rp.descripcion
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN REPORTES r ON rp.id_reporte = r.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            WHERE sn.nombre NOT IN ({placeholders_disp})
        """
        params = list(DISPONIBLE_STATUSES)
        
        if cedula:
            query += " AND p.cedula = %s"
            params.append(cedula)
        if subnovedad:
            query += " AND UPPER(sn.nombre) LIKE UPPER(%s)"
            params.append(f"%{subnovedad}%")
        if fecha:
            query += " AND r.fecha = %s"
            params.append(fecha)
        elif not is_all_months:
            dates = get_month_dates(mes)
            if dates:
                pl = ",".join("%s" for _ in dates)
                query += f" AND r.fecha IN ({pl})"
                params.extend(dates)
                
        query += " ORDER BY p.nombre ASC, r.fecha ASC;"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        agil_td_style = ParagraphStyle(f'AgilTd_{uid}', parent=td_style, fontSize=7, leading=9)
        agil_th_style = ParagraphStyle(f'AgilTh_{uid}', parent=th_style, fontSize=8, leading=10)

        if fecha:
            headers = [
                Paragraph("CÉDULA", agil_th_style),
                Paragraph("INTEGRANTE", agil_th_style),
                Paragraph("NOVEDAD", agil_th_style),
                Paragraph("DESCRIPCIÓN", agil_th_style),
                Paragraph("FECHA", agil_th_style)
            ]
            data = [headers]
            for row in rows:
                data.append([
                    Paragraph(str(row[0]), agil_td_style),
                    Paragraph(row[1], agil_td_style),
                    Paragraph(row[3], agil_td_style),
                    Paragraph(row[4] or "-", agil_td_style),
                    Paragraph(f'<font color="#DC2626"><b>{row[2]}</b></font>', agil_td_style)
                ])
            col_widths = [65, 160, 110, 305, 80]
            filename = f"exportacion_agil_{fecha}.pdf"

        elif not is_all_months:
            headers = [
                Paragraph("CÉDULA", agil_th_style),
                Paragraph("INTEGRANTE", agil_th_style),
                Paragraph(f"RESUMEN DE NOVEDADES ({mes.upper()})", agil_th_style)
            ]
            data = [headers]
            from collections import defaultdict
            person_novs = defaultdict(list)
            for r in rows:
                c_num, p_name, r_date, subnov, desc = r
                day_num = int(r_date.split('-')[2])
                person_novs[(c_num, p_name)].append((day_num, subnov))
                
            for (c_num, p_name), recs in sorted(person_novs.items(), key=lambda x: x[0][1]):
                summary_str = format_agil_month_ranges(recs, highlight_html=True)
                data.append([
                    Paragraph(str(c_num), agil_td_style),
                    Paragraph(p_name, agil_td_style),
                    Paragraph(summary_str, agil_td_style)
                ])
            col_widths = [65, 175, 480]
            filename = f"exportacion_agil_{mes}.pdf"

        else:
            active_m_codes = set(r[2].split('-')[1] for r in rows)
            if not active_m_codes:
                cursor.execute("SELECT DISTINCT to_char(to_date(fecha, 'YYYY-MM-DD'), 'MM') FROM REPORTES;")
                active_m_codes = set(row[0] for row in cursor.fetchall())

            all_month_tuples = [
                ('01', 'ENE'), ('02', 'FEB'), ('03', 'MAR'), ('04', 'ABR'),
                ('05', 'MAY'), ('06', 'JUN'), ('07', 'JUL'), ('08', 'AGO'),
                ('09', 'SEP'), ('10', 'OCT'), ('11', 'NOV'), ('12', 'DIC')
            ]
            month_names_dict = [m for m in all_month_tuples if m[0] in active_m_codes]
            
            headers = [Paragraph("CÉDULA", agil_th_style), Paragraph("INTEGRANTE", agil_th_style)] + [
                Paragraph(m_name, agil_th_style) for _, m_name in month_names_dict
            ]
            data = [headers]
            from collections import defaultdict
            person_months = defaultdict(lambda: defaultdict(list))
            for r in rows:
                c_num, p_name, r_date, subnov, desc = r
                m_code = r_date.split('-')[1]
                day_num = int(r_date.split('-')[2])
                person_months[(c_num, p_name)][m_code].append((day_num, subnov))
                
            for (c_num, p_name), m_dict in sorted(person_months.items(), key=lambda x: x[0][1]):
                row_data = [Paragraph(str(c_num), agil_td_style), Paragraph(p_name, agil_td_style)]
                for m_code, _ in month_names_dict:
                    recs = m_dict.get(m_code, [])
                    summary_str = format_agil_month_ranges(recs, highlight_html=True)
                    row_data.append(Paragraph(summary_str, agil_td_style))
                data.append(row_data)

            month_col_w = max(int(540 / len(month_names_dict)), 46) if month_names_dict else 46
            col_widths = [55, 125] + [month_col_w for _ in month_names_dict]
            filename = f"exportacion_agil_anual_{cedula if cedula else 'todos'}.pdf"

        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(t)

        
    else:
        raise HTTPException(status_code=400, detail="Parámetros inválidos")
        
    try:
        doc.build(story)
    except Exception as e:
        print(f"Error generando PDF para tipo={tipo}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno al generar PDF: {str(e)}")
        
    pdf_buffer.seek(0)
    
    response = StreamingResponse(pdf_buffer, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

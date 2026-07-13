from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
import io
import csv
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, landscape

from app.database import get_db, get_month_dates
from app.dependencies import DISPONIBLE_STATUSES

router = APIRouter(prefix="/api/exportar", tags=["Exportaciones"])

@router.get("/csv")
def exportar_csv(
    tipo: str = Query(..., description="dia, mes, personal, personal_db, subnovedades, consolidado_mensual o historial_novedades"),
    fecha: Optional[str] = Query(None),
    mes: Optional[str] = Query(None),
    cedula: Optional[int] = Query(None),
    subnovedad: Optional[str] = Query(None),
    db = Depends(get_db)
):
    output = io.StringIO()
    writer = csv.writer(output)
    
    cursor = db.cursor()
    
    if tipo == "dia" and fecha:
        writer.writerow(["CEDULA", "APELLIDOS Y NOMBRES", "SUBNOVEDAD", "DESCRIPCION", "DESDE", "HASTA"])
        cursor.execute("SELECT id FROM REPORTES WHERE fecha = ?;", (fecha,))
        r_row = cursor.fetchone()
        if r_row:
            cursor.execute("""
                SELECT p.cedula, p.nombre, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final
                FROM REGISTRO_PERSONAL rp
                JOIN PERSONAL p ON rp.id_personal = p.id
                JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                WHERE rp.id_reporte = ?
                ORDER BY p.nombre ASC;
            """, (r_row[0],))
            for row in cursor.fetchall():
                writer.writerow(list(row))
        filename = f"reporte_dia_{fecha}.csv"
        
    elif tipo == "mes" and mes:
        writer.writerow(["FECHA", "TOTAL PERSONAL", "DISPONIBLES", "NOVEDADES", "DISPONIBILIDAD %"])
        dates = get_month_dates(mes)
        for d in dates:
            cursor.execute("SELECT id FROM REPORTES WHERE fecha = ?;", (d,))
            r_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = ?;", (r_id,))
            total = cursor.fetchone()[0]
            
            placeholders = ",".join("%s" for _ in DISPONIBLE_STATUSES)
            cursor.execute(f"""
                SELECT COUNT(*) FROM REGISTRO_PERSONAL 
                WHERE id_reporte = ? AND id_sub_novedad IN (
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
        cursor.execute("SELECT id, nombre FROM PERSONAL WHERE cedula = ?;", (cedula,))
        p_row = cursor.fetchone()
        if p_row:
            query = """
                SELECT r.fecha, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final
                FROM REGISTRO_PERSONAL rp
                JOIN REPORTES r ON rp.id_reporte = r.id
                JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                WHERE rp.id_personal = ?
            """
            params = [p_row[0]]
            if mes:
                dates = get_month_dates(mes)
                if dates:
                    placeholders = ",".join("?" for _ in dates)
                    query += f" AND r.fecha IN ({placeholders})"
                    params.extend(dates)
                else:
                    query += " AND 1=0"
            if subnovedad:
                query += " AND sn.nombre = ?"
                params.append(subnovedad)
            query += " ORDER BY r.fecha DESC;"
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
        
    elif tipo == "consolidado_mensual" and mes:
        dates = get_month_dates(mes)
        if not dates:
            raise HTTPException(status_code=400, detail="No hay reportes para el mes especificado.")
        
        placeholders = ",".join("%s" for _ in dates)
        cursor.execute(f"SELECT id, fecha FROM REPORTES WHERE fecha IN ({placeholders}) ORDER BY fecha ASC;", dates)
        reports_db = cursor.fetchall()
        report_ids = [r[0] for r in reports_db]
        report_dates = [r[1] for r in reports_db]
        
        headers = ["CEDULA", "INTEGRANTE"] + [f"Dia {d.split('-')[2]}" for d in report_dates]
        writer.writerow(headers)
        
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
                key = (row[0], row[1], row[2]) # cedula, nombre, fecha_retiro
                if key not in person_map:
                    person_map[key] = {}
                person_map[key][row[4]] = row[5] # id_reporte: subnovedad
                
            for (cedula, nombre, f_retiro), reports_dict in sorted(person_map.items(), key=lambda x: x[0][1]):
                row_data = [cedula, nombre]
                for r_id, r_fecha in reports_db:
                    is_retired = False
                    if f_retiro and r_fecha >= f_retiro:
                        is_retired = True
                        
                    if is_retired:
                        row_data.append("RETIRADO")
                    else:
                        row_data.append(reports_dict.get(r_id, "N/A"))
                writer.writerow(row_data)
        filename = f"consolidado_mensual_{mes}.csv"
        
    elif tipo == "historial_novedades":
        writer.writerow(["CEDULA", "APELLIDOS Y NOMBRES", "SUBNOVEDAD", "DESCRIPCION", "DESDE", "HASTA", "FECHA REPORTE"])
        cursor.execute("""
            SELECT p.cedula, p.nombre, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final, r.fecha
            FROM REGISTRO_PERSONAL rp
            JOIN PERSONAL p ON rp.id_personal = p.id
            JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
            JOIN REPORTES r ON rp.id_reporte = r.id
            ORDER BY r.fecha DESC, p.nombre ASC;
        """)
        for row in cursor.fetchall():
            writer.writerow(list(row))
        filename = "historial_completo_novedades.csv"
        
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
    db = Depends(get_db)
):
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
    
    if tipo == "dia" and fecha:
        ws.title = f"Reporte {fecha}"
        
        # Title Row
        ws.merge_cells("A1:F1")
        ws["A1"] = f"BIMEJ12 — REPORTE DIARIO DE PERSONAL — {fecha}"
        ws["A1"].font = title_font
        ws["A1"].fill = title_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 40
        
        # Headers
        headers = ["CÉDULA", "APELLIDOS Y NOMBRES", "SUBNOVEDAD", "DESCRIPCIÓN", "DESDE", "HASTA"]
        ws.append([]) # Blank row
        ws.append(headers)
        
        # Style headers
        ws.row_dimensions[3].height = 25
        for col_idx in range(1, 7):
            cell = ws.cell(row=3, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border
            
        cursor.execute("SELECT id FROM REPORTES WHERE fecha = ?;", (fecha,))
        r_row = cursor.fetchone()
        if r_row:
            cursor.execute("""
                SELECT p.cedula, p.nombre, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final
                FROM REGISTRO_PERSONAL rp
                JOIN PERSONAL p ON rp.id_personal = p.id
                JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                WHERE rp.id_reporte = ?
                ORDER BY p.nombre ASC;
            """, (r_row[0],))
            for row in cursor.fetchall():
                ws.append(list(row))
                
        # Format data rows
        for r_idx in range(4, ws.max_row + 1):
            ws.row_dimensions[r_idx].height = 20
            for c_idx in range(1, 7):
                cell = ws.cell(row=r_idx, column=c_idx)
                cell.font = normal_font
                cell.border = thin_border
                if c_idx == 1:
                    cell.alignment = Alignment(horizontal="left")
                elif c_idx in (5, 6):
                    cell.alignment = Alignment(horizontal="center")
                    
        filename = f"reporte_diario_{fecha}.xlsx"
        
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
            cursor.execute("SELECT id FROM REPORTES WHERE fecha = ?;", (d,))
            r_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = ?;", (r_id,))
            total = cursor.fetchone()[0]
            
            placeholders = ",".join("%s" for _ in DISPONIBLE_STATUSES)
            cursor.execute(f"""
                SELECT COUNT(*) FROM REGISTRO_PERSONAL 
                WHERE id_reporte = ? AND id_sub_novedad IN (
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
        cursor.execute("SELECT id, nombre, CASE WHEN fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END as estado FROM PERSONAL WHERE cedula = ?;", (cedula,))
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
                WHERE rp.id_personal = ?
            """
            params = [p_row[0]]
            if mes:
                dates = get_month_dates(mes)
                if dates:
                    placeholders = ",".join("?" for _ in dates)
                    query += f" AND r.fecha IN ({placeholders})"
                    params.extend(dates)
                else:
                    query += " AND 1=0"
            if subnovedad:
                query += " AND sn.nombre = ?"
                params.append(subnovedad)
            query += " ORDER BY r.fecha DESC;"
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
        
    elif tipo == "consolidado_mensual" and mes:
        ws.title = f"Consolidado {mes}"
        dates = get_month_dates(mes)
        if not dates:
            raise HTTPException(status_code=400, detail="No hay reportes para el mes especificado.")
            
        placeholders = ",".join("%s" for _ in dates)
        cursor.execute(f"SELECT id, fecha FROM REPORTES WHERE fecha IN ({placeholders}) ORDER BY fecha ASC;", dates)
        reports_db = cursor.fetchall()
        report_ids = [r[0] for r in reports_db]
        report_dates = [r[1] for r in reports_db]
        
        num_cols = 2 + len(report_dates)
        col_letter = get_column_letter(num_cols)
        
        ws.merge_cells(f"A1:{col_letter}1")
        if cedula:
            ws["A1"] = f"BIMEJ12 — HISTORIAL DE PERSONAL (CC {cedula}) — {mes.upper()}"
        else:
            ws["A1"] = f"BIMEJ12 — CONSOLIDADO DIARIO DE PERSONAL — {mes.upper()}"
        ws["A1"].font = title_font
        ws["A1"].fill = title_fill
        ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 40
        
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
                query += " AND sn.nombre = %s"
                params.append(subnovedad)
            query += " ORDER BY p.nombre ASC;"
            
            cursor.execute(query, params)
            
            person_map = {}
            for row in cursor.fetchall():
                key = (row[0], row[1], row[2]) # cedula, nombre, fecha_retiro
                if key not in person_map:
                    person_map[key] = {}
                person_map[key][row[4]] = row[5] # id_reporte: subnovedad
                
            for (cedula, nombre, f_retiro), reports_dict in sorted(person_map.items(), key=lambda x: x[0][1]):
                row_data = [cedula, nombre]
                for r_id, r_fecha in reports_db:
                    is_retired = False
                    if f_retiro and r_fecha >= f_retiro:
                        is_retired = True
                        
                    if is_retired:
                        row_data.append("RETIRADO")
                    else:
                        row_data.append(reports_dict.get(r_id, "N/A"))
                ws.append(row_data)
                
        for r_idx in range(4, ws.max_row + 1):
            ws.row_dimensions[r_idx].height = 20
            for c_idx in range(1, num_cols + 1):
                cell = ws.cell(row=r_idx, column=c_idx)
                cell.font = normal_font
                cell.border = thin_border
                if c_idx >= 3:
                    cell.alignment = Alignment(horizontal="center")
                    val = cell.value
                    if val in DISPONIBLE_STATUSES:
                        cell.fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
                        cell.font = Font(name="Calibri", size=9, color="065F46")
                    elif val == "N/A":
                        cell.fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
                        cell.font = Font(name="Calibri", size=9, color="6B7280")
                    elif val == "RETIRADO":
                        cell.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
                        cell.font = Font(name="Calibri", size=9, color="DC2626", bold=True)
                    else:
                        cell.fill = PatternFill(start_color="FFE4E6", end_color="FFE4E6", fill_type="solid")
                        cell.font = Font(name="Calibri", size=9, color="991B1B")
        filename = f"consolidado_personal_{mes}.xlsx"
        
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
            ORDER BY r.fecha DESC, p.nombre ASC;
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
        
    else:
        raise HTTPException(status_code=400, detail="Parámetros inválidos")
        
    # Auto-adjust column widths
    if tipo != "consolidado_mensual":
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row == 1:
                    continue
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
    else:
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 28
        for col_idx in range(3, num_cols + 1):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = 8
        
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
    db = Depends(get_db)
):
    pdf_buffer = io.BytesIO()
    
    # Select document layout based on export type
    doc_layout = landscape(letter) if tipo in ("dia", "mes", "consolidado_mensual", "historial_novedades") else letter
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=doc_layout,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#475569'),
        alignment=1, # Center
        spaceAfter=20
    )
    
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white,
        alignment=1 # Center
    )
    
    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#1E293B'),
        alignment=0 # Left
    )
    
    story = []
    cursor = db.cursor()
    
    if tipo == "dia" and fecha:
        story.append(Paragraph(f"BIMEJ12 — REPORTE DIARIO DE PERSONAL", title_style))
        story.append(Paragraph(f"Fecha del Reporte: {fecha} | Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
        
        headers = [
            Paragraph("CÉDULA", th_style),
            Paragraph("APELLIDOS Y NOMBRES", th_style),
            Paragraph("SUBNOVEDAD", th_style),
            Paragraph("DESCRIPCIÓN", th_style),
            Paragraph("DESDE", th_style),
            Paragraph("HASTA", th_style)
        ]
        
        data = [headers]
        
        cursor.execute("SELECT id FROM REPORTES WHERE fecha = ?;", (fecha,))
        r_row = cursor.fetchone()
        if r_row:
            cursor.execute("""
                SELECT p.cedula, p.nombre, sn.nombre, rp.descripcion, rp.fecha_inicio, rp.fecha_final
                FROM REGISTRO_PERSONAL rp
                JOIN PERSONAL p ON rp.id_personal = p.id
                JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
                WHERE rp.id_reporte = ?
                ORDER BY p.nombre ASC;
            """, (r_row[0],))
            
            for row in cursor.fetchall():
                data.append([
                    Paragraph(str(row[0]), td_style),
                    Paragraph(row[1], td_style),
                    Paragraph(row[2], td_style),
                    Paragraph(row[3] or "", td_style),
                    Paragraph(row[4] or "-", td_style),
                    Paragraph(row[5] or "-", td_style)
                ])
                
        col_widths = [75, 180, 110, 195, 80, 80]
        
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
        filename = f"reporte_dia_{fecha}.pdf"
        
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
            cursor.execute("SELECT id FROM REPORTES WHERE fecha = ?;", (d,))
            r_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = ?;", (r_id,))
            total = cursor.fetchone()[0]
            
            placeholders = ",".join("?" for _ in DISPONIBLE_STATUSES)
            cursor.execute(f"""
                SELECT COUNT(*) FROM REGISTRO_PERSONAL 
                WHERE id_reporte = ? AND id_sub_novedad IN (
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
        cursor.execute("SELECT id, nombre, CASE WHEN fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END as estado, fecha_retiro FROM PERSONAL WHERE cedula = ?;", (cedula,))
        p_row = cursor.fetchone()
        if not p_row:
            raise HTTPException(status_code=404, detail="Personal no encontrado")
            
        p_id, nombre, estado, fecha_retiro = p_row[0], p_row[1], p_row[2], p_row[3]
        
        story.append(Paragraph(f"HISTORIAL DE PERSONAL INDIVIDUAL", title_style))
        story.append(Paragraph(f"Integrante: {nombre} | Cédula: {cedula} | Estado: {estado} " + (f"| Fecha Retiro: {fecha_retiro}" if fecha_retiro else ""), subtitle_style))
        
        cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_personal = ?;", (p_id,))
        total_dias = cursor.fetchone()[0]
        
        placeholders = ",".join("?" for _ in DISPONIBLE_STATUSES)
        cursor.execute(f"""
            SELECT COUNT(*) FROM REGISTRO_PERSONAL 
            WHERE id_personal = ? AND id_sub_novedad IN (
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
            WHERE rp.id_personal = ?
        """
        params = [p_id]
        if mes:
            dates = get_month_dates(mes)
            if dates:
                placeholders = ",".join("?" for _ in dates)
                query += f" AND r.fecha IN ({placeholders})"
                params.extend(dates)
            else:
                query += " AND 1=0"
        if subnovedad:
            query += " AND sn.nombre = ?"
            params.append(subnovedad)
        query += " ORDER BY r.fecha DESC;"
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
        
    elif tipo == "consolidado_mensual" and mes:
        doc_layout = landscape(letter)
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=doc_layout,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        pdf_title = f"BIMEJ12 — CONSOLIDADO DIARIO DE PERSONAL — {mes.upper()}"
        if cedula:
            pdf_title = f"BIMEJ12 — HISTORIAL DE PERSONAL (CC {cedula}) — {mes.upper()}"
        story.append(Paragraph(pdf_title, title_style))
        story.append(Paragraph(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | D = Disponible, N = Novedad, R = Retirado, - = N/A", subtitle_style))
        
        dates = get_month_dates(mes)
        if not dates:
            raise HTTPException(status_code=400, detail="No hay reportes para el mes especificado.")
            
        placeholders = ",".join("%s" for _ in dates)
        cursor.execute(f"SELECT id, fecha FROM REPORTES WHERE fecha IN ({placeholders}) ORDER BY fecha ASC;", dates)
        reports_db = cursor.fetchall()
        report_ids = [r[0] for r in reports_db]
        report_dates = [r[1] for r in reports_db]
        
        headers = [
            Paragraph("CÉDULA", th_style),
            Paragraph("INTEGRANTE", th_style)
        ] + [Paragraph(d.split('-')[2], th_style) for d in report_dates]
        
        data = [headers]
        
        disp_style = ParagraphStyle('DStyle', parent=td_style, textColor=colors.HexColor('#10B981'), fontName='Helvetica-Bold', alignment=1)
        nov_style = ParagraphStyle('NStyle', parent=td_style, textColor=colors.HexColor('#EF4444'), fontName='Helvetica-Bold', alignment=1)
        na_style = ParagraphStyle('NAStyle', parent=td_style, textColor=colors.HexColor('#6B7280'), alignment=1)
        ret_style = ParagraphStyle('RStyle', parent=td_style, textColor=colors.HexColor('#DC2626'), fontName='Helvetica-Bold', alignment=1)
        
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
                key = (row[0], row[1], row[2]) # cedula, nombre, fecha_retiro
                if key not in person_map:
                    person_map[key] = {}
                person_map[key][row[4]] = row[5] # id_reporte: subnovedad
                
            for (cedula, nombre, f_retiro), reports_dict in sorted(person_map.items(), key=lambda x: x[0][1]):
                row_data = [
                    Paragraph(str(cedula), td_style),
                    Paragraph(nombre, td_style)
                ]
                for r_id, r_fecha in reports_db:
                    is_retired = False
                    if f_retiro and r_fecha >= f_retiro:
                        is_retired = True
                        
                    if is_retired:
                        row_data.append(Paragraph("R", ret_style))
                    else:
                        val = reports_dict.get(r_id, "N/A")
                        if val in DISPONIBLE_STATUSES:
                            row_data.append(Paragraph("D", disp_style))
                        elif val == "N/A":
                            row_data.append(Paragraph("-", na_style))
                        else:
                            row_data.append(Paragraph("N", nov_style))
                data.append(row_data)
                
        num_days_col = len(report_dates)
        day_col_width = 18 if num_days_col <= 31 else 15
        name_width = 720 - 60 - (num_days_col * day_col_width)
        col_widths = [60, name_width] + [day_col_width for _ in report_dates]
        
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
            ('ALIGN', (0,0), (1,-1), 'LEFT'),
            ('ALIGN', (2,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(t)
        filename = f"consolidado_personal_{mes}.pdf"
        
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
            ORDER BY r.fecha DESC, p.nombre ASC;
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
        story.append(t)
        filename = "historial_completo_novedades.pdf"
        
    else:
        raise HTTPException(status_code=400, detail="Parámetros inválidos")
        
    doc.build(story)
    pdf_buffer.seek(0)
    
    response = StreamingResponse(pdf_buffer, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

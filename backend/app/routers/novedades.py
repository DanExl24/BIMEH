from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import io
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape

from app.database import get_db, get_month_dates

router = APIRouter(prefix="/api/novedades", tags=["GestionNovedades"])


@router.get("/catalogo")
def get_catalogo_novedades(db = Depends(get_db)):
    """
    Retorna la lista completa de sub_novedades con el conteo acumulado de registros en la base de datos.
    """
    cursor = db.cursor()
    cursor.execute("""
        SELECT sn.id, sn.nombre, COUNT(rp.id) AS total_registros, COUNT(DISTINCT rp.id_personal) AS total_personal
        FROM SUB_NOVEDADES sn
        LEFT JOIN REGISTRO_PERSONAL rp ON sn.id = rp.id_sub_novedad
        GROUP BY sn.id, sn.nombre
        ORDER BY sn.id ASC;
    """)
    rows = cursor.fetchall()
    return [
        {
            "id": row[0],
            "nombre": row[1],
            "total_registros": row[2],
            "total_personal": row[3]
        }
        for row in rows
    ]


def _build_novedades_where_clause(
    id_sub_novedad: Optional[int] = None,
    mes: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    q: Optional[str] = None,
    estado: Optional[str] = None,
):
    where_clauses = []
    params = []

    if id_sub_novedad is not None and id_sub_novedad > 0:
        where_clauses.append("rp.id_sub_novedad = %s")
        params.append(id_sub_novedad)

    if mes and mes.upper() != "TODOS":
        dates = get_month_dates(mes)
        if dates:
            placeholders = ",".join("%s" for _ in dates)
            where_clauses.append(f"r.fecha IN ({placeholders})")
            params.extend(dates)
        else:
            where_clauses.append("1=0")

    if fecha_inicio:
        where_clauses.append("r.fecha >= %s")
        params.append(fecha_inicio)

    if fecha_fin:
        where_clauses.append("r.fecha <= %s")
        params.append(fecha_fin)

    if q and q.strip():
        search_pattern = f"%{q.strip().upper()}%"
        where_clauses.append("(CAST(p.cedula AS TEXT) LIKE %s OR UPPER(p.nombre) LIKE %s)")
        params.extend([search_pattern, search_pattern])

    if estado and estado.upper() != "TODOS":
        if estado.upper() == "ACTIVO":
            where_clauses.append("p.fecha_retiro IS NULL")
        elif estado.upper() == "RETIRADO":
            where_clauses.append("p.fecha_retiro IS NOT NULL")

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    return where_sql, params


@router.get("/consulta")
def consultar_novedades(
    id_sub_novedad: Optional[int] = Query(None, description="ID de la subnovedad a consultar"),
    mes: Optional[str] = Query(None, description="Nombre del mes (ej. ENERO, FEBRERO) o TODOS"),
    fecha_inicio: Optional[str] = Query(None, description="Fecha mínima YYYY-MM-DD"),
    fecha_fin: Optional[str] = Query(None, description="Fecha máxima YYYY-MM-DD"),
    q: Optional[str] = Query(None, description="Búsqueda por cédula o nombre"),
    estado: Optional[str] = Query("TODOS", description="TODOS, ACTIVO o RETIRADO"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    db = Depends(get_db)
):
    cursor = db.cursor()
    where_sql, params = _build_novedades_where_clause(
        id_sub_novedad=id_sub_novedad,
        mes=mes,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        q=q,
        estado=estado
    )

    # 1. Calcular KPIs globales con los filtros aplicados
    kpi_query = f"""
        SELECT 
            COUNT(rp.id) AS total_registros,
            COUNT(DISTINCT rp.id_personal) AS personal_unico,
            COUNT(DISTINCT CASE WHEN p.fecha_retiro IS NULL THEN p.id ELSE NULL END) AS activos_unicos,
            COUNT(DISTINCT CASE WHEN p.fecha_retiro IS NOT NULL THEN p.id ELSE NULL END) AS retirados_unicos,
            MIN(r.fecha) AS primera_fecha,
            MAX(r.fecha) AS ultima_fecha
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON rp.id_personal = p.id
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        JOIN REPORTES r ON rp.id_reporte = r.id
        {where_sql};
    """
    cursor.execute(kpi_query, params)
    kpi_row = cursor.fetchone()

    total_registros = kpi_row[0] or 0
    personal_unico = kpi_row[1] or 0
    activos_unicos = kpi_row[2] or 0
    retirados_unicos = kpi_row[3] or 0
    primera_fecha = kpi_row[4]
    ultima_fecha = kpi_row[5]

    # 2. Paginación de resultados
    offset = (page - 1) * limit
    data_query = f"""
        SELECT 
            rp.id,
            p.cedula,
            p.nombre,
            CASE WHEN p.fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END AS estado,
            p.fecha_retiro,
            sn.id AS id_sub_novedad,
            sn.nombre AS sub_novedad,
            r.fecha AS fecha_reporte,
            COALESCE(rp.fecha_inicio, '') AS fecha_inicio,
            COALESCE(rp.fecha_final, '') AS fecha_final,
            COALESCE(rp.descripcion, '') AS descripcion
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON rp.id_personal = p.id
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        JOIN REPORTES r ON rp.id_reporte = r.id
        {where_sql}
        ORDER BY r.fecha DESC, p.nombre ASC
        LIMIT %s OFFSET %s;
    """
    data_params = list(params) + [limit, offset]
    cursor.execute(data_query, data_params)
    rows = cursor.fetchall()

    registros = [
        {
            "id": row[0],
            "cedula": row[1],
            "nombre": row[2],
            "estado": row[3],
            "fecha_retiro": row[4],
            "id_sub_novedad": row[5],
            "sub_novedad": row[6],
            "fecha_reporte": row[7],
            "fecha_inicio": row[8],
            "fecha_final": row[9],
            "descripcion": row[10]
        }
        for row in rows
    ]

    total_pages = (total_registros + limit - 1) // limit if limit > 0 else 1

    return {
        "kpis": {
            "total_registros": total_registros,
            "personal_unico": personal_unico,
            "activos_unicos": activos_unicos,
            "retirados_unicos": retirados_unicos,
            "primera_fecha": primera_fecha,
            "ultima_fecha": ultima_fecha
        },
        "registros": registros,
        "total": total_registros,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }


@router.get("/exportar/excel")
def exportar_novedades_excel(
    id_sub_novedad: Optional[int] = Query(None),
    mes: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    estado: Optional[str] = Query("TODOS"),
    db = Depends(get_db)
):
    cursor = db.cursor()
    where_sql, params = _build_novedades_where_clause(
        id_sub_novedad=id_sub_novedad,
        mes=mes,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        q=q,
        estado=estado
    )

    # Obtener nombre de la novedad si hay filtro
    subnovedad_nombre = "TODAS LAS NOVEDADES"
    if id_sub_novedad:
        cursor.execute("SELECT nombre FROM SUB_NOVEDADES WHERE id = %s;", (id_sub_novedad,))
        s_row = cursor.fetchone()
        if s_row:
            subnovedad_nombre = s_row[0]

    # Consultar todos los registros coincidentes (hasta un límite seguro de 15.000 para el archivo)
    query = f"""
        SELECT 
            p.cedula,
            p.nombre,
            CASE WHEN p.fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END AS estado,
            sn.nombre AS sub_novedad,
            r.fecha AS fecha_reporte,
            COALESCE(rp.fecha_inicio, '') AS fecha_inicio,
            COALESCE(rp.fecha_final, '') AS fecha_final,
            COALESCE(rp.descripcion, '') AS descripcion
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON rp.id_personal = p.id
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        JOIN REPORTES r ON rp.id_reporte = r.id
        {where_sql}
        ORDER BY r.fecha DESC, p.nombre ASC
        LIMIT 15000;
    """
    cursor.execute(query, params)
    rows = cursor.fetchall()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte de Novedades"
    ws.views.sheetView[0].showGridLines = True

    # Paleta de colores militar / institucional
    primary_color = "0F172A"  # Dark Slate
    secondary_color = "0284C7" # Cyan/Blue
    accent_gray = "F1F5F9"
    border_color = "CBD5E1"

    header_font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color=primary_color, end_color=primary_color, fill_type="solid")
    sub_font = Font(name="Calibri", size=10, bold=True, color="334155")
    sub_fill = PatternFill(start_color=accent_gray, end_color=accent_gray, fill_type="solid")
    
    thin_border = Border(
        left=Side(style='thin', color=border_color),
        right=Side(style='thin', color=border_color),
        top=Side(style='thin', color=border_color),
        bottom=Side(style='thin', color=border_color)
    )

    # 1. Encabezado principal
    ws.merge_cells("A1:H1")
    ws["A1"] = "BIMEH 12 - SISTEMA DE CONTROL OPERACIONAL"
    ws["A1"].font = header_font
    ws["A1"].fill = header_fill
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:H2")
    ws["A2"] = f"REPORTE ANALÍTICO DE NOVEDADES DEL PERSONAL - {subnovedad_nombre}"
    ws["A2"].font = Font(name="Calibri", size=11, bold=True, color="0284C7")
    ws["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 20

    # 2. Resumen de Filtros aplicados
    filtros_resumen = [
        ("Novedad:", subnovedad_nombre, "Mes / Periodo:", mes or "TODOS"),
        ("Rango Fechas:", f"{fecha_inicio or 'Inicio'} a {fecha_fin or 'Fin'}", "Estado Personal:", estado or "TODOS"),
        ("Búsqueda:", q or "(Ninguna)", "Total Registros:", f"{len(rows)} encontrados"),
    ]

    curr_row = 4
    for f1_label, f1_val, f2_label, f2_val in filtros_resumen:
        ws.cell(row=curr_row, column=1, value=f1_label).font = sub_font
        ws.cell(row=curr_row, column=2, value=f1_val).font = Font(name="Calibri", size=10)
        ws.cell(row=curr_row, column=4, value=f2_label).font = sub_font
        ws.cell(row=curr_row, column=5, value=f2_val).font = Font(name="Calibri", size=10, bold=(f2_label == "Total Registros:"))
        curr_row += 1

    curr_row += 1

    # 3. Encabezados de tabla
    headers = [
        "CÉDULA",
        "APELLIDOS Y NOMBRES",
        "ESTADO",
        "NOVEDAD ASIGNADA",
        "FECHA REPORTE",
        "FECHA INICIO",
        "FECHA FINAL",
        "DESCRIPCIÓN / OBSERVACIÓN"
    ]

    col_widths = [14, 34, 12, 25, 15, 14, 14, 40]
    th_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    th_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")

    for col_idx, header_text in enumerate(headers, 1):
        cell = ws.cell(row=curr_row, column=col_idx, value=header_text)
        cell.font = th_font
        cell.fill = th_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
    ws.row_dimensions[curr_row].height = 24
    curr_row += 1

    # 4. Filas de datos
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    for idx, r in enumerate(rows):
        row_fill = zebra_fill if idx % 2 == 1 else white_fill
        r_cells = [
            ws.cell(row=curr_row, column=1, value=r[0]), # Cedula
            ws.cell(row=curr_row, column=2, value=r[1]), # Nombre
            ws.cell(row=curr_row, column=3, value=r[2]), # Estado
            ws.cell(row=curr_row, column=4, value=r[3]), # Subnovedad
            ws.cell(row=curr_row, column=5, value=r[4]), # Fecha reporte
            ws.cell(row=curr_row, column=6, value=r[5] if r[5] else "-"), # Fecha inicio
            ws.cell(row=curr_row, column=7, value=r[6] if r[6] else "-"), # Fecha final
            ws.cell(row=curr_row, column=8, value=r[7] if r[7] else "-")  # Observacion
        ]

        for c_idx, cell in enumerate(r_cells, 1):
            cell.font = Font(name="Calibri", size=9)
            cell.fill = row_fill
            cell.border = thin_border
            if c_idx in (1, 3, 5, 6, 7):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        ws.row_dimensions[curr_row].height = 18
        curr_row += 1

    # Ajustar anchos de columnas
    for i, w in enumerate(col_widths, 1):
        col_letter = get_column_letter(i)
        ws.column_dimensions[col_letter].width = w

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Reporte_Novedades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/exportar/pdf")
def exportar_novedades_pdf(
    id_sub_novedad: Optional[int] = Query(None),
    mes: Optional[str] = Query(None),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    estado: Optional[str] = Query("TODOS"),
    db = Depends(get_db)
):
    cursor = db.cursor()
    where_sql, params = _build_novedades_where_clause(
        id_sub_novedad=id_sub_novedad,
        mes=mes,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        q=q,
        estado=estado
    )

    subnovedad_nombre = "TODAS LAS NOVEDADES"
    if id_sub_novedad:
        cursor.execute("SELECT nombre FROM SUB_NOVEDADES WHERE id = %s;", (id_sub_novedad,))
        s_row = cursor.fetchone()
        if s_row:
            subnovedad_nombre = s_row[0]

    query = f"""
        SELECT 
            p.cedula,
            p.nombre,
            CASE WHEN p.fecha_retiro IS NULL THEN 'ACTIVO' ELSE 'RETIRADO' END AS estado,
            sn.nombre AS sub_novedad,
            r.fecha AS fecha_reporte,
            COALESCE(rp.fecha_inicio, '') AS fecha_inicio,
            COALESCE(rp.fecha_final, '') AS fecha_final,
            COALESCE(rp.descripcion, '') AS descripcion
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON rp.id_personal = p.id
        JOIN SUB_NOVEDADES sn ON rp.id_sub_novedad = sn.id
        JOIN REPORTES r ON rp.id_reporte = r.id
        {where_sql}
        ORDER BY r.fecha DESC, p.nombre ASC
        LIMIT 5000;
    """
    cursor.execute(query, params)
    rows = cursor.fetchall()

    pdf_buffer = io.BytesIO()
    uid = id(pdf_buffer)
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(letter),
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        f'NovedadTitle_{uid}',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        f'NovedadSubtitle_{uid}',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#0284C7'),
        alignment=1,
        spaceAfter=12
    )
    meta_style = ParagraphStyle(
        f'NovedadMeta_{uid}',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#334155'),
        alignment=0
    )
    th_style = ParagraphStyle(
        f'NovedadTH_{uid}',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        textColor=colors.white,
        alignment=1
    )
    td_style = ParagraphStyle(
        f'NovedadTD_{uid}',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        textColor=colors.HexColor('#1E293B'),
        alignment=0
    )
    td_center_style = ParagraphStyle(
        f'NovedadTDCenter_{uid}',
        parent=td_style,
        alignment=1
    )

    story = []
    story.append(Paragraph("BIMEH 12 - SISTEMA DE CONTROL OPERACIONAL", title_style))
    story.append(Paragraph(f"REPORTE OFICIAL DE NOVEDADES - {subnovedad_nombre}", subtitle_style))

    # Meta banner
    meta_text = (
        f"<b>Filtros aplicados:</b> Novedad: <i>{subnovedad_nombre}</i> | "
        f"Mes: <i>{mes or 'TODOS'}</i> | "
        f"Rango Fechas: <i>{fecha_inicio or 'Inicio'} a {fecha_fin or 'Fin'}</i> | "
        f"Estado: <i>{estado or 'TODOS'}</i> | "
        f"Búsqueda: <i>{q or 'N/A'}</i> | "
        f"<b>Total registros:</b> {len(rows)} | "
        f"<b>Fecha emisión:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 10))

    # Tabla
    table_data = [[
        Paragraph("CÉDULA", th_style),
        Paragraph("APELLIDOS Y NOMBRES", th_style),
        Paragraph("ESTADO", th_style),
        Paragraph("NOVEDAD", th_style),
        Paragraph("FECHA REP.", th_style),
        Paragraph("DESDE", th_style),
        Paragraph("HASTA", th_style),
        Paragraph("OBSERVACIÓN", th_style),
    ]]

    for r in rows:
        cedula_str = str(r[0])
        nombre_str = str(r[1])
        estado_str = str(r[2])
        novedad_str = str(r[3])
        fecha_rep_str = str(r[4])
        desde_str = str(r[5]) if r[5] else "-"
        hasta_str = str(r[6]) if r[6] else "-"
        obs_str = str(r[7]) if r[7] else "-"
        if len(obs_str) > 60:
            obs_str = obs_str[:57] + "..."

        table_data.append([
            Paragraph(cedula_str, td_center_style),
            Paragraph(nombre_str, td_style),
            Paragraph(estado_str, td_center_style),
            Paragraph(novedad_str, td_style),
            Paragraph(fecha_rep_str, td_center_style),
            Paragraph(desde_str, td_center_style),
            Paragraph(hasta_str, td_center_style),
            Paragraph(obs_str, td_style)
        ])

    col_widths = [65, 160, 50, 110, 65, 55, 55, 172]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))

    story.append(t)
    doc.build(story)
    pdf_buffer.seek(0)

    filename = f"Reporte_Novedades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException

from app.database import get_db
from app.dependencies import DISPONIBLE_STATUSES
from app.models import (
    AlertaFatigaItem,
    AlertaSanidadItem,
    ProyeccionFuerzaData,
    ProyeccionHorizonte,
    ProyeccionMovimiento,
    ParteDiarioData
)

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])

@router.get("/inconsistencias")
def get_inconsistencias():
    """Reads processing_report.json and returns log of issues."""
    try:
        with open("processing_report.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _clean_param(val, default_val=None):
    if hasattr(val, 'default'):
        return val.default
    return val if val is not None else default_val

def _get_target_date(cursor, fecha: Optional[str]) -> str:
    """Retorna la fecha solicitada o la fecha más reciente de REPORTES."""
    fecha_limpia = _clean_param(fecha)
    if fecha_limpia:
        return str(fecha_limpia)
    cursor.execute("SELECT fecha FROM REPORTES ORDER BY fecha DESC LIMIT 1;")
    row = cursor.fetchone()
    if row:
        return row[0]
    return datetime.now().strftime("%Y-%m-%d")

# ====================================================================
# 1. RADAR DE FATIGA OPERACIONAL
# ====================================================================
@router.get("/fatiga", response_model=List[AlertaFatigaItem])
def get_alertas_fatiga(
    umbral: int = Query(30, description="Días mínimos continuos en servicio sin descanso"),
    fecha: Optional[str] = Query(None, description="Fecha de corte (YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """
    Calcula los efectivos que superan una racha continua de días en servicio disponible
    (AREA OPERACIONES / CDO UNIDAD) sin haber disfrutado de permiso o vacaciones.
    """
    umbral = int(_clean_param(umbral, 30))
    cursor = db.cursor()
    target_date = _get_target_date(cursor, fecha)

    # 1. Obtener los últimos 90 reportes anteriores o iguales a target_date
    cursor.execute(
        "SELECT id, fecha FROM REPORTES WHERE fecha <= %s ORDER BY fecha DESC LIMIT 90;",
        (target_date,)
    )
    reportes = cursor.fetchall()
    if not reportes:
        return []

    ultimo_rep_id = reportes[0][0]

    # 2. Personal disponible en el último reporte analizado
    cursor.execute("""
        SELECT rp.id_personal, p.cedula, p.nombre, sn.nombre AS estado_actual
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON p.id = rp.id_personal
        JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad
        WHERE rp.id_reporte = %s AND sn.nombre IN ('AREA OPERACIONES', 'CDO UNIDAD')
        AND (p.fecha_retiro IS NULL OR p.fecha_retiro = '')
    """, (ultimo_rep_id,))
    disponibles = cursor.fetchall()
    if not disponibles:
        return []

    rep_ids = [r[0] for r in reportes]
    rep_placeholders = ",".join(str(r) for r in rep_ids)

    # 3. Consultar novedades del personal en estos reportes
    cursor.execute(f"""
        SELECT rp.id_reporte, rp.id_personal, sn.nombre
        FROM REGISTRO_PERSONAL rp
        JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad
        WHERE rp.id_reporte IN ({rep_placeholders})
    """)
    historial: Dict[int, Dict[int, str]] = {}
    for r_id, p_id, sn_nombre in cursor.fetchall():
        if p_id not in historial:
            historial[p_id] = {}
        historial[p_id][r_id] = sn_nombre

    # 4. Calcular racha continua hacia atrás
    resultados = []
    descansos = {'PERMISO', 'VACACIONES'}
    disponibles_set = {'AREA OPERACIONES', 'CDO UNIDAD'}

    for p_id, cedula, nombre, estado_actual in disponibles:
        racha = 0
        for r_id, _ in reportes:
            sn = historial.get(p_id, {}).get(r_id)
            if sn in descansos:
                break
            elif sn in disponibles_set:
                racha += 1
            else:
                # Novedad diferente (comisión, curso, incapacidad) interrumpe la racha continua de disponibilidad pura
                break

        if racha >= umbral:
            if racha >= 45:
                nivel = "CRITICO"
                rec = "Supera los 45 días continuos en servicio. Priorizar turno de relevo o permiso operacional inmediato."
            elif racha >= 30:
                nivel = "ALTO"
                rec = "Acumula más de 30 días continuos. Programar turno de descanso próximo."
            else:
                nivel = "MODERADO"
                rec = "Seguimiento preventivo de permanencia en primera línea."

            resultados.append(AlertaFatigaItem(
                id_personal=p_id,
                cedula=cedula,
                nombre=nombre,
                dias_continuos=racha,
                estado_actual=estado_actual,
                nivel_alerta=nivel,
                recomendacion=rec
            ))

    resultados.sort(key=lambda x: x.dias_continuos, reverse=True)
    return resultados

# ====================================================================
# 2. ALERTAS DE SANIDAD Y JUNTA MÉDICA
# ====================================================================
@router.get("/sanidad", response_model=List[AlertaSanidadItem])
def get_alertas_sanidad(
    dias_min: int = Query(15, description="Días mínimos acumulados en novedades médicas"),
    fecha: Optional[str] = Query(None, description="Fecha máxima de corte"),
    anio: Optional[int] = Query(None, description="Año específico a evaluar"),
    db = Depends(get_db)
):
    """
    Identifica efectivos con ausentismos médicos reiterados o prolongados
    (INCAPACIDAD, HOSPITALIZADOS, TRATAMIENTO LESIHMANIASIS) para sugerir Junta Médica o seguimiento prioritario.
    """
    dias_min = int(_clean_param(dias_min, 15))
    anio_limpio = _clean_param(anio)
    cursor = db.cursor()
    target_date = _get_target_date(cursor, fecha)

    filtros = [
        "(UPPER(sn.nombre) LIKE '%%INCAPACIDAD%%' OR UPPER(sn.nombre) LIKE '%%HOSPITAL%%' OR UPPER(sn.nombre) LIKE '%%LESIHMANIASIS%%')",
        "(p.fecha_retiro IS NULL OR p.fecha_retiro = '')",
        "r.fecha <= %s"
    ]
    params: List[Any] = [target_date]

    if anio_limpio:
        filtros.append("r.fecha LIKE %s")
        params.append(f"{anio_limpio}-%%")

    where_clause = " AND ".join(filtros)

    sql = f"""
        SELECT 
            p.id,
            p.cedula,
            p.nombre,
            COUNT(rp.id) AS total_dias_sanidad,
            COUNT(DISTINCT rp.id_reporte) AS episodios,
            MAX(r.fecha) AS ultima_fecha,
            STRING_AGG(DISTINCT sn.nombre, ', ') AS novedades
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON p.id = rp.id_personal
        JOIN REPORTES r ON r.id = rp.id_reporte
        JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad
        WHERE {where_clause}
        GROUP BY p.id, p.cedula, p.nombre
        HAVING COUNT(rp.id) >= %s
        ORDER BY total_dias_sanidad DESC;
    """
    params.append(dias_min)

    cursor.execute(sql, tuple(params))
    filas = cursor.fetchall()

    resultados = []
    for p_id, cedula, nombre, total_dias, episodios, ultima_fecha, novedades in filas:
        if total_dias >= 30:
            clasif = "JUNTA_MEDICA_SUGERIDA"
            rec = "Acumulación médica crítica (>=30 días). Remitir historia clínica a evaluación de Junta Médico-Laboral Militar."
        else:
            clasif = "SEGUIMIENTO_SANIDAD"
            rec = "Seguimiento médico ambulatorio continuo por Sección de Sanidad de la Unidad."

        resultados.append(AlertaSanidadItem(
            id_personal=p_id,
            cedula=cedula,
            nombre=nombre,
            total_dias_sanidad=total_dias,
            episodios=episodios,
            novedades=novedades or "SANIDAD",
            ultima_fecha=ultima_fecha or target_date,
            clasificacion=clasif,
            recomendacion=rec
        ))

    return resultados

# ====================================================================
# 3. PROYECCIÓN DE FUERZA DISPONIBLE (15 / 30 DÍAS)
# ====================================================================
def _parse_date_safe(val: Optional[str]) -> Optional[datetime]:
    if not val:
        return None
    val = val.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None

@router.get("/proyeccion", response_model=ProyeccionFuerzaData)
def get_proyeccion_fuerza(
    dias: int = Query(30, description="Días hacia adelante a proyectar"),
    fecha: Optional[str] = Query(None, description="Fecha base de cálculo"),
    db = Depends(get_db)
):
    """
    Estima la fuerza disponible proyectada a 7, 15 y 30 días calculando las reincorporaciones
    previstas de personal con fecha_final informada (permisos, vacaciones, incapacidades).
    """
    dias = int(_clean_param(dias, 30))
    cursor = db.cursor()
    target_date = _get_target_date(cursor, fecha)

    # 1. Obtener ID del reporte base
    cursor.execute("SELECT id FROM REPORTES WHERE fecha = %s;", (target_date,))
    rep_row = cursor.fetchone()
    if not rep_row:
        # Fallback al último
        cursor.execute("SELECT id, fecha FROM REPORTES ORDER BY fecha DESC LIMIT 1;")
        rep_row = cursor.fetchone()
        target_date = rep_row[1] if rep_row else target_date

    rep_id = rep_row[0] if rep_row else None
    if not rep_id:
        raise HTTPException(status_code=404, detail="No se encontraron reportes en la base de datos")

    # 2. Efectivo actual
    cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = %s;", (rep_id,))
    total_efectivo = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*) 
        FROM REGISTRO_PERSONAL rp
        JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad
        WHERE rp.id_reporte = %s AND sn.nombre IN ('AREA OPERACIONES', 'CDO UNIDAD');
    """, (rep_id,))
    disp_actual = cursor.fetchone()[0] or 0
    nov_actual = max(0, total_efectivo - disp_actual)
    pct_actual = round((disp_actual / total_efectivo * 100), 1) if total_efectivo > 0 else 0.0

    # 3. Militares en novedad con fecha_final conocida
    cursor.execute("""
        SELECT rp.id_personal, p.cedula, p.nombre, sn.nombre AS novedad, rp.fecha_final, rp.descripcion
        FROM REGISTRO_PERSONAL rp
        JOIN PERSONAL p ON p.id = rp.id_personal
        JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad
        WHERE rp.id_reporte = %s 
          AND rp.fecha_final IS NOT NULL 
          AND rp.fecha_final != ''
          AND sn.nombre NOT IN ('AREA OPERACIONES', 'CDO UNIDAD')
        ORDER BY rp.fecha_final ASC;
    """, (rep_id,))
    filas_movs = cursor.fetchall()

    base_dt = _parse_date_safe(target_date) or datetime.now()

    reinc_7 = 0
    reinc_15 = 0
    reinc_30 = 0
    detalle_movs: List[ProyeccionMovimiento] = []

    for p_id, cedula, nombre, novedad, f_fin, desc in filas_movs:
        dt_fin = _parse_date_safe(f_fin)
        if not dt_fin:
            continue

        delta_dias = (dt_fin - base_dt).days
        # Consideramos movimientos futuros o que vencen muy pronto (dentro de los próximos 'dias')
        if 0 <= delta_dias <= dias:
            if delta_dias <= 7:
                reinc_7 += 1
            if delta_dias <= 15:
                reinc_15 += 1
            if delta_dias <= 30:
                reinc_30 += 1

            detalle_movs.append(ProyeccionMovimiento(
                id_personal=p_id,
                cedula=cedula,
                nombre=nombre,
                novedad=novedad,
                fecha_fin=f_fin,
                dias_restantes=delta_dias,
                descripcion=desc
            ))

    detalle_movs.sort(key=lambda m: m.dias_restantes)

    # Proyección neta
    disp_7 = min(total_efectivo, disp_actual + reinc_7)
    disp_15 = min(total_efectivo, disp_actual + reinc_15)
    disp_30 = min(total_efectivo, disp_actual + reinc_30)

    pct_7 = round((disp_7 / total_efectivo * 100), 1) if total_efectivo > 0 else 0.0
    pct_15 = round((disp_15 / total_efectivo * 100), 1) if total_efectivo > 0 else 0.0
    pct_30 = round((disp_30 / total_efectivo * 100), 1) if total_efectivo > 0 else 0.0

    return ProyeccionFuerzaData(
        fecha_base=target_date,
        efectivo_actual={
            "total": total_efectivo,
            "disponibles": disp_actual,
            "novedades": nov_actual,
            "porcentaje": pct_actual
        },
        proyeccion_7_dias=ProyeccionHorizonte(
            estimados_disponibles=disp_7,
            porcentaje=pct_7,
            reincorporaciones=reinc_7,
            salidas_programadas=0
        ),
        proyeccion_15_dias=ProyeccionHorizonte(
            estimados_disponibles=disp_15,
            porcentaje=pct_15,
            reincorporaciones=reinc_15,
            salidas_programadas=0
        ),
        proyeccion_30_dias=ProyeccionHorizonte(
            estimados_disponibles=disp_30,
            porcentaje=pct_30,
            reincorporaciones=reinc_30,
            salidas_programadas=0
        ),
        detalle_movimientos=detalle_movs[:25]
    )

# ====================================================================
# 4. "EL PARTE DE LAS 06:00" (BOLETÍN Y RADIOGRAMA MILITAR)
# ====================================================================
@router.get("/parte-diario", response_model=ParteDiarioData)
def get_parte_diario(
    fecha: Optional[str] = Query(None, description="Fecha del parte diario (YYYY-MM-DD)"),
    db = Depends(get_db)
):
    """
    Consolida el Estado de Fuerza diario de la Unidad en formato formal castrense,
    con desglose de categorías y texto listo para radiograma o mensaje militar oficial.
    """
    cursor = db.cursor()
    target_date = _get_target_date(cursor, fecha)

    # 1. Obtener ID del reporte
    cursor.execute("SELECT id FROM REPORTES WHERE fecha = %s;", (target_date,))
    rep_row = cursor.fetchone()
    if not rep_row:
        cursor.execute("SELECT id, fecha FROM REPORTES ORDER BY fecha DESC LIMIT 1;")
        rep_row = cursor.fetchone()
        if rep_row:
            target_date = rep_row[1]

    if not rep_row:
        raise HTTPException(status_code=404, detail="No hay reportes disponibles para generar el parte diario")

    rep_id = rep_row[0]

    # 2. Conteo total y disponibles
    cursor.execute("SELECT COUNT(*) FROM REGISTRO_PERSONAL WHERE id_reporte = %s;", (rep_id,))
    total_efectivo = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT sn.nombre, COUNT(*)
        FROM REGISTRO_PERSONAL rp
        JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad
        WHERE rp.id_reporte = %s
        GROUP BY sn.nombre;
    """, (rep_id,))
    subnov_rows = cursor.fetchall()
    subnov_dict = {row[0]: row[1] for row in subnov_rows}

    cdo_unidad = subnov_dict.get('CDO UNIDAD', 0)
    area_ops = subnov_dict.get('AREA OPERACIONES', 0)
    total_disponibles = cdo_unidad + area_ops
    total_novedades = max(0, total_efectivo - total_disponibles)
    pct_disp = round((total_disponibles / total_efectivo * 100), 1) if total_efectivo > 0 else 0.0

    # 3. Categorización militar estándar
    cat_sanidad = (
        subnov_dict.get('INCAPACIDAD', 0) +
        subnov_dict.get('HOSPITALIZADOS', 0) +
        subnov_dict.get('TRATAMIENTO LESIHMANIASIS', 0)
    )
    cat_descanso = (
        subnov_dict.get('PERMISO', 0) +
        subnov_dict.get('VACACIONES', 0)
    )
    cat_servicio = (
        subnov_dict.get('COMISION DE SERVICIO', 0) +
        subnov_dict.get('CURSOS', 0) +
        subnov_dict.get('CURSO DE LEY', 0) +
        subnov_dict.get('CICLO CODE', 0) +
        subnov_dict.get('REENTREANAMIENTO', 0)
    )
    cat_admin = max(0, total_novedades - (cat_sanidad + cat_descanso + cat_servicio))

    # 4. Alertas resumidas de mando
    fatiga_alertas = get_alertas_fatiga(umbral=30, fecha=target_date, db=db)
    sanidad_alertas = get_alertas_sanidad(dias_min=15, fecha=target_date, db=db)

    top_fatiga = [
        {"nombre": f.nombre, "dias": f.dias_continuos, "alerta": f.nivel_alerta}
        for f in fatiga_alertas[:5]
    ]
    top_sanidad = [
        {"nombre": s.nombre, "dias": s.total_dias_sanidad, "novedad": s.novedades}
        for s in sanidad_alertas[:5]
    ]

    # 5. Formato del Radiograma Castrense
    radiograma = f"""======================================================================
REPUBLICA DE COLOMBIA - MINISTERIO DE DEFENSA NACIONAL
COMANDO GENERAL DE LAS FUERZAS MILITARES - EJERCITO NACIONAL
SEGUNDA DIVISION - QUINTA BRIGADA
BATALLON DE INFANTERIA N° 12 "GR. ALFONSO MANRIQUE REYES" (BIMEJ 12)
SECCION PERSONAL (S-1) // PARTE DIARIO DE ESTADO DE FUERZA
FECHA DEL PARTE: {target_date} // EMISIÓN: 06:00R
======================================================================
I. RESUMEN NUMERICO DE FUERZA:
   • EFECTIVO TOTAL DE LA UNIDAD : {total_efectivo} HOMBRES
   • EFECTIVO DISPONIBLE        : {total_disponibles} HOMBRES ({pct_disp}% OPERATIVIDAD)
   • PERSONAL EN NOVEDAD        : {total_novedades} HOMBRES ({round(100.0 - pct_disp, 1)}%)

II. DISPOSICION OPERACIONAL DE DISPONIBLES:
   • AREA DE OPERACIONES        : {area_ops} HOMBRES
   • COMANDO DE UNIDAD (CDO)    : {cdo_unidad} HOMBRES

III. DESGLOSE CLASIFICADO DE NOVEDADES:
   • SANIDAD MILITAR (INCAPACIDAD / HOSPITAL) : {cat_sanidad} HOMBRES
   • DESCANSO Y BIENESTAR (PERMISO / VACAC.)  : {cat_descanso} HOMBRES
   • SERVICIO E INSTRUCCION (COMISIÓN / CURSO): {cat_servicio} HOMBRES
   • ADMINISTRATIVAS / RETIROS / OTRAS       : {cat_admin} HOMBRES

IV. ALERTAS S-1 DE MANDO PROACTIVO:
   • PERSONAL EN LÍMITE DE FATIGA (>30 DÍAS) : {len(fatiga_alertas)} HOMBRES
   • CASOS CRÍTICOS SANIDAD (>15 DÍAS ACUM.) : {len(sanidad_alertas)} HOMBRES
======================================================================
OBSERVACIONES:
PARTE GENERADO AUTOMÁTICAMENTE POR EL SISTEMA OPERATIVO BIMEH
DIRECCIÓN SECCIÓN PERSONAL S-1 // BIMEJ 12
======================================================================"""

    desglose_subnov = [
        {"nombre": k, "cantidad": v}
        for k, v in sorted(subnov_dict.items(), key=lambda x: x[1], reverse=True)
    ]

    return ParteDiarioData(
        fecha=target_date,
        total_personal=total_efectivo,
        disponibles=total_disponibles,
        novedades=total_novedades,
        porcentaje_disponibilidad=pct_disp,
        disposicion={"area_operaciones": area_ops, "cdo_unidad": cdo_unidad},
        desglose_categorias={
            "sanidad": cat_sanidad,
            "descanso": cat_descanso,
            "servicio": cat_servicio,
            "administrativas": cat_admin
        },
        desglose_subnovedades=desglose_subnov,
        alertas_resumen={
            "total_fatiga_critica": len(fatiga_alertas),
            "total_sanidad_critica": len(sanidad_alertas),
            "top_casos_fatiga": top_fatiga,
            "top_casos_sanidad": top_sanidad
        },
        radiograma_texto=radiograma
    )

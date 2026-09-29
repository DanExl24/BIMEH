-- ====================================================================
-- BIMEH - MIGRACIÓN DE OPTIMIZACIÓN: ÍNDICES Y VISTAS ANALÍTICAS
-- Acelera consultas de joins y simplifica las consultas del Asistente IA
-- ====================================================================

-- 1. Habilitar extensión de trigramas para búsquedas ultra-rápidas de texto
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. Índices para acelerar búsquedas de personas por nombre y estado
CREATE INDEX IF NOT EXISTS idx_personal_nombre_trgm 
ON PERSONAL USING gin (UPPER(nombre) gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_personal_activos 
ON PERSONAL(id) 
WHERE fecha_retiro IS NULL OR fecha_retiro = '';

-- 3. Índices en Foreign Keys de REGISTRO_PERSONAL (Vitales para acelerar JOINs)
CREATE INDEX IF NOT EXISTS idx_rp_id_personal 
ON REGISTRO_PERSONAL(id_personal);

CREATE INDEX IF NOT EXISTS idx_rp_id_reporte 
ON REGISTRO_PERSONAL(id_reporte);

CREATE INDEX IF NOT EXISTS idx_rp_id_sub_novedad 
ON REGISTRO_PERSONAL(id_sub_novedad);

CREATE INDEX IF NOT EXISTS idx_reportes_fecha 
ON REPORTES(fecha);

CREATE INDEX IF NOT EXISTS idx_sub_novedades_nombre 
ON SUB_NOVEDADES(nombre);

-- ====================================================================
-- VISTAS SIMPLIFICADAS PARA EL ASISTENTE IA Y REPORTES
-- ====================================================================

-- Vista 1: Resumen de cada militar con su estado y total de novedades acumuladas
CREATE OR REPLACE VIEW v_personal_resumen AS
SELECT 
    p.id,
    p.cedula,
    p.nombre,
    CASE 
        WHEN (p.fecha_retiro IS NULL OR p.fecha_retiro = '') THEN 'ACTIVO' 
        ELSE 'RETIRADO' 
    END AS estado,
    p.fecha_retiro,
    COUNT(rp.id) AS total_novedades_historicas
FROM PERSONAL p
LEFT JOIN REGISTRO_PERSONAL rp ON rp.id_personal = p.id
GROUP BY p.id, p.cedula, p.nombre, p.fecha_retiro;

-- Vista 2: Detalle unificado de novedades diarias por militar
CREATE OR REPLACE VIEW v_novedades_detalle AS
SELECT 
    rp.id AS id_registro,
    p.cedula,
    p.nombre,
    CASE 
        WHEN (p.fecha_retiro IS NULL OR p.fecha_retiro = '') THEN 'ACTIVO' 
        ELSE 'RETIRADO' 
    END AS estado,
    r.fecha AS fecha_reporte,
    COALESCE(sn.nombre, 'SIN NOVEDAD') AS novedad,
    rp.descripcion,
    rp.fecha_inicio,
    rp.fecha_final
FROM REGISTRO_PERSONAL rp
JOIN PERSONAL p ON p.id = rp.id_personal
JOIN REPORTES r ON r.id = rp.id_reporte
LEFT JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad;

-- Vista 3: Métricas consolidadas por tipo de novedad
CREATE OR REPLACE VIEW v_conteo_novedades AS
SELECT 
    COALESCE(sn.nombre, 'SIN NOVEDAD') AS novedad,
    COUNT(rp.id) AS total_dias_registrados,
    COUNT(DISTINCT rp.id_personal) AS total_personal_afectado
FROM REGISTRO_PERSONAL rp
JOIN SUB_NOVEDADES sn ON sn.id = rp.id_sub_novedad
GROUP BY sn.nombre;

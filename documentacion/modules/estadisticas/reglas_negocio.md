# Reglas de Negocio — Módulo de Estadísticas (`estadisticas`)

---

## 📈 1. Reglas de Agregación y Métricas

### RN-STAT-001
- **Identificador**: `RN-STAT-001`
- **Descripción**: En el cálculo del Top 15 de personal con más novedades acumuladas, se deben filtrar y excluir obligatoriamente las subnovedades de disponibilidad regular (`sn.nombre NOT IN ('CDO UNIDAD', 'AREA OPERACIONES')`).
- **Motivo**: Evitar que los días de servicio activo ordinario sean contabilizados erróneamente como novedades o ausencias operativas.
- **Módulos afectados**: `estadisticas`.
- **Archivos donde se implementa**: [`backend/app/routers/stats.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/stats.py) (Líneas 24–35), `frontend/src/utils/personal.utils.ts`.
- **Endpoints relacionados**: `GET /api/stats/ranking`
- **Historias de usuario relacionadas**: [HU-STAT-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/historias_usuario.md#hu-stat-001)

---

### RN-STAT-002
- **Identificador**: `RN-STAT-002`
- **Descripción**: La agrupación por subnovedad en `global_rank` realiza un conteo absoluto de filas en `REGISTRO_PERSONAL` agrupado por `id_sub_novedad`, ordenado de mayor a menor frecuencia (`ORDER BY total_dias DESC`).
- **Motivo**: Identificar la volumetría histórica total de cada contingencia en la historia de la unidad.
- **Módulos afectados**: `estadisticas`.
- **Archivos donde se implementa**: [`backend/app/routers/stats.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/stats.py) (Líneas 14–21), `frontend/src/features/estadisticas/views/EstadisticasView.vue`.
- **Endpoints relacionados**: `GET /api/stats/ranking`
- **Historias de usuario relacionadas**: [HU-STAT-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/historias_usuario.md#hu-stat-001)

---

### RN-STAT-003
- **Identificador**: `RN-STAT-003`
- **Descripción**: En la construcción del Heatmap mensual, si un integrante registra `fecha_retiro` y la fecha de la columna evaluada es mayor o igual a dicha fecha (`d >= f_retiro`), el estado asignado en la celda es forzosamente `"RETIRADO"`. Si no existe registro para ese día y no está retirado, el estado es `"N/A"`.
- **Motivo**: Asegurar la veracidad histórica evitando pintar como ausentes injustificados a integrantes que ya causaron baja oficial de la unidad militar.
- **Módulos afectados**: `estadisticas`, `personal`, `cronologia`.
- **Archivos donde se implementa**: [`backend/app/routers/stats.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/stats.py) (Líneas 88–98).
- **Endpoints relacionados**: `GET /api/stats/heatmap`
- **Historias de usuario relacionadas**: [HU-STAT-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/historias_usuario.md#hu-stat-002)

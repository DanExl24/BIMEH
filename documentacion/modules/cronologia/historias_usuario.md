# Historias de Usuario — Módulo de Cronología (`cronologia`)

---

# HU-CRON-001

## Historia
**Como** oficial de servicio o analista de personal  
**Quiero** seleccionar un mes y ver el calendario interactivo con el porcentaje de disponibilidad de cada día  
**Para** identificar visualmente qué días tuvieron caídas críticas en la fuerza disponible de la unidad.

## Descripción
En la vista `/cronologia` (`CronologiaView.vue`), el usuario selecciona un mes activo. El componente `CronologiaActivityCalendar.vue` consume el composable `useCronologiaData.ts` y el endpoint `/api/reportes/calendario?mes=...` a través de `cronologia.service.ts`, renderizando cada fecha del mes con su indicador de disponibilidad porcentual, total de efectivos, disponibles y novedades. Al hacer clic en un día del calendario, la tabla inferior se actualiza automáticamente para mostrar el detalle de ese día.

## Criterios de Aceptación
- El endpoint `/api/reportes/calendario` retorna un arreglo con los días ordenados cronológicamente.
- Cada día incluye: `fecha`, `disponibilidad` (porcentaje con 1 decimal), `total_personal`, `disponibles` y `novedades`.
- Los días con alta disponibilidad ($\ge 80\%$) se identifican con badges verdes, los de media ($50\% - 79\%$) en amarillo/naranja y los de baja ($< 50\%$) en rojo.
- Al hacer clic sobre cualquier celda del día en el calendario, se actualiza la fecha seleccionada en `dateStore.ts` y se recarga la tabla de personal de esa fecha.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-CRON-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/reglas_negocio.md#rn-cron-001), [RN-CRON-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/reglas_negocio.md#rn-cron-002)
- **Endpoints relacionados**: `GET /api/reportes/calendario`
- **Componentes frontend relacionados**: `frontend/src/features/cronologia/views/CronologiaView.vue`, `frontend/src/features/cronologia/components/CronologiaActivityCalendar.vue`, `frontend/src/features/cronologia/composables/useCronologiaData.ts`, `frontend/src/features/cronologia/services/cronologia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/personal.py` (`get_calendario`)

---

# HU-CRON-002

## Historia
**Como** usuario del sistema  
**Quiero** consultar la tabla detallada del reporte diario con filtros por texto y por subnovedad  
**Para** verificar la situación particular de cualquier efectivo en la fecha seleccionada.

## Descripción
El componente `CronologiaDailyReportTable.vue` lista a todos los integrantes presentes en el reporte de la fecha activa. Permite filtrar instantáneamente por número de cédula o nombre mediante un campo de texto, o filtrar por una subnovedad específica a través de un menú desplegable dinámico.

## Criterios de Aceptación
- La consulta a `/api/reportes/dia?fecha=YYYY-MM-DD` retorna la lista completa ordenada alfabéticamente por nombre (`ORDER BY p.nombre ASC`).
- Cada fila contiene: `cedula`, `nombre`, `subnovedad`, `descripcion`, `desde` y `hasta`.
- El filtro de texto en frontend busca en tiempo real en cédula y nombre sin recargar la página.
- El selector de subnovedades permite aislar rápidamente a quienes están en una situación determinada (ej. solo personal en `"CDO UNIDAD"` o `"COMISION"`).
- Si la fecha seleccionada no tiene reporte en la base de datos, la tabla muestra un mensaje informativo `"No hay registros para la fecha seleccionada"`.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-CRON-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/reglas_negocio.md#rn-cron-003)
- **Endpoints relacionados**: `GET /api/reportes/dia`
- **Componentes frontend relacionados**: `frontend/src/features/cronologia/components/CronologiaDailyReportTable.vue`, `frontend/src/features/cronologia/services/cronologia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/personal.py` (`get_reporte_dia`)

---

# HU-CRON-003

## Historia
**Como** comandante de unidad  
**Quiero** visualizar la matriz mensual completa de todos los integrantes de la unidad  
**Para** auditar la continuidad del servicio de toda la fuerza en un único cuadro de mando mensual.

## Descripción
El componente `CronologiaMonthlyHeatmapMatrix.vue` permite desplegar la matriz del mes completo donde las filas representan a cada integrante y las columnas los días del mes, mostrando de forma compacta el estado de cada persona a lo largo de todo el mes.

## Criterios de Aceptación
- Cada celda muestra la letra del estado (`D` para disponible, `N` para novedad, `R` para retirado, `-` para sin reporte).
- Al situar el cursor sobre una celda, se muestra un tooltip flotante con el detalle de la subnovedad y la descripción registrada.
- Incluye un buscador en la tabla para filtrar integrantes dentro de la matriz.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-CRON-004](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/reglas_negocio.md#rn-cron-004)
- **Endpoints relacionados**: `GET /api/stats/heatmap`
- **Componentes frontend relacionados**: `frontend/src/features/cronologia/components/CronologiaMonthlyHeatmapMatrix.vue`, `frontend/src/features/cronologia/services/cronologia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/stats.py` (`get_stats_heatmap`)

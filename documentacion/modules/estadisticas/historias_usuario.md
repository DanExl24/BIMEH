# Historias de Usuario — Módulo de Estadísticas (`estadisticas`)

---

# HU-STAT-001

## Historia
**Como** comandante o analista de personal  
**Quiero** consultar los rankings consolidados globales de subnovedades y el Top de integrantes con más novedades  
**Para** evaluar qué contingencias operacionales consumen más horas-hombre y detectar efectivos con acumulados atípicos de ausencias.

## Descripción
Al acceder a `/estadisticas` (`EstadisticasView.vue`), el sistema consulta `/api/stats/ranking` mediante `estadisticas.service.ts`. El backend genera dos agrupaciones estadísticas:
1. **Ranking Global de Subnovedades**: Conteo total de días acumulados por cada subnovedad en toda la base de datos, ordenado descendente.
2. **Top 15 de Personal con Más Días de Novedad**: Lista de los 15 integrantes que registran el mayor número de días en estados no disponibles.

## Criterios de Aceptación
- El ranking global incluye todas las subnovedades registradas con su sumatoria de días.
- El ranking de personas excluye estrictamente las subnovedades de disponibilidad (`"CDO UNIDAD"` y `"AREA OPERACIONES"`).
- Se limita el listado de personal a los primeros 15 registros con mayor acumulado (`LIMIT 15`).
- Los datos se visualizan en gráficos de barras y tarjetas comparativas con porcentajes de participación.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-STAT-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/reglas_negocio.md#rn-stat-001), [RN-STAT-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/reglas_negocio.md#rn-stat-002)
- **Endpoints relacionados**: `GET /api/stats/ranking`
- **Componentes frontend relacionados**: `frontend/src/features/estadisticas/views/EstadisticasView.vue`, `frontend/src/features/estadisticas/services/estadisticas.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/stats.py` (`get_stats_rankings`)

---

# HU-STAT-002

## Historia
**Como** planificador de operaciones  
**Quiero** visualizar la matriz Heatmap global de todo el personal durante el mes  
**Para** auditar la distribución de descansos, permisos y comisiones de toda la unidad de manera simultánea.

## Descripción
En la sección inferior del módulo de estadísticas, se presenta la matriz general del mes. Cada fila corresponde a un efectivo de la unidad y cada columna a un día calendario del mes. Los estados se codifican cromáticamente y se acompañan de contadores de días totales por fila.

## Criterios de Aceptación
- El endpoint `/api/stats/heatmap?mes=...` retorna un objeto con `fechas` (días del mes) y `data` (lista de integrantes con su arreglo de `estados`).
- Los estados posibles por día son:
  - Nombre de la subnovedad correspondiente si el integrante tuvo reporte ese día.
  - `"RETIRADO"` si la fecha del reporte es posterior o igual a la `fecha_retiro` del integrante.
  - `"N/A"` si el integrante no tuvo registro en ese reporte o no hubo reporte.
- La interfaz implementa scroll horizontal fluido y búsqueda rápida por nombre o cédula.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-STAT-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/reglas_negocio.md#rn-stat-003)
- **Endpoints relacionados**: `GET /api/stats/heatmap`
- **Componentes frontend relacionados**: `frontend/src/features/estadisticas/views/EstadisticasView.vue`, `frontend/src/features/cronologia/services/cronologia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/stats.py` (`get_stats_heatmap`)

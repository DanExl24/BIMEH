# Historias de Usuario — Módulo de Dashboard Operacional (`dashboard`)

---

# HU-DASH-001

## Historia
**Como** comandante de unidad o directivo de personal  
**Quiero** visualizar las tarjetas de KPIs del estado de fuerza diario  
**Para** conocer de manera instantánea el total de efectivos, el personal disponible, el personal en novedades y el porcentaje de disponibilidad operativa.

## Descripción
El usuario accede a la vista principal del Dashboard. El sistema consulta las métricas de estado de fuerza para la fecha activa (o el mes/día seleccionado). Si no se proporciona ningún parámetro temporal, el sistema toma por defecto la fecha del reporte más reciente registrado en la base de datos. Se presentan tarjetas interactivas con valores consolidados y cálculos porcentuales precisos con un decimal.

## Criterios de Aceptación
- Si no se especifica fecha, se debe cargar automáticamente la fecha más reciente de la tabla `REPORTES`.
- Se consideran **Disponibles** únicamente aquellos integrantes cuya subnovedad asignada sea `"CDO UNIDAD"` o `"AREA OPERACIONES"`.
- El total de personal en novedad se calcula como: $\text{Novedades} = \text{Total Personal} - \text{Disponibles}$.
- El porcentaje de disponibilidad se calcula como: $\text{Disponibilidad (\%)} = \left(\frac{\text{Disponibles}}{\text{Total Personal}} \times 100\right)$ redondeado a 1 decimal.
- Si no existen reportes para el filtro seleccionado, todas las métricas deben retornar `0` y disponibilidad `0.0`.
- Se debe mostrar una tarjeta con la cantidad neta de **Cambios vs Ayer**, calculada a partir de las transiciones de estado de cada integrante respecto al reporte inmediatamente anterior.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-DASH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/reglas_negocio.md#rn-dash-001), [RN-DASH-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/reglas_negocio.md#rn-dash-002), [RN-DASH-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/reglas_negocio.md#rn-dash-003)
- **Endpoints relacionados**: `GET /api/dashboard/kpis`, `GET /api/fechas`
- **Componentes frontend relacionados**: `frontend/src/views/DashboardView.vue`, `frontend/src/components/dashboard/DashboardKpis.vue`
- **Controllers/Services relacionados**: `backend/app/routers/dashboard.py` (`get_kpis`, `get_available_dates`)

---

# HU-DASH-002

## Historia
**Como** analista de personal  
**Quiero** consultar la lista clasificada de cambios y transiciones de estado operacional  
**Para** identificar quiénes entraron a novedades hoy, quiénes volvieron a estar disponibles y qué personal cambió de una novedad a otra respecto al día anterior.

## Descripción
El panel inferior del Dashboard presenta la auditoría de transiciones operacionales. Compara el reporte de la fecha seleccionada contra el reporte cronológicamente anterior. Clasifica las diferencias en tres categorías:
1. **Entraron a Novedades**: Integrantes que estaban disponibles y pasaron a un estado de novedad (o ingresaron como nuevo registro no disponible).
2. **Volvieron a Disponibles**: Integrantes que estaban en novedad y pasaron a estado disponible (`"CDO UNIDAD"` o `"AREA OPERACIONES"`).
3. **Otros Cambios**: Modificaciones entre diferentes tipos de novedad (ej. de `"PERMISO"` a `"VACACIONES"`), o bajas/retiros.

## Criterios de Aceptación
- La comparación se realiza contra el reporte inmediatamente previo en el tiempo (`fecha < fecha_actual ORDER BY fecha DESC LIMIT 1`).
- La respuesta agrupa los resultados en tres listas: `entraron_novedades`, `volvieron_disponibles` y `otros_cambios`.
- Cada elemento retornado debe contener: `cedula`, `nombre`, `novedad_anterior`, `novedad_nueva` y `fecha`.
- Se limitan los resultados a un máximo de 150 elementos por categoría para optimizar el renderizado del DOM.
- Si no existe un reporte previo registrado, las listas retornan vacías.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-DASH-004](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/reglas_negocio.md#rn-dash-004)
- **Endpoints relacionados**: `GET /api/dashboard/cambios`
- **Componentes frontend relacionados**: `frontend/src/components/dashboard/DashboardCambiosList.vue`
- **Controllers/Services relacionados**: `backend/app/routers/dashboard.py` (`get_cambios`)

---

# HU-DASH-003

## Historia
**Como** comandante  
**Quiero** visualizar gráficos analíticos de evolución temporal y distribución de novedades  
**Para** analizar patrones de disponibilidad a lo largo del mes y detectar qué novedades concentran la mayor afectación de fuerza.

## Descripción
El Dashboard integra gráficos de Apache ECharts:
- **Gráfico de Evolución**: Muestra una curva de disponibilidad porcentual día a día para el mes seleccionado, permitiendo identificar caídas drásticas de personal.
- **Gráfico de Distribución (Dona)**: Muestra la proporción porcentual y absoluta de cada subnovedad registrada.
- **Gráfico de Novedades Frecuentes**: Ranking de barras con los tipos de novedad más recurrentes (excluyendo la disponibilidad regular).

## Criterios de Aceptación
- El gráfico de evolución debe ordenar cronológicamente los días del mes y mostrar tooltip interactivo con: total personal, disponibles, novedades y porcentaje de disponibilidad.
- El gráfico de distribución debe categorizar cada elemento como `"DISPONIBLE"` o `"NOVEDAD"`.
- Las consultas responden de forma reactiva cuando el usuario cambia el selector de mes o fecha en la barra superior.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-DASH-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/reglas_negocio.md#rn-dash-002), [RN-DASH-005](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/reglas_negocio.md#rn-dash-005)
- **Endpoints relacionados**: `GET /api/dashboard/evolucion`, `GET /api/dashboard/distribucion`, `GET /api/dashboard/novedades-frecuentes`
- **Componentes frontend relacionados**: `frontend/src/components/dashboard/DashboardEvolutionChart.vue`, `frontend/src/components/dashboard/DashboardDistribucionChart.vue`, `frontend/src/components/dashboard/DashboardNovedadesChart.vue`
- **Controllers/Services relacionados**: `backend/app/routers/dashboard.py` (`get_evolucion`, `get_distribucion`, `get_novedades_frecuentes`)

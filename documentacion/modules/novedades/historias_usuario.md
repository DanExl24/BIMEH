# Historias de Usuario — Módulo de Gestión y Búsqueda de Novedades (`novedades`)

---

# HU-NOV-001

## Historia
**Como** comandante o analista de personal  
**Quiero** seleccionar cualquier novedad del catálogo y ver instantáneamente qué integrantes la han tenido y cuántos días acumula  
**Para** tener un panorama inmediato de la fuerza operativa afectada por cada tipo de novedad.

## Descripción
Al acceder al módulo de Gestión de Novedades (`/novedades`), el usuario dispone de un selector central con el catálogo completo de subnovedades, acompañado de botones de acceso rápido a las novedades más frecuentes (VACACIONES, INCAPACIDAD, PERMISO, AREA OPERACIONES, etc.). Al hacer clic en cualquiera de ellas, el sistema actualiza de manera inmediata los indicadores clave (total de registros/días, número de efectivos únicos afectados, relación de activos vs retirados y rango temporal) y despliega la tabla con los registros correspondientes.

## Criterios de Aceptación
- **Criterio 1**: El endpoint `GET /api/novedades/catalogo` debe retornar todas las subnovedades registradas con su ID, nombre, conteo total de registros en `REGISTRO_PERSONAL` y conteo de personal único.
- **Criterio 2**: El usuario puede alternar libremente entre *"TODAS LAS NOVEDADES"* o una novedad puntual.
- **Criterio 3**: La respuesta de consulta debe procesarse en menos de 200 ms gracias al índice `idx_registro_personal_subnovedad`.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-NOV-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/reglas_negocio.md#rn-nov-001), [RN-NOV-002](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/reglas_negocio.md#rn-nov-002)
- **Endpoints relacionados**: `GET /api/novedades/catalogo`, `GET /api/novedades/consulta`
- **Componentes frontend relacionados**: `frontend/src/features/novedades/views/NovedadesView.vue`, `frontend/src/features/novedades/components/NovedadKpis.vue`

---

# HU-NOV-002

## Historia
**Como** administrador o auditor del sistema  
**Quiero** filtrar los registros de novedades por mes operacional, rango de fechas específico, estado de personal y búsqueda por nombre o cédula  
**Para** responder preguntas operativas puntuales como: *¿qué integrantes tuvieron incapacidad en el mes de marzo?* o *¿en qué fechas específicas estuvo de permiso este efectivo?*

## Descripción
En la barra de filtros interactivos, el usuario puede combinar simultáneamente:
1. Selección de mes operacional (ej. ENERO, FEBRERO, MARZO, etc.).
2. Rango de fechas (*Fecha Desde* y *Fecha Hasta* con selector de calendario).
3. Estado del integrante (*TODOS*, *ACTIVO*, *RETIRADO*).
4. Campo de búsqueda de texto con *debounce* automático para filtrar por número de cédula o nombre/apellidos.

El sistema recalcula los KPIs en tiempo real para reflejar exactamente el subconjunto de datos filtrado.

## Criterios de Aceptación
- **Criterio 1**: Si se selecciona un mes, la consulta restringe los reportes a las fechas pertenecientes a dicho mes registradas en la base de datos.
- **Criterio 2**: Si se define un rango de fechas (`fecha_inicio` / `fecha_fin`), se valida que el reporte cumpla `r.fecha >= fecha_inicio` y/o `r.fecha <= fecha_fin`.
- **Criterio 3**: Si se busca por texto, la condición evalúa coincidencia parcial insensible a mayúsculas/minúsculas tanto en `p.cedula` como en `p.nombre`.
- **Criterio 4**: Se provee un botón para restablecer todos los filtros a sus valores predeterminados con un solo clic.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-NOV-003](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/reglas_negocio.md#rn-nov-003), [RN-NOV-004](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/reglas_negocio.md#rn-nov-004)
- **Endpoints relacionados**: `GET /api/novedades/consulta`
- **Componentes frontend relacionados**: `frontend/src/features/novedades/views/NovedadesView.vue`, `frontend/src/features/novedades/services/novedades.service.ts`

---

# HU-NOV-003

## Historia
**Como** evaluador de personal  
**Quiero** consultar la lista de novedades con paginación fluida y acceder directamente al expediente individual del integrante  
**Para** inspeccionar el contexto completo de servicio y antecedentes del efectivo sin perder mi posición de búsqueda.

## Descripción
Los registros coincidentes se presentan en una tabla ordenada cronológicamente de forma descendente por fecha de reporte. Cada fila detalla: número de cédula, apellidos y nombres, badge de estado (`ACTIVO` / `RETIRADO`), nombre de la subnovedad, fecha del reporte, rango de fechas asignado (desde - hasta), observación o descripción, y un botón de enlace directo que abre el expediente del integrante en `/personal/:cedula`.

## Criterios de Aceptación
- **Criterio 1**: Los resultados se paginan en el servidor mediante `page` y `limit` (con opciones de 25, 50 y 100 registros por página).
- **Criterio 2**: El usuario puede navegar a páginas anteriores, siguientes o seleccionar páginas numéricas visibles.
- **Criterio 3**: Al presionar el botón de expediente, la navegación preserva la integridad del historial de navegación.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-NOV-005](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/reglas_negocio.md#rn-nov-005)
- **Endpoints relacionados**: `GET /api/novedades/consulta`
- **Componentes frontend relacionados**: `frontend/src/features/novedades/views/NovedadesView.vue`

---

# HU-NOV-004

## Historia
**Como** oficial de personal u operaciones  
**Quiero** exportar los resultados de la consulta a formatos Excel (.xlsx) y PDF oficial  
**Para** presentar informes de control fidedignos, anexar minutas operativas y compartir auditorías con los mandos de la unidad.

## Descripción
En la parte superior de la vista se ubican los botones **"Exportar Excel"** y **"Exportar PDF"**. Al hacer clic, el sistema genera el reporte correspondiente utilizando el mismo conjunto de filtros aplicado en pantalla. El documento generado contiene la cabecera oficial del BIMEJ 12, resumen detallado de los filtros seleccionados, totales de registros y la tabla de resultados.

## Criterios de Aceptación
- **Criterio 1**: El reporte Excel incluye metadatos de los filtros activos (novedad, mes, rango, estado, total registros) y filas tabulares con bordes, anchos ajustados y colores institucionales.
- **Criterio 2**: El reporte PDF se genera en formato horizontal (*landscape*), con diseño vectorial limpio, estilo tipográfico oficial y numeración.
- **Criterio 3**: Durante la descarga se muestra un estado visual de carga (`Generando...`) en el botón correspondiente, impidiendo envíos duplicados concurrentes.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-NOV-006](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/reglas_negocio.md#rn-nov-006)
- **Endpoints relacionados**: `GET /api/novedades/exportar/excel`, `GET /api/novedades/exportar/pdf`
- **Componentes frontend relacionados**: `frontend/src/features/novedades/views/NovedadesView.vue`, `frontend/src/features/novedades/services/novedades.service.ts`

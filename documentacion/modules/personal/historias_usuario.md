# Historias de Usuario — Módulo de Personal (`personal`)

---

# HU-PERS-001

## Historia
**Como** usuario del sistema  
**Quiero** buscar integrantes del personal mediante un campo de autocompletado en tiempo real por cédula o nombre  
**Para** localizar rápidamente la ficha y expediente de un integrante sin navegar por cientos de registros.

## Descripción
El usuario ingresa al módulo de Personal (`/personal`). En la barra de búsqueda escribe al menos 2 caracteres. El frontend, mediante el composable `usePersonalAutocomplete.ts` y el servicio `personal.service.ts`, realiza una consulta inmediata al endpoint `/api/personal/buscar?q=...`. El backend busca por coincidencia parcial insensible a mayúsculas/minúsculas tanto en el número de cédula como en el nombre completo, retornando hasta un máximo de 50 coincidencias junto con el estado del personal (`ACTIVO` o `RETIRADO`).

## Criterios de Aceptación
- La búsqueda requiere un mínimo de 2 caracteres (`min_length=2`); de lo contrario, el backend retorna `HTTP 422 Unprocessable Entity`.
- La consulta busca en la base de datos coincidencia con `CAST(cedula AS TEXT) LIKE %Q%` o `nombre LIKE %Q%`.
- El resultado incluye: `cedula`, `nombre`, `estado` (`'ACTIVO'` si `fecha_retiro` es nula, `'RETIRADO'` si tiene fecha) y `fecha_retiro`.
- Se limita a un máximo de 50 registros por llamada para garantizar respuesta en menos de 100ms.
- Al hacer clic en un resultado de la lista o tarjeta, el sistema navega a la ruta `/personal/:cedula`.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-PERS-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/reglas_negocio.md#rn-pers-001), [RN-PERS-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/reglas_negocio.md#rn-pers-002)
- **Endpoints relacionados**: `GET /api/personal/buscar`
- **Componentes frontend relacionados**: `frontend/src/features/personal/views/PersonalView.vue`, `frontend/src/features/personal/composables/usePersonalAutocomplete.ts`, `frontend/src/features/personal/services/personal.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/personal.py` (`buscar_personal`)

---

# HU-PERS-002

## Historia
**Como** comandante o analista de talento humano  
**Quiero** ver la ficha técnica y expediente integral del integrante  
**Para** analizar sus porcentajes históricos de disponibilidad, total de días reportados, promedio de duración de rachas de novedades y su última novedad registrada.

## Descripción
Al acceder a `/personal/:cedula` (`PersonalDetalleView.vue`), el composable `usePersonalProfile.ts` orquesta las solicitudes para recuperar la información consolidada del integrante. Calcula el porcentaje total de tiempo que ha estado disponible (`"CDO UNIDAD"` o `"AREA OPERACIONES"`) frente al tiempo en novedades, y ejecuta un algoritmo de análisis secuencial para determinar el promedio en días de duración de cada racha ininterrumpida de novedad.

## Criterios de Aceptación
- Si la cédula no existe en la base de datos, el backend debe retornar `HTTP 404 Not Found` con el mensaje `"Personal no encontrado."`.
- Si el integrante no posee registros operacionales (`total_dias = 0`), todos los indicadores deben retornar en `0` y fechas en `null` de forma segura.
- El cálculo de rachas de novedades agrupa días consecutivos en estado no disponible y obtiene la media aritmética redondeada a un decimal (`promedio_duracion_novedades`).
- La respuesta retorna: `cedula`, `nombre`, `estado`, `fecha_retiro`, `primer_registro_fecha`, `ultimo_registro_fecha`, `total_dias`, `tiempo_disponible_pct`, `tiempo_novedades_pct`, `total_novedades`, `promedio_duracion_novedades`, `ultima_novedad`.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-PERS-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/reglas_negocio.md#rn-pers-003), [RN-PERS-004](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/reglas_negocio.md#rn-pers-004)
- **Endpoints relacionados**: `GET /api/personal/{cedula}`
- **Componentes frontend relacionados**: `frontend/src/features/personal/views/PersonalDetalleView.vue`, `frontend/src/features/personal/components/PersonalHeaderCard.vue`, `frontend/src/features/personal/components/PersonalKpiGrid.vue`, `frontend/src/features/personal/composables/usePersonalProfile.ts`
- **Controllers/Services relacionados**: `backend/app/routers/personal.py` (`get_personal_detalle`)

---

# HU-PERS-003

## Historia
**Como** evaluador de personal  
**Quiero** visualizar el mapa de calor (Heatmap) mensual y anual de disponibilidad del integrante  
**Para** identificar visualmente patrones de inactividad, licencias o ausencias recurrentes en días específicos.

## Descripción
El expediente individual incluye el componente interactivo `PersonalHeatmapMatrix.vue`. Permite alternar entre:
1. **Vista Mensual**: Grilla de hasta 31 días del mes seleccionado.
2. **Vista Anual**: Matriz completa de los 12 meses del año con todas las celdas codificadas por color:
   - **Verde (D)**: Disponible (`"CDO UNIDAD"` o `"AREA OPERACIONES"`).
   - **Naranja (N)**: En Novedad (permiso, vacaciones, etc.).
   - **Gris (-)**: Sin reporte registrado para ese día en el sistema.
   - **Rojo (R)**: En condición de Retirado (fecha posterior a `fecha_retiro`).

## Criterios de Aceptación
- Al pasar el cursor sobre cada celda, debe mostrarse un tooltip con la fecha exacta, la subnovedad y la descripción u observación si existe.
- Permite cambiar interactivamente entre la vista de mapa de calor mensual, mapa de calor anual y la tabla detallada de novedades.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-PERS-005](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/reglas_negocio.md#rn-pers-005)
- **Endpoints relacionados**: `GET /api/personal/{cedula}/historial`
- **Componentes frontend relacionados**: `frontend/src/features/personal/components/PersonalHeatmapMatrix.vue`, `frontend/src/features/personal/components/PersonalTimeline.vue`, `frontend/src/features/personal/composables/usePersonalTimelineFilters.ts`
- **Controllers/Services relacionados**: `backend/app/routers/personal.py` (`get_personal_historial`)

---

# HU-PERS-004

## Historia
**Como** secretario de personal  
**Quiero** abrir un modal de exportación individual desde la ficha del integrante  
**Para** generar y descargar su historial de novedades en Excel, CSV o PDF filtrado por rango o subnovedad específica.

## Descripción
En la parte superior de la ficha del integrante (`PersonalHeaderCard.vue`), el botón "Generar Reporte" despliega el modal compartido `ReportGenerationModal.vue`. El usuario puede configurar el formato (Excel, CSV, PDF), seleccionar el tipo de reporte (Historial Completo o Heatmap Mensual), elegir el mes y opcionalmente filtrar por una subnovedad en particular (ej. solo "INCAPACIDAD MÉDICA").

## Criterios de Aceptación
- El modal permite seleccionar los formatos: Excel (`.xlsx`), CSV (`.csv`) y PDF (`.pdf`).
- Si se selecciona una subnovedad, el reporte generado incluirá únicamente los registros que coincidan con dicho estado.
- La descarga se ejecuta de forma asíncrona mediante streaming binario sin recargar la página.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-PERS-006](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/reglas_negocio.md#rn-pers-006)
- **Endpoints relacionados**: `GET /api/exportar/excel`, `GET /api/exportar/csv`, `GET /api/exportar/pdf`
- **Componentes frontend relacionados**: `frontend/src/components/modals/ReportGenerationModal.vue`, `frontend/src/features/personal/components/PersonalHeaderCard.vue`, `frontend/src/features/reportes/services/reportes.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/exportar.py`

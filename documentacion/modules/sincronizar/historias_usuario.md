# Historias de Usuario — Módulo de Sincronización e Ingesta (`sincronizar`)

---

# HU-SYNC-001

## Historia
**Como** usuario con rol administrativo  
**Quiero** subir un archivo Excel o JSON mediante Drag-and-Drop  
**Para** cargar reportes diarios o mensuales en la base de datos sin depender de conexiones a servicios externos.

## Descripción
El usuario accede a `/sincronizar` y selecciona la pestaña "Archivo Local". Arrastra un archivo `.xlsx` o `.json` al área de carga (`SyncFileDropzone.vue`). El sistema valida que el archivo contenga las columnas mandatorias (`CEDULA`, `APELLIDOS Y NOMBRES`, `SUBNOVEDAD`), detecta si ya existen reportes previos para las fechas incluidas y, de no existir conflictos (o si se marca sobrescritura), inserta los registros en la base de datos.

## Criterios de Aceptación
- Solo se aceptan extensiones `.xlsx`, `.xls` y `.json`. Cualquier otro formato es rechazado con `HTTP 400 Bad Request`.
- Debe validar la presencia de las cabeceras requeridas en las primeras 15 filas del archivo.
- Los números de cédula deben limpiarse de comas, espacios y decimales flotantes (`int(float(str(val)))`), ignorando valores menores o iguales a cero.
- Si no existe el integrante en la tabla `PERSONAL` o la subnovedad en `SUB_NOVEDADES`, el sistema los crea automáticamente sobre la marcha (*get or create*).
- Si la fecha ya existe en la base de datos y `overwrite=False`, el endpoint retorna `status="conflict"` con la lista de fechas duplicadas para confirmación del usuario.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`
- **Reglas de negocio relacionadas**: [RN-SYNC-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/reglas_negocio.md#rn-sync-001), [RN-SYNC-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/reglas_negocio.md#rn-sync-002), [RN-SYNC-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/reglas_negocio.md#rn-sync-003)
- **Endpoints relacionados**: `POST /api/sincronizar/cargar`
- **Componentes frontend relacionados**: `frontend/src/views/SincronizarView.vue`, `frontend/src/components/sincronizar/SyncFileDropzone.vue`, `frontend/src/components/sincronizar/SyncConflictAlert.vue`
- **Controllers/Services relacionados**: `backend/app/routers/sincronizar.py` (`cargar_reporte`)

---

# HU-SYNC-002

## Historia
**Como** administrador de talento humano  
**Quiero** sincronizar de forma remota los reportes desde Google Drive en modo día único, multi-día o mes completo  
**Para** incorporar las últimas modificaciones y novedades operacionales registradas por las subunidades en la nube.

## Descripción
En la pestaña "Google Drive", el usuario selecciona el alcance de sincronización:
- **Día Único**: Sincroniza únicamente la fecha seleccionada.
- **Multi-día**: Selecciona múltiples fechas en el calendario interactivo (`SyncMultiDayCalendar.vue`).
- **Mes Completo**: Sincroniza todas las carpetas del mes seleccionado.
- **Todo el Histórico**: Procesa la totalidad de carpetas de la nube.

El sistema ejecuta el pipeline ETL, descarga los libros correspondientes, realiza inserción masiva en PostgreSQL mediante `execute_values` y muestra el progreso y los logs en tiempo real en `SyncDriveProgress.vue`.

## Criterios de Aceptación
- Requiere autenticación JWT con rol `ADMINISTRATIVO`.
- Utiliza caché en memoria para `PERSONAL` y `SUB_NOVEDADES` para eliminar consultas $N+1$.
- Realiza inserciones en bloque (*batch*) con `psycopg2.extras.execute_values`.
- Notifica al finalizar con el resumen de registros insertados, errores detectados y tiempo de auto-ocultamiento de la alerta (`auto_dismiss_seconds`).

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`
- **Reglas de negocio relacionadas**: [RN-SYNC-004](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/reglas_negocio.md#rn-sync-004), [RN-SYNC-005](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/reglas_negocio.md#rn-sync-005)
- **Endpoints relacionados**: `POST /api/sincronizar/drive`
- **Componentes frontend relacionados**: `frontend/src/components/sincronizar/SyncMultiDayCalendar.vue`, `frontend/src/components/sincronizar/SyncDriveProgress.vue`
- **Controllers/Services relacionados**: `backend/app/routers/sincronizar.py` (`sincronizar_desde_drive`, `sync_local_jsons_to_db`)

---

# HU-SYNC-003

## Historia
**Como** usuario del sistema  
**Quiero** descargar las plantillas oficiales en Excel y JSON  
**Para** preparar archivos de novedades con la estructura y columnas exactas requeridas por el sistema antes de subirlos.

## Descripción
El componente `SyncTemplateDownload.vue` ofrece botones directos para descargar la plantilla oficial en formato Excel (`plantilla_reporte_diario.xlsx`) o en formato JSON (`plantilla_reporte.json`).

## Criterios de Aceptación
- Para `format=excel`, genera un libro de cálculo con las 6 columnas preconfiguradas (`CEDULA`, `APELLIDOS Y NOMBRES`, `SUBNOVEDAD`, `DESCRIPCION`, `DESDE`, `HASTA`) y una fila de ejemplo con anchos ajustados.
- Para `format=json`, genera un JSON de muestra estructurado y formateado con sangría de 4 espacios.

## Metadata
- **Prioridad**: Baja
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-SYNC-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/reglas_negocio.md#rn-sync-001)
- **Endpoints relacionados**: `GET /api/sincronizar/plantilla/{format}`
- **Componentes frontend relacionados**: `frontend/src/components/sincronizar/SyncTemplateDownload.vue`
- **Controllers/Services relacionados**: `backend/app/routers/sincronizar.py` (`descargar_plantilla`)

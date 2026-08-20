# Casos de Uso — Módulo de Sincronización e Ingesta (`sincronizar`)

---

## CU-SYNC-001: Carga Manual de Reporte con Detección de Conflictos

### Actores
- **Principal**: Usuario con rol `ADMINISTRATIVO`.
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
1. El usuario debe estar autenticado con rol `ADMINISTRATIVO`.
2. Poseer el archivo de reporte en formato `.xlsx` o `.json`.

### Flujo Principal
1. El usuario accede a la vista de **Sincronización** (`SincronizarView.vue`).
2. En la pestaña "Archivo Local", selecciona el tipo (**Día** o **Mes**) y arrastra el archivo al componente `SyncFileDropzone.vue`.
3. El frontend envía un formulario multipart a `POST /api/sincronizar/cargar` con `overwrite=false`.
4. El backend valida el formato del archivo y comprueba las cabeceras requeridas (`CEDULA`, `APELLIDOS Y NOMBRES`, `SUBNOVEDAD`).
5. El backend verifica si las fechas a importar ya existen en la base de datos.
6. Si no existen conflictos:
   - Inserta o recupera los IDs en `PERSONAL` y `SUB_NOVEDADES`.
   - Inserta los registros en `REGISTRO_PERSONAL`.
   - Confirma la transacción con `db.commit()`.
   - Responde con `status="success"`.
7. El frontend muestra una notificación de éxito en color verde.

### Flujos Alternativos y Excepciones

#### A1: Conflicto de Duplicidad de Fechas
- **Paso 5**: Si una o más fechas ya tienen reportes en la base de datos y `overwrite` es `false`:
  1. El backend retorna `{"status": "conflict", "conflicts": ["2026-05-15"]}`.
  2. El componente `SyncConflictAlert.vue` abre una ventana modal de advertencia informando al usuario que ya existen datos para esa fecha.
  3. El usuario puede elegir **"Cancelar"** o **"Sobrescribir Datos"**.
  4. Si elige sobrescribir, el frontend reenvía la petición con `overwrite=true`.
  5. El backend borra los registros antiguos e inserta los nuevos.

#### A2: Estructura de Columnas Inválida
- **Paso 4**: Si faltan columnas requeridas:
  1. El backend retorna `HTTP 400 Bad Request` con el detalle del error.
  2. El frontend muestra una alerta roja y sugiere descargar la plantilla oficial.

---

## CU-SYNC-002: Sincronización Remota con Google Drive

### Actores
- **Principal**: Usuario Administrativo.
- **Secundario**: API de Google Drive, Base de Datos PostgreSQL.

### Precondiciones
- La cuenta institucional de Google Drive debe estar autorizada vía OAuth.

### Flujo Principal
1. El usuario selecciona la pestaña "Google Drive".
2. Selecciona el modo de sincronización (Día, Multi-Día o Mes Completo).
3. Presiona **"Iniciar Sincronización"**.
4. El frontend envía `POST /api/sincronizar/drive` con el JSON de configuración.
5. El backend lista y descarga las carpetas de Drive mediante `leer_carpetas.py` y procesa los archivos con `leer_archivos_excel.py`.
6. El backend ejecuta la inserción masiva en lote con `sync_local_jsons_to_db` y `psycopg2.extras.execute_values`.
7. El backend retorna el estado de éxito con los logs del proceso.
8. El frontend muestra la consola de sincronización completada y actualiza las fechas operacionales disponibles.

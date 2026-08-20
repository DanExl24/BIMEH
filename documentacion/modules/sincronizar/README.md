# Módulo 7: Ingesta de Reportes y Sincronización Google Drive (`sincronizar`)

## 📌 Descripción General
El módulo de **Ingesta y Sincronización** es el encargado de alimentar y mantener actualizada la base de datos operacional de BIMEH. Dispone de dos mecanismos de ingesta de datos altamente eficientes:

1. **Carga Manual Drag-and-Drop (Excel / JSON)**: Permite a los usuarios administrativos arrastrar archivos de reportes locales (`.xlsx`, `.xls` o `.json`), validando automáticamente la presencia de columnas obligatorias (`CEDULA`, `APELLIDOS Y NOMBRES`, `SUBNOVEDAD`), detectando conflictos de duplicidad de fechas y ofreciendo sobrescritura controlada.
2. **Sincronización Remota Google Drive**: Proceso automatizado que conecta con la API oficial de Google Drive mediante OAuth 2.0, descarga las carpetas mensuales, procesa las hojas de cálculo operacionales de cada día y realiza una inserción masiva por lotes (*batch insert*) en PostgreSQL optimizada con `psycopg2.extras.execute_values` y tablas maestras cacheadas en memoria.

---

## 🏛️ Arquitectura del Módulo

### Backend
- **Router**: [`backend/app/routers/sincronizar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/sincronizar.py)
- **Módulos de Ingesta y ETL**:
  - [`backend/leer_carpetas.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/leer_carpetas.py) (Exploración de la estructura de carpetas de Drive)
  - [`backend/leer_archivos_excel.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/leer_archivos_excel.py) (Extracción, limpieza y parsing de libros Excel)
  - `backend/config/auth.py` (Manejo de flujo y tokens OAuth 2.0 de Google)

### Frontend (Feature `src/features/sincronizar/` + Capas Compartidas)
- **Vista Principal**: `frontend/src/features/sincronizar/views/SincronizarView.vue`
- **Componentes de Feature**:
  - `frontend/src/features/sincronizar/components/SyncSourceSelector.vue` (Selector de origen: Archivo Local vs Google Drive)
  - `frontend/src/features/sincronizar/components/SyncFileDropzone.vue` (Área Drag-and-Drop para arrastrar archivos)
  - `frontend/src/features/sincronizar/components/SyncMultiDayCalendar.vue` (Selector multi-día interactivo)
  - `frontend/src/features/sincronizar/components/SyncDriveProgress.vue` (Barra de progreso y consola de logs en tiempo real)
  - `frontend/src/features/sincronizar/components/SyncConflictAlert.vue` (Alerta modal de resolución de conflictos de fecha)
  - `frontend/src/features/sincronizar/components/SyncTemplateDownload.vue` (Descargador de plantillas oficiales Excel y JSON)
- **Composables de Feature**:
  - `frontend/src/features/sincronizar/composables/useMultiDaySelection.ts` (Lógica para marcar/desmarcar días en calendario)
  - `frontend/src/features/sincronizar/composables/useLocalFileUpload.ts` (Manejo de carga FormData y conflictos)
- **Servicio de Feature**: `frontend/src/features/sincronizar/services/sync.service.ts`
- **Tipos de Feature**: `frontend/src/features/sincronizar/types/sync.types.ts`
- **Stores Globales**: `frontend/src/stores/appStore.ts` (Control de SSE y progreso Drive en segundo plano), `frontend/src/stores/dateStore.ts`

---

## 🔌 Endpoints del Módulo

| Método | Endpoint | Parámetros | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/sincronizar/oauth/url` | `redirect_uri` | Genera la URL de autorización oficial de Google OAuth. |
| `GET` | `/api/sincronizar/oauth/callback` | `code`, `redirect_uri` | Callback que canjea el código de autorización y guarda el token. |
| `GET` | `/api/sincronizar/plantilla/{format}` | `format` (`excel` / `json`) | Descarga un archivo de plantilla oficial preformateado para carga de datos. |
| `POST` | `/api/sincronizar/cargar` | `tipo`, `fecha`, `mes`, `overwrite`, `file` | Procesa un archivo Excel o JSON local e inserta los reportes. |
| `POST` | `/api/sincronizar/drive` | `DriveSyncRequest` (JSON) | Ejecuta el pipeline ETL de descarga y sincronización desde Google Drive. |

---

## 📄 Documentos del Módulo

- [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/historias_usuario.md)
- [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/reglas_negocio.md)
- [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/casos_uso.md)

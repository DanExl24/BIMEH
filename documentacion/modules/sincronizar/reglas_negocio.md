# Reglas de Negocio — Módulo de Sincronización e Ingesta (`sincronizar`)

---

## 📥 1. Validaciones de Ingesta y Esquema de Archivos

### RN-SYNC-001
- **Identificador**: `RN-SYNC-001`
- **Descripción**: Todo archivo de carga manual (Excel o JSON) debe contener obligatoriamente las tres columnas maestras de negocio: `CEDULA`, `APELLIDOS Y NOMBRES` y `SUBNOVEDAD`. La ausencia de cualquiera de ellas anula la carga con código `HTTP 400 Bad Request`.
- **Motivo**: Prevenir la inserción de registros huérfanos o corruptos que desvirtúen las estadísticas y los conteos de fuerza disponible.
- **Módulos afectados**: `sincronizar`.
- **Archivos donde se implementa**: [`backend/app/routers/sincronizar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/sincronizar.py) (Líneas 133, 163–165, 233, 279), `frontend/src/features/sincronizar/composables/useLocalFileUpload.ts`.
- **Endpoints relacionados**: `POST /api/sincronizar/cargar`
- **Historias de usuario relacionadas**: [HU-SYNC-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/historias_usuario.md#hu-sync-001)

---

### RN-SYNC-002
- **Identificador**: `RN-SYNC-002`
- **Descripción**: Si una fecha a cargar ya posee registros en la tabla `REPORTES` y el parámetro `overwrite` es `FALSE` (o no fue marcado), el sistema detiene la transacción y retorna un estado `status="conflict"` con la lista de fechas duplicadas detectadas.
- **Motivo**: Proteger los datos históricos existentes frente a sobrescrituras involuntarias por parte de los operadores.
- **Módulos afectados**: `sincronizar`.
- **Archivos donde se implementa**: [`backend/app/routers/sincronizar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/sincronizar.py) (Líneas 290–304), `frontend/src/features/sincronizar/components/SyncConflictAlert.vue`.
- **Endpoints relacionados**: `POST /api/sincronizar/cargar`
- **Historias de usuario relacionadas**: [HU-SYNC-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/historias_usuario.md#hu-sync-001)

---

### RN-SYNC-003
- **Identificador**: `RN-SYNC-003`
- **Descripción**: Cuando se autoriza la sobrescritura (`overwrite=TRUE`), el sistema elimina de forma atómica los registros existentes en `REGISTRO_PERSONAL` asociados a ese `id_reporte` antes de insertar los nuevos datos, garantizando integridad referencial y evitando registros duplicados.
- **Motivo**: Permitir la corrección y reingesta limpia de reportes operacionales rectificados.
- **Módulos afectados**: `sincronizar`.
- **Archivos donde se implementa**: [`backend/app/routers/sincronizar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/sincronizar.py) (Líneas 308–314, 461–470).
- **Endpoints relacionados**: `POST /api/sincronizar/cargar`, `POST /api/sincronizar/drive`
- **Historias de usuario relacionadas**: [HU-SYNC-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/historias_usuario.md#hu-sync-001), [HU-SYNC-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/historias_usuario.md#hu-sync-002)

---

## ☁️ 2. Pipeline ETL y Sincronización Remota

### RN-SYNC-004
- **Identificador**: `RN-SYNC-004`
- **Descripción**: Para evitar problemas de sobrecarga por consultas $N+1$ durante la sincronización masiva de miles de registros, el proceso de sincronización debe precargar en diccionarios en memoria las tablas maestras `PERSONAL` (`{cedula: id}`) y `SUB_NOVEDADES` (`{nombre: id}`).
- **Motivo**: Reducir los tiempos de sincronización de minutos a pocos segundos, evitando miles de viajes de red (*roundtrips*) individuales hacia la base de datos PostgreSQL.
- **Módulos afectados**: `sincronizar`.
- **Archivos donde se implementa**: [`backend/app/routers/sincronizar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/sincronizar.py) (Líneas 401–409, 503–520).
- **Endpoints relacionados**: `POST /api/sincronizar/drive`
- **Historias de usuario relacionadas**: [HU-SYNC-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/historias_usuario.md#hu-sync-002)

---

### RN-SYNC-005
- **Identificador**: `RN-SYNC-005`
- **Descripción**: La inserción de filas en `REGISTRO_PERSONAL` durante la sincronización remota debe realizarse en bloques agrupados (*batch insert*) utilizando `psycopg2.extras.execute_values`.
- **Motivo**: Optimizar el rendimiento de escritura en PostgreSQL durante la importación de meses completos o años históricos.
- **Módulos afectados**: `sincronizar`.
- **Archivos donde se implementa**: [`backend/app/routers/sincronizar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/sincronizar.py) (Líneas 546–557).
- **Endpoints relacionados**: `POST /api/sincronizar/drive`
- **Historias de usuario relacionadas**: [HU-SYNC-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/historias_usuario.md#hu-sync-002)

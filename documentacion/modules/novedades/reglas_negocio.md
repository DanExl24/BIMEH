# Reglas de Negocio — Módulo de Gestión y Búsqueda de Novedades (`novedades`)

---

## 🛡️ 1. Naturaleza Operacional y Seguridad

### RN-NOV-001
- **Identificador**: `RN-NOV-001`
- **Descripción**: El módulo de Gestión y Búsqueda de Novedades es estrictamente de **solo lectura**. No permite crear, alterar ni eliminar registros en las tablas `REGISTRO_PERSONAL`, `PERSONAL`, `REPORTES` ni `SUB_NOVEDADES`.
- **Motivo**: Garantizar la inmutabilidad de la auditoría y preservar la integridad referencial de los reportes diarios sincronizados.
- **Módulos afectados**: `novedades`.
- **Archivos donde se implementa**: [`backend/app/routers/novedades.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/novedades.py).
- **Endpoints relacionados**: `GET /api/novedades/catalogo`, `GET /api/novedades/consulta`, `GET /api/novedades/exportar/excel`, `GET /api/novedades/exportar/pdf`.
- **Historias de usuario relacionadas**: [HU-NOV-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/historias_usuario.md#hu-nov-001).

---

### RN-NOV-002
- **Identificador**: `RN-NOV-002`
- **Descripción**: Las consultas masivas sobre `REGISTRO_PERSONAL` (con más de 165.000 filas) deben ejecutarse forzosamente mediante los índices `idx_registro_personal_subnovedad`, `idx_registro_personal_personal`, `idx_registro_personal_reporte` e `idx_reportes_fecha`.
- **Motivo**: Prevenir escaneos secuenciales pesados que degraden el rendimiento del motor de base de datos PostgreSQL, asegurando tiempos de respuesta sub-segundo.
- **Módulos afectados**: `novedades`.
- **Archivos donde se implementa**: [`init_scripts/01_schema.sql`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/init_scripts/01_schema.sql) (Líneas 528–534).
- **Endpoints relacionados**: `GET /api/novedades/consulta`, `GET /api/novedades/exportar/*`.
- **Historias de usuario relacionadas**: [HU-NOV-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/historias_usuario.md#hu-nov-001).

---

## 🔍 2. Filtrado y Reglas de Coincidencia

### RN-NOV-003
- **Identificador**: `RN-NOV-003`
- **Descripción**: El filtro por mes operacional sincroniza dinámicamente los selectores de rango temporal. Al seleccionar un mes específico (ej. FEBRERO, JUNIO), el sistema restringe los selectores de *Día Desde* y *Día Hasta* exclusivamente a los días calendáricos correspondientes a dicho mes (ej. 1 al 28 para febrero, 1 al 30 para junio), evitando combinaciones cronológicas incompatibles. Si el mes seleccionado es *"TODOS LOS MESES"*, el sistema habilita selectores libres de fecha completa (`YYYY-MM-DD`).
- **Motivo**: Garantizar consistencia temporal y evitar que el usuario asigne días o meses no correspondientes al periodo evaluado.
- **Módulos afectados**: `novedades`, `reportes`.
- **Archivos donde se implementa**: [`frontend/src/features/novedades/views/NovedadesView.vue`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/frontend/src/features/novedades/views/NovedadesView.vue), [`backend/app/routers/novedades.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/novedades.py) (Líneas 50–57).
- **Endpoints relacionados**: `GET /api/novedades/consulta`.
- **Historias de usuario relacionadas**: [HU-NOV-002](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/historias_usuario.md#hu-nov-002).

---

### RN-NOV-004
- **Identificador**: `RN-NOV-004`
- **Descripción**: La distinción de estado del personal se calcula evaluando el campo `fecha_retiro`:
  - `ACTIVO`: `fecha_retiro IS NULL`.
  - `RETIRADO`: `fecha_retiro IS NOT NULL`.
  Al filtrar por estado, se excluyen los integrantes que no cumplan la condición en su ficha de personal.
- **Motivo**: Permitir al analista separar los antecedentes de integrantes retirados de la disponibilidad actual del personal en servicio activo.
- **Módulos afectados**: `novedades`, `personal`.
- **Archivos donde se implementa**: [`backend/app/routers/novedades.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/novedades.py) (Líneas 69–73).
- **Endpoints relacionados**: `GET /api/novedades/consulta`.
- **Historias de usuario relacionadas**: [HU-NOV-002](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/historias_usuario.md#hu-nov-002).

---

## 📊 3. Paginación y Exportación Fidedigna

### RN-NOV-005
- **Identificador**: `RN-NOV-005`
- **Descripción**: La consulta paginada limita la entrega de datos a un máximo de `500` registros por solicitud (predeterminado en 50), empleando `LIMIT` y `OFFSET`. El cálculo de KPIs agregados se ejecuta sobre el universo completo de registros filtrados de forma simultánea.
- **Motivo**: Proveer una experiencia de usuario rápida y fluida sin transferir miles de filas innecesarias a través de la red en cada cambio de vista.
- **Módulos afectados**: `novedades`.
- **Archivos donde se implementa**: [`backend/app/routers/novedades.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/novedades.py) (Líneas 100–145).
- **Endpoints relacionados**: `GET /api/novedades/consulta`.
- **Historias de usuario relacionadas**: [HU-NOV-003](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/historias_usuario.md#hu-nov-003).

---

### RN-NOV-006
- **Identificador**: `RN-NOV-006`
- **Descripción**: La exportación a Excel y PDF debe respetar exactamente los filtros aplicados en la consulta actual y limitar el reporte a un techo de seguridad de `15.000` registros para hojas de cálculo y `5.000` registros para documentos PDF, evitando saturación de memoria del servidor.
- **Motivo**: Proteger los recursos del servidor y garantizar que los archivos generados sean manipulables de manera ágil por las aplicaciones ofimáticas del usuario.
- **Módulos afectados**: `novedades`, `exportar`.
- **Archivos donde se implementa**: [`backend/app/routers/novedades.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/novedades.py) (Líneas 190, 310).
- **Endpoints relacionados**: `GET /api/novedades/exportar/excel`, `GET /api/novedades/exportar/pdf`.
- **Historias de usuario relacionadas**: [HU-NOV-004](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/historias_usuario.md#hu-nov-004).

# Casos de Uso — Módulo de Cronología (`cronologia`)

---

## CU-CRON-001: Navegación Cronológica y Consulta de Reporte Diario

### Actores
- **Principal**: Usuario del Sistema (Oficial de Servicio / Comandante).
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
1. El usuario debe estar autenticado.
2. Existen reportes operacionales cargados para el mes seleccionado.

### Flujo Principal
1. El usuario ingresa a la pestaña **"Cronología"** (`CronologiaView.vue`).
2. El sistema carga el mes activo y solicita a la API:
   - `GET /api/reportes/calendario?mes=...`
3. El frontend dibuja las celdas de los días en `CronologiaActivityCalendar.vue` con sus porcentajes y badges de color.
4. El usuario hace clic sobre un día específico en el calendario (ej. `2026-05-15`).
5. La fecha activa se actualiza y se emite la petición `GET /api/reportes/dia?fecha=2026-05-15`.
6. El backend consulta en la tabla `REGISTRO_PERSONAL` los registros asociados al reporte de esa fecha.
7. El componente `CronologiaDailyReportTable.vue` lista a todos los integrantes ordenados alfabéticamente.
8. El usuario utiliza el buscador local para escribir el apellido de un efectivo o selecciona la subnovedad `"PERMISO"` para filtrar la tabla en tiempo real.

### Flujos Alternativos
- **A1: Fecha sin reporte**: Si la fecha seleccionada no tiene registros en la base de datos, el backend responde `[]` y la tabla muestra un aviso indicando que no se generó reporte para ese día.

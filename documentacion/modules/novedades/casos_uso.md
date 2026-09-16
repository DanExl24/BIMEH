# Casos de Uso — Módulo de Gestión y Búsqueda de Novedades (`novedades`)

---

## CU-NOV-001: Consulta de Novedades con Filtros Dinámicos Cruzados

### Actores
- **Principal**: Comandante / Administrador del Sistema / Oficial de Personal.
- **Secundario**: Servidor Backend BIMEH y Motor PostgreSQL.

### Precondiciones
- El usuario debe haber iniciado sesión en el sistema (`token` JWT válido).

### Flujo Principal
1. El usuario hace clic en **"Gestión de Novedades"** en el menú de navegación lateral.
2. La vista `src/features/novedades/views/NovedadesView.vue` se monta e invoca a `novedadesService.getCatalogo()`.
3. El backend responde con el listado de novedades y el volumen total de días/efectivos asociados a cada una.
4. El usuario selecciona una novedad específica (ej. *"INCAPACIDAD"* o *"VACACIONES"*) en el menú desplegable o mediante los botones de acceso rápido.
5. El usuario puede refinar la búsqueda seleccionando:
   - **Mes Operacional**: (ej. *"MARZO"* o *"TODOS"*).
   - **Rango de Fechas**: Fecha desde y Fecha hasta.
   - **Estado**: *"TODOS"*, *"ACTIVO"* o *"RETIRADO"*.
   - **Búsqueda por texto**: Cédula o fragmento de nombres/apellidos.
6. El frontend envía la consulta a `GET /api/novedades/consulta` con los parámetros seleccionados.
7. El motor PostgreSQL ejecuta la consulta utilizando los índices `idx_registro_personal_subnovedad`, `idx_registro_personal_reporte` y `idx_registro_personal_personal`.
8. El backend retorna:
   - Objeto `kpis`: Total registros, efectivos únicos afectados, proporción de activos vs retirados y rango temporal detectado.
   - Lista `registros`: Filas paginadas correspondientes a la página seleccionada.
   - Metadatos de paginación (`total`, `page`, `limit`, `total_pages`).
9. La interfaz actualiza de manera reactiva el componente `NovedadKpis.vue` y la tabla interactiva de resultados.

### Flujos Alternativos y Excepciones
- **A1: Sin resultados coincidentes**: Si ningún registro cumple con los filtros, se muestra un estado vacío informativo (*"No se encontraron registros"*), con los KPIs en `0` y un botón rápido para restablecer filtros.
- **A2: Transición de página**: El usuario presiona *"Siguiente"* o un número de página específico; el sistema solicita únicamente la porción correspondiente mediante `offset/limit` sin recalcular innecesariamente datos pesados.

---

## CU-NOV-002: Auditoría y Navegación al Expediente del Personal

### Actores
- **Principal**: Evaluador de Talento Humano.

### Precondiciones
- El usuario visualiza la tabla de resultados de novedades tras aplicar una búsqueda.

### Flujo Principal
1. El usuario ubica en la tabla a un integrante con novedad reportada.
2. Revisa los datos de la fila: cédula, nombre completo, fecha del reporte diario, rango de novedad (fecha inicio y fin) y observaciones consignadas.
3. El usuario hace clic en el botón de acción **"Ver Expediente"** (icono de enlace externo).
4. El sistema enruta a `/personal/:cedula`, abriendo el expediente digital del integrante donde puede consultar su cronología completa, mapas de calor y disponibilidad histórica.

---

## CU-NOV-003: Exportación Parametrizada a Excel y PDF

### Actores
- **Principal**: Administrador / Oficial de Operaciones.
- **Secundario**: Motor de Reportes Backend (OpenPyXL / ReportLab).

### Precondiciones
- El usuario ha establecido un conjunto de filtros en la vista de Novedades.

### Flujo Principal
1. El usuario hace clic en el botón **"Exportar Excel"** o **"Exportar PDF"**.
2. El frontend activa el indicador de carga en el botón (`Loader2`) y llama a `novedadesService.descargarReporte(formato, filtros)`.
3. El backend recibe la solicitud en `GET /api/novedades/exportar/excel` o `GET /api/novedades/exportar/pdf` preservando exactamente los mismos parámetros aplicados en pantalla.
4. **Si es Excel**:
   - `openpyxl` genera un libro de cálculo con cabecera institucional BIMEJ 12, bloque de filtros activos, anchos auto-ajustados y filas tabulares con estilos corporativos.
5. **Si es PDF**:
   - `reportlab` genera un documento apaisado (*landscape*) de alta fidelidad, con título, metadatos, tabla de registros y numeración.
6. El backend envía el archivo mediante `StreamingResponse` con las cabeceras `Content-Disposition`.
7. El navegador recibe el flujo binario e inicia la descarga local automática del archivo.
8. El frontend desactiva el spinner del botón.

### Flujos Alternativos y Excepciones
- **A1: Error de descarga**: Si el servidor responde con error, el frontend captura la excepción y notifica al usuario mediante un mensaje amigable, restaurando el botón a su estado normal.

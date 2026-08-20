# Casos de Uso — Módulo de Reportes (`reportes`)

---

## CU-REP-001: Exportación Directa de Reporte Diario

### Actores
- **Principal**: Usuario Autenticado (Comandante / Secretario).
- **Secundario**: Servidor Backend (FastAPI, OpenPyXL, ReportLab).

### Precondiciones
- Debe existir al menos un reporte operacional para la fecha seleccionada.

### Flujo Principal
1. El usuario accede a la vista de **Reportes** (`src/features/reportes/views/ReportesView.vue`).
2. En la tarjeta `ReportDirectDownloadCard.vue`, selecciona la fecha en el selector.
3. El usuario presiona el botón **"Descargar Excel"** (o PDF/CSV).
4. El frontend utiliza `reportes.service.ts` y `reportDownloadStore.ts` para disparar la petición `GET /api/exportar/excel?tipo=dia&fecha=YYYY-MM-DD`.
5. El backend ejecuta la consulta en la base de datos para recuperar todos los efectivos del día.
6. El backend instancia un libro de Excel con OpenPyXL, aplica los estilos institucionales (fuente Calibri, cabecera gris `#1F2937` y bordes finos), calcula los anchos de columna e inserta las filas.
7. El backend transmite el archivo en memoria a través de `StreamingResponse` con cabecera `Content-Disposition: attachment; filename=reporte_detallado_YYYY-MM-DD.xlsx`.
8. El navegador recibe el flujo binario y descarga el archivo automáticamente en la carpeta de descargas del usuario.

### Flujos Alternativos y Excepciones
- **A1: Parámetros Inválidos o Faltantes**: Si no se envían parámetros válidos, el backend retorna `HTTP 400 Bad Request` con el mensaje `{"detail": "Parámetros inválidos para la exportación."}`.

# Casos de Uso — Módulo de Personal (`personal`)

---

## CU-PERS-001: Búsqueda Predictiva y Apertura de Expediente

### Actores
- **Principal**: Evaluador / Analista de Personal.
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
- El usuario debe haber iniciado sesión.

### Flujo Principal
1. El usuario navega a la sección **"Personal"** en el menú lateral.
2. En la vista `src/features/personal/views/PersonalView.vue`, escribe al menos dos caracteres en la caja de búsqueda (ej. `"RAM"` o `"6804"`).
3. El composable `usePersonalAutocomplete.ts` captura el input y emite una petición asíncrona a `GET /api/personal/buscar?q=...` a través de `personal.service.ts`.
4. El backend busca registros en la tabla `PERSONAL` que coincidan con la cédula o el nombre.
5. El backend devuelve un arreglo JSON con hasta 50 resultados, indicando cédula, nombre y estado (`ACTIVO` / `RETIRADO`).
6. El frontend despliega la cuadrícula o lista interactiva de resultados con badges diferenciados.
7. El usuario hace clic sobre el integrante deseado.
8. El enrutador navega a `/personal/:cedula`, montando `src/features/personal/views/PersonalDetalleView.vue`.
9. El composable `usePersonalProfile.ts` solicita en paralelo:
   - `GET /api/personal/{cedula}` (Métricas y ficha básica).
   - `GET /api/personal/{cedula}/historial` (Historial detallado).
   - `GET /api/personal/{cedula}/acumulado` (Totales por subnovedad).
10. La pantalla renderiza `PersonalHeaderCard.vue`, `PersonalKpiGrid.vue`, `PersonalNovedadesChart.vue`, `PersonalTimeline.vue` y `PersonalHeatmapMatrix.vue`.

### Flujos Alternativos y Excepciones
- **A1: Menos de 2 caracteres**: El frontend no envía la solicitud y limpia la lista desplegable.
- **A2: Cédula no encontrada**: Si se accede directamente por URL con una cédula inexistente, el backend responde `HTTP 404 Not Found` y la vista muestra un mensaje de advertencia `"Personal no encontrado"`.

---

## CU-PERS-002: Generación de Reporte Individual Filtrado

### Actores
- **Principal**: Usuario Administrativo.
- **Secundario**: Motor de Exportación Backend (OpenPyXL / ReportLab).

### Precondiciones
- El usuario se encuentra en la vista de expediente de un integrante existente.

### Flujo Principal
1. El usuario presiona el botón **"Generar Reporte"** en la tarjeta `PersonalHeaderCard.vue`.
2. Se abre el modal compartido `src/components/modals/ReportGenerationModal.vue`.
3. El usuario selecciona el formato deseado (**Excel**, **CSV** o **PDF**).
4. El usuario selecciona el alcance (**Historial Completo** o **Heatmap Mensual**).
5. Opcionalmente, el usuario elige una subnovedad específica en el selector desplegable (ej. `"VACACIONES"`).
6. El usuario hace clic en **"Descargar Reporte"**.
7. El frontend utiliza `reportes.service.ts` para solicitar el archivo mediante `GET /api/exportar/{formato}?tipo=personal&cedula=...&subnovedad=...`.
8. El backend construye dinámicamente el documento filtrado y lo transmite mediante `StreamingResponse`.
9. El navegador recibe el flujo binario y descarga el archivo (ej. `historial_cedula_6804683.xlsx`).

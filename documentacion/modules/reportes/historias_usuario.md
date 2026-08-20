# Historias de Usuario — Módulo de Reportes (`reportes`)

---

# HU-REP-001

## Historia
**Como** comandante de unidad  
**Quiero** exportar el Reporte Detallado del Día en formato Excel, CSV o PDF  
**Para** presentar la relación oficial del personal de servicio y novedades a los mandos superiores en reuniones operacionales.

## Descripción
En la vista `/reportes`, el usuario selecciona una fecha específica en el calendario y hace clic en el botón de exportación deseado (**Excel**, **CSV** o **PDF**). El backend consulta todos los registros de la fecha, genera el documento con diseño estandarizado (título, cabeceras en negrita con fondo oscuro, cédula, nombres, subnovedad, descripción y vigencia) y lo envía para su descarga inmediata.

## Criterios de Aceptación
- Para `tipo=dia`, el archivo incluye las columnas: `CÉDULA`, `APELLIDOS Y NOMBRES`, `SUBNOVEDAD`, `DESCRIPCIÓN`, `DESDE`, `HASTA`, `FECHA REPORTE`.
- En Excel, la primera fila contiene el título combinado con fondo gris oscuro (`#1F2937`) y texto blanco.
- En PDF, el documento se genera en orientación horizontal (*landscape*) para asegurar que todas las columnas sean legibles sin cortes de texto.
- En CSV, el archivo se codifica con `utf-8-sig` para abrirse sin problemas de caracteres especiales en cualquier versión de Excel.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-REP-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/reglas_negocio.md#rn-rep-001), [RN-REP-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/reglas_negocio.md#rn-rep-002), [RN-REP-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/reglas_negocio.md#rn-rep-003)
- **Endpoints relacionados**: `GET /api/exportar/excel`, `GET /api/exportar/csv`, `GET /api/exportar/pdf`
- **Componentes frontend relacionados**: `frontend/src/views/ReportesView.vue`, `frontend/src/components/reportes/ReportDirectDownloadCard.vue`
- **Controllers/Services relacionados**: `backend/app/routers/exportar.py`

---

# HU-REP-002

## Historia
**Como** secretario de personal  
**Quiero** exportar el Consolidado Mensual en formato matriz (Personal vs Días) en modo letras (`D/N/R/-`) o modo extendido  
**Para** contar con una planilla de control operacional mensual idéntica a los formatos impresos de la institución.

## Descripción
El formulario de Consolidado Mensual (`ReportConsolidadoMensualForm.vue`) permite seleccionar el mes (o `"TODOS"` para el año completo), el formato de salida y el modo de visualización (`modo="letras"` o `modo="completo"`).
- **Modo letras (`modo="letras"`)**:
  - `D`: Disponible (`"CDO UNIDAD"` o `"AREA OPERACIONES"`).
  - `N`: Novedad (cualquier otra subnovedad activa).
  - `R`: Retirado (fecha posterior a la desvinculación).
  - `-`: Sin reporte.
- **Modo completo (`modo="completo"`)**: Muestra el nombre literal de cada subnovedad en la celda correspondiente.

## Criterios de Aceptación
- La cabecera horizontal enumera cada día del mes (`Día 01`, `Día 02`... o `01/05`, `02/05` si es anual).
- Permite aplicar filtros opcionales de cédula y subnovedad.
- El archivo se genera con el nombre `consolidado_personal_<mes>.xlsx` (o `.csv` / `.pdf`).

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-REP-004](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/reglas_negocio.md#rn-rep-004)
- **Endpoints relacionados**: `GET /api/exportar/excel`, `GET /api/exportar/csv`, `GET /api/exportar/pdf`
- **Componentes frontend relacionados**: `frontend/src/components/reportes/ReportConsolidadoMensualForm.vue`
- **Controllers/Services relacionados**: `backend/app/routers/exportar.py`

---

# HU-REP-003

## Historia
**Como** oficial de talento humano  
**Quiero** generar la Exportación Ágil de Novedades  
**Para** obtener un reporte condensado donde las secuencias consecutivas de novedades se compriman en rangos (ej. `10-15 (VACACIONES)`) con notas de observación en cada celda.

## Descripción
La modalidad `tipo="agil"` filtra exclusivamente a los integrantes que registraron novedades (omitiendo a quienes estuvieron disponibles todo el tiempo). Si un integrante tuvo una novedad continuada durante varios días, el motor comprime las fechas mediante la función `format_agil_month_ranges` (ej. `01-05 (PERMISO)` y `12-18 (VACACIONES)`) e inserta en la celda de Excel un comentario emergente (`openpyxl.comments.Comment`) con la justificación y descripción detallada de cada día.

## Criterios de Aceptación
- Excluye de manera estricta los registros de disponibilidad (`sn.nombre NOT IN ('CDO UNIDAD', 'AREA OPERACIONES')`).
- Concatena rangos continuos del mismo tipo de subnovedad.
- En Excel, agrega notas emergentes de celda cuando existan descripciones textuales.
- En PDF, resalta los rangos con formato HTML `<font color="#DC2626"><b>...</b></font>`.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-REP-005](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/reglas_negocio.md#rn-rep-005)
- **Endpoints relacionados**: `GET /api/exportar/excel`, `GET /api/exportar/pdf`
- **Componentes frontend relacionados**: `frontend/src/views/ReportesView.vue`
- **Controllers/Services relacionados**: `backend/app/routers/exportar.py` (`format_agil_month_ranges`, `exportar_excel`)

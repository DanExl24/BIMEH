# Reglas de Negocio — Módulo de Reportes (`reportes`)

---

## 📄 1. Formatos y Codificación de Archivos

### RN-REP-001
- **Identificador**: `RN-REP-001`
- **Descripción**: Toda exportación en formato CSV debe codificarse obligatoriamente con `utf-8-sig` (codificación UTF-8 con marca de orden de bytes BOM).
- **Motivo**: Permitir que Microsoft Excel en plataformas Windows interprete de forma automática y transparente caracteres latinos (acentos, tildes, eñes) sin requerir que el usuario configure manualmente la página de códigos en el asistente de importación.
- **Módulos afectados**: `reportes`.
- **Archivos donde se implementa**: [`backend/app/routers/exportar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/exportar.py) (Línea 276), `frontend/src/features/reportes/services/reportes.service.ts`.
- **Endpoints relacionados**: `GET /api/exportar/csv`
- **Historias de usuario relacionadas**: [HU-REP-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/historias_usuario.md#hu-rep-001)

---

### RN-REP-002
- **Identificador**: `RN-REP-002`
- **Descripción**: La orientación de los documentos PDF generados con ReportLab se determina dinámicamente:
  - Orientación Horizontal (*landscape*): Para tipos de reporte con matrices anchas (`"dia"`, `"mes"`, `"consolidado_mensual"`).
  - Orientación Vertical (*letter* / retrato): Para reportes individuales de ficha técnica (`"personal"`).
- **Motivo**: Maximizar el aprovechamiento del espacio imprimible y evitar el truncamiento de tablas de múltiples columnas.
- **Módulos afectados**: `reportes`.
- **Archivos donde se implementa**: [`backend/app/routers/exportar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/exportar.py) (Línea 1015).
- **Endpoints relacionados**: `GET /api/exportar/pdf`
- **Historias de usuario relacionadas**: [HU-REP-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/historias_usuario.md#hu-rep-001)

---

### RN-REP-003
- **Identificador**: `RN-REP-003`
- **Descripción**: En la generación de PDFs con ReportLab, todos los nombres de estilos (`ParagraphStyle`) deben incorporar un sufijo único derivado de la dirección de memoria del buffer (`f'DocTitle_{uid}'`).
- **Motivo**: Prevenir excepciones `KeyError: 'Style DocTitle already exists'` cuando múltiples usuarios solicitan descargas de PDF simultáneamente en el servidor Uvicorn.
- **Módulos afectados**: `reportes`.
- **Archivos donde se implementa**: [`backend/app/routers/exportar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/exportar.py) (Líneas 1012, 1028–1060).
- **Endpoints relacionados**: `GET /api/exportar/pdf`
- **Historias de usuario relacionadas**: [HU-REP-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/historias_usuario.md#hu-rep-001)

---

## 🗂️ 2. Modalidades y Lógica de Negocio de Exportación

### RN-REP-004
- **Identificador**: `RN-REP-004`
- **Descripción**: En el reporte de `consolidado_mensual`, la celda de cada integrante para un día evaluado se resuelve siguiendo la siguiente precedencia jerárquica estricta:
  1. Si el integrante tiene `fecha_retiro` y la fecha es $\ge$ `fecha_retiro` $\rightarrow$ `R` (o `"RETIRADO"`).
  2. Si no tiene registro en el reporte diario de esa fecha $\rightarrow$ `-` (o `"N/A"`).
  3. Si la subnovedad registrada es `"CDO UNIDAD"` o `"AREA OPERACIONES"` $\rightarrow$ `D` (o nombre literal).
  4. Si la subnovedad registrada es cualquier otra $\rightarrow$ `N` (o nombre literal).
- **Motivo**: Garantizar fidelidad absoluta en la matriz de control de fuerza mensual y anual.
- **Módulos afectados**: `reportes`.
- **Archivos donde se implementa**: [`backend/app/routers/exportar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/exportar.py) (Líneas 252–270), `frontend/src/features/reportes/components/ReportConsolidadoMensualForm.vue`.
- **Endpoints relacionados**: `GET /api/exportar/csv`, `GET /api/exportar/excel`, `GET /api/exportar/pdf`
- **Historias de usuario relacionadas**: [HU-REP-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/historias_usuario.md#hu-rep-002)

---

### RN-REP-005
- **Identificador**: `RN-REP-005`
- **Descripción**: La exportación ágil (`tipo="agil"`) comprime los días consecutivos de la misma novedad en una sola etiqueta de rango `start-end (SUBNOVEDAD)` (ej. `10-15 (VACACIONES)`). Si es un solo día, utiliza el formato de 2 dígitos `day (SUBNOVEDAD)` (ej. `22 (PERMISO)`).
- **Motivo**: Reducir el tamaño de las planillas mensuales permitiendo que las ausencias prolongadas se lean en una sola línea clara por efectivo.
- **Módulos afectados**: `reportes`.
- **Archivos donde se implementa**: [`backend/app/routers/exportar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/exportar.py) (Líneas 21–58).
- **Endpoints relacionados**: `GET /api/exportar/excel`, `GET /api/exportar/pdf`
- **Historias de usuario relacionadas**: [HU-REP-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/historias_usuario.md#hu-rep-003)

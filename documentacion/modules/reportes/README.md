# Módulo 6: Centro de Exportación y Reportes (`reportes`)

## 📌 Descripción General
El módulo de **Centro de Exportación y Reportes** es el motor generador de documentos y archivos descargables oficiales del sistema BIMEH. Permite extraer la información operacional en múltiples formatos estándar de la industria:
- **Excel (`.xlsx`)**: Generado nativamente con la librería `openpyxl`, con estilos visuales corporativos (fuentes Calibri, cabeceras en gris oscuro `#1F2937`, bordes finos, anchos automáticos y notas de celda con comentarios `openpyxl.comments.Comment`).
- **CSV (`.csv`)**: Archivos de texto delimitados por comas con codificación binaria `utf-8-sig` (UTF-8 con BOM) para compatibilidad nativa inmediata con Microsoft Excel en español.
- **PDF (`.pdf`)**: Generado con `reportlab`, con maquetación adaptativa (orientación horizontal *landscape* para tablas anchas y vertical *letter* para reportes individuales) y estilos de párrafo dinámicos con identificadores únicos para evitar colisiones de estilos en entornos concurrentes.

---

## 🏛️ Arquitectura del Módulo

### Backend
- **Router**: [`backend/app/routers/exportar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/exportar.py)
- **Librerías de Renderizado**: `openpyxl`, `reportlab`, `csv`, `io.BytesIO`, `io.StringIO`

### Frontend (Feature `src/features/reportes/` + Capas Compartidas)
- **Vista Principal**: `frontend/src/features/reportes/views/ReportesView.vue`
- **Componentes de Feature**:
  - `frontend/src/features/reportes/components/ReportDirectDownloadCard.vue` (Descargas directas rápidas del mes activo)
  - `frontend/src/features/reportes/components/ReportIndividualExpedienteForm.vue` (Exportación por cédula y subnovedad)
  - `frontend/src/features/reportes/components/ReportConsolidadoMensualForm.vue` (Exportación de matriz mensual / anual)
  - `frontend/src/features/reportes/components/ReportResumenAnualForm.vue` (Resumen anual ejecutivo)
- **Servicio de Feature**: `frontend/src/features/reportes/services/reportes.service.ts` (Construcción de URLs de exportación tipadas)
- **Store Global**: `frontend/src/stores/reportDownloadStore.ts` (Control de descargas asíncronas con modal de progreso)
- **Modales Compartidos**: `frontend/src/components/modals/ExportModal.vue`, `frontend/src/components/modals/ReportGenerationModal.vue`

---

## 🔌 Endpoints del Módulo

| Método | Endpoint | Parámetros Clave | Tipos de Reporte Soportados (`tipo`) |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/exportar/csv` | `tipo`, `fecha`, `mes`, `cedula`, `subnovedad`, `modo` | `dia`, `mes`, `personal`, `personal_db`, `subnovedades`, `consolidado_mensual`, `agil` |
| `GET` | `/api/exportar/excel` | `tipo`, `fecha`, `mes`, `cedula`, `subnovedad`, `modo` | `dia`, `mes`, `personal`, `personal_db`, `subnovedades`, `consolidado_mensual`, `agil` |
| `GET` | `/api/exportar/pdf` | `tipo`, `fecha`, `mes`, `cedula`, `subnovedad`, `modo` | `dia`, `mes`, `personal`, `personal_db`, `subnovedades`, `consolidado_mensual`, `agil` |

---

## 📄 Documentos del Módulo

- [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/historias_usuario.md)
- [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/reglas_negocio.md)
- [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/casos_uso.md)

# Módulo 8: Gestión y Búsqueda de Novedades (`novedades`)

## 📌 Descripción General
El módulo de **Gestión y Búsqueda de Novedades** es una herramienta analítica y de auditoría de solo lectura diseñada para consultar, filtrar y evaluar de manera ágil los registros históricos de novedades del personal militar y operativo del BIMEJ 12.

Permite al mando y administradores del sistema responder en milisegundos interrogantes operacionales clave:
- *¿Qué personal contó con determinada novedad (ej. VACACIONES, PERMISO, INCAPACIDAD) en un mes específico?*
- *¿Qué día exacto comenzó o se reportó la novedad para cada integrante?*
- *¿Cuántos efectivos únicos se encuentran o estuvieron afectados por dicha novedad?*
- *¿Cuál es la proporción de integrantes activos frente a retirados vinculados al registro?*

Incluye métricas agregadas reactivas (KPIs de total registros, efectivos únicos, distribución de estado y rango temporal), tabla interactiva de registros paginados y exportación parametrizada fidedigna tanto en **Excel (.xlsx)** como en **PDF oficial**.

---

## 🏛️ Arquitectura del Módulo

### Backend
- **Router**: [`backend/app/routers/novedades.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/novedades.py)
- **Base de Datos & Conexión**: [`backend/app/database.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/database.py)
- **Script DDL & Índices**: [`init_scripts/01_schema.sql`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/init_scripts/01_schema.sql)

### Frontend (Feature `src/features/novedades/`)
- **Vistas**:
  - `frontend/src/features/novedades/views/NovedadesView.vue` (Vista analítica principal con selector de catálogo, filtros dinámicos, KPIs y tabla)
- **Componentes**:
  - `frontend/src/features/novedades/components/NovedadKpis.vue` (Tarjetas de métricas calculadas en tiempo real)
- **Servicio**:
  - `frontend/src/features/novedades/services/novedades.service.ts`
- **Tipos TypeScript**:
  - `frontend/src/features/novedades/types/novedades.types.ts`
- **Navegación**:
  - `frontend/src/router/index.ts` (Ruta `/novedades`)
  - `frontend/src/components/layout/Sidebar.vue` (Acceso directo en el menú lateral)

---

## 🔌 Endpoints del Módulo

| Método | Endpoint | Parámetros | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/novedades/catalogo` | Ninguno | Retorna el catálogo completo de novedades con el total acumulado de días/registros y personal único asignado a cada una. |
| `GET` | `/api/novedades/consulta` | `id_sub_novedad`, `mes`, `fecha_inicio`, `fecha_fin`, `q`, `estado`, `page`, `limit` | Consulta analítica con filtros dinámicos cruzados. Retorna KPIs agregados y registros paginados con orden cronológico descendente. |
| `GET` | `/api/novedades/exportar/excel` | `id_sub_novedad`, `mes`, `fecha_inicio`, `fecha_fin`, `q`, `estado` | Genera y descarga un archivo Excel (.xlsx) estilizado con encabezado institucional, resumen de filtros aplicados y detalle de registros. |
| `GET` | `/api/novedades/exportar/pdf` | `id_sub_novedad`, `mes`, `fecha_inicio`, `fecha_fin`, `q`, `estado` | Genera y transmite un reporte vectorial PDF en orientación horizontal (landscape) con encabezados oficiales y tabla de auditoría. |

---

## 📄 Documentos del Módulo

- [Casos de Uso](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/casos_uso.md)
- [Historias de Usuario](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/historias_usuario.md)
- [Reglas de Negocio](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/novedades/reglas_negocio.md)

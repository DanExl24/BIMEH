# Módulo 4: Cronología y Bitácora Diaria (`cronologia`)

## 📌 Descripción General
El módulo de **Cronología y Bitácora Diaria** permite consultar de forma cronológica y retrospectiva la situación operacional de la unidad en cualquier fecha registrada. Funciona como el libro digital de novedades diarias de la unidad militar.

Ofrece un calendario interactivo de disponibilidad mensual con porcentajes por día, métricas consolidadas del mes seleccionado, una tabla detallada con buscador predictivo y filtros por subnovedad, y una matriz visual mensual con todas las novedades del personal.

---

## 🏛️ Arquitectura del Módulo

### Backend
- **Router**: [`backend/app/routers/personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py) (`/api/reportes/dia`, `/api/reportes/calendario`), [`backend/app/routers/dashboard.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/dashboard.py) (`/api/fechas`)
- **Adaptadores de Base de Datos**: [`backend/app/database.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/database.py) (`get_month_dates`)

### Frontend (Feature `src/features/cronologia/` + Capas Compartidas)
- **Vista Principal**: `frontend/src/features/cronologia/views/CronologiaView.vue`
- **Componentes de Feature**:
  - `frontend/src/features/cronologia/components/CronologiaActivityCalendar.vue` (Calendario de fechas con disponibilidad %)
  - `frontend/src/features/cronologia/components/CronologiaMonthlyMetrics.vue` (Tarjetas de métricas del mes)
  - `frontend/src/features/cronologia/components/CronologiaDailyReportTable.vue` (Tabla de novedades diarias con filtros)
  - `frontend/src/features/cronologia/components/CronologiaMonthlyHeatmapMatrix.vue` (Matriz consolidada mensual)
- **Composable de Feature**: `frontend/src/features/cronologia/composables/useCronologiaData.ts`
- **Servicio de Feature**: `frontend/src/features/cronologia/services/cronologia.service.ts`
- **Tipos de Feature**: `frontend/src/features/cronologia/types/cronologia.types.ts`
- **Stores Globales**: `frontend/src/stores/dateStore.ts`

---

## 🔌 Endpoints del Módulo

| Método | Endpoint | Parámetros | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/fechas` | Ninguno | Lista todas las fechas que tienen reportes cargados. |
| `GET` | `/api/reportes/dia` | `fecha` (YYYY-MM-DD) | Lista el estado, subnovedad, descripción y vigencia de todos los integrantes en esa fecha. |
| `GET` | `/api/reportes/calendario` | `mes` (Nombre del mes) | Retorna cada día del mes con su total de personal, disponibles, novedades y % disponibilidad. |

---

## 📄 Documentos del Módulo

- [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/historias_usuario.md)
- [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/reglas_negocio.md)
- [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/casos_uso.md)

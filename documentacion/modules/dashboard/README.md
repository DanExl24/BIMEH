# Módulo 2: Dashboard Operacional y KPIs (`dashboard`)

## 📌 Descripción General
El módulo de **Dashboard Operacional** es el panel principal de control y comando del sistema BIMEH. Permite a los comandantes y directivos responder de forma inmediata a la pregunta: *¿Con qué personal disponible contamos hoy?*

Provee métricas cuantitativas consolidadas del estado de fuerza diario (Total Personal, Disponibles, En Novedades, Porcentaje de Disponibilidad), detección automática de transiciones y cambios respecto al día anterior (*Entraron a novedades*, *Volvieron a disponibles*, *Otros cambios*), gráficos de evolución temporal y desglose porcentual de novedades mediante gráficos interactivos de Apache ECharts.

---

## 🏛️ Arquitectura del Módulo

### Backend
- **Router**: [`backend/app/routers/dashboard.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/dashboard.py)
- **Modelos Pydantic**: [`backend/app/models.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/models.py) (`KPIData`)
- **Dependencias de Filtrado**: [`backend/app/dependencies.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/dependencies.py) (`DISPONIBLE_STATUSES = ["CDO UNIDAD", "AREA OPERACIONES"]`, `get_report_ids_for_filter`)

### Frontend
- **Vista Principal**: `frontend/src/views/DashboardView.vue`
- **Componentes**:
  - `frontend/src/components/dashboard/DashboardKpis.vue` (Tarjetas de métricas y porcentajes)
  - `frontend/src/components/dashboard/DashboardEvolutionChart.vue` (Gráfico de línea temporal de disponibilidad)
  - `frontend/src/components/dashboard/DashboardDistribucionChart.vue` (Gráfico dona de distribución)
  - `frontend/src/components/dashboard/DashboardNovedadesChart.vue` (Barras de novedades frecuentes)
  - `frontend/src/components/dashboard/DashboardCambiosList.vue` (Listado clasificado de transiciones diarias)
- **Stores**: `frontend/src/stores/appStore.ts`, `frontend/src/stores/dateStore.ts`

---

## 🔌 Endpoints del Módulo

| Método | Endpoint | Parámetros | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/fechas` | Ninguno | Retorna la lista de todas las fechas que tienen reportes cargados en orden cronológico. |
| `GET` | `/api/dashboard/kpis` | `fecha`, `mes`, `dia` | Totales y promedios del estado de fuerza (Total, Disponibles, Novedades, %, Cambios vs ayer). |
| `GET` | `/api/dashboard/evolucion` | `mes`, `dia` | Serie de tiempo diaria con la fluctuación de disponibilidad durante el periodo filtrado. |
| `GET` | `/api/dashboard/novedades-frecuentes` | `fecha`, `mes`, `dia` | Conteo ordenado descendente de novedades activas (excluyendo estados de disponible). |
| `GET` | `/api/dashboard/distribucion` | `fecha`, `mes`, `dia` | Agrupación de todas las subnovedades con conteo promedio y porcentaje de participación. |
| `GET` | `/api/dashboard/cambios` | `fecha`, `mes`, `dia` | Listado de integrantes que cambiaron de estado respecto al reporte operacional previo. |

---

## 📄 Documentos del Módulo

- [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md)
- [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/reglas_negocio.md)
- [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/casos_uso.md)

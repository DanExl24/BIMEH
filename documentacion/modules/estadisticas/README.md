# Módulo 5: Estadísticas, Tendencias y Heatmap Global (`estadisticas`)

## 📌 Descripción General
El módulo de **Estadísticas y Tendencias** proporciona herramientas analíticas de alto nivel sobre los acumulados históricos de la unidad. Permite evaluar el impacto global de cada tipo de novedad, identificar qué integrantes presentan mayores acumulados de inactividad o ausencias y visualizar la matriz de calor (Heatmap) integral de toda la fuerza durante el mes seleccionado.

Resulta fundamental para la planeación estratégica de vacaciones, comisiones de servicio, relevos operacionales y auditorías de talento humano.

---

## 🏛️ Arquitectura del Módulo

### Backend
- **Router**: [`backend/app/routers/stats.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/stats.py)
- **Dependencias**: [`backend/app/dependencies.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/dependencies.py) (`DISPONIBLE_STATUSES`)

### Frontend
- **Vista Principal**: `frontend/src/views/EstadisticasView.vue`
- **Integración de Gráficos**: Apache ECharts y Matrices CSS Grid / Flexbox personalizadas.

---

## 🔌 Endpoints del Módulo

| Método | Endpoint | Parámetros | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/stats/ranking` | Ninguno | Retorna el ranking global de subnovedades acumuladas y el Top 15 de personal con más días de novedad. |
| `GET` | `/api/stats/heatmap` | `mes` (Nombre del mes) | Retorna la matriz bidimensional de integrantes y días con sus estados operacionales (D, N, RETIRADO, N/A). |

---

## 📄 Documentos del Módulo

- [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/historias_usuario.md)
- [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/reglas_negocio.md)
- [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/casos_uso.md)

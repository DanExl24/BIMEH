# Módulo 3: Gestión y Expediente de Personal (`personal`)

## 📌 Descripción General
El módulo de **Gestión y Expediente de Personal** permite buscar, consultar y auditar el historial de novedades, constancia de servicio y disponibilidad de cada integrante de la unidad de forma individualizada.

Proporciona un buscador predictivo con autocompletado en tiempo real por cédula o nombre, un expediente digital con cálculo de indicadores de rendimiento (porcentaje histórico disponible vs en novedades, promedio de duración de rachas de novedades consecutivas), líneas de tiempo secuenciales, mapa de calor mensual (matriz de 31 días), mapa de calor anual (matriz completa de 12 meses) y un generador modal de reportes individuales.

---

## 🏛️ Arquitectura del Módulo

### Backend
- **Router**: [`backend/app/routers/personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py)
- **Dependencias**: [`backend/app/dependencies.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/dependencies.py)

### Frontend
- **Vistas**:
  - `frontend/src/views/PersonalView.vue` (Buscador y catálogo general)
  - `frontend/src/views/PersonalDetalleView.vue` (Expediente individual y mapas de calor)
- **Componentes**:
  - `frontend/src/components/personal/PersonalHeaderCard.vue` (Ficha técnica y estado ACTIVO/RETIRADO)
  - `frontend/src/components/personal/PersonalKpiGrid.vue` (Métricas de disponibilidad acumulada y rachas)
  - `frontend/src/components/personal/PersonalTimeline.vue` (Bitácora cronológica individual)
  - `frontend/src/components/personal/PersonalNovedadesChart.vue` (Gráfico de distribución histórica de novedades)
  - `frontend/src/components/personal/PersonalHeatmapMatrix.vue` (Matriz interactiva mensual y anual)
  - `frontend/src/components/modals/ReportGenerationModal.vue` (Modal de exportación parametrizable)

---

## 🔌 Endpoints del Módulo

| Método | Endpoint | Parámetros | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/personal/buscar` | `q` (min 2 caracteres) | Búsqueda predictiva de personal por coincidencia en cédula o nombre (límite 50). |
| `GET` | `/api/personal/{cedula}` | `cedula` (int) | Ficha básica, métricas globales, porcentajes, rachas de novedades y estado de retiro. |
| `GET` | `/api/personal/{cedula}/historial` | `cedula` (int) | Listado cronológico completo de todos los días y novedades reportadas del integrante. |
| `GET` | `/api/personal/{cedula}/acumulado` | `cedula` (int) | Conteo agrupado de días acumulados por tipo de subnovedad para el integrante. |

---

## 📄 Documentos del Módulo

- [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/historias_usuario.md)
- [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/reglas_negocio.md)
- [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/casos_uso.md)

# Reglas de Negocio — Módulo de Cronología (`cronologia`)

---

## 📅 1. Calendario y Fechas Operacionales

### RN-CRON-001
- **Identificador**: `RN-CRON-001`
- **Descripción**: La obtención de fechas de un mes determinado se deriva a partir del mapa de meses oficial en `get_month_dates(mes)`. Si el mes no posee reportes en la base de datos, el endpoint `/api/reportes/calendario` retorna un arreglo vacío `[]`.
- **Motivo**: Garantizar consistencia entre los nombres de los meses en español (ej. `"ENERO"`, `"MAYO"`, `"DICIEMBRE"`) y las fechas formateadas en estándar ISO `YYYY-MM-DD`.
- **Módulos afectados**: `cronologia`, `stats`, `reportes`.
- **Archivos donde se implementa**: [`backend/app/database.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/database.py), [`backend/app/routers/personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py) (Líneas 195–234).
- **Endpoints relacionados**: `GET /api/reportes/calendario`
- **Historias de usuario relacionadas**: [HU-CRON-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/historias_usuario.md#hu-cron-001)

---

### RN-CRON-002
- **Identificador**: `RN-CRON-002`
- **Descripción**: Para cada día evaluado en el calendario mensual, el porcentaje de disponibilidad se calcula estrictamente como:
  $$\text{Disponibilidad (\%)} = \left(\frac{\text{Disponibles (CDO UNIDAD + AREA OPERACIONES)}}{\text{Total Personal del Reporte}}\right) \times 100$$
  redondeado a 1 decimal. Si un día no tiene integrantes (`total = 0`), la disponibilidad es `0.0`.
- **Motivo**: Proveer una escala homogénea que permita comparar la operatividad entre distintos días del mes.
- **Módulos afectados**: `cronologia`.
- **Archivos donde se implementa**: [`backend/app/routers/personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py) (Líneas 224–232).
- **Endpoints relacionados**: `GET /api/reportes/calendario`
- **Historias de usuario relacionadas**: [HU-CRON-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/historias_usuario.md#hu-cron-001)

---

## 📋 2. Ordenamiento y Filtrado de Bitácora

### RN-CRON-003
- **Identificador**: `RN-CRON-003`
- **Descripción**: La lista de registros de personal en el endpoint `/api/reportes/dia` debe ordenarse de manera obligatoria y ascendente por el nombre completo del integrante (`ORDER BY p.nombre ASC`).
- **Motivo**: Facilitar la lectura militar estandarizada por orden alfabético de apellidos y nombres en el pase de lista diario.
- **Módulos afectados**: `cronologia`.
- **Archivos donde se implementa**: [`backend/app/routers/personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py) (Línea 182).
- **Endpoints relacionados**: `GET /api/reportes/dia`
- **Historias de usuario relacionadas**: [HU-CRON-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/historias_usuario.md#hu-cron-002)

---

### RN-CRON-004
- **Identificador**: `RN-CRON-004`
- **Descripción**: La matriz de calor mensual agrupa a todos los integrantes que hayan tenido al menos un registro en cualquiera de los reportes del mes consultado, ordenados alfabéticamente.
- **Motivo**: Garantizar que ningún integrante activo durante el mes quede excluido del consolidado visual.
- **Módulos afectados**: `cronologia`, `estadisticas`.
- **Archivos donde se implementa**: [`backend/app/routers/stats.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/stats.py) (Líneas 57–64).
- **Endpoints relacionados**: `GET /api/stats/heatmap`
- **Historias de usuario relacionadas**: [HU-CRON-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/historias_usuario.md#hu-cron-003)

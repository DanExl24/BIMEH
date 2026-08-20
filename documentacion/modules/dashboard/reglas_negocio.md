# Reglas de Negocio — Módulo de Dashboard Operacional (`dashboard`)

---

## 🧮 1. Cálculos de Disponibilidad y Estado de Fuerza

### RN-DASH-001
- **Identificador**: `RN-DASH-001`
- **Descripción**: La condición de personal "DISPONIBLE" está restringida estrictamente a los registros que contengan como subnovedad `"CDO UNIDAD"` o `"AREA OPERACIONES"`.
- **Motivo**: Solo el personal en comando de unidad o desplegado en área de operaciones se encuentra efectivamente en servicio activo e inmediato para la misión. Cualquier otra subnovedad (permiso, vacaciones, comisión, excusa, hospitalización, etc.) constituye una indisponibilidad temporal.
- **Módulos afectados**: `dashboard`, `personal`, `cronologia`, `estadisticas`, `reportes`.
- **Archivos donde se implementa**: [`backend/app/dependencies.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/dependencies.py) (Línea 28: `DISPONIBLE_STATUSES = ["CDO UNIDAD", "AREA OPERACIONES"]`), [`backend/app/routers/dashboard.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/dashboard.py).
- **Endpoints relacionados**: `GET /api/dashboard/kpis`, `GET /api/dashboard/evolucion`, `GET /api/dashboard/distribucion`
- **Historias de usuario relacionadas**: [HU-DASH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md#hu-dash-001), [HU-DASH-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md#hu-dash-003)

---

### RN-DASH-002
- **Identificador**: `RN-DASH-002`
- **Descripción**: El cálculo del porcentaje de disponibilidad se realiza mediante la fórmula:
  $$\text{Disponibilidad (\%)} = \left(\frac{\text{Personal Disponible}}{\text{Total Personal Registrado}}\right) \times 100$$
  redondeado a un dígito decimal. Si el total de personal es cero (`0`), la disponibilidad es obligatoriamente `0.0`.
- **Motivo**: Estandarizar el indicador de mando y prevenir errores de división por cero cuando se consultan periodos sin registros.
- **Módulos afectados**: `dashboard`, `cronologia`, `personal`.
- **Archivos donde se implementa**: [`backend/app/routers/dashboard.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/dashboard.py) (Líneas 86, 146).
- **Endpoints relacionados**: `GET /api/dashboard/kpis`, `GET /api/dashboard/evolucion`
- **Historias de usuario relacionadas**: [HU-DASH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md#hu-dash-001), [HU-DASH-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md#hu-dash-003)

---

### RN-DASH-003
- **Identificador**: `RN-DASH-003`
- **Descripción**: Cuando no se envían parámetros temporales (`fecha=None`, `mes=None`, `dia=None`), el backend consulta automáticamente la última fecha registrada en la base de datos (`SELECT fecha FROM REPORTES ORDER BY fecha DESC LIMIT 1`).
- **Motivo**: Permitir que el dashboard cargue siempre la situación operacional más reciente sin requerir intervención manual del usuario.
- **Módulos afectados**: `dashboard`.
- **Archivos donde se implementa**: [`backend/app/routers/dashboard.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/dashboard.py) (Líneas 41–46, 167–172, 204–209, 257–262).
- **Endpoints relacionados**: `GET /api/dashboard/kpis`, `GET /api/dashboard/novedades-frecuentes`, `GET /api/dashboard/distribucion`, `GET /api/dashboard/cambios`
- **Historias de usuario relacionadas**: [HU-DASH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md#hu-dash-001)

---

## 🔄 2. Detección de Transiciones y Cambios de Estado

### RN-DASH-004
- **Identificador**: `RN-DASH-004`
- **Descripción**: La detección de cambios se realiza comparando el conjunto de tuplas `(id_personal, id_sub_novedad)` del reporte actual contra el reporte cronológicamente inmediatamente anterior (`fecha < fecha_actual ORDER BY fecha DESC LIMIT 1`).
  - Si el estado previo era disponible y el actual es novedad $\rightarrow$ Clasifica como `entraron_novedades`.
  - Si el estado previo era novedad y el actual es disponible $\rightarrow$ Clasifica como `volvieron_disponibles`.
  - Si cambió entre subnovedades no disponibles o causó baja $\rightarrow$ Clasifica como `otros_cambios`.
- **Motivo**: Automatizar la auditoría de relevos y novedades diarias que anteriormente tomaba horas de revisión manual en libros de novedades.
- **Módulos afectados**: `dashboard`.
- **Archivos donde se implementa**: [`backend/app/routers/dashboard.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/dashboard.py) (Líneas 248–372).
- **Endpoints relacionados**: `GET /api/dashboard/cambios`, `GET /api/dashboard/kpis` (cálculo de `cambios_vs_ayer`).
- **Historias de usuario relacionadas**: [HU-DASH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md#hu-dash-001), [HU-DASH-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md#hu-dash-002)

---

## 📊 3. Agregaciones y Filtros Temporales

### RN-DASH-005
- **Identificador**: `RN-DASH-005`
- **Descripción**: Cuando se consulta por mes o anual (múltiples días), las métricas del KPI representan el **promedio diario redondeado** de efectivos en el periodo, mientras que `cambios_vs_ayer` representa la sumatoria total de eventos de transición ocurridos en el lapso.
- **Motivo**: Ofrecer una representación estadística fidedigna del promedio de fuerza disponible durante un mes completo o a lo largo del año.
- **Módulos afectados**: `dashboard`.
- **Archivos donde se implementa**: [`backend/app/routers/dashboard.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/dashboard.py) (Líneas 83–114).
- **Endpoints relacionados**: `GET /api/dashboard/kpis`
- **Historias de usuario relacionadas**: [HU-DASH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md#hu-dash-001), [HU-DASH-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md#hu-dash-003)

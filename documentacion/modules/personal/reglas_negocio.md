# Reglas de Negocio — Módulo de Personal (`personal`)

---

## 🔍 1. Búsqueda y Coincidencia

### RN-PERS-001
- **Identificador**: `RN-PERS-001`
- **Descripción**: La búsqueda predictiva de personal exige una longitud mínima de dos (2) caracteres en el parámetro de consulta `q` (`min_length=2`).
- **Motivo**: Prevenir consultas masivas indiscriminadas con cadenas de 1 solo carácter que sobrecarguen la base de datos con escaneos secuenciales innecesarios.
- **Módulos afectados**: `personal`.
- **Archivos donde se implementa**: [`backend/app/routers/personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py) (Línea 10), `frontend/src/features/personal/composables/usePersonalAutocomplete.ts`.
- **Endpoints relacionados**: `GET /api/personal/buscar`
- **Historias de usuario relacionadas**: [HU-PERS-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/historias_usuario.md#hu-pers-001)

---

### RN-PERS-002
- **Identificador**: `RN-PERS-002`
- **Descripción**: La búsqueda realiza coincidencia tanto sobre el campo numérico `cedula` (casteado a texto) como sobre el campo `nombre` en mayúsculas, limitando la respuesta a 50 resultados.
- **Motivo**: Permitir al usuario encontrar al integrante ya sea digitando fragmentos de su número de identificación o parte de sus apellidos/nombres indistintamente.
- **Módulos afectados**: `personal`.
- **Archivos donde se implementa**: [`backend/app/routers/personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py) (Líneas 14–20), `frontend/src/features/personal/services/personal.service.ts`.
- **Endpoints relacionados**: `GET /api/personal/buscar`
- **Historias de usuario relacionadas**: [HU-PERS-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/historias_usuario.md#hu-pers-001)

---

## 📊 2. Métricas y Algoritmo de Rachas

### RN-PERS-003
- **Identificador**: `RN-PERS-003`
- **Descripción**: El estado operacional de un integrante se define como:
  - `ACTIVO`: Si el campo `fecha_retiro` en la tabla `PERSONAL` es nulo (`NULL`).
  - `RETIRADO`: Si el campo `fecha_retiro` contiene una fecha válida. A partir de esa fecha inclusive, cualquier consulta en el calendario clasifica al integrante como inactivo/retirado (`R`).
- **Motivo**: Mantener el historial histórico de los efectivos desvinculados sin que afecten la disponibilidad activa de fechas posteriores a su baja.
- **Módulos afectados**: `personal`, `cronologia`, `estadisticas`, `reportes`.
- **Archivos donde se implementa**: [`backend/app/routers/personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py) (Líneas 16, 35), [`backend/app/routers/stats.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/stats.py) (Líneas 88–94), `frontend/src/utils/personal.utils.ts`.
- **Endpoints relacionados**: `GET /api/personal/buscar`, `GET /api/personal/{cedula}`, `GET /api/stats/heatmap`
- **Historias de usuario relacionadas**: [HU-PERS-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/historias_usuario.md#hu-pers-001), [HU-PERS-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/historias_usuario.md#hu-pers-002)

---

### RN-PERS-004
- **Identificador**: `RN-PERS-004`
- **Descripción**: El indicador `promedio_duracion_novedades` se calcula detectando secuencias continuas e ininterrumpidas de días en estado no disponible (rachas). Se calcula el promedio sumando las longitudes de todas las rachas y dividiendo por la cantidad de rachas registradas:
  $$\text{Promedio Rachas} = \frac{\sum \text{Días de cada racha}}{\text{Cantidad total de rachas}}$$
  redondeado a 1 decimal. Si nunca ha tenido novedades, el valor es `0.0`.
- **Motivo**: Identificar si las ausencias del personal corresponden a eventos prolongados (ej. licencias o incapacidades de 15 días) o a interrupciones breves y recurrentes de 1 día.
- **Módulos afectados**: `personal`.
- **Archivos donde se implementa**: [`backend/app/routers/personal.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/personal.py) (Líneas 79–96), `frontend/src/features/personal/components/PersonalKpiGrid.vue`.
- **Endpoints relacionados**: `GET /api/personal/{cedula}`
- **Historias de usuario relacionadas**: [HU-PERS-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/historias_usuario.md#hu-pers-002)

---

## 📅 3. Mapas de Calor y Parametrización

### RN-PERS-005
- **Identificador**: `RN-PERS-005`
- **Descripción**: En la matriz de calor, los días en los que no exista un reporte registrado en la base de datos se etiquetan como `"-"` / `"N/A"` y se renderizan con estilo deshabilitado/gris neutro.
- **Motivo**: Distinguir claramente entre un día en el que el integrante estuvo de novedad frente a un día donde no se generó reporte operacional en la unidad.
- **Módulos afectados**: `personal`, `cronologia`, `estadisticas`.
- **Archivos donde se implementa**: `frontend/src/features/personal/components/PersonalHeatmapMatrix.vue`, [`backend/app/routers/stats.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/stats.py) (Línea 97).
- **Endpoints relacionados**: `GET /api/personal/{cedula}/historial`, `GET /api/stats/heatmap`
- **Historias de usuario relacionadas**: [HU-PERS-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/historias_usuario.md#hu-pers-003)

---

### RN-PERS-006
- **Identificador**: `RN-PERS-006`
- **Descripción**: La exportación individual de expediente debe admitir el filtrado opcional por subnovedad (`subnovedad=...`) y por mes (`mes=...`), aplicando cláusulas `WHERE` adicionales sobre la consulta a `REGISTRO_PERSONAL`.
- **Motivo**: Permitir generar constancias y certificaciones específicas (ej. constancia exclusiva de días de permiso o vacaciones de un integrante).
- **Módulos afectados**: `personal`, `reportes`.
- **Archivos donde se implementa**: [`backend/app/routers/exportar.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/exportar.py) (Líneas 144–173, 440–510), `frontend/src/features/reportes/services/reportes.service.ts`.
- **Endpoints relacionados**: `GET /api/exportar/excel`, `GET /api/exportar/csv`, `GET /api/exportar/pdf`
- **Historias de usuario relacionadas**: [HU-PERS-004](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/historias_usuario.md#hu-pers-004)

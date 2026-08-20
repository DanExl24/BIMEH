# Casos de Uso — Módulo de Dashboard Operacional (`dashboard`)

---

## CU-DASH-001: Consulta de KPIs y Estado de Fuerza Diario

### Actores
- **Principal**: Comandante de Unidad / Oficial de Personal.
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
1. El usuario debe estar autenticado en el sistema.
2. Deben existir reportes operacionales cargados en la base de datos.

### Flujo Principal
1. El usuario ingresa a la vista principal del sistema (`DashboardView.vue`).
2. El frontend obtiene la lista de fechas disponibles invocando `GET /api/fechas`.
3. El frontend solicita las métricas del día activo a través de `GET /api/dashboard/kpis?fecha=YYYY-MM-DD`.
4. El backend calcula los conteos de personal total, disponibles y en novedades.
5. El backend calcula el porcentaje de disponibilidad y la cantidad de cambios respecto al día previo.
6. El backend responde con el modelo `KPIData`.
7. El componente `DashboardKpis.vue` renderiza las 5 tarjetas de métricas operacionales.

### Flujos Alternativos
- **A1: No existen reportes para la fecha**: El backend retorna todos los valores en `0` y disponibilidad `0.0`. La interfaz muestra las tarjetas con valor cero sin generar excepciones en pantalla.

---

## CU-DASH-002: Auditoría de Transiciones y Cambios de Novedades

### Actores
- **Principal**: Analista de Personal.
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
- Debe existir al menos un reporte operacional registrado.

### Flujo Principal
1. En el Dashboard, el usuario visualiza el panel inferior de "Novedades Diarias".
2. El frontend realiza la llamada `GET /api/dashboard/cambios?fecha=YYYY-MM-DD`.
3. El backend localiza el reporte inmediatamente anterior.
4. El backend compara registro por registro el estado de cada persona entre ambos días.
5. El backend segrega las transiciones en: `entraron_novedades`, `volvieron_disponibles` y `otros_cambios`.
6. El frontend renderiza el componente `DashboardCambiosList.vue` con pestañas interactivas y badges de color.

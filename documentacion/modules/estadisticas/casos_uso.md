# Casos de Uso — Módulo de Estadísticas (`estadisticas`)

---

## CU-STAT-001: Análisis de Rankings y Tendencias de Novedades

### Actores
- **Principal**: Comandante / Oficial de Personal.
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
- Usuario autenticado con permisos de consulta o administración.

### Flujo Principal
1. El usuario hace clic en **"Estadísticas"** en el menú de navegación lateral.
2. La vista `src/features/estadisticas/views/EstadisticasView.vue` ejecuta de forma concurrente:
   - `GET /api/stats/ranking` mediante `estadisticas.service.ts`.
   - `GET /api/stats/heatmap?mes=...` mediante `cronologia.service.ts`.
3. El backend procesa las consultas de agregación en PostgreSQL.
4. El frontend renderiza el gráfico de barras horizontales con el ranking de subnovedades y la lista del Top 15 de efectivos con más novedades acumuladas.
5. El frontend renderiza la matriz Heatmap global con scroll interactivo.
6. El usuario analiza qué tipos de novedades han impactado en mayor medida la fuerza efectiva y puede cambiar el mes en la cabecera para ver la evolución del Heatmap.

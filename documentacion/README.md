# 📚 Documentación Funcional y Técnica Modular del Sistema BIMEH

**BIMEH** (*Sistema de Control Operacional y Mapa de Calor del Personal*) es una solución integral diseñada para centralizar, auditar, sincronizar y visualizar el estado de fuerza, disponibilidad e historial de novedades del personal militar/operativo de la unidad.

---

## 🗺️ Mapa de Módulos Funcionales

La documentación se encuentra dividida modularmente en la carpeta [`documentacion/modules/`](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules):

| Módulo | Descripción Funcional | Documentos Disponibles |
| :--- | :--- | :--- |
| [**1. Autenticación y Control de Acceso (`auth`)**](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/README.md) | Gestión de sesiones JWT, roles (`ADMINISTRATIVO`, `CONSULTA`), bcrypt, verificación de Google Drive y protección de rutas. | [README](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/README.md) \| [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md) \| [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md) \| [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/casos_uso.md) |
| [**2. Dashboard Operacional (`dashboard`)**](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/README.md) | Panel de control de disponibilidad, KPIs rápidos, detección de cambios vs ayer, gráficos de evolución y distribución por filtros temporales. | [README](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/README.md) \| [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/historias_usuario.md) \| [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/reglas_negocio.md) \| [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/dashboard/casos_uso.md) |
| [**3. Gestión y Expediente de Personal (`personal`)**](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/README.md) | Buscador predictivo, expediente individual, cálculo de rachas de novedades, mapas de calor (mensual y anual) y modal de exportación individual. | [README](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/README.md) \| [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/historias_usuario.md) \| [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/reglas_negocio.md) \| [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/personal/casos_uso.md) |
| [**4. Cronología y Bitácora Diaria (`cronologia`)**](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/README.md) | Bitácora histórica diaria, calendario mensual de actividad y disponibilidad porcentual por fecha, tabla interactiva y matriz de novedades. | [README](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/README.md) \| [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/historias_usuario.md) \| [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/reglas_negocio.md) \| [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/cronologia/casos_uso.md) |
| [**5. Estadísticas y Tendencias (`estadisticas`)**](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/README.md) | Ranking global de subnovedades, Top 15 de personal con mayor cantidad de novedades y matriz Heatmap global del mes para planeación. | [README](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/README.md) \| [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/historias_usuario.md) \| [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/reglas_negocio.md) \| [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/estadisticas/casos_uso.md) |
| [**6. Centro de Exportación y Reportes (`reportes`)**](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/README.md) | Motor de generación de reportes multi-formato (CSV UTF-8-BOM, Excel con comentarios, PDF vectorial) y modalidades (diario, mensual, ágil, BD). | [README](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/README.md) \| [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/historias_usuario.md) \| [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/reglas_negocio.md) \| [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/reportes/casos_uso.md) |
| [**7. Sincronización e Ingesta (`sincronizar`)**](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/README.md) | Carga manual Drag-and-Drop (Excel/JSON), validación de esquemas, resolución de conflictos y sincronización automática con Google Drive vía OAuth. | [README](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/README.md) \| [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/historias_usuario.md) \| [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/reglas_negocio.md) \| [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/sincronizar/casos_uso.md) |

---

## 🔗 Enlaces a Documentación Complementaria

- [Manual Técnico General](file:///c:/Users/alejo/Downloads/automPYdrive/docs/manual_tecnico.md): Arquitectura de software, modelo relacional de PostgreSQL, instrucciones de despliegue y mantenimiento.
- [Manual de Usuario General](file:///c:/Users/alejo/Downloads/automPYdrive/docs/manual_usuario.md): Guía de navegación operativa paso a paso.
- [Guía de Integración Electron / Desktop](file:///c:/Users/alejo/Downloads/automPYdrive/docs/electron_setup.md): Empaquetado como ejecutable de escritorio.

---

## 🔄 Matriz de Trazabilidad Global

Toda la documentación sigue el estándar estricto de trazabilidad:
$$\text{Historia de Usuario (HU)} \longleftrightarrow \text{Regla de Negocio (RN)} \longleftrightarrow \text{Endpoint API REST} \longleftrightarrow \text{Controller / Router} \longleftrightarrow \text{Componente / Vista Frontend}$$

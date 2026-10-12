# Historias de Usuario — Módulo de Centro de Mando S-1 & Inteligencia Preventiva (`mando`)

---

# HU-MANDO-001

## Historia
**Como** comandante de batallón u oficial S-3 / S-1  
**Quiero** identificar en un radar de fatiga a los integrantes de la unidad que llevan más de 30 o 45 días continuos en servicio sin descanso  
**Para** planificar oportunamente los relevos de combate, conceder permisos de bienestar y prevenir la degradación física y psicológica del personal desplegado.

## Descripción
El usuario ingresa a la vista del Centro de Mando S-1 (`MandoS1View.vue`) o visualiza el componente de radar de fatiga en el dashboard (`DashboardFatigueRadar.vue`). El sistema consulta `GET /api/alertas/fatiga` con un umbral configurable de días (30 por defecto). Para cada efectivo disponible en el reporte evaluado (`AREA OPERACIONES` o `CDO UNIDAD`), el sistema reconstruye hacia atrás su historial en hasta 90 reportes continuos. Si el efectivo acumula $\ge 30$ días sin registrar permisos o vacaciones, se emite una alerta clasificada como `ALTO` ($\ge 30$ días) o `CRITICO` ($\ge 45$ días) con recomendaciones automáticas de comando.

## Criterios de Aceptación
- Solo se evalúan efectivos activos (sin fecha de retiro) y que estén en condición disponible en el reporte evaluado.
- El conteo de días continuos se detiene de inmediato al encontrar una subnovedad de descanso (`PERMISO` o `VACACIONES`).
- Se debe categorizar la alerta en tres niveles: `CRITICO` ($\ge 45$), `ALTO` ($\ge 30$) y `MODERADO` ($< 30$).
- La respuesta debe ordenar a los efectivos de forma descendente por días continuos acumulados.
- Cada elemento debe incluir: `id_personal`, `cedula`, `nombre`, `dias_continuos`, `estado_actual`, `nivel_alerta` y `recomendacion`.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-MANDO-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/reglas_negocio.md#rn-mando-001)
- **Endpoints relacionados**: `GET /api/alertas/fatiga`
- **Componentes frontend relacionados**: `frontend/src/features/mando/views/MandoS1View.vue`, `frontend/src/features/dashboard/components/DashboardFatigueRadar.vue`, `frontend/src/features/dashboard/services/alertas.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/alertas.py` (`get_alertas_fatiga`)

---

# HU-MANDO-002

## Historia
**Como** Oficial S-1 o Jefe de Sanidad Militar  
**Quiero** auditar a los efectivos con ausentismos médicos reiterados o prolongados  
**Para** identificar quiénes ameritan evaluación formal ante la Junta Médico-Laboral Militar y gestionar el seguimiento de sanidad de la unidad.

## Descripción
En la sección de Sanidad del Centro de Mando, el usuario consulta `GET /api/alertas/sanidad` con un umbral de días acumulados (15 días por defecto). El sistema analiza todas las apariciones del militar en novedades de salud (`INCAPACIDAD`, `HOSPITALIZADOS`, `TRATAMIENTO LESIHMANIASIS`) hasta la fecha de corte. Si el acumulado es igual o superior a 30 días, se clasifica como `JUNTA_MEDICA_SUGERIDA`, recomendando remitir la historia clínica a evaluación médico-laboral reglamentaria.

## Criterios de Aceptación
- El filtro debe incluir subnovedades cuyo nombre contenga `'INCAPACIDAD'`, `'HOSPITAL'` o `'LESIHMANIASIS'`.
- Se deben excluir los militares que ya tengan fecha de retiro registrada.
- Debe retornar: `id_personal`, `cedula`, `nombre`, `total_dias_sanidad`, `episodios`, `novedades`, `ultima_fecha`, `clasificacion` y `recomendacion`.
- Si el militar tiene $\ge 30$ días acumulados, la clasificación obligatoria es `JUNTA_MEDICA_SUGERIDA`.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-MANDO-002](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/reglas_negocio.md#rn-mando-002)
- **Endpoints relacionados**: `GET /api/alertas/sanidad`
- **Componentes frontend relacionados**: `frontend/src/features/mando/views/MandoS1View.vue`, `frontend/src/features/dashboard/services/alertas.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/alertas.py` (`get_alertas_sanidad`)

---

# HU-MANDO-003

## Historia
**Como** comandante de unidad u oficial S-1  
**Quiero** proyectar la disponibilidad de tropa en horizontes de 7, 15 y 30 días  
**Para** prever la recuperación del pie de fuerza disponible a medida que el personal culmina sus permisos, vacaciones o incapacidades temporales.

## Descripción
El usuario visualiza el widget de Proyección de Fuerza (`DashboardForceProjection.vue`) o la sección correspondiente en `MandoS1View.vue`. El sistema consume `GET /api/alertas/proyeccion`. Recupera los efectivos en novedad en la fecha base que cuenten con `fecha_final` informada. Al calcular los días restantes respecto a la fecha base, el backend estima cuántos efectivos retornarán en los próximos 7, 15 y 30 días, proyectando el total de combatientes disponibles y el porcentaje de operatividad esperado.

## Criterios de Aceptación
- La fecha base se resuelve con base en los filtros temporales activos (`mes`, `dia`, `fecha`) o el último reporte registrado.
- Se consideran reincorporaciones únicamente aquellos registros cuya `fecha_final` sea válida, no vacía y posterior o igual a la fecha base.
- Se calculan tres horizontes: 7 días, 15 días y 30 días.
- Para cada horizonte se debe reportar: `estimados_disponibles`, `porcentaje`, `reincorporaciones` y `salidas_programadas`.
- El total proyectado no puede superar el pie de fuerza total registrado (`min(total_efectivo, disp_actual + reincorporaciones)`).
- Se debe incluir un listado con los próximos 25 movimientos detallados con nombre, novedad, fecha de finalización y días restantes.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-MANDO-003](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/reglas_negocio.md#rn-mando-003)
- **Endpoints relacionados**: `GET /api/alertas/proyeccion`
- **Componentes frontend relacionados**: `frontend/src/features/mando/views/MandoS1View.vue`, `frontend/src/features/dashboard/components/DashboardForceProjection.vue`, `frontend/src/features/dashboard/services/alertas.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/alertas.py` (`get_proyeccion_fuerza`)

---

# HU-MANDO-004

## Historia
**Como** Oficial de Servicio o Ayudante de Comando  
**Quiero** consultar y copiar el texto formal del Parte Diario Militar ("El Parte de las 06:00")  
**Para** emitir el radiograma matutino oficial a la Brigada y a la Comandancia sin necesidad de redactarlo manualmente.

## Descripción
El usuario hace clic en el botón *"El Parte de las 06:00"* desde el Dashboard o Centro de Mando. Se despliega el modal `CommandBriefingModal.vue`, el cual carga `GET /api/alertas/parte-diario`. El sistema entrega el consolidado de fuerza clasificado en 4 categorías militares estándar (Sanidad, Descanso/Bienestar, Servicio/Instrucción, Administrativas) y redacta en tiempo real el radiograma castrense completo con formato oficial del Ejército Nacional. El usuario puede copiar el texto formateado al portapapeles mediante un solo clic.

## Criterios de Aceptación
- El endpoint debe admitir `mes`, `dia` o `fecha` exacta.
- La agrupación de novedades debe obedecer la taxonomía doctrinal:
  - Sanidad: `INCAPACIDAD`, `HOSPITALIZADOS`, `TRATAMIENTO LESIHMANIASIS`.
  - Descanso: `PERMISO`, `VACACIONES`.
  - Servicio: `COMISION DE SERVICIO`, `CURSOS`, `CURSO DE LEY`, `CICLO CODE`, `REENTREANAMIENTO`.
  - Administrativas: restante de novedades.
- El texto del radiograma debe incluir encabezado institucional, resumen numérico, desglose de disponibles (Área de Operaciones vs Comando de Unidad) y alertas críticas de mando.
- La interfaz debe disponer de un botón de copiado con confirmación visual interactiva.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-MANDO-004](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/reglas_negocio.md#rn-mando-004), [RN-MANDO-005](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/reglas_negocio.md#rn-mando-005)
- **Endpoints relacionados**: `GET /api/alertas/parte-diario`
- **Componentes frontend relacionados**: `frontend/src/features/dashboard/components/CommandBriefingModal.vue`, `frontend/src/features/mando/views/MandoS1View.vue`, `frontend/src/features/dashboard/views/DashboardView.vue`
- **Controllers/Services relacionados**: `backend/app/routers/alertas.py` (`get_parte_diario`)

---

# HU-MANDO-005

## Historia
**Como** Comandante de Batallón u Oficial S-1  
**Quiero** descargar el Parte Diario en formato PDF con diseño institucional y bloques de firma  
**Para** archivar físicamente el boletín diario y presentarlo en las reuniones de Estado Mayor de la Brigada.

## Descripción
En la vista de Centro de Mando o en el modal del Parte Diario, el usuario selecciona *"Descargar PDF"*. El backend ejecuta `GET /api/exportar/pdf/parte-diario` utilizando ReportLab. Se genera un documento formal en tamaño carta con encabezado de la República de Colombia, tablas de desglose porcentual, indicadores de alerta y áreas de firma para el Oficial S-1 y el Comandante del Batallón.

## Criterios de Aceptación
- El PDF debe generarse al vuelo en memoria (`StreamingResponse`) sin dejar archivos temporales huérfanos en disco.
- Debe incluir encabezado oficial del Batallón de Infantería N° 12 (BIMEJ 12).
- Debe presentar tablas organizadas con bordes estilizados y paleta de colores institucionales.
- Debe contener espacios reglamentarios para firma y post-firma del Oficial S-1 y Comandante de Batallón.
- La cabecera HTTP de respuesta debe especificar `Content-Type: application/pdf` y `Content-Disposition: inline`.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-MANDO-005](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/reglas_negocio.md#rn-mando-005)
- **Endpoints relacionados**: `GET /api/exportar/pdf/parte-diario`
- **Componentes frontend relacionados**: `frontend/src/features/mando/views/MandoS1View.vue`, `frontend/src/features/dashboard/components/CommandBriefingModal.vue`
- **Controllers/Services relacionados**: `backend/app/routers/exportar.py` (`exportar_pdf_parte_diario`)

---

# HU-MANDO-006

## Historia
**Como** usuario directivo del sistema  
**Quiero** disponer de una vista dedicada de Centro de Mando S-1 accesible desde el menú principal  
**Para** concentrar todas las herramientas analíticas de inteligencia preventiva en un solo panel de control táctico.

## Descripción
Se añade la ruta `/mando-s1` protegida por autenticación y enlazada en la barra de navegación superior (Navbar). Esta vista integra en tiempo real: los KPIs de situación de fuerza, el acceso al Parte Diario y PDF oficial, la cuadrícula del Radar de Fatiga Operacional con control de umbral interactivo, la Proyección de Fuerza a 7/15/30 días con desglose de próximos movimientos y la tabla de auditoría de ausentismos médicos de sanidad. Todo sincronizado reactivamente con el selector de mes y día operacional.

## Criterios de Aceptación
- La ruta `/mando-s1` debe estar registrada en `src/router/index.ts` con meta `requiresAuth: true`.
- Debe reaccionar a cambios en el `dateStore` de forma sincronizada con el Dashboard.
- Debe ofrecer conmutador de umbral de fatiga (30, 45 días) e interactividad en todas las secciones.
- Debe poseer diseño responsivo con estética moderna de mando militar (glassmorphism, paleta slate/cyan).

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-MANDO-006](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/reglas_negocio.md#rn-mando-006)
- **Endpoints relacionados**: `GET /api/alertas/fatiga`, `GET /api/alertas/sanidad`, `GET /api/alertas/proyeccion`, `GET /api/alertas/parte-diario`
- **Componentes frontend relacionados**: `frontend/src/features/mando/views/MandoS1View.vue`, `frontend/src/components/common/Navbar.vue`, `frontend/src/router/index.ts`
- **Controllers/Services relacionados**: `backend/app/routers/alertas.py`

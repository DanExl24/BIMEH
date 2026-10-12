# Casos de Uso — Módulo de Centro de Mando S-1 & Inteligencia Preventiva (`mando`)

---

## CU-MANDO-001: Monitoreo del Radar de Fatiga Operacional y Turnos de Relevo

### Actores
- **Principal**: Comandante de Batallón / Oficial de Operaciones (S-3) / Oficial de Personal (S-1).
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
1. El usuario debe estar autenticado con rol `ADMINISTRATIVO` o `CONSULTA`.
2. Existen reportes diarios cargados en la base de datos para el período evaluado.

### Flujo Principal
1. El usuario accede a la vista de mando (`/mando-s1`) o visualiza el widget en el Dashboard principal (`DashboardFatigueRadar.vue`).
2. El frontend realiza la petición `GET /api/alertas/fatiga` enviando los filtros de período (`mes`, `dia` o `fecha`) y el umbral de días mínimos continuos (por defecto 30).
3. El backend resuelve el reporte objetivo (`_resolve_target_report`) y analiza hasta 90 reportes cronológicamente anteriores.
4. Para cada efectivo disponible en el reporte evaluado (`AREA OPERACIONES` o `CDO UNIDAD`), el backend calcula la racha continua de días en servicio retrocediendo reporte a reporte hasta encontrar un estado de descanso (`PERMISO` o `VACACIONES`).
5. Aquellos efectivos cuya racha iguale o supere el umbral son clasificados en niveles de severidad:
   - **CRÍTICO** ($\ge 45$ días): Se recomienda relevo o permiso operacional inmediato.
   - **ALTO** ($\ge 30$ días): Se recomienda programar descanso próximo.
   - **MODERADO** ($< 30$ días): Seguimiento preventivo.
6. El frontend renderiza las tarjetas de efectivos en riesgo con indicador visual de días acumulados, nivel de alerta y recomendación de comando.

### Flujos Alternativos
- **A1: Ningún efectivo supera el umbral**: El backend retorna una lista vacía `[]`. La interfaz presenta un estado favorable indicando que no hay alertas de fatiga crítica para el período.

---

## CU-MANDO-002: Auditoría de Casos Críticos de Sanidad Militar y Recomendación de Junta Médica

### Actores
- **Principal**: Oficial S-1 / Médico Jefe de la Sección de Sanidad.
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
- El usuario se encuentra en la vista de Centro de Mando (`MandoS1View.vue`).

### Flujo Principal
1. En la pestaña o sección de Sanidad del Centro de Mando, el usuario consulta el estado de las novedades médicas.
2. El frontend solicita `GET /api/alertas/sanidad` con el parámetro `dias_min=15` y los filtros temporales activos.
3. El backend ejecuta la agregación sobre las subnovedades de carácter médico (`INCAPACIDAD`, `HOSPITALIZADOS`, `TRATAMIENTO LESIHMANIASIS`) hasta la fecha de corte.
4. Se agrupan los registros por militar activo calculando el total de días acumulados y la cantidad de episodios distintos.
5. Se asigna la clasificación:
   - $\ge 30$ días: `JUNTA_MEDICA_SUGERIDA` con recomendación de remisión a Junta Médico-Laboral Militar.
   - $15$ a $29$ días: `SEGUIMIENTO_SANIDAD` con recomendación de control ambulatorio continuo.
6. El frontend despliega la tabla de sanidad militar con badges de clasificación y detalle de novedades asociadas.

---

## CU-MANDO-003: Consulta de la Proyección de Fuerza Disponible (Horizontes a 7, 15 y 30 Días)

### Actores
- **Principal**: Comandante de Batallón / Oficial S-1.
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
- Existen registros de novedades con `fecha_final` informada (permisos, licencias, vacaciones, incapacidades temporales).

### Flujo Principal
1. El usuario visualiza la sección de Proyección de Fuerza en el Centro de Mando (`DashboardForceProjection.vue` o `MandoS1View.vue`).
2. El frontend solicita `GET /api/alertas/proyeccion?dias=30` junto con los filtros de fecha.
3. El backend calcula el efectivo actual (total, disponibles, novedades y porcentaje de operatividad base).
4. El backend busca todos los efectivos en novedad en el reporte evaluado que cuenten con `fecha_final` válida posterior o igual a la fecha base.
5. Se computan los días restantes ($\Delta = \text{fecha\_final} - \text{fecha\_base}$) y se determinan las reincorporaciones previstas para cada ventana de tiempo:
   - Próximos 7 días.
   - Próximos 15 días.
   - Próximos 30 días.
6. Se estima la fuerza disponible proyectada: $\text{Disponibles Proyectados} = \min(\text{Total}, \text{Disponibles Actuales} + \text{Reincorporaciones})$.
7. El frontend renderiza las tarjetas de los 3 horizontes temporales con los porcentajes de operatividad futuros y la tabla de los próximos 25 movimientos programados.

---

## CU-MANDO-004: Visualización y Copia del Parte de las 06:00 & Radiograma Castrense

### Actores
- **Principal**: Ayudante de Comando / Oficial de Servicio / Oficial S-1.
- **Secundario**: Servidor Backend BIMEH.

### Precondiciones
- Debe existir un reporte consolidado para la fecha seleccionada.

### Flujo Principal
1. El usuario presiona el botón *"El Parte de las 06:00"* en la barra de acciones rápidas de `MandoS1View.vue` o `DashboardView.vue`.
2. Se abre el modal interactivo `CommandBriefingModal.vue`.
3. El modal consume `GET /api/alertas/parte-diario` con los parámetros temporales activos.
4. El backend consolida los conteos:
   - Efectivo total, disponibles y novedades.
   - Disposición táctica: Área de Operaciones vs Comando de Unidad.
   - Desglose por cuatro categorías militares: Sanidad, Descanso/Bienestar, Servicio/Instrucción y Administrativas.
   - Resumen de alertas críticas de fatiga y sanidad.
   - Texto canónico del Radiograma Militar estructurado con estándares castrenses.
5. El modal muestra las pestañas: Resumen de Fuerza, Radiograma Castrense y Alertas de Mando.
6. El usuario pulsa *"Copiar Radiograma"* para transferir el texto íntegro al portapapeles y transmitirlo por canales institucionales (WhatsApp, correo de comando, radioperador).

---

## CU-MANDO-005: Emisión y Descarga del Boletín Oficial en PDF Institucional

### Actores
- **Principal**: Comandante de Unidad / Oficial S-1.
- **Secundario**: Servidor Backend BIMEH (ReportLab).

### Precondiciones
- El usuario hace clic en el enlace o botón *"Descargar PDF"* del Parte Diario.

### Flujo Principal
1. El usuario invoca la URL `GET /api/exportar/pdf/parte-diario?mes=...&dia=...&fecha=...`.
2. El backend invoca internamente `get_parte_diario(...)` para obtener las métricas oficiales.
3. El motor `ReportLab` construye en memoria (`io.BytesIO`) el documento PDF en orientación vertical con diseño formal:
   - Membrete y encabezado de la República de Colombia y del BIMEJ 12.
   - Tabla de Estado Numérico de Fuerza con porcentaje de operatividad.
   - Cuadro comparativo de Área de Operaciones vs Comando de Unidad.
   - Tabla de desglose de novedades por categorías militares con colores institucionales.
   - Sección de Alertas S-1 (casos prioritarios de fatiga y sanidad).
   - Bloques de pie de página para firmas del Oficial S-1 y del Comandante de Batallón.
4. El backend responde con un flujo de bytes `StreamingResponse` de tipo `application/pdf` y encabezado `Content-Disposition: inline; filename="Parte_Diario_BIMEJ12_YYYY-MM-DD.pdf"`.
5. El navegador abre o descarga el documento PDF de alta fidelidad.

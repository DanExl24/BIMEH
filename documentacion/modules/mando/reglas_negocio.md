# Reglas de Negocio — Módulo de Centro de Mando S-1 & Inteligencia Preventiva (`mando`)

---

## 🛡️ 1. Detección y Control de Fatiga Operacional

### RN-MANDO-001
- **Identificador**: `RN-MANDO-001`
- **Descripción**: La racha continua de fatiga operacional se calcula exclusivamente para el personal activo (`p.fecha_retiro IS NULL OR p.fecha_retiro = ''`) que se encuentre en condición disponible (`AREA OPERACIONES` o `CDO UNIDAD`) en el reporte evaluado.
  - El sistema examina cronológicamente hacia atrás hasta un máximo de 90 reportes continuos anteriores o iguales a la fecha evaluada.
  - La racha se incrementa en `+1` por cada reporte consecutivo donde el efectivo figure en `AREA OPERACIONES` o `CDO UNIDAD`.
  - La racha se interrumpe y detiene inmediatamente ante la presencia de una subnovedad de descanso (`PERMISO` o `VACACIONES`), o ante cualquier otra novedad no disponible.
  - La severidad se clasifica en:
    - `CRITICO`: Racha $\ge 45$ días continuos.
    - `ALTO`: Racha $\ge 30$ días continuos.
    - `MODERADO`: Racha $< 30$ días continuos pero igual o mayor al umbral configurado.
- **Motivo**: Prevenir el agotamiento psicofísico del combatiente, reducir accidentes con armas y optimizar la rotación de tropas en el teatro de operaciones.
- **Módulos afectados**: `mando`, `dashboard`.
- **Archivos donde se implementa**: [`backend/app/routers/alertas.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/alertas.py) (Líneas 72–168), `frontend/src/features/dashboard/components/DashboardFatigueRadar.vue`, `frontend/src/features/mando/views/MandoS1View.vue`.
- **Endpoints relacionados**: `GET /api/alertas/fatiga`
- **Historias de usuario relacionadas**: [HU-MANDO-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/historias_usuario.md#hu-mando-001)

---

## 🏥 2. Ausentismos Médicos y Junta Médico-Laboral Militar

### RN-MANDO-002
- **Identificador**: `RN-MANDO-002`
- **Descripción**: La auditoría de sanidad militar abarca todos los registros de personal activo donde el nombre de la subnovedad contenga `'INCAPACIDAD'`, `'HOSPITAL'` o `'LESIHMANIASIS'` en fechas anteriores o iguales a la fecha de corte.
  - Se totalizan los días acumulados (`COUNT(rp.id)`) y la cantidad de episodios distintos (`COUNT(DISTINCT rp.id_reporte)`).
  - Si el total de días acumulados es $\ge 30$ días $\rightarrow$ Clasificación obligatoria `JUNTA_MEDICA_SUGERIDA` con recomendación de remitir la historia clínica a evaluación formal ante la Junta Médico-Laboral Militar.
  - Si el total de días es $< 30$ días (pero $\ge$ `dias_min`, por defecto 15) $\rightarrow$ Clasificación `SEGUIMIENTO_SANIDAD` para control ambulatorio continuo.
- **Motivo**: Cumplir con los reglamentos sanitarios y de aptitud psicofísica de las Fuerzas Militares de Colombia, identificando oportunamente pérdidas de capacidad laboral o tratamientos prolongados que afecten el efectivo disponible.
- **Módulos afectados**: `mando`.
- **Archivos donde se implementa**: [`backend/app/routers/alertas.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/alertas.py) (Líneas 172–248), `frontend/src/features/mando/views/MandoS1View.vue`.
- **Endpoints relacionados**: `GET /api/alertas/sanidad`
- **Historias de usuario relacionadas**: [HU-MANDO-002](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/reglas_negocio.md#hu-mando-002)

---

## 📈 3. Proyección Analítica de Disponibilidad de Fuerza

### RN-MANDO-003
- **Identificador**: `RN-MANDO-003`
- **Descripción**: La estimación de fuerza disponible a futuro se fundamenta en las fechas finales estipuladas en las novedades del reporte base:
  - Solo se computan registros de militares en novedad (`sn.nombre NOT IN ('AREA OPERACIONES', 'CDO UNIDAD')`) que posean `fecha_final` informada y válida.
  - El delta en días se calcula como: $\Delta_{\text{días}} = \text{fecha\_final} - \text{fecha\_base}$.
  - Se segregan reincorporaciones para 3 horizontes:
    - $\le 7$ días $\rightarrow$ `reinc_7`
    - $\le 15$ días $\rightarrow$ `reinc_15`
    - $\le 30$ días $\rightarrow$ `reinc_30`
  - La fuerza proyectada para cada horizonte $H \in \{7, 15, 30\}$ se calcula como:
    $$\text{Disponibles}_{H} = \min(\text{Total Personal}, \text{Disponibles Actuales} + \text{Reincorporaciones}_{H})$$
  - El porcentaje proyectado no puede superar el 100.0% y se redondea a 1 decimal.
- **Motivo**: Proveer al Estado Mayor una herramienta cuantitativa para programar operaciones tácticas, patrullajes y relevos con certeza sobre la evolución del pie de fuerza disponible.
- **Módulos afectados**: `mando`, `dashboard`.
- **Archivos donde se implementa**: [`backend/app/routers/alertas.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/alertas.py) (Líneas 252–380), `frontend/src/features/dashboard/components/DashboardForceProjection.vue`, `frontend/src/features/mando/views/MandoS1View.vue`.
- **Endpoints relacionados**: `GET /api/alertas/proyeccion`
- **Historias de usuario relacionadas**: [HU-MANDO-003](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/historias_usuario.md#hu-mando-003)

---

## 🏛️ 4. Taxonomía Castrense y Desglose de Novedades

### RN-MANDO-004
- **Identificador**: `RN-MANDO-004`
- **Descripción**: En la consolidación del Estado de Fuerza diario, las novedades de personal deben agruparse estrictamente en cuatro categorías doctrinales:
  1. **Sanidad Militar**: Suma de `INCAPACIDAD`, `HOSPITALIZADOS` y `TRATAMIENTO LESIHMANIASIS`.
  2. **Descanso y Bienestar**: Suma de `PERMISO` y `VACACIONES`.
  3. **Servicio e Instrucción**: Suma de `COMISION DE SERVICIO`, `CURSOS`, `CURSO DE LEY`, `CICLO CODE` y `REENTREANAMIENTO`.
  4. **Administrativas y Otras**: Todo el remanente de personal en novedad no clasificado en los grupos anteriores ($\text{Total Novedades} - (\text{Sanidad} + \text{Descanso} + \text{Servicio})$).
- **Motivo**: Estandarizar la información operativa según los manuales doctrinales de Estado Mayor del Ejército Nacional (EJC) para la rendición de cuentas ante escalones superiores.
- **Módulos afectados**: `mando`, `reportes`.
- **Archivos donde se implementa**: [`backend/app/routers/alertas.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/alertas.py) (Líneas 421–439), [`backend/app/routers/exportar.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/exportar.py) (Líneas 2260–2290).
- **Endpoints relacionados**: `GET /api/alertas/parte-diario`, `GET /api/exportar/pdf/parte-diario`
- **Historias de usuario relacionadas**: [HU-MANDO-004](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/historias_usuario.md#hu-mando-004), [HU-MANDO-005](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/historias_usuario.md#hu-mando-005)

---

## 📑 5. Radiograma Militar y Boletín Oficial en PDF

### RN-MANDO-005
- **Identificador**: `RN-MANDO-005`
- **Descripción**: Tanto el radiograma de texto plano generado en `/api/alertas/parte-diario` como el documento PDF generado en `/api/exportar/pdf/parte-diario` deben incluir obligatoriamente:
  - Encabezado formal de la Unidad: República de Colombia, Ministerio de Defensa Nacional, Ejército Nacional, Segunda División, Quinta Brigada, Batallón de Infantería N° 12 "GR. ALFONSO MANRIQUE REYES" (BIMEJ 12), Sección Personal (S-1).
  - Fecha del parte y hora reglamentaria de emisión: `06:00R`.
  - Resumen numérico: Efectivo total, Disponibles con porcentaje de operatividad y Personal en novedad.
  - Disposición de disponibles: Área de Operaciones vs Comando de Unidad.
  - Alertas preventivas resumidas (total de personal en límite de fatiga y casos críticos de sanidad).
  - En el PDF: Bloques formales de post-firma del Oficial S-1 y del Comandante de Batallón.
- **Motivo**: Garantizar autenticidad institucional, validez jurídica y trazabilidad administrativa para su archivo en la Sección S-1 y radicación ante la Quinta Brigada.
- **Módulos afectados**: `mando`, `reportes`.
- **Archivos donde se implementa**: [`backend/app/routers/alertas.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/alertas.py) (Líneas 453–485), [`backend/app/routers/exportar.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/exportar.py) (Líneas 2196–2430).
- **Endpoints relacionados**: `GET /api/alertas/parte-diario`, `GET /api/exportar/pdf/parte-diario`
- **Historias de usuario relacionadas**: [HU-MANDO-004](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/historias_usuario.md#hu-mando-004), [HU-MANDO-005](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/historias_usuario.md#hu-mando-005)

---

## ⏱️ 6. Jerarquía de Resolución Temporal

### RN-MANDO-006
- **Identificador**: `RN-MANDO-006`
- **Descripción**: Todos los endpoints del Centro de Mando resuelven el reporte objetivo mediante la función `_resolve_target_report` siguiendo la siguiente precedencia estricta:
  1. Si se proporciona `fecha` exacta (formato `YYYY-MM-DD`), se consulta dicho reporte directamente.
  2. Si se proporciona `mes` o `dia`, se consulta el último reporte disponible del período filtrado (`reps[-1]`).
  3. Si no se proporciona ningún filtro, se toma el último reporte registrado en la base de datos (`SELECT id, fecha FROM REPORTES ORDER BY fecha DESC LIMIT 1`).
  4. Si la base de datos no contiene ningún reporte, se retorna `None` y la fecha actual del sistema.
- **Motivo**: Garantizar coherencia y reactividad total con la barra de filtrado global del frontend (`dateStore`), permitiendo a los comandantes viajar en el tiempo para auditar cualquier día del histórico con un solo clic.
- **Módulos afectados**: `mando`, `dashboard`.
- **Archivos donde se implementa**: [`backend/app/routers/alertas.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/alertas.py) (Líneas 33–68).
- **Endpoints relacionados**: `GET /api/alertas/fatiga`, `GET /api/alertas/sanidad`, `GET /api/alertas/proyeccion`, `GET /api/alertas/parte-diario`, `GET /api/exportar/pdf/parte-diario`
- **Historias de usuario relacionadas**: [HU-MANDO-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/historias_usuario.md#hu-mando-001) a [HU-MANDO-006](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/mando/historias_usuario.md#hu-mando-006)

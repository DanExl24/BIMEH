# Reglas de Negocio — Módulo de Asistente IA Militar & Copilot Inteligente (`ia`)

---

## 🛡️ 1. Seguridad, Confinamiento y Guardrails Conversacionales

### RN-IA-001
- **Identificador**: `RN-IA-001`
- **Descripción**: El Asistente IA Militar debe operar bajo confinamiento temático estricto. Está prohibido responder preguntas de cultura general, cocina, deportes, programación genérica o temáticas ajenas a la misión de administración de personal del Batallón de Infantería N° 12 (BIMEJ 12). Ante consultas fuera de dominio, debe declinar cortésmente la respuesta y orientar al usuario a formular consultas operacionales sobre efectivos, novedades o reportes.
- **Motivo**: Proteger los recursos de cómputo y tokens de la API, evitar fugas de propósito del sistema y mantener la formalidad y disciplina requerida en una herramienta castrense de mando.
- **Módulos afectados**: `ia`.
- **Archivos donde se implementa**: [`backend/app/services/gemini_service.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/gemini_service.py) (System Prompt militar y función `is_query_in_domain`), [`backend/app/routers/ia.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/ia.py).
- **Endpoints relacionados**: `POST /api/ia/chat`
- **Historias de usuario relacionadas**: [HU-IA-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-001)

---

## ⚡ 2. Seguridad en Consultas a la Base de Datos y Catálogo Parametrizado

### RN-IA-002
- **Identificador**: `RN-IA-002`
- **Descripción**: La ejecución de consultas SQL derivadas de lenguaje natural debe priorizar siempre el catálogo determinista (`query_catalog.py`). Solo cuando una consulta no coincide con ningún patrón predefinido se permite la generación sintética de SQL mediante Gemini, la cual debe validarse estrictamente contra cláusulas destructivas (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`) antes de ejecutarse en modo solo lectura (`SELECT`).
- **Motivo**: Garantizar el 100% de exactitud matemática en indicadores críticos de mando, prevenir inyecciones SQL y asegurar tiempos de respuesta sub-segundo sin alucinaciones de nombres de tablas o columnas.
- **Módulos afectados**: `ia`, `dashboard`, `reportes`.
- **Archivos donde se implementa**: [`backend/app/services/query_catalog.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/query_catalog.py), [`backend/app/services/gemini_service.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/gemini_service.py) (funciones `classify_query_intent`, `generate_sql_from_catalog`, `execute_safe_sql`).
- **Endpoints relacionados**: `POST /api/ia/chat`
- **Historias de usuario relacionadas**: [HU-IA-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-001), [HU-IA-002](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-002)

---

## 👤 3. Contexto Operativo y Militar Activo

### RN-IA-003
- **Identificador**: `RN-IA-003`
- **Descripción**: Cuando el frontend envía el objeto `active_militar` (cédula y nombre completo del militar seleccionado en pantalla), el backend debe inyectar este contexto en las directivas de análisis del prompt. Si la consulta del usuario omite el sujeto (ej. *"¿cuándo vence su incapacidad?"* o *"¿cuántos días de vacaciones le faltan?"*), el motor de IA debe asociar la solicitud directamente a la cédula del militar activo.
- **Motivo**: Mejorar sustancialmente la experiencia del usuario (UX), permitiendo al personal de la Sección S-1 navegar expedientes de efectivos y consultar dudas inmediatas sin tener que reescribir nombres o cédulas repetidamente.
- **Módulos afectados**: `ia`, `personal`.
- **Archivos donde se implementa**: [`backend/app/routers/ia.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/ia.py) (Líneas 37, 119), [`backend/app/services/gemini_service.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/gemini_service.py), `frontend/src/features/ia/components/AIAssistantDrawer.vue`.
- **Endpoints relacionados**: `POST /api/ia/chat`
- **Historias de usuario relacionadas**: [HU-IA-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-001)

---

## 📜 4. Formato y Doctrina en Documentos Oficiales

### RN-IA-004
- **Identificador**: `RN-IA-004`
- **Descripción**: Todo informe generado en modo reporte (`mode='report'`) o apreciación formal (`/api/ia/apreciacion`) debe cumplir con la estructura doctrinal del Ejército Nacional de Colombia:
  1. Encabezado institucional completo (República de Colombia, Ministerio de Defensa Nacional, Ejército Nacional, Batallón de Infantería N° 12 "GR. ALFONSO MANRIQUE REYES" - BIMEJ 12).
  2. Clasificación del Estado de Fuerza (Total de efectivos, Disponibles en Área de Operaciones / Comando de Unidad, Personal en Novedades con porcentaje exacto de operatividad).
  3. Desglose de novedades críticas (Sanidad, Descanso y Bienestar, Comisiones del Servicio).
  4. Diagnóstico de fatiga o vulnerabilidades operativas.
  5. Recomendaciones de mando para la toma de decisiones.
- **Motivo**: Preservar los estándares formales de comunicación militar militar del Estado Mayor y asegurar que los documentos generados por el sistema puedan ser presentados directamente a la alta comandancia de la brigada o división.
- **Módulos afectados**: `ia`, `mando`.
- **Archivos donde se implementa**: [`backend/app/services/gemini_service.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/gemini_service.py) (Líneas de plantillas de informe y apreciación), [`backend/app/routers/ia.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/ia.py).
- **Endpoints relacionados**: `POST /api/ia/chat` (`mode='report'`), `POST /api/ia/apreciacion`
- **Historias de usuario relacionadas**: [HU-IA-002](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-002), [HU-IA-003](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-003)

---

## ⚙️ 5. Resiliencia de Infraestructura y Configuración en Caliente

### RN-IA-005
- **Identificador**: `RN-IA-005`
- **Descripción**: La arquitectura de IA debe operar bajo un esquema desacoplado y tolerante a fallos:
  1. Si la variable `AI_BACKEND` está en `gemini` pero ocurre un fallo de importación del SDK (`google-genai`), el backend debe conmutar automáticamente a `ollama_service` en modo degradado sin tumbar la API.
  2. Las actualizaciones de modelo o URL enviadas a `POST /api/ia/config` deben aplicarse en caliente en el entorno del proceso en ejecución (`os.environ`), persistiendo para todas las solicitudes subsiguientes de la sesión sin requerir reinicio del servidor.
- **Motivo**: Garantizar alta disponibilidad del asistente incluso en entornos aislados o bases militares de despliegue táctico sin salida constante a Internet.
- **Módulos afectados**: `ia`.
- **Archivos donde se implementa**: [`backend/app/routers/ia.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/ia.py) (Líneas 20–30, 76–86), [`backend/app/services/ollama_service.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/ollama_service.py).
- **Endpoints relacionados**: `GET /api/ia/status`, `POST /api/ia/config`
- **Historias de usuario relacionadas**: [HU-IA-004](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-004), [HU-IA-005](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-005)

---

## 🧭 6. Conciencia de Contexto Visual y Filtro Temporal (Context Awareness)

### RN-IA-006
- **Identificador**: `RN-IA-006`
- **Descripción**: El frontend debe capturar reactivamente la pantalla activa (`current_view`, `current_route`) y el período temporal seleccionado en el panel de control (`selected_month`, `selected_day`), adjuntándolos como metadatos de contexto en toda interacción con el asistente. El backend debe incorporar este contexto en el System Prompt y en la evaluación de intenciones:
  1. Si la consulta del usuario formula preguntas relativas al tiempo (ej. *"¿cuántas novedades hubo?"*, *"¿quién salió a permiso?"*) sin explicitar un mes o rango, el sistema debe asumir y aplicar automáticamente el filtro del período activo en pantalla.
  2. Si la consulta formula preguntas referidas al conjunto de datos visible (ej. *"¿quién de los mostrados tiene más riesgo?"*), el modelo debe contextualizar su respuesta conforme a la vista actual (ej. Mando S-1, Novedades o Personal).
- **Motivo**: Eliminar la fricción cognitiva y evitar la redundancia al obligar al usuario a reiterar la pantalla o el mes en el que se encuentra trabajando.
- **Módulos afectados**: `ia`, `dashboard`, `novedades`, `personal`, `mando`.
- **Archivos donde se implementa**: [`frontend/src/features/ia/components/AIAssistantDrawer.vue`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/frontend/src/features/ia/components/AIAssistantDrawer.vue), [`backend/app/services/gemini_service.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/gemini_service.py), [`backend/app/routers/ia.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/ia.py).
- **Endpoints relacionados**: `POST /api/ia/chat`
- **Historias de usuario relacionadas**: [HU-IA-006](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-006)

---

## 💾 7. Persistencia, Integridad Referencial y Ciclo de Vida de Sesiones de Chat

### RN-IA-007
- **Identificador**: `RN-IA-007`
- **Descripción**: Las conversaciones del Asistente IA deben persistirse de forma relacional en PostgreSQL bajo las siguientes condiciones:
  1. Cada sesión (`ia_sesiones`) posee un identificador único entero, título descriptivo, marca de tiempo de creación y última actualización.
  2. Todo mensaje enviado por el usuario o respondido por el modelo se almacena atómicamente en `ia_mensajes`, vinculado a `session_id` con clave foránea en cascada (`ON DELETE CASCADE`).
  3. Si una consulta entrante carece de `session_id`, el backend debe generar automáticamente una nueva sesión.
  4. El primer mensaje del usuario en una sesión nueva autotitula inteligentemente el hilo utilizando la intención o los primeros 60 caracteres de la consulta.
  5. La eliminación de una sesión debe remover de manera definitiva e inmediata todos los mensajes vinculados para prevenir registros huérfanos.
  6. El identificador de la última sesión activa debe preservarse en el almacenamiento local del cliente (`localStorage.bimej12_ai_session_id`), recuperándose automáticamente al recargar la aplicación SPA.
- **Motivo**: Permitir trazabilidad de consultas de mando, auditoría de respuestas analíticas y continuidad de trabajo en sesiones prolongadas.
- **Módulos afectados**: `ia`.
- **Archivos donde se implementa**: [`backend/app/database.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/database.py) (DDL de `ia_sesiones` e `ia_mensajes`), [`backend/app/routers/ia.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/ia.py), [`frontend/src/features/ia/services/ia.service.ts`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/frontend/src/features/ia/services/ia.service.ts), [`frontend/src/features/ia/components/AIAssistantDrawer.vue`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/frontend/src/features/ia/components/AIAssistantDrawer.vue).
- **Endpoints relacionados**: `GET /api/ia/sesiones`, `POST /api/ia/sesiones`, `GET /api/ia/sesiones/{session_id}`, `DELETE /api/ia/sesiones/{session_id}`, `POST /api/ia/chat`
- **Historias de usuario relacionadas**: [HU-IA-007](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-007)

---

## 📊 8. Previsualización Multiformato y Exportación Sin Límite de Registros

### RN-IA-008
- **Identificador**: `RN-IA-008`
- **Descripción**: La presentación y exportación de datos tabulares generados por el Asistente IA debe cumplir con una arquitectura de dos niveles:
  1. **Nivel 1 (Chat ágil)**: En el cuerpo del Drawer se muestra un resumen o los primeros 10 registros para no sobrecargar el scroll de la conversación ni degradar el rendimiento gráfico.
  2. **Nivel 2 (Inspección en Modal Completo)**: Cuando la consulta genera resultados, se habilita el botón "Ver a detalle", que despliega `QueryResultDetailModal.vue` en el centro de la pantalla sin cortes ni límite de filas.
  3. **Previsualización Dinámica Multiformato**: El modal debe permitir al usuario alternar en tiempo real entre cuatro vistas antes de exportar:
     - *Tabla de Consulta*: Datos tabulares originales con badges y buscador reactivo.
     - *Matriz Heatmap*: Proyección día a día del mes (1 a 31) con celdas interactivas (`D`, `CDO`, `PER`, `INC`, `VAC`, `R`), columna fija de integrante y tooltips con fecha y novedad.
     - *Parte Ágil*: Algoritmo de agregación que consolida días consecutivos de la misma novedad en intervalos continuos (`startDay-endDay (NOVEDAD)`), junto con desglose por categoría.
     - *Estadística de Totales*: 4 KPIs gerenciales, distribución porcentual y barras de progreso animadas en gradiente.
  4. **Exportación Consistente**: Los botones de descarga superior (`Excel` y `PDF`) deben generar el archivo correspondiente a la pestaña visualizada, invocando `POST /api/ia/exportar-tabla` para la tabla pura o los endpoints oficiales `/api/exportar/` para formatos castrenses consolidados.
  5. **No redundancia de controles**: El pie del modal debe mantenerse libre de botones de descarga redundantes, conservando únicamente el contador de registros y el botón de cierre.
- **Motivo**: Brindar al mando militar la capacidad de auditar visualmente cómo quedará estructurado su informe antes de descargarlo o imprimirlo, agilizando la toma de decisiones.
- **Módulos afectados**: `ia`, `reportes`.
- **Archivos donde se implementa**: [`frontend/src/features/ia/components/QueryResultDetailModal.vue`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/frontend/src/features/ia/components/QueryResultDetailModal.vue), [`backend/app/routers/ia.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/ia.py) (endpoint `/exportar-tabla`), [`frontend/src/features/ia/services/ia.service.ts`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/frontend/src/features/ia/services/ia.service.ts).
- **Endpoints relacionados**: `POST /api/ia/exportar-tabla`, `GET /api/exportar/excel`, `GET /api/exportar/pdf`
- **Historias de usuario relacionadas**: [HU-IA-008](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-008)

---

## 🕒 9. Tratamiento Inteligente de Expresiones Temporales Relativas

### RN-IA-009
- **Identificador**: `RN-IA-009`
- **Descripción**: El procesador de lenguaje natural (`date_extractor.py`), los skills deterministas (`NovedadesSkill`) y las directivas de System Prompt para Text-to-SQL deben acotar con rigor militar cualquier expresión temporal relativa:
  1. Expresiones como `"este mes"`, `"en este mes"`, `"mes actual"`, `"mes en curso"` o `"presente mes"` deben mapearse de forma obligatoria e inmediata a `datetime.now().month` y año actual (ej. `2026-10-%`).
  2. NUNCA se debe devolver una consulta anual acumulada (sin cláusula `fecha_reporte LIKE ...`) ante una solicitud de novedad relativa a un mes.
  3. Se prohíbe incluir en la respuesta a personal cuya novedad haya expirado en meses anteriores (por ejemplo, incapacidades médicas finalizadas en meses pasados) cuando el usuario pregunta por el estado de novedad en el mes actual.
  4. La fecha y mes corriente del sistema deben estar permanentemente inyectados en el System Prompt para guiar cualquier modelo generativo (Gemini u Ollama).
- **Motivo**: Prevenir desinformación al comando del batallón, garantizando que una consulta sobre afectación mensual refleje con absoluta exactitud únicamente a los efectivos con novedad vigente durante el período consultado.
- **Módulos afectados**: `ia`, `novedades`.
- **Archivos donde se implementa**: [`backend/app/ia/nlp/date_extractor.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/ia/nlp/date_extractor.py), [`backend/app/ia/skills/base.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/ia/skills/base.py), [`backend/app/ia/prompts/system_prompts.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/ia/prompts/system_prompts.py), [`backend/app/ia/skills/novedades_skill.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/ia/skills/novedades_skill.py).
- **Endpoints relacionados**: `POST /api/ia/chat`
- **Historias de usuario relacionadas**: [HU-IA-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-001), [HU-IA-006](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md#hu-ia-006)



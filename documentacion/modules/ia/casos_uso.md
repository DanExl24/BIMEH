# Casos de Uso — Módulo de Asistente IA Militar & Copilot Inteligente (`ia`)

---

## CU-IA-001: Consulta Operativa en Lenguaje Natural con Copilot IA

### Actores
- **Principal**: Comandante de Unidad / Oficial S-1 / Suboficial de Personal.
- **Secundario**: Servidor Backend BIMEH (`gemini_service.py` o `ollama_service.py`), Google Gemini API / Ollama Local, Base de Datos PostgreSQL/DuckDB.

### Precondiciones
1. El usuario debe estar autenticado en la plataforma BIMEH.
2. El servicio de IA debe estar configurado y en estado online (`GEMINI_API_KEY` válida o demonio Ollama activo).
3. Deben existir reportes de personal cargados en la base de datos.

### Flujo Principal
1. El usuario hace clic en el botón flotante del Asistente IA en el Navbar o presiona el atajo de apertura del Drawer lateral (`AIAssistantDrawer.vue`).
2. El componente frontend ejecuta `iaService.obtenerEstado()` (`GET /api/ia/status`) para verificar disponibilidad, backend activo y modelos disponibles.
3. El usuario formula una consulta en lenguaje natural (ej. *"¿Cuántos soldados están disponibles en el área de operaciones?"*, *"¿Qué personal tiene más de 30 días sin descanso?"* o selecciona una sugerencia rápida).
4. El frontend envía la solicitud `POST /api/ia/chat` con el payload `ChatMessageRequest` conteniendo `message`, `history`, `active_militar` (si se está inspeccionando un efectivo) y `mode='chat'`.
5. El backend valida el backend activo (`get_ai_backend()`) y aplica los guardrails conversacionales y de dominio militar.
6. El servicio evalúa la intención contra el catálogo de consultas parametrizadas (`query_catalog.py`). Si coincide con un patrón determinista, genera el SQL optimizado; de lo contrario, Gemini sintetiza la consulta SQL a partir del esquema.
7. Se ejecuta la consulta SQL de manera segura en modo solo lectura sobre la base de datos.
8. El modelo sintetiza la respuesta militar en lenguaje natural con estilo castrense, citando cifras exactas y justificaciones.
9. El frontend renderiza la respuesta en el chat con formato Markdown, resaltado de datos clave y metadatos de ejecución (tiempo de respuesta en segundos y modelo utilizado).

### Flujos Alternativos
- **A1: Servicio de IA no disponible (offline o sin API Key)**: El backend retorna código HTTP 503 o 500. El frontend muestra una alerta de advertencia indicando la falla y permitiendo reintentar o cambiar a Ollama/Gemini.
- **A2: Pregunta fuera del dominio militar de BIMEH (Guardrails)**: El modelo detecta que la consulta es ajena al sistema (recetas, deportes, código no relacionado, etc.) y responde cortésmente declinando la solicitud y recordando su función como Asistente de Personal S-1 del BIMEJ 12.
- **A3: Error de sintaxis o ejecución SQL**: Si la consulta generada falla, el servicio captura la excepción, realiza un reintento automático con corrección contextual o entrega una explicación clara al usuario.

---

## CU-IA-002: Generación de Informes de Situación de Efectivos en Formato Castrense

### Actores
- **Principal**: Oficial S-1 / Ayudante de Comando.
- **Secundario**: Servidor Backend BIMEH, Google Gemini API.

### Precondiciones
1. El usuario se encuentra en el Drawer de IA o en el panel de mando.
2. Existen datos cargados para la fecha o mes de referencia.

### Flujo Principal
1. El usuario selecciona la acción rápida *"Generar Informe de Personal"* o envía un requerimiento formal (ej. *"Generar informe ejecutivo de novedades de mayo"*).
2. El frontend envía `POST /api/ia/chat` indicando `mode='report'`.
3. El backend recupera las estadísticas consolidadas del período solicitado a través de `query_catalog.py`.
4. El servicio invoca a Gemini con el System Prompt formal militar de redacción de documentos de Estado Mayor:
   - Encabezado: República de Colombia, Ejército Nacional, BIMEJ 12.
   - Diagnóstico Cuantitativo del Estado de Fuerza.
   - Puntos Críticos y Novedades Relevantes.
   - Recomendaciones de Mando para el Comandante.
5. El modelo devuelve el informe estructurado en Markdown castrense.
6. El frontend renderiza el informe en un visor enriquecido permitiendo copiar al portapapeles o imprimir.

### Flujos Alternativos
- **A1: Datos insuficientes para el período**: Si no hay reportes para el mes solicitado, el sistema informa la anomalía y ofrece generar el reporte con base en el último mes disponible.

---

## CU-IA-003: Elaboración Automatizada de Apreciación de Situación de Personal para la Comandancia

### Actores
- **Principal**: Comandante de Batallón / Segundo Comandante / Oficial S-1.
- **Secundario**: Servidor Backend BIMEH, Google Gemini API / Ollama.

### Precondiciones
1. El usuario posee rol con privilegios de comando o administración.
2. La base de datos contiene los registros consolidados de efectivos y novedades del Batallón.

### Flujo Principal
1. El usuario pulsa la opción *"Apreciación de Comandancia"* en el menú de acciones del Asistente IA.
2. El frontend emite una petición `POST /api/ia/apreciacion` con el parámetro opcional `mes='TODOS'` o el mes en curso.
3. El backend (`backend/app/routers/ia.py` -> `generate_apreciacion`) extrae métricas multidimensionales:
   - Efectivo total y porcentaje de operatividad de la unidad.
   - Relación frente a retaguardia (Área de Operaciones vs Comando de Unidad).
   - Análisis de afectación por ausentismo médico (Sanidad/Incapacidades/Leishmaniasis).
   - Diagnóstico del ciclo de descanso y bienestar (Permisos y Vacaciones).
4. El motor de IA procesa la matriz de datos y redacta el documento estratégico de Apreciación de Situación S-1.
5. El backend retorna el objeto JSON con el texto formateado, fecha de generación y modelo empleado.
6. El frontend despliega la apreciación en un panel modal de lectura ejecutiva con controles de copiado y exportación.

---

## CU-IA-004: Supervisión de Salud y Diagnóstico de Modelos de IA

### Actores
- **Principal**: Administrador del Sistema / Usuario del Asistente.
- **Secundario**: Servidor Backend BIMEH, APIs de Google Cloud / Servidor Ollama.

### Precondiciones
- El backend BIMEH debe estar en ejecución.

### Flujo Principal
1. Al montarse el componente `AIAssistantDrawer.vue`, se despacha `GET /api/ia/status`.
2. El backend examina la variable `AI_BACKEND`:
   - Si es `gemini`: valida la presencia de `GEMINI_API_KEY`, consulta el modelo por defecto (`GEMINI_MODEL`) y obtiene la lista de modelos homologados con sus límites de RPM/RPD (`get_gemini_models_info`).
   - Si es `ollama`: ejecuta un ping HTTP contra `OLLAMA_BASE_URL` (`http://localhost:11434/api/tags`), verificando conectividad de red y modelos descargados localmente.
3. El backend retorna el estado consolidado: `backend`, `online`, `model_configured`, `available_models` y posibles alertas o advertencias.
4. El frontend actualiza los indicadores visuales: badge de estado (verde para En Línea, ámbar para Degradado, rojo para Desconectado) y llena el selector dinámico de modelos.

---

## CU-IA-005: Cambio Dinámico de Modelo de Lenguaje en Tiempo de Ejecución

### Actores
- **Principal**: Usuario Operador / Administrador del Sistema.
- **Secundario**: Backend BIMEH.

### Precondiciones
- El Asistente IA debe estar abierto y en estado funcional.

### Flujo Principal
1. En la cabecera del Drawer de IA, el usuario despliega el selector de modelo de lenguaje (ej. alternar entre `gemini-3.5-flash-lite`, `gemini-2.5-flash`, o modelos Ollama locales).
2. El usuario selecciona el modelo deseado.
3. El frontend emite `POST /api/ia/config` enviando el payload `{ "model": "<nuevo_modelo>" }`.
4. El backend actualiza las variables de entorno en memoria (`GEMINI_MODEL` y `OLLAMA_MODEL`) sin reiniciar el proceso del servidor.
5. El backend confirma el cambio respondiendo con el nuevo estado (`get_ia_status()`).
6. Las subsecuentes solicitudes de chat y apreciación utilizan de inmediato el motor seleccionado.

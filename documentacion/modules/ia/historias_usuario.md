# Historias de Usuario — Módulo de Asistente IA Militar & Copilot Inteligente (`ia`)

---

# HU-IA-001

## Historia
**Como** oficial o suboficial de personal de la sección S-1  
**Quiero** interactuar con un asistente de inteligencia artificial en lenguaje natural  
**Para** resolver dudas operativas sobre el estado de fuerza, ubicación de efectivos, historial de novedades y estadísticas del Batallón sin tener que construir consultas manuales.

## Descripción
El usuario abre el panel lateral del Asistente IA (`AIAssistantDrawer.vue`) desde cualquier vista del sistema. Escribe preguntas cotidianas de la gestión castrense (ej. *"¿Cuántos soldados están en comisión actualmente?"*, *"¿Quiénes están en tratamiento de leishmaniasis?"*, *"Dame el resumen del soldado con cédula 123456"*). El sistema procesa la consulta utilizando Google Gemini (o el motor local Ollama en caso de contingencia o modo offline). Si la consulta encaja en un patrón conocido de búsqueda operativa, el sistema aprovecha el catálogo de consultas predefinidas (`query_catalog.py`) para garantizar exactitud matemática y tiempos de respuesta inferiores a un segundo. El resultado se acompaña de un texto explicativo con terminología castrense.

## Criterios de Aceptación
- La interfaz del Drawer debe estar disponible globalmente en la aplicación web mediante el botón del Navbar.
- Las consultas deben preservar el hilo de la conversación enviando el historial previo de mensajes (`history`) al backend.
- Si el usuario está visualizando el expediente de un militar específico, el frontend debe adjuntar automáticamente el contexto (`active_militar`) para resolver referencias pronominales como *"¿cuándo sale a vacaciones?"* o *"¿cuántos días de permiso ha tenido?"*.
- El modelo debe respetar los guardrails de dominio castrense: debe rechazar amablemente preguntas no vinculadas con la administración del BIMEJ 12 o temas militares de personal.
- La respuesta debe incluir el tiempo de procesamiento (`elapsed_seconds`) y el backend utilizado (`backend`).
- Las respuestas numéricas y listas de personal deben renderizarse con formato Markdown estructurado (negritas, tablas, listas).

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-IA-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-001), [RN-IA-002](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-002), [RN-IA-003](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-003)
- **Endpoints relacionados**: `POST /api/ia/chat`, `GET /api/ia/status`
- **Componentes frontend relacionados**: `frontend/src/features/ia/components/AIAssistantDrawer.vue`, `frontend/src/features/ia/services/ia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/ia.py` (`chat_with_ia`), `backend/app/services/gemini_service.py` (`process_user_query`), `backend/app/services/query_catalog.py`

---

# HU-IA-002

## Historia
**Como** Oficial S-1 de la Unidad  
**Quiero** solicitar la redacción automatizada de un informe formal de novedades de personal  
**Para** presentar un parte ejecutivo y analítico a la comandancia de forma rápida y con la estructura doctrinal del Ejército Nacional.

## Descripción
En el chat de IA o mediante el selector de modo del Drawer, el usuario activa el modo de generación de informes (`mode='report'`). Al solicitar un balance de novedades de un período determinado (ej. *"Generar informe de novedades del mes de mayo"*), el motor de IA recopila los datos agregados de la base de datos, construye una síntesis militar con formato castrense oficial (encabezado del Batallón de Infantería N° 12, balance cuantitativo, puntos de atención crítica y recomendaciones táctico-administrativas) y entrega un texto estructurado en Markdown listo para impresión o copiado directo al informe de gestión.

## Criterios de Aceptación
- La solicitud debe procesarse con el flag `mode='report'`.
- El reporte generado debe incluir encabezado institucional formal (República de Colombia, Ministerio de Defensa Nacional, Ejército Nacional, BIMEJ 12).
- Debe discriminar el estado de fuerza en: disponibles en área de operaciones, comando de unidad y personal en novedades.
- Debe detallar los casos prioritarios de sanidad y personal que requiera relevo por exceso de permanencia en servicio.
- Debe incluir una sección final con recomendaciones de comando sugeridas para el Oficial S-1.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`
- **Reglas de negocio relacionadas**: [RN-IA-002](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-002), [RN-IA-004](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-004)
- **Endpoints relacionados**: `POST /api/ia/chat`
- **Componentes frontend relacionados**: `frontend/src/features/ia/components/AIAssistantDrawer.vue`, `frontend/src/features/ia/services/ia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/ia.py`, `backend/app/services/gemini_service.py`

---

# HU-IA-003

## Historia
**Como** Comandante del Batallón  
**Quiero** generar un informe consolidado de Apreciación de Situación de Personal con un solo clic  
**Para** evaluar la capacidad combativa y el bienestar del talento humano de la unidad antes de la toma de decisiones operacionales.

## Descripción
El usuario presiona el botón *"Apreciación de Comandancia"* en el Asistente IA. El sistema ejecuta `POST /api/ia/apreciacion` y recopila todas las métricas operativas del mes seleccionado (o el histórico completo si se selecciona `TODOS`). El motor de inteligencia artificial analiza la proporción de combatientes en el terreno vs retaguardia, el impacto de las incapacidades médicas crónicas y la distribución de descansos, emitiendo un documento estratégico formal de Apreciación S-1.

## Criterios de Aceptación
- El endpoint `POST /api/ia/apreciacion` debe admitir el parámetro `mes` (`TODOS` o el nombre del mes).
- Debe soportar procesamiento tanto en Google Gemini como en el fallback de Ollama (`generate_executive_briefing`).
- El documento retornado debe estructurarse en apartados claros: Situación de Personal, Efectivos Disponibles, Principales Novedades, Vulnerabilidades y Conclusiones de Comando.
- La interfaz debe permitir visualizar la apreciación en pantalla completa y copiar el texto al portapapeles.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-IA-001](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-001), [RN-IA-004](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-004)
- **Endpoints relacionados**: `POST /api/ia/apreciacion`
- **Componentes frontend relacionados**: `frontend/src/features/ia/components/AIAssistantDrawer.vue`, `frontend/src/features/ia/services/ia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/ia.py` (`generar_apreciacion_comandancia`), `backend/app/services/gemini_service.py` (`generate_apreciacion`)

---

# HU-IA-004

## Historia
**Como** Administrador del Sistema  
**Quiero** visualizar en tiempo real el estado de conectividad, cuotas y modelos de IA disponibles  
**Para** monitorear la salud del servicio y evitar interrupciones por agotamiento de cuotas de API.

## Descripción
El componente del Asistente consulta periódicamente `GET /api/ia/status`. El backend reporta si el motor está online, si las credenciales de API Key son válidas y entrega la lista de modelos disponibles en Google Gemini (con cuotas teóricas de RPM/RPD) o los modelos cargados en el demonio local Ollama. En caso de corte de conexión o degradación, la interfaz refleja el estado con indicadores cromáticos claros.

## Criterios de Aceptación
- Si el backend es Gemini, se debe verificar que `GEMINI_API_KEY` exista y no esté vacía.
- Se debe devolver la lista de modelos con metadatos: nombre técnico, display name, límite de RPM y RPD.
- Si el backend es Ollama, se debe comprobar el socket HTTP local y retornar los modelos instalados.
- Si la API Key no está configurada o el servicio local está caído, el campo `online` debe ser `false` y `error` debe detallar la causa.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`
- **Reglas de negocio relacionadas**: [RN-IA-005](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-005)
- **Endpoints relacionados**: `GET /api/ia/status`
- **Componentes frontend relacionados**: `frontend/src/features/ia/components/AIAssistantDrawer.vue`
- **Controllers/Services relacionados**: `backend/app/routers/ia.py` (`get_ia_status`), `backend/app/services/gemini_service.py` (`get_gemini_models_info`)

---

# HU-IA-005

## Historia
**Como** Usuario de BIMEH  
**Quiero** seleccionar el modelo de lenguaje a utilizar para mis consultas  
**Para** alternar entre modelos ultra rápidos y económicos (como `gemini-3.5-flash-lite`) y modelos de alta capacidad de razonamiento según la complejidad de la tarea.

## Descripción
En la cabecera del panel del Asistente IA se dispone de un selector desplegable con los modelos homologados. Al elegir un modelo alternativo, la aplicación envía `POST /api/ia/config` para actualizar el modelo activo en caliente, permitiendo que la sesión actual y futuras consultas utilicen inmediatamente la configuración elegida sin necesidad de reiniciar contenedores ni modificar archivos `.env`.

## Criterios de Aceptación
- El endpoint `POST /api/ia/config` debe recibir `model` y opcionalmente `base_url`.
- La actualización en caliente debe reflejarse inmediatamente en las variables de entorno de la instancia en memoria (`GEMINI_MODEL`, `OLLAMA_MODEL`).
- El backend debe responder con el nuevo estado actualizado invocando `get_ia_status()`.
- Si el usuario especifica un modelo particular en el payload de `POST /api/ia/chat`, ese modelo tiene precedencia sobre el modelo global configurado.

## Metadata
- **Prioridad**: Baja
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-IA-005](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-005)
- **Endpoints relacionados**: `POST /api/ia/config`, `POST /api/ia/chat`
- **Componentes frontend relacionados**: `frontend/src/features/ia/components/AIAssistantDrawer.vue`, `frontend/src/features/ia/services/ia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/ia.py` (`update_ia_config`)

---

# HU-IA-006

## Historia
**Como** Comandante de Batallón u Oficial S-1  
**Quiero** que el Asistente IA reconozca automáticamente la pantalla y el período de fechas que estoy visualizando  
**Para** formular preguntas contextuales directas (*"¿quién de los que veo aquí está más fatigado?"*, *"¿cuántas bajas hubo en este mes?"*) sin tener que escribir nuevamente nombres de vistas ni meses.

## Descripción
Al abrir el Asistente IA, el frontend empaqueta automáticamente el contexto de navegación en el objeto `context` (`current_view`, `current_route`, `selected_month`, `selected_day`), extraído de la ruta activa y del almacén de fechas (`dateStore`). El backend inyecta estos parámetros en el prompt del sistema y evalúa los catálogos y consultas SQL delimitando automáticamente el filtro temporal y el foco operativo. Adicionalmente, el frontend muestra una barra superior con la indicación en tiempo real del contexto observado.

## Criterios de Aceptación
- El drawer debe mostrar en tiempo real la vista activa y el mes/día filtrado.
- El objeto `context` debe adjuntarse en cada payload enviado a `POST /api/ia/chat`.
- El modelo debe interpretar preguntas relativas referidas al mes filtrado sin exigir que el usuario lo mencione explícitamente.
- Al navegar entre vistas (ej. de Dashboard a Mando S-1 o Personal), el contexto del drawer debe actualizarse automáticamente.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-IA-003](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-003), [RN-IA-006](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-006)
- **Endpoints relacionados**: `POST /api/ia/chat`
- **Componentes frontend relacionados**: `frontend/src/features/ia/components/AIAssistantDrawer.vue`, `frontend/src/features/ia/services/ia.service.ts`, `frontend/src/stores/dateStore.ts`
- **Controllers/Services relacionados**: `backend/app/routers/ia.py`, `backend/app/services/gemini_service.py`

---

# HU-IA-007

## Historia
**Como** Oficial de Personal de la Sección S-1  
**Quiero** gestionar múltiples hilos de conversación guardados y recuperar mis chats al recargar la página  
**Para** mantener un registro de consultas analíticas previas, comparar apreciaciones y retomar sesiones de trabajo sin perder el hilo histórico.

## Descripción
El sistema persiste los hilos de conversación en la base de datos relacional PostgreSQL mediante las tablas `ia_sesiones` e `ia_mensajes`. En el Drawer del Asistente IA, el usuario dispone de botones para crear una nueva conversación (`+`), ver el historial de sesiones guardadas y eliminar hilos antiguos. Al recargar el navegador, la aplicación recupera la última sesión activa desde `localStorage` y carga sus mensajes históricos mediante `GET /api/ia/sesiones/{session_id}`.

## Criterios de Aceptación
- Al iniciar un nuevo chat, la sesión debe crearse y titularse automáticamente con base en la primera pregunta formulada.
- Todos los mensajes emitidos por el usuario y respondidos por el asistente deben persistirse de forma atómica en PostgreSQL.
- El panel de historial debe listar las sesiones ordenadas por fecha de actualización, mostrando título, fecha y cantidad de mensajes.
- Debe ser posible cambiar de hilo en cualquier momento, cargando los mensajes correspondientes.
- La eliminación de una sesión debe remover en cascada los mensajes asociados tanto en base de datos como en la interfaz.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-IA-007](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-007)
- **Endpoints relacionados**: `GET /api/ia/sesiones`, `POST /api/ia/sesiones`, `GET /api/ia/sesiones/{session_id}`, `DELETE /api/ia/sesiones/{session_id}`, `POST /api/ia/chat`
- **Componentes frontend relacionados**: `frontend/src/features/ia/components/AIAssistantDrawer.vue`, `frontend/src/features/ia/services/ia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/ia.py`, `backend/app/database.py`

---

# HU-IA-008

## Historia
**Como** Comandante de Batallón u Oficial S-1  
**Quiero** inspeccionar el listado completo de registros de una consulta en un modal centrado y previsualizarla en formato Heatmap, Parte Ágil o Estadística antes de exportar  
**Para** analizar con total comodidad los datos sin límites de visualización en el chat y descargar exactamente el informe oficial que necesito en Excel o PDF.

## Descripción
Cuando el Asistente IA retorna resultados tabulares, muestra una vista preliminar de los 10 primeros registros en el Drawer para no saturar la conversación. Si hay más registros (o el usuario desea un análisis profundo), un botón destacado *"Ver a detalle"* abre el componente `QueryResultDetailModal.vue` en el centro de la pantalla. El modal ofrece cuatro pestañas interactivas de previsualización dinámica:
1. **Tabla de Consulta**: Desglose con numeración, badges oficiales de novedad y buscador en tiempo real.
2. **Matriz Heatmap**: Proyección día a día del mes activo con celdas de colores y tooltips explicativos.
3. **Parte Ágil**: Consolidación automática de fechas consecutivas en rangos castrenses (ej: `01-04 CDO UNIDAD`, `05-06 PERMISO`).
4. **Estadística Totales**: Métricas de resumen (KPIs) y barras de distribución porcentual.
Desde la cabecera superior, el usuario puede exportar directamente la vista previsualizada en formato Excel (`.xlsx`) o PDF (`.pdf`), o copiar los datos al portapapeles en formato TSV. El pie de página se mantiene limpio sin controles redundantes.

## Criterios de Aceptación
- El botón *"Ver a detalle [N registros]"* debe presentarse en el chat siempre que la consulta retorne filas de datos.
- El modal debe desplegarse centrado, con fondo desenfocado (*backdrop blur*), soporte de tecla `Esc` y responsive.
- Debe permitir alternar en tiempo real entre las 4 pestañas de formato (Tabla, Heatmap, Parte Ágil, Estadística) recalculando reactivamente la proyección visual.
- El buscador reactivo debe filtrar los datos instantáneamente en cualquiera de las 4 vistas.
- El botón *"Copiar"* debe copiar al portapapeles los datos formateados en formato TSV según la pestaña activa.
- Los botones superiores de exportación en Excel y PDF deben generar el archivo correspondiente a la vista seleccionada.
- El footer del modal solo debe mostrar el contador de registros y el botón de cierre, sin botones redundantes de descarga.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-IA-008](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-008), [RN-IA-009](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md#rn-ia-009)
- **Endpoints relacionados**: `POST /api/ia/exportar-tabla`, `GET /api/exportar/excel`, `GET /api/exportar/pdf`
- **Componentes frontend relacionados**: `frontend/src/features/ia/components/QueryResultDetailModal.vue`, `frontend/src/features/ia/components/AIAssistantDrawer.vue`, `frontend/src/features/ia/services/ia.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/ia.py`, `backend/app/routers/exportar.py`


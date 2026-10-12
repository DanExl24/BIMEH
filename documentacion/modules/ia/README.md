# Módulo 9: Asistente IA Militar & Copilot Inteligente (`ia`)

## 📌 Descripción General
El módulo de **Asistente IA Militar & Copilot Inteligente** es el componente de analítica conversacional avanzada del sistema BIMEH. Permite a los comandantes de batallón, oficiales de personal (S-1) y analistas institucionales interactuar con la base de datos relacional mediante lenguaje natural en español, convirtiendo preguntas cotidianas en consultas estructuradas SQL seguras (*Text-to-SQL*) y sintetizando respuestas con terminología militar institucional.

El módulo cuenta con una arquitectura de backend híbrida que soporta tanto modelos de frontera en la nube (**Google Gemini 2.5 Flash / Flash Lite**) como modelos de inferencia local sin conexión a internet (**Ollama / LLaMA 3.1 8B / Qwen 2.5 7B**), garantizando soberanía operativa, privacidad de la información castrense y respuesta en milisegundos.

---

## 🏛️ Arquitectura del Módulo

### Backend
- **Router REST**: [`backend/app/routers/ia.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/routers/ia.py)
- **Servicio Gemini (Cloud)**: [`backend/app/services/gemini_service.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/gemini_service.py) (SDK `google-genai`, llamadas estructuradas, fallback y memoria multi-turno).
- **Servicio Ollama (Local)**: [`backend/app/services/ollama_service.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/ollama_service.py) (Conexión HTTP local a `http://localhost:11434`, Text-to-SQL determinista y guardrails).
- **Catálogo de Consultas y Verificación**: [`backend/app/services/query_catalog.py`](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/backend/app/services/query_catalog.py) (Diccionario de patrones SQL institucionales optimizados para PostgreSQL).
- **Tablas y Vistas SQL de Base de Datos**:
  - `ia_sesiones`: Hilos de conversación persistentes con título, fechas y conteo de interacciones.
  - `ia_mensajes`: Registro atómico de mensajes `user` y `assistant` vinculados a la sesión con contexto y metadatos.
  - `v_personal_resumen`: Consolidado de efectivos, estado activo/retirado y totales de novedades.
  - `v_novedades_detalle`: Bitácora unificada con nombres, cédulas, subnovedades, fechas y descripciones.
  - `v_conteo_novedades`: Métricas agrupadas por tipo de novedad y personal afectado.

### Frontend (`src/features/ia/`)
- **Componente Drawer Flotante**: `frontend/src/features/ia/components/AIAssistantDrawer.vue` (Panel lateral deslizable con barra de Context Awareness en tiempo real, selector de hilos guardados, botón de nueva conversación, historial reactivo, formateo de tablas SQL y copia de respuestas).
- **Servicio de Feature**: `frontend/src/features/ia/services/ia.service.ts` (Cliente HTTP para chat, gestión de sesiones persistentes, estado de salud y apreciación).
- **Tipos de Feature**: `frontend/src/features/ia/types/ia.types.ts` (Modelos TypeScript para mensajes, contexto militar, sesiones, estado de IA y tablas).
- **Integración Global**:
  - `frontend/src/App.vue`: Botón permanente en el Header institucional (`[ 🤖 Asistente IA ]`).
  - `frontend/src/components/layout/Sidebar.vue`: Botón táctico de invocación rápida en el menú lateral.

---

## 🔌 Endpoints del Módulo

| Método | Endpoint | Parámetros / Body | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/ia/status` | Ninguno | Verifica el estado del motor activo (Gemini u Ollama), cuotas, latencia y lista de modelos disponibles. |
| `POST` | `/api/ia/config` | `base_url`, `model` | Permite conmutar el modelo activo o la URL de inferencia en caliente sin reiniciar el backend. |
| `GET` | `/api/ia/sesiones` | Ninguno | Lista todas las sesiones de chat guardadas con su título, fecha y total de mensajes. |
| `POST` | `/api/ia/sesiones` | `titulo` (opcional) | Crea un nuevo hilo de conversación vacío. |
| `GET` | `/api/ia/sesiones/{session_id}` | `session_id` (path) | Obtiene los mensajes históricos de una sesión específica. |
| `DELETE` | `/api/ia/sesiones/{session_id}` | `session_id` (path) | Elimina en cascada la sesión y todos sus mensajes asociados. |
| `POST` | `/api/ia/chat` | `message`, `history`, `session_id`, `context`, `active_militar`, `model`, `mode` | Procesa una solicitud en lenguaje natural, ejecuta la consulta SQL segura en PostgreSQL y retorna la síntesis militar vinculada a la sesión. |
| `POST` | `/api/ia/apreciacion` | `mes`, `model` | Genera de forma automatizada el informe formal de Apreciación de Situación de Personal para la comandancia. |

---

## 📄 Documentos del Módulo

- [Historias de Usuario](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/historias_usuario.md)
- [Reglas de Negocio](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/reglas_negocio.md)
- [Casos de Uso](file:///c:/Users/alejo/Downloads/proyectos-dev/BIMEH/documentacion/modules/ia/casos_uso.md)


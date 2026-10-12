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

# Módulo 1: Autenticación y Control de Acceso (`auth`)

## 📌 Descripción General
El módulo de **Autenticación y Control de Acceso** es responsable de la gestión de identidad, control de sesiones, protección de rutas tanto en frontend como en backend, validación criptográfica de credenciales y verificación de la conectividad con servicios externos (Google Drive OAuth).

El sistema implementa autenticación basada en tokens JWT (*JSON Web Tokens*) firmados con algoritmo HS256 y contraseñas cifradas mediante *bcrypt*. Provee un control de acceso basado en roles (**RBAC** - *Role-Based Access Control*) con los perfiles `ADMINISTRATIVO` y `CONSULTA`.

---

## 🏛️ Arquitectura del Módulo

### Backend
- **Router**: [`backend/app/routers/auth.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/auth.py)
- **Dependencias de Seguridad**: [`backend/app/dependencies.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/dependencies.py)
- **Gestor CLI de Usuarios**: [`backend/manage_users.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/manage_users.py)
- **Integración OAuth**: `backend/config/auth.py`

### Frontend (Feature `src/features/auth/` + Capas Compartidas)
- **Vista**: `frontend/src/features/auth/views/LoginView.vue`
- **Servicio de Feature**: `frontend/src/features/auth/services/auth.service.ts`
- **Store de Feature**: `frontend/src/features/auth/stores/authStore.ts` (re-exportado en `frontend/src/stores/authStore.ts`)
- **Tipos de Feature**: `frontend/src/features/auth/types/auth.types.ts`
- **Guardián de Rutas**: `frontend/src/router/index.ts`
- **Cliente HTTP Transversal**: `frontend/src/services/http.ts` (`fetchWithAuth`, `http.get`, `http.post`)
- **Fachada Centralizada**: [`frontend/src/services/api.ts`](file:///c:/Users/alejo/Downloads/automPYdrive/frontend/src/services/api.ts)

---

## 🔌 Endpoints del Módulo

| Método | Endpoint | Descripción | Acceso / Rol |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Autentica credenciales, emite token JWT y actualiza `ultimo_login`. | Público |
| `POST` | `/api/auth/logout` | Notifica cierre de sesión para descarte de token en cliente. | Público / Autenticado |
| `GET` | `/api/auth/me` | Retorna los datos del usuario decodificados del token JWT activo. | Token JWT Requerido |
| `GET` | `/api/auth/drive-status` | Verifica el estado del token OAuth de Google Drive. | Token JWT Requerido |

---

## 📄 Documentos del Módulo

- [Historias de Usuario](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md)
- [Reglas de Negocio](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md)
- [Casos de Uso](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/casos_uso.md)

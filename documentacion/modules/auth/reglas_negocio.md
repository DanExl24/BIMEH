# Reglas de Negocio — Módulo de Autenticación y Control de Acceso (`auth`)

---

## 🔒 1. Permisos y Acceso

### RN-AUTH-001
- **Identificador**: `RN-AUTH-001`
- **Descripción**: La autenticación requiere coincidencia exacta de contraseña mediante verificación criptográfica *bcrypt* contra el hash persistido en la tabla `USUARIO`.
- **Motivo**: Proteger la confidencialidad de las credenciales de acceso y evitar almacenar contraseñas en texto plano.
- **Módulos afectados**: `auth`, todos los módulos protegidos.
- **Archivos donde se implementa**: [`backend/app/routers/auth.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/auth.py) (Líneas 64–78).
- **Endpoints relacionados**: `POST /api/auth/login`
- **Historias de usuario relacionadas**: [HU-AUTH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md#hu-auth-001)

---

### RN-AUTH-002
- **Identificador**: `RN-AUTH-002`
- **Descripción**: La sesión emitida tiene una vigencia fija e improrrogable de 24 horas (`ACCESS_TOKEN_EXPIRE_HOURS = 24`) contenida en el *claim* `exp` del token JWT.
- **Motivo**: Limitar la ventana temporal de exposición ante el eventual compromiso de un token de acceso en un cliente web.
- **Módulos afectados**: `auth`, `dashboard`, `personal`, `cronologia`, `estadisticas`, `reportes`, `sincronizar`.
- **Archivos donde se implementa**: [`backend/app/routers/auth.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/auth.py) (Líneas 13, 100–108), [`backend/app/dependencies.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/dependencies.py) (Líneas 12–26).
- **Endpoints relacionados**: `POST /api/auth/login`, `GET /api/auth/me`, todos los endpoints que inyectan `get_current_user`.
- **Historias de usuario relacionadas**: [HU-AUTH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md#hu-auth-001), [HU-AUTH-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md#hu-auth-003)

---

### RN-AUTH-003
- **Identificador**: `RN-AUTH-003`
- **Descripción**: Los usuarios con estado inactivo (`activo = FALSE` o `0` en la tabla `USUARIO`) tienen el acceso bloqueado de manera absoluta, independientemente de que proporcionen la contraseña correcta.
- **Motivo**: Permitir al administrador suspender de forma inmediata el acceso a usuarios desvinculados o sancionados sin eliminar su historial de auditoría ni sus relaciones en base de datos.
- **Módulos afectados**: `auth`.
- **Archivos donde se implementa**: [`backend/app/routers/auth.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/auth.py) (Líneas 58–63).
- **Endpoints relacionados**: `POST /api/auth/login`
- **Historias de usuario relacionadas**: [HU-AUTH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md#hu-auth-001)

---

## 🛡️ 2. Validaciones y Sesión

### RN-AUTH-004
- **Identificador**: `RN-AUTH-004`
- **Descripción**: El correo electrónico ingresado debe ser normalizado a minúsculas (`correo.lower()`) antes de realizar la consulta en la base de datos.
- **Motivo**: Evitar fallos de inicio de sesión debido a diferencias tipográficas o autocapitalización en teclados móviles.
- **Módulos afectados**: `auth`.
- **Archivos donde se implementa**: [`backend/app/routers/auth.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/auth.py) (Líneas 47).
- **Endpoints relacionados**: `POST /api/auth/login`
- **Historias de usuario relacionadas**: [HU-AUTH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md#hu-auth-001)

---

### RN-AUTH-005
- **Identificador**: `RN-AUTH-005`
- **Descripción**: Al autenticarse satisfactoriamente, el sistema actualiza de manera obligatoria la marca de tiempo `ultimo_login` en el registro correspondiente del usuario.
- **Motivo**: Registrar trazabilidad de auditoría sobre el último acceso efectivo de cada cuenta al sistema.
- **Módulos afectados**: `auth`.
- **Archivos donde se implementa**: [`backend/app/routers/auth.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/auth.py) (Líneas 88–94).
- **Endpoints relacionados**: `POST /api/auth/login`
- **Historias de usuario relacionadas**: [HU-AUTH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md#hu-auth-001)

---

### RN-AUTH-006
- **Identificador**: `RN-AUTH-006`
- **Descripción**: Cualquier respuesta HTTP `401 Unauthorized` originada por token vencido o corrupto desencadena la purga forzosa del token en el cliente (`localStorage.removeItem`) y la redirección a `#/login`.
- **Motivo**: Evitar estados inconsistentes en la interfaz de usuario donde se muestren componentes vacíos por falta de autorización.
- **Módulos afectados**: `auth`, cliente frontend global.
- **Archivos donde se implementa**: [`frontend/src/services/api.ts`](file:///c:/Users/alejo/Downloads/automPYdrive/frontend/src/services/api.ts) (Líneas 16–19).
- **Endpoints relacionados**: Todos los endpoints protegidos.
- **Historias de usuario relacionadas**: [HU-AUTH-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md#hu-auth-003)

---

## ⚡ 3. Integración Externa y Tolerancia a Fallos

### RN-AUTH-007
- **Identificador**: `RN-AUTH-007`
- **Descripción**: La indisponibilidad o expiración del token de Google Drive no debe bajo ninguna circunstancia impedir ni bloquear el inicio de sesión local en el sistema BIMEH.
- **Motivo**: Mantener la alta disponibilidad del sistema para operaciones de consulta, visualización y carga manual de archivos locales aun si la nube de Google presenta fallos de conectividad.
- **Módulos afectados**: `auth`, `sincronizar`.
- **Archivos donde se implementa**: [`backend/app/routers/auth.py`](file:///c:/Users/alejo/Downloads/automPYdrive/backend/app/routers/auth.py) (Líneas 81–86).
- **Endpoints relacionados**: `POST /api/auth/login`, `GET /api/auth/drive-status`
- **Historias de usuario relacionadas**: [HU-AUTH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md#hu-auth-001), [HU-AUTH-004](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/historias_usuario.md#hu-auth-004)

> [!WARNING]
> Si el token de Google Drive se encuentra vencido, los usuarios con rol `ADMINISTRATIVO` podrán iniciar sesión normalmente, pero la sincronización remota desde Drive arrojará error hasta que se reautorice la cuenta institucional vía OAuth.

# Historias de Usuario — Módulo de Autenticación y Control de Acceso (`auth`)

---

# HU-AUTH-001

## Historia
**Como** usuario del sistema BIMEH (Comandante, Secretario de Personal o Directivo)  
**Quiero** iniciar sesión con mi correo electrónico y contraseña  
**Para** acceder a las funcionalidades del sistema según mis permisos asignados.

## Descripción
El usuario ingresa al sistema a través de la pantalla de inicio de sesión (`/login`), ingresando sus credenciales (correo electrónico y contraseña). El sistema valida la existencia de la cuenta en la tabla `USUARIO`, verifica que el usuario se encuentre en estado activo (`activo = TRUE`), valida la contraseña contra el hash almacenado utilizando *bcrypt*, y emite un token JWT firmado con una vigencia de 24 horas.

## Criterios de Aceptación
- El correo electrónico debe tener formato válido de email y convertirse automáticamente a minúsculas para la búsqueda.
- Si las credenciales son incorrectas o el correo no existe, el sistema debe retornar un código de error HTTP `401 Unauthorized` con el mensaje claro `"Correo o contraseña incorrectos"`.
- Si el usuario existe pero tiene el campo `activo = FALSE`, el sistema debe denegar el acceso con HTTP `401 Unauthorized` y el mensaje `"El usuario se encuentra inactivo"`.
- En caso de autenticación exitosa, el sistema debe:
  1. Actualizar el campo `ultimo_login` en la base de datos con la marca de tiempo actual.
  2. Obtener los roles asociados al usuario en la tabla `ROL` vía `USUARIO_ROL`.
  3. Generar y retornar un token JWT que incluya `sub` (ID de usuario), `nombre`, `correo`, `roles` y la fecha de expiración (`exp = utcnow + 24 horas`).
  4. Guardar el token en el almacenamiento local del cliente (`localStorage.bimej12_auth_token`).
  5. Redireccionar al usuario a la vista principal (`/`).
- La verificación de credenciales de Google Drive no debe bloquear ni impedir el inicio de sesión si el servicio externo no está configurado.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-AUTH-001](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md#rn-auth-001), [RN-AUTH-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md#rn-auth-002), [RN-AUTH-003](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md#rn-auth-003), [RN-AUTH-004](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md#rn-auth-004)
- **Endpoints relacionados**: `POST /api/auth/login`
- **Componentes frontend relacionados**: `frontend/src/features/auth/views/LoginView.vue`, `frontend/src/features/auth/stores/authStore.ts`, `frontend/src/features/auth/services/auth.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/auth.py` (`login`), `backend/app/dependencies.py`

---

# HU-AUTH-002

## Historia
**Como** usuario autenticado  
**Quiero** cerrar mi sesión activa  
**Para** proteger la confidencialidad de la información operacional y evitar accesos no autorizados en terminales compartidas.

## Descripción
El usuario presiona el botón de cierre de sesión en la barra lateral o barra de navegación. La aplicación envía la notificación de desconexión al backend, remueve el token JWT del almacenamiento local del navegador, resetea el estado del store `authStore` y redirige inmediatamente al usuario a la pantalla de `/login`.

## Criterios de Aceptación
- Al invocar la acción de logout, se debe eliminar la clave `bimej12_auth_token` de `localStorage`.
- El estado reactivo de Pinia (`isAuthenticated`, `usuario`, `roles`) debe quedar limpio (`null` / `false`).
- El usuario debe ser redirigido forzosamente a la ruta `/login`.
- Si el usuario intenta navegar hacia atrás o acceder a una ruta protegida mediante la barra de URL tras haber cerrado sesión, el guardián de rutas (`router.beforeEach`) debe interceptarlo y redirigirlo a `/login`.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-AUTH-005](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md#rn-auth-005)
- **Endpoints relacionados**: `POST /api/auth/logout`
- **Componentes frontend relacionados**: `frontend/src/components/layout/Sidebar.vue`, `frontend/src/components/layout/Navbar.vue`, `frontend/src/features/auth/stores/authStore.ts`
- **Controllers/Services relacionados**: `backend/app/routers/auth.py` (`logout`)

---

# HU-AUTH-003

## Historia
**Como** sistema cliente y guardián de rutas  
**Quiero** validar la vigencia y autenticidad del token JWT en cada petición y cambio de ruta  
**Para** garantizar que únicamente usuarios con una sesión válida puedan consultar y sincronizar datos.

## Descripción
Todas las vistas del sistema (excepto `/login`) poseen el metadato `requiresAuth: true`. El interceptor de Vue Router verifica la existencia del token antes de cargar cualquier vista con *code splitting*. Asimismo, el interceptor HTTP `fetchWithAuth` en `src/services/http.ts` inyecta la cabecera `Authorization: Bearer <token>` en cada solicitud hacia los endpoints protegidos del backend. Si el backend retorna HTTP 401 por token expirado o inválido, el frontend purga automáticamente las credenciales y traslada al usuario al login.

## Criterios de Aceptación
- Las rutas con `meta.requiresAuth = true` bloquean la navegación si `authStore.isAuthenticated` es falso.
- Si un usuario ya autenticado navega voluntariamente hacia `/login`, el router lo redirige a la vista raíz `/`.
- Si el token JWT ha expirado (más de 24 horas transcurridas desde su emisión), el backend debe responder `HTTP 401 Unauthorized` con el mensaje `"El token de sesión ha expirado"`.
- Si el token posee una firma adulterada o formato incorrecto, el backend debe responder `HTTP 401 Unauthorized` con el mensaje `"Token de sesión inválido"`.
- Ante cualquier respuesta `401` capturada en `fetchWithAuth` (`src/services/http.ts`), se debe purgar el token de `localStorage` y cambiar la URL a `#/login`.

## Metadata
- **Prioridad**: Alta
- **Roles involucrados**: `ADMINISTRATIVO`, `CONSULTA`
- **Reglas de negocio relacionadas**: [RN-AUTH-002](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md#rn-auth-002), [RN-AUTH-006](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md#rn-auth-006)
- **Endpoints relacionados**: `GET /api/auth/me`
- **Componentes frontend relacionados**: `frontend/src/router/index.ts`, `frontend/src/services/http.ts` (`fetchWithAuth`), [`frontend/src/services/api.ts`](file:///c:/Users/alejo/Downloads/automPYdrive/frontend/src/services/api.ts)
- **Controllers/Services relacionados**: `backend/app/dependencies.py` (`get_current_user`)

---

# HU-AUTH-004

## Historia
**Como** usuario administrativo  
**Quiero** verificar si la conexión con Google Drive se encuentra autorizada  
**Para** saber si es posible realizar la sincronización remota de novedades o si es necesario reautorizar la cuenta institucional.

## Descripción
El sistema consulta periódicamente o por demanda el estado del token de Google Drive en el servidor a través del endpoint `/api/auth/drive-status` y el servicio `auth.service.ts`, retornando si las credenciales son válidas o si se requiere reautenticación OAuth.

## Criterios de Aceptación
- Debe responder `{"connected": true}` si el token de Google Drive existe y es válido.
- Debe responder `{"connected": false, "reason": "token_invalid"}` o el detalle del error en caso de requerir reautorización.
- No debe bloquear el uso general del sistema si Google Drive se encuentra desconectado.

## Metadata
- **Prioridad**: Media
- **Roles involucrados**: `ADMINISTRATIVO`
- **Reglas de negocio relacionadas**: [RN-AUTH-007](file:///c:/Users/alejo/Downloads/automPYdrive/documentacion/modules/auth/reglas_negocio.md#rn-auth-007)
- **Endpoints relacionados**: `GET /api/auth/drive-status`
- **Componentes frontend relacionados**: `frontend/src/features/sincronizar/views/SincronizarView.vue`, `frontend/src/features/sincronizar/components/SyncSourceSelector.vue`, `frontend/src/components/layout/Navbar.vue`, `frontend/src/features/auth/services/auth.service.ts`
- **Controllers/Services relacionados**: `backend/app/routers/auth.py` (`drive_status`), `backend/config/auth.py`

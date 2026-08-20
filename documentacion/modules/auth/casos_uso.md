# Casos de Uso — Módulo de Autenticación y Control de Acceso (`auth`)

---

## CU-AUTH-001: Inicio de Sesión de Usuario

### Actores
- **Principal**: Usuario del Sistema (Rol `ADMINISTRATIVO` o `CONSULTA`).
- **Secundario**: Servidor Backend BIMEH, Base de Datos PostgreSQL.

### Precondiciones
1. El usuario debe poseer una cuenta previamente registrada en la tabla `USUARIO`.
2. El servicio backend debe estar operativo y accesible en la red.

### Flujo Principal (Éxito)
1. El usuario ingresa a la aplicación web a través del navegador.
2. El guardián de rutas (`src/router/index.ts`) detecta que no hay sesión activa y renderiza la vista `src/features/auth/views/LoginView.vue`.
3. El usuario ingresa su correo electrónico y su contraseña en el formulario y presiona **"Iniciar Sesión"**.
4. El frontend ejecuta `authService.login()` en `src/features/auth/services/auth.service.ts`, enviando una solicitud `POST /api/auth/login` mediante el cliente base `@services/http`.
5. El backend normaliza el correo a minúsculas y consulta el registro en la tabla `USUARIO`.
6. El backend valida que el campo `activo` sea `TRUE`.
7. El backend valida que la contraseña coincida con el hash almacenado usando `bcrypt.checkpw`.
8. El backend consulta los roles asignados en `ROL` y `USUARIO_ROL`.
9. El backend actualiza la columna `ultimo_login` con la fecha y hora actual.
10. El backend genera un token JWT codificado con clave secreta HS256, expiración de 24 horas y los datos del usuario.
11. El backend responde con código HTTP `200 OK` y el payload con el token y perfil del usuario.
12. El frontend almacena el token en `localStorage.bimej12_auth_token`, actualiza el store `authStore` (`src/features/auth/stores/authStore.ts`) y redirige al Dashboard (`/`).

### Flujos Alternativos y Excepciones

#### A1: Credenciales Incorrectas o Correo Inexistente
- **Paso 5 o 7**: Si el correo no existe en la base de datos o la contraseña no coincide con el hash de *bcrypt*:
  1. El backend retorna `HTTP 401 Unauthorized` con el mensaje `{"detail": "Correo o contraseña incorrectos"}`.
  2. El frontend muestra una alerta de error en color rojo indicando que las credenciales no son válidas.
  3. El usuario permanece en la pantalla de login para reintentar.

#### A2: Usuario Inactivo
- **Paso 6**: Si el registro en la base de datos tiene `activo = FALSE`:
  1. El backend retorna `HTTP 401 Unauthorized` con el mensaje `{"detail": "El usuario se encuentra inactivo"}`.
  2. El frontend notifica que la cuenta está inactiva y debe contactar al administrador del sistema.

#### A3: Falla Temporal en Conexión a Google Drive
- **Paso 10**: Si el token de Google Drive no está disponible o la API de Google no responde:
  1. El backend emite una advertencia en el log del servidor `[AUTH WARNING] Google Drive no autenticado aún`.
  2. El flujo continúa normalmente emitiendo el token JWT local sin interrumpir el login del usuario.

---

## CU-AUTH-002: Cierre de Sesión

### Actores
- **Principal**: Usuario Autenticado.
- **Secundario**: Cliente Frontend (`authStore.ts`, `Sidebar.vue`, `Navbar.vue`, `router/index.ts`).

### Precondiciones
- El usuario debe tener una sesión activa iniciada.

### Flujo Principal
1. El usuario hace clic en la opción **"Cerrar Sesión"** en la barra lateral (`Sidebar.vue`) o barra superior (`Navbar.vue`).
2. El frontend ejecuta el método `logout()` en `src/features/auth/stores/authStore.ts`.
3. El frontend realiza la llamada `POST /api/auth/logout`.
4. El frontend elimina el token JWT de `localStorage` y reinicia las variables reactivas de sesión.
5. El enrutador redirige al usuario a la ruta `#/login`.
6. Cualquier intento posterior de navegación a rutas privadas es interceptado por `router.beforeEach`.

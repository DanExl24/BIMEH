# Guía Didáctica: Configuración y Uso de Electron

¡Bienvenido al desarrollo de aplicaciones de escritorio con Electron! Esta guía está diseñada para que comprendas paso a paso la estructura que hemos creado, qué hace cada archivo y cómo funciona el flujo de trabajo de escritorio con Vue 3 y FastAPI.

---

## 1. Arquitectura de una Aplicación Electron

Electron combina **Chromium** (el navegador web) y **Node.js** (el motor de ejecución de Javascript en servidor) en una sola plataforma. Funciona con dos tipos de procesos principales:

### Proceso Principal (Main Process)
* **Archivo:** `frontend/electron/main.js`
* **Qué hace:** Corre sobre Node.js. Es el que tiene permisos para interactuar con el sistema operativo (abrir ventanas, acceder al disco, ejecutar otros programas). Controla el ciclo de vida de la aplicación.
* **Flujo:** Crea una ventana de navegador (`BrowserWindow`) y carga la URL del frontend (en desarrollo) o los archivos locales compilados (en producción).

### Proceso de Renderizado (Renderer Process)
* **Qué hace:** Es la interfaz gráfica que ve el usuario. En nuestro caso, es nuestra aplicación **Vue 3**.
* **Seguridad:** Por defecto, el proceso de renderizado no tiene acceso a Node.js de forma directa (para evitar que un script malicioso en la web borre archivos del disco).

### Script de Precarga (Preload Script)
* **Archivo:** `frontend/electron/preload.js`
* **Qué hace:** Actúa como un puente seguro. Corre antes de que se cargue la página web y tiene acceso tanto a Node.js como al DOM del frontend. Expone funciones o variables seguras del sistema al frontend de Vue mediante `contextBridge.exposeInMainWorld`.

---

## 2. Explicación de los Archivos Creados

### `frontend/electron/main.js`
Este archivo inicializa la ventana del escritorio:
1. Reconstruye `__dirname` ya que estamos usando módulos ES (`"type": "module"` en `package.json`).
2. Configura las preferencias web de la ventana para habilitar el script `preload.js` y el aislamiento de contexto (`contextIsolation: true`).
3. Detecta el entorno:
   * Si está en **desarrollo**, carga `http://localhost:5173` (el servidor de desarrollo de Vite) para que tengas recarga en caliente (Hot Reload) al modificar el código de Vue.
   * Si está en **producción**, carga el archivo HTML compilado de la app: `dist/index.html`.

### `frontend/electron/preload.js`
* Registra el objeto `window.electronAPI` en el navegador de la aplicación Vue.
* Actualmente expone la propiedad `platform` (ej. `win32` para Windows), pero en el futuro te servirá para enviar o recibir mensajes desde Node.js al frontend mediante `ipcRenderer`.

---

## 3. Ajustes de Compatibilidad Realizados en Vue y Vite

Para que la página web de Vue pueda abrirse localmente como un archivo del disco duro (`file:///.../index.html`) en lugar de servirse desde un servidor web tradicional, realizamos dos ajustes esenciales:

### Enrutamiento Hash (`createWebHashHistory`)
* **Ubicación:** [`frontend/src/router/index.ts`](file:///c:/Users/alejo/Downloads/automPYdrive/frontend/src/router/index.ts)
* **Por qué:** El enrutamiento web clásico (`createWebHistory`) busca direcciones como `file:///C:/dist/personal`, lo cual causa un error de archivo no encontrado en el explorador. El modo Hash añade un `#` (ej. `file:///C:/dist/index.html#/personal`), permitiendo que el enrutador de Vue intercepte la URL internamente y muestre la página correcta de forma local.

### Ruta de Assets Relativa (`base: './'`)
* **Ubicación:** [`frontend/vite.config.ts`](file:///c:/Users/alejo/Downloads/automPYdrive/frontend/vite.config.ts)
* **Por qué:** Por defecto, Vite genera enlaces como `/assets/index.js` (rutas absolutas), que en un sistema de escritorio buscarían el archivo en la raíz del disco duro (`C:/assets/index.js`). Configurar `base: './'` convierte los enlaces en rutas relativas al archivo actual (`./assets/index.js`), permitiendo que carguen desde cualquier carpeta donde se instale la aplicación.

---

## 4. Instrucciones para Ejecutar y Desarrollar

Para trabajar localmente en tu app de escritorio, sigue estos pasos desde terminales independientes:

### Paso 1: Levantar el Servidor Backend (FastAPI)
Ejecuta el servidor de Python como de costumbre:
```bash
cd backend
..\.venv\Scripts\activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Paso 2: Levantar el Servidor de Desarrollo Frontend (Vite)
Este servidor servirá la app de Vue con Hot-Reload:
```bash
cd frontend
npm run dev
```

### Paso 3: Lanzar la Ventana de Escritorio de Electron
En una tercera terminal, arranca la ventana de Electron (que se conectará automáticamente a la URL de desarrollo de Vue):
```bash
cd frontend
npm run electron:dev
```

---

## 5. El Futuro: Conectarse a la Nube y Compilar la App

1. **Conexión a Neon (PostgreSQL en la nube):**
   * Cuando subas la base de datos a Neon, solo necesitaremos modificar los datos de conexión en `backend/app/database.py` (o en un archivo `.env` que configuremos) para que apunte a la base de datos de Neon de forma remota. El frontend y la app de Electron seguirán funcionando exactamente igual, pero consumiendo datos en la nube.
   
2. **Distribución (Generar el ejecutable `.exe`):**
   * Para empaquetar todo como un instalador instalable en Windows, más adelante instalaremos `electron-builder`. Este empaquetará el frontend compilado (`dist/`) junto con el código principal de Electron.

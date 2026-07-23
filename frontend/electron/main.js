import { app, BrowserWindow } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';

// En entornos con ES Modules (debido a "type": "module" en package.json),
// __dirname y __filename no están definidos globalmente. Los reconstruimos aquí:
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function createWindow() {
  // Crear la ventana del navegador con dimensiones optimizadas
  const mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    title: "BIMEH - Sistema de Gestión de Personal",
    webPreferences: {
      // Cargar el script de precarga (preload)
      preload: path.join(__dirname, 'preload.js'),
      // Aislar los contextos de Electron y de la página web por seguridad (Recomendado)
      contextIsolation: true,
      // Desactivar Node de forma directa en el frontend para evitar vulnerabilidades XSS
      nodeIntegration: false,
    },
  });

  // Determinar si estamos en modo desarrollo o producción
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

  if (isDev) {
    // En desarrollo, cargar el servidor de Vite
    mainWindow.loadURL('http://localhost:5173');
    // Abrir herramientas de desarrollo automáticamente
    mainWindow.webContents.openDevTools();
  } else {
    // En producción, cargar el archivo HTML compilado de la carpeta dist/
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

import { spawn } from 'child_process';

let apiProcess = null;

// Función para arrancar el backend de Python en producción
function startBackend() {
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
  if (!isDev) {
    // En producción, el ejecutable de la API se copia a la carpeta de recursos (resources) de la aplicación
    const apiPath = path.join(process.resourcesPath, 'bimeh-api.exe');
    
    // Carpeta AppData escribible propia de la aplicación para guardar datos dinámicos localmente
    const userDataPath = app.getPath('userData');
    
    console.log(`Iniciando API en: ${apiPath}`);
    console.log(`Directorio de trabajo (AppData): ${userDataPath}`);
    
    // Levanta el proceso de Python y redirige el directorio de trabajo (cwd) a userDataPath
    apiProcess = spawn(apiPath, [], {
      cwd: userDataPath,
      env: { ...process.env }
    });

    apiProcess.stdout.on('data', (data) => {
      console.log(`[FastAPI stdout]: ${data}`);
    });

    apiProcess.stderr.on('data', (data) => {
      console.error(`[FastAPI stderr]: ${data}`);
    });

    apiProcess.on('close', (code) => {
      console.log(`El subproceso del backend cerró con código: ${code}`);
    });
  }
}

// Iniciar Electron una vez que esté listo
app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', () => {
    // En macOS, las apps suelen seguir activas en el dock y se recrean al hacer click
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Salir del proceso cuando todas las ventanas estén cerradas (excepto en macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Evento de ciclo de vida antes de salir de Electron: detener el subproceso del backend
app.on('will-quit', () => {
  if (apiProcess) {
    console.log('Deteniendo subproceso de la API de Python...');
    apiProcess.kill();
  }
});

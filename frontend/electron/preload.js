import { contextBridge } from 'electron';

// El script de precarga (preload) corre antes de que el proceso de renderizado (Vue) se cargue.
// Aquí exponemos APIs seguras del sistema a través de contextBridge.
contextBridge.exposeInMainWorld('electronAPI', {
  // Exponemos la plataforma actual para saber si estamos en 'win32', 'darwin' o 'linux'
  platform: process.platform,
  
  // Aquí puedes exponer funciones personalizadas que llamen a ipcRenderer.invoke en el futuro
  // si necesitas transferir datos de forma segura entre Node.js y la aplicación web Vue.
});

const { contextBridge, ipcRenderer } = require('electron');

// El script de precarga (preload) corre antes de que el proceso de renderizado (Vue) se cargue.
// Al usar la extensión .cjs, Node.js lo ejecuta estrictamente en formato CommonJS.
contextBridge.exposeInMainWorld('electronAPI', {
  platform: process.platform,
  // Delega la apertura de URL al proceso principal de Electron via IPC
  openExternal: (url) => ipcRenderer.send('open-external', url),
});


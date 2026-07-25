const { contextBridge, shell } = require('electron');

// El script de precarga (preload) corre antes de que el proceso de renderizado (Vue) se cargue.
// Al usar la extensión .cjs, Node.js lo ejecuta estrictamente en formato CommonJS,
// lo cual es requerido por Electron para scripts de precarga.
contextBridge.exposeInMainWorld('electronAPI', {
  platform: process.platform,
  // Abre una URL en el navegador predeterminado del sistema operativo (Edge, Chrome, etc.)
  openExternal: (url) => shell.openExternal(url),
});

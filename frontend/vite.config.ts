import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  base: './',
  plugins: [vue()],
  server: {
    watch: {
      // Excluir la carpeta android para evitar que Vite dispare HMR loops
      // al copiar assets con "npm run mobile:sync"
      ignored: ['**/android/**', '**/dist/**']
    }
  }
})

<template>
  <div class="min-h-screen bg-darkBg text-slate-100 flex items-center justify-center p-4 font-sans select-none relative overflow-hidden">
    <!-- Animated background gradients -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse"></div>

    <div class="glass-panel max-w-md w-full p-8 rounded-3xl space-y-6 shadow-2xl border border-darkBorder/40 backdrop-blur-md relative z-10">
      <!-- Header -->
      <div class="text-center space-y-2">
        <div class="inline-flex p-3.5 bg-cyan-500/10 border border-cyan-500/25 rounded-2xl text-cyan-400 mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h2 class="text-xs text-cyan-400 font-bold uppercase tracking-widest">Unidad Militar BIMEJ 12</h2>
        <h1 class="text-xl font-extrabold tracking-tight text-slate-100 uppercase">Control de Acceso</h1>
        <p class="text-xs text-slate-500">Ingresa tus credenciales administrativas autorizadas</p>
      </div>

      <!-- Alertas de Error -->
      <div
        v-if="errorMessage"
        class="bg-red-500/10 border border-red-500/20 text-red-400 text-xs px-4 py-3 rounded-xl flex items-center gap-2 animate-bounce"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Estado de Drive OAuth (aparece si Drive no está autorizado tras login) -->
      <div
        v-if="needsDriveAuth"
        class="bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[11px] px-3.5 py-3 rounded-xl space-y-2"
      >
        <p class="font-bold flex items-center gap-1.5">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Google Drive no está autorizado en el servidor
        </p>
        <p class="text-slate-400">Para sincronizar reportes desde Drive, un administrador debe autorizar la cuenta de Google en el servidor.</p>
        <button
          @click="iniciarOAuth"
          class="mt-1 w-full py-2 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 rounded-lg text-[11px] font-bold text-amber-300 transition-all"
        >
          🔗 Autorizar Google Drive ahora
        </button>
        <button
          @click="continuarSinDrive"
          class="w-full py-2 text-slate-500 hover:text-slate-300 text-[10px] transition-all"
        >
          Continuar sin Drive →
        </button>
      </div>

      <!-- Nota informativa (cuando Drive está ok o no se ha verificado aún) -->
      <div v-if="!needsDriveAuth" class="bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-[11px] px-3.5 py-2.5 rounded-xl flex items-start gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cyan-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Para sincronizar desde Google Drive, es necesario autorizar la cuenta Google en la sección Sincronizar.</span>
      </div>

      <!-- Formulario -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <!-- Correo -->
        <div class="space-y-1.5">
          <label class="text-[10px] uppercase font-bold text-slate-400">Correo Electrónico:</label>
          <div class="relative">
            <input
              type="email"
              v-model="correo"
              required
              placeholder="ejemplo@bimeh.com"
              class="w-full bg-darkBg/60 border border-darkBorder rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-all font-mono"
            />
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3.5 top-3.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.206" />
            </svg>
          </div>
        </div>

        <!-- Contraseña -->
        <div class="space-y-1.5">
          <label class="text-[10px] uppercase font-bold text-slate-400">Contraseña:</label>
          <div class="relative">
            <input
              type="password"
              v-model="password"
              required
              placeholder="••••••••••••"
              class="w-full bg-darkBg/60 border border-darkBorder rounded-xl pl-10 pr-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-all font-mono"
            />
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3.5 top-3.5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
        </div>

        <!-- Botón -->
        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full mt-2 py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-800 disabled:text-slate-500 rounded-xl text-xs font-bold text-slate-100 flex items-center justify-center gap-2 transition-all cursor-pointer shadow-md shadow-cyan-900/20 active:scale-98 select-none"
        >
          <template v-if="authStore.loading">
            <div class="w-4 h-4 border-2 border-slate-100/20 border-t-slate-100 rounded-full animate-spin"></div>
            <span>VERIFICANDO...</span>
          </template>
          <span v-else>INGRESAR AL SISTEMA</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import { useAppStore } from '../stores/appStore'

const correo = ref('')
const password = ref('')
const errorMessage = ref('')
const needsDriveAuth = ref(false)

const authStore = useAuthStore()
const appStore = useAppStore()
const router = useRouter()

const handleLogin = async () => {
  errorMessage.value = ''
  needsDriveAuth.value = false
  try {
    const success = await authStore.login(correo.value, password.value)
    if (success) {
      // Verificar si Drive está autorizado en el servidor
      try {
        const driveRes = await fetch(`${appStore.apiBase}/api/auth/drive-status`)
        const driveData = await driveRes.json()
        if (driveData.connected) {
          router.push('/')
        } else {
          needsDriveAuth.value = true
        }
      } catch {
        // Si no se puede verificar Drive, dejar pasar al sistema
        router.push('/')
      }
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Error en las credenciales proporcionadas.'
  }
}

const iniciarOAuth = async () => {
  try {
    const callbackUrl = `${appStore.apiBase}/api/sincronizar/oauth/callback`
    const res = await fetch(`${appStore.apiBase}/api/sincronizar/oauth/url?redirect_uri=${encodeURIComponent(callbackUrl)}`)
    
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || `Error en el servidor (${res.status})`)
    }

    const data = await res.json()
    if (data.auth_url) {
      // En Electron: usar shell.openExternal para abrir en el navegador del sistema (Edge/Chrome)
      // En web o móvil: window.open en nueva pestaña
      const electronAPI = (window as any).electronAPI
      if (electronAPI && electronAPI.openExternal) {
        electronAPI.openExternal(data.auth_url)
      } else {
        window.open(data.auth_url, '_blank')
      }
      needsDriveAuth.value = false
      alert('Se abrió una ventana en tu navegador para autorizar Google Drive. Después de autorizar, vuelve a iniciar sesión aquí.')
    } else {
      throw new Error('El servidor no retornó una URL de autorización válida.')
    }
  } catch (err: any) {
    console.error('Error al iniciar OAuth:', err)
    errorMessage.value = err.message || 'No se pudo iniciar el flujo de autorización. Intenta de nuevo.'
  }
}

const continuarSinDrive = () => {
  needsDriveAuth.value = false
  router.push('/')
}
</script>

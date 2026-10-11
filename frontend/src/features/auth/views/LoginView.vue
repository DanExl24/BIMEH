<template>
  <div class="min-h-screen bg-darkBg text-slate-100 flex items-center justify-center p-4 font-sans select-none relative overflow-hidden">
    <!-- Ambient tactical glow -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>

    <div class="glass-panel max-w-md w-full p-5 sm:p-8 rounded-3xl space-y-6 shadow-2xl border border-darkBorder relative z-10">
      <!-- Header -->
      <div class="text-center space-y-2">
        <div class="inline-flex p-3.5 bg-gradient-to-br from-cyan-500/15 to-blue-500/10 border border-cyan-500/30 rounded-2xl text-cyan-400 mb-1 shadow-lg shadow-cyan-500/10">
          <ShieldCheck class="w-8 h-8 stroke-[2]" />
        </div>
        <div>
          <h2 class="text-xs text-cyan-400 font-bold uppercase tracking-widest">Unidad Militar BIMEJ 12</h2>
          <h1 class="text-xl sm:text-2xl font-black tracking-tight text-slate-100 uppercase">Control de Acceso</h1>
          <p class="text-xs text-slate-400 mt-1">Ingresa tus credenciales administrativas autorizadas</p>
        </div>
      </div>

      <!-- Alerta de Error (Clean tactical banner) -->
      <div
        v-if="errorMessage"
        class="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-3.5 rounded-xl flex items-start gap-2.5 shadow-sm"
      >
        <AlertCircle class="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
        <span class="font-medium leading-relaxed">{{ errorMessage }}</span>
      </div>

      <!-- Nota informativa previa -->
      <div class="bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs p-3 rounded-xl flex items-start gap-2.5">
        <Lock class="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
        <span class="text-slate-300 text-[11px] leading-relaxed">
          Acceso restringido para personal autorizado del BIMEJ 12. Todas las operaciones quedan registradas.
        </span>
      </div>

      <!-- Formulario -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <!-- Correo -->
        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-slate-300 uppercase tracking-wider block">Correo Electrónico:</label>
          <div class="relative">
            <input
              type="email"
              v-model="correo"
              required
              placeholder="ejemplo@bimeh.com"
              class="w-full bg-darkBg border border-darkBorder rounded-xl pl-11 pr-4 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/60 transition-all font-mono shadow-inner"
            />
            <Mail class="w-4 h-4 absolute left-3.5 top-3 text-slate-400 pointer-events-none" />
          </div>
        </div>

        <!-- Contraseña -->
        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-slate-300 uppercase tracking-wider block">Contraseña:</label>
          <div class="relative">
            <input
              type="password"
              v-model="password"
              required
              placeholder="••••••••••••"
              class="w-full bg-darkBg border border-darkBorder rounded-xl pl-11 pr-4 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/60 transition-all font-mono shadow-inner"
            />
            <KeyRound class="w-4 h-4 absolute left-3.5 top-3 text-slate-400 pointer-events-none" />
          </div>
        </div>

        <!-- Botón de Ingreso -->
        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full mt-3 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 rounded-xl text-xs sm:text-sm font-bold text-white flex items-center justify-center gap-2 transition-all cursor-pointer shadow-lg shadow-cyan-950/40 active:scale-98 select-none"
        >
          <Loader2 v-if="authStore.loading" class="w-4 h-4 animate-spin" />
          <span>{{ authStore.loading ? 'VERIFICANDO CREDENCIALES...' : 'INGRESAR AL SISTEMA' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ShieldCheck, 
  Lock, 
  Mail, 
  KeyRound, 
  AlertCircle, 
  Loader2 
} from 'lucide-vue-next'

import { useAuthStore } from '../stores/authStore'
import { authService } from '../services/auth.service'
import { useAppStore } from '@stores/appStore'

const correo = ref('')
const password = ref('')
const errorMessage = ref('')

const authStore = useAuthStore()
const appStore = useAppStore()
const router = useRouter()

const handleLogin = async () => {
  errorMessage.value = ''
  try {
    const success = await authStore.login(correo.value, password.value)
    if (success) {
      // Intentar sincronización en segundo plano (NO bloquea el login)
      try {
        const driveData = await authService.getDriveStatus()
        if (driveData.connected) {
          // Sincronización automática de toda la base de datos (descarga los días faltantes de cualquier mes)
          appStore.startDriveSync({
            tipo: 'todo',
            overwrite: false
          })
        } else {
          console.warn('[LOGIN] Google Drive no conectado. La sincronización automática no se ejecutará.')
        }
      } catch (driveErr) {
        console.warn('[LOGIN] No se pudo verificar estado de Google Drive:', driveErr)
      }

      // Siempre navegar al sistema, independientemente del estado de Drive
      router.push('/')
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Error en las credenciales proporcionadas.'
  }
}
</script>

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

      <!-- Formulario -->
      <form @submit.prevent="handleLogin" class="space-y-4">
        <!-- Correo Electrónico -->
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

        <!-- Botón de Ingreso -->
        <button 
          type="submit" 
          :disabled="authStore.loading"
          class="w-full mt-2 py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-800 disabled:text-slate-500 rounded-xl text-xs font-bold text-slate-100 flex items-center justify-center gap-2 transition-all cursor-pointer shadow-md shadow-cyan-900/20 active:scale-98 select-none"
        >
          <div 
            v-if="authStore.loading" 
            class="w-4 h-4 border-2 border-slate-100/20 border-t-slate-100 rounded-full animate-spin"
          ></div>
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

const correo = ref('')
const password = ref('')
const errorMessage = ref('')

const authStore = useAuthStore()
const router = useRouter()

const handleLogin = async () => {
  errorMessage.value = ''
  try {
    const success = await authStore.login(correo.value, password.value)
    if (success) {
      router.push('/')
    }
  } catch (error: any) {
    errorMessage.value = error.message || 'Error en las credenciales proporcionadas.'
  }
}
</script>

<template>
  <div>
    <!-- Mobile/Tablet Backdrop Overlay (under 1024px) -->
    <transition name="fade">
      <div 
        v-if="isOpen" 
        @click="$emit('close')"
        class="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
        aria-hidden="true"
      ></div>
    </transition>

    <!-- Navigation Sidebar / Drawer -->
    <aside 
      class="w-64 max-w-[85vw] sm:w-64 bg-darkCard/95 border-r border-darkBorder flex flex-col h-screen fixed left-0 top-0 z-50 transition-transform duration-300 lg:translate-x-0 shadow-2xl lg:shadow-none"
      :class="isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
    >
      <!-- Brand / Title -->
      <div class="h-16 pt-[env(safe-area-inset-top,0px)] flex items-center justify-between px-5 border-b border-darkBorder/60 bg-darkCard/80">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center text-darkBg font-black shadow-md shadow-cyan-500/20">
            <Shield class="w-5 h-5 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <h1 class="text-sm font-extrabold tracking-wider text-slate-100 uppercase">BIMEJ 12</h1>
            <p class="text-[11px] text-cyan-400 font-semibold tracking-widest uppercase flex items-center gap-1">
              <span class="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse"></span>
              Comando Operacional
            </p>
          </div>
        </div>

        <!-- Mobile/Tablet Close Button -->
        <button 
          @click="$emit('close')"
          class="lg:hidden text-slate-400 hover:text-slate-100 p-2 rounded-xl hover:bg-darkBorder/60 transition-colors cursor-pointer"
          aria-label="Cerrar menú"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Navigation Menu -->
      <nav class="flex-1 px-3 py-5 space-y-1.5 overflow-y-auto" role="navigation">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path" 
          :to="item.path"
          @click="$emit('close')"
          class="flex items-center gap-3.5 px-3.5 py-3 rounded-xl transition-all duration-200 group text-slate-400 hover:text-slate-100 hover:bg-slate-800/40 select-none"
          active-class="bg-cyan-500/15 text-cyan-400 border-l-3 border-cyan-400 font-semibold shadow-sm"
        >
          <component 
            :is="item.icon" 
            class="w-5 h-5 transition-transform duration-200 group-hover:scale-105"
            :class="$route.path === item.path ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'"
          />
          <span class="text-xs font-medium tracking-wide">{{ item.name }}</span>
        </router-link>
      </nav>

      <!-- Logout Button -->
      <div class="px-3 py-2 border-t border-darkBorder/40">
        <button 
          @click="handleLogout"
          class="w-full flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl transition-all duration-200 group text-red-400/80 hover:text-red-400 hover:bg-red-500/10 cursor-pointer text-left border-none bg-transparent select-none"
        >
          <LogOut class="w-5 h-5 transition-transform duration-200 group-hover:scale-105" />
          <span class="text-xs font-semibold">Cerrar Sesión</span>
        </button>
      </div>

      <!-- Footer Status info -->
      <div class="p-3.5 border-t border-darkBorder/60 bg-darkBg/50">
        <div class="flex items-center gap-2.5">
          <div class="w-2.5 h-2.5 bg-emerald-500 rounded-full animate-pulse shadow-sm shadow-emerald-500/50"></div>
          <div class="min-w-0 flex-1">
            <p class="text-xs font-semibold text-slate-300 truncate">Base de Datos Activa</p>
            <p class="text-[11px] text-slate-400 font-mono truncate">bimeh (PostgreSQL)</p>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { 
  LayoutDashboard, 
  Users, 
  BarChart3, 
  Calendar,
  Download,
  Upload,
  LogOut,
  X,
  Shield
} from 'lucide-vue-next'
import { useAuthStore } from '../../stores/authStore'
import { useRouter } from 'vue-router'

defineProps<{
  isOpen?: boolean
}>()

defineEmits(['close'])

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const menuItems = [
  { name: 'Dashboard General', path: '/', icon: LayoutDashboard },
  { name: 'Buscador de Personal', path: '/personal', icon: Users },
  { name: 'Estadísticas Históricas', path: '/estadisticas', icon: BarChart3 },
  { name: 'Cronología & Heatmap', path: '/cronologia', icon: Calendar },
  { name: 'Centro de Reportes', path: '/reportes', icon: Download },
  { name: 'Sincronizar Datos', path: '/sincronizar', icon: Upload }
]
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>


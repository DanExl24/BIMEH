<template>
  <aside class="w-64 bg-darkCard/95 border-r border-darkBorder flex flex-col h-screen fixed left-0 top-0 z-30">
    <!-- Brand / Title -->
    <div class="h-16 flex items-center justify-between px-6 border-b border-darkBorder">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-cyan-500 rounded-lg flex items-center justify-center text-darkBg font-bold shadow-lg shadow-cyan-500/20">
          B
        </div>
        <div>
          <h1 class="text-md font-bold tracking-wider text-slate-100 uppercase">BIMEJ 12</h1>
          <p class="text-[10px] text-cyan-400 font-semibold tracking-widest uppercase">Reportes Personal</p>
        </div>
      </div>
    </div>

    <!-- Navigation Menu -->
    <nav class="flex-1 px-4 py-6 space-y-2">
      <router-link 
        v-for="item in menuItems" 
        :key="item.path" 
        :to="item.path"
        class="flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group text-slate-400 hover:text-slate-100 hover:bg-darkBorder/40"
        active-class="bg-cyan-500/10 text-cyan-400 border-l-2 border-cyan-400 rounded-l-none font-medium"
      >
        <component 
          :is="item.icon" 
          class="w-5 h-5 transition-transform duration-200 group-hover:scale-110"
          :class="{'text-cyan-400': $route.path === item.path}"
        />
        <span class="text-sm font-medium">{{ item.name }}</span>
      </router-link>
    </nav>

    <!-- Footer Status info -->
    <div class="p-4 border-t border-darkBorder bg-darkBg/30">
      <div class="flex items-center gap-3">
        <div class="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse"></div>
        <div>
          <p class="text-[11px] font-medium text-slate-300">Base de Datos</p>
          <p class="text-[9px] text-slate-500">bimeh (PostgreSQL) activa</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { 
  LayoutDashboard, 
  Users, 
  BarChart3, 
  Calendar,
  Download,
  Upload
} from '@lucide/vue'

const menuItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Buscador Personal', path: '/personal', icon: Users },
  { name: 'Estadísticas Históricas', path: '/estadisticas', icon: BarChart3 },
  { name: 'Cronología y Heatmap', path: '/cronologia', icon: Calendar },
  { name: 'Exportar Reportes', path: '/reportes', icon: Download },
  { name: 'Sincronizar Reportes', path: '/sincronizar', icon: Upload }
]
</script>

import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@stores/authStore'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@features/auth/views/LoginView.vue'),
    meta: { title: 'Control de Acceso' }
  },
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@features/dashboard/views/DashboardView.vue'),
    meta: { requiresAuth: true, title: 'Módulo de Dashboard Operacional' }
  },
  {
    path: '/personal',
    name: 'personal',
    component: () => import('@features/personal/views/PersonalView.vue'),
    meta: { requiresAuth: true, title: 'Buscador y Perfiles de Personal' }
  },
  {
    path: '/personal/:cedula',
    name: 'personal-detalle',
    component: () => import('@features/personal/views/PersonalDetalleView.vue'),
    meta: { requiresAuth: true, title: 'Detalle Histórico de Integrante' }
  },
  {
    path: '/estadisticas',
    name: 'estadisticas',
    component: () => import('@features/estadisticas/views/EstadisticasView.vue'),
    meta: { requiresAuth: true, title: 'Análisis de Novedades y Tendencias' }
  },
  {
    path: '/cronologia',
    name: 'cronologia',
    component: () => import('@features/cronologia/views/CronologiaView.vue'),
    meta: { requiresAuth: true, title: 'Cronología de Actividad Diaria' }
  },
  {
    path: '/reportes',
    name: 'reportes',
    component: () => import('@features/reportes/views/ReportesView.vue'),
    meta: { requiresAuth: true, title: 'Reportes de Personal' }
  },
  {
    path: '/sincronizar',
    name: 'sincronizar',
    component: () => import('@features/sincronizar/views/SincronizarView.vue'),
    meta: { requiresAuth: true, title: 'Carga y Sincronización de Reportes' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router

import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { title: 'Control de Acceso' }
  },
  {
    path: '/',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true, title: 'Módulo de Dashboard Operacional' }
  },
  {
    path: '/personal',
    name: 'personal',
    component: () => import('../views/PersonalView.vue'),
    meta: { requiresAuth: true, title: 'Buscador y Perfiles de Personal' }
  },
  {
    path: '/personal/:cedula',
    name: 'personal-detalle',
    component: () => import('../views/PersonalDetalleView.vue'),
    meta: { requiresAuth: true, title: 'Detalle Histórico de Integrante' }
  },
  {
    path: '/estadisticas',
    name: 'estadisticas',
    component: () => import('../views/EstadisticasView.vue'),
    meta: { requiresAuth: true, title: 'Análisis de Novedades y Tendencias' }
  },
  {
    path: '/cronologia',
    name: 'cronologia',
    component: () => import('../views/CronologiaView.vue'),
    meta: { requiresAuth: true, title: 'Cronología de Actividad Diaria' }
  },
  {
    path: '/reportes',
    name: 'reportes',
    component: () => import('../views/ReportesView.vue'),
    meta: { requiresAuth: true, title: 'Reportes de Personal' }
  },
  {
    path: '/sincronizar',
    name: 'sincronizar',
    component: () => import('../views/SincronizarView.vue'),
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


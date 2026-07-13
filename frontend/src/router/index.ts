import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import PersonalView from '../views/PersonalView.vue'
import PersonalDetalleView from '../views/PersonalDetalleView.vue'
import EstadisticasView from '../views/EstadisticasView.vue'
import CronologiaView from '../views/CronologiaView.vue'
import ReportesView from '../views/ReportesView.vue'
import SincronizarView from '../views/SincronizarView.vue'
import LoginView from '../views/LoginView.vue'
import { useAuthStore } from '../stores/authStore'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/personal',
    name: 'personal',
    component: PersonalView,
    meta: { requiresAuth: true }
  },
  {
    path: '/personal/:cedula',
    name: 'personal-detalle',
    component: PersonalDetalleView,
    meta: { requiresAuth: true }
  },
  {
    path: '/estadisticas',
    name: 'estadisticas',
    component: EstadisticasView,
    meta: { requiresAuth: true }
  },
  {
    path: '/cronologia',
    name: 'cronologia',
    component: CronologiaView,
    meta: { requiresAuth: true }
  },
  {
    path: '/reportes',
    name: 'reportes',
    component: ReportesView,
    meta: { requiresAuth: true }
  },
  {
    path: '/sincronizar',
    name: 'sincronizar',
    component: SincronizarView,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
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


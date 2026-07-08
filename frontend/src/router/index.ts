import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import PersonalView from '../views/PersonalView.vue'
import PersonalDetalleView from '../views/PersonalDetalleView.vue'
import EstadisticasView from '../views/EstadisticasView.vue'
import CronologiaView from '../views/CronologiaView.vue'
import ReportesView from '../views/ReportesView.vue'
import SincronizarView from '../views/SincronizarView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView
  },
  {
    path: '/personal',
    name: 'personal',
    component: PersonalView
  },
  {
    path: '/personal/:cedula',
    name: 'personal-detalle',
    component: PersonalDetalleView
  },
  {
    path: '/estadisticas',
    name: 'estadisticas',
    component: EstadisticasView
  },
  {
    path: '/cronologia',
    name: 'cronologia',
    component: CronologiaView
  },
  {
    path: '/reportes',
    name: 'reportes',
    component: ReportesView
  },
  {
    path: '/sincronizar',
    name: 'sincronizar',
    component: SincronizarView
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

export default router

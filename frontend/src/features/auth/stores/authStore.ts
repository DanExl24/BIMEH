import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services/auth.service'

export interface User {
  nombre: string
  correo: string
  roles: string[]
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('bimej12_auth_token'))
  const user = ref<User | null>(null)
  const loading = ref(false)

  if (localStorage.getItem('bimej12_auth_user')) {
    try {
      user.value = JSON.parse(localStorage.getItem('bimej12_auth_user') || 'null')
    } catch {
      user.value = null
    }
  }

  const isAuthenticated = computed(() => !!token.value)

  const login = async (correo: string, password: string) => {
    loading.value = true
    try {
      const data = await authService.login({ correo, password })
      
      token.value = data.access_token
      user.value = data.usuario

      localStorage.setItem('bimej12_auth_token', data.access_token)
      localStorage.setItem('bimej12_auth_user', JSON.stringify(data.usuario))
      localStorage.setItem('bimej12_auth_time', Date.now().toString())
      
      return true
    } catch (error) {
      console.error('Login error:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const checkMe = async () => {
    if (!token.value) return false

    // Check client-side 24-hour expiration
    const tokenTimeStr = localStorage.getItem('bimej12_auth_time')
    if (tokenTimeStr) {
      const tokenTime = parseInt(tokenTimeStr, 10)
      const oneDayMs = 24 * 60 * 60 * 1000
      if (Date.now() - tokenTime > oneDayMs) {
        console.warn('Session token expired (older than 24 hours). Logging out.')
        logout()
        return false
      }
    }

    try {
      const data = await authService.checkMe()
      user.value = {
        nombre: data.nombre,
        correo: data.correo,
        roles: data.roles
      }
      localStorage.setItem('bimej12_auth_user', JSON.stringify(user.value))
      return true
    } catch (e) {
      logout()
      return false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('bimej12_auth_token')
    localStorage.removeItem('bimej12_auth_user')
    localStorage.removeItem('bimej12_auth_time')
    window.location.hash = '/login'
  }

  return {
    token,
    user,
    loading,
    isAuthenticated,
    login,
    checkMe,
    logout
  }
})

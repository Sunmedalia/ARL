import { defineStore } from 'pinia'
import { apiRequest, setCsrfToken } from '../api/client'

interface SessionData { username: string; csrf_token: string; ai_granted: boolean; session_expires_at: string }

export const useAuthStore = defineStore('auth', {
  state: () => ({ username: '', ready: false, authenticated: false, aiGranted: false }),
  actions: {
    async load(conversationId = '') {
      try {
        const suffix = conversationId ? `?conversation_id=${encodeURIComponent(conversationId)}` : ''
        const data = await apiRequest<SessionData>(`/api/user/session${suffix}`, {}, undefined, false)
        this.username = data.username
        this.aiGranted = data.ai_granted
        this.authenticated = true
        setCsrfToken(data.csrf_token)
      } catch (error) {
        this.username = ''
        this.aiGranted = false
        this.authenticated = false
        setCsrfToken('')
        throw error
      } finally {
        this.ready = true
      }
    },
    async login(username: string, password: string) {
      const data = await apiRequest<SessionData & { username: string }>('/api/user/login', {
        method: 'POST', body: JSON.stringify({ username, password }),
      })
      this.username = data.username
      this.authenticated = true
      await this.load()
    },
    async logout() {
      await apiRequest('/api/user/logout', { method: 'POST', body: '{}' })
      this.$reset(); location.assign('/next/login')
    },
  },
})

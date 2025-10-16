import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/services/api'
import type { Session, SessionCreate } from '@/types/session'

export const useSessionStore = defineStore('session', () => {
  const activeSession = ref<Session | null>(null)
  const sessions = ref<Session[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function createSession(data: SessionCreate) {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.post<Session>('/sessions', data)
      activeSession.value = response.data
      sessions.value.unshift(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSessions() {
    isLoading.value = true
    try {
      const response = await apiClient.get<Session[]>('/sessions')
      sessions.value = response.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      isLoading.value = false
    }
  }

  async function getSession(sessionId: string) {
    isLoading.value = true
    try {
      const response = await apiClient.get<Session>(`/sessions/${sessionId}`)
      activeSession.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function setActiveSession(session: Session) {
    activeSession.value = session
  }

  return {
    activeSession,
    sessions,
    isLoading,
    error,
    createSession,
    fetchSessions,
    getSession,
    setActiveSession
  }
})

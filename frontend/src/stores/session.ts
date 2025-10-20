import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/services/api'
import type { Session, SessionCreate } from '@/types/session'

export const useSessionStore = defineStore('session', () => {
  const activeSession = ref<Session | null>(null)
  const sessions = ref<Session[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const savedSessionId = ref<string | null>(localStorage.getItem('activeSessionId'))

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

  async function setActiveSession(sessionIdOrSession: string | Session) {
    if (typeof sessionIdOrSession === 'string') {
      await getSession(sessionIdOrSession)
    } else {
      activeSession.value = sessionIdOrSession
    }
    if (activeSession.value) {
      savedSessionId.value = activeSession.value.id
      localStorage.setItem('activeSessionId', activeSession.value.id)
    }
  }

  async function endSession(sessionId: string) {
    isLoading.value = true
    try {
      await apiClient.delete(`/sessions/${sessionId}`)
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      if (activeSession.value?.id === sessionId) {
        activeSession.value = null
        savedSessionId.value = null
        localStorage.removeItem('activeSessionId')
      }
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function deleteSession(sessionId: string) {
    return endSession(sessionId)
  }

  async function updateSessionTitle(sessionId: string, title: string) {
    isLoading.value = true
    try {
      const response = await apiClient.patch<Session>(`/sessions/${sessionId}`, { title })
      const index = sessions.value.findIndex(s => s.id === sessionId)
      if (index !== -1) {
        sessions.value[index] = response.data
      }
      if (activeSession.value?.id === sessionId) {
        activeSession.value = response.data
      }
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  return {
    activeSession,
    sessions,
    isLoading,
    error,
    savedSessionId: computed(() => savedSessionId.value),
    createSession,
    fetchSessions,
    getSession,
    setActiveSession,
    endSession,
    deleteSession,
    updateSessionTitle
  }
}, {
  persist: {
    paths: ['savedSessionId']
  }
})

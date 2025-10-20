import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useConnectionStore } from '@/stores/connection'
import { useMessagesStore } from '@/stores/messages'
import type { Session } from '@/types/session'

/**
 * Composable for managing session lifecycle and state
 */
export function useSession() {
  const sessionStore = useSessionStore()
  const connectionStore = useConnectionStore()
  const messagesStore = useMessagesStore()
  const router = useRouter()

  const activeSession = computed(() => sessionStore.activeSession)
  const sessions = computed(() => sessionStore.sessions)
  const isLoading = computed(() => sessionStore.isLoading)
  const error = computed(() => sessionStore.error)

  /**
   * Create a new session and connect to WebSocket
   */
  async function createSession(title?: string): Promise<Session | null> {
    try {
      const session = await sessionStore.createSession(title)
      if (session) {
        await connectionStore.connect(session.id)
      }
      return session
    } catch (err) {
      console.error('Failed to create session:', err)
      return null
    }
  }

  /**
   * Resume an existing session
   */
  async function resumeSession(sessionId: string): Promise<boolean> {
    try {
      await sessionStore.setActiveSession(sessionId)
      await messagesStore.fetchHistory(sessionId)
      await connectionStore.connect(sessionId)
      return true
    } catch (err) {
      console.error('Failed to resume session:', err)
      return false
    }
  }

  /**
   * End the current session
   */
  async function endSession(sessionId?: string): Promise<void> {
    const id = sessionId || activeSession.value?.id
    if (!id) return

    try {
      await sessionStore.endSession(id)
      connectionStore.disconnect()
      messagesStore.clearMessages()
    } catch (err) {
      console.error('Failed to end session:', err)
    }
  }

  /**
   * Switch to a different session
   */
  async function switchSession(sessionId: string): Promise<void> {
    // Disconnect from current session
    connectionStore.disconnect()

    // Resume the new session
    await resumeSession(sessionId)

    // Navigate to home if not already there
    if (router.currentRoute.value.name !== 'home') {
      await router.push({ name: 'home' })
    }
  }

  /**
   * Fetch all user sessions
   */
  async function fetchSessions(): Promise<void> {
    await sessionStore.fetchSessions()
  }

  /**
   * Delete a session
   */
  async function deleteSession(sessionId: string): Promise<boolean> {
    try {
      await sessionStore.deleteSession(sessionId)
      return true
    } catch (err) {
      console.error('Failed to delete session:', err)
      return false
    }
  }

  /**
   * Update session title
   */
  async function updateSessionTitle(sessionId: string, title: string): Promise<boolean> {
    try {
      await sessionStore.updateSessionTitle(sessionId, title)
      return true
    } catch (err) {
      console.error('Failed to update session title:', err)
      return false
    }
  }

  /**
   * Restore session from localStorage on app load
   */
  async function restoreSession(): Promise<void> {
    const savedSessionId = sessionStore.savedSessionId
    if (savedSessionId) {
      await resumeSession(savedSessionId)
    }
  }

  return {
    // State
    activeSession,
    sessions,
    isLoading,
    error,

    // Actions
    createSession,
    resumeSession,
    endSession,
    switchSession,
    fetchSessions,
    deleteSession,
    updateSessionTitle,
    restoreSession,
  }
}

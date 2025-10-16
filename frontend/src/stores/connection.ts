import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting'

export const useConnectionStore = defineStore('connection', () => {
  const status = ref<ConnectionStatus>('disconnected')
  const websocket = ref<WebSocket | null>(null)
  const reconnectAttempts = ref(0)
  const lastError = ref<string | null>(null)

  function setStatus(newStatus: ConnectionStatus) {
    status.value = newStatus
  }

  function setWebSocket(ws: WebSocket | null) {
    websocket.value = ws
  }

  function incrementReconnectAttempts() {
    reconnectAttempts.value++
  }

  function resetReconnectAttempts() {
    reconnectAttempts.value = 0
  }

  function setLastError(error: string | null) {
    lastError.value = error
  }

  return {
    status,
    websocket,
    reconnectAttempts,
    lastError,
    setStatus,
    setWebSocket,
    incrementReconnectAttempts,
    resetReconnectAttempts,
    setLastError
  }
})

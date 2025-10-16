import { ref, onUnmounted } from 'vue'
import { WebSocketClient } from '@/services/websocket'
import { useConnectionStore } from '@/stores/connection'
import { useMessagesStore } from '@/stores/messages'
import { MessageRole, MessageContentType } from '@/types/message'

export function useWebSocket(sessionId: string, token: string) {
  const connectionStore = useConnectionStore()
  const messagesStore = useMessagesStore()
  const client = ref<WebSocketClient | null>(null)

  async function connect() {
    try {
      connectionStore.setStatus('connecting')
      client.value = new WebSocketClient(sessionId, token)

      await client.value.connect()

      client.value.onMessage((message: any) => {
        handleMessage(message)
      })

      connectionStore.setStatus('connected')
      connectionStore.resetReconnectAttempts()
    } catch (error: any) {
      connectionStore.setStatus('disconnected')
      connectionStore.setLastError(error.message)
      throw error
    }
  }

  function handleMessage(message: any) {
    const { type, content, message_id } = message

    switch (type) {
      case 'system':
        console.log('[System]', content)
        break

      case 'command_sent':
        messagesStore.setStreaming(true)
        messagesStore.currentMessageId = message_id
        break

      case 'output_chunk':
        messagesStore.appendToLastMessage(content)
        break

      case 'command_complete':
        messagesStore.setStreaming(false)
        messagesStore.currentMessageId = null
        break

      case 'error':
        console.error('[Error]', content)
        messagesStore.setStreaming(false)
        break

      default:
        console.log('[Unknown message type]', type, message)
    }
  }

  function sendCommand(command: string) {
    if (client.value) {
      // Add user message to store
      messagesStore.addMessage({
        id: crypto.randomUUID(),
        session_id: sessionId,
        role: MessageRole.USER,
        content: command,
        content_type: MessageContentType.TEXT,
        metadata: null,
        timestamp: new Date().toISOString(),
        sequence_number: messagesStore.messages.length + 1,
        is_streamed: false
      })

      // Add placeholder for assistant response
      messagesStore.addMessage({
        id: crypto.randomUUID(),
        session_id: sessionId,
        role: MessageRole.ASSISTANT,
        content: '',
        content_type: MessageContentType.TEXT,
        metadata: null,
        timestamp: new Date().toISOString(),
        sequence_number: messagesStore.messages.length + 1,
        is_streamed: true
      })

      client.value.sendCommand(command)
    }
  }

  function disconnect() {
    if (client.value) {
      client.value.disconnect()
      connectionStore.setStatus('disconnected')
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    connect,
    sendCommand,
    disconnect,
    isConnected: () => client.value?.isConnected() ?? false
  }
}

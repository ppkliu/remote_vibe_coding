import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '@/services/api'
import type { Message } from '@/types/message'

export const useMessagesStore = defineStore('messages', () => {
  const messages = ref<Message[]>([])
  const isStreaming = ref(false)
  const currentMessageId = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  function addMessage(message: Message) {
    messages.value.push(message)
  }

  function appendToLastMessage(content: string) {
    if (messages.value.length > 0) {
      const lastMessage = messages.value[messages.value.length - 1]
      lastMessage.content += content
    }
  }

  function clearMessages() {
    messages.value = []
  }

  function setStreaming(streaming: boolean) {
    isStreaming.value = streaming
  }

  async function fetchHistory(sessionId: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get<Message[]>(`/sessions/${sessionId}/messages`)
      messages.value = response.data
    } catch (e: any) {
      error.value = e.message
      console.error('Failed to fetch message history:', e)
    } finally {
      isLoading.value = false
    }
  }

  return {
    messages,
    isStreaming,
    currentMessageId,
    isLoading,
    error,
    addMessage,
    appendToLastMessage,
    clearMessages,
    setStreaming,
    fetchHistory
  }
})

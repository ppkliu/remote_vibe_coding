import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Message } from '@/types/message'

export const useMessagesStore = defineStore('messages', () => {
  const messages = ref<Message[]>([])
  const isStreaming = ref(false)
  const currentMessageId = ref<string | null>(null)

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

  return {
    messages,
    isStreaming,
    currentMessageId,
    addMessage,
    appendToLastMessage,
    clearMessages,
    setStreaming
  }
})

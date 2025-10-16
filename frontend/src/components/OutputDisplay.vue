<template>
  <div class="output-display" ref="outputContainer">
    <div v-if="messages.length === 0" class="empty-state">
      <p class="text-gray-500 text-center">No messages yet. Send a command to get started!</p>
    </div>
    <div v-else class="messages-container">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', `message-${message.role}`]"
      >
        <div class="message-role">{{ formatRole(message.role) }}</div>
        <div class="message-content">
          <pre v-if="message.content">{{ message.content }}</pre>
          <span v-else class="streaming-indicator">...</span>
        </div>
        <div class="message-timestamp">{{ formatTime(message.timestamp) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { Message } from '@/types/message'
import { MessageRole } from '@/types/message'

interface Props {
  messages: Message[]
}

const props = defineProps<Props>()
const outputContainer = ref<HTMLElement | null>(null)

function formatRole(role: MessageRole): string {
  return role === MessageRole.USER ? 'You' : role === MessageRole.ASSISTANT ? 'Claude' : 'System'
}

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString()
}

function scrollToBottom() {
  nextTick(() => {
    if (outputContainer.value) {
      outputContainer.value.scrollTop = outputContainer.value.scrollHeight
    }
  })
}

watch(() => props.messages, scrollToBottom, { deep: true })
</script>

<style scoped>
.output-display {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #f9fafb;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  padding: 1rem;
  border-radius: 0.5rem;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-user {
  border-left: 4px solid #3b82f6;
}

.message-assistant {
  border-left: 4px solid #10b981;
}

.message-system {
  border-left: 4px solid #f59e0b;
  background: #fffbeb;
}

.message-role {
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  color: #374151;
}

.message-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 0.875rem;
  margin: 0;
}

.message-timestamp {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.5rem;
}

.streaming-indicator {
  color: #9ca3af;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>

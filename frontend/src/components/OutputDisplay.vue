<template>
  <div class="output-display" ref="outputContainer" @scroll="handleScroll">
    <div v-if="isStreaming" class="streaming-banner">
      <span class="streaming-indicator">●</span> Streaming response...
    </div>
    <div v-if="messages.length === 0" class="empty-state">
      <p class="text-gray-500 text-center">No messages yet. Send a command to get started!</p>
    </div>
    <div v-else class="messages-container">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', `message-${message.role}`]"
      >
        <div class="message-header">
          <div class="message-role">{{ formatRole(message.role) }}</div>
          <button
            v-if="message.content && message.role === 'ASSISTANT'"
            class="btn-copy-message"
            @click="copyToClipboard(message.content)"
            title="Copy to clipboard"
          >
            📋 Copy
          </button>
        </div>
        <div class="message-content">
          <pre v-if="message.content">{{ message.content }}</pre>
          <div v-else class="streaming-dots">
            <span class="streaming-indicator">●</span>
            <span class="streaming-indicator">●</span>
            <span class="streaming-indicator">●</span>
          </div>
        </div>
        <div class="message-footer">
          <span class="message-timestamp">{{ formatTime(message.timestamp) }}</span>
          <span v-if="message.metadata?.execution_time_ms" class="execution-time">
            Executed in {{ message.metadata.execution_time_ms }}ms
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { Message } from '@/types/message'
import { MessageRole } from '@/types/message'
import { useToastStore } from '@/stores/toast'

interface Props {
  messages: Message[]
  isStreaming?: boolean
}

const props = defineProps<Props>()
const toastStore = useToastStore()
const outputContainer = ref<HTMLElement | null>(null)
const userScrolledUp = ref(false)
const scrollThreshold = 100 // pixels from bottom

function formatRole(role: MessageRole): string {
  return role === MessageRole.USER ? 'You' : role === MessageRole.ASSISTANT ? 'Claude' : 'System'
}

function formatTime(timestamp: string): string {
  return new Date(timestamp).toLocaleTimeString()
}

function handleScroll() {
  if (!outputContainer.value) return
  const { scrollTop, scrollHeight, clientHeight } = outputContainer.value
  const distanceFromBottom = scrollHeight - scrollTop - clientHeight
  userScrolledUp.value = distanceFromBottom > scrollThreshold
}

function scrollToBottom() {
  // Only auto-scroll if user hasn't scrolled up
  if (!userScrolledUp.value) {
    nextTick(() => {
      if (outputContainer.value) {
        outputContainer.value.scrollTop = outputContainer.value.scrollHeight
      }
    })
  }
}

watch(() => props.messages, scrollToBottom, { deep: true })
watch(() => props.isStreaming, (streaming) => {
  // Auto-scroll when streaming starts
  if (streaming) {
    userScrolledUp.value = false
    scrollToBottom()
  }
})

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    toastStore.success('Copied to clipboard!')
  } catch (err) {
    toastStore.error('Failed to copy to clipboard')
  }
}
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

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-role {
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
}

.btn-copy-message {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  color: #6b7280;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.btn-copy-message:hover {
  background: #e5e7eb;
  color: #374151;
  border-color: #d1d5db;
}

.message-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 0.875rem;
  margin: 0;
}

.streaming-banner {
  position: sticky;
  top: 0;
  background: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  text-align: center;
  font-size: 0.875rem;
  font-weight: 500;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.message-timestamp {
  font-size: 0.75rem;
  color: #9ca3af;
}

.execution-time {
  font-size: 0.75rem;
  color: #10b981;
  font-weight: 500;
}

.streaming-dots {
  display: flex;
  gap: 0.25rem;
}

.streaming-indicator {
  color: #3b82f6;
  animation: pulse 1.5s infinite;
}

.streaming-indicator:nth-child(2) {
  animation-delay: 0.2s;
}

.streaming-indicator:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>

<template>
  <div :class="['connection-status', `status-${status}`]">
    <span class="status-dot"></span>
    <span class="status-text">{{ statusText }}</span>
    <!-- T100: Reconnect button when connection fails -->
    <button
      v-if="showReconnectButton"
      @click="$emit('reconnect')"
      class="btn-reconnect"
      title="Attempt to reconnect"
    >
      🔄 Reconnect
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useConnectionStore } from '@/stores/connection'
import type { ConnectionStatus } from '@/stores/connection'

interface Props {
  status: ConnectionStatus
  maxReconnectAttempts?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxReconnectAttempts: 5
})

const emit = defineEmits<{
  reconnect: []
}>()

const connectionStore = useConnectionStore()

const statusText = computed(() => {
  switch (props.status) {
    case 'connected':
      return 'Connected'
    case 'connecting':
      return 'Connecting...'
    case 'reconnecting':
      return `Reconnecting... (${connectionStore.reconnectAttempts}/${props.maxReconnectAttempts})`
    case 'disconnected':
      return 'Disconnected'
    default:
      return 'Unknown'
  }
})

// T100: Show reconnect button after max reconnection attempts
const showReconnectButton = computed(() => {
  return (
    props.status === 'disconnected' &&
    connectionStore.reconnectAttempts >= props.maxReconnectAttempts
  )
})
</script>

<style scoped>
.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-connected {
  background: #d1fae5;
  color: #065f46;
}

.status-connected .status-dot {
  background: #10b981;
}

.status-connecting,
.status-reconnecting {
  background: #fef3c7;
  color: #92400e;
}

.status-connecting .status-dot,
.status-reconnecting .status-dot {
  background: #f59e0b;
}

.status-disconnected {
  background: #fee2e2;
  color: #991b1b;
}

.status-disconnected .status-dot {
  background: #ef4444;
  animation: none;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.btn-reconnect {
  margin-left: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reconnect:hover {
  background: #2563eb;
  transform: scale(1.05);
}

.btn-reconnect:active {
  transform: scale(0.95);
}
</style>

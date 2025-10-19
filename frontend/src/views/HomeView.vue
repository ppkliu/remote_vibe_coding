<template>
  <div class="home-view">
    <header class="header">
      <div class="header-content">
        <h1 class="title">Claude Code Remote Controller</h1>
        <div class="header-actions">
          <ConnectionStatus :status="connectionStore.status" />
          <button @click="handleCreateSession" v-if="!sessionStore.activeSession" class="btn-primary">
            New Session
          </button>
          <button @click="handleLogout" class="btn-secondary">Logout</button>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div v-if="!sessionStore.activeSession" class="no-session">
        <p>Create a new session to start controlling Claude Code</p>
        <button @click="handleCreateSession" class="btn-primary btn-large">
          Create Session
        </button>
      </div>

      <div v-else class="chat-container">
        <OutputDisplay
          :messages="messagesStore.messages"
          :isStreaming="messagesStore.isStreaming"
          @open-file="handleOpenFile"
        />
        <CommandInput
          :disabled="connectionStore.status !== 'connected'"
          @submit="handleCommandSubmit"
        />
      </div>
    </main>

    <!-- Tool Approval Dialog -->
    <ToolApprovalDialog
      v-if="wsComposable"
      :show="!!wsComposable.toolApprovalRequest.value"
      :tool-name="wsComposable.toolApprovalRequest.value?.toolName || ''"
      :action="wsComposable.toolApprovalRequest.value?.action || ''"
      :prompt="wsComposable.toolApprovalRequest.value?.prompt || ''"
      @approve="handleApprove"
      @reject="handleReject"
    />

    <!-- File Viewer -->
    <FileViewer
      :show="showFileViewer"
      :file-path="selectedFilePath"
      @close="showFileViewer = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSessionStore } from '@/stores/session'
import { useMessagesStore } from '@/stores/messages'
import { useConnectionStore } from '@/stores/connection'
import { useToastStore } from '@/stores/toast'
import { useWebSocket } from '@/composables/useWebSocket'
import { useSession } from '@/composables/useSession'
import CommandInput from '@/components/CommandInput.vue'
import OutputDisplay from '@/components/OutputDisplay.vue'
import ConnectionStatus from '@/components/ConnectionStatus.vue'
import ToolApprovalDialog from '@/components/ToolApprovalDialog.vue'
import FileViewer from '@/components/FileViewer.vue'

const router = useRouter()
const authStore = useAuthStore()
const sessionStore = useSessionStore()
const messagesStore = useMessagesStore()
const connectionStore = useConnectionStore()
const toastStore = useToastStore()

let wsComposable: ReturnType<typeof useWebSocket> | null = null
const showFileViewer = ref(false)
const selectedFilePath = ref('')

async function handleCreateSession() {
  try {
    const session = await sessionStore.createSession({
      title: `Session ${new Date().toLocaleString()}`
    })

    // Connect WebSocket
    if (authStore.accessToken && session.id) {
      wsComposable = useWebSocket(session.id, authStore.accessToken)
      await wsComposable.connect()
      toastStore.success('Session created and connected!')
    }
  } catch (error: any) {
    console.error('Failed to create session:', error)
    toastStore.error(error?.message || 'Failed to create session')
  }
}

function handleCommandSubmit(command: string) {
  if (wsComposable) {
    wsComposable.sendCommand(command)
  }
}

function handleApprove() {
  if (wsComposable) {
    wsComposable.sendToolApproval(true)
  }
}

function handleReject() {
  if (wsComposable) {
    wsComposable.sendToolApproval(false)
  }
}

function handleOpenFile(filePath: string) {
  selectedFilePath.value = filePath
  showFileViewer.value = true
}

function handleLogout() {
  if (wsComposable) {
    wsComposable.disconnect()
  }
  authStore.logout()
  router.push('/login')
}

onMounted(async () => {
  // Fetch existing sessions
  await sessionStore.fetchSessions()

  // Restore saved session if available (T098)
  const sessionComposable = useSession()
  if (sessionStore.savedSessionId) {
    try {
      const savedSessionId = sessionStore.savedSessionId
      await sessionStore.setActiveSession(savedSessionId)

      // Fetch message history for restored session (T099)
      await messagesStore.fetchHistory(savedSessionId)

      // Reconnect WebSocket to restored session
      if (authStore.accessToken) {
        wsComposable = useWebSocket(savedSessionId, authStore.accessToken)
        await wsComposable.connect()
        toastStore.info('Session restored')
      }
    } catch (error: any) {
      console.error('Failed to restore session:', error)
      sessionStore.savedSessionId = ''
      localStorage.removeItem('activeSessionId')
    }
  }
})
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f3f4f6;
}

.header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  overflow: hidden;
}

.no-session {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
}

.no-session p {
  font-size: 1.125rem;
  color: #6b7280;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 0.5rem;
  margin: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.btn-primary {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.125rem;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-secondary:hover {
  background: #dc2626;
}
</style>

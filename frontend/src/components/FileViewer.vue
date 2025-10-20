<template>
  <div v-if="show" class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <div class="file-info">
          <h3 class="file-name">{{ fileName }}</h3>
          <span class="file-path">{{ filePath }}</span>
        </div>
        <button class="close-button" @click="handleClose">&times;</button>
      </div>

      <div class="modal-body">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading file...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <p class="error-message">{{ error }}</p>
          <button class="btn-retry" @click="loadFile">Try Again</button>
        </div>

        <div v-else class="file-content-wrapper">
          <div class="file-meta">
            <span class="meta-item">Size: {{ formatFileSize(fileSize) }}</span>
            <span class="meta-item">Encoding: {{ encoding }}</span>
            <button class="btn-copy" @click="copyToClipboard" title="Copy to clipboard">
              📋 Copy
            </button>
          </div>

          <pre class="file-content"><code>{{ fileContent }}</code></pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import apiClient from '@/services/api'
import { useToastStore } from '@/stores/toast'

interface Props {
  show: boolean
  filePath: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const toastStore = useToastStore()
const isLoading = ref(false)
const error = ref<string | null>(null)
const fileContent = ref('')
const fileSize = ref(0)
const encoding = ref('utf-8')

const fileName = computed(() => {
  return props.filePath.split('/').pop() || props.filePath
})

watch(() => props.show, (newShow) => {
  if (newShow && props.filePath) {
    loadFile()
  }
})

async function loadFile() {
  isLoading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`/files`, {
      params: { path: props.filePath }
    })

    fileContent.value = response.data.content
    fileSize.value = response.data.size
    encoding.value = response.data.encoding
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Failed to load file'
    toastStore.error(error.value)
  } finally {
    isLoading.value = false
  }
}

function handleClose() {
  emit('close')
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(fileContent.value)
    toastStore.success('File content copied to clipboard!')
  } catch (err) {
    toastStore.error('Failed to copy to clipboard')
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.file-info {
  flex: 1;
}

.file-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
}

.file-path {
  font-size: 0.875rem;
  color: #6b7280;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #9ca3af;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.close-button:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #6b7280;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-message {
  color: #ef4444;
  margin-bottom: 1rem;
}

.btn-retry {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-retry:hover {
  background: #2563eb;
}

.file-content-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.file-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.meta-item {
  font-size: 0.875rem;
  color: #6b7280;
}

.btn-copy {
  margin-left: auto;
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.375rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.btn-copy:hover {
  background: #2563eb;
}

.file-content {
  flex: 1;
  overflow: auto;
  margin: 0;
  padding: 1.5rem;
  background: #1f2937;
  color: #f9fafb;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
}

.file-content code {
  font-family: inherit;
}
</style>

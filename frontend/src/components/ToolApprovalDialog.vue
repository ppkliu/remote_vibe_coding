<template>
  <div v-if="show" class="modal-overlay" @click="handleReject">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">Tool Approval Required</h3>
        <button class="close-button" @click="handleReject">&times;</button>
      </div>

      <div class="modal-body">
        <div class="approval-icon">⚠️</div>
        <p class="approval-prompt">{{ prompt }}</p>

        <div class="tool-details">
          <div class="detail-item">
            <span class="detail-label">Action:</span>
            <span class="detail-value">{{ action }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Tool:</span>
            <span class="detail-value code">{{ toolName }}</span>
          </div>
        </div>

        <div class="warning-message">
          <strong>⚠️ Security Note:</strong>
          <p>This operation will execute code or access files on your system. Only approve if you trust the action.</p>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-reject" @click="handleReject">
          ✗ Reject
        </button>
        <button class="btn-approve" @click="handleApprove">
          ✓ Approve
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface Props {
  show: boolean
  toolName: string
  action: string
  prompt: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  approve: []
  reject: []
}>()

function handleApprove() {
  emit('approve')
}

function handleReject() {
  emit('reject')
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
  max-width: 500px;
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
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
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
}

.close-button:hover {
  background: #f3f4f6;
  color: #111827;
}

.modal-body {
  padding: 1.5rem;
}

.approval-icon {
  font-size: 3rem;
  text-align: center;
  margin-bottom: 1rem;
}

.approval-prompt {
  font-size: 1rem;
  color: #374151;
  text-align: center;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.tool-details {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.detail-item:not(:last-child) {
  border-bottom: 1px solid #e5e7eb;
}

.detail-label {
  font-weight: 500;
  color: #6b7280;
}

.detail-value {
  color: #111827;
}

.detail-value.code {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  background: #fee2e2;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.warning-message {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 1rem;
  border-radius: 4px;
}

.warning-message strong {
  display: block;
  color: #92400e;
  margin-bottom: 0.5rem;
}

.warning-message p {
  color: #78350f;
  font-size: 0.875rem;
  margin: 0;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.btn-reject,
.btn-approve {
  flex: 1;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-reject {
  background: #f3f4f6;
  color: #374151;
}

.btn-reject:hover {
  background: #e5e7eb;
}

.btn-approve {
  background: #10b981;
  color: white;
}

.btn-approve:hover {
  background: #059669;
}
</style>

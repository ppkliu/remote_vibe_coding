<template>
  <div class="command-input-container">
    <form @submit.prevent="handleSubmit" class="flex gap-2">
      <input
        v-model="command"
        type="text"
        placeholder="Enter a command for Claude Code..."
        class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        :disabled="disabled"
        @keydown.enter="handleSubmit"
      />
      <button
        type="submit"
        :disabled="disabled || !command.trim()"
        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  disabled?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  submit: [command: string]
}>()

const command = ref('')

function handleSubmit() {
  if (command.value.trim()) {
    emit('submit', command.value)
    command.value = ''
  }
}
</script>

<style scoped>
.command-input-container {
  padding: 1rem;
  background: white;
  border-top: 1px solid #e5e7eb;
}
</style>

<template>
  <div v-if="visible" class="confirmation-overlay" @click="handleOverlayClick">
    <div class="confirmation-dialog" @click.stop>
      <div class="confirmation-header">
        <h3>{{ title }}</h3>
        <button class="close-button" @click="cancel">
          <span class="material-icons">close</span>
        </button>
      </div>
      <div class="confirmation-content">
        <p>{{ message }}</p>
      </div>
      <div class="confirmation-actions">
        <button class="action-button cancel-button" @click="cancel">
          {{ cancelText }}
        </button>
        <button class="action-button confirm-button" @click="confirm">
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    default: 'Are you sure you want to proceed?'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  closeOnOverlay: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['confirm', 'cancel', 'close'])

const confirm = () => {
  emit('confirm')
  emit('close')
}

const cancel = () => {
  emit('cancel')
  emit('close')
}

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    cancel()
  }
}
</script>

<style scoped>
</style>

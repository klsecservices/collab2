<template>
  <div class="notification-container">
    <TransitionGroup name="notification" tag="div">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="['notification', `notification-${notification.type}`]"
        @click="removeNotification(notification.id)"
      >
        <div class="notification-content">
          <div class="notification-icon">
            <span class="material-icons">{{ getIcon(notification.type) }}</span>
          </div>
          <div class="notification-text">
            <div class="notification-title">{{ notification.title }}</div>
            <div v-if="notification.message" class="notification-message">
              {{ notification.message }}
            </div>
          </div>
          <button class="notification-close" @click.stop="removeNotification(notification.id)">
            <span class="material-icons">close</span>
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const notifications = ref([])
let notificationId = 0

const getIcon = (type) => {
  const icons = {
    success: 'check_circle',
    error: 'error',
    warning: 'warning',
    info: 'info'
  }
  return icons[type] || 'info'
}

const addNotification = (notification) => {
  const id = ++notificationId
  const newNotification = {
    id,
    type: notification.type || 'info',
    title: notification.title,
    message: notification.message,
    duration: notification.duration || 5000
  }
  
  notifications.value.push(newNotification)
  
  // Auto-remove after specified time
  if (newNotification.duration > 0) {
    setTimeout(() => {
      removeNotification(id)
    }, newNotification.duration)
  }
  
  return id
}

const removeNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

// Global function for showing notifications
const showNotification = (options) => {
  if (typeof options === 'string') {
    options = { title: options }
  }
  return addNotification(options)
}

// Export functions for global use
window.showNotification = showNotification
window.removeNotification = removeNotification

onUnmounted(() => {
  // Clean up global functions on unmount
  delete window.showNotification
  delete window.removeNotification
})
</script>

<style scoped>
</style>

/**
 * Notification utilities
 */

/**
 * Show success notification
 * @param {string|object} options - Notification text or object with parameters
 * @param {string} [options.title] - Notification title
 * @param {string} [options.message] - Notification message
 * @param {number} [options.duration=5000] - Display duration in milliseconds (0 = don't hide automatically)
 * @returns {number} Notification ID
 */
export const showSuccess = (options) => {
  return showNotification({
    type: 'success',
    ...(typeof options === 'string' ? { title: options } : options)
  })
}

/**
 * Show error notification
 * @param {string|object} options - Notification text or object with parameters
 * @param {string} [options.title] - Notification title
 * @param {string} [options.message] - Notification message
 * @param {number} [options.duration=8000] - Display duration in milliseconds (0 = don't hide automatically)
 * @returns {number} Notification ID
 */
export const showError = (options) => {
  return showNotification({
    type: 'error',
    duration: 8000,
    ...(typeof options === 'string' ? { title: options } : options)
  })
}

/**
 * Show warning notification
 * @param {string|object} options - Notification text or object with parameters
 * @param {string} [options.title] - Notification title
 * @param {string} [options.message] - Notification message
 * @param {number} [options.duration=6000] - Display duration in milliseconds (0 = don't hide automatically)
 * @returns {number} Notification ID
 */
export const showWarning = (options) => {
  return showNotification({
    type: 'warning',
    duration: 6000,
    ...(typeof options === 'string' ? { title: options } : options)
  })
}

/**
 * Show info notification
 * @param {string|object} options - Notification text or object with parameters
 * @param {string} [options.title] - Notification title
 * @param {string} [options.message] - Notification message
 * @param {number} [options.duration=5000] - Display duration in milliseconds (0 = don't hide automatically)
 * @returns {number} Notification ID
 */
export const showInfo = (options) => {
  return showNotification({
    type: 'info',
    ...(typeof options === 'string' ? { title: options } : options)
  })
}

/**
 * Show notification
 * @param {string|object} options - Notification text or object with parameters
 * @param {string} [options.type='info'] - Notification type: 'success', 'error', 'warning', 'info'
 * @param {string} [options.title] - Notification title
 * @param {string} [options.message] - Notification message
 * @param {number} [options.duration=5000] - Display duration in milliseconds (0 = don't hide automatically)
 * @returns {number} Notification ID
 */
export const showNotification = (options) => {
  if (typeof window !== 'undefined' && window.showNotification) {
    return window.showNotification(options)
  }
  console.warn('Notification system not available')
  return -1
}

/**
 * Remove notification by ID
 * @param {number} id - Notification ID
 */
export const removeNotification = (id) => {
  if (typeof window !== 'undefined' && window.removeNotification) {
    window.removeNotification(id)
  }
}

/**
 * Show loading notification
 * @param {string} message - Loading message
 * @returns {number} Notification ID
 */
export const showLoading = (message = 'Loading...') => {
  return showInfo({
    title: message,
    duration: 0 // Don't hide automatically
  })
}

/**
 * Show loading completion notification
 * @param {number} loadingId - Loading notification ID
 * @param {string} message - Success completion message
 */
export const hideLoading = (loadingId, message = 'Done!') => {
  removeNotification(loadingId)
  showSuccess(message)
}

/**
 * Show loading error notification
 * @param {number} loadingId - Loading notification ID
 * @param {string} message - Error message
 */
export const showLoadingError = (loadingId, message = 'Loading error') => {
  removeNotification(loadingId)
  showError(message)
}

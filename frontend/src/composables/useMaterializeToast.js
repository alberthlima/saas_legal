/**
 * Composable para Toast personalizado para Materialize Template
 * Archivo: src/composables/useMaterializeToast.js
 */

import { useToast } from "vue-toastification"

export const useMaterializeToast = () => {
  const toast = useToast()

  /**
   * Toast de éxito
   * @param {string} message - Mensaje principal
   * @param {string|null} title - Título opcional
   * @param {object} options - Opciones adicionales
   */
  const showSuccess = (message, title = null, options = {}) => {
    let content = message
    
    if (title) {
      content = `${title}\n${message}`
    }
    
    toast.success(content, {
      timeout: 5000,
      closeOnClick: true,
      pauseOnFocusLoss: true,
      pauseOnHover: true,
      draggable: true,
      showCloseButtonOnHover: false,
      hideProgressBar: false,
      closeButton: "button",
      icon: true,
      rtl: false,
      ...options
    })
  }

  /**
   * Toast de error
   * @param {string} message - Mensaje principal
   * @param {string} title - Título (por defecto "Error")
   * @param {object} options - Opciones adicionales
   */
  const showError = (message, title = "Error", options = {}) => {
    const content = `${title}\n${message}`
    
    toast.error(content, {
      timeout: 8000, // Más tiempo para errores
      closeOnClick: true,
      pauseOnFocusLoss: true,
      pauseOnHover: true,
      draggable: true,
      showCloseButtonOnHover: false,
      hideProgressBar: false,
      closeButton: "button",
      icon: true,
      rtl: false,
      ...options
    })
  }

  /**
   * Toast de advertencia
   * @param {string} message - Mensaje principal
   * @param {string} title - Título (por defecto "Advertencia")
   * @param {object} options - Opciones adicionales
   */
  const showWarning = (message, title = "Advertencia", options = {}) => {
    const content = `${title}\n${message}`
    
    toast.warning(content, {
      timeout: 6000,
      closeOnClick: true,
      pauseOnFocusLoss: true,
      pauseOnHover: true,
      draggable: true,
      showCloseButtonOnHover: false,
      hideProgressBar: false,
      closeButton: "button",
      icon: true,
      rtl: false,
      ...options
    })
  }

  /**
   * Toast de información
   * @param {string} message - Mensaje principal
   * @param {string} title - Título (por defecto "Información")
   * @param {object} options - Opciones adicionales
   */
  const showInfo = (message, title = "Información", options = {}) => {
    const content = `${title}\n${message}`
    
    toast.info(content, {
      timeout: 4000,
      closeOnClick: true,
      pauseOnFocusLoss: true,
      pauseOnHover: true,
      draggable: true,
      showCloseButtonOnHover: false,
      hideProgressBar: false,
      closeButton: "button",
      icon: true,
      rtl: false,
      ...options
    })
  }

  /**
   * Mostrar toast desde respuesta de Laravel
   * @param {object} response - Respuesta de Axios/Laravel
   */
  const showFromLaravel = (response) => {
    if (response.data?.toast) {
      const { type, message, title, options = {} } = response.data.toast
      
      switch(type?.toLowerCase()) {
        case 'success':
          showSuccess(message, title, options)
          break
        case 'error':
          showError(message, title, options)
          break
        case 'warning':
          showWarning(message, title, options)
          break
        case 'info':
          showInfo(message, title, options)
          break
        default:
          showInfo(message, title || 'Notificación', options)
      }
    }
  }

  /**
   * Mostrar toast personalizado con HTML
   * @param {string} html - Contenido HTML
   * @param {string} type - Tipo de toast (success, error, warning, info)
   * @param {object} options - Opciones adicionales
   */
  const showCustomHTML = (html, type = 'info', options = {}) => {
    const toastMethod = toast[type] || toast.info
    toastMethod(html, {
      timeout: 5000,
      closeOnClick: true,
      pauseOnFocusLoss: true,
      pauseOnHover: true,
      draggable: true,
      showCloseButtonOnHover: false,
      hideProgressBar: false,
      closeButton: "button",
      icon: false, // Deshabilitamos el ícono para HTML personalizado
      rtl: false,
      ...options
    })
  }

  /**
   * Limpiar todos los toasts
   */
  const clear = () => {
    toast.clear()
  }

  /**
   * Cerrar un toast específico
   * @param {number} id - ID del toast
   */
  const dismiss = (id) => {
    toast.dismiss(id)
  }

  /**
   * Toast de confirmación con botones
   * @param {string} message - Mensaje
   * @param {function} onConfirm - Callback al confirmar
   * @param {function} onCancel - Callback al cancelar
   */
  const showConfirmation = (message, onConfirm, onCancel = null) => {
    const html = `
      <div style="padding: 10px 0;">
        <div class="toast-message">${message}</div>
        <div style="margin-top: 15px; text-align: right;">
          <button class="btn-flat toast-cancel" style="margin-right: 10px; color: rgba(255,255,255,0.8);">
            Cancelar
          </button>
          <button class="btn-flat toast-confirm" style="color: white; font-weight: bold;">
            Confirmar
          </button>
        </div>
      </div>
    `
    
    const toastId = toast.info(html, {
      timeout: 0, // No auto-close
      closeOnClick: false,
      closeButton: false,
      icon: false,
      onMounted: (component, toastObject) => {
        // Agregar event listeners a los botones
        const confirmBtn = component.el.querySelector('.toast-confirm')
        const cancelBtn = component.el.querySelector('.toast-cancel')
        
        if (confirmBtn) {
          confirmBtn.addEventListener('click', () => {
            if (onConfirm) onConfirm()
            toast.dismiss(toastObject.id)
          })
        }
        
        if (cancelBtn) {
          cancelBtn.addEventListener('click', () => {
            if (onCancel) onCancel()
            toast.dismiss(toastObject.id)
          })
        }
      }
    })
    
    return toastId
  }

  return {
    // Métodos principales
    showSuccess,
    showError,
    showWarning,
    showInfo,
    
    // Métodos especiales
    showFromLaravel,
    showCustomHTML,
    showConfirmation,
    
    // Utilidades
    clear,
    dismiss,
    
    // Toast original por si necesitas funcionalidad avanzada
    toast
  }
}
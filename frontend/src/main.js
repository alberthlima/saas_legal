import { createApp } from 'vue'
import App from '@/App.vue'
import { registerPlugins } from '@core/utils/plugins'

// Styles
import '@core/scss/template/index.scss'
import '@styles/styles.scss'
// NUEVAS IMPORTACIONES PARA TOAST
import Toast from "vue-toastification"
import "vue-toastification/dist/index.css"
import './assets/css/toast-custom.css' // Nuestro CSS personalizado

// Create vue app
const app = createApp(App)

// CONFIGURACIÓN DEL TOAST
app.use(Toast, {
  // Posición en la esquina superior derecha
  position: "top-right",
  
  // Configuración de timeouts por defecto
  timeout: 5000,
  
  // Comportamientos generales
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: "button",
  icon: true,
  rtl: false,
  
  // Permitir contenido HTML
  dangerouslyHTMLString: true,
  
  // Máximo número de toasts visibles
  maxToasts: 5,
  newestOnTop: true,
  
  // Transiciones (puedes cambiar a "Vue__Toastification__slide" si prefieres)
  transition: "Vue__Toastification__bounce",
  
  // Configuraciones específicas por tipo
  toastDefaults: {
    // Toast de éxito
    success: {
      timeout: 5000,
      icon: true,
    },
    // Toast de error (más tiempo visible)
    error: {
      timeout: 8000,
      icon: true,
    },
    // Toast de advertencia
    warning: {
      timeout: 6000,
      icon: true,
    },
    // Toast de información
    info: {
      timeout: 4000,
      icon: true,
    },
  },
  
  // Clases CSS personalizadas (opcional)
  containerClassName: "custom-toast-container",
  toastClassName: "custom-toast",
  bodyClassName: ["custom-toast-body"],
  progressClassName: "custom-toast-progress",
  
  // Callback cuando se monta un toast (opcional)
  onMounted: (component, toastObject) => {
    // console.log('Toast montado:', toastObject)
  },
  
  // Callback cuando se cierra un toast (opcional)
  onClose: (component, toastObject) => {
    // console.log('Toast cerrado:', toastObject)
  }
})

// Register plugins
registerPlugins(app)

// Mount vue app
app.mount('#app')

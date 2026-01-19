// Validadores personalizados en español para reutilizar en toda la aplicación

export const requiredValidator = value => {
  if (!value || value.length === 0)
    return 'Este campo es obligatorio'
  return true
}

export const emailValidator = value => {
  if (!value)
    return 'Este campo es obligatorio'
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value))
    return 'Por favor ingresa un correo electrónico válido'
  
  return true
}

export const passwordValidator = value => {
  if (!value)
    return 'Este campo es obligatorio'
  
  if (value.length < 6)
    return 'La contraseña debe tener al menos 6 caracteres'
  
  return true
}

export const selectValidator = value => {
  if (!value || value === null || value === undefined)
    return 'Por favor selecciona una opción'
  return true
}

// Validadores para archivos
export const imageValidator = files => {
  if (!files || files.length === 0)
    return 'Este campo es obligatorio'
  
  // Tomar el primer archivo del array
  const file = files[0]
  
  // Tipos de imagen permitidos
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  
  if (!allowedTypes.includes(file.type)) {
    return 'Solo se permiten archivos de imagen (JPG, PNG, GIF, WebP)'
  }
  
  // Validar tamaño (máximo 5MB)
  const maxSize = 5 * 1024 * 1024 // 5MB en bytes
  if (file.size > maxSize) {
    return 'La imagen no debe superar los 5MB'
  }
  
  return true
}

export const pdfValidator = file => {
  if (!file || file.length === 0)
    return 'Este campo es obligatorio'
  
  // Validar que sea PDF
  if (file.type !== 'application/pdf') {
    return 'Solo se permiten archivos PDF'
  }
  
  // Validar tamaño (máximo 10MB)
  const maxSize = 10 * 1024 * 1024 // 10MB en bytes
  if (file.size > maxSize) {
    return 'El PDF no debe superar los 10MB'
  }
  
  return true
}

export const optionalImageValidator = files => {
  if (!files || files.length === 0)
    return true // No es obligatorio
  
  // Tomar el primer archivo del array
  const file = files[0]
  
  // Si hay archivo, validar que sea imagen
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  
  if (!allowedTypes.includes(file.type)) {
    return 'Solo se permiten archivos de imagen (JPG, PNG, GIF, WebP)'
  }
  
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    return 'La imagen no debe superar los 5MB'
  }
  
  return true
}

// Validador opcional para PDF (no requerido)
export const optionalPdfValidator = file => {
  if (!file || file.length === 0)
    return true // No es obligatorio
  
  // Si hay archivo, validar que sea PDF
  if (file.type !== 'application/pdf') {
    return 'Solo se permiten archivos PDF'
  }
  
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    return 'El PDF no debe superar los 10MB'
  }
  
  return true
}
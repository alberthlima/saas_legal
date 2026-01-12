export default [
  {
    title: 'Escritorio',
    to: { name: 'dashboard' },
    icon: { icon: 'ri-pie-chart-box-line' },
  },
  { heading: 'Gestión Documental' },
  {
    title: 'Gestión de Documentos',
    icon: { icon: 'ri-file-pdf-2-fill' },
    children: [
      {
        title: 'Categorías',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Biblioteca',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
    ],
  },
  { heading: 'Suscripciones y Clientes' },
  {
    title: 'Planes',
    to: { name: 'second-page' },
    icon: { icon: 'ri-list-check-3' },
  },
  {
    title: 'Clientes',
    to: { name: 'second-page' },
    icon: { icon: 'ri-group-fill' },
  },
  {
    title: 'Suscripciones',
    to: { name: 'second-page' },
    icon: { icon: 'ri-cash-fill' },
  },
  { heading: 'Reportes' },
  {
    title: 'Reporte por cliente',
    icon: { icon: 'ri-folder-chart-line' },
    to: 'second-page',
  },
  {
    title: 'Reporte por planes',
    to: { name: 'second-page' },
    icon: { icon: 'ri-draft-line' },
  },
  { heading: 'Accesos' },
  {
    title: 'Roles y Permisos',
    to: { name: 'roles-permisos' },
    icon: { icon: 'ri-lock-password-line' },
  },
  {
    title: 'Usuarios',
    to: { name: 'second-page' },
    icon: { icon: 'ri-user-settings-line' },
  },
]

export default [
  {
    title: 'Escritorio',
    to: { name: 'dashboard' },
    permission: "all",
    icon: { icon: 'ri-pie-chart-box-line' },
  },
  { heading: 'Gestión Documental', permissions: ['listar_categoria', 'listar_documento'] },
  {
    title: 'Gestión de Documentos',
    icon: { icon: 'ri-file-pdf-2-fill' },
    children: [
      {
        title: 'Categorías',
        to: 'second-page',
        permission: 'listar_categoria',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Tipos de Documentos',
        to: 'second-page',
        permission: 'listar_tipo_documento',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Biblioteca',
        to: 'second-page',
        permission: 'listar_documento',
        icon: { icon: 'ri-radio-button-line' },
      },
    ],
  },
  { heading: 'Suscripciones y Clientes', permissions: ['listar_plan', 'listar_cliente', 'suscripciones'] },
  {
    title: 'Planes',
    to: { name: 'second-page' },
    permission: 'listar_plan',
    icon: { icon: 'ri-list-check-3' },
  },
  {
    title: 'Clientes',
    to: { name: 'second-page' },
    permission: 'listar_cliente',
    icon: { icon: 'ri-group-fill' },
  },
  {
    title: 'Suscripciones',
    to: { name: 'second-page' },
    permission: 'suscripciones',
    icon: { icon: 'ri-cash-fill' },
  },
  { heading: 'Reportes', permissions: ['reportes'] },
  {
    title: 'Reporte por cliente',
    to: 'second-page',
    permission: 'reportes',
    icon: { icon: 'ri-folder-chart-line' },
  },
  {
    title: 'Reporte por planes',
    to: { name: 'second-page' },
    permission: 'reportes',
    icon: { icon: 'ri-draft-line' },
  },
  { heading: 'Accesos', permissions: ['listar_rol', 'listar_usuario'] },
  {
    title: 'Roles y Permisos',
    to: { name: 'roles-permisos' },
    permission: 'listar_rol',
    icon: { icon: 'ri-lock-password-line' },
  },
  {
    title: 'Usuarios',
    to: { name: 'usuarios' },
    permission: 'listar_usuario',
    icon: { icon: 'ri-user-settings-line' },
  },
]

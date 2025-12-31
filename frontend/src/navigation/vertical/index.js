export default [
  {
    title: 'Escritorio',
    to: { name: 'dashboard' },
    icon: { icon: 'ri-pie-chart-box-line' },
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
    icon: { icon: 'ri-group-line' },
  },
  {
    title: 'Configuraciones',
    icon: { icon: 'ri-tools-line' },
    children: [
      {
        title: 'Actividades Económicas',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Unidades de Medida',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Servicios',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Productos',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Clientes',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Configuracion General',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
    ],
  },
  { heading: 'Contratos y ABMs' },
  {
    title: 'Gestión de Contratos',
    icon: { icon: 'ri-product-hunt-line' },
    children: [
      {
        title: 'Registrar',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Listado',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
    ],
  },
  {
    title: 'Gestión de ABMs',
    icon: { icon: 'ri-money-dollar-box-line' },
    children: [
      {
        title: 'Vegentes',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Adendas',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
      {
        title: 'Expirados',
        to: 'second-page',
        icon: { icon: 'ri-radio-button-line' },
      },
    ],
  },
  { heading: 'Facturación SIN' },
  {
    title: 'Emisión de Facturas',
    icon: { icon: 'ri-box-3-line' },
    children: [
      {
        title: 'Registrar',
        to: 'second-page',
        icon: { icon: 'ri-computer-line' },
      },
      {
        title: 'Listado',
        to: 'second-page',
        icon: { icon: 'ri-bar-chart-line' },
      },
    ],
  },
  {
    title: 'Anulación de Facturas',
    icon: { icon: 'ri-translate' },
    children: [
      {
        title: 'Registrar',
        to: 'second-page',
        icon: { icon: 'ri-computer-line' },
      },
      {
        title: 'Listado',
        to: 'second-page',
        icon: { icon: 'ri-bar-chart-line' },
      },
    ],
  },
  { heading: 'Reportes' },
  {
    title: 'Reporte por cliente',
    icon: { icon: 'ri-file-ppt-2-line' },
    to: 'second-page',
  },
  {
    title: 'Reporte de Facturación',
    to: { name: 'second-page' },
    icon: { icon: 'ri-draft-line' },
  },
]

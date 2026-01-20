import { canNavigate } from '@layouts/plugins/casl'

export const setupGuards = router => {
  // 👉 router.beforeEach
  // Docs: https://router.vuejs.org/guide/advanced/navigation-guards.html#global-before-guards
  router.beforeEach(to => {
    /*
         * If it's a public route, continue navigation. This kind of pages are allowed to visited by login & non-login users. Basically, without any restrictions.
         * Examples of public routes are, 404, under maintenance, etc.
         */
    if (to.meta.public)
      return

    /**
         * Check if user is logged in by checking if token & user data exists in local storage
         * Feel free to update this logic to suit your needs
         */
    const isLoggedIn = localStorage.getItem("token") && localStorage.getItem("user"); //!!(useCookie('userData').value && useCookie('accessToken').value)

    /*
          If user is logged in and is trying to access login like page, redirect to home
          else allow visiting the page
          (WARN: Don't allow executing further by return statement because next code will check for permissions)
         */
    if (to.meta.unauthenticatedOnly) {
      if (isLoggedIn)
        return '/'
      else
        return undefined
    }

    let USER = localStorage.getItem("user") ? JSON.parse(localStorage.getItem("user")) : null;
    if (USER && USER.role.name != 'Super-Admin') {
      //lista de permisos del usuario autenticado
      let permissions = USER.permissions;
      if (permissions.includes(to.meta.permission) || to.meta.permission == 'all') {
        return true;
      } else {
        return {
          name: 'not-authorized'
        };
      }
    }

    if (!isLoggedIn && to.matched.length) {
      /* eslint-disable indent */
      return isLoggedIn
        ? { name: 'not-authorized' }
        : {
          name: 'login',
          query: {
            ...to.query,
            to: to.fullPath !== '/' ? to.path : undefined,
          },
        }
      /* eslint-enable indent */
    }
  })
}

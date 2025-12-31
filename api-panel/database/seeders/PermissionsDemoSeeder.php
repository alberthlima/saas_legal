<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;
use Spatie\Permission\PermissionRegistrar;

class PermissionsDemoSeeder extends Seeder
{
    /**
     * Create the initial roles and permissions.
     *
     * @return void
     */
    public function run()
    {
        // Reset cached roles and permissions
        app()[PermissionRegistrar::class]->forgetCachedPermissions();

        Permission::create(['guard_name' => 'api','name' => 'Escritorio']);
        // create permissions
        Permission::create(['guard_name' => 'api','name' => 'registrar_rol']);
        Permission::create(['guard_name' => 'api','name' => 'listar_rol']);
        Permission::create(['guard_name' => 'api','name' => 'editar_rol']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_rol']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_usuario']);
        Permission::create(['guard_name' => 'api','name' => 'listar_usuario']);
        Permission::create(['guard_name' => 'api','name' => 'editar_usuario']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_usuario']);
        
        Permission::create(['guard_name' => 'api','name' => 'listar_actividad_economica']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_unidad']);
        Permission::create(['guard_name' => 'api','name' => 'listar_unidad']);
        Permission::create(['guard_name' => 'api','name' => 'editar_unidad']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_unidad']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_servicio']);
        Permission::create(['guard_name' => 'api','name' => 'listar_servicio']);
        Permission::create(['guard_name' => 'api','name' => 'editar_servicio']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_servicio']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_producto']);
        Permission::create(['guard_name' => 'api','name' => 'listar_producto']);
        Permission::create(['guard_name' => 'api','name' => 'editar_producto']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_producto']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_cliente']);
        Permission::create(['guard_name' => 'api','name' => 'listar_cliente']);
        Permission::create(['guard_name' => 'api','name' => 'editar_cliente']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_cliente']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_configuracion']);
        Permission::create(['guard_name' => 'api','name' => 'listar_configuracion']);
        Permission::create(['guard_name' => 'api','name' => 'editar_configuracion']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_configuracion']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_contrato']);
        Permission::create(['guard_name' => 'api','name' => 'listar_contrato']);
        Permission::create(['guard_name' => 'api','name' => 'editar_contrato']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_contrato']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_abm']);
        Permission::create(['guard_name' => 'api','name' => 'listar_abm']);
        Permission::create(['guard_name' => 'api','name' => 'editar_abm']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_abm']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_factura']);
        Permission::create(['guard_name' => 'api','name' => 'listar_factura']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_factura']);

        Permission::create(['guard_name' => 'api','name' => 'reportes']);
        
        // create roles and assign existing permissions

        $role3 = Role::create(['guard_name' => 'api','name' => 'Super-Admin']);
        // gets all permissions via Gate::before rule; see AuthServiceProvider

        $user = \App\Models\User::factory()->create([
            'name' => 'Super-Admin User',
            'email' => 'mlima@gmail.com',
            'password' => bcrypt('12345678')
        ]);
        $user->assignRole($role3);
    }
}
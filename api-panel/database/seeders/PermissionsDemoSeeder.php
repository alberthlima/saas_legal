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

        Permission::create(['guard_name' => 'api','name' => 'escritorio']);
        // create permissions
        Permission::create(['guard_name' => 'api','name' => 'registrar_categoria']);
        Permission::create(['guard_name' => 'api','name' => 'listar_categoria']);
        Permission::create(['guard_name' => 'api','name' => 'editar_categoria']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_categoria']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_tipo_documento']);
        Permission::create(['guard_name' => 'api','name' => 'listar_tipo_documento']);
        Permission::create(['guard_name' => 'api','name' => 'editar_tipo_documento']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_tipo_documento']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_documento']);
        Permission::create(['guard_name' => 'api','name' => 'listar_documento']);
        Permission::create(['guard_name' => 'api','name' => 'editar_documento']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_documento']);
        
        Permission::create(['guard_name' => 'api','name' => 'registrar_membresia']);
        Permission::create(['guard_name' => 'api','name' => 'listar_membresia']);
        Permission::create(['guard_name' => 'api','name' => 'editar_membresia']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_membresia']);

        Permission::create(['guard_name' => 'api','name' => 'clientes']);

        Permission::create(['guard_name' => 'api','name' => 'suscripciones']);

        Permission::create(['guard_name' => 'api','name' => 'config']);

        Permission::create(['guard_name' => 'api','name' => 'reportes']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_rol']);
        Permission::create(['guard_name' => 'api','name' => 'listar_rol']);
        Permission::create(['guard_name' => 'api','name' => 'editar_rol']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_rol']);

        Permission::create(['guard_name' => 'api','name' => 'registrar_usuario']);
        Permission::create(['guard_name' => 'api','name' => 'listar_usuario']);
        Permission::create(['guard_name' => 'api','name' => 'editar_usuario']);
        Permission::create(['guard_name' => 'api','name' => 'eliminar_usuario']);
        
        // create roles and assign existing permissions

        $role = Role::create(['guard_name' => 'api','name' => 'Super-Admin']);
        // gets all permissions via Gate::before rule; see AuthServiceProvider

        $user = \App\Models\User::factory()->create([
            'name' => 'Super-Admin',
            'surname' => 'User',
            'email' => 'mlima@gmail.com',
            'password' => bcrypt('12345678'),
            'role_id' => $role->id,
        ]);
        $user->assignRole($role);
    }
}
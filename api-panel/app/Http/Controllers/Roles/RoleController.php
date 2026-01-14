<?php

namespace App\Http\Controllers\Roles;

use App\Http\Controllers\Controller;
use Spatie\Permission\Models\Role;
use Illuminate\Http\Request;

class RoleController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $search = $request->get("search");
        $roles = Role::where("name", "LIKE", "%" . $search . "%")->orderBy("id", "desc")->get();
        return response()->json([
            "roles" => $roles->map(function ($role) {
                return [
                    "id" => $role->id,
                    "name" => $role->name,
                    "created_at" => $role->created_at->format("Y/m/d H:i:s"),
                    "permissions" => $role->permissions->map(function ($permission) {
                        return [
                            "id" => $permission->id,
                            "name" => $permission->name,
                        ];
                    }),
                    "permissions_pluck" => $role->permissions->pluck("name"),
                ];
            }),
        ], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $exist_role = Role::where("name", $request->name)->first();
        
        if ($exist_role) {
            return response()->json([
                "message" => "El rol ya existe",
            ], 403);
        }

        $role = Role::create([
            "name" => $request->name,
            "guard_name" => "api",
        ]);

        $permisos = $request->permissions;
        $role->syncPermissions($permisos);
        
        return response()->json([
            "message" => "Rol creado correctamente",
            "role" => $role,
        ], 200);
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        $exist_role = Role::where("name", $request->name)->where("id", "<>", $id)->first();
        if ($exist_role) {
            return response()->json([
                "message" => "El rol ya existe",
            ], 403);
        }

        $role = Role::findOrFail($id);

        $role->update([
            "name" => $request->name,
        ]);

        $permisos = $request->permissions;
        $role->syncPermissions($permisos);

        return response()->json([
            "message" => "Rol actualizado correctamente",
            "role" => $role,
        ], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        $role = Role::findOrFail($id);
        $role->delete();

        return response()->json([
            "message" => "Rol eliminado correctamente",
        ], 200);
    }
}

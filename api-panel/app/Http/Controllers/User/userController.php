<?php

namespace App\Http\Controllers\User;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use App\Models\User;
use Spatie\Permission\Models\Role;
use Illuminate\Support\Facades\DB;

class userController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $search = $request->get("search");
        $users = User::where(DB::raw("CONCAT(name, ' ', surname, ' ', email)"), "LIKE", "%" . $search . "%")->orderBy("id", "desc")->get();
        return response()->json([
            "users" => $users->map(function ($user) {
                return [
                    "id" => $user->id,
                    "name" => $user->name,
                    "surname" => $user->surname,
                    "full_name" => $user->name . " " . $user->surname,
                    "email" => $user->email,
                    "avatar" => $user->avatar ? env("APP_URL") . "/storage/" . $user->avatar : NULL,
                    "created_at" => $user->created_at->format("Y/m/d H:i:s"),
                    "state" => $user->state,
                    "role_id" => $user->role_id,
                    "role" => [
                        "name" => $user->role->name,
                    ],
                ];
            }),
        ], 200);
    }

    public function getRoles()
    {
        $roles = Role::all();
        return response()->json([
            "roles" => $roles->map(function ($role) {
                return [
                    "id" => $role->id,
                    "name" => $role->name,
                ];
            }),
        ], 200);
    }

    /**
     */
    public function store(Request $request)
    {
        $is_user_exists = User::where("email", $request->email)->first();
        if ($is_user_exists) {
            return response()->json([
                "message" => "El usuario ya existe",
            ], 403);
        }

        $data = $request->all();

        if($request->hasFile("imagen")){
            $path = Storage::disk('public')->putFile("users", $request->file("imagen"));
            $data["avatar"] = $path;
        }

        if($request->password){
            $data["password"] = bcrypt($request->password);
        }

        $user = User::create($data);

        $rol = Role::findOrFail($request->role_id);
        $user->assignRole($rol);

        return response()->json([
            "message" => "Usuario creado exitosamente",
            "user" => [
                    "id" => $user->id,
                    "name" => $user->name,
                    "surname" => $user->surname,
                    "full_name" => $user->name . " " . $user->surname,
                    "email" => $user->email,
                    "avatar" => $user->avatar ? env("APP_URL") . "/storage/" . $user->avatar : NULL,
                    "created_at" => $user->created_at->format("Y/m/d H:i:s"),
                    "state" => $user->state,
                    "role_id" => $user->role_id,
                    "role" => [
                        "name" => $user->role->name,
                    ],
                ],
        ], 200);
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {

    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        $is_user_exists = User::where("email", $request->email)->where("id", "<>", $id)->first();
        if ($is_user_exists) {
            return response()->json([
                "message" => "El usuario ya existe",
            ], 403);
        }

        $user = User::findOrFail($id);
        $data = $request->all();

        if($request->hasFile("imagen")){
            if($user->avatar){
                Storage::disk('public')->delete($user->avatar);
            }
            $path = Storage::disk('public')->putFile("users", $request->file("imagen"));
            $data["avatar"] = $path;
        }

        if($request->password){
            $data["password"] = bcrypt($request->password);
        }

        $user->update($data);

        if($request->role_id != $user->role_id){
            $rol_old = Role::findOrFail($user->role_id);
            $user->removeRole($rol_old);

            $rol_new = Role::findOrFail($request->role_id);
            $user->assignRole($rol_new);
        }

        return response()->json([
            "message" => "Usuario actualizado exitosamente",
            "user" => [
                    "id" => $user->id,
                    "name" => $user->name,
                    "surname" => $user->surname,
                    "full_name" => $user->name . " " . $user->surname,
                    "email" => $user->email,
                    "avatar" => $user->avatar ? env("APP_URL") . "/storage/" . $user->avatar : NULL,
                    "created_at" => $user->created_at->format("Y/m/d H:i:s"),
                    "state" => $user->state,
                    "role_id" => $user->role_id,
                    "role" => [
                        "name" => $user->role->name,
                    ],
                ],
        ], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        $user = User::findOrFail($id);
        $user->delete();

        return response()->json([
            "message" => "Usuario eliminado exitosamente",
        ], 200);
    }
}

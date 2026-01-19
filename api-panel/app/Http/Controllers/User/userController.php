<?php

namespace App\Http\Controllers\User;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;

class userController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $search = $request->get("search");
        $users = User::where("name", "LIKE", "%" . $search . "%")->orderBy("id", "desc")->get();
        return response()->json([
            "users" => $users->map(function ($user) {
                return [
                    "id" => $user->id,
                    "full_name" => $user->name . " " . $user->surname,
                    "email" => $user->email,
                    "avatar" => $user->avatar,
                    "created_at" => $user->created_at->format("Y/m/d H:i:s"),
                    "role_id" => $user->role_id,
                    "role" => [
                        "name" => $user->role->name,
                    ],
                ];
            }),
        ], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        
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
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}

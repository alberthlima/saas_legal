<?php

namespace App\Http\Controllers\Membership;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Membership;

class membershipController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $search = $request->search;
        $memberships = Membership::where('name', 'like', "%$search%")->get();
        return response()->json([
            'memberships' => $memberships->map(function ($membership) {
                return [
                    'id' => $membership->id,
                    'name' => $membership->name,
                    'description' => $membership->description,
                    'price' => $membership->price,
                    'daily_limit' => $membership->daily_limit,
                    'max_specialists' => $membership->max_specialists,
                    'state' => $membership->state,
                    'created_at' => $membership->created_at->format('Y/m/d H:i:s'),
                ];
            }),
        ], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $is_membership_exists = Membership::where('name', $request->name)->first();
        if ($is_membership_exists) {
            return response()->json([
                'message' => 'La membresía ya existe',
            ], 403);
        }

        $membership = Membership::create($request->all());
        return response()->json([
            'message' => 'Membresía creada exitosamente',
            'membership' => [
                'id' => $membership->id,
                'name' => $membership->name,
                'description' => $membership->description,
                'price' => $membership->price,
                'daily_limit' => $membership->daily_limit,
                'max_specialists' => $membership->max_specialists,
                'state' => $membership->state,
                'created_at' => $membership->created_at->format('Y/m/d H:i:s'),
            ],
        ], 200);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Membership $membership)
    {
        $is_membership_exists = Membership::where('name', $request->name)->where('id', '!=', $membership->id)->first();
        if ($is_membership_exists) {
            return response()->json([
                'message' => 'La membresía ya existe',
            ], 403);
        }

        $membership->update($request->all());
        return response()->json([
            'message' => 'Membresía actualizada exitosamente',
            'membership' => [
                'id' => $membership->id,
                'name' => $membership->name,
                'description' => $membership->description,
                'price' => $membership->price,
                'daily_limit' => $membership->daily_limit,
                'max_specialists' => $membership->max_specialists,
                'state' => $membership->state,
                'created_at' => $membership->created_at->format('Y/m/d H:i:s'),
            ],
        ], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Membership $membership)
    {
        $membership->delete();
        return response()->json([
            'message' => 'Membresía eliminada exitosamente',
        ], 200);
    }
}

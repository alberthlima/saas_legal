<?php

namespace App\Http\Controllers\TypeDocument;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\TypeDocument;

class typeDocumentController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $search = $request->search;
        $types = TypeDocument::where('name', 'like', "%$search%")->get();
        return response()->json([
            'types' => $types->map(function ($type) {
                return [
                    'id' => $type->id,
                    'name' => $type->name,
                    'state' => $type->state,
                    'created_at' => $type->created_at->format('Y/m/d H:i:s'),
                ];
            }),
        ], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $is_type_exists = TypeDocument::where('name', $request->name)->first();
        if ($is_type_exists) {
            return response()->json([
                'message' => 'El tipo de documento ya existe',
            ], 403);
        }

        $type = TypeDocument::create($request->all());
        return response()->json([
            'message' => 'Tipo de documento creado exitosamente',
            'type' => [
                'id' => $type->id,
                'name' => $type->name,
                'state' => $type->state,
                'created_at' => $type->created_at->format('Y/m/d H:i:s'),
            ],
        ], 200);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, TypeDocument $type)
    {
        $is_type_exists = TypeDocument::where('name', $request->name)->where('id', '!=', $type->id)->first();
        if ($is_type_exists) {
            return response()->json([
                'message' => 'El tipo de documento ya existe',
            ], 403);
        }

        $type->update($request->all());
        return response()->json([
            'message' => 'Tipo de documento actualizado exitosamente',
            'type' => [
                'id' => $type->id,
                'name' => $type->name,
                'state' => $type->state,
                'created_at' => $type->created_at->format('Y/m/d H:i:s'),
            ],
        ], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(TypeDocument $type)
    {
        $type->delete();
        return response()->json([
            'message' => 'Tipo de documento eliminado exitosamente',
        ], 200);
    }
}

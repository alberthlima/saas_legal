<?php

namespace App\Http\Controllers\Category;

use App\Http\Controllers\Controller;
use App\Models\Category;
use Illuminate\Http\Request;

class categoryController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $search = $request->search;
        $categories = Category::where('name', 'like', "%$search%")->get();
        return response()->json([
            'categories' => $categories->map(function ($category) {
                return [
                    'id' => $category->id,
                    'name' => $category->name,
                    'description' => $category->description,
                    'state' => $category->state,
                    'created_at' => $category->created_at->format('Y/m/d H:i:s'),
                ];
            }),
        ], 200);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $is_category_exists = Category::where('name', $request->name)->first();
        if ($is_category_exists) {
            return response()->json([
                'message' => 'La categoría ya existe',
            ], 403);
        }

        $category = Category::create($request->all());
        return response()->json([
            'message' => 'Categoría creada exitosamente',
            'category' => [
                'id' => $category->id,
                'name' => $category->name,
                'description' => $category->description,
                'state' => $category->state,
                'created_at' => $category->created_at->format('Y/m/d H:i:s'),
            ],
        ], 200);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, Category $category)
    {
        $is_category_exists = Category::where('name', $request->name)->where('id', '!=', $category->id)->first();
        if ($is_category_exists) {
            return response()->json([
                'message' => 'La categoría ya existe',
            ], 403);
        }

        $category->update($request->all());
        return response()->json([
            'message' => 'Categoría actualizada exitosamente',
            'category' => [
                'id' => $category->id,
                'name' => $category->name,
                'description' => $category->description,
                'state' => $category->state,
                'created_at' => $category->created_at->format('Y/m/d H:i:s'),
            ],
        ], 200);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(Category $category)
    {
        $category->delete();
        return response()->json([
            'message' => 'Categoría eliminada exitosamente',
        ], 200);
    }
}

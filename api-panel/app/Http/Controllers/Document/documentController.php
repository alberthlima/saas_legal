<?php

namespace App\Http\Controllers\Document;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;

use App\Models\Document;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Http;

class documentController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $search = $request->search;
        $documents = Document::where('name', 'LIKE', "%{$search}%")->with('typeDocument')->latest()->get();
        return response()->json([
            'success' => true,
            'documents' => $documents
        ]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $validator = Validator::make(array_merge($request->all(), $request->allFiles()), [
            'name' => 'required|string|max:255',
            'description' => 'nullable|string',
            'type_document_id' => 'required|exists:type_documents,id',
            'category_ids' => 'required|array',
            'category_ids.*' => 'exists:categories,id',
            'file' => 'required|file|mimes:pdf|max:10240', // Máximo 10MB
        ]);

        if ($validator->fails()) {
            return response()->json(['success' => false, 'errors' => $validator->errors()], 422);
        }

        try {
            // Guardar archivo en el disco 'public' para que sea accesible
            $path = $request->file('file')->store('documents', 'public');
            $url = Storage::disk('public')->url($path);

            $document = Document::create([
                'name' => $request->name,
                'description' => $request->description,
                'path' => $url,
                'type_document_id' => $request->type_document_id,
                'category_ids' => $request->category_ids,
                'status' => 'active'
            ]);

            // Llamar al servicio RAG para ingesta automática
            $this->ingestToRag($document);

            return response()->json([
                'success' => true,
                'message' => 'Documento creado e ingresado correctamente',
                'document' => $document->load('typeDocument')
            ], 201);

        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => 'Error al crear documento: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        $document = Document::with('typeDocument')->find($id);
        if (!$document) {
            return response()->json(['success' => false, 'message' => 'Documento no encontrado'], 404);
        }

        return response()->json(['success' => true, 'document' => $document]);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        $document = Document::find($id);
        if (!$document) {
            return response()->json(['success' => false, 'message' => 'Documento no encontrado'], 404);
        }

        $validator = Validator::make(array_merge($request->all(), $request->allFiles()), [
            'name' => 'sometimes|required|string|max:255',
            'description' => 'nullable|string',
            'type_document_id' => 'sometimes|required|exists:type_documents,id',
            'category_ids' => 'sometimes|required|array',
            'category_ids.*' => 'exists:categories,id',
            'status' => 'sometimes|string|in:active,inactive',
            'file' => 'nullable|file|mimes:pdf|max:10240',
        ]);

        if ($validator->fails()) {
            return response()->json(['success' => false, 'errors' => $validator->errors()], 422);
        }

        try {
            $data = $request->except('file');

            if ($request->hasFile('file')) {
                // Eliminar archivo anterior del disco 'public'
                if ($document->path) {
                    $oldPath = str_replace(Storage::url(''), '', $document->path);
                    Storage::disk('public')->delete($oldPath);
                }

                // Guardar nuevo archivo
                $path = $request->file('file')->store('documents', 'public');
                $data['path'] = Storage::disk('public')->url($path);
            }

            $document->update($data);

            // Sincronizar cambios con el RAG (re-ingesta)
            $this->ingestToRag($document);

            return response()->json([
                'success' => true,
                'message' => 'Documento actualizado correctamente',
                'document' => $document->load('typeDocument')
            ]);

        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => 'Error al actualizar: ' . $e->getMessage()], 500);
        }
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        $document = Document::find($id);
        if (!$document) {
            return response()->json(['success' => false, 'message' => 'Documento no encontrado'], 404);
        }

        try {
            // Eliminar de Qdrant
            $this->deleteFromRag($document->id);
            
            // Borrado lógico
            $document->delete();
            return response()->json(['success' => true, 'message' => 'Documento archivado de la DB y eliminado de Qdrant']);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => 'Error al eliminar: ' . $e->getMessage()], 500);
        }
    }

    private function ingestToRag(Document $document)
    {
        try {
            // El RAG ve la carpeta storage/app/public/documents como /app/pdfs
            // Por lo tanto, necesitamos pasarle solo el nombre del archivo
            $filename = basename($document->path);
            
            $url = "http://rag-core:8000/ingest-pdf";
            
            $response = Http::timeout(60)->post($url, [
                'pdf_path' => $filename,
                'doc_id' => (string) $document->id,
                'name' => (string) $document->name,
                'description' => (string) $document->description,
                'category_ids' => $document->category_ids,
                'status' => $document->status,
                'replace_existing' => true
            ]);

            return $response->successful();
        } catch (\Exception $e) {
            \Log::error("Error enviando a RAG: " . $e->getMessage());
            return false;
        }
    }

    private function deleteFromRag($doc_id)
    {
        try {
            $url = "http://rag-core:8000/document/" . $doc_id;
            $response = Http::delete($url);
            return $response->successful();
        } catch (\Exception $e) {
            \Log::error("Error eliminando de RAG: " . $e->getMessage());
            return false;
        }
    }
}

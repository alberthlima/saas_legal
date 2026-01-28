<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\SoftDeletes;

class Document extends Model
{
    use HasFactory;
    use SoftDeletes;

    protected $fillable = [
        'name',
        'description',
        'path',
        'category_ids',
        'type_document_id',
        'status'
    ];

    protected $casts = [
        'category_ids' => 'array',
    ];

    /**
     * Relación con el tipo de documento.
     */
    public function typeDocument()
    {
        return $this->belongsTo(TypeDocument::class);
    }
}

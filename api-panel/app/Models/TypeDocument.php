<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Carbon\Carbon;
use Illuminate\Database\Eloquent\SoftDeletes;

class TypeDocument extends Model
{
    use SoftDeletes;
    protected $fillable = [
        'name',
        'state',
        'deleted_at'
    ];

    public function setCreatedAtAttribute($value)
    {
    	date_default_timezone_set('America/La_Paz');
        $this->attributes["created_at"]= Carbon::now();
    }

    public function setUpdatedAtAttribute($value)
    {
    	date_default_timezone_set("America/La_Paz");
        $this->attributes["updated_at"]= Carbon::now();
    }
}

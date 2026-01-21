<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use Carbon\Carbon;

class Membership extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'name',
        'description',
        'price',
        'daily_limit',
        'max_specialists',
        'state',
        'deleted_at',
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

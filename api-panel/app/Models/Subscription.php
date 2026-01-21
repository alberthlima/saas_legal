<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Subscription extends Model
{
    use SoftDeletes;

    protected $fillable = [
        'client_id',
        'membership_id',
        'start_date',
        'end_date',
        'status',
    ];

    public function client()
    {
        return $this->belongsTo(Client::class);
    }

    public function membership()
    {
        return $this->belongsTo(Membership::class);
    }

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

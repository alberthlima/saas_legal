<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Setting extends Model
{
    use HasFactory;

    protected $fillable = [
        'contact_name',
        'telegram_user',
        'bank_details',
        'admin_telegram_id',
        'qr',
    ];
}

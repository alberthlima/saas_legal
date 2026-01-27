<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('settings', function (Blueprint $table) {
            $table->id();
            $table->string('contact_name')->nullable();
            $table->string('telegram_user')->nullable();
            $table->string('admin_telegram_id')->nullable();
            $table->text('bank_details')->nullable();
            $table->string('qr')->nullable();
            $table->timestamps();
            $table->softDeletes();
        });

        // Insertar registro inicial por defecto
        \Illuminate\Support\Facades\DB::table('settings')->insert([
            'contact_name' => 'Admin SaaS Legal',
            'telegram_user' => '@SaaSLegalAdmin',
            'bank_details' => 'Banco Nacional, Cuenta: 1234567890, Titular: SaaS Legal',
            'admin_telegram_id' => '123456789',
            'qr' => null,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('settings');
    }
};

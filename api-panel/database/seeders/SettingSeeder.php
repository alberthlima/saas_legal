<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Setting;

class SettingSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        Setting::updateOrCreate(
            ['id' => 1],
            [
                'contact_name' => 'Admin SaaS Legal',
                'telegram_user' => '@SaaSLegalAdmin',
                'bank_details' => 'Banco Nacional, Cuenta: 1234567890, Titular: SaaS Legal',
                'admin_telegram_id' => '123456789',
                'qr' => null,
            ]
        );
    }
}

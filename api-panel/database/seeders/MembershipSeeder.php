<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Membership;

class MembershipSeeder extends Seeder
{
    public function run(): void
    {
        $memberships = [
            [
                'name' => 'Plan Estudiante',
                'description' => 'Acceso esencial para investigación académica y apoyo en tareas jurídicas.',
                'price' => 35.00,
                'daily_limit' => 10,
                'max_specialists' => 1,
            ],
            [
                'name' => 'Plan Profesional',
                'description' => 'Ideal para abogados independientes. Consultas rápidas y múltiples especialidades.',
                'price' => 150.00,
                'daily_limit' => 50,
                'max_specialists' => 3,
            ],
            [
                'name' => 'Plan Firma / Buffet',
                'description' => 'Acceso premium para despachos. Consultas masivas y todas las ramas del derecho.',
                'price' => 450.00,
                'daily_limit' => 250,
                'max_specialists' => 7,
            ]
        ];

        foreach ($memberships as $plan) {
            Membership::updateOrCreate(['name' => $plan['name']], [
                'description' => $plan['description'],
                'price' => $plan['price'],
                'daily_limit' => $plan['daily_limit'],
                'max_specialists' => $plan['max_specialists'],
                'state' => 1
            ]);
        }
    }
}
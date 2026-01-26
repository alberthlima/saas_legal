<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Category;

class CategorySeeder extends Seeder
{
    public function run(): void
    {
        $categories = [
            [
                'name' => 'Estudiante / Académico',
                'description' => 'Esta categoría se refiere a: Apoyo en investigación jurídica, resúmenes de leyes, práctica forense y consultas sobre doctrina legal y jurisprudencia boliviana.'
            ],
            [
                'name' => 'Derecho Civil',
                'description' => 'Esta categoría se refiere a: Contratos, deudas, herencias, alquileres y propiedad de inmuebles.'
            ],
            [
                'name' => 'Derecho Civil',
                'description' => 'Esta categoría abarca casos con respecto a: Contratos, préstamos, deudas, herencias, alquileres y propiedad de inmuebles.'
            ],

            [
                'name' => 'Derecho Penal',
                'description' => 'Esta categoría abarca casos con respecto a: Casos ante la fiscalía, defensa en delitos, procesos policiales y audiencias.'
            ],
            [
                'name' => 'Derecho de Familia',
                'description' => 'Esta categoría abarca casos con respecto a: Asistencia familiar, divorcios, guardas, tutela y adopciones.'
            ],
            [
                'name' => 'Derecho Laboral',
                'description' => 'Esta categoría abarca casos con respecto a: Cálculo de beneficios sociales, despidos injustificados, finiquitos y contratos de trabajo.'
            ],
            [
                'name' => 'Derecho Comercial',
                'description' => 'Esta categoría abarca casos con respecto a: Constitución de empresas, sociedades, marcas y trámites ante el SEPREC.'
            ],
            [
                'name' => 'Derecho Administrativo',
                'description' => 'Esta categoría abarca casos con respecto a: Trámites ante alcaldías, gobernaciones, ministerios y recursos contra el Estado.'
            ],
            [
                'name' => 'Derecho Tributario',
                'description' => 'Esta categoría abarca casos con respecto a: Impuestos, recursos ante el SIN, multas e impugnaciones tributarias.'
            ],
            [
                'name' => 'Derecho Constitucional',
                'description' => 'Esta categoría abarca casos con respecto a: Acciones de Libertad, Amparos Constitucionales y defensa de derechos fundamentales.'
            ],
        ];

        foreach ($categories as $cat) {
            Category::updateOrCreate(['name' => $cat['name']], [
                'description' => $cat['description'],
                'state' => 1
            ]);
        }
    }
}
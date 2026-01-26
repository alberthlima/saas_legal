<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ClientResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'telegram_id' => $this->telegram_id,
            'name' => $this->name,
            'ci' => $this->ci,
            'phone' => $this->phone,
            'city' => $this->city,
            'client_type' => $this->client_type,
            'state' => $this->state == 1 ? 'Activo' : 'Bloqueado',
            'created_at' => $this->created_at->format('d/m/Y H:i'),
        ];
    }
}

<?php

namespace App\Http\Controllers\Bot;

use App\Http\Controllers\Controller;
use App\Models\Client;
use App\Models\Membership;
use App\Models\Subscription;
use Illuminate\Http\Request;
use Carbon\Carbon;

class BotController extends Controller
{
    /**
     * Verifica el estado del cliente por su ID de Telegram
     */
    public function checkClient($telegram_id)
    {
        $client = Client::with(['activeSubscription.membership'])
            ->where('telegram_id', $telegram_id)
            ->first();

        if (!$client) {
            return response()->json([
                'exists' => false,
                'message' => 'Cliente no registrado'
            ]);
        }

        return response()->json([
            'exists' => true,
            'client' => $client,
            'subscription' => $client->activeSubscription
        ]);
    }

    /**
     * Registra un nuevo cliente desde el Bot
     */
    public function registerClient(Request $request)
    {
        $request->validate([
            'telegram_id' => 'required|unique:clients,telegram_id',
            'name' => 'required|string',
            'ci' => 'nullable|string',
            'client_type' => 'nullable|string',
        ]);

        $client = Client::create([
            'telegram_id' => $request->telegram_id,
            'name' => $request->name,
            'ci' => $request->ci,
            'client_type' => $request->client_type,
            'state' => 1,
        ]);

        return response()->json([
            'message' => 'Cliente registrado con éxito',
            'client' => $client
        ]);
    }

    /**
     * Lista las membresías activas para que el bot las muestre
     */
    public function listMemberships()
    {
        $memberships = Membership::where('state', 1)->get();
        
        return response()->json([
            'memberships' => $memberships
        ]);
    }

    /**
     * Crea una intención de suscripción (pendiente de pago)
     */
    public function subscribe(Request $request)
    {
        $request->validate([
            'telegram_id' => 'required|exists:clients,telegram_id',
            'membership_id' => 'required|exists:memberships,id',
        ]);

        $client = Client::where('telegram_id', $request->telegram_id)->first();

        // Si ya tiene una suscripción pendiente, la actualizamos o cancelamos la anterior
        Subscription::where('client_id', $client->id)
            ->where('status', 'pending_payment')
            ->delete();

        $subscription = Subscription::create([
            'client_id' => $client->id,
            'membership_id' => $request->membership_id,
            'status' => 'pending_payment',
        ]);

        return response()->json([
            'message' => 'Suscripción iniciada. Pendiente de pago.',
            'subscription' => $subscription
        ]);
    }
}

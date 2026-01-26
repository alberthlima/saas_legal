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

        // Buscar suscripción pendiente o activa
        $currentSubscription = Subscription::with('membership')
            ->where('client_id', $client->id)
            ->whereIn('status', ['pending_payment', 'active'])
            ->latest()
            ->first();

        return response()->json([
            'exists' => true,
            'client' => $client,
            'subscription' => $client->activeSubscription,
            'current_subscription' => $currentSubscription
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
            'phone' => 'nullable|string',
            'city' => 'nullable|string',
            'client_type' => 'nullable|string',
        ]);

        $client = Client::create([
            'telegram_id' => $request->telegram_id,
            'name' => $request->name,
            'ci' => $request->ci,
            'phone' => $request->phone,
            'city' => $request->city,
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

        // Cancelar suscripciones pendientes anteriores
        Subscription::where('client_id', $client->id)
            ->where('status', 'pending_payment')
            ->update(['status' => 'cancelled']);

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

    /**
     * Cancela la suscripción actual del cliente
     */
    public function cancelSubscription(Request $request)
    {
        $request->validate([
            'telegram_id' => 'required|exists:clients,telegram_id',
        ]);

        $client = Client::where('telegram_id', $request->telegram_id)->first();

        $subscription = Subscription::where('client_id', $client->id)
            ->whereIn('status', ['pending_payment', 'active'])
            ->latest()
            ->first();

        if ($subscription) {
            $subscription->update(['status' => 'cancelled']);
            return response()->json([
                'message' => 'Suscripción cancelada exitosamente',
                'subscription' => $subscription
            ]);
        }

        return response()->json([
            'message' => 'No hay suscripción activa para cancelar'
        ], 404);
    }
}

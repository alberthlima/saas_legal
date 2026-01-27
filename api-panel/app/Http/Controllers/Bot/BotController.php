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
     * Lista las categorías disponibles para el bot
     */
    public function listCategories()
    {
        $categories = \App\Models\Category::where('state', 1)->get();
        return response()->json([
            'categories' => $categories
        ]);
    }

    /**
     * Guarda las categorías seleccionadas para una suscripción
     */
    public function setSubscriptionCategories(Request $request)
    {
        $request->validate([
            'subscription_id' => 'required|exists:subscriptions,id',
            'category_ids' => 'required|array',
            'category_ids.*' => 'exists:categories,id',
        ]);

        $subscription = Subscription::findOrFail($request->subscription_id);
        
        // Sincronizar categorías
        $subscription->categories()->sync($request->category_ids);

        return response()->json([
            'message' => 'Categorías actualizadas correctamente',
            'subscription' => $subscription->load('categories')
        ]);
    }

    /**
     * Sube el comprobante (voucher) de pago
     */
    public function uploadVoucher(Request $request)
    {
        $request->validate([
            'subscription_id' => 'required|exists:subscriptions,id',
            'voucher' => 'required|image|max:5120', // 5MB max
        ]);

        $subscription = Subscription::findOrFail($request->subscription_id);

        if ($request->hasFile('voucher')) {
            // Eliminar voucher anterior si existe
            if ($subscription->voucher) {
                \Illuminate\Support\Facades\Storage::disk('public')->delete($subscription->voucher);
            }
            
            $path = $request->file('voucher')->store('vouchers', 'public');
            $subscription->update([
                'voucher' => $path,
                // Opcional: Podríamos cambiar el status aquí si es necesario
            ]);
        }

        return response()->json([
            'message' => 'Comprobante subido correctamente',
            'subscription' => $subscription
        ]);
    }

    /**
     * Notifica al administrador sobre un pago reportado
     */
    public function notifyPayment(Request $request)
    {
        $request->validate([
            'telegram_id' => 'required|exists:clients,telegram_id',
            'subscription_id' => 'required|exists:subscriptions,id',
        ]);

        $client = Client::where('telegram_id', $request->telegram_id)->first();
        $subscription = Subscription::with('membership')->findOrFail($request->subscription_id);

        // El bot ya maneja la notificación directa si tiene el admin_telegram_id
        // Aquí solo registramos que se notificó si fuera necesario.
        
        return response()->json([
            'message' => 'Notificación de pago enviada al administrador',
            'client_name' => $client->name,
            'plan' => $subscription->membership->name
        ]);
    }
}

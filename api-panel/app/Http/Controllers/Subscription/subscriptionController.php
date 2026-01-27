<?php

namespace App\Http\Controllers\Subscription;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Subscription;
use Illuminate\Support\Facades\Http;

class subscriptionController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index(Request $request)
    {
        $search = $request->search;

        $subscriptions = Subscription::with(['client', 'membership', 'categories'])
            ->whereHas('client', function ($query) use ($search) {
                $query->where('name', 'like', "%$search%");
            })
            ->orWhereHas('membership', function ($query) use ($search) {
                $query->where('name', 'like', "%$search%");
            })
            ->orderBy('id', 'desc')
            ->get();

        return response()->json([
            'subscriptions' => $subscriptions->map(function ($subscription) {
                return [
                    'id' => $subscription->id,
                    'name' => $subscription->client->name,
                    'membership' => $subscription->membership->name,
                    'start_date' => $subscription->start_date ? $subscription->start_date : 'N/A',
                    'end_date' => $subscription->end_date ? $subscription->end_date : 'N/A',
                    'state' => $subscription->status,
                    'voucher_url' => $subscription->voucher_url,
                    'categories' => $subscription->categories->map(function ($cat) {
                        return [
                            'id' => $cat->id,
                            'name' => $cat->name
                        ];
                    }),
                    'created_at' => $subscription->created_at->format('d/m/Y H:i'),
                ];
            })
        ]);
    }

    public function approve($id)
    {
        $subscription = Subscription::findOrFail($id);
        
        // Calcular fechas: hoy y 30 días después
        $start = now();
        $end = now()->addDays(30);

        $subscription->update([
            'status' => 'active',
            'start_date' => $start->format('Y-m-d'),
            'end_date' => $end->format('Y-m-d')
        ]);

        // Notificar al cliente vía Telegram
        $this->notifyClient($subscription);

        return response()->json([
            'message' => 'Suscripción aprobada con éxito',
            'subscription' => $subscription
        ]);
    }

    public function cancel($id)
    {
        $subscription = Subscription::findOrFail($id);
        
        $subscription->update([
            'status' => 'cancelled'
        ]);

        return response()->json([
            'message' => 'Suscripción cancelada'
        ]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }

    private function notifyClient($subscription)
    {
        $subscription->load(['client', 'membership']);
        $client = $subscription->client;
        $membership = $subscription->membership;
        $token = env('TELEGRAM_TOKEN');

        if (!$client->telegram_id || !$token) {
            return;
        }

        $message = "🎉 <b>¡Suscripción Activada!</b>\n\n"
                 . "Hola <b>{$client->name}</b>, tenemos buenas noticias.\n"
                 . "Tu suscripción al plan <b>{$membership->name}</b> ha sido aprobada con éxito.\n\n"
                 . "📅 <b>Vence el:</b> {$subscription->end_date}\n\n"
                 . "Ya puedes disfrutar de todos tus beneficios. Usa /start para ver tu panel actualizado.";

        try {
            Http::post("https://api.telegram.org/bot{$token}/sendMessage", [
                'chat_id' => $client->telegram_id,
                'text' => $message,
                'parse_mode' => 'HTML'
            ]);
        } catch (\Exception $e) {
            \Log::error("Error notificando cliente {$client->telegram_id}: " . $e->getMessage());
        }
    }
}

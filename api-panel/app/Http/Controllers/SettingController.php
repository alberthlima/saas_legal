<?php

namespace App\Http\Controllers;

use App\Models\Setting;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class SettingController extends Controller
{
    public function index()
    {
        $setting = Setting::first();
        if (!$setting) {
            $setting = Setting::updateOrCreate(
                ['id' => 1],
                [
                    'contact_name' => 'Admin SaaS Legal',
                    'telegram_user' => '@SaaSLegalAdmin',
                    'bank_details' => 'Banco Nacional, Cuenta: 12345678, Titular: SaaS Legal',
                    'admin_telegram_id' => '123456789',
                    'qr' => null,
                ]
            );
        }
        
        $setting->qr_url = $setting->qr ? url(Storage::url($setting->qr)) : null;

        return response()->json($setting);
    }

    public function update(Request $request)
    {
        $setting = Setting::first();
        if (!$setting) {
            $setting = new Setting();
        }

        $data = $request->only([
            'contact_name',
            'telegram_user',
            'bank_details',
            'admin_telegram_id'
        ]);

        if ($request->hasFile('qr')) {
            // Eliminar imagen anterior si existe
            if ($setting->qr) {
                Storage::disk('public')->delete($setting->qr);
            }
            $path = $request->file('qr')->store('qr_codes', 'public');
            $data['qr'] = $path;
        }

        $setting->fill($data);
        $setting->save();

        if ($setting->qr) {
            $setting->qr_url = url(Storage::url($setting->qr));
        } else {
            $setting->qr_url = null;
        }

        return response()->json([
            'message' => 'Configuración actualizada correctamente',
            'setting' => $setting
        ]);
    }

    public function getBotSettings()
    {
        $setting = Setting::first();
        if ($setting && $setting->qr) {
            $setting->qr_url = url(Storage::url($setting->qr));
        } else if ($setting) {
            $setting->qr_url = null;
        }
        return response()->json($setting);
    }
}

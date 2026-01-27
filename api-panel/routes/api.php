<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\Roles\RoleController;
use App\Http\Controllers\User\userController;
use App\Http\Controllers\Category\categoryController;
use App\Http\Controllers\TypeDocument\typeDocumentController;
use App\Http\Controllers\Membership\MembershipController;
use App\Http\Controllers\Bot\BotController;
use App\Http\Controllers\Client\clientController;
use App\Http\Controllers\Subscription\subscriptionController;
use App\Http\Controllers\SettingController;

// Rutas para el Bot de Telegram
Route::group(['prefix' => 'bot'], function () {
    Route::get('/check-client/{telegram_id}', [BotController::class, 'checkClient']);
    Route::post('/register-client', [BotController::class, 'registerClient']);
    Route::get('/memberships', [BotController::class, 'listMemberships']);
    Route::post('/subscribe', [BotController::class, 'subscribe']);
    Route::post('/cancel-subscription', [BotController::class, 'cancelSubscription']);
    Route::get('/settings', [SettingController::class, 'getBotSettings']);
    Route::get('/categories', [BotController::class, 'listCategories']);
    Route::post('/set-categories', [BotController::class, 'setSubscriptionCategories']);
    Route::post('/notify-payment', [BotController::class, 'notifyPayment']);
    Route::post('/upload-voucher', [BotController::class, 'uploadVoucher']);
});

Route::group([
    //'middleware' => 'auth:api',
    'prefix' => 'auth'
], function ($router) {
    Route::post('/register', [AuthController::class, 'register'])->name('register');
    Route::post('/login', [AuthController::class, 'login'])->name('login');
    Route::post('/logout', [AuthController::class, 'logout'])->middleware('auth:api')->name('logout');
    Route::post('/refresh', [AuthController::class, 'refresh'])->middleware('auth:api')->name('refresh');
    Route::post('/me', [AuthController::class, 'me'])->middleware('auth:api')->name('me');
});

Route::group([
    "middleware" => ["auth:api"]
], function ($router) {
    Route::resource("role", RoleController::class);

    Route::get("user/get-roles", [userController::class, 'getRoles']);
    Route::post("user/{id}", [userController::class, 'update']);
    Route::resource("user", userController::class);

    Route::resource("category", categoryController::class);

    Route::resource("type", typeDocumentController::class);

    Route::resource("membership", MembershipController::class);

    Route::resource("client", clientController::class);

    Route::post("subscription/{id}/approve", [subscriptionController::class, 'approve']);
    Route::post("subscription/{id}/cancel", [subscriptionController::class, 'cancel']);
    Route::resource("subscription", subscriptionController::class);

    Route::get("settings", [SettingController::class, 'index']);
    Route::post("settings", [SettingController::class, 'update']);
});
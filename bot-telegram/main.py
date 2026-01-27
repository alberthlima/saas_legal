import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Configuración de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Cargar variables de entorno
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("LARAVEL_API_URL")

# Ruta del Sticker Local
STICKER_BIENVENIDA = "assets/img/sticker_animado_final.webm"

# Estados de la conversación
BOTONES_INICIO, NOMBRE, CI, TELEFONO, CIUDAD, TIPO, SELECCION_PLAN, GESTION_SUSCRIPCION, SELECCION_CATEGORIAS, ESPERANDO_VOUCHER = range(10)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra un Sticker y verifica el acceso con HTML"""
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    logging.info(f"Comando /start recibido de {first_name} (ID: {telegram_id})")

    # Limpiar datos previos
    context.user_data.clear()

    # 📝 Mensaje de Bienvenida con HTML
    welcome_html = (
        f"⚖️ <b>Bienvenido, {first_name}</b>\n"
        f"<i>Iniciando sistema de justicia digital...</i>\n\n"
        f"🔍 Verificando su acceso en la base de datos..."
    )
    
    await update.message.reply_text(welcome_html, parse_mode="HTML")

    #  Enviar Sticker de Bienvenida
    try:
        if os.path.exists(STICKER_BIENVENIDA):
            with open(STICKER_BIENVENIDA, 'rb') as sticker:
                await update.message.reply_sticker(sticker=sticker)
    except Exception as e:
        logging.error(f"Error enviando Sticker: {e}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/bot/check-client/{telegram_id}")
            data = response.json()

            if data.get('exists'):
                client_data = data['client']
                subscription = data.get('current_subscription')
                
                msg = (
                    f"✅ <b>Acceso Concedido</b>\n\n"
                    f"Bienvenido de nuevo, <b>{client_data['name']}</b>.\n"
                )
                if subscription:
                    msg += f"📋 Membresía: <code>{subscription['membership']['name']}</code>\n"
                    msg += f"📅 Estado: <b>{subscription['status']}</b>"
                else:
                    msg += "\n⚠️ No tienes una membresía activa.\nUsa /planes para ver las opciones disponibles."
                
                await update.message.reply_text(msg, parse_mode="HTML")
                return ConversationHandler.END
            else:
                reply_keyboard = [['📝 Iniciar Registro', '❌ Cancelar']]
                await update.message.reply_text(
                    "👋 <b>¡Hola! Un gusto saludarte.</b>\n\n"
                    "Parece que es tu primera vez por aquí. Para brindarte asesoría legal personalizada, necesitamos completar un registro rápido.\n\n"
                    "¿Deseas registrarte ahora?",
                    parse_mode="HTML",
                    reply_markup=ReplyKeyboardMarkup(
                        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                    ),
                )
                return BOTONES_INICIO
                
    except Exception as e:
        logging.error(f"Error en start: {e}")
        await update.message.reply_text("❌ Error al conectar con el servidor central.", parse_mode="HTML")
        return ConversationHandler.END

async def manejar_decision_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el botón de Iniciar Registro o Cancelar"""
    decision = update.message.text

    if decision == '📝 Iniciar Registro':
        await update.message.reply_text(
            "✨ <b>¡Excelente decisión!</b>\n\n"
            "Comencemos. Por favor, escribe tu <b>Nombre Completo</b>:",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )
        return NOMBRE
    else:
        await update.message.reply_text(
            "Entendido. Si cambias de opinión, solo escribe /start nuevamente.",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def pedir_ci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el nombre y pide el CI"""
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"🤝 Gracias, <b>{update.message.text}</b>.\n\nAhora, por favor ingresa tu <b>CI</b>:",
        parse_mode="HTML"
    )
    return CI

async def pedir_telefono(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el CI y pide el telefono"""
    context.user_data['ci'] = update.message.text
    await update.message.reply_text(
        f"📱 Gracias. Ahora, por favor ingresa tu <b>Número de Teléfono</b>:",
        parse_mode="HTML"
    )
    return TELEFONO

async def pedir_ciudad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el Telefono y pide la Ciudad"""
    context.user_data['telefono'] = update.message.text
    
    ciudades = [
        ['La Paz', 'El Alto', 'Santa Cruz'],
        ['Cochabamba', 'Oruro', 'Potosí'],
        ['Tarija', 'Sucre', 'Trinidad'],
        ['Cobija']
    ]
    
    await update.message.reply_text(
        "🌆 <b>¿En qué ciudad te encuentras actualmente?</b>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            ciudades, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return CIUDAD

async def pedir_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda la Ciudad y pide el tipo de cliente"""
    context.user_data['city'] = update.message.text
    
    reply_keyboard = [['Estudiante', 'Abogado', 'Particular']]
    
    await update.message.reply_text(
        "📍 <b>Último paso</b>\n\n¿Cuál es tu perfil profesional?",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return TIPO

async def finalizar_registro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía los datos a Laravel y finaliza"""
    context.user_data['client_type'] = update.message.text
    telegram_id = update.effective_user.id
    
    await update.message.reply_text("💾 <b>Procesando registro...</b>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())

    try:
        datos_cliente = {
            "telegram_id": telegram_id,
            "name": context.user_data['name'],
            "ci": context.user_data['ci'],
            "phone": context.user_data['telefono'],
            "city": context.user_data['city'],
            "client_type": context.user_data['client_type']
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/bot/register-client", json=datos_cliente)
            
            if response.status_code == 200:
                await update.message.reply_text(
                    "🎉 <b>¡Felicidades! Tu cuenta ha sido creada.</b>\n\n"
                    "Usa el comando /planes para elegir tu membresía.",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text("❌ Hubo un inconveniente al guardar tus datos.", parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error en registro: {e}")
        await update.message.reply_text("❌ Error de comunicación.", parse_mode="HTML")

    return ConversationHandler.END

async def mostrar_planes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra los planes disponibles desde la API"""
    telegram_id = update.effective_user.id
    
    try:
        async with httpx.AsyncClient() as client:
            check_response = await client.get(f"{API_URL}/bot/check-client/{telegram_id}")
            check_data = check_response.json()
            
            if not check_data.get('exists'):
                await update.message.reply_text("⚠️ <b>Primero debes registrarte.</b>\nUsa /start para registrarte.", parse_mode="HTML")
                return ConversationHandler.END
            
            current_sub = check_data.get('current_subscription')
            
            if current_sub:
                plan_name = current_sub['membership']['name']
                plan_price = current_sub['membership']['price']
                status = current_sub['status']
                context.user_data['current_subscription'] = current_sub
                
                if status == 'pending_payment':
                    msg = (
                        f"💳 <b>Suscripción Pendiente</b>\n\n"
                        f"Plan: <b>{plan_name}</b>\n"
                        f"💰 Precio: <code>{plan_price} BOB</code>\n"
                        f"🔴 Estado: <b>Pendiente de Pago</b>\n\n"
                        f"¿Qué deseas hacer?"
                    )
                    keyboard = [['💳 Pagar Ahora'], ['🔄 Cambiar Plan'], ['❌ Cancelar Suscripción']]
                elif status == 'active':
                    msg = (
                        f"✅ <b>Suscripción Activa</b>\n\n"
                        f"Tu plan <b>{plan_name}</b> está activo.\n"
                        f"💰 Precio: <code>{plan_price} BOB</code>\n\n"
                        f"¿Qué deseas hacer?"
                    )
                    keyboard = [['📊 Ver Detalles'], ['❌ Cancelar Suscripción']]
                else:
                    return await mostrar_lista_planes(update, context, client)
                
                await update.message.reply_text(msg, parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
                return GESTION_SUSCRIPCION
            else:
                return await mostrar_lista_planes(update, context, client)
    except Exception as e:
        logging.error(f"Error en mostrar_planes: {e}")
        await update.message.reply_text("❌ Error de servidor.", parse_mode="HTML")
        return ConversationHandler.END

async def mostrar_lista_planes(update: Update, context: ContextTypes.DEFAULT_TYPE, client):
    """Muestra la lista de planes disponibles"""
    response = await client.get(f"{API_URL}/bot/memberships")
    data = response.json()
    memberships = data.get('memberships', [])
    
    if not memberships:
        await update.message.reply_text("❌ No hay planes disponibles.", parse_mode="HTML")
        return ConversationHandler.END
    
    context.user_data['memberships'] = memberships
    msg = "💎 <b>Planes de Membresía Disponibles</b>\n\n"
    keyboard = []
    for plan in memberships:
        msg += f"🔹 <b>{plan['name']}</b>\n💰 {plan['price']} BOB | Límite: {plan['daily_limit']} consultas\n🛡️ {plan['max_specialists']} Especialistas\n\n"
        keyboard.append([plan['name']])
    
    keyboard.append(["❌ Cancelar"])
    await update.message.reply_text(msg + "Elija su plan:", parse_mode="HTML", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return SELECCION_PLAN

async def procesar_seleccion_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el plan y pide elegir categorías"""
    seleccion = update.message.text
    if seleccion == "❌ Cancelar":
        await update.message.reply_text("Cancelado.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    memberships = context.user_data.get('memberships', [])
    plan = next((p for p in memberships if p['name'] == seleccion), None)
    
    if not plan:
        await update.message.reply_text("Opción no válida.")
        return SELECCION_PLAN
    
    context.user_data['selected_plan'] = plan
    context.user_data['selected_categories'] = []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/bot/categories")
            categories = response.json().get('categories', [])
            context.user_data['available_categories'] = categories
            
            # Lógica para Plan Estudiante (auto-seleccionar y finalizar)
            if "Estudiante" in plan['name']:
                est_cat = next((c for c in categories if "Estudiante" in c['name']), None)
                if est_cat:
                    context.user_data['selected_categories'] = [est_cat['id']]
                    await update.message.reply_text("📚 <b>Plan Estudiante:</b> Se ha asignado automáticamente la categoría Estudiante.", parse_mode="HTML")
                    return await finalizar_suscripcion_con_categorias(update, context)
                else:
                    await update.message.reply_text("❌ Error: No se encontró la categoría Estudiante.")
                    return ConversationHandler.END

            # Iniciar selección secuencial para otros planes
            context.user_data['selection_step'] = 1
            return await pedir_siguiente_categoria(update, context)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ Error de comunicación con el servidor.")
        return ConversationHandler.END

async def pedir_siguiente_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pide la siguiente categoría en el flujo secuencial"""
    plan = context.user_data['selected_plan']
    step = context.user_data['selection_step']
    available = context.user_data['available_categories']
    selected_ids = context.user_data['selected_categories']

    if step > plan['max_specialists']:
        return await finalizar_suscripcion_con_categorias(update, context)

    msg = (
        f"🎯 <b>Plan: {plan['name']}</b>\n"
        f"Seleccione su especialista <b>{step}/{plan['max_specialists']}</b>:"
    )
    
    # Mostrar solo categorías no seleccionadas aún
    keyboard = []
    for cat in available:
        if cat['id'] not in selected_ids:
            keyboard.append([cat['name']])
    
    keyboard.append(["❌ Cancelar"])
    
    await update.message.reply_text(
        msg, 
        parse_mode="HTML", 
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return SELECCION_CATEGORIAS

async def manejar_seleccion_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección de UNA categoría y pasa a la siguiente"""
    seleccion = update.message.text
    available = context.user_data['available_categories']
    selected = context.user_data['selected_categories']
    
    if seleccion == "❌ Cancelar":
        await update.message.reply_text("Acción cancelada.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    category = next((c for c in available if c['name'] == seleccion), None)
    
    if not category:
        await update.message.reply_text("Por favor, elija una opción válida del teclado.")
        return await pedir_siguiente_categoria(update, context)
    
    selected.append(category['id'])
    context.user_data['selection_step'] += 1
    
    return await pedir_siguiente_categoria(update, context)

async def finalizar_suscripcion_con_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Crea la suscripción y asocia las categorías"""
    telegram_id = update.effective_user.id
    plan = context.user_data['selected_plan']
    categories = context.user_data['selected_categories']
    
    await update.message.reply_text("⏳ <b>Procesando su suscripción...</b>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())

    try:
        async with httpx.AsyncClient() as client:
            # 1. Crear Suscripción
            sub_resp = await client.post(f"{API_URL}/bot/subscribe", json={
                "telegram_id": telegram_id,
                "membership_id": plan['id']
            }, timeout=30.0)
            
            if sub_resp.status_code != 200:
                logging.error(f"Error en subscribe: {sub_resp.text}")
                await update.message.reply_text("❌ No pudimos iniciar tu suscripción en este momento.")
                return ConversationHandler.END

            subscription = sub_resp.json().get('subscription')
            
            # 2. Guardar Categorías
            cat_resp = await client.post(f"{API_URL}/bot/set-categories", json={
                "subscription_id": subscription['id'],
                "category_ids": categories
            }, timeout=30.0)
            
            if cat_resp.status_code != 200:
                logging.error(f"Error en set-categories: {cat_resp.text}")
                await update.message.reply_text("❌ Error al asignar especialidades.")
                return ConversationHandler.END
            
            await update.message.reply_text(
                f"🎉 <b>¡Registro Exitoso!</b>\n\n"
                f"Has elegido el <b>{plan['name']}</b>.\n"
                f"Estado: <b>Pendiente de Pago</b>.\n\n"
                f"Usa /planes para ver los datos de pago y activar tus beneficios.",
                parse_mode="HTML"
            )
            return ConversationHandler.END
    except Exception as e:
        logging.error(f"Error crítico: {e}", exc_info=True)
        await update.message.reply_text("❌ Error de comunicación con el servidor central.")
        return ConversationHandler.END

async def manejar_gestion_suscripcion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el pago y detalles con datos dinámicos"""
    opcion = update.message.text
    telegram_id = update.effective_user.id
    current_sub = context.user_data.get('current_subscription')

    if opcion == '💳 Pagar Ahora':
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{API_URL}/bot/settings")
                settings = resp.json()
                
                msg = (
                    f"💳 <b>Datos de Pago</b>\n\n"
                    f"👤 <b>Contacto:</b> {settings['contact_name']}\n"
                    f"🏦 <b>Datos Bancarios:</b>\n{settings['bank_details']}\n\n"
                    f"📱 <b>Soporte:</b> {settings['telegram_user']}\n\n"
                    "Escanea el siguiente QR para realizar el pago:"
                )
                
                keyboard = [['✅ Pago Realizado'], ['❌ Volver']]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

                qr_url = settings.get('qr_url')
                if qr_url:
                    # Ajustar URL si estamos en Docker (localhost -> saas_legal_api)
                    if "localhost" in qr_url or "127.0.0.1" in qr_url:
                        qr_url = qr_url.replace("localhost", "saas_legal_api").replace("127.0.0.1", "saas_legal_api")
                    
                    try:
                        qr_resp = await client.get(qr_url, timeout=10.0)
                        if qr_resp.status_code == 200:
                            from io import BytesIO
                            photo = BytesIO(qr_resp.content)
                            photo.name = "qr_pago.png"
                            await update.message.reply_photo(photo=photo, caption=msg, parse_mode="HTML", reply_markup=reply_markup)
                        else:
                            logging.error(f"Error QR: status {qr_resp.status_code} on {qr_url}")
                            await update.message.reply_text(msg + "\n\n⚠️ (No se pudo cargar el QR, usa los datos manuales)", parse_mode="HTML", reply_markup=reply_markup)
                    except Exception as e:
                        logging.error(f"Error descargando QR en {qr_url}: {e}")
                        await update.message.reply_text(msg + "\n\n⚠️ (Error al cargar el QR)", parse_mode="HTML", reply_markup=reply_markup)
                else:
                    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=reply_markup)
                return GESTION_SUSCRIPCION
        except Exception as e:
            logging.error(f"Error settings: {e}")
            await update.message.reply_text("❌ Error de comunicación. Intenta de nuevo en unos segundos.")
            return ConversationHandler.END

    elif opcion == '✅ Pago Realizado':
        await update.message.reply_text(
            "📸 <b>¡Excelente!</b>\n\nPor favor, <b>envía una foto de tu comprobante o voucher</b> de pago para que el administrador pueda verificarlo rápidamente.",
            parse_mode="HTML", reply_markup=ReplyKeyboardRemove()
        )
        return ESPERANDO_VOUCHER

    elif opcion == '❌ Volver':
        return await mostrar_planes(update, context)

    elif opcion == '❌ Cancelar Suscripción':
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_URL}/bot/cancel-subscription",
                    json={"telegram_id": telegram_id}
                )
                if response.status_code == 200:
                    await update.message.reply_text("✅ Suscripción Cancelada.", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
                else:
                    await update.message.reply_text("❌ Error al cancelar.", reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            logging.error(f"Error: {e}")
            await update.message.reply_text("Error de comunicación.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    elif opcion == '📊 Ver Detalles':
        if current_sub:
            plan = current_sub['membership']
            await update.message.reply_text(
                f"📊 <b>Detalles de tu Suscripción</b>\n\n"
                f"📦 <b>Plan:</b> {plan['name']}\n"
                f"💰 <b>Precio:</b> {plan['price']} BOB\n"
                f"✅ <b>Límite Diario:</b> {plan['daily_limit']} consultas\n"
                f"👥 <b>Especialistas:</b> {plan['max_specialists']}",
                parse_mode="HTML", reply_markup=ReplyKeyboardRemove()
            )
        return ConversationHandler.END

    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación"""
    await update.message.reply_text(
        "Acción cancelada. 👋",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def manejar_envio_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la foto del voucher, la sube a la API y notifica al admin"""
    telegram_id = update.effective_user.id
    current_sub = context.user_data.get('current_subscription')
    
    if not update.message.photo:
        await update.message.reply_text("⚠️ Por favor, envía una <b>foto</b> del comprobante.")
        return ESPERANDO_VOUCHER

    # Obtener la foto (la mejor calidad)
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    
    await update.message.reply_text("⏳ <b>Subiendo comprobante...</b>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient() as client:
            # 1. Subir a la API
            files = {'voucher': ('voucher.jpg', bytes(photo_bytes), 'image/jpeg')}
            data = {'subscription_id': current_sub['id']}
            
            resp = await client.post(f"{API_URL}/bot/upload-voucher", data=data, files=files, timeout=30.0)
            
            if resp.status_code != 200:
                logging.error(f"Error subiendo voucher: {resp.text}")
                await update.message.reply_text("❌ Error al subir el comprobante. Por favor intenta de nuevo.")
                return ESPERANDO_VOUCHER

            # 2. Notificar al Admin
            resp_settings = await client.get(f"{API_URL}/bot/settings")
            settings = resp_settings.json()
            admin_id = settings.get('admin_telegram_id')

            if admin_id:
                first_name = update.effective_user.first_name
                plan_name = current_sub['membership']['name']
                msg_admin = (
                    f"🔔 <b>¡Nuevo Pago con Voucher!</b>\n\n"
                    f"👤 <b>Cliente:</b> {first_name}\n"
                    f"📦 <b>Plan:</b> {plan_name}\n"
                    f"🆔 <b>Telegram ID:</b> <code>{telegram_id}</code>\n\n"
                    f"Verifique el comprobante en el panel."
                )
                try:
                    # Enviar mensaje al admin con la foto del voucher
                    from io import BytesIO
                    voucher_to_admin = BytesIO(photo_bytes)
                    voucher_to_admin.name = "comprobante.jpg"
                    await context.bot.send_photo(chat_id=admin_id, photo=voucher_to_admin, caption=msg_admin, parse_mode="HTML")
                except Exception as e:
                    logging.error(f"Error enviando voucher al admin: {e}")

            await update.message.reply_text(
                "✅ <b>¡Comprobante Recibido!</b>\n\n"
                "Tu pago está siendo verificado. Te notificaremos cuando tu suscripción sea activada.",
                parse_mode="HTML", reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END

    except Exception as e:
        logging.error(f"Error crítico en voucher: {e}", exc_info=True)
        await update.message.reply_text("❌ Error de comunicación. Intenta subirlo de nuevo.")
        return ESPERANDO_VOUCHER

import asyncio

if __name__ == '__main__':
    if not TOKEN:
        logging.error("TELEGRAM_TOKEN no encontrado en el archivo .env")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BOTONES_INICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_decision_inicio)],
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pedir_ci)],
            CI: [MessageHandler(filters.TEXT & ~filters.COMMAND, pedir_telefono)],
            TELEFONO: [MessageHandler(filters.TEXT & ~filters.COMMAND, pedir_ciudad)],
            CIUDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, pedir_tipo)],
            TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalizar_registro)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    planes_handler = ConversationHandler(
        entry_points=[CommandHandler("planes", mostrar_planes)],
        states={
            SELECCION_PLAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_seleccion_plan)],
            SELECCION_CATEGORIAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_seleccion_categorias)],
            GESTION_SUSCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_gestion_suscripcion)],
            ESPERANDO_VOUCHER: [MessageHandler(filters.PHOTO, manejar_envio_voucher)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)
    app.add_handler(planes_handler)
    
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    logging.info("Iniciando Bot...")
    app.run_polling()

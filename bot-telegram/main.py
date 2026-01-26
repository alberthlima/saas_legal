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
BOTONES_INICIO, NOMBRE, CI, TELEFONO, CIUDAD, TIPO, SELECCION_PLAN, GESTION_SUSCRIPCION = range(8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra un Sticker y verifica el acceso con HTML"""
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    logging.info(f"Comando /start recibido de {first_name} (ID: {telegram_id})")

    # 📝 Mensaje de Bienvenida con HTML
    # Nota: En Telegram HTML, no existe <br>, se usa \n para saltos de línea.
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
        else:
            logging.warning(f"No se encontró el sticker en {STICKER_BIENVENIDA}")
    except Exception as e:
        logging.error(f"Error enviando Sticker: {e}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/bot/check-client/{telegram_id}")
            data = response.json()

            if data.get('exists'):
                client_data = data['client']
                subscription = data.get('subscription')
                
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
                # Flujo para usuario nuevo con botones estéticos
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
            # Primero verificamos si el cliente existe
            check_response = await client.get(f"{API_URL}/bot/check-client/{telegram_id}")
            check_data = check_response.json()
            
            if not check_data.get('exists'):
                await update.message.reply_text(
                    "⚠️ <b>Primero debes registrarte.</b>\nUsa /start para iniciar tu registro.",
                    parse_mode="HTML"
                )
                return ConversationHandler.END
            
            # Verificar si ya tiene una suscripción activa o pendiente
            current_sub = check_data.get('current_subscription')
            
            if current_sub:
                # Ya tiene una suscripción
                plan_name = current_sub['membership']['name']
                plan_price = current_sub['membership']['price']
                status = current_sub['status']
                
                # Guardamos la suscripción actual en context
                context.user_data['current_subscription'] = current_sub
                
                if status == 'pending_payment':
                    msg = (
                        f"💳 <b>Suscripción Pendiente</b>\n\n"
                        f"Ya tienes el plan <b>{plan_name}</b> seleccionado.\n"
                        f"💰 Precio: <code>{plan_price} BOB</code>\n"
                        f"🔴 Estado: <b>Pendiente de Pago</b>\n\n"
                        f"¿Qué deseas hacer?"
                    )
                    keyboard = [
                        ['💳 Pagar Ahora'],
                        ['🔄 Cambiar Plan'],
                        ['❌ Cancelar Suscripción']
                    ]
                elif status == 'active':
                    msg = (
                        f"✅ <b>Suscripción Activa</b>\n\n"
                        f"Tu plan <b>{plan_name}</b> está activo.\n"
                        f"💰 Precio: <code>{plan_price} BOB</code>\n\n"
                        f"¿Qué deseas hacer?"
                    )
                    keyboard = [
                        ['📊 Ver Detalles'],
                        ['❌ Cancelar Suscripción']
                    ]
                else:
                    # Estado desconocido, mostrar planes normales
                    return await mostrar_lista_planes(update, context, client)
                
                await update.message.reply_text(
                    msg,
                    parse_mode="HTML",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard, one_time_keyboard=True, resize_keyboard=True
                    )
                )
                return GESTION_SUSCRIPCION
            else:
                # No tiene suscripción, mostrar lista de planes
                return await mostrar_lista_planes(update, context, client)
            
    except Exception as e:
        logging.error(f"Error en mostrar_planes: {e}")
        await update.message.reply_text("❌ Error al conectar con el servidor.", parse_mode="HTML")
        return ConversationHandler.END

async def mostrar_lista_planes(update: Update, context: ContextTypes.DEFAULT_TYPE, client):
    """Muestra la lista de planes disponibles"""
    response = await client.get(f"{API_URL}/bot/memberships")
    data = response.json()
    
    memberships = data.get('memberships', [])
    if not memberships:
        await update.message.reply_text("❌ No hay planes disponibles en este momento.", parse_mode="HTML")
        return ConversationHandler.END
    
    # Guardamos las membresías en context.user_data para usarlas después
    context.user_data['memberships'] = memberships
    
    # Construir el mensaje con los planes
    msg = "💎 <b>Planes de Membresía Disponibles</b>\n\n"
    keyboard = []
    
    for plan in memberships:
        msg += (
            f"🔹 <b>{plan['name']}</b>\n"
            f"💰 Precio: <code>{plan['price']} BOB</code>\n"
            f"📝 {plan['description']}\n"
            f"✅ Límite Diario: {plan['daily_limit']} consultas\n\n"
        )
        keyboard.append([plan['name']])
        
    keyboard.append(["❌ Cancelar"])
    
    await update.message.reply_text(
        msg + "Por favor, elige el plan que mejor se adapte a tus necesidades:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return SELECCION_PLAN

async def procesar_seleccion_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa el plan elegido y crea la suscripción"""
    seleccion = update.message.text
    telegram_id = update.effective_user.id
    
    if seleccion == "❌ Cancelar":
        await update.message.reply_text("Acción cancelada. Usa /planes cuando estés listo.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    memberships = context.user_data.get('memberships', [])
    plan_elegido = next((p for p in memberships if p['name'] == seleccion), None)
    
    if not plan_elegido:
        await update.message.reply_text("❌ Selección no válida. Por favor elige de la lista.")
        return SELECCION_PLAN
    
    try:
        async with httpx.AsyncClient() as client:
            datos_sub = {
                "telegram_id": telegram_id,
                "membership_id": plan_elegido['id']
            }
            response = await client.post(f"{API_URL}/bot/subscribe", json=datos_sub)
            
            if response.status_code == 200:
                await update.message.reply_text(
                    f"✅ <b>¡Excelente elección!</b>\n\n"
                    f"Has seleccionado el <b>{plan_elegido['name']}</b>.\n"
                    f"Su suscripción está <b>Pendiente de Pago</b>.\n\n"
                    f"Por favor, realice el pago correspondiente para activar sus beneficios.",
                    parse_mode="HTML",
                    reply_markup=ReplyKeyboardRemove()
                )
            else:
                await update.message.reply_text("❌ No pudimos procesar tu suscripción. Intenta más tarde.", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        logging.error(f"Error en procesar_seleccion_plan: {e}")
        await update.message.reply_text("❌ Error de comunicación.", reply_markup=ReplyKeyboardRemove())
        
    return ConversationHandler.END

async def manejar_gestion_suscripcion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja las opciones cuando el usuario ya tiene una suscripción"""
    opcion = update.message.text
    telegram_id = update.effective_user.id
    
    if opcion == '💳 Pagar Ahora':
        await update.message.reply_text(
            "💳 <b>Proceso de Pago</b>\n\n"
            "Por favor, realiza la transferencia bancaria a:\n\n"
            "🏦 <b>Banco:</b> Banco Nacional\n"
            "💼 <b>Cuenta:</b> 1234567890\n"
            "👤 <b>Titular:</b> SaaS Legal\n\n"
            "Una vez realizado el pago, envía el comprobante a nuestro WhatsApp para activar tu membresía.",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    elif opcion == '🔄 Cambiar Plan':
        # Mostrar lista de planes disponibles
        try:
            async with httpx.AsyncClient() as client:
                return await mostrar_lista_planes(update, context, client)
        except Exception as e:
            logging.error(f"Error al cambiar plan: {e}")
            await update.message.reply_text("❌ Error al cargar planes.", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
    
    elif opcion == '❌ Cancelar Suscripción':
        # Cancelar la suscripción actual
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_URL}/bot/cancel-subscription",
                    json={"telegram_id": telegram_id}
                )
                
                if response.status_code == 200:
                    await update.message.reply_text(
                        "✅ <b>Suscripción Cancelada</b>\n\n"
                        "Tu suscripción ha sido cancelada exitosamente.\n"
                        "Puedes volver a suscribirte en cualquier momento usando /planes",
                        parse_mode="HTML",
                        reply_markup=ReplyKeyboardRemove()
                    )
                else:
                    await update.message.reply_text(
                        "❌ No se pudo cancelar la suscripción. Intenta más tarde.",
                        reply_markup=ReplyKeyboardRemove()
                    )
        except Exception as e:
            logging.error(f"Error al cancelar suscripción: {e}")
            await update.message.reply_text("❌ Error de comunicación.", reply_markup=ReplyKeyboardRemove())
        
        return ConversationHandler.END
    
    elif opcion == '📊 Ver Detalles':
        current_sub = context.user_data.get('current_subscription')
        if current_sub:
            plan = current_sub['membership']
            await update.message.reply_text(
                f"📊 <b>Detalles de tu Suscripción</b>\n\n"
                f"📦 <b>Plan:</b> {plan['name']}\n"
                f"💰 <b>Precio:</b> {plan['price']} BOB\n"
                f"📝 <b>Descripción:</b> {plan['description']}\n"
                f"✅ <b>Límite Diario:</b> {plan['daily_limit']} consultas\n"
                f"👥 <b>Especialistas:</b> {plan['max_specialists']}\n"
                f"🟢 <b>Estado:</b> Activa",
                parse_mode="HTML",
                reply_markup=ReplyKeyboardRemove()
            )
        return ConversationHandler.END
    
    else:
        await update.message.reply_text(
            "❌ Opción no válida. Usa /planes para ver tus opciones.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación"""
    await update.message.reply_text(
        "Acción cancelada. 👋",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

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
            GESTION_SUSCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_gestion_suscripcion)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)
    app.add_handler(planes_handler)
    
    # Solución para RuntimeError en versiones nuevas de Python (3.12, 3.13, 3.14)
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    logging.info("Iniciando Bot...")
    app.run_polling()

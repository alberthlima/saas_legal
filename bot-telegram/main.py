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

# ID de Sticker Estético (Mazo de justicia o balanza)
# Puedes obtener este ID enviando un sticker a @idstickerbot en Telegram
STICKER_LEGAL = "CAACAgEAAxkBAAMrZ4_F_V_X_X_X_X_X_X_X_X" 

# Estados de la conversación
BOTONES_INICIO, NOMBRE, CI, TIPO = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra un Sticker y verifica el acceso con HTML"""
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    logging.info(f"Comando /start recibido de {first_name} (ID: {telegram_id})")

    # � Enviar Sticker de Bienvenida (Opcional, si el ID es válido)
    try:
        # Si no tienes un ID válido, puedes comentar esta línea
        # await update.message.reply_sticker(sticker=STICKER_LEGAL)
        pass
    except Exception as e:
        logging.error(f"Error enviando Sticker: {e}")

    # 📝 Mensaje de Bienvenida con HTML
    # Nota: En Telegram HTML, no existe <br>, se usa \n para saltos de línea.
    welcome_html = (
        f"⚖️ <b>Bienvenido, {first_name}</b>\n"
        f"<i>Iniciando sistema de justicia digital...</i>\n\n"
        f"🔍 Verificando su acceso en la base de datos..."
    )
    
    await update.message.reply_text(welcome_html, parse_mode="HTML")

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

async def pedir_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el CI y pide el tipo de cliente"""
    context.user_data['ci'] = update.message.text
    
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

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación"""
    await update.message.reply_text(
        "Acción cancelada. 👋",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

if __name__ == '__main__':
    if not TOKEN:
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BOTONES_INICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_decision_inicio)],
            NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pedir_ci)],
            CI: [MessageHandler(filters.TEXT & ~filters.COMMAND, pedir_tipo)],
            TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalizar_registro)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

# ==============================================================================
# BOT TELEGRAM - SAAS LEGAL
# ==============================================================================
# Este bot permite a los usuarios registrarse, ver planes de membresía,
# seleccionar especialistas y reportar pagos mediante carga de vouchers.
# 
# Tecnologías: python-telegram-bot, httpx, hupper (para auto-reload)
# ==============================================================================

import os
import logging
import httpx
import asyncio
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

# ------------------------------------------------------------------------------
# 1. CONFIGURACIÓN Y VARIABLES DE ENTORNO
# ------------------------------------------------------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("LARAVEL_API_URL")
RAG_URL = os.getenv("RAG_URL", "http://rag-core:8000")

# Sticker enviado al iniciar el bot para una experiencia más visual
STICKER_BIENVENIDA = "assets/img/sticker_animado_final.webm"

# Definición de Estados para la Máquina de Estados (ConversationHandler)
(
    BOTONES_INICIO, 
    NOMBRE, 
    CI, 
    TELEFONO, 
    CIUDAD, 
    TIPO, 
    SELECCION_PLAN, 
    GESTION_SUSCRIPCION, 
    SELECCION_CATEGORIAS, 
    ESPERANDO_VOUCHER 
) = range(10)

# ------------------------------------------------------------------------------
# 2. FUNCIONES DE REGISTRO (FLUJO INICIAL)
# ------------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Punto de entrada principal del bot.
    - Verifica si el usuario ya existe en la base de datos de Laravel.
    - Si existe, muestra su estado actual.
    - Si no existe, inicia el proceso de registro.
    """
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name
    
    logging.info(f"Comando /start recibido de {first_name} (ID: {telegram_id})")

    context.user_data.clear()

    # Mensaje inicial de bienvenida
    welcome_html = (
        f"⚖️ <b>Bienvenido, {first_name}</b>\n"
        f"<i>Iniciando sistema de justicia digital...</i>\n\n"
        f"🔍 Verificando su acceso en la base de datos..."
    )
    
    await update.message.reply_text(welcome_html, parse_mode="HTML")

    # Envío de sticker animado
    try:
        if os.path.exists(STICKER_BIENVENIDA):
            with open(STICKER_BIENVENIDA, 'rb') as sticker:
                await update.message.reply_sticker(sticker=sticker)
    except Exception as e:
        logging.error(f"Error enviando Sticker: {e}")

    # Consulta a la API para verificar cliente
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
                # Usuario no registrado
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
    """Maneja la decisión de iniciar registro o cancelar."""
    decision = update.message.text

    if decision == '📝 Iniciar Registro':
        await update.message.reply_text(
            "✨ <b>¡Excelente decisión!</b>\n\nComencemos. Por favor, escribe tu <b>Nombre Completo</b>:",
            parse_mode="HTML", reply_markup=ReplyKeyboardRemove()
        )
        return NOMBRE
    else:
        await update.message.reply_text("Entendido. 👋", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def pedir_ci(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura el nombre y solicita el CI."""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("🤝 Gracias.\n\nAhora, por favor ingresa tu <b>CI</b>:", parse_mode="HTML")
    return CI

async def pedir_telefono(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura el CI y solicita el teléfono."""
    context.user_data['ci'] = update.message.text
    await update.message.reply_text("📱 Ahora, ingresa tu <b>Número de Teléfono</b>:", parse_mode="HTML")
    return TELEFONO

async def pedir_ciudad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura el teléfono y despliega teclado de ciudades."""
    context.user_data['telefono'] = update.message.text
    ciudades = [['La Paz', 'El Alto', 'Santa Cruz'], ['Cochabamba', 'Oruro', 'Potosí'], ['Tarija', 'Sucre', 'Trinidad'], ['Cobija']]
    await update.message.reply_text("🌆 <b>¿En qué ciudad te encuentras actualmente?</b>", parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(ciudades, one_time_keyboard=True, resize_keyboard=True))
    return CIUDAD

async def pedir_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Captura la ciudad y solicita el perfil profesional."""
    context.user_data['city'] = update.message.text
    reply_keyboard = [['Estudiante', 'Abogado', 'Particular']]
    await update.message.reply_text("📍 <b>Último paso</b>\n\n¿Cuál es tu perfil profesional?", parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return TIPO

async def finalizar_registro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía todos los datos recolectados a la API de Laravel para crear el usuario."""
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
                await update.message.reply_text("🎉 <b>¡Cuenta creada!</b>\n\nUsa /planes para elegir tu membresía.", parse_mode="HTML")
            else:
                await update.message.reply_text("❌ No pudimos guardar tus datos.", parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error en registro: {e}")
        await update.message.reply_text("❌ Error de comunicación.", parse_mode="HTML")

    return ConversationHandler.END

# ------------------------------------------------------------------------------
# 3. GESTIÓN DE MEMBRESÍAS Y PLANES
# ------------------------------------------------------------------------------

async def mostrar_planes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /planes. 
    Muestra la suscripción actual o la lista de planes disponibles.
    """
    telegram_id = update.effective_user.id
    
    try:
        async with httpx.AsyncClient() as client:
            check_response = await client.get(f"{API_URL}/bot/check-client/{telegram_id}")
            check_data = check_response.json()
            
            if not check_data.get('exists'):
                await update.message.reply_text("⚠️ Primero debes registrarte (/start).", parse_mode="HTML")
                return ConversationHandler.END
            
            current_sub = check_data.get('current_subscription')
            
            # Si tiene una suscripción pendiente o activa, mostramos gestión
            if current_sub:
                plan_name = current_sub['membership']['name']
                plan_price = current_sub['membership']['price']
                status = current_sub['status']
                context.user_data['current_subscription'] = current_sub
                
                if status == 'pending_payment':
                    msg = (f"💳 <b>Suscripción Pendiente</b>\n\nPlan: <b>{plan_name}</b>\n"
                           f"💰 Precio: <code>{plan_price} BOB</code>\n🔴 Estado: <b>Pendiente de Pago</b>\n\n"
                           f"¿Qué deseas hacer?")
                    keyboard = [['💳 Pagar Ahora'], ['🔄 Cambiar Plan'], ['❌ Cancelar Suscripción']]
                elif status == 'active':
                    msg = (f"✅ <b>Suscripción Activa</b>\n\nTu plan <b>{plan_name}</b> está activo.\n"
                           f"💰 Precio: <code>{plan_price} BOB</code>\n\n¿Qué deseas hacer?")
                    keyboard = [['📊 Ver Detalles'], ['❌ Cancelar Suscripción']]
                else:
                    return await mostrar_lista_planes(update, context, client)
                
                await update.message.reply_text(msg, parse_mode="HTML", 
                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
                return GESTION_SUSCRIPCION
            else:
                # No tiene suscripción, mostrar lista de planes
                return await mostrar_lista_planes(update, context, client)
    except Exception as e:
        logging.error(f"Error en mostrar_planes: {e}")
        await update.message.reply_text("❌ Error de servidor.", parse_mode="HTML")
        return ConversationHandler.END

async def mostrar_lista_planes(update: Update, context: ContextTypes.DEFAULT_TYPE, client):
    """Obtiene y despliega las membresías activas desde la API."""
    response = await client.get(f"{API_URL}/bot/memberships")
    data = response.json()
    memberships = data.get('memberships', [])
    
    context.user_data['memberships'] = memberships
    msg = "💎 <b>Planes de Membresía Disponibles</b>\n\n"
    keyboard = []
    for plan in memberships:
        msg += f"🔹 <b>{plan['name']}</b>\n💰 {plan['price']} BOB | Límite: {plan['daily_limit']}\n\n"
        keyboard.append([plan['name']])
    
    keyboard.append(["❌ Cancelar"])
    await update.message.reply_text(msg + "Elija su plan:", parse_mode="HTML", 
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return SELECCION_PLAN

async def procesar_seleccion_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia el flujo de selección de categorías basado en el plan elegido.
    - Plan Estudiante: Se asigna automáticamente la categoría correspondiente.
    - Otros Planes: Inicia flujo SECUENCIAL (Pregunta 1 a la vez).
    """
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
            
            # --- Lógica Especial para Estudiantes ---
            if "Estudiante" in plan['name']:
                est_cat = next((c for c in categories if "Estudiante" in c['name']), None)
                if est_cat:
                    context.user_data['selected_categories'] = [est_cat['id']]
                    await update.message.reply_text("📚 <b>Plan Estudiante:</b> Se ha asignado automáticamente la categoría Estudiante.", parse_mode="HTML")
                    return await finalizar_suscripcion_con_categorias(update, context)
                else:
                    await update.message.reply_text("❌ Error: Categoría Estudiante no encontrada.")
                    return ConversationHandler.END

            # --- Flujo Secuencial para Profesionales/Particulares ---
            context.user_data['selection_step'] = 1
            return await pedir_siguiente_categoria(update, context)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("❌ Error de comunicación.")
        return ConversationHandler.END

async def pedir_siguiente_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pregunta por la siguiente categoría según el límite del plan (max_specialists)."""
    plan = context.user_data['selected_plan']
    step = context.user_data['selection_step']
    available = context.user_data['available_categories']
    selected_ids = context.user_data['selected_categories']

    # Si ya seleccionó el máximo permitido, finalizar
    if step > plan['max_specialists']:
        return await finalizar_suscripcion_con_categorias(update, context)

    msg = f"🎯 <b>Plan: {plan['name']}</b>\nSeleccione su especialista <b>{step}/{plan['max_specialists']}</b>:"
    
    # Filtrar categorías que no han sido seleccionadas aún
    keyboard = [[cat['name']] for cat in available if cat['id'] not in selected_ids]
    keyboard.append(["❌ Cancelar"])
    
    await update.message.reply_text(msg, parse_mode="HTML", 
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return SELECCION_CATEGORIAS

async def manejar_seleccion_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa la categoría elegida en el paso actual."""
    seleccion = update.message.text
    available = context.user_data['available_categories']
    selected = context.user_data['selected_categories']
    
    if seleccion == "❌ Cancelar":
        await update.message.reply_text("Acción cancelada.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    category = next((c for c in available if c['name'] == seleccion), None)
    if not category:
        await update.message.reply_text("Opción no válida.")
        return await pedir_siguiente_categoria(update, context)
    
    selected.append(category['id'])
    context.user_data['selection_step'] += 1
    
    return await pedir_siguiente_categoria(update, context)

async def finalizar_suscripcion_con_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda la suscripción y las categorías seleccionadas en Laravel."""
    telegram_id = update.effective_user.id
    plan = context.user_data['selected_plan']
    categories = context.user_data['selected_categories']
    
    await update.message.reply_text("⏳ <b>Procesando su suscripción...</b>", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())

    try:
        async with httpx.AsyncClient() as client:
            # 1. Crear registro de suscripción
            sub_resp = await client.post(f"{API_URL}/bot/subscribe", json={"telegram_id": telegram_id, "membership_id": plan['id']})
            if sub_resp.status_code != 200:
                return await update.message.reply_text("❌ Error al iniciar suscripción.")

            subscription = sub_resp.json().get('subscription')
            
            # 2. Asociar categorías a la suscripción
            cat_resp = await client.post(f"{API_URL}/bot/set-categories", 
                json={"subscription_id": subscription['id'], "category_ids": categories})
            
            if cat_resp.status_code == 200:
                await update.message.reply_text(f"🎉 <b>¡Registro Exitoso!</b>\n\nPlan: <b>{plan['name']}</b>.\n"
                    "Estado: <b>Pendiente de Pago</b>.\n\nUsa /planes para ver opciones de pago.", parse_mode="HTML")
            else:
                await update.message.reply_text("❌ Error al guardar especialidades.")
    except Exception as e:
        logging.error(f"Error crítico: {e}")
        await update.message.reply_text("❌ Error de comunicación central.")

    return ConversationHandler.END

# ------------------------------------------------------------------------------
# 4. FLUJO DE PAGO Y VOUCHER
# ------------------------------------------------------------------------------

async def manejar_gestion_suscripcion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja las acciones de una suscripción ya existente (Pagar, Cancelar, Ver)."""
    opcion = update.message.text
    telegram_id = update.effective_user.id
    current_sub = context.user_data.get('current_subscription')

    if opcion == '💳 Pagar Ahora':
        # Muestra datos bancarios y el código QR de pago obtenido del administrador
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{API_URL}/bot/settings")
                settings = resp.json()
                
                msg = (f"💳 <b>Datos de Pago</b>\n\n👤 <b>Contacto:</b> {settings['contact_name']}\n"
                       f"🏦 <b>Datos Bancarios:</b>\n{settings['bank_details']}\n\n"
                       f"📱 <b>Soporte:</b> {settings['telegram_user']}\n\n"
                       "Escanea el siguiente QR para realizar el pago:")
                
                reply_markup = ReplyKeyboardMarkup([['✅ Pago Realizado'], ['❌ Volver']], one_time_keyboard=True, resize_keyboard=True)

                qr_url = settings.get('qr_url')
                if qr_url:
                    # Ajuste de URL para entornos Docker
                    if "localhost" in qr_url or "127.0.0.1" in qr_url:
                        qr_url = qr_url.replace("localhost", "saas_legal_api").replace("127.0.0.1", "saas_legal_api")
                    
                    try:
                        qr_resp = await client.get(qr_url)
                        if qr_resp.status_code == 200:
                            from io import BytesIO
                            photo = BytesIO(qr_resp.content)
                            photo.name = "qr_pago.png"
                            await update.message.reply_photo(photo=photo, caption=msg, parse_mode="HTML", reply_markup=reply_markup)
                        else:
                            await update.message.reply_text(msg + "\n⚠️ QR no disponible.", parse_mode="HTML", reply_markup=reply_markup)
                    except:
                        await update.message.reply_text(msg + "\n⚠️ Error cargando QR.", parse_mode="HTML", reply_markup=reply_markup)
                else:
                    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=reply_markup)
                return GESTION_SUSCRIPCION
        except:
            await update.message.reply_text("❌ Error al obtener datos de pago.")
            return ConversationHandler.END

    elif opcion == '✅ Pago Realizado':
        # Solicita la foto del comprobante
        await update.message.reply_text("📸 <b>¡Excelente!</b>\n\nPor favor, <b>envía una foto de tu comprobante o voucher</b>.",
            parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        return ESPERANDO_VOUCHER

    elif opcion == '❌ Volver':
        return await mostrar_planes(update, context)

    elif opcion == '📊 Ver Detalles':
        if current_sub:
            plan = current_sub['membership']
            await update.message.reply_text(f"📊 <b>Detalles</b>\n\nPlan: <b>{plan['name']}</b>\nLímite: {plan['daily_limit']}\nEspecialistas: {plan['max_specialists']}", 
                parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    return ConversationHandler.END

async def manejar_envio_voucher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Recibe la imagen del voucher.
    1. Sube la imagen a la API.
    2. Notifica al administrador vía Telegram enviándole la misma foto.
    """
    telegram_id = update.effective_user.id
    current_sub = context.user_data.get('current_subscription')
    
    if not update.message.photo:
        await update.message.reply_text("⚠️ Por favor, envía una <b>foto</b>.")
        return ESPERANDO_VOUCHER

    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    
    await update.message.reply_text("⏳ <b>Subiendo comprobante...</b>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient() as client:
            # Subida a Laravel
            files = {'voucher': ('voucher.jpg', bytes(photo_bytes), 'image/jpeg')}
            resp = await client.post(f"{API_URL}/bot/upload-voucher", data={'subscription_id': current_sub['id']}, files=files)
            
            if resp.status_code != 200:
                return await update.message.reply_text("❌ Error al subir el voucher.")

            # Notificación al Administrador
            resp_settings = await client.get(f"{API_URL}/bot/settings")
            settings = resp_settings.json()
            admin_id = settings.get('admin_telegram_id')

            if admin_id:
                msg_admin = (f"🔔 <b>¡Nuevo Voucher!</b>\n\n👤 <b>Cliente:</b> {update.effective_user.first_name}\n"
                             f"📦 <b>Plan:</b> {current_sub['membership']['name']}\n🆔 <b>ID:</b> <code>{telegram_id}</code>")
                try:
                    from io import BytesIO
                    await context.bot.send_photo(chat_id=admin_id, photo=BytesIO(photo_bytes), caption=msg_admin, parse_mode="HTML")
                except:
                    logging.error("No se pudo notificar al admin.")

            await update.message.reply_text("✅ <b>Comprobante Recibido.</b>\nVerificaremos tu pago a la brevedad.", parse_mode="HTML")
            return ConversationHandler.END
    except:
        await update.message.reply_text("❌ Error de comunicación.")
        return ESPERANDO_VOUCHER

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fallback para cancelar cualquier conversación activa con /cancelar."""
    await update.message.reply_text("Acción cancelada. 👋", parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def consultar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /consulta <pregunta>.
    Busca respuestas en los documentos legales basados en la suscripción del usuario.
    """
    telegram_id = update.effective_user.id
    pregunta = " ".join(context.args) if context.args else ""

    if not pregunta:
        await update.message.reply_text("❓ <b>¿Qué deseas consultar?</b>\nUsa: <code>/consulta tu pregunta aquí</code>", parse_mode="HTML")
        return

    await update.message.reply_text("🔍 <b>Consultando inteligencia legal...</b>", parse_mode="HTML")

    try:
        async with httpx.AsyncClient() as client:
            # 1. Verificar suscripción y categorías permitidas
            resp_client = await client.get(f"{API_URL}/bot/check-client/{telegram_id}")
            data_client = resp_client.json()

            if not data_client.get('exists') or not data_client.get('current_subscription'):
                await update.message.reply_text("⚠️ Necesitas una suscripción activa para realizar consultas legal. Usa /planes.", parse_mode="HTML")
                return

            sub = data_client['current_subscription']
            if sub['status'] != 'active':
                await update.message.reply_text(f"⚠️ Tu suscripción está <b>{sub['status']}</b>. Debes estar activo para consultar.", parse_mode="HTML")
                return

            # Obtener IDs de categorías permitidas para este usuario (desde la tabla pivote de su suscripción)
            category_ids = [c['id'] for c in sub.get('categories', [])]
            logging.info(f"Consulta de {telegram_id} - Pregunta: '{pregunta}' - Categorías: {category_ids}")

            # 2. Llamar al servicio RAG
            payload = {
                "question": pregunta,
                "category_ids": category_ids,
                "status": "active",
                "top_k": 10
            }

            resp_rag = await client.post(f"{RAG_URL}/query", json=payload, timeout=30.0)
            
            if resp_rag.status_code == 200:
                data_rag = resp_rag.json()
                logging.info(f"Respuesta RAG recibida. Contextos encontrados: {data_rag.get('num_contexts')}")
                answer = data_rag.get('answer', "No pude encontrar una respuesta clara.")
                
                await update.message.reply_text(f"⚖️ <b>Asesoría Legal AI:</b>\n\n{answer}", parse_mode="HTML")
            else:
                logging.error(f"Error RAG: {resp_rag.status_code} - {resp_rag.text}")
                await update.message.reply_text("❌ El cerebro de la IA no respondió. Por favor, intenta más tarde.", parse_mode="HTML")

    except Exception as e:
        logging.error(f"Error en consulta RAG: {e}")
        await update.message.reply_text("❌ Error de conexión con el sistema de justicia digital.", parse_mode="HTML")

# ------------------------------------------------------------------------------
# 5. INICIALIZACIÓN DEL BOT
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    if not TOKEN:
        logging.error("TELEGRAM_TOKEN no encontrado en .env")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    
    # Manejador para el Flujo de Registro
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

    # Manejador para el Flujo de Planes y Pagos
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
    app.add_handler(CommandHandler("consulta", consultar))
    
    # Soporte para entornos asíncronos
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    logging.info("Iniciando Bot...")
    app.run_polling()

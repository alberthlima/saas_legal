# 🤖 Guía Educativa: Bot de Telegram Legal AI

Esta guía te ayudará a entender cómo funciona el bot de Telegram y qué hace cada parte del código en Python. ¡No te preocupes si no sabes mucho de Python, aquí lo explicamos paso a paso!

---

## 📂 Archivos en esta carpeta

1.  **`main.py`**: Es el archivo principal donde está toda la "lógica" (lo que el bot hace y dice).
2.  **`Dockerfile`**: Es la "receta" para que Docker sepa cómo instalar Python y las librerías necesarias.
3.  **`requirements.txt`**: Una lista de las herramientas que el bot necesita descargar (como `httpx` para hablar con Internet).
4.  **`assets/`**: Carpeta que contiene recursos visuales como el sticker animado de bienvenida.

---

## 🔍 Explicación del Código (`main.py`)

El archivo se divide en secciones clave que manejan diferentes "conversaciones":

### 1. Las Importaciones y Configuración (Líneas 1-54)

Aquí cargamos las herramientas (`httpx`, `telegram`, `dotenv`) y definimos los **Estados**. Los estados son como "marcadores de posición" para que el bot recuerde en qué parte de la charla está cada usuario (ej: `NOMBRE`, `SELECCION_PLAN`, `ESPERANDO_VOUCHER`).

### 2. Flujo de Registro Inicial (Líneas 56-201)

Cuando escribes `/start`, el bot:

- **Saluda con Estilo**: Envía un sticker animado (`assets/img/sticker_animado_final.webm`).
- **Consulta a Laravel**: Pregunta si ya existes en la base de datos.
- **Registro Paso a Paso**: Si eres nuevo, te pide Nombre, CI, Teléfono, Ciudad y Tipo de Cliente, guardando todo en Laravel al final.

### 3. Selección de Planes y Especialidades (Líneas 203-389)

Al usar `/planes`, el bot permite elegir una membresía. Lo nuevo y genial aquí es:

- **Límites Dinámicos**: Si un plan permite 3 especialistas, el bot te preguntará 3 veces qué categorías deseas, una por una.
- **Lógica para Estudiantes**: Si eliges el plan "Estudiante", el bot te asigna automáticamente la categoría de estudiante sin preguntar.
- **Guardado Relacional**: Las categorías elegidas se guardan vinculadas a tu suscripción en Laravel.

### 4. Pagos y Configuraciones Globales (Líneas 392-455)

Cuando decides pagar (`💳 Pagar Ahora`):

- **Datos en Tiempo Real**: El bot no tiene los datos bancarios escritos en el código ("hardcoded"). Los pide a la API de Laravel (tabla `settings`).
- **QR Dinámico**: Si el administrador cambia la imagen del QR en el panel web, el bot mostrará automáticamente el nuevo QR al cliente.
- **Multicloud Ready**: El código ajusta automáticamente las URLs si detecta que está corriendo dentro de Docker.

### 5. Carga de Voucher y Notificación al Admin (Líneas 457-502)

Una vez que el usuario hace el pago:

- **Envío de Foto**: El usuario sube una foto de su comprobante.
- **Subida a Laravel**: El bot envía la imagen a la API para que quede registrada en la suscripción.
- **Alerta al Administrador**: El bot busca el `admin_telegram_id` en las configuraciones y le reenvía la foto del voucher junto con los datos del cliente para que pueda aprobarlo desde el panel.

### 6. El Corazón del Bot (Líneas 513-558)

Aquí es donde se "enciende" todo. Usamos dos `ConversationHandler`:

1. Uno para el **Registro** (comando `/start`).
2. Otro para los **Planes y Pagos** (comando `/planes`).

---

## 🌐 Integración con la API Central

El bot es un "cliente" de la API de Laravel. Toda la información importante (clientes, precios, categorías, configuración de banco) vive en la base de datos central. Esto permite que el sistema sea escalable y fácil de administrar desde la web.

---

## 🛠️ Comandos Útiles para ti

Si quieres ver qué está "pensando" el bot mientras hablas con él:

```bash
# Ver los mensajes del bot en tiempo real
docker-compose logs -f bot
```

Si haces un cambio en el código `main.py`:

```bash
# Reiniciar el bot para que lea los cambios
docker-compose restart bot
```

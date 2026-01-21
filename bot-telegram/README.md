# 🤖 Guía Educativa: Bot de Telegram Legal AI

Esta guía te ayudará a entender cómo funciona el bot de Telegram y qué hace cada parte del código en Python. ¡No te preocupes si no sabes mucho de Python, aquí lo explicamos paso a paso!

---

## 📂 Archivos en esta carpeta

1.  **`main.py`**: Es el archivo principal donde está toda la "lógica" (lo que el bot hace y dice).
2.  **`Dockerfile`**: Es como la "receta" para que Docker sepa cómo instalar Python y las librerías necesarias.
3.  **`requirements.txt`**: Una lista simple de las herramientas que el bot necesita descargar (como `httpx` para hablar con Internet).

---

## 🔍 Explicación del Código (`main.py`)

El archivo se divide en secciones clave:

### 1. Las Importaciones (Líneas 1-14)

```python
import os
import logging
import httpx
from telegram import Update, ...
```

Aquí le decimos a Python qué herramientas queremos usar.

- `os`: Para leer el Token desde el archivo `.env`.
- `httpx`: Es el cartero que lleva y trae mensajes entre el Bot y tu API de Laravel.
- `telegram`: Es la librería oficial de Telegram que nos permite recibir mensajes.

### 2. Gestión de Estados (Líneas 27-28)

```python
NOMBRE, CI, TIPO = range(3)
```

Como el registro es un proceso de varios pasos (primero nombre, luego CI, etc.), usamos "estados". Es como un semáforo: el bot sabe en qué paso está cada usuario.

### 3. El Comando `/start` (Líneas 31-62)

Es el primer contacto. Aquí el Bot hace algo muy importante:

- **Consulta a Laravel**: Antes de saludar, le pregunta a tu API: `¿Conoces a este ID de Telegram?`.
- **Decisión**:
  - Si Laravel dice "Sí", el bot te da la bienvenida y termina.
  - Si dice "No", el bot dice "¡Eres nuevo!" y activa el flujo de registro devolviendo el estado `NOMBRE`.

### 4. Recolección de Datos (Líneas 64-81)

Funciones como `pedir_ci` y `pedir_tipo`:

- Guardan lo que escribiste en una "mochila" temporal llamada `context.user_data`.
- Te preguntan lo siguiente.
- En el paso del **Tipo de Cliente**, el bot crea botones elegantes en tu celular usando `ReplyKeyboardMarkup`.

### 5. Finalizando el Registro (Líneas 83-111)

Cuando ya tiene todo, ocurre la magia de la integración:

- El bot empaqueta tu Nombre, CI y Tipo en un paquete (JSON).
- Envía un `POST` (petición de guardado) al endpoint `/api/bot/register-client` de Laravel.
- Laravel lo guarda en la base de datos MySQL y le responde al bot "OK".

### 6. El Corazón del Bot (Líneas 124-148)

```python
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
```

Aquí es donde el bot realmente se enciende. Configuramos el `ConversationHandler`, que es el director de orquesta que dice: "Si el usuario está en el paso NOMBRE y escribe algo, mándalo a la función `pedir_ci`".

---

## 🌐 ¿Cómo se conecta con Laravel?

En el archivo `docker-compose.yml`, configuramos esta línea:
`LARAVEL_API_URL: http://saas_legal_api:8000/api`

Esto es genial porque:

- **No necesitas IP**: Docker hace que el Bot reconozca el nombre `saas_legal_api` como si fuera una dirección web interna.
- **Seguridad**: La base de datos MySQL está protegida; solo Laravel habla con ella, y el Bot solo habla con Laravel.

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

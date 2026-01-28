# Guía de despliegue local (sin Docker)

Esta guía explica cómo correr **todo el stack** en tu PC local sin Docker:

- Qdrant (motor vectorial)
- `rag-core` (servicio Python con FastAPI para ingest y RAG)
- `api-panel` (API PHP / Laravel)

> Requisitos previos: ya tienes Git, PHP, Composer, Node y Python instalados.

---

## 1. Clonar o actualizar el proyecto

```bash
cd C:\ruta\donde\guardas\proyectos
git clone https://TU_REPO.git saas_legal   # si aún no lo clonaste
cd saas_legal
git pull                                  # para traer los últimos cambios
```

La estructura relevante:

- `saas_legal/rag-core` → servicio Python (FastAPI + Qdrant + OpenAI)
- `saas_legal/api-panel` → API Laravel (panel / backend del sistema)

---

## 2. Instalar y ejecutar Qdrant localmente

### 2.1. Instalar Qdrant

Opción recomendada en Windows: **binario oficial**.

1. Ir a la página de Qdrant (Downloads) y descargar el binario para Windows.
2. Descomprimir en una carpeta, por ejemplo:

```text
C:\qdrant
```

3. Dentro tendrás un ejecutable tipo `qdrant.exe`.

### 2.2. Ejecutar Qdrant

En una consola **separada**:

```bash
cd C:\qdrant
qdrant.exe
```

Por defecto Qdrant expone:

- HTTP: `http://127.0.0.1:6333`

No cierres esta consola mientras uses el sistema.

---

## 3. Configurar variables de entorno (entorno local)

Crea un archivo `.env` en `saas_legal/rag-core` (o revisa el que ya tengas) con al menos:

```env
# Qdrant
QDRANT_HOST=127.0.0.1
QDRANT_PORT=6333
QDRANT_COLLECTION=legal_docs

# OpenAI
OPENAI_API_KEY=TU_API_KEY
OPENAI_MODEL=gpt-4o-mini
```

En `api-panel` (Laravel) revisa tu `.env` para apuntar al servicio `rag-core`, por ejemplo:

```env
RAG_CORE_URL=http://127.0.0.1:8000
```

(Usa la variable/clave que ya tengas definida en tu config de Laravel.)

---

## 4. Levantar `rag-core` (Python / FastAPI)

### 4.1. Crear entorno virtual e instalar dependencias

En una nueva consola:

```bash
cd d:\SISTEMAS\PRUEBAS\saas_legal\rag-core

# Crear entorno virtual (Windows)
python -m venv .venv

# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt   # si ya existe
```

Si no tienes `requirements.txt`, puedes generarlo a partir de las librerías usadas (ejemplo aproximado):

```bash
pip install fastapi uvicorn qdrant-client python-dotenv openai llama-index pdfplumber
pip freeze > requirements.txt
```

### 4.2. Ejecutar el servidor FastAPI

Desde la misma consola con el venv activo:

```bash
cd d:\SISTEMAS\PRUEBAS\saas_legal\rag-core
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Deberías ver el servidor corriendo en:

- `http://127.0.0.1:8000`
- Documentación automática: `http://127.0.0.1:8000/docs`

Endpoints clave:

- `POST /ingest-pdf` → ingesta de PDFs hacia Qdrant
- `POST /query` → consultas RAG
- `GET /documents` → listar documentos
- `DELETE /admin/qdrant/collection` → **borrar toda la colección**

---

## 5. Levantar `api-panel` (Laravel)

### 5.1. Instalar dependencias PHP

En otra consola:

```bash
cd d:\SISTEMAS\PRUEBAS\saas_legal\api-panel
composer install
```

Copia `.env.example` a `.env` si aún no lo hiciste:

```bash
cp .env.example .env   # en PowerShell puedes usar: copy .env.example .env
```

Configura en `.env`:

- Conexión a base de datos local (MySQL, MariaDB, etc.).
- URL del servicio `rag-core` (por ejemplo `RAG_CORE_URL=http://127.0.0.1:8000`).

Luego genera la clave de la app y corre migraciones:

```bash
php artisan key:generate
php artisan migrate
```

### 5.2. Levantar servidor de desarrollo Laravel

```bash
php artisan serve --host=0.0.0.0 --port=8001
```

Tu API Laravel quedará en, por ejemplo:

- `http://127.0.0.1:8001`

Desde aquí tu controlador `DocumentController` llamará a `rag-core` usando la URL configurada en `.env`.

---

## 6. Flujo completo en local

1. **Iniciar Qdrant** en una consola:

   ```bash
   cd C:\qdrant
   qdrant.exe
   ```

2. **Iniciar `rag-core`** (FastAPI) en otra consola:

   ```bash
   cd d:\SISTEMAS\PRUEBAS\saas_legal\rag-core
   .venv\Scripts\activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Iniciar `api-panel`** (Laravel) en otra consola:

   ```bash
   cd d:\SISTEMAS\PRUEBAS\saas_legal\api-panel
   php artisan serve --host=0.0.0.0 --port=8001
   ```

4. **Usar el sistema** (desde Postman o desde el frontend que tengas):

   - Crear/editar un documento en tu sistema (Laravel), subir el PDF.
   - El `DocumentController` enviará la petición a `rag-core /ingest-pdf` con:

     ```json
     {
       "pdf_path": "ruta/archivo.pdf",
       "doc_id": "ID en base de datos",
       "name": "Nombre legible",
       "description": "Descripción del documento",
       "category_ids": [1, 2],
       "status": "active",
       "replace_existing": true
     }
     ```

   - `rag-core` leerá el PDF desde su carpeta `pdfs/`, generará chunks, embeddings y los guardará en Qdrant.

5. **Consultar**

   - Puedes llamar desde Laravel al endpoint `/query` de `rag-core` o probar directo en `http://127.0.0.1:8000/docs`.

---

## 7. Notas sobre la carpeta `pdfs`

En `rag-core/main.py`, la ruta del PDF se construye como:

```python
pdf_full_path = Path("pdfs") / request.pdf_path
```

Eso significa que, en tu entorno local:

- Debes colocar los PDFs en `d:\SISTEMAS\PRUEBAS\saas_legal\rag-core\pdfs`.
- `request.pdf_path` debe ser el nombre relativo dentro de esa carpeta (ej. `"mi_documento.pdf"` o `"cliente/contrato.pdf"`).

Asegúrate de replicar esta estructura cuando copies los archivos desde tu entorno de desarrollo actual.

---

## 8. Resumen rápido (checklist)

- [ ] Qdrant instalado y corriendo en `127.0.0.1:6333`.
- [ ] `.env` de `rag-core` configurado (`QDRANT_*`, `OPENAI_API_KEY`).
- [ ] Entorno virtual Python creado e instalado `requirements.txt`.
- [ ] `uvicorn main:app --reload --port 8000` funcionando.
- [ ] `.env` de Laravel apuntando a `RAG_CORE_URL` correcto.
- [ ] `php artisan serve --port 8001` funcionando.
- [ ] PDFs copiados a `rag-core/pdfs`.
- [ ] Ingesta probada vía API del panel o vía `/ingest-pdf` directo.

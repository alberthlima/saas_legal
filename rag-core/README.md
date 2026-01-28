# 🧠 RAG-Core: Sistema de Recuperación y Generación para Legal-AI

Este es el motor central de Inteligencia Artificial encargado de procesar documentos legales (PDF), indexarlos en una base de datos vectorial y responder preguntas basadas en su contenido.

## 🏗️ Arquitectura del Sistema

El sistema utiliza una arquitectura **RAG (Retrieval-Augmented Generation)** que se divide en tres capas principales:

1.  **Capa de Ingesta (Ingest)**:
    - **Carga**: Se leen los PDFs y se extrae el texto usando `llama-index`.
    - **Chunking**: El texto se divide en fragmentos (chunks) para que la IA los procese mejor.
    - **Embeddings**: Cada fragmento se convierte en un vector numérico usando el modelo `text-embedding-3-small` de OpenAI.
2.  **Capa de Almacenamiento (Vector DB)**:
    - Se utiliza **Qdrant** para almacenar los vectores y sus metadatos (categoría, área, doc_id).
    - Permite realizar búsquedas por "similitud semántica" (busca ideas, no solo palabras exactas).
3.  **Capa de Consulta (Query)**:
    - Cuando el usuario pregunta, el sistema busca los fragmentos más relevantes en Qdrant.
    - Los fragmentos encontrados se envían a **GPT-4o-mini** como "contexto" para generar la respuesta final.

## 📁 Estructura de Archivos

- `main.py`: Punto de entrada de la API (FastAPI). Define los endpoints para ingesta y consulta.
- `vector_db.py`: Gestiona la conexión y operaciones con la base de datos **Qdrant**.
- `data_loader.py`: Contiene la lógica para procesar PDFs y generar embeddings.
- `custom_types.py`: Definiciones de esquemas de datos.

## 🚀 Instalación y Despliegue

### Requisitos

- Docker y Docker Compose.
- OpenAI API Key.

### Despliegue con Docker

El proyecto incluye un `Dockerfile` y un `docker-compose.yaml` para facilitar el despliegue.

```bash
# 1. Configurar variables de entorno en .env
OPENAI_API_KEY=tu_clave_aqui
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# 2. Levantar el servicio
docker compose up -d
```

## 📡 Guía de Endpoints (API)

### 1. Ingestar un PDF

`POST /ingest-pdf`
Envía la orden para que el sistema procese un archivo PDF que ya esté en la carpeta `pdfs`.

**Request Body:**

```json
{
  "pdf_path": "ley_trabajo.pdf",
  "doc_id": "L001",
  "area": "Laboral",
  "category": "Leyes",
  "replace_existing": true
}
```

### 2. Consultar al asistente

`POST /query`
Realiza una pregunta al sistema filtrando por área o documento específico.

**Request Body:**

```json
{
  "question": "¿Cuál es la indemnización por despido injustificado?",
  "area": "Laboral",
  "top_k": 3
}
```

### 3. Listar documentos

`GET /documents`
Obtiene la lista de todos los documentos indexados en el sistema.

---

> [!TIP]
> **Integración con Laravel**: Cuando subes un archivo en el panel administrativo, Laravel debe disparar una llamada a `/ingest-pdf` para sincronizar el documento con este servicio.

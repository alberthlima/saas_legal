import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
import os
from datetime import datetime
from pathlib import Path
from openai import OpenAI

from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage

load_dotenv()

app = FastAPI()
logger = logging.getLogger("uvicorn")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Modelos de request
class IngestRequest(BaseModel):
    pdf_path: str
    doc_id: str
    # area y doc_version se mantienen por compatibilidad pero ya no se usan como metadata principal
    area: str = "general"  # Deprecated: se deja por compatibilidad
    doc_version: str = "1.0"  # Se usa solo para la generación de IDs internos
    author: str = None
    category_ids: list[int] = []  # Lista de IDs de categorías
    status: str = "active"
    replace_existing: bool = True
    name: str | None = None
    description: str | None = None


class QueryRequest(BaseModel):
    question: str
    area: str = "general"
    category_ids: list[int] = None  # Filtrar por categorías permitidas
    doc_id: str = None
    status: str = "active"
    top_k: int = 10


@app.post("/ingest-pdf")
async def rag_ingest_pdf(request: IngestRequest):
    """
    PROCESO DE INGESTA:
    1. Localiza el PDF en el servidor.
    2. Si el doc_id ya existe y replace_existing es True, limpia los datos viejos.
    3. Pica el PDF en fragmentos (chunks).
    4. Convierte fragmentos a vectores (OpenAI).
    5. Guarda todo en Qdrant con sus etiquetas (área, categoría).
    """
    try:
        store = QdrantStorage()
        
        # 1. Construir la ruta completa del PDF usando pathlib
        pdf_full_path = Path("pdfs") / request.pdf_path
        
        # Verificar si el archivo existe antes de proceder
        if not pdf_full_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Archivo PDF no encontrado: {request.pdf_path} (buscado en: {pdf_full_path})"
            )
        
        if not pdf_full_path.is_file():
            raise HTTPException(
                status_code=400,
                detail=f"La ruta no es un archivo válido: {request.pdf_path}"
            )
        
        # 2. Si se debe reemplazar, eliminar versión anterior
        deleted_count = 0
        if request.replace_existing:
            deleted_count = store.delete_document(request.doc_id)
            logger.info(f"Eliminados {deleted_count} chunks del doc_id: {request.doc_id}")
        
        # 3. Cargar y chunk el PDF (convertir Path a string para compatibilidad)
        chunks = load_and_chunk_pdf(str(pdf_full_path))
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No se pudieron extraer chunks del PDF")
        
        # 4. Generar embeddings
        vecs = embed_texts(chunks)
        
        # 5. Crear IDs únicos para cada chunk
        ids = [
            str(uuid.uuid5(uuid.NAMESPACE_URL, f"{request.doc_id}:v{request.doc_version}:{i}"))
            for i in range(len(chunks))
        ]
        
        # 6. Crear payloads enriquecidos con metadata
        upload_timestamp = datetime.now().isoformat()
        payloads = [
            {
                "text": chunks[i],
                "source": request.pdf_path,
                "doc_id": request.doc_id,
                "category_ids": request.category_ids,
                "upload_date": upload_timestamp,
                "status": request.status,
                "chunk_index": i,
                "metadata": {
                    "author": request.author,
                    "name": request.name,
                    "description": request.description,
                }
            }
            for i in range(len(chunks))
        ]
        
        # 7. Upsert en Qdrant
        store.upsert(ids, vecs, payloads)
        
        return {
            "success": True,
            "ingested": len(chunks),
            "doc_id": request.doc_id,
            "name": request.name,
            "description": request.description,
            "deleted_previous": deleted_count if request.replace_existing else 0,
            "upload_date": upload_timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/query")
async def rag_query(request: QueryRequest):
    """
    PROCESO DE CONSULTA (RAG):
    1. Convierte la pregunta del usuario en un vector.
    2. Busca en Qdrant los fragmentos de PDF más parecidos a la pregunta.
    3. Toma esos fragmentos y se los entrega a GPT-4o-mini.
    4. GPT redacta la respuesta usando solo el "Contexto" entregado.
    """
    try:
        # 1. Generar embedding de la pregunta
        query_vec = embed_texts([request.question])[0]
        
        # 2. Buscar en Qdrant con filtros (traer más resultados para re-ranking)
        store = QdrantStorage()
        found = store.search(
            query_vector=query_vec,
            top_k=request.top_k * 3,  # Traer 3x más para re-ranking
            area=request.area,
            doc_id=request.doc_id,
            status=request.status,
            category_ids=request.category_ids
        )
        
        # 2.5 RE-RANKING: Detectar si la pregunta menciona un artículo específico
        import re
        article_match = re.search(r'art[ií]culo\s+(\d+)', request.question, re.IGNORECASE)
        
        if article_match and found["contexts"]:
            target_article = article_match.group(1)
            logger.info(f"Detectado: Usuario pregunta por Artículo {target_article}")
            
            # Separar contextos que contienen el artículo específico
            exact_matches = []
            other_contexts = []
            
            for ctx in found["contexts"]:
                # Buscar "Artículo X" al inicio del chunk (con o sin tilde)
                if re.search(rf'Art[ií]culo\s+{target_article}[\.\s]', ctx, re.IGNORECASE):
                    exact_matches.append(ctx)
                else:
                    other_contexts.append(ctx)
            
            # Re-ordenar: primero los matches exactos, luego los demás
            found["contexts"] = exact_matches + other_contexts
            logger.info(f"Re-ranking: {len(exact_matches)} matches exactos del Artículo {target_article}")
        
        # Limitar al top_k original
        found["contexts"] = found["contexts"][:request.top_k]
        
        # DEBUG: Imprimir los contextos encontrados
        logger.info(f"Query: {request.question}")
        logger.info(f"Contextos encontrados ({len(found['contexts'])}):")
        for i, ctx in enumerate(found["contexts"]):
            logger.info(f"--- Contexto {i+1} (primeros 100 caracteres) ---")
            logger.info(ctx[:100].replace('\n', ' '))
        
        if not found["contexts"]:
            return {
                "answer": "No se encontró información relevante en los documentos disponibles.",
                "sources": [],
                "doc_ids": [],
                "num_contexts": 0
            }
        
        # 3. Construir contexto para el LLM
        context_block = "\n\n".join(f"- {c}" for c in found["contexts"])
        
        # Eliminar info de área si no es relevante
        user_content = (
            f"Usa el siguiente contexto para responder la pregunta.\n\n"
            f"Contexto:\n{context_block}\n\n"
            f"Pregunta: {request.question}\n\n"
            "Responde de manera concisa usando únicamente el contexto proporcionado."
        )

        # 4. Llamar a OpenAI
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un asistente que responde preguntas basándose únicamente en el contexto proporcionado. Si la información no está en el contexto, indícalo claramente."
                },
                {"role": "user", "content": user_content}
            ],
            max_tokens=1024,
            temperature=0.2
        )

        answer = response.choices[0].message.content.strip()
        
        return {
            "answer": answer,
            "sources": found["sources"],
            "doc_ids": found.get("doc_ids", []),
            "num_contexts": len(found["contexts"]),
            "filters_applied": {
                "area": request.area,
                "doc_id": request.doc_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error querying: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error querying: {str(e)}")


@app.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    """
    Elimina físicamente un documento y todos sus chunks
    """
    try:
        store = QdrantStorage()
        count = store.delete_document(doc_id)
        
        if count == 0:
            raise HTTPException(status_code=404, detail=f"Documento {doc_id} no encontrado")
        
        return {
            "success": True,
            "doc_id": doc_id,
            "chunks_affected": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@app.get("/document/{doc_id}/info")
async def get_document_info(doc_id: str):
    """
    Obtiene información de un documento
    """
    try:
        store = QdrantStorage()
        info = store.get_document_info(doc_id)
        
        if not info:
            raise HTTPException(status_code=404, detail=f"Documento {doc_id} no encontrado")
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/documents")
async def list_documents(area: str = None):
    """
    Lista todos los documentos en la base de datos
    Opcionalmente filtrados por área
    """
    try:
        store = QdrantStorage()
        documents = store.list_documents(area=area)
        
        return {
            "total": len(documents),
            "documents": documents,
            "filtered_by_area": area
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.delete("/admin/qdrant/collection")
async def delete_qdrant_collection():
    try:
        store = QdrantStorage()
        store.delete_all()
        return {"success": True, "message": "Colección de Qdrant eliminada completamente"}
    except Exception as e:
        logger.error(f"Error deleting Qdrant collection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
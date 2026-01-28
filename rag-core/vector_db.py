from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class QdrantStorage:
    def __init__(self, url=None, collection=None, dim=3072):
        # Cargar configuración desde variables de entorno
        if url is None:
            qdrant_host = os.getenv("QDRANT_HOST", "127.0.0.1")
            qdrant_port = os.getenv("QDRANT_PORT", "6333")
            url = f"http://{qdrant_host}:{qdrant_port}"
        
        if collection is None:
            collection = os.getenv("QDRANT_COLLECTION", "docs")
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection
        
        # Crear colección si no existe
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
            logger.info(f"Colección '{self.collection}' creada")

    def delete_all(self) -> None:
        """Elimina completamente la colección actual (todos los puntos)."""
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
            logger.info(f"Colección '{self.collection}' eliminada completamente")

    def upsert(self, ids: List[str], vectors: List[List[float]], payloads: List[Dict], batch_size: int = 200):
        """Inserta o actualiza puntos en la colección en lotes (batches).

        :param ids: Lista de IDs de puntos.
        :param vectors: Lista de vectores (embeddings).
        :param payloads: Lista de payloads asociados a cada punto.
        :param batch_size: Tamaño del lote para enviar a Qdrant.
        """
        total = len(ids)
        if not (len(vectors) == total and len(payloads) == total):
            raise ValueError("Las listas ids, vectors y payloads deben tener el mismo tamaño")

        logger.info(f"Iniciando upsert de {total} puntos en lotes de hasta {batch_size}")

        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            batch_points = [
                PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i])
                for i in range(start, end)
            ]
            self.client.upsert(self.collection, points=batch_points)
            logger.info(f"Upsert de lote {start}-{end - 1} completado ({len(batch_points)} puntos)")

        logger.info(f"Upsert total de {total} puntos completado en lotes")

    def delete_document(self, doc_id: str) -> int:
        """
        Elimina físicamente todos los puntos de un documento
        Retorna la cantidad de puntos eliminados
        """
        # Obtener IDs de los puntos a eliminar
        scroll_result = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=Filter(
                must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
            ),
            limit=10000,  # Ajustar según necesidad
            with_payload=False,
            with_vectors=False
        )
        
        points_to_delete = scroll_result[0]
        
        if not points_to_delete:
            logger.warning(f"No se encontraron puntos para doc_id: {doc_id}")
            return 0
        
        point_ids = [p.id for p in points_to_delete]
        
        # Eliminar puntos
        self.client.delete(
            collection_name=self.collection,
            points_selector=point_ids
        )
        
        count = len(point_ids)
        logger.info(f"Eliminados {count} puntos del documento {doc_id}")
        return count

    def search(
        self, 
        query_vector: List[float], 
        top_k: int = 5,
        area: Optional[str] = None,
        doc_id: Optional[str] = None,
        status: Optional[str] = "active",
        category_ids: Optional[List[int]] = None
    ) -> Dict:
        """
        Búsqueda vectorial con filtros opcionales
        """
        # Construir filtros
        filter_conditions = []
        
        if area:
            filter_conditions.append(
                FieldCondition(key="area", match=MatchValue(value=area))
            )
        
        if doc_id:
            filter_conditions.append(
                FieldCondition(key="doc_id", match=MatchValue(value=doc_id))
            )

        if status:
            filter_conditions.append(
                FieldCondition(key="status", match=MatchValue(value=status))
            )
        
        if category_ids:
            # En Qdrant, si guardamos un array, podemos buscar si contiene alguno de estos valores
            # Usamos MatchAny para comparar contra una lista de valores
            from qdrant_client.models import MatchAny
            filter_conditions.append(
                FieldCondition(key="category_ids", match=MatchAny(any=category_ids))
            )
        
        # Aplicar filtros si existen
        query_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Realizar búsqueda
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            query_filter=query_filter,
            with_payload=True,
            limit=top_k
        )
        
        contexts = []
        sources = set()
        doc_ids = set()
        
        for r in results:
            payload = getattr(r, "payload", None) or {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            doc_id_val = payload.get("doc_id", "")
            
            if text:
                contexts.append(text)
                if source:
                    sources.add(source)
                if doc_id_val:
                    doc_ids.add(doc_id_val)
        
        return {
            "contexts": contexts,
            "sources": list(sources),
            "doc_ids": list(doc_ids)
        }

    def get_document_info(self, doc_id: str) -> Optional[Dict]:
        """Obtiene información de un documento"""
        scroll_result = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=Filter(
                must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
            ),
            limit=1,
            with_payload=True,
            with_vectors=False
        )
        
        if scroll_result[0]:
            point = scroll_result[0][0]
            payload = getattr(point, "payload", {})
            metadata = payload.get("metadata", {}) or {}
            return {
                "doc_id": payload.get("doc_id"),
                "source": payload.get("source"),
                "name": metadata.get("name"),
                "description": metadata.get("description"),
                "upload_date": payload.get("upload_date"),
                "status": payload.get("status", "active"),
                "category_ids": payload.get("category_ids", [])
            }
        return None
    
    def list_documents(self, area: Optional[str] = None) -> List[Dict]:
        """
        Lista todos los documentos únicos en la colección
        Opcionalmente filtrados por área
        """
        filter_conditions = []
        if area:
            filter_conditions.append(
                FieldCondition(key="area", match=MatchValue(value=area))
            )
        
        query_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Scroll para obtener todos los documentos
        scroll_result = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=query_filter,
            limit=10000,
            with_payload=True,
            with_vectors=False
        )
        
        # Agrupar por doc_id para obtener documentos únicos
        docs_dict = {}
        for point in scroll_result[0]:
            payload = getattr(point, "payload", {})
            metadata = payload.get("metadata", {}) or {}
            doc_id = payload.get("doc_id")
            
            if doc_id and doc_id not in docs_dict:
                docs_dict[doc_id] = {
                    "doc_id": doc_id,
                    "source": payload.get("source"),
                    "name": metadata.get("name"),
                    "description": metadata.get("description"),
                    "upload_date": payload.get("upload_date")
                }
        
        return list(docs_dict.values())
"""
Verificar estado de la ingesta en Qdrant y guardar en archivo
"""
from qdrant_client import QdrantClient
from collections import defaultdict

client = QdrantClient(host="qdrant", port=6333)

# Obtener todos los puntos
all_points = client.scroll(
    collection_name="legal_docs",
    limit=10000,
    with_payload=True
)[0]

output = []
output.append("="*60)
output.append("ESTADO DE LA BASE DE DATOS QDRANT")
output.append("="*60)
output.append(f"Total de chunks: {len(all_points)}")

# Agrupar por doc_id
docs_by_id = defaultdict(lambda: {"count": 0, "source": "", "area": "", "category_ids": []})

for point in all_points:
    doc_id = point.payload.get('doc_id', 'unknown')
    docs_by_id[doc_id]["count"] += 1
    docs_by_id[doc_id]["source"] = point.payload.get('source', 'N/A')
    docs_by_id[doc_id]["area"] = point.payload.get('area', 'N/A')
    docs_by_id[doc_id]["category_ids"] = point.payload.get('category_ids', [])

output.append(f"\nDocumentos indexados: {len(docs_by_id)}")
output.append("\n" + "="*60)
output.append("DETALLE POR DOCUMENTO")
output.append("="*60)

# Ordenar por doc_id
for doc_id in sorted(docs_by_id.keys()):
    info = docs_by_id[doc_id]
    output.append(f"\nDoc ID: {doc_id}")
    output.append(f"  Archivo: {info['source']}")
    output.append(f"  Área: {info['area']}")
    output.append(f"  Categorías: {info['category_ids']}")
    output.append(f"  Chunks: {info['count']}")

# Agrupar por área
output.append("\n" + "="*60)
output.append("RESUMEN POR ÁREA")
output.append("="*60)

areas = defaultdict(lambda: {"docs": 0, "chunks": 0})
for doc_id, info in docs_by_id.items():
    area = info['area']
    areas[area]["docs"] += 1
    areas[area]["chunks"] += info['count']

for area in sorted(areas.keys()):
    output.append(f"\n{area.upper()}:")
    output.append(f"  Documentos: {areas[area]['docs']}")
    output.append(f"  Chunks totales: {areas[area]['chunks']}")

output.append("\n" + "="*60)

# Guardar en archivo
result_text = "\n".join(output)
with open("ingestion_status.txt", "w", encoding="utf-8") as f:
    f.write(result_text)

# También imprimir
print(result_text)
print("\n✅ Resultados guardados en: ingestion_status.txt")

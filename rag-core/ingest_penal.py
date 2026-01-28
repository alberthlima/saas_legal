"""
Script de Ingesta Masiva - Área Penal
Detecta automáticamente PDFs en el directorio pdfs/ y los ingesta
"""
import requests
import json
import time
from pathlib import Path
import os

# Configuración
RAG_URL = "http://localhost:8000"
CATEGORY_PENAL = 2
PDF_DIR = Path("/app/pdfs")  # Ruta dentro del contenedor

def get_available_pdfs():
    """Detecta todos los PDFs disponibles en el directorio"""
    if not PDF_DIR.exists():
        print(f"❌ Directorio {PDF_DIR} no existe")
        return []
    
    pdfs = list(PDF_DIR.glob("*.pdf"))
    return [pdf.name for pdf in pdfs]

def ingest_pdf(pdf_name, doc_id, category_ids):
    """Ingesta un PDF individual"""
    payload = {
        "pdf_path": pdf_name,
        "doc_id": str(doc_id),
        "category_ids": category_ids,
        "area": "penal",
        "replace_existing": True
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"Ingiriendo: {pdf_name}")
        print(f"Doc ID: {doc_id}")
        print(f"{'='*60}")
        
        response = requests.post(
            f"{RAG_URL}/ingest-pdf",
            json=payload,
            timeout=300  # 5 minutos timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ÉXITO")
            print(f"   Chunks creados: {data.get('chunks_created', 'N/A')}")
            print(f"   Fecha: {data.get('upload_date', 'N/A')}")
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("INGESTA MASIVA - ÁREA PENAL")
    print("="*60)
    
    # Detectar PDFs disponibles
    pdfs_disponibles = get_available_pdfs()
    
    if not pdfs_disponibles:
        print("❌ No se encontraron PDFs en el directorio pdfs/")
        print(f"   Directorio buscado: {PDF_DIR}")
        return
    
    # Filtrar solo PDFs del área penal (excluir la constitución)
    pdfs_penales = [
        pdf for pdf in pdfs_disponibles 
        if not pdf.startswith("QyIZ")  # Excluir constitución
    ]
    
    print(f"PDFs encontrados: {len(pdfs_disponibles)}")
    print(f"PDFs del área penal: {len(pdfs_penales)}")
    print(f"Categoría: {CATEGORY_PENAL} (Penal)")
    print("="*60)
    
    # Mostrar lista de PDFs a ingestar
    print("\nPDFs a ingestar:")
    for i, pdf in enumerate(pdfs_penales, 1):
        print(f"  {i}. {pdf}")
    
    print("\n" + "="*60)
    input("Presiona Enter para comenzar la ingesta...")
    
    resultados = {
        "exitosos": 0,
        "fallidos": 0,
        "total": len(pdfs_penales)
    }
    
    for i, pdf in enumerate(pdfs_penales, start=1):
        doc_id = f"penal_{i}"
        
        # Ingestar con categoría penal
        category_ids = [CATEGORY_PENAL]
        
        success = ingest_pdf(pdf, doc_id, category_ids)
        
        if success:
            resultados["exitosos"] += 1
        else:
            resultados["fallidos"] += 1
        
        # Pausa entre ingestas
        if i < len(pdfs_penales):
            print("\nEsperando 3 segundos antes del siguiente...")
            time.sleep(3)
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DE INGESTA")
    print("="*60)
    print(f"Total documentos: {resultados['total']}")
    print(f"✅ Exitosos: {resultados['exitosos']}")
    print(f"❌ Fallidos: {resultados['fallidos']}")
    print("="*60)
    
    if resultados['fallidos'] == 0:
        print("\n🎉 ¡Ingesta completada exitosamente!")
    else:
        print(f"\n⚠️ Hubo {resultados['fallidos']} errores. Revisar logs.")

if __name__ == "__main__":
    main()

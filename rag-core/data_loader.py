# creación de los vectores
from openai import OpenAI
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv
import re

# cargar variables de entorno definidas en el archivo .env
load_dotenv()

# inicialización del cliente de OpenAI para el uso de modelos de lenguaje y embeddings
client = OpenAI()

# definición del modelo de embeddings y de la dimensión de los vectores resultantes
EMBED_MODEL = "text-embedding-3-large"
EMBED_DIM = 3072

# configuración del divisor de texto: fragmentos más pequeños para PDFs grandes
# Reducido para evitar payloads muy grandes en Qdrant
splitter = SentenceSplitter(chunk_size=800, chunk_overlap=150)

def clean_text(text: str) -> str:
    # Eliminar encabezados y pies de página comunes que generan ruido
    patterns = [
        r"TEXTO DE CONSULTA",
        r"Derechos Reservados © Gaceta Oficial de Bolivia",
        r"\"2022 AÑO DE LA REVOLUCIÓN CULTURAL PARA LA DESPATRIARCALIZACIÓN: POR UNA VIDA LIBRE DE VIOLENCIA CONTRA LAS MUJERES\"",
        r"Gaceta Oficial de Bolivia",
    ]
    for p in patterns:
        text = re.sub(p, "", text, flags=re.IGNORECASE)
    
    # Limpiar espacios múltiples y líneas vacías excesivas
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def load_and_chunk_pdf(path: str):
    # carga un archivo PDF desde la ruta indicada, extrae su contenido textual y lo divide en fragmentos adecuados.
    docs = PDFReader().load_data(file=path)
    full_text = "\n".join([d.text for d in docs if getattr(d, "text", None)])
    cleaned_text = clean_text(full_text)

    # FRAGMENTACIÓN BASADA EN ARTÍCULOS
    # Buscamos patrones de "Artículo X." para dividir
    article_pattern = r"(?i)Artículo\s+\d+[\.\s]"
    
    # Encontrar todos los inicios de artículo
    split_points = [m.start() for m in re.finditer(article_pattern, cleaned_text)]
    
    if not split_points:
        # Si no hay artículos detectados, usamos el splitter normal
        print(f"No articles detected in {path}, using standard splitting.")
        return splitter.split_text(cleaned_text)

    chunks = []
    # El primer fragmento antes del primer artículo (Preámbulo/Títulos)
    if split_points[0] > 0:
        chunks.append(cleaned_text[:split_points[0]].strip())

    for i in range(len(split_points)):
        start = split_points[i]
        end = split_points[i+1] if i+1 < len(split_points) else len(cleaned_text)
        chunk_text = cleaned_text[start:end].strip()
        
        # Si el fragmento es demasiado largo (> 1500 chars), lo dividimos con el splitter normal
        if len(chunk_text) > 1500:
            sub_chunks = splitter.split_text(chunk_text)
            chunks.extend(sub_chunks)
        else:
            chunks.append(chunk_text)

    # retorno de la lista de fragmentos resultantes
    print(f"Extracted {len(chunks)} chunks using Article-Regex from {path}")
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    # genera los embeddings correspondientes a una lista de fragmentos de texto utilizando el modelo de OpenAI especificado.
    # solicitud al modelo de OpenAI para generar embeddings del texto proporcionado
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )

    # extracción y retorno de los vectores de embeddings generados
    return [item.embedding for item in response.data]

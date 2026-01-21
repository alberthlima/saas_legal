FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El comando se ejecutará con recarga automática si montamos el volumen
CMD ["python", "main.py"]

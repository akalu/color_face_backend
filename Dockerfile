FROM python:3.10-slim

# Instalar dependencias del sistema para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar todos los archivos
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para iniciar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
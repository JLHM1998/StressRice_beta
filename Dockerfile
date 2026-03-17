# Usamos una imagen base ligera de Python
FROM python:3.9-slim

# 1. Instalar dependencias del sistema necesarias para GDAL y Rasterio
# Esto es obligatorio para que geopandas y rasterio funcionen en el servidor
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    libgdal-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Configurar variables de entorno para que Python encuentre GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# 2. Crear directorio de trabajo
WORKDIR /app

# 3. Copiar los archivos de requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar todo el código de tu app al servidor
COPY . .

# 5. Comando para ejecutar la app
CMD ["streamlit", "run", "app_cwsi.py", "--server.port=8501", "--server.address=0.0.0.0"]

# Imagen base Python 3.11 slim
FROM python:3.11-slim

# 1. Instalar dependencias del sistema para GDAL, GEOS, PROJ (requeridos por rasterio, geopandas y shapely)
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 2. Variables de entorno para compilación de GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# 3. Directorio de trabajo
WORKDIR /app

# 4. Instalar dependencias Python (primero para aprovechar cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar código de la aplicación
COPY . .

# 6. Exponer puerto (Render asigna el PORT dinámicamente)
EXPOSE 8501

# 7. Ejecutar la app usando PORT de entorno si está disponible, sino 8501
CMD streamlit run app_cwsi.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false

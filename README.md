# StressRice: Plataforma de Monitoreo Agrícola 🌾

**StressRice** es una plataforma web avanzada diseñada para la agricultura de precisión en el cultivo de arroz. Utilizando imágenes térmicas y multiespectrales obtenidas por drones, la plataforma permite calcular índices de estrés hídrico (CWSI) y realizar calibraciones radiométricas precisas para optimizar el riego y mejorar el rendimiento de los cultivos.

![StressRice Home](assets/stressrice_logo_v2.png)

## 🚀 Características Principales

### 1. 🏠 Inicio (Dashboard)
- **Interfaz Elegante**: Diseño moderno y profesional con soporte para modo oscuro.
- **Navegación Rápida**: Acceso directo a los módulos de Calibración y CWSI.
- **Información Clave**: Resumen de las capacidades de la plataforma (Agricultura 4.0, Teledetección).

### 2. 🔥 Calibración Térmica
- **Corrección Radiométrica**: Algoritmos avanzados para calibrar imágenes térmicas utilizando datos de temperatura de referencia (húmedo y seco).
- **Visualización Interactiva**: Gráficos de regresión lineal para validar la calidad de la calibración.
- **Descarga de Manual**: Acceso directo al manual de usuario de ThermiCAL.

### 3. 💧 Cálculo de CWSI (Crop Water Stress Index)
- **Monitoreo de Estrés Hídrico**: Cálculo automático del índice CWSI para detectar necesidades de riego.
- **Análisis Geoespacial**: Procesamiento de ortomosaicos térmicos y estructurales.
- **Histogramas y Estadísticas**: Distribución detallada de los niveles de estrés en el cultivo.

### 4. 📋 Registros (Admin)
- **Control de Acceso**: Módulo exclusivo para administradores.
- **Historial de Usuarios**: Registro detallado de quién ha accedido a la plataforma (Nombre, ID, Fecha/Hora).
- **Exportación de Datos**: Descarga del historial completo en formato CSV.

## 🛠️ Instalación y Uso Local

### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Pasos
1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/JLHM1998/StressRice.git
    cd StressRice
    ```

2.  **Crear un entorno virtual (opcional pero recomendado)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/Mac
    venv\Scripts\activate     # En Windows
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación**:
    ```bash
    streamlit run app_cwsi.py
    ```

## 🔐 Credenciales de Administrador
Para acceder al módulo de **Registros**, debes iniciar sesión con uno de los siguientes usuarios (ID/Email):
- `Admin`
- `Joluh`
- `Creador`

## 📄 Créditos y Financiamiento
- **Desarrollado por**: José Luis (Joluh)
- **Financiamiento**: Proyecto EcosmartRice (Contrato PE501086540-2024-PROCIENCIA) - CONCYTEC
- **Institución**: Universidad Nacional Agraria La Molina

---
*Powered by StressRice © 2025*

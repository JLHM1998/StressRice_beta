import streamlit as st
import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from rasterio.io import MemoryFile
from rasterio.warp import reproject
from rasterio.enums import Resampling as RRes
from rasterio.features import rasterize
from shapely.validation import make_valid
import geopandas as gpd
import datetime
import os
import csv
import time
import tempfile
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_option_menu import option_menu
import plotly.express as px

# =====================================================
# CONFIGURACIÓN DE PÁGINA
# =====================================================

st.set_page_config(
    page_title="StressRice",
    layout="wide",
    page_icon="🌾",
    initial_sidebar_state="expanded"
)

# =====================================================
# ESTILOS CSS (DISEÑO PREMIUM & ADAPTABLE)
# =====================================================

def inject_custom_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

            :root {
                /* Palette based on user request */
                --color-dark-blue: #1B264F;  /* Deep Navy */
                --color-teal: #2A9D8F;       /* Teal/Cyan */
                --color-green: #6A994E;      /* Natural Green */
                --color-brown: #8D6E63;      /* Earthy Brown */
                
                --primary-color: var(--color-green);
                --secondary-color: var(--color-dark-blue);
                --accent-color: var(--color-teal);
                
                /* Light Mode Defaults */
                --bg-gradient-start: #f8f9fa;
                --bg-gradient-end: #e9ecef;
                --text-main: #212529;
                --text-muted: #6c757d;
                --card-bg: rgba(255, 255, 255, 0.90);
                --glass-border: rgba(255, 255, 255, 0.6);
                --sidebar-bg: #ffffff;
                --shadow-color: rgba(0,0,0,0.08);
            }

            @media (prefers-color-scheme: dark) {
                :root {
                    --bg-gradient-start: #0f172a;
                    --bg-gradient-end: #1e293b;
                    --text-main: #f1f5f9;
                    --text-muted: #94a3b8;
                    --card-bg: rgba(30, 41, 59, 0.85);
                    --glass-border: rgba(255, 255, 255, 0.1);
                    --sidebar-bg: #0f172a;
                    --shadow-color: rgba(0,0,0,0.3);
                }
            }

            /* Animaciones */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); }
            }

            .animate-fade-in {
                animation: fadeIn 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            }

            /* Tipografía Global */
            html, body, [class*="css"] {
                font-family: 'Plus Jakarta Sans', sans-serif;
                color: var(--text-main);
                -webkit-font-smoothing: antialiased;
            }

            h1, h2, h3, h4, h5, h6 {
                font-family: 'Outfit', sans-serif;
                font-weight: 700;
                color: var(--primary-color);
                letter-spacing: -0.02em;
            }

            /* Fondo de la Aplicación */
            .stApp {
                background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
                background-attachment: fixed;
            }

            /* Sidebar */
            [data-testid="stSidebar"] {
                background-color: var(--sidebar-bg);
                border-right: 1px solid var(--glass-border);
            }
            
            [data-testid="stSidebar"] h1 {
                color: var(--primary-color);
            }
            
            [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
                color: var(--text-main);
            }

            /* Cards con Efecto Glassmorphism Refinado */
            .glass-card {
                background: var(--card-bg);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border-radius: 20px;
                border: 1px solid var(--glass-border);
                padding: 40px;
                margin-bottom: 24px;
                box-shadow: 0 8px 32px 0 var(--shadow-color);
                transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            }

            .glass-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px 0 var(--shadow-color);
                border-color: rgba(42, 157, 143, 0.3);
            }

            /* Contenedores de KPIs */
            .kpi-card {
                background: linear-gradient(145deg, rgba(255,255,255,0.6), rgba(255,255,255,0.3));
                border-radius: 16px;
                padding: 20px;
                border: 1px solid rgba(255,255,255,0.5);
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }

            /* Botones Personalizados */
            .stButton > button {
                background: linear-gradient(135deg, var(--color-green), var(--color-teal));
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0.75rem 2rem;
                font-weight: 600;
                font-size: 1rem;
                letter-spacing: 0.3px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(106, 153, 78, 0.3);
            }

            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(106, 153, 78, 0.4);
                filter: brightness(1.1);
                color: white;
            }

            /* Header Container */
            .header-hero {
                background: linear-gradient(120deg, var(--color-dark-blue), var(--color-green));
                padding: 40px 60px;
                border-radius: 30px;
                color: white;
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 50px;
                box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
            }
            
            .header-hero::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(circle at top right, rgba(255,255,255,0.1) 0%, transparent 60%);
                pointer-events: none;
            }

            .header-content {
                z-index: 1;
                text-align: center;
                flex-grow: 1;
                padding: 0 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }

            .header-title {
                font-size: 4rem;
                margin: 10px 0 0 0;
                font-weight: 800;
                letter-spacing: -1.5px;
                color: white !important;
                text-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }

            .header-subtitle {
                font-size: 1.4rem;
                opacity: 0.95;
                margin-top: 12px;
                font-weight: 400;
                color: rgba(255,255,255,0.9) !important;
                letter-spacing: 0.5px;
            }

            .logo-container {
                background: rgba(255, 255, 255, 0.95);
                padding: 15px;
                border-radius: 20px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .logo-container:hover {
                transform: scale(1.05);
            }

            .logo-img {
                height: 120px;
                object-fit: contain;
            }
            
            .center-logo {
                height: 80px;
                margin-bottom: 10px;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
            }

            /* Footer */
            .footer {
                text-align: center;
                margin-top: 100px;
                padding: 40px;
                color: var(--text-muted);
                font-size: 0.9rem;
                border-top: 1px solid var(--glass-border);
            }
            
            /* Login Box */
            .login-container {
                max-width: 480px;
                margin: 100px auto;
                padding: 60px;
                background: var(--card-bg);
                border-radius: 30px;
                box-shadow: 0 30px 80px -20px var(--shadow-color);
                text-align: center;
                border: 1px solid var(--glass-border);
                backdrop-filter: blur(20px);
            }
            
            /* Inputs Estilizados */
            .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > div {
                border-radius: 10px;
                border: 1px solid rgba(0,0,0,0.08);
                background-color: rgba(255,255,255,0.7);
                color: var(--text-main);
                transition: all 0.2s;
            }
            
            .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus {
                border-color: var(--color-teal);
                box-shadow: 0 4px 12px rgba(42, 157, 143, 0.1);
                background-color: #ffffff;
            }
            
            /* Tooltips customizados (si se usa help) */
            .stTooltipIcon {
                color: var(--color-teal);
            }
            
            /* Citation Box */
            .citation-box {
                background-color: rgba(42, 157, 143, 0.1);
                border-left: 4px solid var(--color-teal);
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-size: 0.9rem;
                color: var(--text-muted);
            }
            .citation-box a {
                color: var(--color-teal);
                text-decoration: none;
                font-weight: 600;
            }
            .citation-box a:hover {
                text-decoration: underline;
            }
            
            /* Dashboard Elements */
            .dashboard-stat {
                background: rgba(255, 255, 255, 0.5);
                border-radius: 16px;
                padding: 20px;
                text-align: center;
                border: 1px solid var(--glass-border);
            }
            
            .status-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }
            
            .status-online { background-color: #2ecc71; box-shadow: 0 0 10px #2ecc71; }
            .status-warning { background-color: #f1c40f; box-shadow: 0 0 10px #f1c40f; }
            
            .alert-box {
                background: rgba(255, 59, 48, 0.1);
                border-left: 4px solid #ff3b30;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
            }
        </style>
    """, unsafe_allow_html=True)

# =====================================================
# GESTIÓN DE AUTENTICACIÓN Y DATOS
# =====================================================

class AuthManager:
    # Lista de administradores autorizados para ver registros
    ADMINS = ["Admin", "Joluh", "Creador"]

    @staticmethod
    def get_img_as_base64(file_path):
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except:
            return ""
    
    @staticmethod
    def get_file_content(file_path):
        try:
            with open(file_path, "rb") as f:
                return f.read()
        except:
            return None

    @staticmethod
    def get_google_sheet_client():
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            return client
        except Exception:
            return None

    @staticmethod
    def save_user(name, dni_email):
        # Intentar guardar en Google Sheets
        client = AuthManager.get_google_sheet_client()
        if client:
            try:
                sheet_name = st.secrets["gcp_service_account"]["sheet_name"]
                sheet = client.open(sheet_name).sheet1
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([timestamp, name, dni_email])
            except Exception:
                pass 
        
        # Siempre guardar localmente
        return AuthManager.save_user_local(name, dni_email)

    @staticmethod
    def save_user_local(name, dni_email):
        USERS_FILE = "users.csv"
        file_exists = os.path.exists(USERS_FILE)
        try:
            with open(USERS_FILE, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Timestamp", "Nombre", "DNI_Email"])
                writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, dni_email])
            return True
        except Exception as e:
            st.error(f"Error local: {e}")
            return False

    @staticmethod
    def get_local_logs():
        USERS_FILE = "users.csv"
        if os.path.exists(USERS_FILE):
            try:
                df = pd.read_csv(USERS_FILE)
                return df
            except Exception:
                return pd.DataFrame()
        return pd.DataFrame()

    @staticmethod
    def render_login():
        # Usar el nuevo logo moderno de StressRice (v2)
        logo_path = "assets/stressrice_logo_v2.png"
             
        rice_plant = AuthManager.get_img_as_base64(logo_path)

        st.markdown(f"""
            <div class="login-container animate-fade-in">
                <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                    <img src="data:image/png;base64,{rice_plant}" style="height: 350px; object-fit: contain;">
                </div>
                <p style="color: var(--text-muted); margin-bottom: 40px; font-size: 1.2rem; font-weight: 500;">Plataforma de Monitoreo Agrícola</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            with st.form("login_form"):
                name = st.text_input("Nombre Completo", placeholder="Ej: Juan Pérez", help="Ingresa tu nombre y apellido")
                dni_email = st.text_input("Usuario / Email", placeholder="Ej: admin", help="Ingresa tu usuario asignado")
                submit = st.form_submit_button("Ingresar", use_container_width=True)
                
                if submit:
                    if name and dni_email:
                        if AuthManager.save_user(name, dni_email):
                            st.session_state['logged_in'] = True
                            st.session_state['user_name'] = name
                            st.session_state['user_id'] = dni_email # Guardar ID para verificar permisos
                            st.success(f"¡Bienvenido, {name}!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("Por favor completa todos los campos.")

# =====================================================
# MÓDULOS DE LA APLICACIÓN
# =====================================================

class AppModules:
    @staticmethod
    def change_page(page_name):
        st.session_state['selected_module'] = page_name

    @staticmethod
    def render_header():
        escudo = AuthManager.get_img_as_base64("assets/Escudo.png")
        logo_tyc = AuthManager.get_img_as_base64("assets/logo_TyC.png")
        
        # Header centrado con 3 elementos: Escudo - Título - TyC
        st.markdown(f"""
            <div class="header-hero animate-fade-in">
                <div class="logo-container">
                    <img src="data:image/png;base64,{escudo}" class="logo-img">
                </div>
                <div class="header-content">
                    <h1 class="header-title">StressRice</h1>
                    <p class="header-subtitle">Tecnología Avanzada para el Cultivo de Arroz</p>
                </div>
                <div>
                    <img src="data:image/png;base64,{logo_tyc}" class="logo-img">
                </div>
            </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def home_page():
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)

        # Hero Section con diseño CSS puro (sin imagen externa)
        st.markdown("""
            <div class="glass-card" style="padding: 0; overflow: hidden; display: flex; flex-direction: row; flex-wrap: wrap; align-items: stretch; min-height: 400px; border: 1px solid rgba(255,255,255,0.5);">
                <div style="flex: 1; padding: 60px 50px; display: flex; flex-direction: column; justify-content: center; min-width: 300px;">
                    <div style="margin-bottom: 20px;">
                        <span style="background: rgba(106, 153, 78, 0.15); color: var(--color-green); padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; letter-spacing: 1px; text-transform: uppercase;">Cloud Platform v2.0</span>
                    </div>
                    <h2 style="font-size: 3rem; color: var(--color-dark-blue); font-weight: 800; line-height: 1.1; margin-bottom: 20px;">
                        Agricultura de <br><span style="background: linear-gradient(120deg, var(--color-teal), var(--color-green)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Precisión</span>
                    </h2>
                    <p style="font-size: 1.1rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 10px;">
                        StressRice integra teledetección térmica y modelamiento avanzado para optimizar la gestión hídrica del cultivo de arroz en la costa norte del Perú.
                    </p>
                </div>
                <div style="flex: 1; min-width: 280px; background: linear-gradient(135deg, var(--color-dark-blue) 0%, var(--color-teal) 50%, var(--color-green) 100%); display: flex; align-items: center; justify-content: center; padding: 40px; position: relative; overflow: hidden;">
                    <div style="position: absolute; inset: 0; background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.08) 0%, transparent 60%);"></div>
                    <div style="text-align: center; z-index: 1;">
                        <div style="font-size: 5rem; margin-bottom: 15px; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));">🌾</div>
                        <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; font-weight: 600; margin: 0;">Monitoreo con Drones</p>
                        <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-top: 6px;">Imágenes Térmicas &amp; Multiespectrales</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Module Cards
        st.markdown('<h3 style="text-align: center; margin: 60px 0 40px 0; color: var(--color-dark-blue);">Módulos Principales</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="glass-card" style="text-align: center; height: 100%;">
                    <div style="font-size: 3.5rem; margin-bottom: 15px;">🔥</div>
                    <h3 style="color: var(--color-dark-blue);">Calibración Térmica</h3>
                    <p style="color: var(--text-muted);">Corrección radiométrica para sensores embarcados.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Ir a Calibración", use_container_width=True): AppModules.change_page("Calibración")
        
        with col2:
            st.markdown("""
                <div class="glass-card" style="text-align: center; height: 100%;">
                    <div style="font-size: 3.5rem; margin-bottom: 15px;">💧</div>
                    <h3 style="color: var(--color-dark-blue);">Índice CWSI</h3>
                    <p style="color: var(--text-muted);">Estimación espacial del estrés hídrico en el cultivo.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Ir a CWSI", use_container_width=True): AppModules.change_page("Cálculo CWSI")

        # Features Section
        st.markdown("""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 60px;">
                <div class="kpi-card">
                    <div style="font-size: 2rem;">🎯</div>
                    <h4>Alta Precisión</h4>
                    <p style="font-size: 0.9rem; color: var(--text-muted);">Modelos validados con r² > 0.92</p>
                </div>
                 <div class="kpi-card">
                    <div style="font-size: 2rem;">⚡</div>
                    <h4>Rápido</h4>
                    <p style="font-size: 0.9rem; color: var(--text-muted);">Procesamiento en la nube</p>
                </div>
                 <div class="kpi-card">
                    <div style="font-size: 2rem;">📊</div>
                    <h4>Reportes</h4>
                    <p style="font-size: 0.9rem; color: var(--text-muted);">Gráficos interactivos y CSV</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def render_citation():
        st.markdown("""
            <div class="citation-box">
                📚 <b>Referencia Científica:</b><br>
                "Water Stress Index and Stomatal Conductance under Different Irrigation Regimes with Thermal Sensors in Rice Fields on the Northern Coast of Peru"<br>
                <i>Remote Sens.</i> <b>2024</b>, <i>16</i>(5), 796. <a href="https://www.mdpi.com/2072-4292/16/5/796" target="_blank">Leer publicación completa</a>
            </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def calibration_module():
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        
        col_title, col_manual = st.columns([3, 1])
        with col_title:
            st.markdown("### 🔥 Calibración Radiométrica")
            st.caption("Corrección de temperatura basada en modelos lineales calibrados in-situ.")
        with col_manual:
            manual_content = AuthManager.get_file_content("Manual_Usuario_ThermiCAL.pdf")
            if manual_content:
                st.download_button("📘 Manual PDF", manual_content, "Manual_Usuario_ThermiCAL.pdf", "application/pdf", use_container_width=True)

        AppModules.render_citation()

        # Layout Refinado
        col_main, col_preview = st.columns([1, 1.2])
        
        with col_main:
            st.markdown('<div class="glass-card" style="padding: 20px;">', unsafe_allow_html=True)
            st.markdown("#### ⚙️ Configuración")
            region = st.selectbox("🌎 Región", ["Lambayeque", "Lima"])
            
            provincia = distrito = zona = None
            if region == "Lambayeque":
                provincia = st.selectbox("📍 Provincia", ["Ferreñafe", "Chiclayo"])
                if provincia == "Ferreñafe": zona = st.selectbox("🗺️ Zona", ["Zapote"])
                elif provincia == "Chiclayo":
                    distrito = st.selectbox("🏙️ Distrito", ["Chongoyape", "Picsi"])
                    if distrito == "Chongoyape": zona = st.selectbox("🗺️ Zona", ["Carniche", "Paredones"])
                    elif distrito == "Picsi": zona = "Picsi"
            elif region == "Lima":
                zona = st.selectbox("📍 Zona", ["La Molina"])
            
            horas = [datetime.time(h, 0) for h in range(9, 16)]
            hora = st.selectbox("🕒 Hora", horas, format_func=lambda t: t.strftime("%I:%M %p"))

            # Ecuaciones
            ecuaciones = {
                ("Zapote", datetime.time(9, 0)): (0.8700, 9.500),
                ("Zapote", datetime.time(10, 0)): (0.9000, 9.800),
                ("Zapote", datetime.time(11, 0)): (0.9150, 9.950),
                ("Zapote", datetime.time(12, 0)): (0.9244, 10.019),
                ("Zapote", datetime.time(13, 0)): (0.9150, 9.950),
                ("Zapote", datetime.time(14, 0)): (0.9000, 9.800),
                ("Zapote", datetime.time(15, 0)): (0.8700, 9.500),
                ("Paredones", datetime.time(9, 0)): (0.85, 10.5),
                ("Paredones", datetime.time(10, 0)): (0.88, 11.2),
                ("Paredones", datetime.time(11, 0)): (0.90, 9.8),
                ("Paredones", datetime.time(12, 0)): (0.87, 10.0),
                ("Paredones", datetime.time(13, 0)): (0.89, 10.3),
                ("Paredones", datetime.time(14, 0)): (0.92, 11.0),
                ("Paredones", datetime.time(15, 0)): (0.95, 11.5),
                ("Carniche", datetime.time(9, 0)): (0.92, 12.1),
                ("Carniche", datetime.time(10, 0)): (0.95, 11.5),
                ("Carniche", datetime.time(11, 0)): (0.93, 12.0),
                ("Carniche", datetime.time(12, 0)): (0.91, 11.8),
                ("Carniche", datetime.time(13, 0)): (0.94, 11.9),
                ("Carniche", datetime.time(14, 0)): (0.96, 12.3),
                ("Carniche", datetime.time(15, 0)): (0.98, 12.7),
                ("Picsi", datetime.time(9, 0)): (0.6980, 8.520),
                ("Picsi", datetime.time(10, 0)): (0.7050, 8.630),
                ("Picsi", datetime.time(11, 0)): (0.7100, 8.700),
                ("Picsi", datetime.time(12, 0)): (0.7139, 8.7325),
                ("Picsi", datetime.time(13, 0)): (0.7100, 8.700),
                ("Picsi", datetime.time(14, 0)): (0.7050, 8.630),
                ("Picsi", datetime.time(15, 0)): (0.6980, 8.520),
                ("La Molina", datetime.time(9, 0)): (0.7130, 10.350),
                ("La Molina", datetime.time(10, 0)): (0.7180, 10.450),
                ("La Molina", datetime.time(11, 0)): (0.7240, 10.520),
                ("La Molina", datetime.time(12, 0)): (0.7291, 10.592),
                ("La Molina", datetime.time(13, 0)): (0.7240, 10.520),
                ("La Molina", datetime.time(14, 0)): (0.7180, 10.450),
                ("La Molina", datetime.time(15, 0)): (0.7130, 10.350),
            }
            
            A, B = ecuaciones.get((zona, hora), (1.0, 0.0))
            st.info(f"Modelo seleccionado: **{zona} - {hora.strftime('%H:%M')}**")
            st.latex(f"T' = {A:.4f} \\cdot T + {B:.4f}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_preview:
            st.markdown('<div class="glass-card" style="padding: 20px;">', unsafe_allow_html=True)
            st.markdown("#### 📂 Archivo Raster")
            uploaded_file = st.file_uploader("GeoTIFF Térmico", type=["tif", "tiff"])
            
            if uploaded_file:
                with st.spinner("Calibrando..."):
                    with rasterio.open(uploaded_file) as src:
                        profile = src.profile
                        image = src.read(1).astype(np.float32)
                    
                    calibrated = A * image + B
                    # Clamping visual
                    
                    st.success("Calibración completada")
                    
                    t1, t2 = st.tabs(["Original", "Calibrada"])
                    with t1: st.image(AppModules.plot_image(np.clip(image, 0, 60), "Original (°C)"), use_container_width=True)
                    with t2: st.image(AppModules.plot_image(np.clip(calibrated, 0, 60), "Calibrada (°C)"), use_container_width=True)
                    
                    profile.update(dtype=rasterio.float32)
                    with MemoryFile() as mem:
                        with mem.open(**profile) as dst: dst.write(calibrated.astype(rasterio.float32), 1)
                        st.download_button(
                            "📥 Descargar Resultado",
                            mem.read(),
                            f"{zona}_{hora.strftime('%H%M')}_calibrada.tif",
                            "image/tiff",
                            use_container_width=True
                        )
            else:
                st.info("Sube una imagen para comenzar.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def plot_image(data, title):
        vmin, vmax = np.percentile(data, [2, 98])
        fig, ax = plt.subplots(figsize=(4, 3))
        # Use a colormap that works well in both modes, or stick to inferno which is standard for thermal
        im = ax.imshow(data, cmap='inferno', vmin=vmin, vmax=vmax)
        ax.axis('off')
        ax.set_title(title, fontsize=10, fontweight='bold', color='#333333') 
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        
        import io
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=150)
        buf.seek(0)
        plt.close(fig)
        return buf

    @staticmethod
    def cwsi_module():
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        st.markdown("### 💧 Cálculo de Estrés Hídrico (CWSI)")
        
        AppModules.render_citation()
        
        # Panel de Configuración Estilizado
        st.markdown('<div class="glass-card" style="padding: 20px;">', unsafe_allow_html=True)
        with st.expander("🛠️ Parámetros del Modelo Biofísico", expanded=True):
            cols = st.columns(3)
            with cols[0]:
                st.markdown("**Variables Climáticas**")
                TA_C = st.number_input("Aire - Temp (°C)", value=28.6)
                VPD_KPA = st.number_input("Aire - VPD (kPa)", value=2.7)
            with cols[1]:
                st.markdown("**Línea Base (NWSB)**")
                NWSB_A = st.number_input("Intercepto (a)", value=-1.2)
                NWSB_B = st.number_input("Pendiente (b)", value=-2.5)
            with cols[2]:
                st.markdown("**Filtros**")
                UL_QUANTILE = st.slider("Percentil Límite Sup.", 0.90, 0.999, 0.98)
                NDSM_MIN_M = st.number_input("Altura Mínima (m)", value=1.5)
        st.markdown('</div>', unsafe_allow_html=True)

        col_in1, col_in2 = st.columns(2)
        with col_in1:
            st.markdown('<div class="glass-card" style="padding: 20px; height: 100%;">', unsafe_allow_html=True)
            st.markdown("#### 1. Rasters de Entrada")
            th_file = st.file_uploader("Térmica (K/C)", type=["tif", "tiff"], key="cwsi_th")
            dsm_file = st.file_uploader("DSM (Elevación)", type=["tif", "tiff"], key="cwsi_dsm")
            dtm_file = st.file_uploader("DTM (Terreno)", type=["tif", "tiff"], key="cwsi_dtm")
            st.markdown('</div>', unsafe_allow_html=True)
        with col_in2:
            st.markdown('<div class="glass-card" style="padding: 20px; height: 100%;">', unsafe_allow_html=True)
            st.markdown("#### 2. RGB y Vectores")
            c_rgb = st.columns(3)
            R_file = c_rgb[0].file_uploader("R", type=["tif"], key="cwsi_r")
            G_file = c_rgb[1].file_uploader("G", type=["tif"], key="cwsi_g")
            B_file = c_rgb[2].file_uploader("B", type=["tif"], key="cwsi_b")
            
            copas_files = st.file_uploader("Shapefiles (Completo)", type=["shp", "shx", "dbf", "prj", "gpkg"], accept_multiple_files=True)
            id_field = st.text_input("ID Parcela (Columna)", value="arbol_id")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🚀 Iniciar Procesamiento", type="primary", use_container_width=True):
            if not all([th_file, dsm_file, dtm_file, R_file, G_file, B_file]) or not copas_files:
                st.error("⚠️ Faltan archivos requeridos para el cálculo.")
                return

            with st.spinner("⏳ Procesando ortomosaicos y calculando índices..."):
                try:
                    # In-memory helper
                    def read_resample(f, ref=None):
                        with rasterio.open(f) as src:
                            if ref is None: return src.read(1).astype("float32"), src.profile
                            
                            out = np.empty((ref["height"], ref["width"]), dtype="float32")
                            reproject(
                                source=rasterio.band(src, 1),
                                destination=out,
                                src_transform=src.profile["transform"],
                                src_crs=src.profile["crs"],
                                dst_transform=ref["transform"],
                                dst_crs=ref["crs"],
                                resampling=RRes.bilinear
                            )
                            return out
                    
                    # 1. Load Thermal First (Reference)
                    th, th_prof = read_resample(th_file)
                    
                    # 2. Resample others
                    dsm = read_resample(dsm_file, th_prof)
                    dtm = read_resample(dtm_file, th_prof)
                    R = read_resample(R_file, th_prof)
                    G = read_resample(G_file, th_prof)
                    B = read_resample(B_file, th_prof)

                    # 3. Indices
                    ndsm = dsm - dtm
                    den = (G + R - B)
                    den[den==0] = np.nan
                    vari = (G - R) / den
                    
                    mask = (ndsm > NDSM_MIN_M) & (vari > 0.05) & (th > 0)

                    # 4. Vectors
                    def load_gdf(files):
                        temp = tempfile.mkdtemp()
                        shp = None
                        gpkg = None
                        for f in files:
                            path = os.path.join(temp, f.name)
                            with open(path, "wb") as w: w.write(f.getbuffer())
                            if f.name.endswith(".shp"): shp = path
                            elif f.name.endswith(".gpkg"): gpkg = path
                        if shp: return gpd.read_file(shp)
                        if gpkg: return gpd.read_file(gpkg)
                        return None

                    gdf = load_gdf(copas_files)
                    if gdf is None: st.error("Error leyendo Shapefile"); return
                    gdf = gdf.to_crs(th_prof["crs"])

                    # 5. CWSI Calculation
                    LL = NWSB_A + NWSB_B * VPD_KPA
                    # Calculate UL dynamically from image or fixed? Using image quantiles as proxy for Ts_max usually
                    # but original code used DeltaT quantiles. preserving logic.
                    DeltaT = th - TA_C
                    valid_dt = DeltaT[mask & np.isfinite(DeltaT)]
                    if valid_dt.size == 0: st.error("No hay píxeles válidos en la máscara."); return
                    
                    UL_val = np.quantile(valid_dt, UL_QUANTILE)
                    # Theoretical UL is usually Ts - Ta = a + b*VPD + C ?? 
                    # Original code used: cwsi = (dT - LL) / (UL_val - LL)
                    # where UL_val is a scalar derived from the image max hot pixels.
                    
                    cwsi = ((th - TA_C) - LL) / (UL_val - LL)
                    cwsi = np.clip(cwsi, 0, 1)

                    # 6. Extraction
                    records = []
                    h, w = th.shape
                    
                    # Optimization: Rasterize all polygons at once if IDs are numeric? 
                    # Stick to iterrows for safety with string IDs
                    transform = th_prof["transform"]
                    
                    progress = st.progress(0)
                    total_poly = len(gdf)

                    for i, (idx, row) in enumerate(gdf.iterrows()):
                        geom = row.geometry
                        if not geom or geom.is_empty:
                            continue
                        geom = make_valid(geom)
                        # Rasterize single polygon
                        m_poly = rasterize([(geom, 1)], out_shape=(h, w), transform=transform, fill=0, dtype="uint8").astype(bool)

                        vals = cwsi[m_poly & mask]
                        vals = vals[np.isfinite(vals)]

                        if vals.size > 0:
                            pid = row[id_field] if id_field in row.index else idx
                            records.append({
                                id_field: pid,
                                "CWSI_mean": round(float(np.mean(vals)), 4),
                                "CWSI_min": round(float(np.min(vals)), 4),
                                "CWSI_max": round(float(np.max(vals)), 4),
                                "Area_px": int(vals.size)
                            })
                        if total_poly > 0 and i % max(1, total_poly // 20) == 0:
                            progress.progress(min(1.0, (i + 1) / total_poly))
                    
                    progress.empty()

                    if not records:
                        st.warning("No se extrajeron datos. Revisa la superposición de shapefiles.")
                        return

                    df = pd.DataFrame(records)
                    
                    # Presentation
                    st.markdown("---")
                    st.success(f"✅ Procesamiento completado: {len(df)} parcelas analizadas.")
                    
                    c_map, c_data = st.columns([1, 1])
                    
                    with c_map:
                        st.markdown("#### 🗺️ Mapa de Estrés (Render)")
                        fig, ax = plt.subplots(figsize=(6, 6))
                        # Use masked array for plot
                        cwsi_ma = np.ma.masked_where(~mask, cwsi)
                        im = ax.imshow(cwsi_ma, cmap='RdYlBu_r', vmin=0, vmax=1)
                        ax.axis('off')
                        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="CWSI")
                        st.pyplot(fig)
                        
                    with c_data:
                        st.markdown("#### 📉 Distribución")
                        fig = px.histogram(df, x="CWSI_mean", nbins=20, title="Histograma de Estrés Hídrico", color_discrete_sequence=['#2A9D8F'])
                        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown("#### 📊 Detalle por Parcela")
                    
                    # Interactive Bar Chart
                    fig_bar = px.bar(df, x=id_field, y="CWSI_mean", color="CWSI_mean", 
                                     color_continuous_scale="RdYlBu_r", title="Estrés Hídrico Promedio por Lote")
                    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_bar, use_container_width=True)

                    # Table Download
                    csv = df.to_csv(index=False).encode()
                    st.download_button("📥 Descargar Reporte CSV", csv, "reporte_cwsi.csv", "text/csv", type="primary")

                except Exception as e:
                    st.error(f"Ocurrió un error: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def admin_module():
        st.markdown('<div class="animate-fade-in">', unsafe_allow_html=True)
        st.markdown("### 📋 Registros de Acceso")
        st.markdown("""
            <div class="glass-card">
                <p>Historial de usuarios que han accedido a la plataforma StressRice. (Solo visible para Administradores)</p>
            </div>
        """, unsafe_allow_html=True)

        df = AuthManager.get_local_logs()
        
        if not df.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de Registros", len(df))
            with col2:
                last_access = df.iloc[-1]['Timestamp'] if 'Timestamp' in df.columns else "N/A"
                st.metric("Último Acceso", last_access)

            st.dataframe(df, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Historial Completo",
                data=csv,
                file_name="historial_accesos.csv",
                mime="text/csv",
            )
        else:
            st.info("No hay registros disponibles todavía.")
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# MAIN APP
# =====================================================

def main():
    inject_custom_css()
    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        AuthManager.render_login()
    else:
        with st.sidebar:
            # Logo en sidebar
            rice_plant = AuthManager.get_img_as_base64("assets/stressrice_logo_v2.png")
            if rice_plant:
                 st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{rice_plant}" style="width: 180px; margin-bottom: 20px;"></div>', unsafe_allow_html=True)
            
            st.markdown(f"👤 **{st.session_state.get('user_name', 'Usuario')}**")
            
            # Definir opciones de menú según permisos
            menu_options = ["Inicio", "Calibración", "Cálculo CWSI"]
            menu_icons = ["house", "thermometer-sun", "droplet-half"]
            
            # Verificar si el usuario es admin
            user_id = st.session_state.get('user_id', '')
            user_name = st.session_state.get('user_name', '')
            
            # Simple check: si el nombre o ID está en la lista de admins (case-insensitive)
            is_admin = user_name.lower() in [a.lower() for a in AuthManager.ADMINS] or user_id.lower() in [a.lower() for a in AuthManager.ADMINS]
            
            if is_admin:
                menu_options.append("Registros")
                menu_icons.append("table")

            # Inicializar estado de navegación si no existe
            if 'selected_module' not in st.session_state:
                st.session_state['selected_module'] = menu_options[0]

            # Asegurar que el valor en session_state sea válido
            if st.session_state['selected_module'] not in menu_options:
                 st.session_state['selected_module'] = menu_options[0]

            selected = option_menu(
                menu_title=None,
                options=menu_options,
                icons=menu_icons,
                menu_icon="cast",
                default_index=menu_options.index(st.session_state['selected_module']),
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "var(--primary-color)", "font-size": "18px"}, 
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "rgba(0,0,0,0.05)", "color": "var(--text-main)"},
                    "nav-link-selected": {"background-color": "var(--primary-color)", "color": "white"},
                }
            )
            
            # Sincronizar el estado si el usuario cambia la opción desde el sidebar
            if selected != st.session_state['selected_module']:
                st.session_state['selected_module'] = selected
                st.rerun()
            
            st.markdown("---")
            if st.button("Cerrar Sesión"):
                st.session_state['logged_in'] = False
                st.rerun()

        # Main Content
        AppModules.render_header()
        
        # Usar la variable selected directamente
        if selected == "Inicio":
            AppModules.home_page()
        elif selected == "Calibración":
            AppModules.calibration_module()
        elif selected == "Cálculo CWSI":
            AppModules.cwsi_module()
        elif selected == "Registros":
            if is_admin:
                AppModules.admin_module()
            else:
                st.error("Acceso denegado.")

        # Footer
        st.markdown("""
            <div class="footer">
                <p><b>Financiamiento:</b> Proyecto EcosmartRice (Contrato PE501086540-2024-PROCIENCIA) - CONCYTEC</p>
                <p>© 2025-2026 Universidad Nacional Agraria La Molina | Powered by StressRice v2.0</p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

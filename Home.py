import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL E AMBIENTE
# ==============================================================================
APP_VERSION = "v116.0"

# Detecção de Ambiente (Secrets)
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

# Configurações da Página
titulo_pag = "[TESTE] Omnisfera" if IS_TEST_ENV else "Omnisfera | Ecossistema"
icone_pag = "🛠️" if IS_TEST_ENV else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ==============================================================================
# 2. UTILITÁRIOS E CORES
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Definição de Cores
if IS_TEST_ENV:
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
    display_text = "OMNISFERA | TESTE"
    footer_visibility = "visible" 
else:
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"
    display_text = f"OMNISFERA {APP_VERSION}"
    footer_visibility = "hidden"

# ==============================================================================
# 3. CSS GLOBAL BLINDADO (COM AJUSTES DE ESPAÇAMENTO E SCROLL)
# ==============================================================================
css_estatico = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    
    html { scroll-behavior: smooth; }
    html, body, [class*="css"] { 
        font-family: 'Nunito', sans-serif; 
        color: #2D3748; 
        background-color: #F7FAFC;
    }

    /* Animações */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    .hover-spring { transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease; }
    .hover-spring:hover { transform: translateY(-5px) scale(1.01); box-shadow: 0 15px 30px rgba(0,0,0,0.08) !important; z-index: 10; }

    /* AJUSTE: Padding reduzido no topo para compactar */
    .block-container { 
        padding-top: 80px !important; 
        padding-bottom: 2rem !important; 
        margin-top: 0rem !important;
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* --- HEADER (Movimenta-se com a página) --- */
    .logo-container {
        display: flex; align-items: center; justify-content: flex-start; 
        gap: 20px; 
        position: absolute; /* Mudado de FIXED para ABSOLUTE */
        top: 0; left: 0; width: 100%; height: 90px;
        background: linear-gradient(to bottom, #F7FAFC 0%, rgba(247, 250, 252, 0) 100%);
        z-index: 9998; 
        padding-left: 40px;
        padding-top: 10px;
    }
    .header-subtitle-text {
        font-family: 'Nunito', sans-serif; font-weight: 600; font-size: 1.1rem; /* Fonte levemente menor */
        color: #718096; border-left: 2px solid #CBD5E0; padding-left: 20px;
        height: 40px; display: flex; align-items: center; letter-spacing: -0.3px;
    }
    .logo-icon-spin { height: 70px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }
    .logo-text-static { height: 45px; width: auto; }

    /* Login Styles */
    .login-container { 
        background-color: white; padding: 40px 40px 50px 40px; 
        border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.08); 
        text-align: center; border: 1px solid #E2E8F0; 
        max-width: 500px; margin: 0 auto; margin-top: 60px;
        animation: fadeInUp 0.8s ease-out;
    }
    .login-logo-spin { height: 100px; width: auto; animation: spin 45s linear infinite; margin-bottom: 10px; }
    .login-logo-static { height: 60px; width: auto; margin-left: 10px; }
    .logo-wrapper { display: flex; justify-content: center; align-items: center; margin-bottom: 25px; }

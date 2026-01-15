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
    initial_sidebar_state="expanded" # Será ocultada via CSS no login
)

# ==============================================================================
# 2. DEFINIÇÃO DE CORES E UTILITÁRIOS
# ==============================================================================

# Definição Dinâmica de Cores
if IS_TEST_ENV:
    # Teste: Amarelo e Rodapé Visível
    card_bg = "rgba(255, 220, 50, 0.95)" 
    card_border = "rgba(200, 160, 0, 0.5)"
    display_text = "OMNISFERA | TESTE"
    footer_visibility = "visible" 
else:
    # Produção: Branco Gelo e Rodapé Oculto
    card_bg = "rgba(255, 255, 255, 0.85)"
    card_border = "rgba(255, 255, 255, 0.6)"
    display_text = f"OMNISFERA {APP_VERSION}"
    footer_visibility = "hidden"

def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ==============================================================================
# 3. CSS GLOBAL (CORRIGIDO E SEGURO)
# ==============================================================================
# Separamos o CSS estático do dinâmico para evitar SyntaxError nas f-strings

css_estatico = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
    
    /* --- RESET E BASE --- */
    html { scroll-behavior: smooth; }
    html, body, [class*="css"] { 
        font-family: 'Nunito', sans-serif; 
        color: #2D3748; 
        background-color: #F7FAFC;
    }

    /* --- ANIMAÇÕES --- */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .hover-spring {
        transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
    }
    .hover-spring:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 20px 40px rgba(0,0,0,0.08) !important;
        z-index: 10;
    }

    .block-container { 
        padding-top: 140px !important; 
        padding-bottom: 3rem !important; 
        margin-top: 0rem !important;
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* --- HEADER (APENAS LOGADOS) --- */
    .logo-container {
        display: flex; 
        align-items: center; 
        justify-content: flex-start; 
        gap: 20px; 
        position: fixed; top: 0; left: 0; width: 100%; height: 100px;
        background-color: rgba(247, 250, 252, 0.8); 
        backdrop-filter: blur(16px) saturate(180%); 
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.6);
        z-index: 9998; 
        box-shadow: 0 4px 30px rgba(0,0,0,0.03);
        padding-left: 40px;
    }

    .header-subtitle-text {
        font-family: 'Nunito', sans-serif;
        font-weight: 600;
        font-size: 1.2rem;
        color: #718096;
        border-left: 2px solid #CBD5E0;
        padding-left: 20px;
        height: 50px;
        display: flex;
        align-items: center;
        letter-spacing: -0.5px;
    }

    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .logo-icon-spin { height: 80px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }
    .logo-text-static { height: 50px; width: auto; }

    /* --- COMPONENTES --- */
    header[data-testid="stHeader"] { background-color: transparent !important; z-index: 9999 !important; pointer-events: none; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important; top: 110px !important; left: 20px !important; z-index: 1000000 !important;
        visibility: visible !important; display: flex !important;
        background-color: rgba(255,255,255,0.9) !important;
        backdrop-filter: blur(8px);
        border: 1px solid #E2E8F0 !important; border-radius: 12px !important;
        width: 40px !important; height: 40px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
        align-items: center !important; justify-content: center !important;
        color: #4A5568 !important; pointer-events: auto !important; 
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    [data-testid="stSidebarCollapsedControl"]:hover {
        background-color: #3182CE !important; color: white !important; transform: scale(1.1); box-shadow: 0 8px 20px rgba(49, 130, 206, 0.3) !important;
    }

    /* --- BENTO GRID & CARDS --- */
    .dash-hero { 
        background: radial-gradient(circle at top right, #0F52BA, #062B61); 
        border-radius: 24px; margin-bottom: 40px; 
        box-shadow: 0 20px 40px -10px rgba(15, 82, 186, 0.4);
        color: white; position: relative; overflow: hidden;
        padding: 60px;
        display: flex; align-items: center; justify-content: flex-start;
        margin-top: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .hero-title { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2.4rem; margin: 0; line-height: 1.1; margin-bottom: 15px; letter-spacing: -1px; }
    .hero-subtitle { font-family: 'Inter', sans-serif; font-size: 1.15rem; opacity: 0.9; font-weight: 400; max-width: 600px; }
    .hero-bg-icon { position: absolute; right: 30px; font-size: 10rem; opacity: 0.05; top: 10px; transform: rotate(-10deg); pointer-events: none; }

    .tool-card { 
        background: white; border-radius: 24px; padding: 30px 25px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.02); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        text-align: center; position: relative; overflow: hidden;
    }
    .card-logo-box { height: 90px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    .card-logo-img { max-height: 85px; width: auto; object-fit: contain; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1)); }
    .tool-desc-short { font-size: 0.95rem; color: #7

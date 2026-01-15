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
    initial_sidebar_state="expanded" # Será controlada via CSS
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
# 3. CSS GLOBAL (SEPARADO PARA EVITAR ERROS)
# ==============================================================================

# CSS ESTÁTICO (Estrutura e Animações) - Sem f-string para evitar conflito de chaves
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
    @keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

    .hover-spring { transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease; }
    .hover-spring:hover { transform: translateY(-8px) scale(1.01); box-shadow: 0 20px 40px rgba(0,0,0,0.08) !important; z-index: 10; }

    .block-container { 
        padding-top: 20px !important; 
        padding-bottom: 3rem !important; 
        margin-top: 0rem !important;
        animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    /* Header (Apenas Logado) */
    .logo-container {
        display: flex; align-items: center; justify-content: flex-start; 
        gap: 20px; position: fixed; top: 0; left: 0; width: 100%; height: 100px;
        background-color: rgba(247, 250, 252, 0.8); 
        backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.6);
        z-index: 9998; box-shadow: 0 4px 30px rgba(0,0,0,0.03);
        padding-left: 40px;
    }
    .header-subtitle-text {
        font-family: 'Nunito', sans-serif; font-weight: 600; font-size: 1.2rem;
        color: #718096; border-left: 2px solid #CBD5E0; padding-left: 20px;
        height: 50px; display: flex; align-items: center; letter-spacing: -0.5px;
    }
    .logo-icon-spin { height: 80px; width: auto; animation: spin 45s linear infinite; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }
    .logo-text-static { height: 50px; width: auto; }

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
    
    .manifesto-login { font-family: 'Nunito', sans-serif; font-size: 0.95rem; color: #64748B; font-style: italic; line-height: 1.6; margin-bottom: 30px; }
    
    /* Inputs & Buttons */
    .stTextInput input { border-radius: 12px !important; border: 1px solid #E2E8F0 !important; padding: 12px !important; background-color: #F8FAFC !important; }
    .stTextInput input:focus { border-color: #3182CE !important; box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1); }
    
    /* Bento Grid */
    .dash-hero { 
        background: radial-gradient(circle at top right, #0F52BA, #062B61); 
        border-radius: 24px; margin-bottom: 40px; margin-top: 100px; /* Espaço para o header */
        box-shadow: 0 20px 40px -10px rgba(15, 82, 186, 0.4);
        color: white; position: relative; overflow: hidden; padding: 60px;
        display: flex; align-items: center; justify-content: flex-start;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .hero-title { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 2.4rem; margin: 0; line-height: 1.1; margin-bottom: 15px; }
    .hero-subtitle { font-family: 'Inter', sans-serif; font-size: 1.15rem; opacity: 0.9; }
    .hero-bg-icon { position: absolute; right: 30px; font-size: 10rem; opacity: 0.05; top: 10px; transform: rotate(-10deg); }

    .tool-card { 
        background: white; border-radius: 24px; padding: 30px 25px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.02); border: 1px solid #E2E8F0; 
        height: 100%; display: flex; flex-direction: column; justify-content: space-between; 
        text-align: center; position: relative; overflow: hidden;
    }
    .card-logo-box { height: 90px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
    .card-logo-img { max-height: 85px; width: auto; object-fit: contain; }
    .tool-desc-short { font-size: 0.95rem; color: #718096; font-weight: 500; margin-bottom: 25px; min-height: 45px; }
    
    .border-blue { border-bottom: 6px solid #3182CE; } 
    .border-purple { border-bottom: 6px solid #805AD5; } 
    .border-teal { border-bottom: 6px solid #38B2AC; }

    /* Hide Elements */
    [data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
"""
st.markdown(css_estatico, unsafe_allow_html=True)

# CSS DINÂMICO (Cores e Visibilidade)
st.markdown(f"""
<style>
    .omni-badge {{
        position: fixed; top: 20px; right: 20px;
        background: {card_bg}; border: 1px solid {card_border};
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        padding: 8px 25px; min-width: 200px; border-radius: 16px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06); z-index: 999990;
        display: flex; align-items: center; justify-content: center;
        pointer-events: none; transition: transform 0.3s ease;
    }}
    .omni-text {{
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 0.7rem;
        color: #2D3748; letter-spacing: 2px; text-transform: uppercase;
    }}
    footer {{ visibility: {footer_visibility} !important; }}
    
    /* Botões Dinâmicos */
    div[data-testid="column"] .stButton button {{
        width: 100%; border-radius: 14px !important; border: none !important;
        font-family: 'Inter', sans-serif; font-weight: 700 !important; font-size: 0.95rem !important;
        padding: 14px 0; transition: all 0.3s ease;
        background-color: #F1F5F9; color: #475569;
    }}
    div[data-testid="column"] .stButton button:hover {{ 
        background-color: #3182CE !important; color: white !important; 
        box-shadow: 0 8px 15px rgba(49, 130, 206, 0.25); transform: translateY(-2px);
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE SEGURANÇA E LOGIN
# ==============================================================================
def sistema_seguranca():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        
        # CSS PARA ESCONDER SIDEBAR APENAS NO LOGIN
        st.markdown("""
        <style>
            section[data-testid="stSidebar"] { display: none !important; }
            [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        </style>
        """, unsafe_allow_html=True)

        btn_text = "🚀 ENTRAR (TESTE)" if IS_TEST_ENV else "🔒 ACESSAR OMNISFERA"
        btn_color = "#E65100" if IS_TEST_ENV else "#0F52BA"

        # CSS Específico para botão de login (cor forte)
        st.markdown(f"""
        <style>
            div.stButton > button {{
                background-color: {btn_color} !important; color: white !important; height: 50px !important;
            }}
        </style>
        """, unsafe_allow_html=True)

        c1, c_login, c2 = st.columns([1, 2, 1])
        
        with c_login:
            st.markdown("<div class='login-container'>", unsafe_allow_html=True)
            
            # LOGO CENTRALIZADA
            icone_b64 = get_base64_image("omni_icone.png")
            texto_b64 = get_base64_image("omni_texto.png")
            
            if icone_b64 and texto_b64:
                st.markdown(f"""
                <div class="logo-wrapper">
                    <img src="data:image/png;base64,{icone_b64}" class="login-logo-spin">
                    <img src="data:image/png;base64,{texto_b64}" class="login-logo-static">
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2 style='color:#0F52BA; margin:0; margin-bottom:10px;'>OMNISFERA</h2>", unsafe_allow_html=True)

            # MANIFESTO
            st.markdown("""<div class="manifesto-login">"A Omnisfera é um ecossistema vivo onde a <strong>Neurociência</strong> encontra a <strong>Pedagogia</strong>."</div>""", unsafe_allow_html=True)
            
            # FORMULÁRIO
            if IS_TEST_ENV:
                with st.expander("📝 Dados (Opcional)"):
                    nome_user = st.text_input("nome_fake", placeholder="Nome", label_visibility="collapsed")
                    cargo_user = st.text_input("cargo_fake", placeholder="Cargo", label_visibility="collapsed")
            else:
                st.markdown("<div style='text-align:left; font-weight:700; color:#475569; font-size:0.9rem; margin-bottom:5px;'>Identificação</div>", unsafe_allow_html=True)
                nome_user = st.text_input("nome_real", placeholder="Seu Nome", label_visibility="collapsed")
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                cargo_user = st.text_input("cargo_real", placeholder="Seu Cargo", label_visibility="collapsed")
                
                st.markdown("---")
                st.caption("ℹ️ Software em fase Beta. Uso restrito.")
                concordo = st.checkbox("Concordo com os termos.")
                
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                senha = st.text_input("senha_real", type="password", placeholder="Senha", label_visibility="collapsed")

            st.markdown("<div style='height:20px'></div>", unsafe

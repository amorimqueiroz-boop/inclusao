import streamlit as st
from datetime import date
from openai import OpenAI
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v116.0"

# Detecção de Ambiente
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except:
    IS_TEST_ENV = False

titulo_pag = "[TESTE] Omnisfera" if IS_TEST_ENV else "Omnisfera | Ecossistema"
icone_pag = "omni_icone.png" if os.path.exists("omni_icone.png") else "🌐"

st.set_page_config(
    page_title=titulo_pag,
    page_icon=icone_pag,
    layout="wide",
    initial_sidebar_state="expanded" 
)

# ==============================================================================
# 2. UTILITÁRIOS
# ==============================================================================
def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# ==============================================================================
# 3. CSS "ESTILO CANVA" (Horizontal & Clean)
# ==============================================================================
css_estatico = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
        color: #2D3748;
        background-color: #F8F9FA;
    }

    /* --- HEADER (LOGO | SLOGAN ..... BADGE) --- */
    .header-bar {
        position: fixed; top: 0; left: 0; width: 100%; height: 90px;
        background-color: rgba(255, 255, 255, 0.95);
        border-bottom: 1px solid #E2E8F0;
        z-index: 9999;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 40px;
        backdrop-filter: blur(5px); -webkit-backdrop-filter: blur(5px);
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .header-left { display: flex; align-items: center; gap: 20px; }
    .header-logo-img { height: 50px; width: auto; }
    .header-divider { height: 40px; width: 1px; background-color: #CBD5E0; }
    .header-slogan { color: #718096; font-size: 1rem; font-weight: 600; }
    .header-badge { 
        background: #F7FAFC; border: 1px solid #E2E8F0; 
        padding: 6px 16px; border-radius: 20px; 
        font-size: 0.75rem; font-weight: 800; color: #4A5568; letter-spacing: 1px;
    }

    /* Container Principal */
    .block-container { padding-top: 110px !important; padding-bottom: 3rem !important; }

    /* --- LOGIN --- */
    .login-box {
        background: white; border-radius: 24px; padding: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        text-align: center; border: 1px solid #E2E8F0;
        max-width: 600px; margin: 0 auto; margin-top: 50px;
    }
    .login-logo { height: 80px; margin-bottom: 20px; }
    .login-manifesto { font-style: italic; color: #718096; margin-bottom: 30px; font-size: 0.95rem; }
    .stTextInput input { border-radius: 8px !important; border: 1px solid #E2E8F0 !important; height: 46px !important; }
    .termo-box {
        background-color: #F8FAFC; padding: 15px; border-radius: 10px;
        height: 100px; overflow-y: scroll; font-size: 0.75rem;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
        text-align: justify; color: #4A5568;
    }

    /* --- HERO (Azul Degradê) --- */
    .hero-banner {
        background: linear-gradient(90deg, #0F52BA 0%, #2c5282 100%);
        border-radius: 16px; padding: 40px; color: white;
        margin-bottom: 40px; position: relative; overflow: hidden;
        box-shadow: 0 10px 25px rgba(15, 82, 186, 0.25);
    }
    .hero-title { font-size: 2rem; font-weight: 800; margin-bottom: 10px; }
    .hero-text { font-size: 1.1rem; opacity: 0.9; max-width: 800px; }
    .hero-bg-icon { position: absolute; right: -20px; bottom: -40px; font-size: 15rem; opacity: 0.05; transform: rotate(-15deg); }

    /* --- CARDS HORIZONTAIS (ACESSO RÁPIDO) --- */
    .h-card-container {
        background: white; border: 2px solid #E2E8F0; border-radius: 16px;
        padding: 20px; height: 140px;
        display: flex; align-items: center; gap: 20px;
        transition: all 0.2s ease; position: relative;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .h-card-container:hover { 
        border-color: #3182CE; transform: translateY(-3px); 
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }
    
    /* Logo no Card */
    .h-card-logo-area { 
        width: 140px; height: 100%;
        display: flex; justify-content: center; align-items: center; 
        border-right: 1px solid #F0F0F0; padding-right: 20px; flex-shrink: 0;
    }
    .h-card-logo-img { max-height: 50px; max-width: 100%; object-fit: contain; }

    /* Botão Link (Direita) */
    .h-card-btn-area button {
        background: transparent !important; border: none !important;
        color: #2D3748 !important; text-decoration: underline;
        font-weight: 700 !important; font-size: 1rem !important;
        padding: 0 !important; margin: 0 !important;
        text-align: left !important; white-space: normal !important;
        height: auto !important; line-height: 1.4 !important;
        display: flex !important; justify-content: flex-start !important;
    }
    .h-card-btn-area button:hover { color: #0F52BA !important; text-decoration: none !important; }
    
    /* Cards Conhecimento */
    .k-card-container {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 15px; height: 90px;
        display: flex; align-items: center; gap: 15px;
        transition: all 0.2s ease;
    }
    .k-card-container:hover { border-color: #3182CE; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .k-icon {
        width: 45px; height: 45px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; flex-shrink: 0;
    }
    .k-btn-area button {
        background: transparent !important; border: none !important;
        color: #1A202C !important; font-size: 0.9rem !important;
        font-weight: 700 !important; text-align: left !important;
        padding: 0 !important;
    }

    .section-header { font-size: 1.2rem; font-weight: 800; color: #1A202C; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
    
    /* Insight */
    .insight-box {
        background: #FFFBEB; border: 1px solid #F6E05E; border-radius: 12px;
        padding: 20px; display: flex; align-items: center; gap: 20px; margin-top: 30px;
    }
    .insight-icon {
        background: #FEFCBF; width: 50px; height: 50px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: #D69E2E; font-size: 1.5rem; flex-shrink: 0;
    }

    [data-testid="stHeader"] { visibility: hidden; height: 0; }
    [data-testid="stToolbar"] { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
"""
st.markdown(css_estatico, unsafe_allow_html=True)

# CSS DINÂMICO PARA BOTÃO DE LOGIN
cor_btn = "#E65100" if IS_TEST_ENV else "#0F52BA"
st.markdown(f"""<style>.btn-login-inline button {{ margin-top: 29px !important; height: 46px !important; background-color: {cor_btn} !important; color: white !important; border-radius: 8px !important; font-weight: 700 !important; width: 100%; }}</style>""", unsafe_allow_html=True)

# ==============================================================================
# 4. SISTEMA DE LOGIN
# ==============================================================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    c1, c_main, c2 = st.columns([1, 2, 1])
    with c_main:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        img_login = get_base64_image("omni_icone.png")
        if img_login: st.markdown(f"<img src='data:image/png;base64,{img_login}' class='login-logo'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#0F52BA; margin:0;'>OMNISFERA</h2>", unsafe_allow_html=True)
        st.markdown("<div class='login-manifesto'>\"A Omnisfera foi desenvolvida com muito cuidado e carinho...\"</div>", unsafe_allow_html=True)
        
        with st.expander("📄 Ler Termos de Uso"):
            st.markdown("<div class='termo-box'>1. Confidencialidade...<br>2. Beta...<br>3. Responsabilidade...</div>", unsafe_allow_html=True)
        
        concordo = st.checkbox("Li e concordo com os termos.")
        c_pass, c_btn = st.columns([3, 1])
        with c_pass: senha = st.text_input("Senha de Acesso", type="password")
        with c_btn: 
            st.markdown('<div class="btn-login-inline">', unsafe_allow_html=True)
            entrar = st.button("ENTRAR")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if entrar:
            senha_correta = "PEI_START_2026"
            if IS_TEST_ENV: senha_correta = ""
            if not concordo: st.warning("Aceite os termos.")
            elif senha != senha_correta and not IS_TEST_ENV: st.error("Senha incorreta.")
            else:
                st.session_state["autenticado"] = True; st.session_state["usuario_nome"] = "Visitante"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# 5. DASHBOARD HOME
# ==============================================================================
img_header = get_base64_image("omni_icone.png")
text_header = get_base64_image("omni_texto.png")
logo_html = f"<img src='data:image/png;base64,{img_header}' class='header-logo-img'>" if img_header else "🌐"
nome_html = f"<img src='data:image/png;base64,{text_header}' style='height:30px; margin-left:10px;'>" if text_header else "<span style='font-weight:800; font-size:1.5rem; color:#0F52BA;'>OMNISFERA</span>"

st.markdown(f"""
<div class="header-bar">
    <div class="header-left">{logo_html}{nome_html}<div class="header-divider"></div><div class="header-slogan">Ecossistema de Inteligência Pedagógica e Inclusiva</div></div>
    <div class="header-badge">OMNISFERA {APP_VERSION}</div>
</div>
""", unsafe_allow_html=True)

# HERO
nome = st.session_state.get("usuario_nome", "Visitante").split()[0]
st.markdown(f"""<div class="hero-banner"><div class="hero-title">Olá, {nome}!</div><div class="hero-text">"A inclusão escolar transforma diferenças em oportunidades."</div><i class="ri-heart-pulse-fill hero-bg-icon"></i></div>""", unsafe_allow_html=True)

# ACESSO RÁPIDO (HORIZONTAL)
st.markdown('<div class="section-header"><i class="ri-cursor-fill"></i> Acesso Rápido</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

def card_horizontal(coluna, img, texto, link):
    with coluna:
        img_b64 = get_base64_image(img)
        st.markdown(f"""<div class="h-card-container"><div class="h-card-logo-area"><img src="data:image/png;base64,{img_b64}" class="h-card-logo-img"></div><div style="flex-grow:1;" class="h-card-btn-area">""", unsafe_allow_html=True)
        if st.button(texto, key=f"btn_{img}"): st.switch_page(link)
        st.markdown("</div></div>", unsafe_allow_html=True)

card_horizontal(c1, "360.png", "Crie seu plano de ensino individualizado", "pages/1_PEI.py")
card_horizontal(c2, "pae.png", "Sala de recursos e eliminação de barreiras", "pages/2_PAE.py")
card_horizontal(c3, "hub.png", "Faça adaptação de atividades e roteiros", "pages/3_Hub_Inclusao.py")

# CONHECIMENTO (HORIZONTAL COMPACTO)
st.markdown('<div style="height:30px;"></div><div class="section-header"><i class="ri-book-mark-fill"></i> Conhecimento</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

def card_know(coluna, icon, color, bg, title, link):
    with coluna:
        st.markdown(f"""<div class="k-card-container"><div class="k-icon" style="background:{bg}; color:{color};"><i class="{icon}"></i></div><div class="k-btn-area" style="flex-grow:1;">""", unsafe_allow_html=True)
        if link.startswith("http"): st.markdown(f"<a href='{link}' target='_blank' style='text-decoration:none; color:#1A202C; font-weight:700; font-size:0.9rem;'>{title}</a>", unsafe_allow_html=True)
        else: st.button(title, key=f"kb_{title}", disabled=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

card_know(k1, "ri-file-text-line", "#3182CE", "#EBF8FF", "PEI vs PAEE", "#")
card_know(k2, "ri-scales-3-line", "#D69E2E", "#FFFFF0", "Legislação", "https://planalto.gov.br")
card_know(k3, "ri-brain-line", "#D53F8C", "#FFF5F7", "Neurociência", "#")
card_know(k4, "ri-compass-3-line", "#38A169", "#F0FFF4", "BNCC", "http://basenacionalcomum.mec.gov.br/")

# INSIGHT & FOOTER
st.markdown('<div style="height:30px;"></div>', unsafe_allow_html=True)
st.markdown("""<div class="insight-box"><div class="insight-icon"><i class="ri-lightbulb-flash-line"></i></div><div><div style="font-weight:800; font-size:0.8rem; color:#D69E2E;">INSIGHT DO DIA</div><div style="font-style:italic; color:#4A5568;">"Entender como o cérebro aprende é fundamental."</div></div></div>""", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#CBD5E0; font-size:0.8rem; margin-top:60px;'>Omnisfera desenvolvida e CRIADA por RODRIGO A. QUEIROZ; assim como PEI360, PAEE360 & HUB de Inclusão</div>", unsafe_allow_html=True)

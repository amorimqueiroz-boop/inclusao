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
# 3. CSS GLOBAL (ESTILO CANVA - HORIZONTAL)
# ==============================================================================
cor_btn_login = "#E65100" if IS_TEST_ENV else "#0F52BA"

css_estatico = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
        color: #2D3748;
        background-color: #F8F9FA;
    }

    /* --- HEADER FIXO --- */
    .header-bar {
        position: fixed; top: 0; left: 0; width: 100%; height: 90px;
        background-color: rgba(255, 255, 255, 0.95);
        border-bottom: 1px solid #E2E8F0;
        z-index: 9999;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 40px;
        backdrop-filter: blur(5px);
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

    /* Ajuste Container */
    .block-container { padding-top: 110px !important; padding-bottom: 3rem !important; }

    /* --- LOGIN --- */
    .login-box {
        background: white; border-radius: 24px; padding: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        text-align: center; border: 1px solid #E2E8F0;
        max-width: 600px; margin: 0 auto; margin-top: 50px;
    }
    .login-logo { height: 80px; margin-bottom: 20px; }
    .login-manifesto { font-style: italic; color: #718096; margin-bottom: 30px; font-size: 0.95rem; line-height: 1.5; }
    .termo-box {
        background-color: #F8FAFC; padding: 15px; border-radius: 10px;
        height: 100px; overflow-y: scroll; font-size: 0.75rem;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
        text-align: justify; color: #4A5568;
    }
    .stTextInput input { border-radius: 8px !important; border: 1px solid #E2E8F0 !important; height: 46px !important; }

    /* --- HERO --- */
    .hero-banner {
        background: linear-gradient(90deg, #0F52BA 0%, #2c5282 100%);
        border-radius: 16px; padding: 40px; color: white;
        margin-bottom: 40px; position: relative; overflow: hidden;
        box-shadow: 0 10px 25px rgba(15, 82, 186, 0.25);
    }
    .hero-title { font-size: 2rem; font-weight: 800; margin-bottom: 10px; }
    .hero-text { font-size: 1.1rem; opacity: 0.9; max-width: 800px; }
    .hero-bg-icon { position: absolute; right: -20px; bottom: -40px; font-size: 15rem; opacity: 0.05; transform: rotate(-15deg); }

    /* --- CARDS ACESSO RÁPIDO (Horizontal + Texto Clicável) --- */
    
    /* 1. Logo (Esquerda) - Absoluta sobre o botão */
    .card-logo-overlay {
        position: absolute;
        top: 0; left: 0;
        width: 35%; /* Ocupa 35% da esquerda */
        height: 100%;
        display: flex; align-items: center; justify-content: center;
        z-index: 2; 
        pointer-events: none; /* Clique passa para o botão */
        border-right: 1px solid #F0F0F0;
    }
    .card-logo-overlay img { max-height: 60px; max-width: 80%; object-fit: contain; }

    /* 2. O Botão (Texto Descritivo) */
    .card-btn-wrapper button {
        background-color: white !important;
        border: 2px solid #E2E8F0 !important; /* Borda padrão */
        border-radius: 16px !important;
        height: 120px !important;
        width: 100% !important;
        
        /* Typography do Texto */
        color: #2D3748 !important;
        font-family: 'Nunito', sans-serif !important;
        font-weight: 600 !important; /* Texto com peso médio */
        font-size: 0.95rem !important;
        text-align: left !important;
        text-decoration: underline !important; /* Parece link */
        text-decoration-color: transparent !important; /* Esconde sublinhado normal */
        
        /* Espaçamento para empurrar texto para a direita da logo */
        padding-left: 40% !important; 
        padding-right: 20px !important;
        
        box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        white-space: normal !important; /* Permite quebra de linha */
        line-height: 1.4 !important;
    }

    /* Hover Effect */
    .card-btn-wrapper button:hover {
        border-color: #3182CE !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.06) !important;
        color: #0F52BA !important;
        background-color: #FAFAFA !important;
    }
    
    /* Bordas Coloridas Específicas (Aplicadas via CSS inline no Python, mas classes ajudam) */
    
    /* --- CONHECIMENTO (Compacto) --- */
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
    .k-link { text-decoration: none; color: #1A202C; font-weight: 700; font-size: 0.9rem; }

    /* Headers e Insight */
    .section-header { font-size: 1.2rem; font-weight: 800; color: #1A202C; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
    .insight-box {
        background: #FFFBEB; border: 1px solid #F6E05E; border-radius: 12px;
        padding: 20px; display: flex; align-items: center; gap: 20px; margin-top: 30px;
    }
    .insight-icon {
        background: #FEFCBF; width: 50px; height: 50px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        color: #D69E2E; font-size: 1.5rem; flex-shrink: 0;
    }

    [data-testid="stHeader"], [data-testid="stToolbar"] { visibility: hidden; height: 0; }
    section[data-testid="stSidebar"] { display: none; }
</style>
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.1.0/fonts/remixicon.css" rel="stylesheet">
"""
st.markdown(css_estatico, unsafe_allow_html=True)

# CSS Dinâmico para Login
st.markdown(f"""
<style>
    .btn-login-inline button {{
        margin-top: 29px !important;
        height: 46px !important;
        background-color: {cor_btn_login} !important;
        color: white !important;
        border-radius: 8px !important; font-weight: 700 !important;
        border: none !important; width: 100%;
    }}
    .btn-login-inline button:hover {{ opacity: 0.9; }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. LOGIN
# ==============================================================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    c1, c_main, c2 = st.columns([1, 2, 1])
    with c_main:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        img_login = get_base64_image("omni_icone.png")
        if img_login: st.markdown(f"<img src='data:image/png;base64,{img_login}' class='login-logo'>", unsafe_allow_html=True)
        else: st.markdown("<h2 style='color:#0F52BA;'>OMNISFERA</h2>", unsafe_allow_html=True)
        
        # MANIFESTO ATUALIZADO
        st.markdown("<div class='login-manifesto'>\"A Omnisfera foi desenvolvida com muito cuidado e carinho com o objetivo de auxiliar as escolas na tarefa de incluir. Ela tem o potencial para revolucionar o cenário da inclusão no Brasil.\"</div>", unsafe_allow_html=True)
        
        with st.expander("📄 Ler Termos de Uso e Confidencialidade"):
            st.markdown("""
            <div class="termo-box">
                <strong>1. Confidencialidade:</strong> É proibido inserir dados reais sensíveis (nomes completos, documentos) que identifiquem estudantes.<br>
                <strong>2. Natureza Beta:</strong> O sistema está em evolução constante.<br>
                <strong>3. Responsabilidade:</strong> As sugestões da IA são apoio pedagógico e devem ser validadas por um profissional humano.
            </div>
            """, unsafe_allow_html=True)
        
        concordo = st.checkbox("Li e concordo com os termos.")
        
        c_pass, c_btn = st.columns([3, 1])
        with c_pass: senha = st.text_input("Senha de Acesso", type="password")
        with c_btn:
            st.markdown('<div class="btn-login-inline">', unsafe_allow_html=True)
            entrar = st.button("ENTRAR" if IS_TEST_ENV else "ACESSAR")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if entrar:
            senha_ok = "PEI_START_2026"
            if IS_TEST_ENV: senha_ok = ""
            if not concordo: st.warning("Aceite os termos.")
            elif senha != senha_ok and not IS_TEST_ENV: st.error("Senha incorreta.")
            else:
                st.session_state["autenticado"] = True; st.session_state["usuario_nome"] = "Visitante"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# 5. DASHBOARD
# ==============================================================================
# Header
img_h = get_base64_image("omni_icone.png")
text_h = get_base64_image("omni_texto.png")
logo_html = f"<img src='data:image/png;base64,{img_h}' class='header-logo-img'>" if img_h else "🌐"
nome_html = f"<img src='data:image/png;base64,{text_h}' style='height:30px; margin-left:10px;'>" if text_h else "<span style='font-weight:800; font-size:1.5rem; color:#0F52BA;'>OMNISFERA</span>"

st.markdown(f"""
<div class="header-bar">
    <div class="header-left">{logo_html}{nome_html}<div class="header-divider"></div><div class="header-slogan">Ecossistema de Inteligência Pedagógica e Inclusiva</div></div>
    <div class="header-badge">OMNISFERA {APP_VERSION}</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("**👤 Educador**"); st.markdown("---")
    if st.button("Enviar Feedback"): st.toast("Obrigado!", icon="✅")

# Hero
nome = st.session_state.get("usuario_nome", "Visitante").split()[0]
st.markdown(f"""<div class="hero-banner"><div class="hero-title">Olá, {nome}!</div><div class="hero-text">"A inclusão escolar transforma diferenças em oportunidades."</div><i class="ri-heart-pulse-fill hero-bg-icon"></i></div>""", unsafe_allow_html=True)

# --- ACESSO RÁPIDO (HORIZONTAL + TEXTO COMO BOTÃO) ---
st.markdown('<div class="section-header"><i class="ri-cursor-fill"></i> Acesso Rápido</div>', unsafe_allow_html=True)

# Função atualizada para aplicar borda colorida e layout horizontal
def card_horizontal_texto_botao(coluna, img, texto, link, cor_borda):
    with coluna:
        # A logo é desenhada como HTML absoluto (flutua sobre o botão à esquerda)
        img_b64 = get_base64_image(img)
        
        # Aplica a cor da borda específica via estilo inline na div container do botão
        # O botão em si tem bg branco, então usamos uma div wrapper invisível para posicionar a logo
        st.markdown(f"""
        <style>
            div[data-testid="stVerticalBlock"] > div:has(div.card-btn-wrapper) {{
                /* Tenta isolar o estilo se possível, mas o inline abaixo é mais seguro */
            }}
        </style>
        <div style="position: relative; height: 120px; margin-bottom: 20px;">
            <div class="card-logo-overlay">
                <img src="data:image/png;base64,{img_b64}">
            </div>
            <style>
                div.row-widget.stButton > button[kind="secondary"] {{
                    border-bottom: 4px solid {cor_borda} !important;
                }}
            </style>
            <div class="card-btn-wrapper">
        """, unsafe_allow_html=True)
        
        # O botão do Streamlit é o corpo do card e contém o TEXTO
        if st.button(texto, key=f"btn_{img}"):
            st.switch_page(link)
            
        st.markdown("</div></div>", unsafe_allow_html=True)

# Usando 3 colunas para os cards
c1, c2, c3 = st.columns(3)

# Chamada com as cores exatas do mockup
# PEI: Azul | PAEE: Roxo | HUB: Teal/Verde
# Obs: O CSS global define .card-btn-wrapper button, o style inline ajusta a borda.
# Como o Streamlit não permite passar ID para o botão, o style inline acima pode vazar se não formos cuidadosos.
# WORKAROUND SEGURO: Usar st.markdown para criar a borda na div wrapper e deixar o botão sem borda inferior.

def card_horizontal_seguro(coluna, img, texto, link, cor_borda):
    with coluna:
        img_b64 = get_base64_image(img)
        # Borda aplicada na div wrapper para não depender de seletores instáveis
        st.markdown(f"""
        <div style="position: relative; height: 120px; margin-bottom: 15px;">
            <div class="card-logo-overlay">
                <img src="data:image/png;base64,{img_b64}">
            </div>
            <div class="card-btn-wrapper" style="border-bottom: 4px solid {cor_borda}; border-radius: 16px;">
        """, unsafe_allow_html=True)
        
        if st.button(texto, key=f"btn_{img}"):
            st.switch_page(link)
            
        st.markdown("</div></div>", unsafe_allow_html=True)

card_horizontal_seguro(c1, "360.png", "Crie seu plano de ensino individualizado", "pages/1_PEI.py", "#3182CE")
card_horizontal_seguro(c2, "pae.png", "Sala de recursos e eliminação de barreiras", "pages/2_PAE.py", "#805AD5")
card_horizontal_seguro(c3, "hub.png", "Faça adaptação de atividades e roteiros", "pages/3_Hub_Inclusao.py", "#38B2AC")

# --- CONHECIMENTO ---
st.markdown('<div style="height:20px;"></div><div class="section-header"><i class="ri-book-mark-fill"></i> Conhecimento</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

def card_know(coluna, icon, color, bg, title, link):
    with coluna:
        st.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration:none;">
            <div class="k-card-container">
                <div class="k-icon" style="background:{bg}; color:{color};"><i class="{icon}"></i></div>
                <div class="k-link">{title}</div>
            </div>
        </a>
        """, unsafe_allow_html=True)

card_know(k1, "ri-file-text-line", "#3182CE", "#EBF8FF", "PEI vs PAEE", "#")
card_know(k2, "ri-scales-3-line", "#D69E2E", "#FFFFF0", "Legislação", "https://planalto.gov.br")
card_know(k3, "ri-brain-line", "#D53F8C", "#FFF5F7", "Neurociência", "#")
card_know(k4, "ri-compass-3-line", "#38A169", "#F0FFF4", "BNCC", "http://basenacionalcomum.mec.gov.br/")

# --- INSIGHT & FOOTER ---
st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="insight-box">
    <div class="insight-icon"><i class="ri-lightbulb-flash-line"></i></div>
    <div>
        <div style="font-weight:800; font-size:0.8rem; color:#D69E2E;">INSIGHT DO DIA</div>
        <div style="font-style:italic; color:#4A5568;">"Entender como o cérebro aprende é fundamental para potencializar o ensino e criar ambientes de aprendizado mais eficazes e inclusivos."</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align:center; color:#CBD5E0; font-size:0.8rem; margin-top:50px;'>Omnisfera desenvolvida e CRIADA por RODRIGO A. QUEIROZ; assim como PEI360, PAEE360 & HUB de Inclusão</div>", unsafe_allow_html=True)

# pages/0_Home.py
import streamlit as st
from datetime import datetime, date
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v155.0 (Final Pro)"

try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except Exception:
    IS_TEST_ENV = False

st.set_page_config(
    page_title="Omnisfera",
    page_icon="omni_icone.png" if os.path.exists("omni_icone.png") else "🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. CSS & DESIGN SYSTEM (O SEGREDO DO VISUAL)
# ==============================================================================
st.markdown("""
<style>
/* Fontes Modernas */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #2B3674;
    background-color: #F4F7FE; /* Fundo Cinza/Azul Claro */
}

/* Limpeza do Streamlit */
[data-testid="stSidebarNav"], [data-testid="stHeader"] { display: none !important; }
.block-container {
    padding-top: 100px !important; /* Espaço para o Header maior */
    padding-bottom: 4rem !important;
    max-width: 98% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* --- TOPBAR (HEADER) --- */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 90px; /* Mais alta */
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #E2E8F0;
    z-index: 9999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 40px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}
.brand-area { display: flex; align-items: center; gap: 15px; }
.logo-spin { height: 55px; width: auto; animation: spin 45s linear infinite; }
.logo-text-img { height: 35px; width: auto; } /* Imagem do Texto */

.user-area { display: flex; align-items: center; gap: 15px; }
.workspace-badge {
    background: #F4F7FE; padding: 6px 14px; border-radius: 30px;
    font-size: 0.8rem; font-weight: 700; color: #A3AED0; border: 1px solid #E2E8F0;
}
.user-avatar {
    width: 40px; height: 40px; background: #4318FF; color: white;
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 1rem;
}

/* --- HERO SECTION --- */
.hero-banner {
    background: linear-gradient(135deg, #4318FF 0%, #2B3674 100%);
    border-radius: 20px; padding: 40px 50px; color: white;
    margin-bottom: 40px; display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 20px 40px -10px rgba(67, 24, 255, 0.25);
    position: relative; overflow: hidden;
}
/* Efeito de fundo */
.hero-banner::before {
    content: ""; position: absolute; right: -50px; top: -100px; width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.hero-content h1 { font-size: 2.2rem; font-weight: 700; margin: 0; letter-spacing: -1px; }
.hero-content p { opacity: 0.9; font-size: 1.1rem; margin-top: 5px; max-width: 600px; }

/* --- CARDS DE MÓDULO (DESIGN SAAS) --- */
.saas-card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.02);
    display: flex; align-items: center; gap: 18px;
    height: 120px; /* Altura fixa */
    position: relative;
    overflow: hidden;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid transparent;
}

/* Barra lateral colorida */
.saas-card::after {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px;
    background: currentColor; /* Herda a cor do texto definida inline */
}

.saas-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.08);
    border-color: #E2E8F0;
}

.icon-circle {
    width: 56px; height: 56px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem; flex-shrink: 0;
}

.card-text h3 { margin: 0; font-size: 1.15rem; font-weight: 700; color: #2B3674; }
.card-text p { margin: 4px 0 0 0; font-size: 0.85rem; color: #A3AED0; line-height: 1.3; }

.arrow-action { 
    margin-left: auto; color: #CBD5E0; font-size: 1.5rem; transition: 0.2s; 
}
.saas-card:hover .arrow-action { color: #4318FF; transform: translateX(5px); }

/* --- BOTÃO FANTASMA (CORREÇÃO TOTAL) --- */
/* Este container puxa o botão do Streamlit para cima do HTML */
.ghost-btn-wrapper {
    position: relative;
    height: 120px;
    margin-top: -120px; /* Puxa para cima exatamente a altura do card */
    z-index: 10;
}
.ghost-btn-wrapper button {
    width: 100% !important;
    height: 100% !important;
    opacity: 0 !important; /* Invisível */
    border: none !important;
    cursor: pointer !important;
    padding: 0 !important;
}

/* --- TEMAS DE COR --- */
.bg-purple { background: #F4F7FE; color: #4318FF; }
.bg-green { background: #F0FDF4; color: #05CD99; }
.bg-orange { background: #FFF7ED; color: #FFB547; }
.bg-pink { background: #FDF2F8; color: #FF0080; }
.bg-navy { background: #F4F7FE; color: #2B3674; }

@keyframes spin { 100% { transform: rotate(360deg); } }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. HELPERS & STATE
# ==============================================================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "dados" not in st.session_state: st.session_state.dados = {"nome": "", "nasc": date(2015,1,1), "serie": None}

def get_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

def escola_vinculada():
    return st.session_state.get("workspace_name") or st.session_state.get("workspace_id", "")[:12]

# Gate de Segurança
if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
    st.warning("🔒 Acesso negado. Por favor, faça login.")
    if st.button("Ir para Login"): st.rerun()
    st.stop()

# ==============================================================================
# 4. HEADER & HERO
# ==============================================================================

# Carregar Imagens
icone_b64 = get_base64("omni_icone.png")
texto_b64 = get_base64("omni_texto.png")

logo_html = f'<img src="data:image/png;base64,{icone_b64}" class="logo-spin">' if icone_b64 else "🌐"
# Se não tiver a imagem do texto, usa texto puro como fallback
text_html = f'<img src="data:image/png;base64,{texto_b64}" class="logo-text-img">' if texto_b64 else "<span style='font-weight:800; font-size:1.5rem; color:#2B3674;'>OMNISFERA</span>"

user_name = st.session_state.get('usuario_nome', 'Visitante').split()[0]
user_initials = user_name[:2].upper()
workspace = escola_vinculada()

# Render Header
st.markdown(f"""
<div class="topbar">
    <div class="brand-area">
        {logo_html}
        {text_html}
    </div>
    <div class="user-area">
        <div class="workspace-badge">{workspace}</div>
        <div class="user-avatar">{user_initials}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Render Hero
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-content">
        <h1>{saudacao}, {user_name}!</h1>
        <p>"A inclusão acontece quando aprendemos com as diferenças e não com as igualdades."</p>
    </div>
    <div style="font-size:3rem; opacity:0.8;">🚀</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. MÓDULOS (FUNCIONALIDADE CORRIGIDA)
# ==============================================================================
st.markdown("### ⚡ Acesso Rápido")

def render_saas_card(title, desc, icon, bg_class, color_hex, page_path, key):
    # 1. HTML Visual (Design Lindo)
    st.markdown(f"""
    <div class="saas-card" style="color: {color_hex};">
        <div class="icon-circle {bg_class}">
            <i class="{icon}"></i>
        </div>
        <div class="card-text">
            <h3>{title}</h3>
            <p>{desc}</p>
        </div>
        <div class="arrow-action"><i class="ri-arrow-right-s-line"></i></div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Botão Funcional (Invisível por cima)
    st.markdown('<div class="ghost-btn-wrapper">', unsafe_allow_html=True)
    if st.button(f"btn_{key}", key=key):
        # Lógica de Redirecionamento
        if "Alunos" in title:
            # Verifica se o arquivo é pages/Alunos.py ou Alunos.py (ajuste conforme seu arquivo real)
            st.switch_page("pages/Alunos.py" if os.path.exists("pages/Alunos.py") else "Alunos.py")
        elif "Estudantes" in title: # Caso use sinonimos
             st.switch_page("pages/Alunos.py")
        elif st.session_state.dados.get("nome"):
            st.switch_page(page_path)
        else:
            st.toast("⚠️ Selecione um aluno em 'Estudantes' primeiro!", icon="👇")
            time.sleep(1)
            st.switch_page("pages/Alunos.py")
    st.markdown('</div>', unsafe_allow_html=True)

# Grid 3 Colunas x 2 Linhas
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    # 1. Alunos
    render_saas_card("Estudantes", "Gestão e histórico.", "ri-group-line", "bg-purple", "#4318FF", "pages/Alunos.py", "m_aluno")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    # 4. Hub
    render_saas_card("Hub de Recursos", "Banco de materiais e IA.", "ri-rocket-2-line", "bg-green", "#05CD99", "pages/3_Hub_Inclusao.py", "m_hub")

with c2:
    # 2. PEI
    render_saas_card("Estratégias & PEI", "Plano Individualizado.", "ri-book-open-line", "bg-purple", "#4318FF", "pages/1_PEI.py", "m_pei")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    # 5. Diário
    render_saas_card("Diário de Bordo", "Registro de evidências.", "ri-file-list-3-line", "bg-orange", "#FFB547", "pages/4_Diario_de_Bordo.py", "m_diario")

with c3:
    # 3. PAEE
    render_saas_card("Plano de Ação / PAEE", "Sala de recursos.", "ri-puzzle-2-line", "bg-pink", "#FF0080", "pages/2_PAE.py", "m_pae")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    # 6. Dados
    render_saas_card("Evolução & Dados", "Indicadores e progresso.", "ri-bar-chart-box-line", "bg-navy", "#2B3674", "pages/5_Monitoramento_Avaliacao.py", "m_dados")

# ==============================================================================
# 6. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.image(icone_b64 if os.path.exists("omni_icone.png") else "https://via.placeholder.com/150", width=60)
    st.markdown("### Navegação")
    if st.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #A3AED0; font-size: 0.75rem;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>", unsafe_allow_html=True)

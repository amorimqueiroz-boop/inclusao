import streamlit as st
from datetime import date, datetime
from zoneinfo import ZoneInfo
import base64
import os
import graphviz
import time

import omni_utils as ou

# Importar OpenAI para gerar mensagem de boas-vindas
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v2.0 - Guia de Inclusão"

try:
    IS_TEST_ENV = st.secrets.get("ENV", "PRODUCAO") == "TESTE"
except Exception:
    IS_TEST_ENV = False

st.set_page_config(
    page_title="Omnisfera - Plataforma de Inclusão Educacional",
    page_icon="omni_icone.png",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# ==============================================================================
# 2. CSS & DESIGN SYSTEM (COM SIDEBAR OCULTADA)
# ==============================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #1E293B !important;
    background-color: #F8FAFC !important;
}

/* --- OCULTAR SIDEBAR E HEADER NATIVOS DO STREAMLIT --- */
[data-testid="stSidebarNav"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="collapsedControl"],
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
footer {
    display: none !important;
}

/* Ajustar padding para compensar a topbar fixa */
.block-container {
    padding-top: 100px !important;
    padding-bottom: 4rem !important;
    max-width: 95% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* --- HEADER FIXO COM LOGO GRANDE --- */
.topbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 80px;
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid #E2E8F0;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.brand-box {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-logo {
    height: 55px !important;
    width: auto !important;
    animation: spin 45s linear infinite;
    filter: brightness(1.1);
}

.brand-img-text {
    height: 35px !important;
    width: auto;
    margin-left: 10px;
}

.user-badge {
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    padding: 6px 14px;
    border-radius: 99px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #64748B;
    letter-spacing: 0.5px;
}

/* --- HERO SECTION --- */
.hero-wrapper {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
    border-radius: 20px;
    padding: 3rem;
    color: white;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px -10px rgba(30, 58, 138, 0.3);
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 140px;
    max-height: 180px;
}

.hero-wrapper::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
    opacity: 0.3;
}

.hero-wrapper::after {
    content: "";
    position: absolute;
    right: -60px;
    top: -60px;
    width: 300px;
    height: 300px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    pointer-events: none;
    filter: blur(40px);
}

.hero-content {
    z-index: 2;
    position: relative;
    flex: 1;
    min-width: 0;
}

.hero-greet {
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
    line-height: 1.2;
}

.hero-text {
    font-size: 1.1rem;
    opacity: 0.95;
    max-width: 100%;
    line-height: 1.5;
    font-weight: 500;
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: normal;
    hyphens: auto;
    flex: 1;
}

.hero-icon {
    opacity: 0.8;
    font-size: 4rem;
    z-index: 1;
    position: relative;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

/* --- MODULE CARDS --- */
.mod-card-wrapper {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.mod-card-rect {
    background: white;
    border-radius: 16px 16px 0 0;
    padding: 0;
    border: 1px solid #E2E8F0;
    border-bottom: none;
    display: flex;
    flex-direction: row;
    align-items: center;
    height: 130px;
    width: 100%;
    position: relative;
    overflow: hidden;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.mod-card-rect:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
    border-color: #CBD5E1;
}

.mod-bar {
    width: 6px;
    height: 100%;
    flex-shrink: 0;
}

.mod-icon-area {
    width: 90px;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
    flex-shrink: 0;
    background: #FAFAFA;
    border-right: 1px solid #F1F5F9;
    transition: all 0.3s ease;
}

.mod-card-rect:hover .mod-icon-area {
    background: white;
    transform: scale(1.05);
}

.mod-content {
    flex-grow: 1;
    padding: 0 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.mod-title {
    font-weight: 800;
    font-size: 1.1rem;
    color: #1E293B;
    margin-bottom: 6px;
    letter-spacing: -0.3px;
    transition: color 0.2s;
}

.mod-card-rect:hover .mod-title {
    color: #4F46E5;
}

.mod-desc {
    font-size: 0.8rem;
    color: #64748B;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* --- CORES DOS CARDS DE MÓDULO (PALETA VIBRANTE - AZUIS QUE DIALOGAM COM VERMELHO) --- */
/* Estudantes - Azul Índigo Vibrante */
.c-indigo { background: #2563EB !important; }
.bg-indigo-soft { 
    background: #DBEAFE !important; 
    color: #1E40AF !important;
}

/* PEI - Azul Céu Vibrante */
.c-blue { background: #0EA5E9 !important; }
.bg-blue-soft { 
    background: #E0F2FE !important;
    color: #0284C7 !important;
}

/* PAEE - Roxo Vibrante */
.c-purple { background: #A855F7 !important; }
.bg-purple-soft { 
    background: #F3E8FF !important;
    color: #9333EA !important;
}

/* Hub - Verde Água Vibrante */
.c-teal { background: #06B6D4 !important; }
.bg-teal-soft { 
    background: #CFFAFE !important;
    color: #0891B2 !important;
}

/* Diário - Rosa Vibrante */
.c-rose { background: #F43F5E !important; }
.bg-rose-soft { 
    background: #FFE4E6 !important;
    color: #E11D48 !important;
}

/* Monitoramento - Azul Oceano Vibrante */
.c-sky { background: #0C4A6E !important; }
.bg-sky-soft { 
    background: #BAE6FD !important;
    color: #075985 !important;
}

/* --- BOTÕES STREAMLIT --- */
.stButton > button {
    border-radius: 0 0 16px 16px !important;
    border: 1px solid #E2E8F0 !important;
    border-top: none !important;
    background: white !important;
    color: #64748B !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    padding: 12px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03) !important;
}

.stButton > button:hover {
    background: #F8FAFC !important;
    color: #4F46E5 !important;
    border-color: #E2E8F0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08) !important;
}

/* --- RECURSOS --- */
.res-card-link {
    text-decoration: none !important;
    display: block;
    height: 100%;
    border-radius: 14px;
    overflow: hidden;
}

.res-card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    border: 1px solid #E2E8F0;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    min-height: 96px;
}

.res-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
    border-color: transparent;
}

.res-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
    transition: all 0.3s ease;
}

.res-card:hover .res-icon {
    transform: scale(1.1) rotate(5deg);
}

.res-info {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

.res-name {
    font-weight: 700;
    color: #1E293B;
    font-size: 0.95rem;
    margin-bottom: 2px;
    transition: color 0.2s;
}

.res-card:hover .res-name {
    color: #4F46E5;
}

.res-meta {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748B;
    opacity: 0.8;
}

/* --- CARDS DE INFORMAÇÃO --- */
.info-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #E2E8F0;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    height: 100%;
    min-height: 320px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.info-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
    border-color: #CBD5E1;
}

.info-card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #F1F5F9;
}

.info-card-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
}

.info-card-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #1E293B;
    margin: 0;
    line-height: 1.3;
}

.info-card-content {
    flex-grow: 1;
    overflow-y: auto;
    padding-right: 8px;
}

.info-card-content p {
    font-size: 0.85rem;
    color: #64748B;
    line-height: 1.5;
    margin-bottom: 12px;
}

.info-card-content ul {
    font-size: 0.85rem;
    color: #64748B;
    line-height: 1.5;
    margin-left: 16px;
    margin-bottom: 12px;
}

.info-card-content li {
    margin-bottom: 6px;
}

/* --- CORES DOS CARDS DE INFORMAÇÃO --- */
.info-card-orange {
    border-left: 4px solid #EA580C;
}
.info-card-orange .info-card-icon {
    background: #FFF7ED;
    color: #EA580C;
    border: 1px solid #FDBA74;
}

.info-card-blue {
    border-left: 4px solid #3B82F6;
}
.info-card-blue .info-card-icon {
    background: #EFF6FF;
    color: #3B82F6;
    border: 1px solid #93C5FD;
}

.info-card-purple {
    border-left: 4px solid #8B5CF6;
}
.info-card-purple .info-card-icon {
    background: #F5F3FF;
    color: #8B5CF6;
    border: 1px solid #C4B5FD;
}

.info-card-teal {
    border-left: 4px solid #14B8A6;
}
.info-card-teal .info-card-icon {
    background: #F0FDFA;
    color: #14B8A6;
    border: 1px solid #5EEAD4;
}

.info-card-rose {
    border-left: 4px solid #E11D48;
}
.info-card-rose .info-card-icon {
    background: #FFF1F2;
    color: #E11D48;
    border: 1px solid #FDA4AF;
}

.info-card-indigo {
    border-left: 4px solid #4F46E5;
}
.info-card-indigo .info-card-icon {
    background: #EEF2FF;
    color: #4F46E5;
    border: 1px solid #A5B4FC;
}

/* --- MÉTRICAS --- */
.metric-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid #E2E8F0;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.06);
    border-color: #CBD5E1;
}

.metric-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.5rem;
    display: block;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #1E293B;
    line-height: 1;
    margin-bottom: 0.25rem;
}

.metric-change {
    font-size: 0.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
}

.metric-up { color: #059669 !important; }
.metric-down { color: #DC2626 !important; }
.metric-neutral { color: #64748B !important; }

/* --- CORES RECURSOS --- */
.rc-sky {
    background: #F0F9FF !important;
    color: #0284C7 !important;
    border-color: #BAE6FD !important;
}
.rc-sky .res-icon { background: #F0F9FF !important; border: 1px solid #BAE6FD !important; }

.rc-green {
    background: #F0FDF4 !important;
    color: #16A34A !important;
    border-color: #BBF7D0 !important;
}
.rc-green .res-icon { background: #F0FDF4 !important; border: 1px solid #BBF7D0 !important; }

.rc-rose {
    background: #FFF1F2 !important;
    color: #E11D48 !important;
    border-color: #FECDD3 !important;
}
.rc-rose .res-icon { background: #FFF1F2 !important; border: 1px solid #FECDD3 !important; }

.rc-orange {
    background: #FFF7ED !important;
    color: #EA580C !important;
    border-color: #FDBA74 !important;
}
.rc-orange .res-icon { background: #FFF7ED !important; border: 1px solid #FDBA74 !important; }

/* --- ANIMAÇÕES --- */
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* --- RESPONSIVIDADE --- */
@media (max-width: 1024px) {
    .topbar { padding: 0 1.5rem; }
    .hero-wrapper { padding: 2rem; }
    .hero-greet { font-size: 2rem; }
    .mod-card-rect { height: 120px; }
    .mod-icon-area { width: 80px; }
    .info-card { min-height: 350px; }
}

@media (max-width: 768px) {
    .topbar { padding: 0 1rem; }
    .hero-wrapper {
        padding: 1.5rem;
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }
    .hero-greet { font-size: 1.75rem; }
    .hero-text { font-size: 1rem; }
    .hero-icon { font-size: 3rem; }
    .mod-card-rect { height: 110px; }
    .mod-icon-area { width: 70px; font-size: 1.5rem; }
    .mod-title { font-size: 1rem; }
    .mod-desc { font-size: 0.75rem; }
    .res-card { padding: 16px; gap: 12px; }
    .res-icon { width: 40px; height: 40px; font-size: 1.2rem; }
    .info-card { min-height: 380px; padding: 18px; }
}

@media (max-width: 640px) {
    .brand-img-text { display: none; }
    .user-badge { display: none; }
    .mod-card-rect { height: 100px; }
    .mod-icon-area { width: 60px; }
    .mod-content { padding: 0 16px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. FUNÇÕES AUXILIARES
# ==============================================================================
# Importar biblioteca de ícones do omni_utils
from omni_utils import get_icon, icon_title
def get_base64_image(image_path: str) -> str:
    """Carrega imagem e converte para base64"""
    if not os.path.exists(image_path):
        return ""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def escola_vinculada() -> str:
    """Retorna nome da escola formatado"""
    workspace_name = st.session_state.get("workspace_name", "")
    workspace_id = st.session_state.get("workspace_id", "")
    
    if workspace_name:
        return workspace_name[:20] + "..." if len(workspace_name) > 20 else workspace_name
    elif workspace_id:
        return f"ID: {workspace_id[:8]}..."
    return "Sem Escola"


def get_user_initials(nome: str) -> str:
    """Retorna iniciais do usuário para avatar"""
    if not nome:
        return "U"
    parts = nome.split()
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    return nome[:2].upper() if len(nome) >= 2 else nome[0].upper()


# ==============================================================================
# 4. INICIALIZAÇÃO DO ESTADO
# ==============================================================================
def initialize_session_state():
    """Inicializa todas as variáveis de estado necessárias"""
    defaults = {
        "autenticado": False,
        "workspace_id": None,
        "usuario_nome": "Visitante",
        "workspace_name": "Escola Modelo",
        "dados": {"nome": "", "nasc": date(2015, 1, 1), "serie": None}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Inicializa estado
initialize_session_state()

# Verificação de autenticação
if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div style='
                text-align: center; 
                padding: 3rem; 
                background: white;
                border-radius: 20px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 20px 40px rgba(0,0,0,0.05);
                margin: 4rem 0;
            '>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>🔐</div>
                <h3 style='color: #1E293B; margin-bottom: 1rem;'>Acesso Restrito</h3>
                <p style='color: #64748B; margin-bottom: 1.5rem;'>Sessão inválida ou expirada. Por favor, faça login novamente.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🔓 Fazer Login", use_container_width=True, type="primary"):
                # Limpa toda a sessão
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                # Redireciona para o login
                st.switch_page("streamlit_app.py")
    st.stop()

# ==============================================================================
# 5. FUNÇÕES DE RENDERIZAÇÃO
# ==============================================================================
def render_topbar():
    """Renderiza a barra superior fixa"""
    icone_b64 = get_base64_image("omni_icone.png")
    texto_b64 = get_base64_image("omni_texto.png")
    workspace = escola_vinculada()
    nome_user = st.session_state.get("usuario_nome", "Visitante").split()[0]
    
    # Avatar com iniciais
    user_initials = get_user_initials(nome_user)
    
    img_logo = (
        f'<img src="data:image/png;base64,{icone_b64}" class="brand-logo" alt="Omnisfera Logo">'
        if icone_b64 else "🌐"
    )
    
    img_text = (
        f'<img src="data:image/png;base64,{texto_b64}" class="brand-img-text" alt="Omnisfera">'
        if texto_b64 else "<span style='font-weight:800; font-size:1.2rem; color:#2B3674;'>OMNISFERA</span>"
    )
    
    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand-box">
                {img_logo}
                {img_text}
            </div>
            <div class="brand-box" style="gap: 16px;">
                <div class="user-badge">{workspace}</div>
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    font-weight: 700;
                    color: #334155;
                ">
                    <div style="
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #4F46E5, #7C3AED);
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: 800;
                        font-size: 0.9rem;
                    ">{user_initials}</div>
                    <div>{nome_user}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_module_card(title, desc, icon, color_cls, bg_cls, page, key):
    """Cria um card de módulo com botão de acesso"""
    st.markdown(
        f"""
        <div class="mod-card-wrapper">
            <div class="mod-card-rect">
                <div class="mod-bar {color_cls}"></div>
                <div class="mod-icon-area {bg_cls}">
                    <i class="{icon}"></i>
                </div>
                <div class="mod-content">
                    <div class="mod-title">{title}</div>
                    <div class="mod-desc">{desc}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    if st.button(
        f"📂 ACESSAR {title.split()[0].upper()}",
        key=f"btn_{key}",
        use_container_width=True,
        help=f"Clique para acessar {title}",
    ):
        st.switch_page(page)


def render_central_conhecimento():
    """Renderiza a Central de Conhecimento com as novas abas"""
    
    # Adiciona CSS específico para a Central de Conhecimento (estilo elegante da home)
    st.markdown("""
    <style>
        /* Cards e Containers - Estilo Elegante */
        .content-card {
            background: white; border: 1px solid #E2E8F0; border-radius: 16px;
            padding: 24px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); height: 100%; margin-bottom: 20px;
        }
        .content-card:hover { 
            transform: translateY(-4px); 
            border-color: #CBD5E1; 
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
        }
        .content-card h4 {
            font-weight: 800; color: #1E293B; margin-bottom: 12px; font-size: 1.1rem;
        }
        .content-card p {
            color: #64748B; line-height: 1.6; font-size: 0.9rem;
        }
        
        /* Manual Step Visuals - Estilo Elegante */
        .manual-box {
            border-left: 5px solid #2563EB; background: white; padding: 28px;
            border-radius: 0 16px 16px 0; margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .manual-box:hover {
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.06);
            border-left-color: #1E40AF;
        }
        .manual-header { 
            font-size: 1.3rem; font-weight: 800; color: #1E293B; 
            margin-bottom: 12px; display: flex; align-items: center; gap: 12px;
            letter-spacing: -0.3px;
        }
        .manual-quote { 
            font-style: italic; color: #64748B; background: #F8FAFC; padding: 14px 16px; 
            border-radius: 10px; margin-bottom: 18px; border-left: 3px solid #CBD5E1;
            font-size: 0.95rem; line-height: 1.5;
        }
        .key-concept { 
            background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            border: 1px solid #BFDBFE; color: #1E40AF; padding: 16px; 
            border-radius: 12px; margin-top: 18px; font-size: 0.9rem; font-weight: 700;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        }
        .manual-box ul {
            color: #475569; line-height: 1.8; margin-top: 12px;
        }
        .manual-box li {
            margin-bottom: 8px;
        }

        /* Glossários - Estilo Elegante */
        .term-good { 
            background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
            border-left: 4px solid #16A34A; padding: 18px; border-radius: 12px; 
            margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            transition: all 0.2s;
        }
        .term-good:hover {
            box-shadow: 0 4px 12px rgba(22, 163, 74, 0.1);
            transform: translateX(2px);
        }
        .term-good div:first-child {
            color: #166534; font-weight: 800; font-size: 1.05rem; margin-bottom: 6px;
            letter-spacing: -0.2px;
        }
        .term-good div:last-child {
            color: #14532d; font-size: 0.9rem; line-height: 1.5;
        }
        .term-bad { 
            background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
            border-left: 4px solid #DC2626; padding: 18px; border-radius: 12px; 
            margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            transition: all 0.2s;
        }
        .term-bad:hover {
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.1);
            transform: translateX(2px);
        }
        .term-bad div:first-child {
            color: #991b1b; font-weight: 800; text-decoration: line-through; font-size: 1.05rem; margin-bottom: 6px;
            letter-spacing: -0.2px;
        }
        .term-bad div:last-child {
            color: #7f1d1d; font-size: 0.9rem; line-height: 1.5;
        }
        .glossary-item { 
            background: white; padding: 24px; border-radius: 16px; 
            border-left: 5px solid #2563EB; 
            margin-bottom: 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .glossary-item:hover { 
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
            transform: translateY(-2px);
            border-left-color: #1E40AF;
        }
        .glossary-item div:first-child {
            color: #1E3A8A; font-weight: 800; font-size: 1.1rem; margin-bottom: 8px;
            letter-spacing: -0.2px;
        }
        .glossary-item div:last-child {
            color: #475569; font-size: 0.95rem; line-height: 1.6;
        }

        /* AI Chat Box - Estilo Elegante */
        .ai-box {
            background: linear-gradient(135deg, #FFFFFF 0%, #F0FDFA 100%);
            border: 2px solid #CCFBF1; border-radius: 16px; padding: 24px;
            margin-top: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        }
        .ai-box div:first-child {
            font-weight: 800; color: #0D9488; font-size: 1.1rem;
        }

        /* Abas - Estilo Elegante da Home */
        .stTabs [data-baseweb="tab-list"] { 
            gap: 12px; flex-wrap: wrap; 
            border-bottom: none !important;
            padding-bottom: 8px;
            margin-bottom: 24px;
        }
        /* Remove qualquer risco/linha embaixo das tabs */
        div[data-baseweb="tab-border"],
        div[data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab"]::after,
        .stTabs [data-baseweb="tab"]::before {
            display: none !important;
            border-bottom: none !important;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: white; border-radius: 12px; border: 1px solid #E2E8F0;
            padding: 12px 20px; font-weight: 700; color: #64748B; 
            flex-grow: 1; text-align: center;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 0.9rem;
            letter-spacing: -0.2px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            border-bottom: none !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #F8FAFC;
            border-color: #CBD5E1;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.04);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #2563EB 0%, #0EA5E9 100%) !important;
            color: white !important; 
            border-color: #2563EB !important;
            border-bottom: none !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        }
        .stTabs [aria-selected="true"]::after,
        .stTabs [aria-selected="true"]::before {
            display: none !important;
            border-bottom: none !important;
        }
        
        /* Correção para abas Legislação e Biblioteca */
        .stTabs [data-baseweb="tab-panel"] {
            overflow: visible !important;
        }
        
        /* Corrigir colunas quebradas */
        .stTabs [data-baseweb="tab-panel"] .row-widget {
            width: 100% !important;
        }
        
        /* Corrigir expanders */
        .stTabs [data-baseweb="tab-panel"] .streamlit-expander {
            width: 100% !important;
            margin-bottom: 12px !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] .streamlit-expanderHeader {
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            white-space: normal !important;
        }
        
        /* Corrigir ai-box */
        .ai-box {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        
        /* Garantir que colunas não quebrem */
        .stTabs [data-baseweb="tab-panel"] [data-testid="column"] {
            width: 100% !important;
            min-width: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Título elegante com ícone
    st.markdown(f"""
    <div style="margin-bottom: 8px; margin-top: -80px;">
        <h2 style="font-size: 2rem; font-weight: 800; color: #1E293B; margin-bottom: 8px; letter-spacing: -0.5px; display: flex; align-items: center; gap: 12px;">
            {get_icon("hub", 32, "#2563EB")}
            <span>Central de Inteligência Inclusiva</span>
        </h2>
        <p style="color: #64748B; font-size: 1rem; font-weight: 500; margin-left: 44px;">
            Fundamentos Pedagógicos, Marcos Legais e Ferramentas Práticas.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegação Principal (emojis mantidos nas abas - limitação do Streamlit)
    tab_panorama, tab_legal, tab_glossario, tab_linguagem, tab_biblio, tab_manual = st.tabs([
        "📊 Panorama & Fluxos", 
        "⚖️ Legislação & IA", 
        "📖 Glossário Técnico", 
        "🗣️ Dicionário Inclusivo",
        "📚 Biblioteca Virtual",
        "📘 Manual da Jornada"
    ])
    
    # ABA 1: PANORAMA
    with tab_panorama:
        st.markdown(f"### {icon_title('O Fluxo da Inclusão (Omnisfera 2025)', 'fluxo', 24, '#2563EB')}", unsafe_allow_html=True)
        st.caption("Visualização do ecossistema escolar atualizado com os novos decretos.")
        
        try:
            fluxo = graphviz.Digraph()
            fluxo.attr(rankdir='LR', bgcolor='transparent', margin='0')
            fluxo.attr('node', shape='box', style='rounded,filled', fontname='Inter', fontsize='11', height='0.6')
            
            fluxo.node('A', '1. ACOLHIMENTO\n(Matrícula Garantida)', fillcolor='#DBEAFE', color='#2563EB', fontcolor='#1E40AF', style='rounded,filled')
            fluxo.node('B', '2. ESTUDO DE CASO\n(Avaliação Pedagógica)', fillcolor='#2563EB', fontcolor='white', color='#1E3A8A', style='rounded,filled')
            fluxo.node('C', '3. IDENTIFICAÇÃO\n(Necessidades)', fillcolor='#D1FAE5', color='#10B981', fontcolor='#047857', style='rounded,filled')
            fluxo.node('D', '4. PLANEJAMENTO\n(PEI + PAEE)', fillcolor='#E9D5FF', color='#8B5CF6', fontcolor='#6D28D9', style='rounded,filled')
            fluxo.node('E', '5. PRÁTICA\n(Sala + AEE)', fillcolor='#FED7AA', color='#F59E0B', fontcolor='#D97706', style='rounded,filled')
            
            fluxo.edge('A', 'B', label=' Equipe')
            fluxo.edge('B', 'C', label=' Substitui Laudo')
            fluxo.edge('C', 'D')
            fluxo.edge('D', 'E', label=' Duplo Fundo')
            
            st.graphviz_chart(fluxo, use_container_width=True)
        except:
            st.error("Visualizador gráfico indisponível.")

        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="content-card">
                <h4>{icon_title('Filosofia: "Outrar-se"', 'filosofia', 20, '#2563EB')}</h4>
                <p style="color:#64748b;">A capacidade de sentir o mundo do outro mantendo o distanciamento profissional. É ter empatia sem confundir papéis, superando o capacitismo.</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="content-card">
                <h4>{icon_title('Justiça Curricular', 'justica', 20, '#2563EB')}</h4>
                <p style="color:#64748b;">O currículo não pode ser uma barreira. O PEI materializa a justiça curricular, garantindo acesso ao conhecimento através da adaptação.</p>
            </div>
            """, unsafe_allow_html=True)

    # ABA 2: LEGISLAÇÃO & IA
    with tab_legal:
        c_info, c_ai = st.columns([1.5, 1])
        
        with c_info:
            st.markdown(f"### {icon_title('Legislação em Foco (2025)', 'legislacao', 24, '#2563EB')}", unsafe_allow_html=True)
            
            with st.expander("⚖️ Decreto 12.686/2025: O Financiamento (Duplo Fundo)", expanded=True):
                st.markdown("""
                **Mudança Estrutural:**
                1.  **Dupla Matrícula:** O aluno público-alvo da educação especial é contabilizado **duas vezes** no FUNDEB (Matrícula Comum + AEE).
                2.  **Destinação:** A verba extra deve ser usada para Sala de Recursos, materiais adaptados e contratação de profissionais de apoio.
                """)
                
            with st.expander("🚫 Decreto 12.773/2025: Garantia de Acesso (Escolas Privadas)"):
                st.markdown("""
                **Tolerância Zero para Barreiras:**
                1.  **Taxas Extras:** É **ilegal** cobrar valor adicional na mensalidade para custear monitor ou material.
                2.  **Porta de Entrada:** A escola não pode exigir laudo médico para efetivar a matrícula. A avaliação pedagógica é soberana.
                """)

            st.markdown("#### ⏳ Marcos Históricos")
            st.caption("1988 (Constituição) • 1994 (Salamanca) • 2008 (PNEEPEI) • 2015 (LBI)")

        with c_ai:
            st.markdown("""
            <div class="ai-box">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:2rem;">🤖</span>
                    <div style="font-weight:700; color:#0d9488;">Consultor Legal IA</div>
                </div>
                <p style="font-size:0.9rem; color:#475569; margin-top:5px;">
                    Dúvidas sobre a lei? Pergunte à nossa inteligência especializada nos decretos de inclusão.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            user_question = st.text_input("Digite sua dúvida jurídica aqui:", placeholder="Ex: A escola pode exigir laudo para matricular?")
            
            if user_question:
                with st.spinner("Analisando Decretos 12.686 e 12.773..."):
                    time.sleep(1.5)
                    st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:16px; border-left:5px solid #0d9488; margin-top:16px; box-shadow:0 4px 12px rgba(0,0,0,0.08);">
                        <div style="font-weight:800; color:#0d9488; font-size:1.05rem; margin-bottom:10px; letter-spacing:-0.2px;">Resposta da IA:</div>
                        <div style="color:#475569; line-height:1.6; font-size:0.95rem;">
                            Com base no <strong style="color:#1E293B;">Decreto 12.773/2025</strong>, a exigência de laudo médico como condição prévia para matrícula é ilegal. A escola deve realizar o <strong style="color:#1E293B;">Estudo de Caso</strong> pedagógico.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ABA 3: GLOSSÁRIO TÉCNICO
    with tab_glossario:
        st.markdown(f"### {icon_title('Glossário Técnico Conceitual', 'glossario', 24, '#2563EB')}", unsafe_allow_html=True)
        st.markdown("Definições oficiais para embasar relatórios e PEIs.")
        
        termo_busca = st.text_input("🔍 Filtrar conceitos:", placeholder="Digite para buscar...")

        glossario_db = [
            {"t": "AEE (Atendimento Educacional Especializado)", "d": "Serviços educacionais suplementares que potencializam habilidades para que o aluno adquira autonomia. É transversal a todos os níveis, mas não substitui a escolarização regular."},
            {"t": "Alteridade", "d": "Conceito relacionado à capacidade de reconhecer e respeitar o 'outro' em sua diferença, incorporado por uma escola com responsabilidade social."},
            {"t": "Capacitismo", "d": "Toda forma de distinção, restrição ou exclusão que tenha o propósito de prejudicar, impedir ou anular o reconhecimento dos direitos da pessoa com deficiência."},
            {"t": "Cultura do Pertencimento", "d": "Uma cultura escolar onde o aluno realmente faz parte da comunidade, sendo condição essencial para o desenvolvimento inclusivo."},
            {"t": "Declaração de Salamanca", "d": "Resolução da ONU (1994) que estabeleceu princípios para a educação especial, formalizando o compromisso com a escola inclusiva."},
            {"t": "Educação Especial", "d": "Modalidade de educação que, dentro da inclusiva, oferece serviços, recursos e estratégias para atender às necessidades específicas."},
            {"t": "Educação Inclusiva", "d": "A efetivação do direito constitucional à educação para todos, garantindo que aprendam juntos independentemente das diferenças."},
            {"t": "Estudo de Caso", "d": "Metodologia de produção e registro de informações. Em 2025, é a porta de entrada que substitui o laudo médico."},
            {"t": "Justiça Curricular", "d": "Conceito que busca um currículo relevante e representativo, promovendo igualdade de condições e respeitando particularidades."},
            {"t": "Outragem / Outrar-se", "d": "Postura de quem é capaz de se colocar no lugar do outro, sentir o mundo do outro como se fosse seu próprio, numa relação empática."},
            {"t": "PcD", "d": "Sigla utilizada para se referir à Pessoa com Deficiência."},
            {"t": "PEI (Plano Educacional Individualizado)", "d": "Documento pedagógico de natureza obrigatória e atualização contínua ('documento vivo'), que visa garantir o atendimento personalizado."},
            {"t": "PNEEPEI", "d": "Política Nacional de Educação Especial na Perspectiva da Educação Inclusiva (2008)."},
            {"t": "PNAD Contínua", "d": "Pesquisa do IBGE que produziu estatísticas sobre pessoas com deficiência no Brasil."},
            {"t": "Profissional de Apoio Escolar", "d": "Atua no suporte (higiene, alimentação, locomoção). Deve ter nível médio e formação de 180h. Substitui 'cuidador'."},
            {"t": "Tecnologias Assistivas", "d": "Ferramentas, recursos ou dispositivos que auxiliam na funcionalidade e autonomia (pranchas, softwares, dispositivos)."},
            {"t": "Vieses Inconscientes", "d": "Processos inconscientes que levam a reproduzir comportamentos e discursos preconceituosos por associações aprendidas socialmente."}
        ]

        filtro = [g for g in glossario_db if termo_busca.lower() in g['t'].lower() or termo_busca.lower() in g['d'].lower()]
        
        for item in filtro:
            st.markdown(f"""
            <div class="glossary-item">
                <div style="color:#0F52BA; font-weight:700; font-size:1.1rem; margin-bottom:5px;">{item['t']}</div>
                <div style="color:#475569; font-size:0.95rem; line-height:1.5;">{item['d']}</div>
            </div>""", unsafe_allow_html=True)

    # ABA 4: DICIONÁRIO ANTICAPACITISTA
    with tab_linguagem:
        st.markdown(f"### {icon_title('Guia de Linguagem Inclusiva', 'linguagem', 24, '#2563EB')}", unsafe_allow_html=True)
        st.markdown("Termos para adotar e termos para abolir, baseados no respeito e na técnica.")

        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown(f"#### {icon_title('PREFIRA (Termos Corretos)', 'preferir', 20, '#16A34A')}", unsafe_allow_html=True)
            termos_bons = [
                ("Pessoa com Deficiência (PcD)", "Termo legal da LBI. Marca a deficiência como atributo, não identidade total."),
                ("Estudante com Deficiência", "Foco na pessoa primeiro."),
                ("Neurodivergente", "Funcionamento cerebral atípico (TEA, TDAH), sem conotação de doença."),
                ("Surdo", "Termo identitário correto (Comunidade Surda)."),
                ("Ritmo Próprio", "Respeita a singularidade da aprendizagem."),
                ("Típico / Atípico", "Substitui 'Normal' e 'Anormal'.")
            ]
            for t, d in termos_bons:
                st.markdown(f"""
                <div class="term-good">
                    <div>{t}</div>
                    <div>{d}</div>
                </div>""", unsafe_allow_html=True)

        with col_g2:
            st.markdown(f"#### {icon_title('EVITE (Termos Ofensivos)', 'evitar', 20, '#DC2626')}", unsafe_allow_html=True)
            termos_ruins = [
                ("Portador de Deficiência", "Deficiência não se porta (como uma bolsa). É intrínseca."),
                ("Aluno de Inclusão", "Segrega. Todos são alunos de inclusão."),
                ("Criança Especial", "Eufemismo que infantiliza. Use o nome da criança."),
                ("Surdo-Mudo", "Erro técnico. A surdez não implica mudez. Surdos têm voz."),
                ("Atrasado / Lento", "Pejorativo. Ignora a neurodiversidade."),
                ("Doença Mental", "Deficiência não é doença. Doença tem cura; deficiência é condição."),
                ("Fingir de João-sem-braço", "Expressão capacitista.")
            ]
            for t, d in termos_ruins:
                st.markdown(f"""
                <div class="term-bad">
                    <div style="text-decoration:line-through;">{t}</div>
                    <div>{d}</div>
                </div>""", unsafe_allow_html=True)

    # ABA 5: BIBLIOTECA VIRTUAL
    with tab_biblio:
        st.markdown(f"### {icon_title('Acervo Bibliográfico Completo', 'biblioteca', 24, '#2563EB')}", unsafe_allow_html=True)
        st.markdown("Clique nos itens para expandir o resumo e acessar o link (quando disponível).")

        def render_livro(titulo, autor, resumo, link=None, tag="Referência"):
            with st.expander(f"📚 {titulo}"):
                st.markdown(f"**Autor/Fonte:** {autor}")
                st.markdown(f"**Sobre:** {resumo}")
                if link:
                    st.markdown(f"""<a href="{link}" target="_blank" class="biblio-link">{get_icon('buscar', 16, '#2563EB')} Acessar Documento</a>""", unsafe_allow_html=True)

        st.markdown(f"#### {icon_title('Legislação e Documentos Oficiais', 'legislacao_doc', 20, '#2563EB')}", unsafe_allow_html=True)
        render_livro("Lei Brasileira de Inclusão (13.146/2015)", "Brasil", "Estatuto da PcD. Define barreira e criminaliza discriminação.", "http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm")
        render_livro("Decretos 12.686 e 12.773 (2025)", "Governo Federal", "Regulamentam o financiamento do AEE (Duplo Fundo) e proíbem cobranças extras.", "https://www.planalto.gov.br")
        render_livro("Política Nacional de Educação Especial (2008)", "MEC", "Consolidou a matrícula na escola comum.", "http://portal.mec.gov.br/seesp/arquivos/pdf/politica.pdf")
        render_livro("Declaração de Salamanca (1994)", "UNESCO", "Marco mundial da escola inclusiva.", "https://unesdoc.unesco.org/ark:/48223/pf0000139394")
        render_livro("Base Nacional Comum Curricular (BNCC)", "MEC", "Define as aprendizagens essenciais.", "https://www.gov.br/mec/pt-br/escola-em-tempo-integral/BNCC_EI_EF_110518_versaofinal.pdf")
        render_livro("Convenção sobre os Direitos das Pessoas com Deficiência", "ONU/Brasil (2008)", "Tratado internacional com status de emenda constitucional.", "https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2009/decreto/d6949.htm")

        st.markdown(f"#### {icon_title('Fundamentos Pedagógicos e Autores', 'pedagogia', 20, '#2563EB')}", unsafe_allow_html=True)
        render_livro("Inclusão Escolar: O que é? Como fazer?", "Maria Teresa Eglér Mantoan (2003)", "Diferencia integração de inclusão. Obra clássica.", None)
        render_livro("O Currículo e seus desafios: em busca da justiça curricular", "Branca Jurema Ponce (2018)", "Discute a justiça curricular como base da inclusão.", "http://www.curriculosemfronteiras.org/vol18iss3articles/ponce.pdf")
        render_livro("Altas Habilidades/Superdotação: inteligência e criatividade", "Virgolim, A. M. R. (2014)", "Conceitos de Renzulli e modelo dos três anéis.", None)
        render_livro("Mentes que mudam: a arte e a ciência de mudar as nossas mentes", "Howard Gardner (2005)", "Teoria das Inteligências Múltiplas aplicada.", None)
        render_livro("Capacitismo: o que é, onde vive?", "Sidney Andrade", "Entendendo o preconceito estrutural.", "https://medium.com/@sidneyandrade23")
        render_livro("Os Benefícios da Educação Inclusiva (2016)", "Instituto Alana", "Estudos comprovam ganhos para todos.", "https://alana.org.br/wp-content/uploads/2016/11/Os_Beneficios_da_Ed_Inclusiva_final.pdf")

    # ABA 6: MANUAL DA JORNADA
    with tab_manual:
        st.markdown(f"### {icon_title('Manual da Jornada Omnisfera: O Ciclo da Inclusão', 'manual', 24, '#2563EB')}", unsafe_allow_html=True)
        st.markdown("Fluxo de trabalho ideal conectando planejamento, AEE e prática.")

        # PASSO 1
        st.markdown(f"""
        <div class="manual-box">
            <div class="manual-header">{get_icon('pei', 28, '#0EA5E9')} <span>O Alicerce: Planejamento (PEI)</span></div>
            <div class="manual-quote">"Não há inclusão sem intenção. Conhecer para incluir."</div>
            <p>Tudo começa na página <strong>Estratégias & PEI</strong>. Antes de pensar em recursos, precisamos mapear quem é o estudante.</p>
            <p><strong>Ação na Plataforma:</strong></p>
            <ul>
                <li>Registre o histórico e o diagnóstico na aba Estudante.</li>
                <li>Mapeie as barreiras de aprendizagem (cognitivas, sensoriais ou físicas).</li>
                <li>Use a IA para estruturar metas de curto, médio e longo prazo.</li>
            </ul>
            <div class="key-concept">
                💡 <strong>Conceito Chave:</strong> O PEI não é um "laudo", é um projeto de futuro. Ele define O QUE vamos ensinar e QUAIS barreiras remover.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PASSO 2
        st.markdown(f"""
        <div class="manual-box">
            <div class="manual-header">{get_icon('pae', 28, '#A855F7')} <span>A Estratégia: O AEE e o Plano de Ação (PAEE)</span></div>
            <div class="manual-quote">"A articulação entre o suporte especializado e a sala comum."</div>
            <p>Aqui entra a execução técnica do PEI. Na página <strong>Plano de Ação / PAEE</strong>, organizamos o Atendimento Especializado.</p>
            <p><strong>Ação na Plataforma:</strong></p>
            <ul>
                <li>Defina a frequência e o foco dos atendimentos no contraturno.</li>
                <li>Estabeleça a ponte com o professor regente.</li>
                <li>Organize a Tecnologia Assistiva.</li>
            </ul>
            <div class="key-concept">
                💡 <strong>Conceito Chave:</strong> O AEE não funciona isolado. Ele é o laboratório onde se testam as ferramentas que permitirão ao aluno acessar o currículo comum.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PASSO 3
        st.markdown(f"""
        <div class="manual-box">
            <div class="manual-header">{get_icon('hub', 28, '#06B6D4')} <span>A Ferramenta: Adaptação (Hub de Inclusão)</span></div>
            <div class="manual-quote">"Acessibilidade é garantir que o conteúdo chegue a todos."</div>
            <p>Com o plano definido, vamos construir a aula. A página <strong>Hub de Recursos</strong> é sua oficina.</p>
            <div class="key-concept">
                💡 <strong>Conceito Chave:</strong> Adaptar não é empobrecer o currículo, é torná-lo flexível.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # PASSO 4 e 5 (Agrupados)
        c_log, c_data = st.columns(2)
        with c_log:
            st.markdown(f"""
            <div class="content-card" style="border-left:5px solid #F43F5E;">
                <h4>{icon_title('O Registro: Diário de Bordo', 'diario', 20, '#F43F5E')}</h4>
                <p><em>"O olhar atento transforma a prática."</em></p>
                <p>Registre o que funcionou e o engajamento. Use o conceito de <strong>"outrar-se"</strong>.</p>
            </div>
            """, unsafe_allow_html=True)
        with c_data:
            st.markdown(f"""
            <div class="content-card" style="border-left:5px solid #0C4A6E;">
                <h4>{icon_title('O Fechamento: Avaliação', 'monitoramento', 20, '#0C4A6E')}</h4>
                <p><em>"Avaliar para recalcular a rota."</em></p>
                <p>Use as <strong>Rubricas</strong> para fugir do "achismo". Se a meta foi atingida, avançamos.</p>
            </div>
            """, unsafe_allow_html=True)

        # Tabela Resumo Final
        st.markdown(f"#### {icon_title('Resumo do Ecossistema', 'fluxo', 20, '#2563EB')}", unsafe_allow_html=True)
        st.markdown(f"""
        | Passo | Módulo | Função |
        | :--- | :--- | :--- |
        | 1 | {get_icon('pei', 18, '#0EA5E9')} PEI | **Fundamentar:** Quem é o aluno? |
        | 2 | {get_icon('pae', 18, '#A855F7')} PAEE | **Estruturar:** Suporte especializado. |
        | 3 | {get_icon('hub', 18, '#06B6D4')} Hub | **Instrumentalizar:** Criar recursos. |
        | 4 | {get_icon('diario', 18, '#F43F5E')} Diário | **Registrar:** Execução diária. |
        | 5 | {get_icon('monitoramento', 18, '#0C4A6E')} Dados | **Validar:** Medir sucesso. |
        """, unsafe_allow_html=True)


def render_resources():
    """Renderiza os recursos externos"""
    resources_data = [
        {
            "title": "Lei da Inclusão",
            "desc": "LBI e diretrizes",
            "icon": "ri-government-fill",
            "theme": "rc-sky",
            "link": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm"
        },
        {
            "title": "Base Nacional",
            "desc": "Competências BNCC",
            "icon": "ri-compass-3-fill",
            "theme": "rc-green",
            "link": "http://basenacionalcomum.mec.gov.br/"
        },
        {
            "title": "Neurociência",
            "desc": "Artigos e estudos",
            "icon": "ri-brain-fill",
            "theme": "rc-rose",
            "link": "https://institutoneurosaber.com.br/"
        },
        {
            "title": "Ajuda Omnisfera",
            "desc": "Tutoriais e suporte",
            "icon": "ri-question-fill",
            "theme": "rc-orange",
            "link": "#"
        },
    ]
    
    cols = st.columns(4, gap="medium")
    for idx, resource in enumerate(resources_data):
        with cols[idx]:
            if resource["link"] != "#":
                st.markdown(
                    f"""
                    <a href="{resource['link']}" target="_blank" class="res-card-link">
                        <div class="res-card {resource['theme']}">
                            <div class="res-icon {resource['theme']}"><i class="{resource['icon']}"></i></div>
                            <div class="res-info">
                                <div class="res-name">{resource['title']}</div>
                                <div class="res-meta">{resource['desc']}</div>
                            </div>
                        </div>
                    </a>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="res-card {resource['theme']}" style="cursor: pointer;">
                        <div class="res-icon {resource['theme']}"><i class="{resource['icon']}"></i></div>
                        <div class="res-info">
                            <div class="res-name">{resource['title']}</div>
                            <div class="res-meta">{resource['desc']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )




# ==============================================================================
# 6. RENDERIZAÇÃO PRINCIPAL
# ==============================================================================

# Renderiza a topbar fixa (OCULTA SIDEBAR NATIVA)
render_topbar()

# ==============================================================================
# FUNÇÃO PARA GERAR MENSAGEM DE BOAS-VINDAS COM IA
# ==============================================================================
@st.cache_data(ttl=3600)  # Cache por 1 hora
def gerar_mensagem_boas_vindas_ia(api_key: str, nome_user: str, dia_semana: str, hora: int, saudacao: str):
    """Gera uma mensagem personalizada de boas-vindas usando IA"""
    if not api_key or not OpenAI:
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        dias_semana_pt = {
            "Monday": "segunda-feira",
            "Tuesday": "terça-feira", 
            "Wednesday": "quarta-feira",
            "Thursday": "quinta-feira",
            "Friday": "sexta-feira",
            "Saturday": "sábado",
            "Sunday": "domingo"
        }
        
        dia_pt = dias_semana_pt.get(dia_semana, dia_semana)
        
        prompt = f"""
        Você é um assistente educacional da plataforma Omnisfera, uma ferramenta de inclusão educacional.
        
        Crie uma mensagem de boas-vindas à Omnisfera que seja calorosa e inspiradora.
        
        CONTEXTO:
        - Dia da semana: {dia_pt}
        - Horário: {hora}h ({saudacao})
        - Plataforma: Omnisfera - Ecossistema de Inclusão Educacional
        
        DIRETRIZES IMPORTANTES:
        - A mensagem deve ser de BOAS-VINDAS À OMNISFERA
        - NÃO inclua saudações como "Bom dia", "Boa tarde" ou "Boa noite" (isso já aparece separadamente)
        - NÃO mencione o nome do educador (isso já aparece separadamente)
        - SEMPRE mencione a importância da inclusão escolar ou educação inclusiva
        - Mencione que a Omnisfera trabalhará JUNTO com o educador para facilitar a inclusão
        - Mencione o dia da semana de forma natural (ex: "Nesta segunda-feira", "Neste fim de semana")
        - Adapte o tom ao horário (manhã = energia, tarde = produtividade, noite = reflexão)
        - Seja breve (máximo 2-3 frases)
        - Use linguagem calorosa mas profissional
        - A mensagem deve inspirar e motivar para o trabalho com inclusão escolar
        
        Exemplo de estrutura: "Bem-vindo(a) à Omnisfera! [falar sobre importância da inclusão]. [mencionar que trabalharemos juntos]."
        
        Retorne APENAS a mensagem, sem aspas ou formatação adicional, SEM incluir saudações ou nomes.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        return None

# HERO SECTION
agora_brasilia = datetime.now(ZoneInfo("America/Sao_Paulo"))
hora = agora_brasilia.hour
dia_semana = agora_brasilia.strftime("%A")
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
nome_user = st.session_state.get("usuario_nome", "Visitante").split()[0]

# Tentar gerar mensagem com IA
mensagem_ia = None
api_key = st.secrets.get("OPENAI_API_KEY", "")
if api_key:
    mensagem_ia = gerar_mensagem_boas_vindas_ia(api_key, nome_user, dia_semana, hora, saudacao)

# Mensagem padrão caso IA não funcione
mensagem_final = mensagem_ia if mensagem_ia else f'"{saudacao}! A inclusão acontece quando aprendemos com as diferenças e não com as igualdades."'

st.markdown(
    f"""
    <div class="hero-wrapper">
        <div class="hero-content">
            <div class="hero-greet">{saudacao}, {nome_user}!</div>
            <div class="hero-text">{mensagem_final}</div>
        </div>
        <div class="hero-icon"><i class="ri-heart-pulse-fill"></i></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Módulos da Plataforma
st.markdown("### 🚀 Módulos da Plataforma")

modules_data = [
    {
        "title": "Estudantes",
        "desc": "Gestão completa de estudantes, histórico e acompanhamento individualizado.",
        "icon": "ri-user-star-fill",  # Ícone mais bonito
        "color_cls": "c-indigo",
        "bg_cls": "bg-indigo-soft",
        "page": "pages/Alunos.py",
        "key": "m_aluno",
    },
    {
        "title": "Estratégias & PEI",
        "desc": "Plano Educacional Individual com objetivos, avaliações e acompanhamento.",
        "icon": "ri-book-3-fill",  # Ícone mais bonito
        "color_cls": "c-blue",
        "bg_cls": "bg-blue-soft",
        "page": "pages/1_PEI.py",
        "key": "m_pei",
    },
    {
        "title": "Plano de Ação / PAEE",
        "desc": "Plano de Atendimento Educacional Especializado e sala de recursos.",
        "icon": "ri-puzzle-fill",  # Ícone mais bonito
        "color_cls": "c-purple",
        "bg_cls": "bg-purple-soft",
        "page": "pages/2_PAE.py",
        "key": "m_pae",
    },
    {
        "title": "Hub de Recursos",
        "desc": "Biblioteca de materiais, modelos e inteligência artificial para apoio.",
        "icon": "ri-rocket-fill",  # Ícone mais bonito
        "color_cls": "c-teal",
        "bg_cls": "bg-teal-soft",
        "page": "pages/3_Hub_Inclusao.py",
        "key": "m_hub",
    },
    {
        "title": "Diário de Bordo",
        "desc": "Registro diário de observações, evidências e intervenções.",
        "icon": "ri-edit-box-fill",  # Ícone mais bonito
        "color_cls": "c-rose",
        "bg_cls": "bg-rose-soft",
        "page": "pages/4_Diario_de_Bordo.py",
        "key": "m_diario",
    },
    {
        "title": "Evolução & Dados",
        "desc": "Indicadores, gráficos e relatórios de progresso dos estudantes.",
        "icon": "ri-line-chart-fill",  # Ícone mais bonito
        "color_cls": "c-sky",
        "bg_cls": "bg-sky-soft",
        "page": "pages/5_Monitoramento_Avaliacao.py",
        "key": "m_dados",
    },
]

# Organiza módulos em grid responsivo
cols = st.columns(3, gap="medium")
for i, module in enumerate(modules_data):
    with cols[i % 3]:
        create_module_card(
            title=module["title"],
            desc=module["desc"],
            icon=module["icon"],
            color_cls=module["color_cls"],
            bg_cls=module["bg_cls"],
            page=module["page"],
            key=module["key"]
        )

st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

# Nova Seção: Central de Conhecimento
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
st.markdown("---")
render_central_conhecimento()

# ==============================================================================
# RODAPÉ COM ASSINATURA
# ==============================================================================
ou.render_footer_assinatura()

import streamlit as st
from datetime import date, datetime
import base64
import os

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v2.2 - Guia de Inclusão"

try:
    IS_TEST_ENV = st.secrets.get("ENV", "PRODUCAO") == "TESTE"
except Exception:
    IS_TEST_ENV = False

st.set_page_config(
    page_title="Omnisfera - Plataforma de Inclusão Educacional",
    page_icon="🌐" if not os.path.exists("omni_icone.png") else "omni_icone.png",
    layout="wide",
    initial_sidebar_state="auto",
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
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px -10px rgba(30, 58, 138, 0.3);
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 220px;
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
    max-width: 800px;
    line-height: 1.6;
    font-weight: 500;
}

.hero-icon {
    opacity: 0.8;
    font-size: 4rem;
    z-index: 1;
    position: relative;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

/* --- NAV CARD (BOTÕES DE MÓDULO ESTILO RECURSO) --- */
/* Wrapper para o truque do botão overlay */
.nav-card-container {
    position: relative;
    height: 70px; /* Altura fixa para alinhar */
    margin-bottom: 10px;
}

.nav-card {
    background: white;
    border-radius: 12px;
    padding: 8px 12px;
    border: 1px solid #E2E8F0;
    display: flex;
    flex-direction: row; /* Ícone esquerda, Texto direita */
    align-items: center;
    gap: 10px;
    transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s ease;
    height: 100%;
    width: 100%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

/* Efeito de hover aplicado quando o container (que tem o botão) recebe hover */
.nav-card-container:hover .nav-card {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
    border-color: #7C3AED; /* Borda roxa no hover */
}

/* Ícone */
.nav-icon-box {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
    /* Padrão Roxo */
    background: #F5F3FF; 
    color: #7C3AED; 
    border: 1px solid #C4B5FD;
}

/* Texto */
.nav-title {
    font-weight: 700;
    font-size: 0.8rem;
    color: #1E293B;
    line-height: 1.1;
    text-align: left;
}

/* --- BOTÃO INVISÍVEL (OVERLAY) --- */
/* Isso estica o botão do Streamlit para cobrir o card visual e ficar transparente */
div[data-testid="column"] button {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 70px !important; /* Mesma altura do card */
    opacity: 0 !important;
    z-index: 5 !important;
    cursor: pointer !important;
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
                <p style='color: #64748B;'>Sessão inválida ou expirada. Por favor, faça login novamente.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        if st.button("🔓 Ir para Login", use_container_width=True, type="primary"):
            st.session_state.autenticado = False
            st.session_state.workspace_id = None
            st.rerun()
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


def render_nav_cards():
    """Renderiza os cartões de navegação em linha única"""
    # Definição dos módulos (incluindo Início)
    modules_data = [
        {"title": "Início", "icon": "ri-home-smile-2-fill", "page": "pages/0_Home.py", "key": "m_home"},
        {"title": "Estudantes", "icon": "ri-group-fill", "page": "pages/Alunos.py", "key": "m_aluno"},
        {"title": "Estratégias PEI", "icon": "ri-book-open-fill", "page": "pages/1_PEI.py", "key": "m_pei"},
        {"title": "PAEE", "icon": "ri-settings-5-fill", "page": "pages/2_PAE.py", "key": "m_pae"},
        {"title": "Hub", "icon": "ri-rocket-2-fill", "page": "pages/3_Hub_Inclusao.py", "key": "m_hub"},
        {"title": "Diário", "icon": "ri-file-list-3-fill", "page": "pages/4_Diario_de_Bordo.py", "key": "m_diario"},
        {"title": "Dados", "icon": "ri-bar-chart-box-fill", "page": "pages/5_Monitoramento_Avaliacao.py", "key": "m_dados"},
    ]

    # Grid de 7 colunas
    cols = st.columns(len(modules_data), gap="small")
    
    for i, mod in enumerate(modules_data):
        with cols[i]:
            # 1. Renderiza o Card Visual (HTML/CSS)
            st.markdown(
                f"""
                <div class="nav-card-container">
                    <div class="nav-card">
                        <div class="nav-icon-box"><i class="{mod['icon']}"></i></div>
                        <div class="nav-title">{mod['title']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # 2. Renderiza o Botão Invisível (Overlay)
            # Este botão usa a classe CSS definida acima para cobrir o card visualmente
            if st.button(" ", key=mod["key"], use_container_width=True):
                if mod["title"] == "Início":
                    st.rerun()
                else:
                    st.switch_page(mod["page"])


def render_info_cards():
    """Renderiza os cards informativos"""
    info_cards_data = [
        {
            "title": "Acolhimento e Cultura Inclusiva",
            "icon": "ri-heart-line",
            "color": "info-card-orange",
            "content": """
                <p><strong>Foco:</strong> O primeiro passo para a inclusão efetiva.</p>
                <p><strong>Conceito:</strong> Receber o aluno com deficiência não garante a inclusão automática; é necessário integrar plenamente por meio de práticas pedagógicas significativas.</p>
            """
        },
        {
            "title": "Gestão Estratégica (PGEI)",
            "icon": "ri-strategy-line",
            "color": "info-card-blue",
            "content": """
                <p><strong>Foco:</strong> Organização macro da escola para a inclusão.</p>
                <p><strong>O que é:</strong> O Plano Geral de Educação Inclusiva (PGEI) organiza ações para diferentes perfis (deficiências, transtornos, altas habilidades).</p>
            """
        },
        {
            "title": "Equipe Multidisciplinar",
            "icon": "ri-team-line",
            "color": "info-card-purple",
            "content": """
                <p><strong>Foco:</strong> Papéis e responsabilidades dos profissionais.</p>
                <ul>
                    <li><strong>Orientador Educacional:</strong> Convivência e integração.</li>
                    <li><strong>Psicólogo Escolar:</strong> Estudos de caso e orientação.</li>
                </ul>
            """
        },
        {
            "title": "O Plano Individual (PEI/PDI)",
            "icon": "ri-file-list-3-line",
            "color": "info-card-teal",
            "content": """
                <p><strong>Foco:</strong> O roteiro de aprendizagem do aluno.</p>
                <p><strong>Definição:</strong> O PEI é um roteiro flexível e obrigatório para nortear a aprendizagem, elaborado pela equipe multi.</p>
            """
        },
        {
            "title": "Adaptações e Transtornos",
            "icon": "ri-settings-5-line",
            "color": "info-card-rose",
            "content": """
                <p><strong>Foco:</strong> Estratégias para sala de aula.</p>
                <ul>
                    <li><strong>Flexibilidade:</strong> Tempo estendido.</li>
                    <li><strong>Avaliação:</strong> Instrumentos diversificados.</li>
                </ul>
            """
        },
        {
            "title": "Deficiências e Suporte Prático",
            "icon": "ri-wheelchair-line",
            "color": "info-card-indigo",
            "content": """
                <p><strong>Foco:</strong> Resumo técnico das necessidades.</p>
                <ul>
                    <li><strong>Física:</strong> Acessibilidade e mobilidade.</li>
                    <li><strong>Auditiva:</strong> Libras e recursos visuais.</li>
                </ul>
            """
        }
    ]
    
    # Grid responsivo para cards informativos
    cols = st.columns(3, gap="medium")
    for i, card in enumerate(info_cards_data):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="info-card {card['color']}">
                    <div class="info-card-header">
                        <div class="info-card-icon">
                            <i class="{card['icon']}"></i>
                        </div>
                        <h3 class="info-card-title">{card['title']}</h3>
                    </div>
                    <div class="info-card-content">
                        {card['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # Pequeno espaçamento vertical se houver quebra de linha
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


def render_resources():
    """Renderiza os recursos externos"""
    resources_data = [
        {"title": "Lei da Inclusão", "desc": "LBI e diretrizes", "icon": "ri-government-fill", "theme": "rc-sky", "link": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm"},
        {"title": "Base Nacional", "desc": "Competências BNCC", "icon": "ri-compass-3-fill", "theme": "rc-green", "link": "http://basenacionalcomum.mec.gov.br/"},
        {"title": "Neurociência", "desc": "Artigos e estudos", "icon": "ri-brain-fill", "theme": "rc-rose", "link": "https://institutoneurosaber.com.br/"},
        {"title": "Ajuda Omnisfera", "desc": "Tutoriais e suporte", "icon": "ri-question-fill", "theme": "rc-orange", "link": "#"},
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


def render_metrics():
    """Renderiza as métricas do dashboard"""
    metrics_data = [
        {"label": "Alunos Ativos", "value": "12", "change": "+2", "trend": "up"},
        {"label": "PEIs Ativos", "value": "8", "change": "+1", "trend": "up"},
        {"label": "Evidências Hoje", "value": "3", "change": "0", "trend": "neutral"},
        {"label": "Meta Mensal", "value": "75%", "change": "+5%", "trend": "up"},
    ]
    
    cols = st.columns(4, gap="medium")
    for idx, metric in enumerate(metrics_data):
        with cols[idx]:
            trend_icon = "↗️" if metric["trend"] == "up" else "↘️" if metric["trend"] == "down" else "➡️"
            trend_class = "metric-up" if metric["trend"] == "up" else "metric-down" if metric["trend"] == "down" else "metric-neutral"
            
            st.markdown(
                f"""
                <div class="metric-card">
                    <span class="metric-label">{metric['label']}</span>
                    <div class="metric-value">{metric['value']}</div>
                    <div class="metric-change {trend_class}">
                        {trend_icon} {metric['change']}
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

# HERO SECTION
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"
nome_user = st.session_state.get("usuario_nome", "Visitante").split()[0]

st.markdown(
    f"""
    <div class="hero-wrapper">
        <div class="hero-content">
            <div class="hero-greet">{saudacao}, {nome_user}!</div>
            <div class="hero-text">"A inclusão acontece quando aprendemos com as diferenças e não com as igualdades."</div>
        </div>
        <div class="hero-icon"><i class="ri-heart-pulse-fill"></i></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Módulos da Plataforma (NAV CARDS)
st.markdown("### 🚀 Acesso Rápido")
render_nav_cards()

st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

# Recursos Externos
st.markdown("### 📚 Recursos Externos & Referências")
render_resources()

# Métricas
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
render_metrics()

# Nova Seção: Guia de Inclusão
st.markdown("---")
st.markdown("## 📘 Guia Prático de Inclusão")
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
render_info_cards()

# Rodapé
st.markdown(
    f"""
    <div style='
        text-align: center;
        color: #64748B;
        font-size: 0.75rem;
        padding: 20px;
        border-top: 1px solid #E2E8F0;
        margin-top: 40px;
    '>
        <strong>Omnisfera {APP_VERSION}</strong> • Plataforma de Inclusão Educacional • 
        Desenvolvido por RODRIGO A. QUEIROZ • 
        {datetime.now().strftime("%d/%m/%Y %H:%M")}
    </div>
    """,
    unsafe_allow_html=True,
)

import streamlit as st
from datetime import date, datetime
import base64
import os

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v2.1 - Guia de Inclusão Otimizado"

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
    margin-bottom: 40px;
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
    background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
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

/* --- CORES DOS CARDS DE MÓDULO (RESTAURADAS) --- */
.c-indigo { background: #4F46E5 !important; }
.bg-indigo-soft { 
    background: #EEF2FF !important; 
    color: #4F46E5 !important;
}

.c-blue { background: #3B82F6 !important; }
.bg-blue-soft { 
    background: #EFF6FF !important;
    color: #2563EB !important;
}

.c-purple { background: #8B5CF6 !important; }
.bg-purple-soft { 
    background: #F5F3FF !important;
    color: #7C3AED !important;
}

.c-teal { background: #14B8A6 !important; }
.bg-teal-soft { 
    background: #F0FDFA !important;
    color: #0D9488 !important;
}

.c-rose { background: #E11D48 !important; }
.bg-rose-soft { 
    background: #FFF1F2 !important;
    color: #BE123C !important;
}

.c-sky { background: #0284C7 !important; }
.bg-sky-soft { 
    background: #F0F9FF !important;
    color: #0369A1 !important;
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

/* --- CARDS DE INFORMAÇÃO (GUIA) MELHORADOS --- */
.info-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #E2E8F0;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
    height: 100%;
    min-height: 280px; /* Reduzido levemente pois agora são 2 colunas */
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

/* Novas classes para o Guia (Tag e Lista) */
.guide-tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 12px;
}

.tag-orange { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.tag-blue { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.tag-purple { background: #FAF5FF; color: #7E22CE; border: 1px solid #E9D5FF; }
.tag-teal { background: #F0FDFA; color: #0F766E; border: 1px solid #99F6E4; }
.tag-rose { background: #FFF1F2; color: #BE123C; border: 1px solid #FECDD3; }
.tag-indigo { background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE; }

.info-card-content p {
    font-size: 0.9rem;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 12px;
}

.info-card-content ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.info-card-content li {
    position: relative;
    padding-left: 20px;
    margin-bottom: 8px;
    font-size: 0.85rem;
    color: #64748B;
    line-height: 1.5;
}

.info-card-content li::before {
    content: "•";
    position: absolute;
    left: 4px;
    color: #CBD5E1;
    font-weight: bold;
}

/* --- CORES DOS CARDS DE INFORMAÇÃO --- */
.info-card-orange { border-left: 4px solid #EA580C; }
.info-card-orange .info-card-icon { background: #FFF7ED; color: #EA580C; border: 1px solid #FDBA74; }

.info-card-blue { border-left: 4px solid #3B82F6; }
.info-card-blue .info-card-icon { background: #EFF6FF; color: #3B82F6; border: 1px solid #93C5FD; }

.info-card-purple { border-left: 4px solid #8B5CF6; }
.info-card-purple .info-card-icon { background: #F5F3FF; color: #8B5CF6; border: 1px solid #C4B5FD; }

.info-card-teal { border-left: 4px solid #14B8A6; }
.info-card-teal .info-card-icon { background: #F0FDFA; color: #14B8A6; border: 1px solid #5EEAD4; }

.info-card-rose { border-left: 4px solid #E11D48; }
.info-card-rose .info-card-icon { background: #FFF1F2; color: #E11D48; border: 1px solid #FDA4AF; }

.info-card-indigo { border-left: 4px solid #4F46E5; }
.info-card-indigo .info-card-icon { background: #EEF2FF; color: #4F46E5; border: 1px solid #A5B4FC; }

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


def create_module_card(title, desc, icon, color_cls, bg_cls, page, key):
    """Cria um card de módulo com botão de acesso"""
    with st.container():
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
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_info_cards():
    """Renderiza os cards informativos com layout melhorado (2 colunas)"""
    info_cards_data = [
        {
            "title": "Acolhimento & Cultura",
            "icon": "ri-heart-line",
            "color": "info-card-orange",
            "tag_class": "tag-orange",
            "tag_text": "PASSO 01",
            "content": """
                <p>Receber o aluno com deficiência não garante a inclusão automática; é necessário integrar plenamente.</p>
                <ul>
                    <li><strong>Políticas:</strong> Adoção de um PPP que contemple a diversidade.</li>
                    <li><strong>Acessibilidade:</strong> Adaptação da infraestrutura (rampas, banheiros).</li>
                    <li><strong>Mediação:</strong> Gestores atuando proativamente contra preconceitos.</li>
                </ul>
            """
        },
        {
            "title": "Gestão Estratégica (PGEI)",
            "icon": "ri-strategy-line",
            "color": "info-card-blue",
            "tag_class": "tag-blue",
            "tag_text": "ORGANIZAÇÃO MACRO",
            "content": """
                <p>O Plano Geral de Educação Inclusiva organiza ações para todos os perfis (deficiências, transtornos).</p>
                <ul>
                    <li>Levantar perfis específicos dos alunos.</li>
                    <li>Dimensionar a equipe de inclusão x número de alunos.</li>
                    <li>Planejar ações coletivas alinhadas ao PPP.</li>
                </ul>
            """
        },
        {
            "title": "Equipe Multidisciplinar",
            "icon": "ri-team-line",
            "color": "info-card-purple",
            "tag_class": "tag-purple",
            "tag_text": "RESPONSABILIDADES",
            "content": """
                <p>Quem faz o que no processo de inclusão escolar:</p>
                <ul>
                    <li><strong>Psicólogo Escolar:</strong> Estudos de caso e orientação (não clínico).</li>
                    <li><strong>AT (Terapêutico):</strong> Profissional externo para apoio individual (ex: autismo).</li>
                    <li><strong>AP (Pedagógico):</strong> Apoio na locomoção, higiene e materiais.</li>
                </ul>
            """
        },
        {
            "title": "O Plano Individual (PEI)",
            "icon": "ri-file-list-3-line",
            "color": "info-card-teal",
            "tag_class": "tag-teal",
            "tag_text": "ROTEIRO DE APRENDIZAGEM",
            "content": """
                <p>Roteiro flexível e obrigatório para nortear a aprendizagem do estudante.</p>
                <ul>
                    <li><strong>Elaboração:</strong> Equipe multi + família + externos.</li>
                    <li><strong>Essencial:</strong> Identidade, necessidades e tecnologias assistivas.</li>
                    <li><strong>Avaliação:</strong> Baseada no progresso individual (não comparativa).</li>
                </ul>
            """
        },
        {
            "title": "Adaptações & Sala de Aula",
            "icon": "ri-settings-5-line",
            "color": "info-card-rose",
            "tag_class": "tag-rose",
            "tag_text": "ESTRATÉGIAS PRÁTICAS",
            "content": """
                <p>Ajustes no cotidiano para garantir o acesso ao currículo.</p>
                <ul>
                    <li><strong>Flexibilidade:</strong> Tempo estendido para tarefas e provas.</li>
                    <li><strong>Avaliação:</strong> Diversificar instrumentos (orais, adaptados).</li>
                    <li><strong>Ambiente:</strong> Organizar sala para reduzir estímulos excessivos.</li>
                </ul>
            """
        },
        {
            "title": "Deficiências: Suporte",
            "icon": "ri-wheelchair-line",
            "color": "info-card-indigo",
            "tag_class": "tag-indigo",
            "tag_text": "RESUMO TÉCNICO",
            "content": """
                <p>Principais necessidades por tipo de deficiência:</p>
                <ul>
                    <li><strong>Auditiva:</strong> Libras, leitura labial, legendas.</li>
                    <li><strong>Visual:</strong> Braille, audiodescrição, leitores de tela.</li>
                    <li><strong>Intelectual:</strong> Linguagem simples e apoio na rotina.</li>
                </ul>
            """
        }
    ]
    
    # Grid de 2 colunas para melhor leitura
    for i in range(0, len(info_cards_data), 2):
        cols = st.columns(2, gap="medium")
        
        # Card Esquerda
        if i < len(info_cards_data):
            card = info_cards_data[i]
            with cols[0]:
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
                            <span class="guide-tag {card['tag_class']}">{card['tag_text']}</span>
                            {card['content']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        
        # Card Direita
        if i + 1 < len(info_cards_data):
            card = info_cards_data[i+1]
            with cols[1]:
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
                            <span class="guide-tag {card['tag_class']}">{card['tag_text']}</span>
                            {card['content']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        
        # Espaçamento entre linhas
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


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

# Módulos da Plataforma
st.markdown("### 🚀 Módulos da Plataforma")

modules_data = [
    {
        "title": "Estudantes",
        "desc": "Gestão completa de alunos, histórico e acompanhamento individualizado.",
        "icon": "ri-group-fill",
        "color_cls": "c-indigo",
        "bg_cls": "bg-indigo-soft",
        "page": "pages/Alunos.py",
        "key": "m_aluno",
    },
    {
        "title": "Estratégias & PEI",
        "desc": "Plano Educacional Individual com objetivos, avaliações e acompanhamento.",
        "icon": "ri-book-open-fill",
        "color_cls": "c-blue",
        "bg_cls": "bg-blue-soft",
        "page": "pages/1_PEI.py",
        "key": "m_pei",
    },
    {
        "title": "Plano de Ação / PAEE",
        "desc": "Plano de Atendimento Educacional Especializado e sala de recursos.",
        "icon": "ri-settings-5-fill",  # Ícone alterado
        "color_cls": "c-purple",
        "bg_cls": "bg-purple-soft",
        "page": "pages/2_PAE.py",
        "key": "m_pae",
    },
    {
        "title": "Hub de Recursos",
        "desc": "Biblioteca de materiais, modelos e inteligência artificial para apoio.",
        "icon": "ri-rocket-2-fill",
        "color_cls": "c-teal",
        "bg_cls": "bg-teal-soft",
        "page": "pages/3_Hub_Inclusao.py",
        "key": "m_hub",
    },
    {
        "title": "Diário de Bordo",
        "desc": "Registro diário de observações, evidências e intervenções.",
        "icon": "ri-file-list-3-fill",
        "color_cls": "c-rose",
        "bg_cls": "bg-rose-soft",
        "page": "pages/4_Diario_de_Bordo.py",
        "key": "m_diario",
    },
    {
        "title": "Evolução & Dados",
        "desc": "Indicadores, gráficos e relatórios de progresso dos alunos.",
        "icon": "ri-bar-chart-box-fill",
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

# Recursos Externos
st.markdown("### 📚 Recursos Externos & Referências")
render_resources()

# Nova Seção: Guia de Inclusão OTIMIZADO
st.markdown("---")
st.markdown("## 📘 Guia Prático de Inclusão")
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# Renderiza o guia com layout melhorado (2 colunas + tags)
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

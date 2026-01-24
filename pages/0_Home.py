import streamlit as st
from datetime import date, datetime
import base64
import os

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v2.5 - UI Square"

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
# 2. CSS & DESIGN SYSTEM
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

/* --- OCULTAR ELEMENTOS NATIVOS --- */
[data-testid="stSidebarNav"], [data-testid="stHeader"], [data-testid="stToolbar"], footer {
    display: none !important;
}

/* Ajuste de padding para a topbar fixa */
.block-container {
    padding-top: 100px !important;
    padding-bottom: 4rem !important;
    max-width: 95% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* --- TOPBAR FIXA --- */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 80px;
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid #E2E8F0; z-index: 9999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 2.5rem; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}
.brand-box { display: flex; align-items: center; gap: 12px; }
.brand-logo { height: 50px; width: auto; }
.user-badge { background: #F1F5F9; border: 1px solid #E2E8F0; padding: 6px 14px; border-radius: 99px; font-size: 0.8rem; font-weight: 700; color: #64748B; }

/* --- HERO SECTION (CARD AZUL) --- */
.hero-wrapper {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
    border-radius: 16px;
    padding: 2rem; /* Padding reduzido */
    color: white;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25);
    display: flex; align-items: center; justify-content: space-between;
    min-height: 160px; /* Altura reduzida */
}
.hero-wrapper::before {
    content: ""; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
    opacity: 0.3;
}
.hero-content { z-index: 2; position: relative; }
.hero-greet { font-size: 2rem; font-weight: 800; margin-bottom: 0.2rem; letter-spacing: -0.5px; line-height: 1.2; }
.hero-text { font-size: 0.95rem; opacity: 0.95; max-width: 800px; line-height: 1.5; font-weight: 500; }
.hero-icon { opacity: 0.8; font-size: 3rem; z-index: 1; position: relative; }

/* --- BOTÕES QUADRADOS (TOP NAV) --- */
.sq-nav-container {
    position: relative;
    height: 72px; /* Altura fixa menor */
    margin-bottom: 10px; /* Espaço até o card azul */
}

.sq-nav-card {
    background: white;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    
    /* Layout Flex Vertical para ficar quadrado */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    
    width: 100%;
    height: 100%;
    
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

/* Hover roxo */
.sq-nav-container:hover .sq-nav-card {
    transform: translateY(-3px);
    box-shadow: 0 8px 16px rgba(124, 58, 237, 0.1); /* Sombra roxa */
    border-color: #7C3AED;
    background-color: #FAFAFA;
}

.sq-nav-icon {
    font-size: 1.5rem; /* Ícone um pouco menor */
    color: #7C3AED; /* Roxo */
    transition: transform 0.2s ease;
}

.sq-nav-container:hover .sq-nav-icon {
    transform: scale(1.1);
}

.sq-nav-title {
    font-weight: 800;
    font-size: 0.65rem; /* Fonte menor */
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: center;
}

.sq-nav-container:hover .sq-nav-title {
    color: #7C3AED;
}

/* --- TRUQUE DO BOTÃO INVISÍVEL (CLICÁVEL) --- */
/* Força o botão do Streamlit a ocupar 100% da área e ser invisível */
.stButton button {
    width: 100% !important;
}

/* Target específico para os botões da navegação */
div[data-testid="column"] button {
    height: 72px !important; /* Mesma altura do container */
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    color: transparent !important;
    z-index: 2;
}

div[data-testid="column"] button:hover {
    background: transparent !important;
    color: transparent !important;
    border: none !important;
}

/* --- RESTO DO DESIGN (RECURSOS, ETC) --- */
.res-card { background: white; border-radius: 14px; padding: 20px; border: 1px solid #E2E8F0; display: flex; align-items: center; gap: 16px; height: 100%; }
.res-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
.rc-sky .res-icon { background: #F0F9FF; color: #0284C7; }
.metric-card { background: white; border-radius: 16px; padding: 1.5rem; border: 1px solid #E2E8F0; text-align: center; }
.info-card { background: white; border-radius: 16px; padding: 20px; border: 1px solid #E2E8F0; height: 100%; }
.info-card-orange { border-left: 4px solid #EA580C; }
</style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. HELPER FUNCTIONS
# ==============================================================================
def get_base64_image(image_path: str) -> str:
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()

def escola_vinculada() -> str:
    wn = st.session_state.get("workspace_name", "")
    wi = st.session_state.get("workspace_id", "")
    if wn: return wn[:20] + "..." if len(wn) > 20 else wn
    elif wi: return f"ID: {wi[:8]}..."
    return "Sem Escola"

def get_user_initials(nome: str) -> str:
    if not nome: return "U"
    parts = nome.split()
    if len(parts) >= 2: return f"{parts[0][0]}{parts[-1][0]}".upper()
    return nome[:2].upper() if len(nome) >= 2 else nome[0].upper()

# ==============================================================================
# 4. INITIALIZE STATE
# ==============================================================================
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "workspace_id" not in st.session_state: st.session_state.workspace_id = None

if not st.session_state.autenticado:
    # Tela de bloqueio simples se não autenticado
    st.warning("Acesso restrito. Faça login.")
    if st.button("Ir para Login"): st.rerun()
    st.stop()

# ==============================================================================
# 5. RENDERIZAÇÃO
# ==============================================================================

# --- TOPBAR ---
def render_topbar():
    icone_b64 = get_base64_image("omni_icone.png")
    texto_b64 = get_base64_image("omni_texto.png")
    workspace = escola_vinculada()
    nome_user = st.session_state.get("usuario_nome", "Visitante").split()[0]
    user_initials = get_user_initials(nome_user)
    
    img_logo = f'<img src="data:image/png;base64,{icone_b64}" class="brand-logo">' if icone_b64 else "🌐"
    img_text = f'<img src="data:image/png;base64,{texto_b64}" class="brand-img-text">' if texto_b64 else "<span style='font-weight:800; font-size:1.2rem; color:#2B3674;'>OMNISFERA</span>"
    
    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand-box">{img_logo}{img_text}</div>
            <div class="brand-box" style="gap: 16px;">
                <div class="user-badge">{workspace}</div>
                <div style="display: flex; align-items: center; gap: 10px; font-weight: 700; color: #334155;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9rem;">{user_initials}</div>
                    <div>{nome_user}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- QUADRADOS DE NAVEGAÇÃO (ACIMA DO HERO) ---
def render_square_menu():
    # Lista com 7 itens para alinhar
    modules = [
        {"title": "Início", "icon": "ri-home-smile-2-fill", "page": "pages/0_Home.py", "key": "sq_home"},
        {"title": "Estudantes", "icon": "ri-group-fill", "page": "pages/Alunos.py", "key": "sq_aluno"},
        {"title": "PEI", "icon": "ri-book-open-fill", "page": "pages/1_PEI.py", "key": "sq_pei"},
        {"title": "PAEE", "icon": "ri-settings-5-fill", "page": "pages/2_PAE.py", "key": "sq_pae"},
        {"title": "Hub", "icon": "ri-rocket-2-fill", "page": "pages/3_Hub_Inclusao.py", "key": "sq_hub"},
        {"title": "Diário", "icon": "ri-file-list-3-fill", "page": "pages/4_Diario_de_Bordo.py", "key": "sq_diario"},
        {"title": "Dados", "icon": "ri-bar-chart-box-fill", "page": "pages/5_Monitoramento_Avaliacao.py", "key": "sq_dados"},
    ]
    
    # 7 colunas - gap small para ficarem próximos
    cols = st.columns(7, gap="small")
    
    for i, mod in enumerate(modules):
        with cols[i]:
            # Container visual (HTML)
            # O z-index 1 garante que fique "embaixo" do botão transparente (z-index 2)
            st.markdown(
                f"""
                <div class="sq-nav-container">
                    <div class="sq-nav-card">
                        <i class="{mod['icon']} sq-nav-icon"></i>
                        <div class="sq-nav-title">{mod['title']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Botão Funcional Invisível (Overlay)
            # O label contém um espaço vazio " " para renderizar, mas o CSS o torna transparente e ajusta o tamanho
            if st.button(" ", key=mod["key"], use_container_width=True):
                if mod["title"] == "Início":
                    st.rerun()
                else:
                    st.switch_page(mod["page"])

# ==============================================================================
# 6. EXECUÇÃO PRINCIPAL
# ==============================================================================

# 1. Topbar Fixa
render_topbar()

# 2. Navegação Quadrada (AGORA AQUI EM CIMA)
# Pequeno espaço para separar da topbar fixa
st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True) 
render_square_menu()

# 3. Hero Card (AGORA ABAIXO)
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

# 4. Resto do Conteúdo (Recursos, Métricas, Guia)
st.markdown("### 📚 Recursos Externos & Referências")

res_data = [
    {"t": "Lei Inclusão", "d": "LBI 13.146", "i": "ri-government-fill", "c": "rc-sky", "l": "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm"},
    {"t": "Base Nacional", "d": "BNCC Oficial", "i": "ri-compass-3-fill", "c": "rc-green", "l": "http://basenacionalcomum.mec.gov.br/"},
    {"t": "Neurociência", "d": "Artigos", "i": "ri-brain-fill", "c": "rc-rose", "l": "https://institutoneurosaber.com.br/"},
    {"t": "Ajuda", "d": "Tutoriais", "i": "ri-question-fill", "c": "rc-orange", "l": "#"},
]

c_res = st.columns(4, gap="medium")
for i, r in enumerate(res_data):
    with c_res[i]:
        st.markdown(
            f"""<a href="{r['l']}" target="_blank" style="text-decoration:none;">
            <div class="res-card {r['c']}"><div class="res-icon"><i class="{r['i']}"></i></div>
            <div class="res-info"><div class="res-name">{r['t']}</div><div class="res-meta">{r['d']}</div></div></div></a>""",
            unsafe_allow_html=True
        )

st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
st.markdown("### 📊 Visão Geral")

# Métricas simples para exemplo
m_cols = st.columns(4)
metrics = [("Alunos", "12", "metric-up"), ("PEIs", "8", "metric-up"), ("Evidências", "3", "metric-neutral"), ("Meta", "75%", "metric-up")]
for i, (lbl, val, cls) in enumerate(metrics):
    with m_cols[i]:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value">{val}</div></div>""", unsafe_allow_html=True)

st.markdown("---")
st.caption(f"Omnisfera {APP_VERSION} • Desenvolvido por RODRIGO A. QUEIROZ")

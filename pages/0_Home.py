# pages/0_Home.py
import streamlit as st
from datetime import date, datetime
import base64
import os

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v161.0 (Sidebar Travada + Ordem dos Cards + Logo PAEE + Cores Diário/Dados)"

try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except Exception:
    IS_TEST_ENV = False

st.set_page_config(
    page_title="Omnisfera",
    page_icon="omni_icone.png" if os.path.exists("omni_icone.png") else "🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
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
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1E293B;
    background-color: #F8FAFC;
}

/* Limpeza Geral */
[data-testid="stSidebarNav"], [data-testid="stHeader"] { 
    display: none !important; 
}

/* --- TRAVA SIDEBAR: começa recolhida e sem botão de reabrir --- */
[data-testid="collapsedControl"]{
    display: none !important;
}

.block-container { 
    padding-top: 100px !important; 
    padding-bottom: 4rem !important; 
    max-width: 95% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* --- HEADER --- */
.topbar {
    position: fixed; 
    top: 0; 
    left: 0; 
    right: 0; 
    height: 80px;
    background: rgba(255,255,255,0.95); 
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #E2E8F0; 
    z-index: 9999;
    display: flex; 
    align-items: center; 
    justify-content: space-between;
    padding: 0 40px;
}

.brand-box { 
    display: flex; 
    align-items: center; 
    gap: 12px; 
}

.brand-logo { 
    height: 45px; 
    width: auto; 
    animation: spin 45s linear infinite; 
}

.brand-img-text { 
    height: 30px; 
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
}

/* --- SIDEBAR PERSONALIZADA --- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border-right: 1px solid #E2E8F0;
}

.sidebar-logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid #E2E8F0;
}

.sidebar-nav-section {
    padding: 0 15px;
}

.sidebar-nav-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sidebar-nav-button {
    width: 100%;
    margin-bottom: 8px;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    background: white;
    color: #475569;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 12px 16px;
    text-align: left;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 10px;
}

.sidebar-nav-button:hover {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    color: white;
    border-color: #4F46E5;
    transform: translateX(5px);
}

.sidebar-nav-button i {
    font-size: 1.1rem;
}

/* --- HERO SECTION --- */
.hero-wrapper {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
    border-radius: 20px; 
    padding: 40px; 
    color: white;
    margin-bottom: 40px; 
    position: relative; 
    overflow: hidden;
    box-shadow: 0 15px 30px -10px rgba(30, 58, 138, 0.3);
    display: flex; 
    align-items: center; 
    justify-content: space-between;
}

.hero-wrapper::after {
    content: ""; 
    position: absolute; 
    right: -50px; 
    top: -50px;
    width: 300px; 
    height: 300px; 
    background: rgba(255,255,255,0.1);
    border-radius: 50%; 
    pointer-events: none;
}

.hero-content { z-index: 1; }

.hero-greet { 
    font-size: 2rem; 
    font-weight: 800; 
    margin-bottom: 8px; 
    letter-spacing: -1px; 
}

.hero-text { 
    font-size: 1.05rem; 
    opacity: 0.95; 
    max-width: 800px; 
}

/* --- CONTAINER DO CARD + BOTÃO --- */
.mod-card-wrapper {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
}

/* --- CARDS DE MÓDULO --- */
.mod-card-rect {
    background: white;
    border-radius: 16px 16px 0 0;
    padding: 0;
    border: 1px solid #E2E8F0;
    border-bottom: none;
    box-shadow: 0 4px 6px rgba(0,0,0,0.01);
    display: flex; 
    flex-direction: row;
    align-items: center;
    height: 120px;
    width: 100%;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}

.mod-card-rect:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    border-color: #CBD5E1;
}

.mod-bar { width: 6px; height: 100%; flex-shrink: 0; }

.mod-icon-area {
    width: 80px; 
    height: 100%;
    display: flex; 
    align-items: center; 
    justify-content: center;
    font-size: 1.8rem; 
    flex-shrink: 0;
    background: #FAFAFA;
    border-right: 1px solid #F1F5F9;
}

.mod-content {
    flex-grow: 1; 
    padding: 0 20px;
    display: flex; 
    flex-direction: column; 
    justify-content: center;
}

.mod-title { 
    font-weight: 800; 
    font-size: 1rem; 
    color: #1E293B; 
    margin-bottom: 4px; 
}

.mod-desc { 
    font-size: 0.75rem; 
    color: #64748B; 
    line-height: 1.3; 
}

/* --- BOTÕES (Streamlit) - só hover leve (sem pintar tudo) --- */
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
}

/* --- RECURSOS --- */
.res-card-link { text-decoration: none !important; display: block; height: 100%; }

.res-card {
    background: white; 
    border-radius: 14px; 
    padding: 18px;
    border: 1px solid #E2E8F0; 
    display: flex; 
    align-items: center; 
    gap: 14px;
    transition: all 0.2s; 
    height: 100%;
}

.res-card:hover { 
    transform: translateY(-3px); 
    box-shadow: 0 8px 16px rgba(0,0,0,0.05); 
}

.res-icon { 
    width: 42px; 
    height: 42px; 
    border-radius: 10px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 1.3rem;
}

.res-info { display: flex; flex-direction: column; }
.res-name { font-weight: 700; color: #1E293B; font-size: 0.9rem; }
.res-meta { font-size: 0.75rem; font-weight: 600; opacity: 0.8; }

/* CORES TEMÁTICAS DOS CARDS */
.c-blue { background: #3B82F6; color: #3B82F6; }
.bg-blue-soft { background: #EFF6FF; color: #2563EB; }
.c-purple { background: #8B5CF6; color: #8B5CF6; }
.bg-purple-soft { background: #F5F3FF; color: #7C3AED; }
.c-teal { background: #14B8A6; color: #14B8A6; }
.bg-teal-soft { background: #F0FDFA; color: #0D9488; }
.c-indigo { background: #6366F1; color: #6366F1; }
.bg-indigo-soft { background: #EEF2FF; color: #4F46E5; }
.c-slate { background: #64748B; color: #64748B; }
.bg-slate-soft { background: #F8FAFC; color: #475569; }

/* NOVAS PALETAS (Diário e Dados) */
.c-rose { background: #E11D48; color: #E11D48; }
.bg-rose-soft { background: #FFF1F2; color: #BE123C; }

.c-sky { background: #0284C7; color: #0284C7; }
.bg-sky-soft { background: #F0F9FF; color: #0369A1; }

/* Cores Recursos */
.rc-green { background: #F0FDF4; color: #16A34A; border-color: #DCFCE7; }
.rc-orange { background: #FFF7ED; color: #EA580C; border-color: #FFEDD5; }
.rc-rose { background: #FFF1F2; color: #E11D48; border-color: #FECDD3; }
.rc-sky { background: #F0F9FF; color: #0284C7; border-color: #E0F2FE; }

@keyframes spin { 100% { transform: rotate(360deg); } }

/* --- RESPONSIVIDADE --- */
@media (max-width: 768px) {
    .topbar { padding: 0 20px; }
    .hero-wrapper { padding: 30px 20px; }
    .mod-card-rect { height: 100px; }
    .mod-icon-area { width: 60px; }
    .mod-title { font-size: 0.9rem; }
    .mod-desc { font-size: 0.7rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 3. HELPERS
# ==============================================================================
def acesso_bloqueado(msg: str):
    st.markdown(
        f"<div style='text-align:center; padding:50px; color:#64748B;'><h3>🔐 Acesso Restrito</h3><p>{msg}</p></div>",
        unsafe_allow_html=True,
    )
    if st.button("Ir para Login"):
        st.session_state.autenticado = False
        st.session_state.workspace_id = None
        st.rerun()
    st.stop()


def get_base64_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def escola_vinculada():
    return st.session_state.get("workspace_name") or st.session_state.get("workspace_id", "")[:8]


# ==============================================================================
# 4. SEGURANÇA / ESTADO
# ==============================================================================
if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
    acesso_bloqueado("Sessão inválida.")

if "dados" not in st.session_state:
    st.session_state.dados = {"nome": "", "nasc": date(2015, 1, 1), "serie": None}


# ==============================================================================
# 5. FUNÇÃO DE CARD (com logo opcional)
# ==============================================================================
def create_module_with_button(
    title,
    desc,
    icon,
    color_cls,
    bg_cls,
    page_path,
    key,
    logo_path=None,
):
    """Cria um card com botão abaixo. Se logo_path existir, usa imagem no lugar do ícone."""
    logo_html = ""
    if logo_path and os.path.exists(logo_path):
        logo_b64 = get_base64_image(logo_path)
        if logo_b64:
            logo_html = f"""
            <img src="data:image/png;base64,{logo_b64}" style="
                height:34px; width:auto;
                filter: drop-shadow(0 2px 6px rgba(0,0,0,.08));
            "/>
            """

    with st.container():
        st.markdown(
            f"""
        <div class="mod-card-wrapper">
            <div class="mod-card-rect">
                <div class="mod-bar {color_cls}"></div>
                <div class="mod-icon-area {bg_cls}">
                    {logo_html if logo_html else f"<i class='{icon}'></i>"}
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
            st.switch_page(page_path)

        st.markdown("</div>", unsafe_allow_html=True)


# ==============================================================================
# 6. RENDERIZAÇÃO PRINCIPAL
# ==============================================================================

# TOPBAR
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")
workspace = escola_vinculada()
nome_user = st.session_state.get("usuario_nome", "Visitante").split()[0]

img_logo = (
    f'<img src="data:image/png;base64,{icone_b64}" class="brand-logo">'
    if icone_b64
    else "🌐"
)
img_text = (
    f'<img src="data:image/png;base64,{texto_b64}" class="brand-img-text">'
    if texto_b64
    else "<span style='font-weight:800; font-size:1.2rem; color:#2B3674;'>OMNISFERA</span>"
)

st.markdown(
    f"""
<div class="topbar">
    <div class="brand-box">
        {img_logo} 
        {img_text}
    </div>
    <div class="brand-box">
        <div class="user-badge">{workspace}</div>
        <div style="font-weight:700; color:#334155;">{nome_user}</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# SIDEBAR (vai iniciar recolhida e sem botão de reabrir)
with st.sidebar:
    st.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)

    if os.path.exists("omnisfera.png"):
        st.image("omnisfera.png", use_column_width=True)
    elif os.path.exists("omni_texto.png"):
        st.image("omni_texto.png", use_column_width=True)
    else:
        st.markdown(
            """
        <div style="text-align: center;">
            <div style="font-size: 1.8rem; font-weight: 800; color: #4F46E5; margin-bottom: 5px;">
                🌐
            </div>
            <div style="font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); 
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                OMNISFERA
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class="sidebar-nav-section">
        <div class="sidebar-nav-title">
            <i class="ri-compass-3-line"></i> NAVEGAÇÃO
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    sidebar_options = [
        ("👥 Alunos", "pages/Alunos.py", "#4F46E5", "ri-team-line"),
        ("📘 PEI", "pages/1_PEI.py", "#3B82F6", "ri-book-open-line"),
        ("🧩 PAEE", "pages/2_PAE.py", "#8B5CF6", "ri-puzzle-line"),
        ("🚀 Hub", "pages/3_Hub_Inclusao.py", "#14B8A6", "ri-rocket-line"),
        ("📓 Diário", "pages/4_Diario_de_Bordo.py", "#E11D48", "ri-notebook-line"),
        ("📊 Dados", "pages/5_Monitoramento_Avaliacao.py", "#0284C7", "ri-bar-chart-line"),
    ]

    for label, page, color, icon in sidebar_options:
        st.markdown(
            f"""
        <button class="sidebar-nav-button" onclick="window.location='{page}'" 
                style="border-left: 4px solid {color};">
            <i class="{icon}"></i> {label}
        </button>
        """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div style='margin: 20px 0; border-top: 1px solid #E2E8F0;'></div>",
        unsafe_allow_html=True,
    )

    if st.button(
        "🚪 Sair do Sistema",
        use_container_width=True,
        type="secondary",
        help="Clique para sair do sistema",
    ):
        st.session_state.autenticado = False
        st.rerun()

# HERO
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"

st.markdown(
    f"""
<div class="hero-wrapper">
    <div class="hero-content">
        <div class="hero-greet">{saudacao}, {nome_user}!</div>
        <div class="hero-text">"A inclusão acontece quando aprendemos com as diferenças e não com as igualdades."</div>
    </div>
    <div style="opacity:0.8; font-size:4rem;"><i class="ri-heart-pulse-fill"></i></div>
</div>
""",
    unsafe_allow_html=True,
)

# MÓDULOS (ordem pela sequência das pastas)
st.markdown("### 🚀 Módulos da Plataforma")

modules = [
    {
        "title": "Estudantes",
        "desc": "Gestão completa de alunos, histórico e acompanhamento individualizado.",
        "icon": "ri-group-fill",
        "color_cls": "c-indigo",
        "bg_cls": "bg-indigo-soft",
        "page": "pages/Alunos.py",
        "key": "m_aluno",
        "logo_path": None,
    },
    {
        "title": "Estratégias & PEI",
        "desc": "Plano Educacional Individual com objetivos, avaliações e acompanhamento.",
        "icon": "ri-book-open-fill",
        "color_cls": "c-blue",
        "bg_cls": "bg-blue-soft",
        "page": "pages/1_PEI.py",
        "key": "m_pei",
        "logo_path": None,
    },
    {
        "title": "Plano de Ação / PAEE",
        "desc": "Plano de Atendimento Educacional Especializado e sala de recursos.",
        "icon": "ri-puzzle-fill",
        "color_cls": "c-purple",
        "bg_cls": "bg-purple-soft",
        "page": "pages/2_PAE.py",
        "key": "m_pae",
        # TROQUE o caminho abaixo pelo arquivo real do seu logo (se existir)
        "logo_path": "assets/paee_logo.png",
    },
    {
        "title": "Hub de Recursos",
        "desc": "Biblioteca de materiais, modelos e inteligência artificial para apoio.",
        "icon": "ri-rocket-2-fill",
        "color_cls": "c-teal",
        "bg_cls": "bg-teal-soft",
        "page": "pages/3_Hub_Inclusao.py",
        "key": "m_hub",
        "logo_path": None,
    },
    {
        "title": "Diário de Bordo",
        "desc": "Registro diário de observações, evidências e intervenções.",
        "icon": "ri-file-list-3-fill",
        "color_cls": "c-rose",
        "bg_cls": "bg-rose-soft",
        "page": "pages/4_Diario_de_Bordo.py",
        "key": "m_diario",
        "logo_path": None,
    },
    {
        "title": "Evolução & Dados",
        "desc": "Indicadores, gráficos e relatórios de progresso dos alunos.",
        "icon": "ri-bar-chart-box-fill",
        "color_cls": "c-sky",
        "bg_cls": "bg-sky-soft",
        "page": "pages/5_Monitoramento_Avaliacao.py",
        "key": "m_dados",
        "logo_path": None,
    },
]

cols = st.columns(3, gap="medium")
for i, module in enumerate(modules):
    with cols[i % 3]:
        create_module_with_button(
            title=module["title"],
            desc=module["desc"],
            icon=module["icon"],
            color_cls=module["color_cls"],
            bg_cls=module["bg_cls"],
            page_path=module["page"],
            key=module["key"],
            logo_path=module.get("logo_path"),
        )

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# RECURSOS EXTERNOS
st.markdown("### 📚 Recursos Externos & Referências")
r1, r2, r3, r4 = st.columns(4, gap="medium")


def create_resource(col, title, desc, icon, theme, link):
    with col:
        if link != "#":
            st.markdown(
                f"""
            <a href="{link}" target="_blank" class="res-card-link">
                <div class="res-card {theme}">
                    <div class="res-icon {theme}"><i class="{icon}"></i></div>
                    <div class="res-info">
                        <div class="res-name">{title}</div>
                        <div class="res-meta">{desc}</div>
                    </div>
                </div>
            </a>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="res-card {theme}" style="cursor: pointer;">
                <div class="res-icon {theme}"><i class="{icon}"></i></div>
                <div class="res-info">
                    <div class="res-name">{title}</div>
                    <div class="res-meta">{desc}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


create_resource(
    r1,
    "Lei da Inclusão",
    "LBI e diretrizes",
    "ri-government-fill",
    "rc-sky",
    "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm",
)
create_resource(
    r2,
    "Base Nacional",
    "Competências BNCC",
    "ri-compass-3-fill",
    "rc-green",
    "http://basenacionalcomum.mec.gov.br/",
)
create_resource(
    r3,
    "Neurociência",
    "Artigos e estudos",
    "ri-brain-fill",
    "rc-rose",
    "https://institutoneurosaber.com.br/",
)
create_resource(r4, "Ajuda Omnisfera", "Tutoriais e suporte", "ri-question-fill", "rc-orange", "#")

# RODAPÉ
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Alunos Ativos", "12", "+2")
with col2:
    st.metric("PEIs Ativos", "8", "+1")
with col3:
    st.metric("Evidências Hoje", "3", "0")
with col4:
    st.metric("Meta Mensal", "75%", "+5%")

st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.markdown(
    f"""
<div style='
    text-align: center; 
    color: #64748B; 
    font-size: 0.75rem;
    padding: 20px;
    border-top: 1px solid #E2E8F0;
    margin-top: 20px;
'>
    <strong>Omnisfera v2.0</strong> • Plataforma de Inclusão Educacional • 
    Desenvolvido por RODRIGO A. QUEIROZ • 
    {datetime.now().strftime("%d/%m/%Y %H:%M")}
</div>
""",
    unsafe_allow_html=True,
)

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
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1E293B;
    background-color: #F8FAFC;
}

/* ... (todo o resto do CSS) ... */
</style>
"""

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
# 4. INICIALIZAÇÃO DO ESTADO
# ==============================================================================
def initialize_session_state():
    required_keys = {
        "autenticado": False,
        "workspace_id": None,
        "usuario_nome": "Visitante",
        "workspace_name": "",
        "dados": {"nome": "", "nasc": date(2015, 1, 1), "serie": None}
    }
    for key, default in required_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default

# ==============================================================================
# 5. COMPONENTES DE UI
# ==============================================================================
def render_topbar():
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

def render_sidebar():
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

def render_hero():
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
        <div style="opacity:0.8; font-size:4rem;"><i class="ri-heart-pulse-fill"></i></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

def render_modules():
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

def render_resources():
    st.markdown("### 📚 Recursos Externos & Referências")
    r1, r2, r3, r4 = st.columns(4, gap="medium")

    resources = [
        ("Lei da Inclusão", "LBI e diretrizes", "ri-government-fill", "rc-sky", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm"),
        ("Base Nacional", "Competências BNCC", "ri-compass-3-fill", "rc-green", "http://basenacionalcomum.mec.gov.br/"),
        ("Neurociência", "Artigos e estudos", "ri-brain-fill", "rc-rose", "https://institutoneurosaber.com.br/"),
        ("Ajuda Omnisfera", "Tutoriais e suporte", "ri-question-fill", "rc-orange", "#"),
    ]

    for col, (title, desc, icon, theme, link) in zip([r1, r2, r3, r4], resources):
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

def render_footer():
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

# ==============================================================================
# 6. FUNÇÃO DE CARD (com logo opcional)
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
# 7. RENDERIZAÇÃO PRINCIPAL
# ==============================================================================
def main():
    initialize_session_state()

    # Verificação de autenticação
    if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
        acesso_bloqueado("Sessão inválida.")

    # Carregar CSS
    st.markdown(CSS, unsafe_allow_html=True)

    # Renderizar componentes
    render_topbar()
    render_sidebar()
    render_hero()
    render_modules()
    render_resources()
    render_footer()

# ==============================================================================
# 8. EXECUÇÃO
# ==============================================================================
if __name__ == "__main__":
    main()

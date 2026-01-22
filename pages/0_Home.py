# pages/0_Home.py
import streamlit as st
from datetime import date, datetime
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v159.0 (Correções: Botão + Ícone + Verificação)"

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
# 2. CSS & DESIGN SYSTEM ATUALIZADO
# ==============================================================================
st.markdown("""
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

.hero-content { 
    z-index: 1; 
}

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
    border-radius: 16px 16px 0 0; /* Arredondar só em cima */
    padding: 0;
    border: 1px solid #E2E8F0;
    border-bottom: none; /* Remove borda inferior */
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

.mod-bar { 
    width: 6px; 
    height: 100%; 
    flex-shrink: 0; 
}

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

/* --- BOTÕES COLORIDOS ABAIXO DOS CARDS --- */
.mod-action-button {
    width: 100%;
    height: 40px;
    border: none;
    border-radius: 0 0 16px 16px;
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.mod-action-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Cores específicas para cada tipo de botão */
.btn-indigo {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
}

.btn-indigo:hover {
    background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%);
}

.btn-teal {
    background: linear-gradient(135deg, #14B8A6 0%, #0D9488 100%);
}

.btn-teal:hover {
    background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%);
}

.btn-blue {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
}

.btn-blue:hover {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
}

.btn-purple {
    background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
}

.btn-purple:hover {
    background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
}

.btn-slate {
    background: linear-gradient(135deg, #64748B 0%, #475569 100%);
}

.btn-slate:hover {
    background: linear-gradient(135deg, #475569 0%, #334155 100%);
}

/* --- RECURSOS --- */
.res-card-link { 
    text-decoration: none !important; 
    display: block; 
    height: 100%; 
}

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

.res-info { 
    display: flex; 
    flex-direction: column; 
}

.res-name { 
    font-weight: 700; 
    color: #1E293B; 
    font-size: 0.9rem; 
}

.res-meta { 
    font-size: 0.75rem; 
    font-weight: 600; 
    opacity: 0.8; 
}

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

/* Cores Recursos */
.rc-green { background: #F0FDF4; color: #16A34A; border-color: #DCFCE7; }
.rc-orange { background: #FFF7ED; color: #EA580C; border-color: #FFEDD5; }
.rc-rose { background: #FFF1F2; color: #E11D48; border-color: #FECDD3; }
.rc-sky { background: #F0F9FF; color: #0284C7; border-color: #E0F2FE; }

@keyframes spin { 
    100% { transform: rotate(360deg); } 
}

/* --- RESPONSIVIDADE --- */
@media (max-width: 768px) {
    .topbar {
        padding: 0 20px;
    }
    .hero-wrapper {
        padding: 30px 20px;
    }
    .mod-card-rect {
        height: 100px;
    }
    .mod-icon-area {
        width: 60px;
    }
    .mod-title {
        font-size: 0.9rem;
    }
    .mod-desc {
        font-size: 0.7rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. HELPERS
# ==============================================================================
def acesso_bloqueado(msg):
    st.markdown(f"<div style='text-align:center; padding:50px; color:#64748B;'><h3>🔐 Acesso Restrito</h3><p>{msg}</p></div>", unsafe_allow_html=True)
    if st.button("Ir para Login"):
        st.session_state.autenticado = False
        st.session_state.workspace_id = None
        st.rerun()
    st.stop()

# Verificar autenticação
if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
    acesso_bloqueado("Sessão inválida.")

# Inicializar dados se não existirem
if "dados" not in st.session_state:
    st.session_state.dados = {"nome": "", "nasc": date(2015,1,1), "serie": None}

def get_base64_image(image_path):
    if not os.path.exists(image_path): 
        return ""
    with open(image_path, "rb") as f: 
        return base64.b64encode(f.read()).decode()

def escola_vinculada():
    return st.session_state.get("workspace_name") or st.session_state.get("workspace_id", "")[:8]

# ==============================================================================
# 4. FUNÇÃO PARA CRIAR CARDS COM BOTÕES COLORIDOS (SEM VERIFICAÇÃO DE ALUNO)
# ==============================================================================
def create_module_with_button(title, desc, icon, color_cls, bg_cls, btn_class, page_path, key):
    """Cria um card com botão colorido abaixo - SEM verificação de aluno"""
    
    # Container principal
    with st.container():
        # Card visual
        st.markdown(f"""
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
        """, unsafe_allow_html=True)
        
        # Botão colorido abaixo do card
        if st.button(
            f"📂 ACESSAR {title.split()[0].upper()}",  # Pega a primeira palavra do título
            key=f"btn_{key}",
            # REMOVIDO: type="primary" if "indigo" in btn_class else "secondary" (isso causava cor vermelha)
            use_container_width=True,
            help=f"Clique para acessar {title}"
        ):
            # Lógica de navegação SIMPLIFICADA - SEM verificação de aluno
            st.switch_page(page_path)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 5. RENDERIZAÇÃO PRINCIPAL
# ==============================================================================

# TOPBAR
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")
workspace = escola_vinculada()
nome_user = st.session_state.get('usuario_nome', 'Visitante').split()[0]

img_logo = f'<img src="data:image/png;base64,{icone_b64}" class="brand-logo">' if icone_b64 else "🌐"
img_text = f'<img src="data:image/png;base64,{texto_b64}" class="brand-img-text">' if texto_b64 else "<span style='font-weight:800; font-size:1.2rem; color:#2B3674;'>OMNISFERA</span>"

st.markdown(f"""
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
""", unsafe_allow_html=True)

# SIDEBAR SIMPLIFICADA
with st.sidebar:
    # Logo
    if os.path.exists("omni_icone.png"):
        st.image("omni_icone.png", width=60)
    else:
        st.markdown("### 🌐 **Omnisfera**")
    
    st.markdown("---")
    
    # Links rápidos
    st.markdown("#### 🔗 Navegação Rápida")
    
    # Criar botões na sidebar com ícones
    sidebar_options = [
        ("👥 Alunos", "pages/Alunos.py", "#4F46E5"),
        ("📘 PEI", "pages/1_PEI.py", "#3B82F6"),
        ("🧩 PAEE", "pages/2_PAE.py", "#8B5CF6"),
        ("🚀 Hub", "pages/3_Hub_Inclusao.py", "#14B8A6"),
        ("📓 Diário", "pages/4_Diario_de_Bordo.py", "#64748B"),
        ("📊 Dados", "pages/5_Monitoramento_Avaliacao.py", "#475569"),
    ]
    
    for label, page, color in sidebar_options:
        if st.button(
            label, 
            use_container_width=True, 
            key=f"sidebar_{label}",
            help=f"Clique para acessar {label}"
        ):
            st.switch_page(page)
    
    st.markdown("---")
    
    # Botão de logout
    if st.button("🚪 Sair do Sistema", use_container_width=True, type="secondary"):
        st.session_state.autenticado = False
        st.rerun()

# HERO SECTION
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"

st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-content">
        <div class="hero-greet">{saudacao}, {nome_user}!</div>
        <div class="hero-text">"A inclusão acontece quando aprendemos com as diferenças e não com as igualdades."</div>
    </div>
    <div style="opacity:0.8; font-size:4rem;"><i class="ri-heart-pulse-fill"></i></div>
</div>
""", unsafe_allow_html=True)

# MÓDULOS COM BOTÕES COLORIDOS
st.markdown("### 🚀 Módulos da Plataforma")

# Definir módulos com suas cores específicas (CORRIGIDO: Ícone do PAEE)
modules = [
    {
        "title": "Estudantes",
        "desc": "Gestão completa de alunos, histórico e acompanhamento individualizado.",
        "icon": "ri-group-fill",  # ✅ Ícone correto
        "color_cls": "c-indigo",
        "bg_cls": "bg-indigo-soft",
        "btn_class": "btn-indigo",  # ✅ Cor indigo como os outros
        "page": "pages/Alunos.py",
        "key": "m_aluno"
    },
    {
        "title": "Hub de Recursos",
        "desc": "Biblioteca de materiais, modelos e inteligência artificial para apoio.",
        "icon": "ri-rocket-2-fill",  # ✅ Ícone correto
        "color_cls": "c-teal",
        "bg_cls": "bg-teal-soft",
        "btn_class": "btn-teal",
        "page": "pages/3_Hub_Inclusao.py",
        "key": "m_hub"
    },
    {
        "title": "Estratégias & PEI",
        "desc": "Plano Educacional Individual com objetivos, avaliações e acompanhamento.",
        "icon": "ri-book-open-fill",  # ✅ Ícone correto
        "color_cls": "c-blue",
        "bg_cls": "bg-blue-soft",
        "btn_class": "btn-blue",
        "page": "pages/1_PEI.py",
        "key": "m_pei"
    },
    {
        "title": "Plano de Ação / PAEE",
        "desc": "Plano de Atendimento Educacional Especializado e sala de recursos.",
        "icon": "ri-puzzle-fill",  # ✅ CORRIGIDO: Ícone correto (puzzle-fill ao invés de puzzle-2-fill)
        "color_cls": "c-purple",
        "bg_cls": "bg-purple-soft",
        "btn_class": "btn-purple",
        "page": "pages/2_PAE.py",
        "key": "m_pae"
    },
    {
        "title": "Diário de Bordo",
        "desc": "Registro diário de observações, evidências e intervenções.",
        "icon": "ri-file-list-3-fill",  # ✅ Ícone correto
        "color_cls": "c-slate",
        "bg_cls": "bg-slate-soft",
        "btn_class": "btn-slate",
        "page": "pages/4_Diario_de_Bordo.py",
        "key": "m_diario"
    },
    {
        "title": "Evolução & Dados",
        "desc": "Indicadores, gráficos e relatórios de progresso dos alunos.",
        "icon": "ri-bar-chart-box-fill",  # ✅ Ícone correto
        "color_cls": "c-slate",
        "bg_cls": "bg-slate-soft",
        "btn_class": "btn-slate",
        "page": "pages/5_Monitoramento_Avaliacao.py",
        "key": "m_dados"
    }
]

# Criar grid 3x2
cols = st.columns(3, gap="medium")

# Distribuir módulos pelas colunas
for i, module in enumerate(modules):
    with cols[i % 3]:
        # Usar a função que cria card + botão
        create_module_with_button(
            title=module["title"],
            desc=module["desc"],
            icon=module["icon"],
            color_cls=module["color_cls"],
            bg_cls=module["bg_cls"],
            btn_class=module["btn_class"],
            page_path=module["page"],
            key=module["key"]
        )

# Adicionar espaçamento entre as linhas
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# RECURSOS EXTERNOS
st.markdown("### 📚 Recursos Externos & Referências")

# Criar colunas para recursos
r1, r2, r3, r4 = st.columns(4, gap="medium")

# Função para criar recursos
def create_resource(col, title, desc, icon, theme, link):
    with col:
        if link != "#":
            st.markdown(f"""
            <a href="{link}" target="_blank" class="res-card-link">
                <div class="res-card {theme}">
                    <div class="res-icon {theme}"><i class="{icon}"></i></div>
                    <div class="res-info">
                        <div class="res-name">{title}</div>
                        <div class="res-meta">{desc}</div>
                    </div>
                </div>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="res-card {theme}" style="cursor: pointer;">
                <div class="res-icon {theme}"><i class="{icon}"></i></div>
                <div class="res-info">
                    <div class="res-name">{title}</div>
                    <div class="res-meta">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Adicionar recursos
create_resource(r1, "Lei da Inclusão", "LBI e diretrizes", "ri-government-fill", "rc-sky", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm")
create_resource(r2, "Base Nacional", "Competências BNCC", "ri-compass-3-fill", "rc-green", "http://basenacionalcomum.mec.gov.br/")
create_resource(r3, "Neurociência", "Artigos e estudos", "ri-brain-fill", "rc-rose", "https://institutoneurosaber.com.br/")
create_resource(r4, "Ajuda Omnisfera", "Tutoriais e suporte", "ri-question-fill", "rc-orange", "#")

# RODAPÉ
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)

# Estatísticas rápidas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Alunos Ativos", "12", "+2")
with col2:
    st.metric("PEIs Ativos", "8", "+1")
with col3:
    st.metric("Evidências Hoje", "3", "0")
with col4:
    st.metric("Meta Mensal", "75%", "+5%")

# Copyright
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
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
""", unsafe_allow_html=True)

# CSS ADICIONAL para corrigir cor do botão Estudantes
st.markdown("""
<style>
/* CSS para corrigir a cor do botão Estudantes */
.stButton > button {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
    color: white !important;
    border: none !important;
}

/* Cor específica para cada botão baseado no texto */
.stButton > button:contains("ACESSAR ESTUDANTES") {
    background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
}

.stButton > button:contains("ACESSAR HUB") {
    background: linear-gradient(135deg, #14B8A6 0%, #0D9488 100%) !important;
}

.stButton > button:contains("ACESSAR ESTRATÉGIAS") {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
}

.stButton > button:contains("ACESSAR PLANO") {
    background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%) !important;
}

.stButton > button:contains("ACESSAR DIÁRIO") {
    background: linear-gradient(135deg, #64748B 0%, #475569 100%) !important;
}

.stButton > button:contains("ACESSAR EVOLUÇÃO") {
    background: linear-gradient(135deg, #64748B 0%, #475569 100%) !important;
}

/* Hover states */
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# pages/0_Home.py
import streamlit as st
from datetime import date, datetime
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v157.0 (Botão Funcional Fix)"

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
# 2. CSS & DESIGN SYSTEM - CORRIGIDO
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

/* --- CONTAINER DOS CARDS (NOVO) --- */
.mod-card-container {
    position: relative;
    margin-bottom: 20px;
    height: 120px;
}

/* --- CARDS DE MÓDULO (SIMPLIFICADO) --- */
.mod-card-rect {
    background: white;
    border-radius: 16px;
    padding: 0;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.01);
    display: flex; 
    flex-direction: row;
    align-items: center;
    height: 120px;
    width: 100%;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
    cursor: pointer;
}

.mod-card-rect:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.06);
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

/* BOTÃO VISUAL DENTRO DO CARD */
.mod-btn-visual {
    background-color: #4318FF;
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 6px 12px;
    border-radius: 6px;
    margin-right: 20px;
    white-space: nowrap;
    transition: all 0.2s;
    letter-spacing: 0.5px;
}

.mod-card-rect:hover .mod-btn-visual {
    background-color: #2B3674;
    transform: scale(1.05);
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

/* CORES TEMÁTICAS */
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

/* BOTÃO DO STREAMLIT INVISÍVEL (NOVA ABORDAGEM) */
.mod-btn-invisible {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    cursor: pointer;
    z-index: 5;
    border: none;
    background: transparent;
}

.mod-btn-invisible:hover {
    cursor: pointer;
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
# 4. FUNÇÃO PARA CRIAR CARDS CLICÁVEIS
# ==============================================================================
def create_clickable_card(title, desc, icon, color_cls, bg_cls, page_path, key):
    """Cria um card clicável com botão invisível"""
    
    # HTML do card (apenas visual)
    card_html = f"""
    <div class="mod-card-container">
        <div class="mod-card-rect" id="card_{key}">
            <div class="mod-bar {color_cls}"></div>
            <div class="mod-icon-area {bg_cls}">
                <i class="{icon} {color_cls}" style="background:transparent; -webkit-background-clip: text; color: transparent; filter: brightness(0.9);"></i>
                <i class="{icon}" style="color: inherit;"></i> 
            </div>
            <div class="mod-content">
                <div class="mod-title">{title}</div>
                <div class="mod-desc">{desc}</div>
            </div>
            <div class="mod-btn-visual">CLIQUE AQUI</div>
        </div>
    </div>
    <style>.{color_cls} {{ background-color: currentColor; }}</style>
    """
    
    # Renderizar o card
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Criar um botão invisível que cobre todo o card
    # Usamos um container para posicionar o botão
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        # O botão estará no meio (coluna 2), mas invisível
        with col2:
            # Botão invisível que cobre a área do card
            if st.button(f" ", key=f"btn_{key}", help=f"Acessar {title}"):
                # Lógica de navegação
                if "Alunos" in title or st.session_state.dados.get("nome"):
                    st.switch_page(page_path)
                else:
                    st.toast("Selecione um aluno primeiro!", icon="⚠️")
                    time.sleep(1)
                    st.switch_page("pages/0_Alunos.py")

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

# SIDEBAR
with st.sidebar:
    # Usar caminho relativo correto
    if os.path.exists("omni_icone.png"):
        st.image("omni_icone.png", width=60)
    else:
        st.markdown("🌐 **Omnisfera**")
    
    st.markdown("### Navegação")
    
    # Botões da sidebar que funcionam
    nav_options = [
        ("👥 Alunos", "pages/0_Alunos.py"),
        ("📘 PEI", "pages/1_PEI.py"),
        ("🧩 PAEE", "pages/2_PAE.py"),
        ("🚀 Hub", "pages/3_Hub_Inclusao.py"),
        ("📓 Diário", "pages/4_Diario_de_Bordo.py"),
        ("📊 Dados", "pages/5_Monitoramento_Avaliacao.py"),
    ]
    
    for label, page in nav_options:
        if st.button(label, use_container_width=True, key=f"sidebar_{label}"):
            st.switch_page(page)
    
    st.markdown("---")
    if st.button("🚪 Sair", use_container_width=True, key="sair"):
        st.session_state.autenticado = False
        st.rerun()

# HERO
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

# MÓDULOS (3 COLUNAS)
st.markdown("### 🚀 Seus Módulos")

# Definir os módulos
modules = [
    {
        "title": "Estudantes",
        "desc": "Gestão e histórico.",
        "icon": "ri-group-fill",
        "color": "c-indigo",
        "bg": "bg-indigo-soft",
        "page": "pages/0_Alunos.py",
        "key": "m_aluno"
    },
    {
        "title": "Hub de Recursos",
        "desc": "Materiais e IA.",
        "icon": "ri-rocket-2-fill",
        "color": "c-teal",
        "bg": "bg-teal-soft",
        "page": "pages/3_Hub_Inclusao.py",
        "key": "m_hub"
    },
    {
        "title": "Estratégias & PEI",
        "desc": "Plano Individualizado.",
        "icon": "ri-book-open-fill",
        "color": "c-blue",
        "bg": "bg-blue-soft",
        "page": "pages/1_PEI.py",
        "key": "m_pei"
    },
    {
        "title": "Plano de Ação / PAEE",
        "desc": "Sala de recursos.",
        "icon": "ri-puzzle-2-fill",
        "color": "c-purple",
        "bg": "bg-purple-soft",
        "page": "pages/2_PAE.py",
        "key": "m_pae"
    },
    {
        "title": "Diário de Bordo",
        "desc": "Registro de evidências.",
        "icon": "ri-file-list-3-fill",
        "color": "c-slate",
        "bg": "bg-slate-soft",
        "page": "pages/4_Diario_de_Bordo.py",
        "key": "m_diario"
    },
    {
        "title": "Evolução & Dados",
        "desc": "Indicadores e progresso.",
        "icon": "ri-bar-chart-box-fill",
        "color": "c-slate",
        "bg": "bg-slate-soft",
        "page": "pages/5_Monitoramento_Avaliacao.py",
        "key": "m_dados"
    }
]

# Criar grid 3x2
cols = st.columns(3, gap="medium")

# Distribuir módulos pelas colunas
for i, module in enumerate(modules):
    with cols[i % 3]:
        # Usar a nova função que cria cards clicáveis
        if st.button(f"**{module['title']}**", 
                    key=f"btn_main_{module['key']}",
                    help=f"Clique para acessar {module['title']}",
                    use_container_width=True):
            if "Alunos" in module['title'] or st.session_state.dados.get("nome"):
                st.switch_page(module['page'])
            else:
                st.toast("Selecione um aluno primeiro!", icon="⚠️")
                time.sleep(1)
                st.switch_page("pages/0_Alunos.py")
        
        # Card visual (agora apenas decorativo, o clique é no botão acima)
        st.markdown(f"""
        <div class="mod-card-rect">
            <div class="mod-bar {module['color']}"></div>
            <div class="mod-icon-area {module['bg']}">
                <i class="{module['icon']} {module['color']}" style="background:transparent; -webkit-background-clip: text; color: transparent; filter: brightness(0.9);"></i>
                <i class="{module['icon']}" style="color: inherit;"></i> 
            </div>
            <div class="mod-content">
                <div class="mod-title">{module['title']}</div>
                <div class="mod-desc">{module['desc']}</div>
            </div>
            <div class="mod-btn-visual">CLIQUE AQUI</div>
        </div>
        <style>.{module['color']} {{ background-color: currentColor; }}</style>
        """, unsafe_allow_html=True)

# RECURSOS EXTERNOS
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
st.markdown("### 📚 Recursos Externos")

# Criar colunas para recursos
r1, r2, r3, r4 = st.columns(4, gap="medium")

# Função para criar recursos
def create_resource(col, title, desc, icon, theme, link):
    with col:
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

# Adicionar recursos
create_resource(r1, "Lei da Inclusão", "LBI e diretrizes", "ri-government-fill", "rc-sky", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm")
create_resource(r2, "Base Nacional", "Competências BNCC", "ri-compass-3-fill", "rc-green", "http://basenacionalcomum.mec.gov.br/")
create_resource(r3, "Neurociência", "Artigos e estudos", "ri-brain-fill", "rc-rose", "https://institutoneurosaber.com.br/")
create_resource(r4, "Ajuda Omnisfera", "Tutoriais e suporte", "ri-question-fill", "rc-orange", "#")

# RODAPÉ
st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.75rem;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ • {}</div>".format(
    datetime.now().strftime("%d/%m/%Y")
), unsafe_allow_html=True)

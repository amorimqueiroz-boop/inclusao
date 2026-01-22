# pages/0_Home.py
import streamlit as st
from datetime import date
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v136.1 (Wide Dashboard + Fix)"

# Detecção de Ambiente
try:
    IS_TEST_ENV = st.secrets.get("ENV") == "TESTE"
except Exception:
    IS_TEST_ENV = False

st.set_page_config(
    page_title="Omnisfera",
    page_icon="omni_icone.png" if os.path.exists("omni_icone.png") else "🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. GATE DE ACESSO (PROTEÇÃO)
# ==============================================================================
def acesso_bloqueado(msg: str):
    st.markdown(f"""
    <div style="
        max-width: 500px; margin: 15vh auto; text-align: center; 
        padding: 40px; background: white; border-radius: 20px; 
        border: 1px solid #E2E8F0; box-shadow: 0 20px 50px rgba(0,0,0,0.05);
    ">
        <div style="font-size: 4rem; margin-bottom: 20px;">🔐</div>
        <div style="font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.5rem; color: #1A202C; margin-bottom: 10px;">
            Acesso Restrito
        </div>
        <div style="color: #718096; margin-bottom: 30px; font-size: 1rem;">
            {msg}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔑 Ir para Login", use_container_width=True, type="primary"):
            st.session_state.autenticado = False
            st.session_state.workspace_id = None
            st.rerun()
    st.stop()

if not st.session_state.get("autenticado", False):
    acesso_bloqueado("Sua sessão expirou ou não foi iniciada.")

if not st.session_state.get("workspace_id"):
    acesso_bloqueado("Nenhum workspace vinculado ao seu PIN.")

# ==============================================================================
# 3. HELPERS & STATE
# ==============================================================================
if "dados" not in st.session_state:
    st.session_state.dados = {"nome": "", "nasc": date(2015, 1, 1), "serie": None, "turma": "", "diagnostico": "", "student_id": None}

def get_base64_image(image_path: str) -> str:
    if not image_path or not os.path.exists(image_path): return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def escola_vinculada() -> str:
    return st.session_state.get("workspace_name") or st.session_state.get("workspace_id", "")[:8]

# ==============================================================================
# 4. CSS (DESIGN WIDE & FLUIDO)
# ==============================================================================
st.markdown("""
<style>
/* Fontes & Ícones */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Nunito:wght@400;600;700&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

/* Reset e Base */
html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    color: #1A202C;
    background-color: #F8FAFC; /* Fundo levemente azulado/cinza */
}

/* Limpeza do Streamlit */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }

/* LAYOUT WIDE (95% DA TELA) */
.block-container { 
    padding-top: 100px !important; 
    padding-bottom: 3rem !important; 
    max-width: 95% !important; 
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* --- TOPBAR FLUTUANTE --- */
.header-container {
    position: fixed; top: 0; left: 0; width: 100%; height: 75px;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(226, 232, 240, 0.6);
    z-index: 99999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 40px;
}

.logo-spin { height: 42px; width: auto; animation: spin 30s linear infinite; }
.logo-text { height: 28px; width: auto; margin-left: 12px; }
.header-div { width: 1px; height: 24px; background: #CBD5E0; margin: 0 20px; }
.header-slogan { font-weight: 600; color: #64748B; font-size: 0.9rem; letter-spacing: 0.2px; }

.header-badge {
    display: flex; flex-direction: column; align-items: flex-end;
}
.badge-label { font-size: 0.65rem; font-weight: 800; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; }
.badge-val { font-size: 0.9rem; font-weight: 800; color: #1E293B; }

@keyframes spin { 100% { transform: rotate(360deg); } }

/* --- HERO SECTION (WIDE) --- */
.hero-wide {
    background: linear-gradient(120deg, #1E40AF 0%, #3B82F6 100%);
    border-radius: 24px;
    padding: 40px 50px;
    color: white;
    box-shadow: 0 20px 40px -10px rgba(37, 99, 235, 0.3);
    margin-bottom: 50px;
    display: flex; 
    align-items: center; 
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}

.hero-wide::before {
    content: "";
    position: absolute;
    top: -50%; left: -10%; width: 50%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    transform: rotate(30deg);
    pointer-events: none;
}

.hero-content { position: relative; z-index: 1; }
.hero-welcome { font-family: 'Inter', sans-serif; font-weight: 900; font-size: 2.2rem; margin-bottom: 8px; letter-spacing: -1px; }
.hero-sub { opacity: 0.9; font-size: 1.1rem; font-weight: 500; max-width: 600px; line-height: 1.5; }

.hero-stats {
    display: flex; gap: 30px;
    background: rgba(255,255,255,0.1);
    padding: 15px 30px;
    border-radius: 16px;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255,255,255,0.2);
}
.stat-item { text-align: center; }
.stat-val { font-weight: 900; font-size: 1.4rem; line-height: 1; }
.stat-lbl { font-size: 0.75rem; opacity: 0.8; text-transform: uppercase; margin-top: 4px; font-weight: 600; }

/* --- CARDS (WIDE GRID) --- */
.flat-card {
    background: white;
    border-radius: 20px;
    padding: 30px;
    border: 1px solid #F1F5F9;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    min-height: 200px;
    position: relative;
    display: flex; flex-direction: column; 
    justify-content: flex-start;
}

.flat-card:hover {
    transform: translateY(-5px) scale(1.01);
    box-shadow: 0 20px 40px -5px rgba(0, 0, 0, 0.08);
    border-color: #E2E8F0;
    z-index: 10;
}

.icon-box {
    width: 60px; height: 60px;
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 28px;
    margin-bottom: 20px;
}

.card-title { 
    font-family: 'Inter', sans-serif; 
    font-weight: 800; 
    font-size: 1.25rem; 
    color: #1A202C; 
    margin-bottom: 10px; 
}
.card-desc { 
    font-size: 0.95rem; 
    color: #64748B; 
    line-height: 1.6; 
    flex-grow: 1; 
}
.card-footer {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #F1F5F9;
    font-size: 0.85rem; 
    font-weight: 700; 
    display: flex; align-items: center; gap: 8px;
    color: #475569;
    transition: color 0.2s;
}
.flat-card:hover .card-footer { color: #2563EB; }

/* Temas de Cor */
.theme-blue { background: #EFF6FF; color: #2563EB; }
.theme-purple { background: #FAF5FF; color: #9333EA; }
.theme-teal { background: #F0FDFA; color: #0D9488; }
.theme-indigo { background: #EEF2FF; color: #4F46E5; }
.theme-gray { background: #F8FAFC; color: #64748B; }

/* Botão Fantasma */
.ghost-btn button {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    opacity: 0; z-index: 20; cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. TOPBAR RENDER
# ==============================================================================
icone_b64 = get_base64_image("omni_icone.png")
texto_b64 = get_base64_image("omni_texto.png")
esc = escola_vinculada()

logo_html = f'<img src="data:image/png;base64,{icone_b64}" class="logo-spin">' if icone_b64 else "🌐"
nome_html = f'<img src="data:image/png;base64,{texto_b64}" class="logo-text">' if texto_b64 else "<b style='color:#0F52BA;margin-left:10px'>OMNISFERA</b>"

st.markdown(f"""
<div class="header-container">
    <div style="display:flex; align-items:center;">
        {logo_html}
        {nome_html}
        <div class="header-div"></div>
        <div class="header-slogan">Inteligência Pedagógica</div>
    </div>
    <div class="header-badge">
        <div class="badge-label">WORKSPACE ATIVO</div>
        <div class="badge-val">{esc if esc else "Não vinculado"}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown("### 🧭 Navegação")
    if st.button("👥 Alunos", use_container_width=True): st.switch_page("pages/0_Alunos.py")
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("📘 PEI", use_container_width=True): st.switch_page("pages/1_PEI.py")
    with c2: 
        if st.button("🧩 PAEE", use_container_width=True): st.switch_page("pages/2_PAE.py")
    
    if st.button("🚀 Hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")
    
    st.markdown("---")
    st.markdown(f"**👤 {st.session_state.get('usuario_nome', 'Usuário')}**")
    st.caption(st.session_state.get("usuario_cargo", "Educador"))
    
    if st.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# ==============================================================================
# 7. HERO SECTION (WIDE & STATS)
# ==============================================================================
nome_usuario = st.session_state.get('usuario_nome', 'Visitante').split()[0]

# Estatísticas Visuais
total_alunos = len(st.session_state.get("banco_estudantes", []))
aluno_ativo = st.session_state.dados.get("nome", "Nenhum")

# Correção do Erro de Split: Verifica se existe e não está vazio
display_aluno = "-"
if aluno_ativo and aluno_ativo != "Nenhum" and aluno_ativo.strip():
    display_aluno = aluno_ativo.split()[0]

st.markdown(f"""
<div class="hero-wide">
    <div class="hero-content">
        <div class="hero-welcome">Olá, {nome_usuario}!</div>
        <div class="hero-sub">
            Seu painel de controle está pronto. <br>
            Acesse seus módulos de inclusão com um clique.
        </div>
    </div>
    
    <div class="hero-stats">
        <div class="stat-item">
            <div class="stat-val">{total_alunos}</div>
            <div class="stat-lbl">Alunos</div>
        </div>
        <div style="width:1px; background:rgba(255,255,255,0.3);"></div>
        <div class="stat-item">
            <div class="stat-val">Ativo</div>
            <div class="stat-lbl">{display_aluno}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 8. MÓDULOS (GRID REDEFINIDO)
# ==============================================================================
st.markdown("### 🚀 Módulos da Omnisfera")

def render_module_card(title, desc, icon_class, theme_class, target_page, key, cta_text="Acessar"):
    st.markdown(f"""
    <div class="flat-card">
        <div class="icon-box {theme_class}">
            <i class="{icon_class}"></i>
        </div>
        <div>
            <div class="card-title">{title}</div>
            <div class="card-desc">{desc}</div>
        </div>
        <div class="card-footer">
            {cta_text} <i class="ri-arrow-right-line"></i>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button(f"btn_{key}", key=key):
        if target_page:
            if "Alunos" in title or st.session_state.dados.get("nome"):
                st.switch_page(target_page)
            else:
                st.toast("⚠️ Selecione um aluno no módulo 'Estudantes' primeiro!", icon="👇")
                time.sleep(1.5)
                st.switch_page("pages/0_Alunos.py")
        else:
            st.toast("🚧 Em desenvolvimento", icon="🔨")
    st.markdown('</div>', unsafe_allow_html=True)

# GRID DE 3 COLUNAS
c1, c2, c3 = st.columns(3, gap="large")

with c1:
    render_module_card(
        "Estudantes", 
        "Gestão centralizada, histórico clínico e seleção do aluno ativo.", 
        "ri-group-line", "theme-indigo", "pages/0_Alunos.py", "mod_alunos"
    )
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    render_module_card(
        "Hub de Recursos", 
        "Banco de adaptações, materiais pedagógicos e ferramentas de IA.", 
        "ri-rocket-2-line", "theme-teal", "pages/3_Hub_Inclusao.py", "mod_hub"
    )

with c2:
    render_module_card(
        "Estratégias & PEI", 
        "Criação e gestão do Plano Educacional Individualizado (PEI 360).", 
        "ri-book-open-line", "theme-blue", "pages/1_PEI.py", "mod_pei"
    )
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    render_module_card(
        "Diário de Bordo", 
        "Registro contínuo de evidências e anotações diárias.", 
        "ri-file-list-3-line", "theme-gray", "pages/4_Diario_de_Bordo.py", "mod_diario", "Em breve"
    )

with c3:
    render_module_card(
        "Plano de Ação / PAEE", 
        "Organização do AEE, intervenções e sala de recursos multifuncionais.", 
        "ri-puzzle-2-line", "theme-purple", "pages/2_PAE.py", "mod_pae"
    )
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    render_module_card(
        "Evolução & Dados", 
        "Indicadores, KPIs e visão longitudinal do progresso do aluno.", 
        "ri-bar-chart-box-line", "theme-gray", "pages/5_Monitoramento_Avaliacao.py", "mod_dados", "Em breve"
    )

# Footer
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.75rem; margin-top: 60px;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>", unsafe_allow_html=True)

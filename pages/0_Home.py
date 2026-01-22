# pages/0_Home.py
import streamlit as st
from datetime import datetime, date
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v142.0 (Portal Omnisfera)"

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
# 2. GATE DE ACESSO
# ==============================================================================
def acesso_bloqueado(msg: str):
    # HTML Flush (sem indentação) para evitar bug de renderização
    html_error = f"""
<div style="display:flex; justify-content:center; align-items:center; height:70vh;">
<div style="text-align:center; padding:40px; background:white; border-radius:24px; box-shadow:0 10px 40px rgba(0,0,0,0.08); max-width:480px; border:1px solid #E2E8F0;">
<div style="font-size:3rem; margin-bottom:15px;">🔐</div>
<h3 style="color:#1E293B; margin-bottom:10px; font-family:'Inter',sans-serif;">Acesso Restrito</h3>
<p style="color:#64748B; margin-bottom:25px;">{msg}</p>
</div>
</div>
"""
    st.markdown(html_error, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Ir para Login", type="primary", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.workspace_id = None
            st.rerun()
    st.stop()

if not st.session_state.get("autenticado", False):
    acesso_bloqueado("Sua sessão expirou.")

if not st.session_state.get("workspace_id"):
    acesso_bloqueado("Workspace não identificado.")

# ==============================================================================
# 3. HELPERS
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
# 4. CSS (DESIGN SYSTEM PORTAL)
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1E293B;
    background-color: #F8FAFC;
}

/* Limpeza UI Streamlit */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }
.block-container { 
    padding-top: 80px !important; 
    padding-bottom: 3rem !important; 
    max-width: 1300px !important; 
}

/* TOPBAR */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 64px;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid #E2E8F0;
    z-index: 9999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 32px;
}
.brand-area { display: flex; align-items: center; gap: 12px; }
.brand-logo { height: 32px; width: auto; animation: spin 40s linear infinite; }
.brand-text { font-weight: 800; font-size: 1.1rem; color: #0F172A; letter-spacing: -0.5px; }
.user-area { display: flex; align-items: center; gap: 16px; }
.workspace-badge { 
    background: #F1F5F9; padding: 4px 10px; border-radius: 6px; 
    font-size: 0.75rem; font-weight: 700; color: #64748B; border: 1px solid #E2E8F0; text-transform: uppercase;
}

/* HERO */
.hero-portal {
    background: linear-gradient(120deg, #1E40AF 0%, #2563EB 100%);
    border-radius: 20px;
    padding: 36px 40px;
    color: white;
    box-shadow: 0 10px 30px -10px rgba(37, 99, 235, 0.4);
    margin-bottom: 40px;
    display: flex; flex-direction: column; gap: 8px;
    position: relative; overflow: hidden;
}
.hero-portal::before {
    content: ""; position: absolute; top: -50px; right: -50px; width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.hero-title { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.8rem; margin: 0; }
.hero-quote { font-size: 1.05rem; opacity: 0.9; font-style: italic; max-width: 800px; line-height: 1.6; }

/* MODULE CARDS */
.mod-card {
    background: white; border-radius: 16px; padding: 24px;
    border: 1px solid #E2E8F0; height: 100%; min-height: 150px;
    position: relative; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex; flex-direction: column; justify-content: space-between;
}
.mod-card:hover {
    transform: translateY(-4px); box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.08); border-color: #CBD5E1;
}
.mod-icon {
    width: 44px; height: 44px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; margin-bottom: 16px;
}
.mod-title { font-weight: 700; font-size: 1.05rem; color: #1E293B; margin-bottom: 4px; }
.mod-desc { font-size: 0.85rem; color: #64748B; line-height: 1.4; }
.mod-cta {
    font-size: 0.8rem; font-weight: 700; margin-top: 15px; display: flex; align-items: center; gap: 5px;
    padding-top: 15px; border-top: 1px solid #F1F5F9;
}

/* INFO CARDS (FUNDAMENTOS) */
.info-section { margin-top: 40px; margin-bottom: 20px; }
.info-header { font-size: 1.2rem; font-weight: 800; color: #1E293B; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
.info-box {
    background: white; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0;
    margin-bottom: 15px;
}
.info-title { font-weight: 700; color: #0F172A; margin-bottom: 8px; font-size: 1rem; }
.info-text { font-size: 0.9rem; color: #475569; line-height: 1.6; }
.highlight { color: #2563EB; font-weight: 600; }

/* RESOURCE LINKS */
.res-card {
    background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px;
    display: flex; align-items: center; gap: 12px; transition: all 0.2s;
}
.res-card:hover { background: white; border-color: #CBD5E1; transform: translateY(-2px); }
.res-icon { font-size: 1.5rem; color: #64748B; }
.res-text { font-weight: 600; color: #1E293B; font-size: 0.9rem; }

/* THEMES */
.t-indigo { background: #EEF2FF; color: #4F46E5; }
.t-blue { background: #EFF6FF; color: #2563EB; }
.t-purple { background: #FAF5FF; color: #9333EA; }
.t-teal { background: #F0FDFA; color: #0D9488; }
.t-slate { background: #F8FAFC; color: #64748B; }

.ghost-btn button { position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; z-index: 10; cursor: pointer; }
@keyframes spin { 100% { transform: rotate(360deg); } }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. RENDER HEADER
# ==============================================================================
icone_b64 = get_base64_image("omni_icone.png")
workspace_name = escola_vinculada()
usuario_nome = st.session_state.get('usuario_nome', 'Visitante')
iniciais = usuario_nome[:2].upper() if usuario_nome else "UN"

logo_img = f'<img src="data:image/png;base64,{icone_b64}" class="brand-logo">' if icone_b64 else "🌐"

st.markdown(f"""
<div class="topbar">
    <div class="brand-area">
        {logo_img}
        <div class="brand-text">OMNISFERA</div>
    </div>
    <div class="user-area">
        <div class="workspace-badge">{workspace_name}</div>
        <div style="font-weight:600; color:#1E293B; font-size:0.9rem;">{usuario_nome.split()[0]}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. SIDEBAR (Navegação Auxiliar)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🧭 Navegação")
    # Nota: Usando 'pages/0_Alunos.py' baseado na lista de arquivos. Ajuste se necessário.
    if st.button("👥 Alunos", use_container_width=True): st.switch_page("pages/0_Alunos.py")
    
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("📘 PEI", use_container_width=True): st.switch_page("pages/1_PEI.py")
    with c2: 
        if st.button("🧩 PAEE", use_container_width=True): st.switch_page("pages/2_PAE.py")
    
    if st.button("🚀 Hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")
    
    st.markdown("---")
    if st.button("Sair", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# ==============================================================================
# 7. CONTEÚDO PRINCIPAL
# ==============================================================================

# HERO (Inspiracional)
frase_inclusao = "A inclusão não é sobre inserir pessoas em moldes pré-existentes, mas sobre transformar o ambiente para que todos possam pertencer."

st.markdown(f"""
<div class="hero-portal">
    <div class="hero-title">Olá, {usuario_nome.split()[0]}!</div>
    <div class="hero-quote">"{frase_inclusao}"</div>
</div>
""", unsafe_allow_html=True)

# MÓDULOS (Grid Principal)
st.markdown("### 🚀 Acesso aos Módulos")

def render_module(title, desc, icon, theme, page_path, key):
    # HTML SEM indentação interna para evitar bugs
    html = f"""
<div class="mod-card">
<div class="mod-icon {theme}"><i class="{icon}"></i></div>
<div>
<div class="mod-title">{title}</div>
<div class="mod-desc">{desc}</div>
</div>
<div class="mod-cta" style="color:inherit">Acessar <i class="ri-arrow-right-line"></i></div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
    
    st.markdown(f'<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button(f"btn_{key}", key=key):
        st.switch_page(page_path)
    st.markdown('</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4, gap="medium")

with c1:
    render_module("Estudantes", "Gestão e histórico.", "ri-group-line", "t-indigo", "pages/0_Alunos.py", "m_aluno")
with c2:
    render_module("PEI 360°", "Estratégias e Plano.", "ri-book-open-line", "t-blue", "pages/1_PEI.py", "m_pei")
with c3:
    render_module("PAEE", "Sala de Recursos.", "ri-puzzle-2-line", "t-purple", "pages/2_PAE.py", "m_pae")
with c4:
    render_module("Hub Inclusão", "Materiais e IA.", "ri-rocket-2-line", "t-teal", "pages/3_Hub_Inclusao.py", "m_hub")

# SEÇÃO DE FUNDAMENTOS (Conteúdo Rico em Abas)
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
st.markdown('<div class="info-header"><i class="ri-book-mark-fill" style="color:#2563EB;"></i> Fundamentos da Inclusão</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏛️ Cultura Inclusiva", "🚫 Combate ao Capacitismo", "🏫 A Escola Necessária"])

with tab1:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("""
        <div class="info-box">
            <div class="info-title">Foco: A filosofia do acolhimento real</div>
            <div class="info-text">
                <span class="highlight">Conceito de "Outrar-se":</span> A inclusão exige a capacidade de "fazer-se outro", sentir o mundo do outro numa relação empática, sem confundir os sentimentos.
            </div>
        </div>
        <div class="info-box">
            <div class="info-title">Pertencimento vs. Retórica</div>
            <div class="info-text">
                Receber o aluno é diferente de incluí-lo. É necessário criar uma cultura onde a presença física venha acompanhada de participação efetiva. Não basta falar sobre inclusão, é preciso vivê-la.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="info-box" style="border-left: 4px solid #2563EB;">
            <div class="info-title">Justiça Curricular</div>
            <div class="info-text">
                O currículo deve representar e respeitar todos os grupos sociais, oferecendo condições igualitárias de desenvolvimento. Adaptação não é favor, é direito e justiça.
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="info-box">
        <div class="info-title">O que é Capacitismo?</div>
        <div class="info-text">
            É qualquer discriminação que prejudique a pessoa com deficiência (PCD), baseada na premissa de que a deficiência a torna "menos capaz" ou "inferior".
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    t2_c1, t2_c2 = st.columns(2)
    with t2_c1:
        st.markdown("""
        <div class="info-box">
            <div class="info-title">⚠️ Atenção à Linguagem</div>
            <div class="info-text">
                Evite metáforas que reforçam estigmas (ex: "dar uma de joão-sem-braço", "fingir demência"). A linguagem constrói realidade.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with t2_c2:
        st.markdown("""
        <div class="info-box">
            <div class="info-title">👁️ Visão de Potência</div>
            <div class="info-text">
                Abandonar a visão de "limitação" e focar nas habilidades que podem ser desenvolvidas. Todo aluno aprende, mas não no mesmo tempo nem do mesmo jeito.
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class="info-box">
        <div class="info-title">Características de um ambiente sensibilizado</div>
        <ul style="margin:0; padding-left:20px; color:#475569; font-size:0.9rem;">
            <li style="margin-bottom:10px;"><b>Equipe Engajada:</b> Educadores interessados nos direitos de TODOS, não apenas dos que se encaixam no padrão.</li>
            <li style="margin-bottom:10px;"><b>Eventos Acessíveis:</b> Festas e atividades extracurriculares planejadas para que todos participem plenamente.</li>
            <li style="margin-bottom:10px;"><b>Formação Contínua:</b> Busca constante por práticas anticapacitistas e diversidade.</li>
            <li><b>Parceria com Famílias:</b> Uma relação de confiança e troca, fundamental para o sucesso do PEI.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# RODAPÉ DE RECURSOS (LINKS ÚTEIS)
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
st.markdown('<div class="info-header"><i class="ri-links-line" style="color:#64748B;"></i> Recursos Externos</div>', unsafe_allow_html=True)

r1, r2, r3, r4 = st.columns(4)

def render_resource(col, icon, text, link):
    with col:
        st.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration:none;">
            <div class="res-card">
                <i class="{icon} res-icon"></i>
                <div class="res-text">{text}</div>
            </div>
        </a>
        """, unsafe_allow_html=True)

render_resource(r1, "ri-file-text-line", "Lei da Inclusão", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm")
render_resource(r2, "ri-compass-3-line", "Base Nacional (BNCC)", "http://basenacionalcomum.mec.gov.br/")
render_resource(r3, "ri-brain-line", "Neurociência", "https://institutoneurosaber.com.br/")
render_resource(r4, "ri-question-line", "Ajuda Omnisfera", "#")

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.75rem;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>", unsafe_allow_html=True)

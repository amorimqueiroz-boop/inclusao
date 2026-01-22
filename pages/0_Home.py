# pages/0_Home.py
import streamlit as st
from datetime import date, datetime
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v146.0 (Grid 3x2 Full Width)"

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
# 2. CSS & DESIGN SYSTEM (AJUSTADO PARA TELA TODA)
# ==============================================================================
st.markdown("""
<style>
/* Fontes e Ícones */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1E293B;
    background-color: #F8FAFC;
}

/* Limpeza Geral */
[data-testid="stSidebarNav"], [data-testid="stHeader"] { display: none !important; }

/* LAYOUT FULL WIDTH */
.block-container { 
    padding-top: 80px !important; 
    padding-bottom: 4rem !important; 
    max-width: 95% !important; /* Ocupa a tela toda */
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* --- HEADER --- */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 70px;
    background: rgba(255,255,255,0.9); backdrop-filter: blur(12px);
    border-bottom: 1px solid #E2E8F0; z-index: 9999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 40px;
}
.brand-box { display: flex; align-items: center; gap: 12px; }
.brand-logo { height: 36px; width: auto; animation: spin 45s linear infinite; }
.brand-name { font-weight: 800; font-size: 1.1rem; color: #0F172A; letter-spacing: -0.5px; }
.user-badge { 
    background: #F1F5F9; border: 1px solid #E2E8F0; 
    padding: 6px 14px; border-radius: 99px; font-size: 0.8rem; font-weight: 700; color: #64748B;
}

/* --- HERO SECTION --- */
.hero-wrapper {
    background: linear-gradient(120deg, #1E3A8A 0%, #2563EB 100%);
    border-radius: 20px; padding: 40px; color: white;
    margin-bottom: 40px; position: relative; overflow: hidden;
    box-shadow: 0 15px 30px -10px rgba(30, 58, 138, 0.3);
    display: flex; align-items: center; justify-content: space-between;
}
.hero-wrapper::after {
    content: ""; position: absolute; right: -50px; top: -50px;
    width: 300px; height: 300px; background: rgba(255,255,255,0.1);
    border-radius: 50%; pointer-events: none;
}
.hero-content { z-index: 1; }
.hero-greet { font-size: 2rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -1px; }
.hero-text { font-size: 1.05rem; opacity: 0.95; max-width: 800px; }

/* --- CARDS DE MÓDULO (RETANGULARES 3 COLUNAS) --- */
.mod-card-rect {
    background: white;
    border-radius: 16px;
    padding: 0;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.01);
    display: flex; flex-direction: row;
    align-items: center;
    height: 110px; /* Altura controlada */
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}

.mod-card-rect:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.06);
    border-color: #CBD5E1;
}

.mod-bar { width: 5px; height: 100%; flex-shrink: 0; }

.mod-icon-area {
    width: 80px; height: 100%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.8rem; flex-shrink: 0;
    background: #FAFAFA;
    border-right: 1px solid #F1F5F9;
}

.mod-content {
    flex-grow: 1; padding: 0 20px;
    display: flex; flex-direction: column; justify-content: center;
}
.mod-title { font-weight: 800; font-size: 1rem; color: #1E293B; margin-bottom: 3px; }
.mod-desc { font-size: 0.8rem; color: #64748B; line-height: 1.3; }

.mod-action {
    width: 50px; height: 100%;
    display: flex; align-items: center; justify-content: center;
    color: #CBD5E1; font-size: 1.4rem;
    transition: color 0.2s;
}
.mod-card-rect:hover .mod-action { color: #3B82F6; }

/* BOTÃO INVISÍVEL (OVERLAY) */
.ghost-btn-container {
    position: relative;
    height: 110px; /* Igual ao card */
    margin-top: -110px; /* Puxa para cima */
    z-index: 10;
}
.ghost-btn-container button {
    width: 100%; height: 100%;
    opacity: 0; border: none; cursor: pointer;
}

/* --- RECURSOS --- */
.res-card-link { text-decoration: none !important; display: block; height: 100%; }
.res-card {
    background: white; border-radius: 14px; padding: 18px;
    border: 1px solid #E2E8F0; display: flex; align-items: center; gap: 14px;
    transition: all 0.2s; height: 100%;
}
.res-card:hover { transform: translateY(-3px); box-shadow: 0 8px 16px rgba(0,0,0,0.05); }
.res-icon { 
    width: 42px; height: 42px; border-radius: 10px; 
    display: flex; align-items: center; justify-content: center; font-size: 1.3rem;
}
.res-info { display: flex; flex-direction: column; }
.res-name { font-weight: 700; color: #1E293B; font-size: 0.9rem; }
.res-meta { font-size: 0.75rem; font-weight: 600; opacity: 0.8; }

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

@keyframes spin { 100% { transform: rotate(360deg); } }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. HELPERS
# ==============================================================================
def acesso_bloqueado(msg):
    st.markdown(f"<div style='text-align:center; padding:50px; color:#64748B;'><h3>🔐 Acesso Restrito</h3><p>{msg}</p></div>", unsafe_allow_html=True)
    if st.button("Ir para Login"):
        st.session_state.autenticado = False; st.session_state.workspace_id = None; st.rerun()
    st.stop()

if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
    acesso_bloqueado("Sessão inválida.")

if "dados" not in st.session_state: st.session_state.dados = {"nome": "", "nasc": date(2015,1,1), "serie": None}

def get_base64_image(image_path):
    if not os.path.exists(image_path): return ""
    with open(image_path, "rb") as f: return base64.b64encode(f.read()).decode()

def escola_vinculada():
    return st.session_state.get("workspace_name") or st.session_state.get("workspace_id", "")[:8]

# ==============================================================================
# 4. RENDERIZAÇÃO
# ==============================================================================

# TOPBAR
icone_b64 = get_base64_image("omni_icone.png")
workspace = escola_vinculada()
nome_user = st.session_state.get('usuario_nome', 'Visitante').split()[0]
img_logo = f'<img src="data:image/png;base64,{icone_b64}" class="brand-logo">' if icone_b64 else "🌐"

st.markdown(f"""
<div class="topbar">
    <div class="brand-box">{img_logo} <div class="brand-name">OMNISFERA</div></div>
    <div class="brand-box">
        <div class="user-badge">{workspace}</div>
        <div style="font-weight:700; color:#334155;">{nome_user}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("### Navegação")
    if st.button("👥 Alunos", use_container_width=True): st.switch_page("pages/0_Alunos.py")
    if st.button("📘 PEI", use_container_width=True): st.switch_page("pages/1_PEI.py")
    if st.button("🧩 PAEE", use_container_width=True): st.switch_page("pages/2_PAE.py")
    if st.button("🚀 Hub", use_container_width=True): st.switch_page("pages/3_Hub_Inclusao.py")
    st.markdown("---")
    if st.button("Sair", use_container_width=True):
        st.session_state.autenticado = False; st.rerun()

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

# MÓDULOS (3 COLUNAS - 2 POR LINHA - BOTÃO INTEGRADO)
st.markdown("### 🚀 Seus Módulos")

def render_rect_module(title, desc, icon, color_cls, bg_cls, page_path, key):
    # 1. Card Visual
    st.markdown(f"""
    <div class="mod-card-rect">
        <div class="mod-bar {color_cls}"></div>
        <div class="mod-icon-area {bg_cls}">
            <i class="{icon} {color_cls}" style="background:transparent; -webkit-background-clip: text; color: transparent; filter: brightness(0.9);"></i>
            <i class="{icon}" style="color: inherit;"></i> 
        </div>
        <div class="mod-content">
            <div class="mod-title">{title}</div>
            <div class="mod-desc">{desc}</div>
        </div>
        <div class="mod-action"><i class="ri-arrow-right-s-line"></i></div>
    </div>
    <style>.{color_cls} {{ background-color: currentColor; }}</style>
    """, unsafe_allow_html=True)
    
    # 2. Botão Overlay
    st.markdown('<div class="ghost-btn-container">', unsafe_allow_html=True)
    if st.button(f"btn_{key}", key=key):
        if "Alunos" in title or st.session_state.dados.get("nome"):
            st.switch_page(page_path)
        else:
            st.toast("Selecione um aluno primeiro!", icon="⚠️")
            time.sleep(1)
            st.switch_page("pages/0_Alunos.py")
    st.markdown('</div>', unsafe_allow_html=True)

# GRID 3 COLUNAS (3x2)
c1, c2, c3 = st.columns(3, gap="medium")

# Coluna 1: Base & Apoio
with c1:
    render_rect_module("Estudantes", "Gestão e histórico.", "ri-group-fill", "c-indigo", "bg-indigo-soft", "pages/0_Alunos.py", "m_aluno")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_rect_module("Hub de Recursos", "Banco de materiais e IA.", "ri-rocket-2-fill", "c-teal", "bg-teal-soft", "pages/3_Hub_Inclusao.py", "m_hub")

# Coluna 2: Planejamento
with c2:
    render_rect_module("Estratégias & PEI", "Plano Individualizado.", "ri-book-open-fill", "c-blue", "bg-blue-soft", "pages/1_PEI.py", "m_pei")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_rect_module("Plano de Ação / PAEE", "Sala de recursos.", "ri-puzzle-2-fill", "c-purple", "bg-purple-soft", "pages/2_PAE.py", "m_pae")

# Coluna 3: Acompanhamento
with c3:
    render_rect_module("Diário de Bordo", "Registro de evidências.", "ri-file-list-3-fill", "c-slate", "bg-slate-soft", "pages/4_Diario_de_Bordo.py", "m_diario")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_rect_module("Evolução & Dados", "Indicadores e progresso.", "ri-bar-chart-box-fill", "c-slate", "bg-slate-soft", "pages/5_Monitoramento_Avaliacao.py", "m_dados")

# RECURSOS EXTERNOS
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
st.markdown("### 📚 Recursos Externos")

def render_resource(col, title, desc, icon, theme, link):
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

r1, r2, r3, r4 = st.columns(4, gap="medium")

render_resource(r1, "Lei da Inclusão", "LBI e diretrizes", "ri-government-fill", "rc-sky", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm")
render_resource(r2, "Base Nacional", "Competências BNCC", "ri-compass-3-fill", "rc-green", "http://basenacionalcomum.mec.gov.br/")
render_resource(r3, "Neurociência", "Artigos e estudos", "ri-brain-fill", "rc-rose", "https://institutoneurosaber.com.br/")
render_resource(r4, "Ajuda Omnisfera", "Tutoriais e suporte", "ri-question-fill", "rc-orange", "#")

st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.75rem;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>", unsafe_allow_html=True)

# pages/0_Home.py
import streamlit as st
from datetime import date
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v138.0 (Fix HTML Rendering)"

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
# 2. GATE DE ACESSO
# ==============================================================================
def acesso_bloqueado(msg: str):
    # HTML sem indentação para não quebrar
    html_alert = f"""
<div style="max-width:500px; margin:100px auto; text-align:center; padding:30px; background:white; border-radius:16px; border:1px solid #E2E8F0; box-shadow:0 10px 30px rgba(0,0,0,0.08);">
<div style="font-size:3rem; margin-bottom:15px;">🔐</div>
<div style="font-weight:800; font-size:1.2rem; color:#2D3748; margin-bottom:8px;">Acesso Restrito</div>
<div style="color:#718096; margin-bottom:20px;">{msg}</div>
</div>
"""
    st.markdown(html_alert, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔑 Ir para Login", use_container_width=True, type="primary"):
            st.session_state.autenticado = False
            st.session_state.workspace_id = None
            st.rerun()
    st.stop()

if not st.session_state.get("autenticado", False):
    acesso_bloqueado("Sessão expirada ou não iniciada.")

if not st.session_state.get("workspace_id"):
    acesso_bloqueado("Nenhum workspace vinculado.")

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
# 4. CSS (DESIGN SYSTEM)
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Nunito:wght@400;600;700&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
    color: #1A202C;
    background-color: #F8FAFC;
}

[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }

/* CONTROLE DE LARGURA */
.block-container { 
    padding-top: 90px !important; 
    padding-bottom: 3rem !important; 
    max-width: 1200px !important;
}

/* TOPBAR */
.header-container {
    position: fixed; top: 0; left: 0; width: 100%; height: 70px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #E2E8F0;
    z-index: 99999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 30px;
}
.logo-spin { height: 38px; width: auto; animation: spin 30s linear infinite; }
.logo-text { height: 26px; width: auto; margin-left: 10px; }
.header-div { width: 1px; height: 24px; background: #CBD5E0; margin: 0 15px; }
.header-slogan { font-weight: 600; color: #64748B; font-size: 0.85rem; }
.header-badge {
    display: flex; flex-direction: column; align-items: flex-end;
}
.badge-label { font-size: 0.6rem; font-weight: 800; color: #94A3B8; text-transform: uppercase; }
.badge-val { font-size: 0.85rem; font-weight: 800; color: #1E293B; }

@keyframes spin { 100% { transform: rotate(360deg); } }

/* HERO */
.hero-box {
    background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
    border-radius: 16px;
    padding: 30px 40px;
    color: white;
    box-shadow: 0 10px 30px -5px rgba(37, 99, 235, 0.3);
    margin-bottom: 30px;
    display: flex; align-items: center; justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.hero-box::before {
    content: ""; position: absolute; top: -50%; left: -10%; width: 50%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    transform: rotate(30deg); pointer-events: none;
}
.hero-content { position: relative; z-index: 1; }
.hero-welcome { font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.8rem; margin-bottom: 5px; }
.hero-sub { opacity: 0.9; font-size: 1rem; font-weight: 500; }

.hero-stats {
    display: flex; gap: 20px;
    background: rgba(255,255,255,0.1);
    padding: 10px 20px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.2);
}
.stat-val { font-weight: 800; font-size: 1.2rem; line-height: 1; text-align: center; }
.stat-lbl { font-size: 0.7rem; opacity: 0.8; text-transform: uppercase; margin-top: 4px; text-align: center; }

/* CARDS */
.flat-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    transition: all 0.2s ease;
    height: 160px;
    position: relative;
    display: flex; flex-direction: column; 
    justify-content: space-between;
    overflow: hidden;
}
.flat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.06);
    border-color: #CBD5E0;
}
.icon-box {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    margin-bottom: 12px;
}
.card-title { 
    font-family: 'Inter', sans-serif; font-weight: 700; 
    font-size: 1.05rem; color: #1A202C; margin-bottom: 4px; 
}
.card-desc { font-size: 0.85rem; color: #718096; line-height: 1.4; }
.card-footer {
    font-size: 0.8rem; font-weight: 700; color: #475569;
    display: flex; align-items: center; gap: 6px;
    border-top: 1px solid #F1F5F9;
    padding-top: 10px;
    margin-top: 10px;
}
.flat-card:hover .card-footer { color: #2563EB; }

.theme-blue { background: #EBF8FF; color: #3182CE; }
.theme-purple { background: #FAF5FF; color: #805AD5; }
.theme-teal { background: #E6FFFA; color: #319795; }
.theme-indigo { background: #EEF2FF; color: #4F46E5; }
.theme-gray { background: #F7FAFC; color: #718096; }

/* Botão fantasma para clique total */
.ghost-btn {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10;
}
.ghost-btn button {
    width: 100% !important; height: 100% !important;
    opacity: 0 !important; cursor: pointer !important;
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
<div class="badge-label">WORKSPACE</div>
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
# 7. HERO SECTION
# ==============================================================================
nome_usuario = st.session_state.get('usuario_nome', 'Visitante').split()[0]
total_alunos = len(st.session_state.get("banco_estudantes", []))
aluno_ativo = st.session_state.dados.get("nome", "")

# Correção segura para nome do aluno
display_aluno = "Nenhum"
if aluno_ativo and isinstance(aluno_ativo, str) and aluno_ativo.strip():
    display_aluno = aluno_ativo.split()[0]

st.markdown(f"""
<div class="hero-box">
<div class="hero-content">
<div class="hero-welcome">Olá, {nome_usuario}!</div>
<div class="hero-sub">Seu painel de controle está pronto.</div>
</div>
<div class="hero-stats">
<div style="text-align:center">
<div class="stat-val">{total_alunos}</div>
<div class="stat-lbl">Alunos</div>
</div>
<div style="width:1px; background:rgba(255,255,255,0.3); margin:0 5px;"></div>
<div style="text-align:center">
<div class="stat-val">{display_aluno}</div>
<div class="stat-lbl">Ativo</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 8. MÓDULOS (CARDS)
# ==============================================================================
st.markdown("### 🚀 Módulos")

def render_module_card(title, desc, icon_class, theme_class, target_page, key, cta_text="Acessar"):
    # Renderiza o Card HTML SEM IDENTAÇÃO para evitar bug de renderização
    html_content = f"""
<div class="flat-card">
<div class="icon-box {theme_class}"><i class="{icon_class}"></i></div>
<div>
<div class="card-title">{title}</div>
<div class="card-desc">{desc}</div>
</div>
<div class="card-footer">{cta_text} <i class="ri-arrow-right-line"></i></div>
</div>
"""
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Botão invisível do Streamlit por cima
    st.markdown(f'<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button(f"btn_{key}", key=key):
        if target_page:
            if "Alunos" in title or st.session_state.dados.get("nome"):
                st.switch_page(target_page)
            else:
                st.toast("⚠️ Selecione um aluno primeiro!", icon="👇")
                time.sleep(1)
                st.switch_page("pages/0_Alunos.py")
        else:
            st.toast("🚧 Em desenvolvimento", icon="🔨")
    st.markdown('</div>', unsafe_allow_html=True)

# Grid
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    render_module_card("Estudantes", "Gestão e histórico.", "ri-group-line", "theme-indigo", "pages/0_Alunos.py", "m_aluno")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_module_card("Hub de Recursos", "Banco de materiais e IA.", "ri-rocket-2-line", "theme-teal", "pages/3_Hub_Inclusao.py", "m_hub")

with c2:
    render_module_card("Estratégias & PEI", "Plano Individualizado.", "ri-book-open-line", "theme-blue", "pages/1_PEI.py", "m_pei")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_module_card("Diário de Bordo", "Registro de evidências.", "ri-file-list-3-line", "theme-gray", "pages/4_Diario_de_Bordo.py", "m_diario", "Em breve")

with c3:
    render_module_card("Plano de Ação / PAEE", "Sala de recursos.", "ri-puzzle-2-line", "theme-purple", "pages/2_PAE.py", "m_pae")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_module_card("Evolução & Dados", "Indicadores e KPIs.", "ri-bar-chart-box-line", "theme-gray", "pages/5_Monitoramento_Avaliacao.py", "m_dados", "Em breve")

st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.75rem; margin-top: 40px;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>", unsafe_allow_html=True)

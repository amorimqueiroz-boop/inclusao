# pages/0_Home.py
import streamlit as st
from datetime import datetime, date
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v141.0 (Navegação Livre)"

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
    html_error = f"""
<div style="display:flex; justify-content:center; align-items:center; height:80vh;">
<div style="text-align:center; padding:40px; background:white; border-radius:24px; box-shadow:0 20px 60px rgba(0,0,0,0.08); max-width:480px; border:1px solid #E2E8F0;">
<div style="font-size:4rem; margin-bottom:10px;">🔒</div>
<h2 style="color:#1E293B; margin-bottom:10px; font-family:'Inter',sans-serif;">Acesso Restrito</h2>
<p style="color:#64748B; margin-bottom:30px;">{msg}</p>
</div>
</div>
"""
    st.markdown(html_error, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🔑 Voltar para Login", type="primary", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.workspace_id = None
            st.rerun()
    st.stop()

if not st.session_state.get("autenticado", False):
    acesso_bloqueado("Sessão finalizada. Por favor, faça login novamente.")

if not st.session_state.get("workspace_id"):
    acesso_bloqueado("Workspace não identificado.")

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
# 4. CSS (DESIGN SYSTEM PRO)
# ==============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: #1E293B;
    background-color: #F1F5F9;
}

[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }
.block-container { 
    padding-top: 80px !important; 
    padding-bottom: 2rem !important; 
    max-width: 1400px !important; 
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* TOPBAR */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 64px;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(226, 232, 240, 0.6);
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
    font-size: 0.75rem; font-weight: 600; color: #475569; border: 1px solid #E2E8F0;
}
.user-avatar {
    width: 32px; height: 32px; border-radius: 50%; background: #3B82F6; color: white;
    display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem;
}

/* HERO SECTION */
.welcome-card {
    background: white;
    border-radius: 20px;
    padding: 32px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    margin-bottom: 32px;
    display: flex; justify-content: space-between; align-items: center;
}
.welcome-text h1 { margin: 0; font-size: 1.8rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em; }
.welcome-text p { margin: 4px 0 0 0; color: #64748B; font-size: 0.95rem; }

.quick-actions { display: flex; gap: 12px; }
.action-btn-mock {
    background: #EFF6FF; color: #2563EB; border: 1px solid #DBEAFE;
    padding: 8px 16px; border-radius: 10px; font-size: 0.85rem; font-weight: 600;
    display: flex; align-items: center; gap: 6px; cursor: pointer; transition: all 0.2s;
}
.action-btn-mock:hover { background: #DBEAFE; transform: translateY(-1px); }

/* CARDS */
.module-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    border: 1px solid #E2E8F0;
    height: 100%; min-height: 160px;
    position: relative;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex; flex-direction: column; justify-content: space-between;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.module-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.08);
    border-color: #CBD5E1;
}
.mod-icon {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; margin-bottom: 16px;
}
.mod-title { font-weight: 700; font-size: 1.1rem; color: #1E293B; margin-bottom: 4px; }
.mod-desc { font-size: 0.85rem; color: #64748B; line-height: 1.4; }
.mod-arrow { 
    position: absolute; top: 24px; right: 24px; 
    color: #CBD5E1; transition: all 0.2s; 
}
.module-card:hover .mod-arrow { color: #3B82F6; transform: translateX(2px); }

/* WIDGETS */
.widget-card {
    background: white; border-radius: 16px; padding: 20px;
    border: 1px solid #E2E8F0; margin-bottom: 20px;
}
.widget-title {
    font-size: 0.85rem; font-weight: 700; color: #94A3B8; 
    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px;
}
.timeline-item { display: flex; gap: 12px; margin-bottom: 16px; }
.tl-dot {
    width: 8px; height: 8px; border-radius: 50%; background: #CBD5E1;
    margin-top: 6px; flex-shrink: 0;
}
.tl-content { font-size: 0.85rem; color: #475569; }
.tl-time { font-size: 0.75rem; color: #94A3B8; margin-top: 2px; }

.bg-indigo { background: #EEF2FF; color: #4F46E5; }
.bg-blue { background: #EFF6FF; color: #2563EB; }
.bg-purple { background: #FAF5FF; color: #9333EA; }
.bg-teal { background: #F0FDFA; color: #0D9488; }
.bg-slate { background: #F8FAFC; color: #64748B; }

.ghost-btn button {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    opacity: 0; z-index: 10; cursor: pointer;
}

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
        <div class="user-avatar">{iniciais}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 6. CONTEÚDO PRINCIPAL
# ==============================================================================

# Hero Section
dt_now = datetime.now()
saudacao = "Bom dia" if 5 <= dt_now.hour < 12 else "Boa tarde" if 12 <= dt_now.hour < 18 else "Boa noite"

st.markdown(f"""
<div class="welcome-card">
    <div class="welcome-text">
        <h1>{saudacao}, {usuario_nome.split()[0]}!</h1>
        <p>Aqui está o resumo das suas atividades de inclusão hoje.</p>
    </div>
    <div class="quick-actions">
        <div class="action-btn-mock"><i class="ri-add-circle-line"></i> Novo Aluno</div>
        <div class="action-btn-mock"><i class="ri-file-edit-line"></i> Anotação</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Layout: 70% Módulos | 30% Sidebar Widgets
col_main, col_side = st.columns([2.5, 1], gap="medium")

# --- ESQUERDA: MÓDULOS ---
with col_main:
    st.markdown("### 🚀 Seus Módulos", unsafe_allow_html=True)
    
    def draw_module(title, desc, icon, color_cls, page_path, key):
        # HTML do Card
        html = f"""
<div class="module-card">
<div class="mod-icon {color_cls}"><i class="{icon}"></i></div>
<div class="mod-arrow"><i class="ri-arrow-right-up-line"></i></div>
<div>
<div class="mod-title">{title}</div>
<div class="mod-desc">{desc}</div>
</div>
</div>
"""
        st.markdown(html, unsafe_allow_html=True)
        
        # Botão Fantasma (AGORA SEM RESTRIÇÃO)
        st.markdown(f'<div class="ghost-btn">', unsafe_allow_html=True)
        if st.button(f"btn_{key}", key=key):
            # AQUI ESTÁ A MUDANÇA: Navegação direta, sem verificar aluno
            st.switch_page(page_path)
        st.markdown('</div>', unsafe_allow_html=True)

    # Grid de Módulos
    g1, g2 = st.columns(2, gap="medium")
    
    with g1:
        draw_module("Estudantes", "Gestão de cadastro e histórico clínico.", "ri-group-line", "bg-indigo", "pages/0_Alunos.py", "m_alunos")
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        draw_module("Plano de Ação (PAEE)", "Sala de recursos e intervenções.", "ri-puzzle-2-line", "bg-purple", "pages/2_PAE.py", "m_pae")
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        draw_module("Diário de Bordo", "Registro diário de evidências.", "ri-file-list-3-line", "bg-slate", "pages/4_Diario_de_Bordo.py", "m_diario")

    with g2:
        draw_module("Estratégias & PEI", "Plano Educacional Individualizado.", "ri-book-open-line", "bg-blue", "pages/1_PEI.py", "m_pei")
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        draw_module("Hub de Recursos", "Banco de materiais e adaptações.", "ri-rocket-2-line", "bg-teal", "pages/3_Hub_Inclusao.py", "m_hub")
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        draw_module("Evolução & Dados", "Indicadores de progresso.", "ri-bar-chart-box-line", "bg-slate", "pages/5_Monitoramento_Avaliacao.py", "m_dados")

# --- DIREITA: STATUS ---
with col_side:
    st.markdown("### 📌 Status", unsafe_allow_html=True)
    
    aluno_ativo = st.session_state.dados.get("nome")
    display_aluno = aluno_ativo if aluno_ativo else "Nenhum aluno selecionado"
    cor_status = "#10B981" if aluno_ativo else "#94A3B8"
    
    st.markdown(f"""
    <div class="widget-card">
        <div class="widget-title">Aluno em Foco</div>
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:10px; height:10px; border-radius:50%; background:{cor_status};"></div>
            <div style="font-weight:700; color:#334155;">{display_aluno}</div>
        </div>
        <div style="margin-top:10px; font-size:0.8rem; color:#64748B;">
            {f"Série: {st.session_state.dados.get('serie','-')}" if aluno_ativo else "Vá em Estudantes para selecionar."}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="widget-card">
        <div class="widget-title">Atividade Recente</div>
        <div class="timeline-item">
            <div class="tl-dot" style="background:#3B82F6"></div>
            <div>
                <div class="tl-content">Login realizado</div>
                <div class="tl-time">Agora mesmo</div>
            </div>
        </div>
        <div class="timeline-item">
            <div class="tl-dot"></div>
            <div>
                <div class="tl-content">Sistema atualizado</div>
                <div class="tl-time">v141.0</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

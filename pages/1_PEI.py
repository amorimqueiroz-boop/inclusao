# pages/0_Home.py
import streamlit as st
from datetime import datetime, date
import base64
import os
import time
from streamlit_cropper import st_cropper
import streamlit as st
from auth_gate import require_auth_or_block

require_auth_or_block()


# ==============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ==============================================================================
APP_VERSION = "v150.0 (SaaS Design)"

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
# 2. CSS AVANÇADO (O "MOTOR" DO DESIGN)
# ==============================================================================
st.markdown("""
<style>
/* Importando fontes modernas (DM Sans e Inter) */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

/* --- RESET & BASE --- */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #2B3674; /* Azul escuro elegante */
    background-color: #F4F7FE; /* Fundo cinza-azulado do print */
}

/* Esconde elementos nativos indesejados */
[data-testid="stHeader"] { display: none !important; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 98% !important;
}

/* --- HEADER SUPERIOR (SIMULADO) --- */
.top-header {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 30px; background: transparent;
}
.search-bar {
    background: white; border-radius: 30px; padding: 10px 20px;
    display: flex; align-items: center; gap: 10px; color: #A3AED0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.01); width: 400px;
    font-size: 0.9rem;
}
.profile-area {
    display: flex; align-items: center; gap: 15px;
    background: white; padding: 6px 10px 6px 20px; border-radius: 30px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.01);
}
.profile-name { font-weight: 700; font-size: 0.9rem; color: #2B3674; text-align: right; line-height: 1.2; }
.profile-role { font-size: 0.7rem; color: #A3AED0; font-weight: 500; }
.profile-avatar {
    width: 38px; height: 38px; background: #4318FF; color: white;
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.9rem;
}

/* --- HERO BANNER (AZUL) --- */
.hero-banner {
    background: linear-gradient(135deg, #4318FF 0%, #2B3674 100%); /* Azul Royal */
    border-radius: 20px;
    padding: 40px 50px;
    color: white;
    position: relative; overflow: hidden;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 20px 40px -10px rgba(67, 24, 255, 0.2);
    margin-bottom: 40px;
}
.hero-text h1 { font-family: 'DM Sans', sans-serif; font-size: 2.2rem; font-weight: 700; margin: 0; letter-spacing: -1px; }
.hero-text p { font-size: 1.05rem; opacity: 0.9; margin-top: 8px; max-width: 600px; }
.hero-moon { font-size: 2rem; margin-left: 10px; vertical-align: middle; }

/* Status do Sistema (Pílula) */
.system-status {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 10px 20px; border-radius: 14px;
    text-align: center; min-width: 160px;
}
.status-dot { width: 10px; height: 10px; background: #01B574; border-radius: 50%; display: inline-block; margin-right: 6px; }
.status-text { font-weight: 700; font-size: 0.9rem; }

/* --- SECTION TITLE --- */
.section-label {
    border-left: 4px solid #4318FF;
    padding-left: 15px; margin-bottom: 20px;
    font-size: 1.2rem; font-weight: 700; color: #2B3674;
}

/* --- CARDS DE MÓDULO (ESTILO SAAS) --- */
.module-card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    position: relative;
    box-shadow: 0 10px 30px rgba(0,0,0,0.02);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex; align-items: center; justify-content: space-between;
    height: 110px; /* Altura fixa elegante */
    overflow: hidden;
}

/* Borda lateral colorida (Identidade) */
.module-card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 6px;
    background: currentColor; /* Pega a cor do texto do container */
}

.module-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.06);
}

.card-left { display: flex; align-items: center; gap: 18px; }

/* Ícone */
.icon-container {
    width: 50px; height: 50px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem;
    /* As cores serão injetadas via estilo inline no python */
}

.text-content h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #1B2559; }
.text-content p { margin: 2px 0 0 0; font-size: 0.8rem; color: #A3AED0; max-width: 200px; }

.arrow-icon { color: #CBD5E0; font-size: 1.5rem; transition: 0.2s; }
.module-card:hover .arrow-icon { color: #4318FF; transform: translateX(3px); }

/* --- BOTÃO FANTASMA --- */
.ghost-btn button {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    opacity: 0; z-index: 10; cursor: pointer;
}

/* Ajustes de Cores Específicas */
.c-purple { color: #7551FF; background: #F4F7FE; } /* Estudantes */
.c-blue   { color: #4318FF; background: #F4F7FE; } /* PEI */
.c-pink   { color: #FF0080; background: #F4F7FE; } /* PAEE */
.c-teal   { color: #05CD99; background: #F4F7FE; } /* Hub */
.c-orange { color: #FFB547; background: #F4F7FE; } /* Diário */
.c-navy   { color: #2B3674; background: #F4F7FE; } /* Dados */

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. LOGICA & DADOS
# ==============================================================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "dados" not in st.session_state: st.session_state.dados = {"nome": "", "nasc": date(2015,1,1), "serie": None}

def get_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

def escola_vinculada():
    return st.session_state.get("workspace_name") or st.session_state.get("workspace_id", "")[:12]

# GATE DE SEGURANÇA
if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
    st.warning("Acesso não autorizado.")
    if st.button("Fazer Login"): st.rerun()
    st.stop()

# ==============================================================================
# 4. RENDERIZAÇÃO DA PÁGINA
# ==============================================================================

# --- HEADER SUPERIOR ---
usuario_nome = st.session_state.get('usuario_nome', 'Visitante')
cargo = st.session_state.get('usuario_cargo', 'Educador')
iniciais = usuario_nome[:2].upper()
escola = escola_vinculada()

st.markdown(f"""
<div class="top-header">
    <div class="search-bar">
        <i class="ri-search-line"></i> Buscar aluno, escola ou documento...
    </div>
    <div class="profile-area">
        <div style="display:flex; flex-direction:column; align-items:flex-end;">
            <div class="profile-name">{usuario_nome.split()[0]}</div>
            <div class="profile-role">{escola}</div>
        </div>
        <div class="profile-avatar">{iniciais}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- HERO BANNER ---
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"

st.markdown(f"""
<div class="hero-banner">
    <div class="hero-text">
        <h1>{saudacao}, {usuario_nome.split()[0]}! <span class="hero-moon">🌙</span></h1>
        <p>"A inclusão acontece quando aprendemos com as diferenças e não com as igualdades."</p>
    </div>
    <div class="system-status">
        <div style="font-size:0.75rem; opacity:0.8; margin-bottom:4px;">Status do Sistema</div>
        <div><span class="status-dot"></span> <span class="status-text">Online</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- TÍTULO SEÇÃO ---
st.markdown('<div class="section-label">Acesso Rápido</div>', unsafe_allow_html=True)

# --- FUNÇÃO DO CARD SAAS ---
def render_saas_card(title, desc, icon, icon_color_class, text_color_hex, target_page, key):
    # HTML do Card
    st.markdown(f"""
    <div class="module-card" style="color: {text_color_hex};">
        <div class="card-left">
            <div class="icon-container {icon_color_class}">
                <i class="{icon}"></i>
            </div>
            <div class="text-content">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
        </div>
        <div class="arrow-icon"><i class="ri-arrow-right-s-line"></i></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão Fantasma
    st.markdown(f'<div class="ghost-btn">', unsafe_allow_html=True)
    if st.button(f"btn_{key}", key=key):
        if "Alunos" in title or st.session_state.dados.get("nome"):
            st.switch_page(target_page)
        else:
            st.toast("⚠️ Selecione um aluno primeiro em 'Estudantes'.", icon="👇")
            time.sleep(1)
            st.switch_page("pages/0_Alunos.py")
    st.markdown('</div>', unsafe_allow_html=True)

# --- GRID 3x2 ---
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    render_saas_card("Estudantes", "Gestão de cadastro e histórico.", "ri-group-line", "c-purple", "#7551FF", "pages/0_Alunos.py", "m_aluno")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_saas_card("Hub de Recursos", "Banco de materiais e IA.", "ri-rocket-2-line", "c-teal", "#05CD99", "pages/3_Hub_Inclusao.py", "m_hub")

with c2:
    render_saas_card("Estratégias & PEI", "Plano Educacional Individualizado.", "ri-book-open-line", "c-blue", "#4318FF", "pages/1_PEI.py", "m_pei")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_saas_card("Diário de Bordo", "Registro diário de evidências.", "ri-file-list-3-line", "c-orange", "#FFB547", "pages/4_Diario_de_Bordo.py", "m_diario")

with c3:
    render_saas_card("Plano de Ação / PAEE", "Sala de recursos e intervenções.", "ri-puzzle-2-line", "c-pink", "#FF0080", "pages/2_PAE.py", "m_pae")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    render_saas_card("Evolução & Dados", "Indicadores e progresso.", "ri-bar-chart-box-line", "c-navy", "#2B3674", "pages/5_Monitoramento_Avaliacao.py", "m_dados")

# --- SIDEBAR (Mantém funcionalidade) ---
with st.sidebar:
    st.image("omni_icone.png" if os.path.exists("omni_icone.png") else "https://via.placeholder.com/150", width=50)
    st.markdown("### Navegação")
    if st.button("Sair", use_container_width=True):
        st.session_state.autenticado = False; st.rerun()

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #A3AED0; font-size: 0.75rem;'>Omnisfera desenvolvida por RODRIGO A. QUEIROZ</div>", unsafe_allow_html=True)

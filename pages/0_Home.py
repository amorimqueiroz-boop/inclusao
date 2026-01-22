# pages/0_Home.py
import streamlit as st
from datetime import datetime, date
import base64
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera",
    page_icon="omni_icone.png" if os.path.exists("omni_icone.png") else "🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. CSS (ESTILOS VISUAIS)
# ==============================================================================
st.markdown("""
<style>
/* Fontes */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
@import url("https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css");

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #F8FAFC;
    color: #1E293B;
}

/* Limpeza */
[data-testid="stHeader"], [data-testid="stSidebarNav"] { display: none !important; }
.block-container { padding-top: 100px !important; max-width: 95% !important; }

/* HEADER */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; height: 80px;
    background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
    border-bottom: 1px solid #E2E8F0; z-index: 999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 40px;
}
.brand-group { display: flex; align-items: center; gap: 12px; }
.brand-logo { height: 45px; animation: spin 60s linear infinite; }
.brand-text { font-weight: 800; color: #1E293B; font-size: 1.2rem; }

/* HERO */
.hero {
    background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 100%);
    border-radius: 20px; padding: 40px 50px; color: white;
    margin-bottom: 40px; position: relative; overflow: hidden;
    box-shadow: 0 10px 30px -10px rgba(37, 99, 235, 0.4);
}
.hero h1 { font-weight: 800; font-size: 2.2rem; margin: 0 0 10px 0; }
.hero p { opacity: 0.9; font-size: 1.1rem; max-width: 700px; margin: 0; }

/* CARD (Fundo Visual) */
.card-box {
    background: white; border-radius: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    height: 140px; /* Altura fixa para alinhar */
    position: relative;
    display: flex; align-items: center;
    padding-left: 100px; /* Espaço para o ícone */
    padding-right: 150px; /* Espaço para o botão */
    overflow: visible;
}

/* Barra Lateral Colorida */
.card-edge {
    position: absolute; left: 0; top: 0; bottom: 0; width: 8px;
    border-radius: 16px 0 0 16px;
}

/* Ícone */
.card-icon {
    position: absolute; left: 25px; top: 50%; transform: translateY(-50%);
    font-size: 2rem;
}

/* Texto */
.card-content h3 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #0F172A; }
.card-content p { margin: 4px 0 0 0; font-size: 0.85rem; color: #64748B; }

/* POSICIONAMENTO DO BOTÃO STREAMLIT (O TRUQUE) */
/* Isso pega o botão que vem LOGO DEPOIS do HTML e o move para dentro do card */
div.element-container:has(div.card-box) + div.element-container button {
    position: absolute !important;
    top: -95px !important; /* Sobe para dentro do card */
    right: 25px !important; /* Alinha à direita */
    width: auto !important;
    background-color: #4F46E5 !important; /* Roxo bonito */
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2) !important;
    z-index: 10 !important;
    transition: transform 0.2s !important;
}
div.element-container:has(div.card-box) + div.element-container button:hover {
    background-color: #4338ca !important;
    transform: translateY(-2px) !important;
}

/* RECURSOS EXTERNOS */
.res-link { text-decoration: none; }
.res-card {
    background: white; padding: 20px; border-radius: 12px;
    border: 1px solid #E2E8F0; display: flex; align-items: center; gap: 15px;
    transition: transform 0.2s;
}
.res-card:hover { transform: translateY(-3px); border-color: #CBD5E1; }
.res-icon { font-size: 1.5rem; }
.res-tit { font-weight: 700; color: #1E293B; font-size: 0.95rem; }
.res-sub { font-size: 0.8rem; color: #64748B; }

@keyframes spin { 100% { transform: rotate(360deg); } }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. HELPERS
# ==============================================================================
if "dados" not in st.session_state: st.session_state.dados = {"nome": "", "nasc": date(2015,1,1)}
if "autenticado" not in st.session_state: st.session_state.autenticado = False

def get_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

def escola():
    return st.session_state.get("workspace_name") or st.session_state.get("workspace_id", "")[:10]

# Gate
if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
    st.warning("Sessão encerrada.")
    if st.button("Reconectar"): st.rerun()
    st.stop()

# ==============================================================================
# 4. LAYOUT
# ==============================================================================

# TOPBAR
img_b64 = get_base64("omni_icone.png")
txt_b64 = get_base64("omni_texto.png")
user = st.session_state.get("usuario_nome", "Visitante").split()[0]

logo_tag = f'<img src="data:image/png;base64,{img_b64}" class="brand-logo">' if img_b64 else "🌐"
txt_tag = f'<img src="data:image/png;base64,{txt_b64}" style="height:30px;">' if txt_b64 else "<b>OMNISFERA</b>"

st.markdown(f"""
<div class="topbar">
    <div class="brand-group">{logo_tag} {txt_tag}</div>
    <div class="brand-group">
        <span style="background:#F1F5F9; padding:5px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; color:#64748B;">{escola()}</span>
        <div style="width:35px; height:35px; background:#2563EB; color:white; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700;">{user[:2].upper()}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# HERO
hora = datetime.now().hour
saudacao = "Bom dia" if 5 <= hora < 12 else "Boa tarde" if 12 <= hora < 18 else "Boa noite"

st.markdown(f"""
<div class="hero">
    <h1>{saudacao}, {user}!</h1>
    <p>Seu painel de controle pedagógico está pronto. Selecione um módulo abaixo.</p>
</div>
""", unsafe_allow_html=True)

# MÓDULOS (FUNCIONALIDADE CORRIGIDA)
st.markdown("### 🚀 Seus Módulos")

def card_funcional(titulo, desc, icone, cor, arquivo, chave):
    # HTML SEM INDENTAÇÃO
    html = f"""
<div class="card-box">
<div class="card-edge" style="background-color: {cor};"></div>
<div class="card-icon" style="color: {cor};"><i class="{icone}"></i></div>
<div class="card-content">
<h3>{titulo}</h3>
<p>{desc}</p>
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
    
    # BOTÃO REAL (que será movido pelo CSS acima)
    if st.button("CLIQUE AQUI", key=chave):
        # Lógica de redirecionamento precisa
        if "Alunos" in titulo:
            st.switch_page("pages/Alunos.py") 
        elif st.session_state.dados.get("nome"):
            st.switch_page(arquivo)
        else:
            st.toast("⚠️ Selecione um aluno primeiro!", icon="🚫")
            time.sleep(1)
            st.switch_page("pages/Alunos.py")

# GRID 2 POR LINHA (Para ficar largo e bonito)
c1, c2 = st.columns(2, gap="large")

with c1:
    card_funcional("Estudantes", "Gestão e histórico escolar.", "ri-group-fill", "#4F46E5", "pages/Alunos.py", "btn_aluno")
    st.write("") # Espaço
    card_funcional("Plano de Ação / PAEE", "Sala de recursos e intervenções.", "ri-puzzle-2-fill", "#9333EA", "pages/2_PAE.py", "btn_paee")
    st.write("")
    card_funcional("Hub de Recursos", "Materiais adaptados e IA.", "ri-rocket-2-fill", "#0D9488", "pages/3_Hub_Inclusao.py", "btn_hub")

with c2:
    card_funcional("Estratégias & PEI", "Plano Educacional Individualizado.", "ri-book-open-fill", "#2563EB", "pages/1_PEI.py", "btn_pei")
    st.write("")
    card_funcional("Diário de Bordo", "Registro diário de evidências.", "ri-file-list-3-fill", "#EA580C", "pages/4_Diario_de_Bordo.py", "btn_diario")
    st.write("")
    card_funcional("Evolução & Dados", "Indicadores e progresso.", "ri-bar-chart-box-fill", "#0F172A", "pages/5_Monitoramento_Avaliacao.py", "btn_dados")

# RECURSOS EXTERNOS
st.markdown("<br>### 📚 Recursos Externos", unsafe_allow_html=True)

def link_card(col, icon, tit, sub, url, color):
    with col:
        st.markdown(f"""
<a href="{url}" target="_blank" class="res-link">
<div class="res-card">
<div class="res-icon" style="color:{color}"><i class="{icon}"></i></div>
<div>
<div class="res-tit" style="color:{color}">{tit}</div>
<div class="res-sub">{sub}</div>
</div>
</div>
</a>
""", unsafe_allow_html=True)

r1, r2, r3, r4 = st.columns(4, gap="medium")
link_card(r1, "ri-government-fill", "Lei da Inclusão", "LBI e diretrizes", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm", "#0284C7")
link_card(r2, "ri-compass-3-fill", "Base Nacional", "Competências BNCC", "http://basenacionalcomum.mec.gov.br/", "#16A34A")
link_card(r3, "ri-brain-fill", "Neurociência", "Artigos e estudos", "https://institutoneurosaber.com.br/", "#DB2777")
link_card(r4, "ri-question-fill", "Ajuda", "Tutoriais", "#", "#EA580C")

# SIDEBAR
with st.sidebar:
    if os.path.exists("omni_icone.png"): st.image("omni_icone.png", width=60)
    st.write("---")
    if st.button("Sair do Sistema"):
        st.session_state.autenticado = False; st.rerun()

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #CBD5E0; font-size: 0.75rem;'>Omnisfera v160.0</div>", unsafe_allow_html=True)

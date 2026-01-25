import streamlit as st
import requests
from datetime import datetime, date
import base64
import os

# BIBLIOTECA DE MENU
from streamlit_option_menu import option_menu 

# ==============================================================================
# 1. CONFIGURAÇÃO
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera • Estudantes",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_VERSION = "v3.1 - Menu Seguro"

# ==============================================================================
# 2. DESIGN & CSS (CORREÇÃO DO ESPAÇAMENTO)
# ==============================================================================
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
<style>
    /* CORREÇÃO CRÍTICA: Espaço seguro para o menu não ficar escondido */
    .block-container { 
        padding-top: 2rem !important; /* Espaço suficiente para o menu */
        padding-bottom: 3rem; 
    }
    
    /* Remove a barra de topo padrão do Streamlit para não cobrir o menu */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 1 !important; /* Fica atrás do nosso menu se houver sobreposição */
        height: 0px !important; /* Tenta reduzir a altura */
    }
    
    /* Esconder elementos nativos desnecessários */
    [data-testid="stSidebarNav"], footer { display: none !important; }

    /* CARD HERO */
    .mod-card-wrapper { display: flex; flex-direction: column; margin-bottom: 20px; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; margin-top: 15px;}
    .mod-card-rect { background: white; padding: 0; display: flex; align-items: center; height: 90px; position: relative; }
    .mod-bar { width: 6px; height: 100%; position: absolute; left: 0; background-color: #0284C7; }
    .mod-icon-area { width: 80px; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; background: #F0F9FF; color: #0284C7; margin-left: 6px; }
    .mod-content { flex-grow: 1; padding: 0 20px; display: flex; flex-direction: column; justify-content: center; }
    .mod-title { font-weight: 800; font-size: 1.1rem; color: #1E293B; margin-bottom: 4px; }
    .mod-desc { font-size: 0.8rem; color: #64748B; }

    /* TABELA DE ALUNOS */
    .student-table { background: white; border-radius: 12px; border: 1px solid #E2E8F0; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.02); margin-top: 20px; }
    .student-header { display: grid; grid-template-columns: 3fr 1fr 1fr 2fr 1fr; background: #F8FAFC; padding: 12px 20px; border-bottom: 1px solid #E2E8F0; font-weight: 800; color: #475569; font-size: 0.8rem; text-transform: uppercase; }
    .student-row { display: grid; grid-template-columns: 3fr 1fr 1fr 2fr 1fr; padding: 12px 20px; border-bottom: 1px solid #F1F5F9; align-items: center; background: white; }
    .student-row:hover { background: #F8FAFC; }
    
    /* BADGES */
    .badge-grade { background: #F0F9FF; color: #0369A1; padding: 2px 8px; border-radius: 8px; font-size: 0.7rem; font-weight: 700; border: 1px solid #BAE6FD; }
    .badge-class { background: #F0FDF4; color: #15803D; padding: 2px 8px; border-radius: 8px; font-size: 0.7rem; font-weight: 700; border: 1px solid #BBF7D0; }
    
    /* MODAL DELETAR */
    .delete-confirm-banner { background: #FEF3C7; border: 1px solid #FDE68A; border-radius: 8px; padding: 8px 12px; margin-top: 4px; font-size: 0.8rem; color: #92400E; display: flex; align-items: center; gap: 8px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO
# ==============================================================================
def render_navbar():
    opcoes = [
        "Início", 
        "Estudantes", 
        "Estratégias & PEI", 
        "Plano de Ação (AEE)", 
        "Hub de Recursos", 
        "Diário de Bordo", 
        "Evolução & Dados"
    ]
    
    icones = [
        "house", 
        "people", 
        "book", 
        "puzzle", 
        "rocket", 
        "journal", 
        "bar-chart"
    ]

    selected = option_menu(
        menu_title=None, 
        options=opcoes,
        icons=icones,
        default_index=1, # Aba 'Estudantes' selecionada
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff", "border": "1px solid #E2E8F0", "border-radius": "10px", "margin-bottom": "10px"},
            "icon": {"color": "#64748B", "font-size": "14px"}, 
            "nav-link": {"font-size": "11px", "text-align": "center", "margin": "0px", "--hover-color": "#F1F5F9", "color": "#475569", "white-space": "nowrap"},
            "nav-link-selected": {"background-color": "#0284C7", "color": "white", "font-weight": "600"},
        }
    )
    
    # Navegação
    if selected == "Início":
        target = "pages/0_Home.py" if os.path.exists("pages/0_Home.py") else "0_Home.py"
        if not os.path.exists(target): target = "Home.py"
        st.switch_page(target)
    elif selected == "Estratégias & PEI": st.switch_page("pages/1_PEI.py")
    elif selected == "Plano de Ação (AEE)": st.switch_page("pages/2_PAE.py")
    elif selected == "Hub de Recursos": st.switch_page("pages/3_Hub_Inclusao.py")
    elif selected == "Diário de Bordo": st.switch_page("pages/4_Diario_de_Bordo.py")
    elif selected == "Evolução & Dados": st.switch_page("pages/5_Monitoramento_Avaliacao.py")

render_navbar()

# ==============================================================================
# 4. LÓGICA DE DADOS (SUPABASE)
# ==============================================================================

# Autenticação
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    # Mostra aviso visual em vez de apenas parar, para você saber se é erro de auth
    st.warning("🔒 Acesso restrito. Faça login na Home.")
    st.stop()

# Helpers
def _sb_headers():
    try:
        key = st.secrets.get("SUPABASE_SERVICE_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
        return {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    except: return {}

# Funções API
@st.cache_data(ttl=10, show_spinner=False)
def list_students_rest(workspace_id):
    try:
        url = st.secrets.get("SUPABASE_URL").rstrip("/") + "/rest/v1/students"
        params = f"?select=id,name,grade,class_group,diagnosis&workspace_id=eq.{workspace_id}&order=created_at.desc"
        r = requests.get(url + params, headers=_sb_headers(), timeout=10)
        return r.json() if r.status_code == 200 else []
    except: return []

def delete_student_rest(sid, wid):
    try:
        url = st.secrets.get("SUPABASE_URL").rstrip("/") + f"/rest/v1/students?id=eq.{sid}&workspace_id=eq.{wid}"
        requests.delete(url, headers=_sb_headers())
        return True
    except: return False

# ==============================================================================
# 5. ÁREA DE TRABALHO
# ==============================================================================

# Variáveis
ws_id = st.session_state.get("workspace_id")
user_name = st.session_state.get("usuario_nome", "Visitante")
user_first = user_name.split()[0]
saudacao = "Bom dia" if 5 <= datetime.now().hour < 12 else "Boa tarde"

# Refresh
if st.session_state.get("force_refresh"):
    list_students_rest.clear()
    st.session_state["force_refresh"] = False

if not ws_id:
    st.error("Nenhum workspace selecionado.")
    st.stop()

alunos = list_students_rest(ws_id)

# Card Hero
st.markdown(f"""
    <div class="mod-card-wrapper">
        <div class="mod-card-rect">
            <div class="mod-bar"></div>
            <div class="mod-icon-area"><i class="ri-group-fill"></i></div>
            <div class="mod-content">
                <div class="mod-title">Gestão de Estudantes</div>
                <div class="mod-desc">{saudacao}, <strong>{user_first}</strong>! Gerencie os dados dos alunos vinculados aos PEIs neste workspace.</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Controles
c1, c2 = st.columns([3, 1])
with c1:
    q = st.text_input("Buscar por nome", placeholder="Digite o nome...", label_visibility="collapsed")
with c2:
    if st.button("🔄 Atualizar Lista", use_container_width=True):
        st.session_state["force_refresh"] = True
        st.rerun()

# Filtragem
if q:
    alunos = [a for a in alunos if q.lower() in (a.get("name") or "").lower()]

# ==============================================================================
# 6. TABELA DE ALUNOS
# ==============================================================================
if not alunos:
    st.info("Nenhum estudante encontrado.")
else:
    st.markdown("""
    <div class="student-table">
        <div class="student-header"><div>Nome</div><div>Série</div><div>Turma</div><div>Diagnóstico</div><div>Ações</div></div>
    """, unsafe_allow_html=True)
    
    for a in alunos:
        sid = a.get("id")
        nome = a.get("name", "—")
        serie = a.get("grade", "—")
        turma = a.get("class_group", "—")
        diag = a.get("diagnosis", "—")
        
        confirm_key = f"confirm_del_{sid}"
        if confirm_key not in st.session_state:
            st.session_state[confirm_key] = False
        
        st.markdown(f"""
        <div class="student-row">
            <div style="font-weight:700; color:#1E293B;">{nome}</div>
            <div><span class="badge-grade">{serie}</span></div>
            <div><span class="badge-class">{turma}</span></div>
            <div style="font-size:0.8rem; color:#64748B;">{diag}</div>
            <div>
        """, unsafe_allow_html=True)
        
        if not st.session_state[confirm_key]:
            col_btn, _ = st.columns([1, 4])
            with col_btn:
                if st.button("🗑️", key=f"btn_del_{sid}", help="Excluir"):
                    st.session_state[confirm_key] = True
                    st.rerun()
        else:
            st.markdown(f"""<div class="delete-confirm-banner"><i class="ri-alert-fill"></i> Excluir <b>{nome}</b>?</div>""", unsafe_allow_html=True)
            c_sim, c_nao = st.columns(2)
            with c_sim:
                if st.button("✅", key=f"yes_{sid}", type="primary"):
                    delete_student_rest(sid, ws_id)
                    list_students_rest.clear()
                    st.session_state[confirm_key] = False
                    st.rerun()
            with c_nao:
                if st.button("❌", key=f"no_{sid}"):
                    st.session_state[confirm_key] = False
                    st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Rodapé
st.markdown(f"<div style='text-align:center;color:#94A3B8;font-size:0.7rem;padding:20px;margin-top:20px;'>{len(alunos)} estudantes • {APP_VERSION}</div>", unsafe_allow_html=True)

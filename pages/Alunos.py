import streamlit as st
import requests
from datetime import datetime
import os
import sys

# ==============================================================================
# 0. IMPORTAÇÃO SEGURA DO OMNI_UTILS
# ==============================================================================
# Adiciona o diretório raiz ao path para conseguir importar omni_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import omni_utils as ou
except ImportError:
    st.error("Erro crítico: O arquivo 'omni_utils.py' não foi encontrado na pasta raiz.")
    st.stop()

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Omnisfera • Estudantes",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_VERSION = "v3.7 - Modularizado"

def gap_hub():
    """Respiro padrão do Hub (mesmo feeling de distâncias)."""
    st.markdown(
        """
        <style>
          .omni-page-gap { height: 14px; }
        </style>
        <div class="omni-page-gap"></div>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# 2. RENDERIZAÇÃO DOS COMPONENTES VISUAIS (HEADER E MENU)
# ==============================================================================

# Garante que o estado de sessão (login, workspace) existe
ou.ensure_state()

# 1. Renderiza o Cabeçalho (Logo + Usuário)
ou.render_omnisfera_header()

# ==============================================================================
# AJUSTE FINO DE LAYOUT (Igual ao PEI - PADRONIZADO)
# ==============================================================================
def forcar_layout_hub():
    st.markdown("""
        <style>
            /* 1. Remove o cabeçalho padrão do Streamlit e a linha colorida */
            header[data-testid="stHeader"] {
                visibility: hidden !important;
                height: 0px !important;
            }

            /* 2. Puxa todo o conteúdo para cima (O SEGREDO ESTÁ AQUI) */
            .block-container {
                padding-top: 1rem !important; /* Padronizado: mesma distância do PEI */
                padding-bottom: 1rem !important;
                margin-top: 0px !important;
            }

            /* 3. Remove padding extra se houver container de navegação */
            div[data-testid="stVerticalBlock"] > div:first-child {
                padding-top: 0px !important;
            }
            
            /* 4. Esconde o menu hambúrguer e rodapé */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# CHAME ESTA FUNÇÃO LOGO NO INÍCIO DO CÓDIGO
forcar_layout_hub()

# 2. CSS Específico desta página (Cards e Tabelas)
st.markdown("""
<style>
    /* CARD HERO */
    .mod-card-wrapper { display: flex; flex-direction: column; margin-bottom: 20px; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-top: 0 !important; border: 1px solid #E2E8F0;}
    .mod-card-rect { background: white; padding: 0; display: flex; align-items: center; height: 130px !important; position: relative; border-radius: 16px 16px 0 0; border-bottom: none; }
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

# 3. Renderiza o Menu de Navegação (Aba Ativa: Estudantes)
ou.render_navbar(active_tab="Estudantes")

# ==============================================================================
# 3. LÓGICA DE DADOS
# ==============================================================================

# Verificação de segurança
if not st.session_state.autenticado:
    st.warning("🔒 Acesso restrito. Faça login na Home.")
    st.stop()

# Helpers API (Local)
@st.cache_data(ttl=10, show_spinner=False)
def list_students_rest(workspace_id):
    try:
        url = st.secrets.get("SUPABASE_URL").rstrip("/") + "/rest/v1/students"
        # Usa o header helper do omni_utils
        headers = ou._headers()
        params = f"?select=id,name,grade,class_group,diagnosis&workspace_id=eq.{workspace_id}&order=created_at.desc"
        r = requests.get(url + params, headers=headers, timeout=10)
        return r.json() if r.status_code == 200 else []
    except: return []

def delete_student_rest(sid, wid):
    try:
        url = st.secrets.get("SUPABASE_URL").rstrip("/") + f"/rest/v1/students?id=eq.{sid}&workspace_id=eq.{wid}"
        headers = ou._headers()
        requests.delete(url, headers=headers)
        return True
    except: return False

# ==============================================================================
# 4. APLICAÇÃO PRINCIPAL
# ==============================================================================
ws_id = st.session_state.get("workspace_id")
user_name = st.session_state.get("usuario_nome", "Visitante")
user_first = user_name.split()[0]
saudacao = "Bom dia" if 5 <= datetime.now().hour < 12 else "Boa tarde"

# Lógica de Refresh
if st.session_state.get("force_refresh"):
    list_students_rest.clear()
    st.session_state["force_refresh"] = False

if not ws_id:
    st.error("Nenhum workspace selecionado.")
    st.stop()

# Busca Alunos
alunos = list_students_rest(ws_id)

# Renderiza Hero Card
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

# Controles de Busca
c1, c2 = st.columns([3, 1])
with c1:
    q = st.text_input("Buscar por nome", placeholder="Digite o nome...", label_visibility="collapsed")
with c2:
    if st.button("🔄 Atualizar Lista", use_container_width=True):
        st.session_state["force_refresh"] = True
        st.rerun()

# Filtragem Local
if q:
    alunos = [a for a in alunos if q.lower() in (a.get("name") or "").lower()]

# Tabela
if not alunos:
    st.info("Nenhum estudante encontrado.")
else:
    st.markdown("""
    <div class="student-table">
        <div class="student-header"><div>Nome</div><div>Série</div><div>Turma</div><div>Diagnóstico</div><div>Ações</div></div>
    """, unsafe_allow_html=True)
    
    for a in alunos:
        sid, nome = a.get("id"), a.get("name", "—")
        serie, turma = a.get("grade", "—"), a.get("class_group", "—")
        diag = a.get("diagnosis", "—")
        
        # Chave única para controle de estado do botão de deletar
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
        
        # Coluna de Ações (Botão Python dentro do HTML Layout)
        if not st.session_state[confirm_key]:
            c_btn, _ = st.columns([1, 4])
            with c_btn:
                if st.button("🗑️", key=f"btn_del_{sid}", help="Excluir"):
                    st.session_state[confirm_key] = True
                    st.rerun()
        else:
            st.markdown(f"""<div class="delete-confirm-banner"><i class="ri-alert-fill"></i> Excluir <b>{nome}</b>?</div>""", unsafe_allow_html=True)
            c_s, c_n = st.columns(2)
            with c_s:
                if st.button("✅", key=f"yes_{sid}", type="primary"):
                    delete_student_rest(sid, ws_id)
                    list_students_rest.clear()
                    st.session_state[confirm_key] = False
                    st.rerun()
            with c_n:
                if st.button("❌", key=f"no_{sid}"):
                    st.session_state[confirm_key] = False
                    st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Rodapé Simples
st.markdown(f"<div style='text-align:center;color:#94A3B8;font-size:0.7rem;padding:20px;margin-top:20px;'>{len(alunos)} estudantes • {APP_VERSION}</div>", unsafe_allow_html=True)

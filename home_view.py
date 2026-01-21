# home_view.py
import streamlit as st
from omni_utils import ensure_state, inject_base_css, supabase_log_access

APP_VERSION = "v1.0"

def _open_page(page_path: str, event: str):
    """Navega para uma página do /pages somente após clique (evita loops)."""
    user = st.session_state.get("user") or {}
    nome = user.get("nome", "Visitante")
    cargo = user.get("cargo", "")

    try:
        supabase_log_access(
            workspace_id=st.session_state.workspace_id,
            nome=nome,
            cargo=cargo,
            event=event,
            app_version=APP_VERSION,
        )
    except Exception:
        pass

    st.switch_page(page_path)

def render_home():
    ensure_state()
    inject_base_css()

    if not st.session_state.get("autenticado") or not st.session_state.get("workspace_id"):
        st.session_state.view = "login"
        st.rerun()

    user = st.session_state.get("user") or {}
    nome = user.get("nome", "Visitante")
    cargo = user.get("cargo", "")

    st.markdown(
        f"""
<div class="header-lite">
  <div>
    <div class="h-title">Olá, {nome} 👋</div>
    <div class="h-sub">{cargo} · Workspace ativo</div>
  </div>
  <div class="h-badge">OMNISFERA {APP_VERSION}</div>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Acesso rápido")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("🧠 Abrir PEI 360º", use_container_width=True):
            _open_page("pages/1_PEI.py", "open_pei")

    with c2:
        if st.button("👥 Alunos", use_container_width=True):
            _open_page("pages/0_Alunos.py", "open_alunos")

    with c3:
        if st.button("🧩 PAE", use_container_width=True):
            _open_page("pages/2_PAE.py", "open_pae")

    st.markdown("---")
    c4, c5, c6 = st.columns(3)

    with c4:
        if st.button("📚 Hub Inclusão", use_container_width=True):
            _open_page("pages/3_Hub_Inclusao.py", "open_hub")

    with c5:
        if st.button("📝 Diário de Bordo", use_container_width=True):
            _open_page("pages/4_Diario_de_Bordo.py", "open_diario")

    with c6:
        if st.button("📈 Monitoramento & Avaliação", use_container_width=True):
            _open_page("pages/5_Monitoramento_Avaliacao.py", "open_monitoramento")

    st.markdown("---")
    if st.button("🔒 Sair"):
        try:
            supabase_log_access(
                workspace_id=st.session_state.workspace_id,
                nome=nome,
                cargo=cargo,
                event="logout",
                app_version=APP_VERSION,
            )
        except Exception:
            pass

        st.session_state.autenticado = False
        st.session_state.workspace_id = None
        st.session_state.user = None
        st.session_state.view = "login"
        st.rerun()
